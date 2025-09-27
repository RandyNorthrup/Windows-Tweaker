from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QPushButton,
    QHBoxLayout, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem,
    QComboBox, QCheckBox, QSpinBox, QSlider, QLineEdit, QMessageBox
)

Category = str
# Apply returns (ok, message)
ApplyFn = Callable[[Any], Tuple[bool, str]]

@dataclass
class Tweak:
    id: str
    category: Category
    label: str
    type: str  # dropdown|toggle|number|slider|text
    default: Any
    tooltip: str = ""
    help: str = ""
    warning: str = ""
    options: Optional[List[str]] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    step: Optional[int] = None
    apply: ApplyFn = lambda value: (True, "noop")


class ActionPreview(QDialog):
    def __init__(self, actions: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Preview & Confirm")
        self.setMinimumSize(560, 420)
        layout = QVBoxLayout(self)
        info = QLabel("Review the actions below. Click OK to execute.")
        layout.addWidget(info)
        self.listw = QListWidget()
        for a in actions:
            self.listw.addItem(QListWidgetItem(a))
        layout.addWidget(self.listw)
        self.warn = QLabel("⚠️ Some actions require Administrator privileges.")
        layout.addWidget(self.warn)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)


class TweakTab(QWidget):
    def __init__(self, category: Category, tweaks: List[Tweak], settings: QSettings, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.category = category
        self.tweaks = tweaks
        self.settings = settings
        self.controls: Dict[str, Union[QComboBox, QCheckBox, QSpinBox, QSlider, QLineEdit]] = {}

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(18, 18, 18, 18)

        box = QGroupBox(category)
        form = QFormLayout(box)

        for t in tweaks:
            ctrl = self._make_control(t)
            self.controls[t.id] = ctrl
            lbl = QLabel(t.label)
            lbl.setToolTip(t.help or t.tooltip)
            form.addRow(lbl, ctrl)
            if t.warning:
                w = QLabel(f"⚠️ {t.warning}")
                form.addRow("", w)

        self.main.addWidget(box)

        row = QHBoxLayout()
        row.addStretch()
        self.resetBtn = QPushButton("Reset")
        self.applyBtn = QPushButton("Apply")
        self.applyBtn.clicked.connect(self.apply)
        self.resetBtn.clicked.connect(self.load_defaults)
        row.addWidget(self.resetBtn)
        row.addWidget(self.applyBtn)
        self.main.addLayout(row)

        self.load_settings()

    def _make_control(self, t: Tweak) -> Union[QComboBox, QCheckBox, QSpinBox, QSlider, QLineEdit]:
        if t.type == "dropdown":
            cb: QComboBox = QComboBox()
            cb.addItems(t.options or [])
            cb.setCurrentIndex(max(0, (t.options or [t.default]).index(t.default)))
            cb.setToolTip(t.tooltip)
            return cb
        elif t.type == "toggle":
            chk: QCheckBox = QCheckBox()
            chk.setChecked(bool(t.default))
            chk.setToolTip(t.tooltip)
            return chk
        elif t.type == "number":
            sp: QSpinBox = QSpinBox()
            if t.minimum is not None: sp.setMinimum(t.minimum)
            if t.maximum is not None: sp.setMaximum(t.maximum)
            if t.step is not None: sp.setSingleStep(t.step)
            sp.setValue(int(t.default))
            sp.setToolTip(t.tooltip)
            return sp
        elif t.type == "slider":
            sl: QSlider = QSlider(Qt.Orientation.Horizontal)
            sl.setMinimum(t.minimum or 0)
            sl.setMaximum(t.maximum or 100)
            sl.setSingleStep(t.step or 1)
            sl.setValue(int(t.default))
            sl.setToolTip(t.tooltip)
            return sl
        elif t.type == "text":
            le: QLineEdit = QLineEdit()
            le.setText(str(t.default))
            le.setToolTip(t.tooltip)
            return le
        else:
            raise ValueError(f"Unknown control type: {t.type}")

    def _key(self, tid: str) -> str:
        return f"{self.category}/{tid}"

    def save_settings(self):
        for t in self.tweaks:
            ctrl = self.controls[t.id]
            if isinstance(ctrl, QComboBox):
                self.settings.setValue(self._key(t.id), ctrl.currentText())
            elif isinstance(ctrl, QCheckBox):
                self.settings.setValue(self._key(t.id), ctrl.isChecked())
            elif isinstance(ctrl, (QSpinBox, QSlider)):
                self.settings.setValue(self._key(t.id), int(ctrl.value()))
            elif isinstance(ctrl, QLineEdit):
                self.settings.setValue(self._key(t.id), ctrl.text())
        self.settings.sync()

    def load_settings(self):
        for t in self.tweaks:
            ctrl = self.controls[t.id]
            val = self.settings.value(self._key(t.id), t.default)
            if isinstance(ctrl, QComboBox):
                sval = str(val)
                if t.options and sval in t.options:
                    ctrl.setCurrentIndex(t.options.index(sval))
            elif isinstance(ctrl, QCheckBox):
                ctrl.setChecked(val is True or str(val).lower() == "true")
            elif isinstance(ctrl, (QSpinBox, QSlider)):
                try:
                    ctrl.setValue(int(str(val)))
                except Exception:
                    ctrl.setValue(int(t.default))
            elif isinstance(ctrl, QLineEdit):
                ctrl.setText(str(val))

    def load_defaults(self):
        for t in self.tweaks:
            ctrl = self.controls[t.id]
            if isinstance(ctrl, QComboBox):
                if t.options:
                    ctrl.setCurrentIndex(max(0, t.options.index(t.default)))
            elif isinstance(ctrl, QCheckBox):
                ctrl.setChecked(bool(t.default))
            elif isinstance(ctrl, (QSpinBox, QSlider)):
                ctrl.setValue(int(t.default))
            elif isinstance(ctrl, QLineEdit):
                ctrl.setText(str(t.default))

    def validate(self) -> Tuple[bool, str]:
        return True, ""

    def collect_actions(self) -> List[str]:
        actions: List[str] = []
        for t in self.tweaks:
            v = self.current_value(t)
            actions.append(f"[{self.category}] {t.label} → {v}")
        return actions

    def current_value(self, t: Tweak) -> Any:
        ctrl = self.controls[t.id]
        if isinstance(ctrl, QComboBox):
            return ctrl.currentText()
        elif isinstance(ctrl, QCheckBox):
            return ctrl.isChecked()
        elif isinstance(ctrl, (QSpinBox, QSlider)):
            return int(ctrl.value())
        elif isinstance(ctrl, QLineEdit):
            return ctrl.text()

    def apply(self):
        ok, msg = self.validate()
        if not ok:
            QMessageBox.warning(self, "Validation error", msg)
            return
        actions = self.collect_actions()
        dlg = ActionPreview(actions, self)
        if dlg.exec():
            self.save_settings()
            failures: List[str] = []
            for t in self.tweaks:
                val = self.current_value(t)
                ok, out = t.apply(val)
                if not ok:
                    failures.append(f"{t.label}: {out}")
            if failures:
                QMessageBox.critical(self, "Some actions failed", "\n".join(failures))
            else:
                QMessageBox.information(self, "Success", f"{self.category}: all actions applied.")


def build_tab_widget(category: Category, tweaks: List[Tweak], settings: QSettings, parent=None) -> TweakTab:
    return TweakTab(category, tweaks, settings, parent)