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
- **High-DPI**: Must include DPI awareness code (e.g., `ctk.set_appearance_mode` or `Qt.HighDpiScaleFactorRoundingPolicy`).
- **Visual Depth**: Use 8px/16px grids, rounded corners (8-12px), and subtle border glows or layered transparencies.
- **Color Palette**: Use curated palettes, not default system colors. Consider dark mode by default.

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

```python
"""PySide6 Theme Implementation"""
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import Signal, QObject

class ThemeStyles:
    DARK = """
        QMainWindow { background-color: #0f0f0f; }
        QWidget { background-color: #1a1a1a; color: #ffffff; }
        QPushButton {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            padding: 8px 16px;
        }
        QPushButton:hover { background-color: #3d3d3d; }
        QLineEdit {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
        }
    """
    
    LIGHT = """
        QMainWindow { background-color: #f5f5f5; }
        QWidget { background-color: #ffffff; color: #1a1a1a; }
        QPushButton {
            background-color: #e8e8e8;
            color: #1a1a1a;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            padding: 8px 16px;
        }
        QPushButton:hover { background-color: #d8d8d8; }
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 8px;
            color: #1a1a1a;
        }
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

```python
"""CustomTkinter Theme Implementation"""
import customtkinter as ctk

class CTkThemeManager:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.theme_manager = ThemeManager()
        self.theme_manager.add_listener(self._on_theme_change)
        self.apply_theme()
    
    def apply_theme(self):
        mode = "dark" if self.theme_manager.is_dark else "light"
        ctk.set_appearance_mode(mode)
    
    def toggle(self):
        self.theme_manager.toggle()
    
    def _on_theme_change(self, is_dark: bool):
        self.apply_theme()

# Usage
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme_mgr = CTkThemeManager(self)
        
        # Theme toggle button with icon
        self.theme_btn = ctk.CTkButton(
            self,
            text="🌓",
            width=40,
            command=self.theme_mgr.toggle
        )
        self.theme_btn.pack(anchor="ne", padx=10, pady=10)
```

### Flet Theme Switching

```python
"""Flet Theme Implementation"""
import flet as ft

def main(page: ft.Page):
    theme_manager = ThemeManager()
    
    def apply_theme():
        page.theme_mode = ft.ThemeMode.DARK if theme_manager.is_dark else ft.ThemeMode.LIGHT
        page.update()
    
    def toggle_theme(e):
        theme_manager.toggle()
        apply_theme()
    
    # Theme toggle button
    theme_button = ft.IconButton(
        icon=ft.icons.DARK_MODE if theme_manager.is_dark else ft.icons.LIGHT_MODE,
        on_click=toggle_theme,
        tooltip="Toggle theme"
    )
    
    page.appbar = ft.AppBar(
        title=ft.Text("My App"),
        actions=[theme_button]
    )
    
    apply_theme()

ft.app(target=main)
```

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

## Quick Reference

```text
✓ MVVM Architecture
✓ 60FPS UI Thread Rule
✓ Resource Path Manager
✓ DPI Awareness
✓ Global Error Handler
✓ Modern Typography
✓ Dark Mode Default
✓ Grid/Pack Layout Only
✓ Production Build Config
✓ Theme Manager (Light/Dark/System)
✓ Theme Preference Persistence
✓ Semantic Color Palette
```