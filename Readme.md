## Windows Tweaker - Usage & Development

### Platform Requirements
- **Windows only:** Most tweaks require Windows registry and PowerShell access (`winreg`, etc.).
- On **macOS/Linux**, the app will run but Windows-specific features will be disabled or stubbed.

### How to Run
- **Windows:**
	1. Open a terminal in the parent directory of `windows11_tweaker`.
	2. Run: `python -m windows11_tweaker.main`
- **macOS/Linux:**
	- You can launch the app, but most tweaks will be unavailable due to missing Windows APIs.

### How to add a new tweak
1. Create a new function entry in an existing module under `tweaks/` **or** add a new `myfeature.py` file exporting `get_tweaks() -> List[Tweak]`.
2. Choose a `category` string — it becomes a **tab** automatically.
3. Pick a control `type` (`dropdown|toggle|number|slider|text`), defaults, tooltips, and (optional) warning/help.
4. Implement the `apply` lambda/function to perform real work (registry, PowerShell, etc.).

That’s it — the app discovers the module, builds the UI, persists values with `QSettings`, previews actions, and applies them.

---

### Notes
- The example `apply` handlers are stubs (`print(...)`). Wire them to real logic or call into `util.admin` helpers.
- Validation hooks are available per tab (override `validate()` in a custom tab if needed). The generic tab currently returns valid; you can extend it to cross-check related numeric ranges.
- The stylesheet provides a **modern light theme**, rounded corners, subtle transparency, and tidy controls.
- Packaging tip: add a `pyproject.toml` and mark `windows11_tweaker` as a package to run `python -m windows11_tweaker.main`.