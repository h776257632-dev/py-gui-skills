I understand. To make this a functional **Skill** for an AI Agent (like Cursor, Windsurf, or a custom LLM), it needs to be in **English** and provided as a **single, clean, copyable block** that includes the YAML metadata and the full technical specification.

Copy the entire block below and save it as `python-gui-engineering.md`:

```markdown
---
name: python-gui-engineering
description: Create production-grade Python desktop interfaces with high design quality and robust engineering. Use this skill when the user asks to build desktop applications, dashboards, or system utilities. Generates high-performance, visually refined code (PySide6, CustomTkinter, Flet) that follows MVVM patterns and avoids the "dated" look of legacy GUI frameworks.
license: MIT / Production-Grade Standard
---

This skill guides the creation of distinctive, production-grade Python desktop interfaces that avoid generic "AI slop" or legacy aesthetics. It ensures code is architecturally sound, thread-safe, and ready for distribution.

## Framework Decision Matrix

Before coding, AI must select the framework based on these criteria:

| Framework | Best For | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **CustomTkinter** | Lightweight tools | Modern look, zero complex dependencies | Limited widget variety for large apps |
| **PySide6 (Qt)** | Commercial/Complex | Industry standard, QSS styling, huge widget set | Larger bundle size, complex licensing |
| **Flet (Flutter)** | High-end UI/UX | Pixel-perfect, native animations, Web-ready | Heavy abstraction from system low-level |

## Engineering & Design Thinking

1. **Architecture**: Default to **MVVM (Model-View-ViewModel)**. Keep UI logic separate from business logic.
2. **The 60FPS Rule**: Never block the main UI thread. All I/O, API, or heavy compute MUST use `QThread`, `threading.Thread`, or `asyncio`.
3. **Asset Integrity**: Use a robust path manager to handle `_MEIPASS` (for PyInstaller) and local dev paths.
4. **Platform Tone**: Decide if the app follows **Native OS** (Fluent/Material) or a **Custom Shell** (Brutalist, Minimalist, or Cyberpunk).

## Project Scaffolding

AI should implement the following structure:

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

## Technical Guidelines

### 1. Robust Path Management

Never use hardcoded paths. Always use a resource wrapper:

```python
def get_resource(relative_path):
    import sys, os
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

```

### 2. Modern Aesthetics (UI/UX)

* **Typography**: Explicitly set font rendering. Use modern stacks like `Inter`, `Geist`, or `Segoe UI Variable`.
* **High-DPI**: Must include DPI awareness code (e.g., `ctk.set_appearance_mode` or `Qt.HighDpiScaleFactorRoundingPolicy`).
* **Visual Depth**: Use 8px/16px grids, rounded corners (8-12px), and subtle border glows or layered transparencies.

### 3. Concurrency Template

When performing long-running tasks:

* **PySide6**: Use `QThread` and `Signal` for safe UI updates.
* **Tkinter**: Use `threading` and `root.after()` or `queue.Queue`.
* **Flet**: Use `asyncio` natively.

## Distribution & Packaging

AI must provide a build script or template for:

* **Nuitka (Recommended)**: `--standalone --windows-disable-console --enable-plugin=pyside6`
* **PyInstaller**: Provide a `.spec` file that correctly bundles the `assets/` directory.

## Anti-Patterns (NEVER DO)

* **No Absolute Positioning**: Never use `.place(x, y)`. Use `grid` or `pack` for responsiveness.
* **No Main-Thread Blocking**: Never run `time.sleep()` or synchronous `requests` in the UI loop.
* **No Hardcoded Assets**: Never assume `icons/logo.png` exists relative to the current working directory.
* **No Silent Crashes**: Always implement a global `sys.excepthook` to catch and display errors in a GUI dialog.

```

---

### **Next Step for you:**
Would you like me to demonstrate how to use this **Skill** by generating a **PySide6** or **CustomTkinter** starter project that follows these exact rules?

```