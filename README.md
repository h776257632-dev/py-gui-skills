# Python GUI Engineering Skill

<p align="center">
  <strong>Production-grade Python desktop interface development guidelines</strong>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">中文</a>
</p>

---

## Overview

This skill guides AI assistants to create high-quality, production-ready Python desktop applications. It ensures:

- ✅ Modern UI/UX aesthetics (no "dated" look)
- ✅ Thread-safe, non-blocking architecture
- ✅ Cross-platform compatibility
- ✅ Ready-to-distribute packaging

## Supported Frameworks

| Framework | Best For | Key Advantage |
|-----------|----------|---------------|
| **PySide6** | Commercial apps | Industry standard, rich widgets |
| **CustomTkinter** | Lightweight tools | Simple, modern look |
| **Flet** | High-end UI | Pixel-perfect, web-ready |

## Quick Start

### 1. Copy to AI Skills Directory

```bash
# Example locations:
# Cursor:    ~/.cursor/skills/
# Windsurf:  ~/.windsurf/skills/
# Custom:    Your configured skills path
```

### 2. Reference in Prompts

Simply ask the AI to build a GUI application - the skill activates automatically when relevant.

```
Build a file manager application with PySide6
Create a system monitor dashboard using CustomTkinter
```

## Build Scripts

This skill includes automated build scripts for packaging:

```bash
# Windows
scripts\build.bat                    # Nuitka (default)
scripts\build.bat pyinstaller        # PyInstaller
scripts\build.bat --onefile --clean  # Single executable

# Linux/macOS
./scripts/build.sh
./scripts/build.sh pyinstaller --onefile
```

### Options

| Option | Description |
|--------|-------------|
| `--main FILE` | Entry point (default: main.py) |
| `--name NAME` | Application name |
| `--icon FILE` | Icon file (.ico/.icns) |
| `--onefile` | Single executable |
| `--clean` | Clean before build |

## Project Structure

Generated projects follow this structure:

```
project/
├── assets/          # Icons, fonts, themes
├── src/
│   ├── ui/          # Views and widgets
│   ├── core/        # Business logic
│   └── utils/       # Helpers
├── scripts/         # Build scripts
├── main.py          # Entry point
└── requirements.txt
```

## Key Principles

1. **MVVM Architecture** - Separation of UI and business logic
2. **60 FPS Rule** - Never block the main thread
3. **Resource Management** - Robust path handling for packaging
4. **Modern Aesthetics** - HiDPI, dark mode, smooth animations

## License

MIT License - Use freely in any project.
