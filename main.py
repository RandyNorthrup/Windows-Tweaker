from __future__ import annotations
from typing import Dict, List
from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QStatusBar,
    QToolBar, QMessageBox
)
from PySide6.QtGui import QAction

from .tweaks.base import Tweak, Category, build_tab_widget
from .tweaks import load_all_tweaks, group_by_category
from .util.ps import checkpoint

APP_ORG = "YourOrg"
APP_NAME = "Windows 11 Tweaker (Modular)"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1000, 720)

        self.settings = QSettings(APP_ORG, APP_NAME)

        # Load tweaks
        tweaks: List[Tweak] = load_all_tweaks()
        self.grouped: Dict[Category, List[Tweak]] = group_by_category(tweaks)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tab_widgets = {}
        for cat, items in self.grouped.items():
            tabw = build_tab_widget(cat, items, self.settings, parent=self)
            self.tabs.addTab(tabw, cat)
            self.tab_widgets[cat] = tabw

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.addWidget(self.tabs)
        container.setObjectName("card")
        self.setCentralWidget(container)

        tb = QToolBar("Main")
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)

        actCheckpoint = QAction("Create Restore Point", self)
        actCheckpoint.triggered.connect(self.create_restore_point)
        tb.addAction(actCheckpoint)

        actApplyAll = QAction("Apply All", self)
        actApplyAll.triggered.connect(self.apply_all)
        tb.addAction(actApplyAll)

        actSave = QAction("Save", self)
        actSave.setToolTip("Save choices without applying")
        actSave.triggered.connect(self.save_all)
        tb.addAction(actSave)

        actReset = QAction("Reset All", self)
        actReset.triggered.connect(self.reset_all)
        tb.addAction(actReset)

        sb = QStatusBar()
        self.setStatusBar(sb)
        self.toast(f"Loaded {len(tweaks)} tweak(s)")

        self.apply_styles()

    def toast(self, msg: str):
        self.statusBar().showMessage(msg, 3000)

    def apply_styles(self):
        self.setStyleSheet(
            """
            QMainWindow { background: #f5f7fb; }
            #card { background: rgba(255,255,255,0.92); border-radius: 18px; margin: 12px; }
            QGroupBox { background: rgba(255,255,255,0.85); border: 1px solid #e6eaf2; border-radius: 14px; margin-top: 12px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 4px 8px; color: #334155; font-weight: 600; }
            QLabel.section { font-size: 14pt; font-weight: 700; color: #1f2937; margin: 6px 0 4px 2px; }
            QLabel.pill-info, QLabel.pill-hint, QLabel.pill-warn { border-radius: 10px; padding: 8px 10px; margin: 8px 0; }
            QTabWidget::pane { border: 0px; margin: 6px; }
            QTabBar::tab { background: rgba(255,255,255,0.85); border: 1px solid #e6eaf2; padding: 8px 14px; margin-right: 6px; border-top-left-radius: 12px; border-top-right-radius: 12px; color: #334155; }
            QTabBar::tab:selected { background: #ffffff; color: #111827; }
            QPushButton { background: #ffffff; border: 1px solid #dbe2ee; padding: 8px 14px; border-radius: 12px; }
            QPushButton:hover { border-color: #bcd0f7; }
            QPushButton:pressed { background: #f1f5ff; }
            QComboBox, QSpinBox, QLineEdit { background: #ffffff; border: 1px solid #dbe2ee; border-radius: 10px; padding: 6px 10px; }
            QSlider::groove:horizontal { height: 6px; background: #e6eaf2; border-radius: 3px; }
            QSlider::handle:horizontal { width: 16px; height: 16px; margin: -6px 0; background: #ffffff; border: 1px solid #bcd0f7; border-radius: 8px; }
            QStatusBar { background: rgba(255,255,255,0.8); border-top: 1px solid #e6eaf2; }
            """
        )

    # ----- Global actions -----
    def gather_all_actions(self) -> List[str]:
        actions: List[str] = []
        for tab in self.tab_widgets.values():
            ok, msg = tab.validate()
            if not ok:
                raise ValueError(msg)
            actions += tab.collect_actions()
        return actions

    def create_restore_point(self):
        ok, out = checkpoint("Before Windows11Tweaker ApplyAll")
        QMessageBox.information(self, "Restore Point", out if ok else f"Failed: {out}")

    def apply_all(self):
        try:
            _ = self.gather_all_actions()
        except ValueError as e:
            QMessageBox.warning(self, "Validation error", str(e))
            return
        for tab in self.tab_widgets.values():
            tab.apply()
        self.toast("All tabs applied")

    def save_all(self):
        for tab in self.tab_widgets.values():
            tab.save_settings()
        self.toast("All settings saved (no actions executed)")

    def reset_all(self):
        for tab in self.tab_widgets.values():
            tab.load_defaults()
        self.toast("All tabs reset to defaults")


def main():
    import sys
    app = QApplication(sys.argv)
    app.setOrganizationName(APP_ORG)
    app.setApplicationName(APP_NAME)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()