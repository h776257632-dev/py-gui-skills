---
name: python-gui-engineering
description: Create production-grade Python desktop interfaces with high design quality and robust engineering. Use this skill when the user asks to build desktop applications, dashboards, or system utilities. Generates high-performance, visually refined code (PySide6, CustomTkinter, Flet) that follows MVVM patterns and avoids the "dated" look of legacy GUI frameworks.
---

# Python GUI Engineering Skill

This skill guides the creation of distinctive, production-grade Python desktop interfaces that avoid generic "AI slop" or legacy aesthetics. It ensures code is architecturally sound, thread-safe, and ready for distribution.

---

## Framework Decision Matrix

Before coding, select the framework based on these criteria:

| Framework | Best For | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **CustomTkinter** | Lightweight tools | Modern look, zero complex dependencies | Limited widget variety for large apps |
| **PySide6 (Qt)** | Commercial/Complex | Industry standard, QSS styling, huge widget set | Larger bundle size, complex licensing |
| **Flet (Flutter)** | High-end UI/UX | Pixel-perfect, native animations, Web-ready | Heavy abstraction from system low-level |

---

## Engineering & Design Principles

1. **Architecture**: Default to **MVVM (Model-View-ViewModel)**. Keep UI logic separate from business logic.
2. **The 60FPS Rule**: Never block the main UI thread. All I/O, API, or heavy compute MUST use `QThread`, `threading.Thread`, or `asyncio`.
3. **Asset Integrity**: Use a robust path manager to handle `_MEIPASS` (for PyInstaller) and local dev paths.
4. **Platform Tone**: Decide if the app follows **Native OS** (Fluent/Material) or a **Custom Shell** (Brutalist, Minimalist, or Cyberpunk).

---

## Project Scaffolding

Implement the following structure for all projects:

```text
project_root/
├── assets/             # Icons (SVG preferred), themes, fonts
├── src/
│   ├── ui/             # Views and custom widgets
│   ├── core/           # Business logic and data models
│   └── utils/          # Path manager, thread workers, helpers
├── build/              # .spec files and build scripts
├── main.py             # Entry point
└── requirements.txt
```

---

## Technical Guidelines

### 1. Robust Path Management

Never use hardcoded paths. Always use a resource wrapper:

```python
import sys
import os

def get_resource(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
```

### 2. Modern Aesthetics (UI/UX)

- **Typography**: Explicitly set font rendering. Use modern stacks like `Inter`, `Geist`, or `Segoe UI Variable`.
- **High-DPI**: Must include DPI awareness code (see below).
- **Visual Depth**: Use 8px/16px grids, rounded corners (8-12px), and subtle border glows or layered transparencies.
- **Color Palette**: Use curated palettes, not default system colors. Consider dark mode by default.

#### Windows High-DPI Awareness (REQUIRED)

> [!IMPORTANT]
> **Always include this code at the TOP of your main.py**, before any Qt/Tkinter imports.  
> Without this, your app will appear blurry on 4K/HiDPI displays on Windows.

```python
"""Windows DPI Awareness - MUST be called before any GUI imports"""
import os
import sys

def enable_high_dpi():
    """Enable crisp rendering on Windows High-DPI displays."""
    if os.name == 'nt':  # Windows only
        try:
            from ctypes import windll
            # SetProcessDpiAwareness(1) = System DPI aware
            # SetProcessDpiAwareness(2) = Per-monitor DPI aware (best)
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # Fallback for older Windows versions
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass

# Call immediately at startup, BEFORE importing PySide6/Tkinter
enable_high_dpi()

# For PySide6, also set these environment variables before import
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

# NOW import your GUI framework
from PySide6.QtWidgets import QApplication
# or: import customtkinter as ctk
```

For **CustomTkinter**, also call this after creating the app:
```python
import customtkinter as ctk
ctk.deactivate_automatic_dpi_awareness()  # If you handle DPI manually
# or let CTK handle it automatically (default behavior)
```

### 3. Concurrency Patterns

When performing long-running tasks:

**PySide6 (Qt)**:
```python
from PySide6.QtCore import QThread, Signal

class Worker(QThread):
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, task_func, *args):
        super().__init__()
        self.task_func = task_func
        self.args = args
    
    def run(self):
        try:
            result = self.task_func(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
```

**CustomTkinter**:
```python
import threading
import queue

class ThreadedTask:
    def __init__(self, root, task_func, callback):
        self.root = root
        self.queue = queue.Queue()
        self.callback = callback
        threading.Thread(target=self._run, args=(task_func,), daemon=True).start()
        self._check_queue()
    
    def _run(self, task_func):
        try:
            result = task_func()
            self.queue.put(('success', result))
        except Exception as e:
            self.queue.put(('error', str(e)))
    
    def _check_queue(self):
        try:
            status, data = self.queue.get_nowait()
            self.callback(status, data)
        except queue.Empty:
            self.root.after(100, self._check_queue)
```

**Flet**:
```python
import asyncio

async def long_running_task(page, update_ui_callback):
    # Use asyncio natively
    result = await asyncio.to_thread(blocking_function)
    update_ui_callback(result)
    page.update()
```

---

## Global Error Handling

Always implement a global exception hook:

```python
import sys
import traceback

def setup_exception_handler(show_error_dialog):
    """Setup global exception handler for GUI apps."""
    def exception_hook(exc_type, exc_value, exc_tb):
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(error_msg, file=sys.stderr)
        show_error_dialog("Unexpected Error", error_msg)
    
    sys.excepthook = exception_hook

# For PySide6
def show_qt_error(title: str, message: str):
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.critical(None, title, message)

# For CustomTkinter
def show_ctk_error(title: str, message: str):
    import customtkinter as ctk
    from tkinter import messagebox
    messagebox.showerror(title, message)
```

---

## MVVM Data Binding Pattern

> [!CAUTION]
> **NEVER update UI widgets directly from a Worker thread!**  
> Always emit signals from the worker and connect them to UI update methods on the main thread.

### ViewModel Template (PySide6)

Use this pattern to separate business logic from UI:

```python
"""ViewModel Template - Separating Logic from UI"""
from PySide6.QtCore import QObject, Signal, Property, Slot

class ViewModel(QObject):
    """
    Base ViewModel for MVVM pattern.
    All business logic goes here, NOT in the View.
    """
    # Signals for UI updates - UI connects to these
    status_changed = Signal(str)
    data_updated = Signal(list)
    progress_changed = Signal(int)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._status = "Ready"
        self._progress = 0
        self._data = []
    
    # Properties with notify signals for data binding
    @Property(str, notify=status_changed)
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value: str):
        if self._status != value:
            self._status = value
            self.status_changed.emit(value)
    
    @Property(int, notify=progress_changed)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value: int):
        if self._progress != value:
            self._progress = value
            self.progress_changed.emit(value)
    
    @Slot()
    def load_data(self):
        """Example: Load data in background thread."""
        from PySide6.QtCore import QThread
        
        self.status = "Loading..."
        self.worker = DataWorker(self._fetch_data)
        self.worker.finished.connect(self._on_data_loaded)
        self.worker.error.connect(self._on_error)
        self.worker.start()
    
    def _fetch_data(self):
        # Simulate heavy work
        import time
        time.sleep(2)
        return ["Item 1", "Item 2", "Item 3"]
    
    def _on_data_loaded(self, result):
        self._data = result
        self.data_updated.emit(result)
        self.status = "Ready"
    
    def _on_error(self, error_msg):
        self.error_occurred.emit(error_msg)
        self.status = "Error"
```

### View-ViewModel Connection

```python
"""View connects to ViewModel signals, never manipulates data directly"""
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self, view_model: ViewModel):
        super().__init__()
        self.vm = view_model
        self.setup_ui()
        self.bind_viewmodel()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.status_label = QLabel("Ready")
        self.load_btn = QPushButton("Load Data")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.load_btn)
    
    def bind_viewmodel(self):
        """Connect ViewModel signals to UI updates."""
        # ViewModel -> View (data binding)
        self.vm.status_changed.connect(self.status_label.setText)
        self.vm.data_updated.connect(self._on_data_updated)
        self.vm.error_occurred.connect(self._show_error)
        
        # View -> ViewModel (user actions)
        self.load_btn.clicked.connect(self.vm.load_data)
    
    def _on_data_updated(self, data: list):
        # Update UI with new data
        print(f"Received {len(data)} items")
    
    def _show_error(self, message: str):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)
```

### MVVM Anti-Patterns

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| `self.label.setText(data)` in Worker | Emit `Signal` → connect to `QLabel.setText` |
| `view_model.some_widget.update()` | ViewModel has NO reference to widgets |
| Business logic in `MainWindow` | Business logic in `ViewModel` only |
| Direct database calls in View | ViewModel calls Repository/Service layer |

---

## Distribution & Packaging

> [!TIP]
> This skill includes ready-to-use build scripts in the `scripts/` directory. Copy them to your project and run directly.

### Quick Start (Using Build Scripts)

**Windows:**
```batch
# Copy scripts to your project, then:
scripts\build.bat                    # Build with Nuitka (default)
scripts\build.bat pyinstaller        # Build with PyInstaller
scripts\build.bat --onefile --clean  # Single exe, clean build
```

**Linux/macOS:**
```bash
chmod +x scripts/build.sh
./scripts/build.sh                    # Build with Nuitka (default)
./scripts/build.sh pyinstaller        # Build with PyInstaller
./scripts/build.sh --onefile --clean  # Single exe, clean build
```

### Script Options

| Option | Description |
|--------|-------------|
| `--main FILE` | Entry point file (default: main.py) |
| `--name NAME` | Application name |
| `--icon FILE` | Icon file (.ico/.icns) |
| `--onefile` | Create single executable |
| `--clean` | Clean build artifacts first |
| `--framework` | Force framework (pyside6/ctk/flet) |

### Manual Commands

#### Nuitka (Recommended)

```bash
nuitka --standalone \
       --windows-disable-console \
       --enable-plugin=pyside6 \
       --include-data-dir=assets=assets \
       --output-dir=dist \
       main.py
```

#### PyInstaller (.spec template)

```python
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

---

## Starter Templates

### PySide6 Starter

```python
"""PySide6 Production Starter Template"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title = QLabel("Welcome")
        title.setFont(QFont("Segoe UI Variable", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f0f;
            }
            QLabel {
                color: #ffffff;
            }
        """)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### CustomTkinter Starter

```python
"""CustomTkinter Production Starter Template"""
import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My Application")
        self.geometry("800x600")
        self.minsize(640, 480)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
    
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, corner_radius=16)
        main_frame.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            main_frame,
            text="Welcome",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.grid(row=0, column=0, pady=(24, 16))

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
```

---

## Anti-Patterns (NEVER DO)

| ❌ Anti-Pattern | ✅ Correct Approach |
|-----------------|---------------------|
| `.place(x, y)` absolute positioning | Use `grid` or `pack` for responsiveness |
| `time.sleep()` in UI loop | Use `QThread`, `threading`, or `asyncio` |
| Hardcoded paths like `icons/logo.png` | Use `get_resource()` helper |
| Silent crashes | Implement `sys.excepthook` with GUI dialog |
| Default system fonts | Explicitly set modern font stack |
| Raw RGB colors (255, 0, 0) | Use curated hex palettes with HSL tuning |
| Theme switch without text color | **ALWAYS** set `color` property for every widget when changing theme |
| Relying on color inheritance | Explicitly set `color` for QLabel, QCheckBox, etc. |
| Only styling common widgets | Cover ALL widgets: menus, tooltips, scrollbars, headers |

---

## Theme Switching & Style Management

Modern applications must support dynamic theme switching. Implement a centralized theme manager for consistency.

### Theme Manager Pattern

```python
"""Universal Theme Manager - Works with any framework"""
import json
import os
from enum import Enum
from typing import Callable, List

class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class ThemeManager:
    _instance = None
    _listeners: List[Callable] = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_mode = ThemeMode.DARK
            cls._instance._load_preference()
        return cls._instance
    
    @property
    def current_mode(self) -> ThemeMode:
        return self._current_mode
    
    @property
    def is_dark(self) -> bool:
        if self._current_mode == ThemeMode.SYSTEM:
            return self._detect_system_theme() == "dark"
        return self._current_mode == ThemeMode.DARK
    
    def set_mode(self, mode: ThemeMode):
        self._current_mode = mode
        self._save_preference()
        self._notify_listeners()
    
    def toggle(self):
        """Toggle between light and dark mode."""
        new_mode = ThemeMode.LIGHT if self.is_dark else ThemeMode.DARK
        self.set_mode(new_mode)
    
    def add_listener(self, callback: Callable):
        self._listeners.append(callback)
    
    def _notify_listeners(self):
        for listener in self._listeners:
            listener(self.is_dark)
    
    def _detect_system_theme(self) -> str:
        """Detect OS theme preference."""
        try:
            import darkdetect
            return darkdetect.theme().lower()
        except ImportError:
            # Fallback: Windows registry check
            if os.name == 'nt':
                import winreg
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                    )
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return "light" if value else "dark"
                except:
                    pass
            return "dark"
    
    def _get_config_path(self) -> str:
        config_dir = os.path.join(os.path.expanduser("~"), ".myapp")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "theme.json")
    
    def _save_preference(self):
        with open(self._get_config_path(), 'w') as f:
            json.dump({"mode": self._current_mode.value}, f)
    
    def _load_preference(self):
        try:
            with open(self._get_config_path(), 'r') as f:
                data = json.load(f)
                self._current_mode = ThemeMode(data.get("mode", "dark"))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
```

### PySide6 Dynamic Theme Switching

> [!CAUTION]
> **CRITICAL: Text Color Must Switch With Theme!**  
> When switching themes, you MUST update both `background-color` AND `color` for ALL widgets.  
> Forgetting to update text color will make text invisible (white text on white background or black text on black background).

```python
"""PySide6 Theme Implementation - Complete Widget Coverage"""
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import Signal, QObject

class ThemeStyles:
    """
    IMPORTANT: Every widget MUST have explicit 'color' property set!
    Never rely on inheritance alone - some widgets don't inherit color properly.
    """
    
    DARK = """
        /* === BASE STYLES === */
        QMainWindow { background-color: #0f0f0f; }
        QWidget { background-color: #1a1a1a; color: #ffffff; }
        
        /* === TEXT WIDGETS - CRITICAL: Must set color! === */
        QLabel { color: #ffffff; background: transparent; }
        QLabel[secondary="true"] { color: #a0a0a0; }
        
        QLineEdit {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 8px;
            selection-background-color: #6366f1;
            selection-color: #ffffff;
        }
        QLineEdit:focus { border-color: #6366f1; }
        QLineEdit::placeholder { color: #6b7280; }
        
        QTextEdit, QPlainTextEdit {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            selection-background-color: #6366f1;
        }
        
        /* === BUTTONS === */
        QPushButton {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        QPushButton:hover { background-color: #3d3d3d; }
        QPushButton:pressed { background-color: #4d4d4d; }
        QPushButton:disabled { color: #6b7280; background-color: #1a1a1a; }
        
        QPushButton[primary="true"] {
            background-color: #6366f1;
            color: #ffffff;
            border: none;
        }
        QPushButton[primary="true"]:hover { background-color: #818cf8; }
        
        /* === LISTS & TABLES === */
        QListWidget, QListView, QTreeWidget, QTreeView {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
        }
        QListWidget::item, QTreeWidget::item {
            color: #ffffff;
            padding: 8px;
        }
        QListWidget::item:selected { background-color: #6366f1; color: #ffffff; }
        QListWidget::item:hover { background-color: #2d2d2d; }
        
        QTableWidget, QTableView {
            background-color: #1a1a1a;
            color: #ffffff;
            gridline-color: #3d3d3d;
        }
        QHeaderView::section {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            padding: 8px;
        }
        
        /* === COMBO & SPIN BOXES === */
        QComboBox {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #ffffff;
            selection-background-color: #6366f1;
        }
        
        QSpinBox, QDoubleSpinBox {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
        }
        
        /* === CHECKBOXES & RADIO === */
        QCheckBox, QRadioButton { color: #ffffff; }
        QCheckBox::indicator, QRadioButton::indicator {
            width: 18px; height: 18px;
        }
        
        /* === GROUP & TAB === */
        QGroupBox {
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
        }
        QGroupBox::title { color: #ffffff; }
        
        QTabWidget::pane { border: 1px solid #3d3d3d; }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #a0a0a0;
            padding: 8px 16px;
        }
        QTabBar::tab:selected { background-color: #1a1a1a; color: #ffffff; }
        
        /* === MENUS & TOOLTIPS === */
        QMenuBar { background-color: #1a1a1a; color: #ffffff; }
        QMenuBar::item:selected { background-color: #3d3d3d; }
        QMenu {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
        }
        QMenu::item:selected { background-color: #6366f1; }
        
        QToolTip {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
        }
        
        /* === SCROLLBARS === */
        QScrollBar:vertical, QScrollBar:horizontal {
            background-color: #1a1a1a;
        }
        QScrollBar::handle { background-color: #3d3d3d; border-radius: 4px; }
        QScrollBar::handle:hover { background-color: #4d4d4d; }
        
        /* === STATUS & PROGRESS === */
        QStatusBar { color: #a0a0a0; }
        QProgressBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk { background-color: #6366f1; }
    """
    
    LIGHT = """
        /* === BASE STYLES === */
        QMainWindow { background-color: #f5f5f5; }
        QWidget { background-color: #ffffff; color: #1a1a1a; }
        
        /* === TEXT WIDGETS - CRITICAL: Must set color! === */
        QLabel { color: #1a1a1a; background: transparent; }
        QLabel[secondary="true"] { color: #6b7280; }
        
        QLineEdit {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 8px;
            selection-background-color: #6366f1;
            selection-color: #ffffff;
        }
        QLineEdit:focus { border-color: #6366f1; }
        QLineEdit::placeholder { color: #9ca3af; }
        
        QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            selection-background-color: #6366f1;
        }
        
        /* === BUTTONS === */
        QPushButton {
            background-color: #e8e8e8;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        QPushButton:hover { background-color: #d8d8d8; }
        QPushButton:pressed { background-color: #c8c8c8; }
        QPushButton:disabled { color: #9ca3af; background-color: #f0f0f0; }
        
        QPushButton[primary="true"] {
            background-color: #4f46e5;
            color: #ffffff;
            border: none;
        }
        QPushButton[primary="true"]:hover { background-color: #6366f1; }
        
        /* === LISTS & TABLES === */
        QListWidget, QListView, QTreeWidget, QTreeView {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
        }
        QListWidget::item, QTreeWidget::item {
            color: #1a1a1a;
            padding: 8px;
        }
        QListWidget::item:selected { background-color: #6366f1; color: #ffffff; }
        QListWidget::item:hover { background-color: #f0f0f0; }
        
        QTableWidget, QTableView {
            background-color: #ffffff;
            color: #1a1a1a;
            gridline-color: #e0e0e0;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            padding: 8px;
        }
        
        /* === COMBO & SPIN BOXES === */
        QComboBox {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #1a1a1a;
            selection-background-color: #6366f1;
            selection-color: #ffffff;
        }
        
        QSpinBox, QDoubleSpinBox {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
        }
        
        /* === CHECKBOXES & RADIO === */
        QCheckBox, QRadioButton { color: #1a1a1a; }
        
        /* === GROUP & TAB === */
        QGroupBox {
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
        }
        QGroupBox::title { color: #1a1a1a; }
        
        QTabWidget::pane { border: 1px solid #d0d0d0; }
        QTabBar::tab {
            background-color: #f0f0f0;
            color: #6b7280;
            padding: 8px 16px;
        }
        QTabBar::tab:selected { background-color: #ffffff; color: #1a1a1a; }
        
        /* === MENUS & TOOLTIPS === */
        QMenuBar { background-color: #ffffff; color: #1a1a1a; }
        QMenuBar::item:selected { background-color: #e8e8e8; }
        QMenu {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
        }
        QMenu::item:selected { background-color: #6366f1; color: #ffffff; }
        
        QToolTip {
            background-color: #1a1a1a;
            color: #ffffff;
            border: none;
        }
        
        /* === SCROLLBARS === */
        QScrollBar:vertical, QScrollBar:horizontal {
            background-color: #f0f0f0;
        }
        QScrollBar::handle { background-color: #c0c0c0; border-radius: 4px; }
        QScrollBar::handle:hover { background-color: #a0a0a0; }
        
        /* === STATUS & PROGRESS === */
        QStatusBar { color: #6b7280; }
        QProgressBar {
            background-color: #e8e8e8;
            color: #1a1a1a;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk { background-color: #4f46e5; }
    """

class QtThemeManager(QObject):
    theme_changed = Signal(bool)  # Emits True for dark mode
    
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.theme_manager = ThemeManager()
        self.theme_manager.add_listener(self._on_theme_change)
        self.apply_theme()
    
    def apply_theme(self):
        style = ThemeStyles.DARK if self.theme_manager.is_dark else ThemeStyles.LIGHT
        self.app.setStyleSheet(style)
    
    def toggle(self):
        self.theme_manager.toggle()
    
    def _on_theme_change(self, is_dark: bool):
        self.apply_theme()
        self.theme_changed.emit(is_dark)

# Usage in MainWindow
class MainWindow(QMainWindow):
    def __init__(self, theme_mgr: QtThemeManager):
        super().__init__()
        self.theme_mgr = theme_mgr
        self.theme_mgr.theme_changed.connect(self._on_theme_changed)
        
        # Theme toggle button
        self.theme_btn = QPushButton("🌓 Toggle Theme")
        self.theme_btn.clicked.connect(self.theme_mgr.toggle)
    
    def _on_theme_changed(self, is_dark: bool):
        # Update any theme-specific icons or assets
        icon = "moon.svg" if is_dark else "sun.svg"
        # self.theme_btn.setIcon(QIcon(get_resource(f"assets/{icon}")))
```

### CustomTkinter Theme Switching

> [!IMPORTANT]
> **CustomTkinter handles text colors automatically!**  
> Unlike PySide6, `ctk.set_appearance_mode()` updates both backgrounds AND text colors.  
> However, if you use custom `text_color` parameters, you MUST update them manually on theme change.

```python
"""CustomTkinter Theme Implementation - Complete Example"""
import customtkinter as ctk

class CTkThemeManager:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.theme_manager = ThemeManager()
        self.theme_manager.add_listener(self._on_theme_change)
        self._themed_widgets = []  # Track widgets with custom colors
        self.apply_theme()
    
    def apply_theme(self):
        mode = "dark" if self.theme_manager.is_dark else "light"
        ctk.set_appearance_mode(mode)
        self._update_custom_colored_widgets()
    
    def toggle(self):
        self.theme_manager.toggle()
    
    def register_themed_widget(self, widget, dark_text="#ffffff", light_text="#1a1a1a"):
        """Register widgets with custom text colors for manual updates."""
        self._themed_widgets.append((widget, dark_text, light_text))
    
    def _update_custom_colored_widgets(self):
        """Update text color for widgets with custom styling."""
        for widget, dark_text, light_text in self._themed_widgets:
            color = dark_text if self.theme_manager.is_dark else light_text
            try:
                widget.configure(text_color=color)
            except:
                pass  # Some widgets may not support text_color
    
    def _on_theme_change(self, is_dark: bool):
        self.apply_theme()

# Usage with proper text color handling
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme_mgr = CTkThemeManager(self)
        
        # Standard widgets - colors update automatically
        self.label = ctk.CTkLabel(self, text="Auto-themed label")
        self.label.pack(pady=10)
        
        # Custom colored widget - must register for manual updates
        self.custom_label = ctk.CTkLabel(
            self,
            text="Custom colored label",
            text_color="#ff6b6b"  # Custom color that needs updating
        )
        self.custom_label.pack(pady=10)
        # Register for theme-aware color switching
        self.theme_mgr.register_themed_widget(
            self.custom_label,
            dark_text="#ff6b6b",   # Red on dark
            light_text="#dc2626"  # Darker red on light
        )
        
        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            self,
            text="🌓",
            width=40,
            command=self.theme_mgr.toggle
        )
        self.theme_btn.pack(anchor="ne", padx=10, pady=10)
```

### Flet Theme Switching & Component Architecture

> [!WARNING]
> **Flet is DECLARATIVE, not imperative like Qt!**  
> Avoid putting all code in a single `main()` function. Use `UserControl` classes to organize components.

#### Flet Component Pattern (UserControl)

```python
"""Flet Component Architecture - ALWAYS use UserControl for reusable components"""
import flet as ft

class ThemedCard(ft.UserControl):
    """Reusable card component with proper state management."""
    
    def __init__(self, title: str, content: str):
        super().__init__()
        self.title = title
        self.content = content
        self._expanded = False
    
    def build(self):
        self.title_text = ft.Text(self.title, size=18, weight=ft.FontWeight.BOLD)
        self.content_text = ft.Text(self.content, visible=self._expanded)
        self.expand_btn = ft.IconButton(
            icon=ft.icons.EXPAND_MORE,
            on_click=self._toggle_expand
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([self.title_text, self.expand_btn]),
                self.content_text
            ]),
            padding=16,
            border_radius=12,
            bgcolor=ft.colors.SURFACE_VARIANT
        )
    
    def _toggle_expand(self, e):
        self._expanded = not self._expanded
        self.content_text.visible = self._expanded
        self.expand_btn.icon = (
            ft.icons.EXPAND_LESS if self._expanded else ft.icons.EXPAND_MORE
        )
        self.update()


class AppView(ft.UserControl):
    """Main application view - encapsulates the entire UI."""
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
    
    def build(self):
        self.status_text = ft.Text("Ready", size=24)
        self.cards = ft.Column([
            ThemedCard("Card 1", "This is the content of card 1"),
            ThemedCard("Card 2", "This is the content of card 2"),
        ], spacing=12)
        
        return ft.Container(
            content=ft.Column([
                self.status_text,
                self.cards,
                ft.ElevatedButton("Load Data", on_click=self._on_load_click)
            ], spacing=16),
            padding=24
        )
    
    def _on_load_click(self, e):
        self.status_text.value = "Loading..."
        self.update()
        # Simulate async work
        import asyncio
        asyncio.create_task(self._load_data_async())
    
    async def _load_data_async(self):
        import asyncio
        await asyncio.sleep(1)  # Simulate network call
        self.status_text.value = "Data loaded!"
        self.update()


def main(page: ft.Page):
    """Entry point - keep this minimal, delegate to UserControls."""
    theme_manager = ThemeManager()
    
    # Theme setup
    def apply_theme():
        page.theme_mode = ft.ThemeMode.DARK if theme_manager.is_dark else ft.ThemeMode.LIGHT
        page.update()
    
    def toggle_theme(e):
        theme_manager.toggle()
        apply_theme()
        # Update icon
        theme_btn.icon = (
            ft.icons.LIGHT_MODE if theme_manager.is_dark else ft.icons.DARK_MODE
        )
        page.update()
    
    # AppBar with theme toggle
    theme_btn = ft.IconButton(
        icon=ft.icons.DARK_MODE if theme_manager.is_dark else ft.icons.LIGHT_MODE,
        on_click=toggle_theme,
        tooltip="Toggle theme"
    )
    
    page.appbar = ft.AppBar(
        title=ft.Text("My App"),
        center_title=True,
        actions=[theme_btn]
    )
    
    # Main view - all UI logic in UserControl
    app_view = AppView(theme_manager)
    page.add(app_view)
    
    apply_theme()

ft.app(target=main)
```

#### Flet Best Practices

| ❌ Anti-Pattern | ✅ Correct Approach |
|-----------------|---------------------|
| All logic in `main()` function | Use `UserControl` subclasses for components |
| Storing widgets in global variables | Store in `self.` within `UserControl` |
| Direct `page.add()` for every widget | Create component hierarchy, add root only |
| `time.sleep()` for async work | Use `asyncio.create_task()` and `await` |
| Manual color switching | Use `page.theme_mode` + Material Design tokens |

### System Theme Auto-Follow (Optional)

```python
"""Auto-follow system theme changes (requires darkdetect)"""
# pip install darkdetect

import darkdetect
import threading

def start_system_theme_listener(callback):
    """Listen for OS theme changes in background."""
    def listener():
        darkdetect.listener(callback)
    
    thread = threading.Thread(target=listener, daemon=True)
    thread.start()

# Usage with ThemeManager
theme_manager = ThemeManager()
theme_manager.set_mode(ThemeMode.SYSTEM)

def on_system_theme_change(new_theme):
    # Refresh UI when system theme changes
    theme_manager._notify_listeners()

start_system_theme_listener(on_system_theme_change)
```

### Theme-Aware Color Palette

```python
"""Semantic color system that adapts to theme"""

class Colors:
    @staticmethod
    def get(is_dark: bool) -> dict:
        if is_dark:
            return {
                "bg_primary": "#0f0f0f",
                "bg_secondary": "#1a1a1a",
                "bg_tertiary": "#2d2d2d",
                "text_primary": "#ffffff",
                "text_secondary": "#a0a0a0",
                "accent": "#6366f1",
                "accent_hover": "#818cf8",
                "border": "#3d3d3d",
                "success": "#22c55e",
                "warning": "#f59e0b",
                "error": "#ef4444",
            }
        else:
            return {
                "bg_primary": "#ffffff",
                "bg_secondary": "#f5f5f5",
                "bg_tertiary": "#e8e8e8",
                "text_primary": "#1a1a1a",
                "text_secondary": "#6b7280",
                "accent": "#4f46e5",
                "accent_hover": "#6366f1",
                "border": "#d0d0d0",
                "success": "#16a34a",
                "warning": "#d97706",
                "error": "#dc2626",
            }

# Usage
colors = Colors.get(theme_manager.is_dark)
button_style = f"background-color: {colors['accent']};"
```

### Theme-Aware Icon Management

> [!CAUTION]
> **Icons MUST adapt to theme!**  
> Black icons on dark backgrounds and white icons on light backgrounds are invisible.  
> Always provide light/dark icon variants OR use dynamic SVG coloring.

#### Strategy 1: Light/Dark Icon Variants (Recommended)

Organize your assets folder with theme variants:

```text
assets/
├── icons/
│   ├── light/          # Icons for LIGHT theme (dark icons)
│   │   ├── settings.svg
│   │   ├── home.svg
│   │   └── user.svg
│   └── dark/           # Icons for DARK theme (light icons)
│       ├── settings.svg
│       ├── home.svg
│       └── user.svg
```

#### Icon Manager (Universal)

```python
"""Theme-Aware Icon Manager"""
import os

class IconManager:
    """Automatically loads correct icon variant based on theme."""
    
    def __init__(self, base_path: str = "assets/icons"):
        self.base_path = base_path
        self._is_dark = True
    
    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
    
    def get_icon_path(self, icon_name: str) -> str:
        """Get icon path for current theme."""
        theme_folder = "dark" if self._is_dark else "light"
        return os.path.join(self.base_path, theme_folder, f"{icon_name}.svg")
    
    def get_icon(self, icon_name: str):
        """Get QIcon/PhotoImage based on framework."""
        path = self.get_icon_path(icon_name)
        
        # For PySide6
        from PySide6.QtGui import QIcon
        return QIcon(path)

# Usage
icon_manager = IconManager()
theme_manager.add_listener(lambda is_dark: icon_manager.set_theme(is_dark))
```

#### Strategy 2: Dynamic SVG Coloring (PySide6)

For single-color icons, dynamically recolor SVG content:

```python
"""Dynamic SVG Icon Coloring for PySide6"""
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, Qt

class ThemedIcon:
    """Creates QIcon with dynamic color based on theme."""
    
    @staticmethod
    def from_svg(svg_path: str, color: str, size: int = 24) -> QIcon:
        """Load SVG and apply color tint."""
        # Read SVG content
        with open(svg_path, 'r') as f:
            svg_content = f.read()
        
        # Replace fill/stroke colors (works for simple SVGs)
        # For complex SVGs, use currentColor in the SVG source
        svg_content = svg_content.replace('fill="black"', f'fill="{color}"')
        svg_content = svg_content.replace('fill="#000"', f'fill="{color}"')
        svg_content = svg_content.replace('stroke="black"', f'stroke="{color}"')
        
        # Render to pixmap
        renderer = QSvgRenderer(QByteArray(svg_content.encode()))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    @staticmethod
    def get_themed(svg_path: str, is_dark: bool, size: int = 24) -> QIcon:
        """Get icon with appropriate color for theme."""
        color = "#ffffff" if is_dark else "#1a1a1a"
        return ThemedIcon.from_svg(svg_path, color, size)

# Usage in MainWindow
def _on_theme_changed(self, is_dark: bool):
    icon_color = "#ffffff" if is_dark else "#1a1a1a"
    self.settings_btn.setIcon(ThemedIcon.from_svg("assets/settings.svg", icon_color))
    self.home_btn.setIcon(ThemedIcon.from_svg("assets/home.svg", icon_color))
```

#### CustomTkinter Icon Switching

```python
"""Theme-Aware Icons for CustomTkinter"""
from PIL import Image
import customtkinter as ctk

class CTkThemedIcon:
    """Manages light/dark icon variants for CustomTkinter."""
    
    def __init__(self, icon_name: str, size: tuple = (24, 24)):
        self.icon_name = icon_name
        self.size = size
        self._light_image = None
        self._dark_image = None
        self._load_images()
    
    def _load_images(self):
        light_path = f"assets/icons/light/{self.icon_name}.png"
        dark_path = f"assets/icons/dark/{self.icon_name}.png"
        
        self._light_image = ctk.CTkImage(
            light_image=Image.open(light_path),
            dark_image=Image.open(dark_path),
            size=self.size
        )
    
    @property
    def image(self) -> ctk.CTkImage:
        """CTkImage automatically switches based on appearance mode."""
        return self._light_image

# Usage - CTkImage handles theme switching automatically!
settings_icon = CTkThemedIcon("settings")
settings_btn = ctk.CTkButton(
    master=self,
    image=settings_icon.image,  # Auto-switches with theme
    text="Settings",
    compound="left"
)
```

> [!TIP]
> **CustomTkinter's `CTkImage` is magic!**  
> Pass both `light_image` and `dark_image` parameters, and it automatically switches when you call `ctk.set_appearance_mode()`.

#### Icon Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct Approach |
|-----------------|---------------------|
| Single icon for all themes | Provide light/dark variants OR dynamic coloring |
| Black-only SVG icons | Use `currentColor` in SVG or recolor dynamically |
| Hardcoded icon colors | Use `IconManager.get_icon()` with theme awareness |
| PNG icons for all sizes | Use SVG for scalability, PNG only for complex images |
| Ignoring icon colors on theme switch | Register icons with `ThemeManager.add_listener()` |

### Additional Theme-Sensitive Elements

> [!WARNING]
> **Don't forget these often-overlooked elements!**  
> The following UI elements are frequently missed during theme implementation.

#### 1. Cursor/Caret Color (PySide6)

The text cursor in input fields may be invisible if not styled:

```python
# In your QSS stylesheet
QLineEdit, QTextEdit, QPlainTextEdit {
    /* For Qt 5.12+ */
    qproperty-cursorColor: #ffffff;  /* Dark theme */
}
```

For older Qt versions or dynamic switching:
```python
from PySide6.QtGui import QPalette, QColor

def set_cursor_color(widget, color: str):
    """Set text cursor color for input widgets."""
    palette = widget.palette()
    palette.setColor(QPalette.Text, QColor(color))
    widget.setPalette(palette)
```

#### 2. Hyperlink Colors

Links in QLabel or rich text become invisible if not styled:

```python
# QSS for links
QLabel {
    /* Link colors */
}

# Or set via palette
palette.setColor(QPalette.Link, QColor("#6366f1"))        # Normal
palette.setColor(QPalette.LinkVisited, QColor("#818cf8"))  # Visited
```

For HTML content in QLabel:
```python
# Dark theme
label.setText('<a href="..." style="color: #6366f1;">Link</a>')

# Better: Use CSS classes
label.setStyleSheet("QLabel a { color: #6366f1; }")
```

#### 3. Focus Ring/Indicator

Focus borders must be visible in both themes:

```python
# Dark theme QSS
*:focus {
    outline: 2px solid #6366f1;
    outline-offset: 2px;
}

QLineEdit:focus, QPushButton:focus {
    border: 2px solid #6366f1;
}

# Light theme - may need darker color
QLineEdit:focus {
    border: 2px solid #4f46e5;
}
```

#### 4. Separators and Dividers

QFrame separators need explicit colors:

```python
# QSS
QFrame[frameShape="HLine"], QFrame[frameShape="VLine"] {
    background-color: #3d3d3d;  /* Dark theme */
    /* background-color: #d0d0d0;  Light theme */
}

# CustomTkinter
separator = ctk.CTkFrame(master, height=1, fg_color=("gray70", "gray30"))
```

#### 5. Chart/Graph Theming (Matplotlib)

If using matplotlib for data visualization:

```python
"""Theme-Aware Matplotlib Integration"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

def apply_chart_theme(is_dark: bool):
    """Apply theme to matplotlib figures."""
    if is_dark:
        plt.style.use('dark_background')
        params = {
            'figure.facecolor': '#1a1a1a',
            'axes.facecolor': '#1a1a1a',
            'axes.edgecolor': '#3d3d3d',
            'axes.labelcolor': '#ffffff',
            'text.color': '#ffffff',
            'xtick.color': '#a0a0a0',
            'ytick.color': '#a0a0a0',
            'grid.color': '#3d3d3d',
            'legend.facecolor': '#2d2d2d',
            'legend.edgecolor': '#3d3d3d',
        }
    else:
        plt.style.use('default')
        params = {
            'figure.facecolor': '#ffffff',
            'axes.facecolor': '#ffffff',
            'axes.edgecolor': '#d0d0d0',
            'axes.labelcolor': '#1a1a1a',
            'text.color': '#1a1a1a',
            'xtick.color': '#6b7280',
            'ytick.color': '#6b7280',
            'grid.color': '#e0e0e0',
            'legend.facecolor': '#f5f5f5',
            'legend.edgecolor': '#d0d0d0',
        }
    
    plt.rcParams.update(params)

# Register with theme manager
theme_manager.add_listener(apply_chart_theme)
```

#### 6. Theme Transition Animation (Optional)

For smooth theme switching instead of jarring instant change:

```python
"""Smooth Theme Transition for PySide6"""
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsOpacityEffect

class SmoothThemeSwitcher:
    """Fade transition when switching themes."""
    
    def __init__(self, main_window):
        self.window = main_window
        self.effect = QGraphicsOpacityEffect(main_window)
        main_window.setGraphicsEffect(self.effect)
    
    def switch_theme(self, apply_new_theme_func):
        """Fade out, apply theme, fade in."""
        # Fade out
        self.fade_out = QPropertyAnimation(self.effect, b"opacity")
        self.fade_out.setDuration(150)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.3)
        self.fade_out.setEasingCurve(QEasingCurve.OutQuad)
        
        def on_fade_out_done():
            apply_new_theme_func()
            # Fade in
            self.fade_in = QPropertyAnimation(self.effect, b"opacity")
            self.fade_in.setDuration(150)
            self.fade_in.setStartValue(0.3)
            self.fade_in.setEndValue(1.0)
            self.fade_in.setEasingCurve(QEasingCurve.InQuad)
            self.fade_in.start()
        
        self.fade_out.finished.connect(on_fade_out_done)
        self.fade_out.start()
```

#### 7. Print/Export Considerations

When printing or exporting, force light theme for readability:

```python
def prepare_for_print(widget):
    """Temporarily switch to light theme for printing."""
    original_theme = theme_manager.is_dark
    
    if original_theme:
        theme_manager.set_mode(ThemeMode.LIGHT)
    
    # Do printing...
    yield
    
    # Restore original theme
    if original_theme:
        theme_manager.set_mode(ThemeMode.DARK)

# Usage with context manager
import contextlib

@contextlib.contextmanager
def print_mode():
    original = theme_manager.current_mode
    theme_manager.set_mode(ThemeMode.LIGHT)
    try:
        yield
    finally:
        theme_manager.set_mode(original)

# Usage
with print_mode():
    printer.print(document)
```

---

## Common UI Components

### Modern Card Component (PySide6)

```python
class Card(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            Card {
                background-color: #1a1a1a;
                border-radius: 12px;
                border: 1px solid #2a2a2a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI Variable", 14, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)
```

### Animated Button (CustomTkinter)

```python
class AnimatedButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_color = self.cget("fg_color")
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(fg_color=self._lighten_color(self.default_color))
    
    def _on_leave(self, event):
        self.configure(fg_color=self.default_color)
    
    def _lighten_color(self, color):
        # Simple color lightening for hover effect
        if isinstance(color, tuple):
            return color[0]  # Return first color for simplicity
        return color
```

---

## UX Enhancement Pack (The Final 5%)

> [!TIP]
> **These details separate "functional" from "professional".**  
> Implement these micro-interactions and state persistence features to achieve world-class desktop UX.

### 1. Window State Persistence

> [!IMPORTANT]
> **Don't frustrate users!** Always restore window size and position from the previous session.  
> This is the #1 "professional feel" feature that most apps overlook.

```python
"""Window State Manager (PySide6)"""
from PySide6.QtCore import QSettings, QByteArray
from PySide6.QtWidgets import QMainWindow

class WindowStateManager:
    """Automatically saves and restores window geometry and state."""
    
    def __init__(self, window: QMainWindow, app_name: str = "MyApp"):
        self.window = window
        self.settings = QSettings(app_name, "MainWindow")
    
    def restore(self):
        """Call this in __init__ after setup_ui()."""
        geometry = self.settings.value("geometry")
        state = self.settings.value("windowState")
        
        if geometry and isinstance(geometry, QByteArray):
            self.window.restoreGeometry(geometry)
        if state and isinstance(state, QByteArray):
            self.window.restoreState(state)
    
    def save(self):
        """Call this in closeEvent()."""
        self.settings.setValue("geometry", self.window.saveGeometry())
        self.settings.setValue("windowState", self.window.saveState())

# Integration with MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state_manager = WindowStateManager(self)
        self.setup_ui()
        self.state_manager.restore()  # Restore after UI setup
    
    def closeEvent(self, event):
        self.state_manager.save()
        super().closeEvent(event)
```

**CustomTkinter Version:**
```python
"""Window State for CustomTkinter"""
import json
import os

class CTkWindowState:
    def __init__(self, root, config_file="~/.myapp/window.json"):
        self.root = root
        self.config_path = os.path.expanduser(config_file)
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
    
    def restore(self):
        try:
            with open(self.config_path, 'r') as f:
                state = json.load(f)
                self.root.geometry(state.get("geometry", "800x600"))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    def save(self):
        state = {"geometry": self.root.geometry()}
        with open(self.config_path, 'w') as f:
            json.dump(state, f)

# Usage
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.window_state = CTkWindowState(self)
        self.window_state.restore()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_close(self):
        self.window_state.save()
        self.destroy()
```

### 2. Non-Modal Toast Notifications

> [!NOTE]
> **Stop using Message Boxes for success messages!**  
> Use non-intrusive Toasts/Snackbars for "Saved", "Connected", "Copied" feedback.

```python
"""Modern Toast Notification (PySide6)"""
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect, QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint

class Toast(QLabel):
    """Non-modal notification that auto-dismisses."""
    
    # Style presets
    STYLES = {
        "success": {"bg": "#22c55e", "icon": "✓"},
        "error":   {"bg": "#ef4444", "icon": "✕"},
        "warning": {"bg": "#f59e0b", "icon": "⚠"},
        "info":    {"bg": "#3b82f6", "icon": "ℹ"},
    }
    
    def __init__(self, parent: QWidget, message: str, 
                 style: str = "success", duration: int = 2500):
        super().__init__(parent)
        
        preset = self.STYLES.get(style, self.STYLES["info"])
        icon = preset["icon"]
        bg = preset["bg"]
        
        self.setText(f" {icon}  {message} ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        self.adjustSize()
        
        # Position at bottom center of parent
        self._position_toast()
        
        # Fade-in animation
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        
        self.fade_anim = QPropertyAnimation(self.effect, b"opacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.show()
        self.fade_anim.start()
        
        # Schedule fade-out
        QTimer.singleShot(duration, self._fade_out)
    
    def _position_toast(self):
        parent_rect = self.parent().rect()
        x = (parent_rect.width() - self.width()) // 2
        y = parent_rect.height() - self.height() - 50
        self.move(x, y)
    
    def _fade_out(self):
        self.fade_anim.setDirection(QPropertyAnimation.Backward)
        self.fade_anim.finished.connect(self.deleteLater)
        self.fade_anim.start()

# Usage
def on_save_success(self):
    Toast(self, "Settings saved successfully", style="success")

def on_connection_lost(self):
    Toast(self, "Connection lost. Retrying...", style="warning", duration=4000)
```

### 3. Loading State Management

> [!CAUTION]
> **Prevent Double Submission!**  
> Always disable buttons and show loading indicators during async operations.

```python
"""Busy Indicator Utilities"""
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QObject, Signal
from functools import wraps

class BusyButton(QPushButton):
    """Button that shows loading state and prevents double-clicks."""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._original_text = text
        self._is_busy = False
    
    def set_busy(self, busy: bool, loading_text: str = "Processing..."):
        self._is_busy = busy
        self.setEnabled(not busy)
        self.setText(f"⏳ {loading_text}" if busy else self._original_text)
    
    @property
    def is_busy(self) -> bool:
        return self._is_busy

# Decorator for async operations
def with_loading(button_attr: str, loading_text: str = "Loading..."):
    """
    Decorator that manages button loading state.
    
    Usage:
        @with_loading("my_button", "Saving...")
        def on_save_clicked(self):
            # Do async work
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            button = getattr(self, button_attr)
            button.set_busy(True, loading_text)
            try:
                return func(self, *args, **kwargs)
            finally:
                # Note: For truly async operations, call set_busy(False) in callback
                pass
        return wrapper
    return decorator

# For thread-based operations, use signal to restore state
class AsyncTaskRunner(QObject):
    """Run task in thread with automatic button state management."""
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, button: BusyButton):
        super().__init__()
        self.button = button
        self.finished.connect(self._on_complete)
        self.error.connect(self._on_complete)
    
    def run(self, task_func, loading_text="Processing..."):
        self.button.set_busy(True, loading_text)
        # Start worker thread...
    
    def _on_complete(self, result=None):
        self.button.set_busy(False)
```

### 4. Keyboard Shortcuts & Accessibility

> [!IMPORTANT]
> **Productivity apps MUST support keyboard shortcuts!**  
> Define standard shortcuts (Ctrl+S, Ctrl+Q, Esc) and document them.

```python
"""Keyboard Shortcut Manager (PySide6)"""
from PySide6.QtWidgets import QShortcut, QMainWindow
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt

class ShortcutManager:
    """Centralized keyboard shortcut management."""
    
    # Standard shortcuts that every app should have
    STANDARD_SHORTCUTS = {
        "save":     "Ctrl+S",
        "open":     "Ctrl+O",
        "quit":     "Ctrl+Q",
        "undo":     "Ctrl+Z",
        "redo":     "Ctrl+Shift+Z",
        "settings": "Ctrl+,",
        "help":     "F1",
        "close":    "Esc",
        "refresh":  "F5",
        "find":     "Ctrl+F",
    }
    
    def __init__(self, window: QMainWindow):
        self.window = window
        self._shortcuts = {}
    
    def register(self, name: str, callback, key_sequence: str = None):
        """Register a shortcut with optional custom key sequence."""
        key = key_sequence or self.STANDARD_SHORTCUTS.get(name)
        if not key:
            raise ValueError(f"Unknown shortcut: {name}")
        
        shortcut = QShortcut(QKeySequence(key), self.window)
        shortcut.activated.connect(callback)
        self._shortcuts[name] = shortcut
        return shortcut
    
    def register_standard(self, callbacks: dict):
        """
        Register multiple standard shortcuts at once.
        
        Usage:
            shortcuts.register_standard({
                "save": self.on_save,
                "quit": self.close,
                "settings": self.open_settings,
            })
        """
        for name, callback in callbacks.items():
            self.register(name, callback)

# Usage in MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        self.shortcuts = ShortcutManager(self)
        self.shortcuts.register_standard({
            "save": self.on_save,
            "quit": self.close,
            "settings": self.open_settings,
            "refresh": self.refresh_data,
        })
        # Custom shortcut
        self.shortcuts.register("toggle_theme", self.toggle_theme, "Ctrl+T")
```

**CustomTkinter Shortcuts:**
```python
"""Keyboard Bindings for CustomTkinter"""
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        self.bind("<Control-s>", lambda e: self.on_save())
        self.bind("<Control-q>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.on_escape())
        self.bind("<F5>", lambda e: self.refresh())
        self.bind("<Control-comma>", lambda e: self.open_settings())
```

#### Shortcut Discoverability (CRITICAL!)

> [!CAUTION]
> **Shortcuts are useless if users don't know they exist!**  
> Always expose shortcuts through Tooltips, Menus, and Help dialogs.

**Method 1: Tooltips with Shortcut Hints**
```python
# PySide6 - Add shortcut to tooltip
save_btn = QPushButton("Save")
save_btn.setToolTip("Save document (Ctrl+S)")  # Include shortcut in tooltip!

# CustomTkinter
save_btn = ctk.CTkButton(master, text="Save")
# CTk doesn't have native tooltips, use CTkToolTip or hover binding
```

**Method 2: Menu Items with Shortcuts**
```python
# PySide6 - Menus automatically show shortcut text
file_menu = menubar.addMenu("&File")

save_action = file_menu.addAction("&Save")
save_action.setShortcut(QKeySequence("Ctrl+S"))  # Shows "Ctrl+S" in menu!
save_action.triggered.connect(self.on_save)

quit_action = file_menu.addAction("&Quit")
quit_action.setShortcut(QKeySequence("Ctrl+Q"))
quit_action.triggered.connect(self.close)
```

**Method 3: Keyboard Shortcuts Help Dialog**
```python
"""Shortcuts Help Dialog (PySide6)"""
class ShortcutsHelpDialog(QDialog):
    def __init__(self, shortcuts: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Create shortcuts table
        table = QTableWidget(len(shortcuts), 2)
        table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        
        for row, (action, key) in enumerate(shortcuts.items()):
            table.setItem(row, 0, QTableWidgetItem(action))
            table.setItem(row, 1, QTableWidgetItem(key))
        
        layout.addWidget(table)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

# Usage - bind to F1 or Help menu
SHORTCUTS_HELP = {
    "Save": "Ctrl+S",
    "Open": "Ctrl+O",
    "Quit": "Ctrl+Q",
    "Undo": "Ctrl+Z",
    "Redo": "Ctrl+Shift+Z",
    "Settings": "Ctrl+,",
    "Refresh": "F5",
    "Show Shortcuts": "F1",
}

def show_shortcuts_help(self):
    dialog = ShortcutsHelpDialog(SHORTCUTS_HELP, self)
    dialog.exec()

# Register F1 to show help
self.shortcuts.register("help", self.show_shortcuts_help)
```

**Method 4: Status Bar Hints**
```python
# Show shortcut hint in status bar on hover
def eventFilter(self, obj, event):
    if event.type() == QEvent.Enter:
        if obj == self.save_btn:
            self.statusBar().showMessage("Save document (Ctrl+S)", 3000)
    return super().eventFilter(obj, event)
```

### UX Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct Approach |
|-----------------|---------------------|
| Window always opens at default size | Save/restore geometry with `QSettings` |
| `QMessageBox` for "Saved!" confirmation | Use non-modal `Toast` notification |
| Button stays enabled during async task | Disable + show loading indicator |
| No keyboard shortcuts | Define `Ctrl+S`, `Ctrl+Q`, `Esc` at minimum |
| Shortcuts exist but not documented | Show in Tooltips, Menus, and F1 Help dialog |
| Loading state shows "Loading..." text only | Use spinner icon + disabled state |
| User must click to dismiss success message | Auto-dismiss Toast after 2-3 seconds |

---

## Quick Reference

```text
✓ MVVM Architecture
✓ MVVM Data Binding (Property + Signal)
✓ 60FPS UI Thread Rule
✓ Resource Path Manager
✓ Windows High-DPI Awareness
✓ Global Error Handler
✓ Modern Typography
✓ Dark Mode Default
✓ Grid/Pack Layout Only
✓ Production Build Config
✓ Theme Manager (Light/Dark/System)
✓ Theme Preference Persistence
✓ Theme Text Color Sync
✓ Theme-Aware Icons (Light/Dark variants)
✓ Theme Cursor/Caret Color
✓ Theme Hyperlink Colors
✓ Theme Focus Ring/Indicator
✓ Theme Chart/Graph Coloring
✓ Semantic Color Palette
✓ Flet UserControl Pattern
✓ Window State Persistence
✓ Non-Modal Toast Notifications
✓ Loading State Management
✓ Keyboard Shortcuts (Ctrl+S, Esc, etc.)
```