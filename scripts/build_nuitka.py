#!/usr/bin/env python3
"""
Nuitka Build Script for Python GUI Applications
Cross-platform build automation with intelligent defaults.

Usage:
    python build_nuitka.py [options]

Options:
    --name NAME         Application name (default: from main.py or directory)
    --main MAIN         Entry point file (default: main.py)
    --icon ICON         Icon file path (.ico for Windows, .icns for macOS)
    --console           Enable console window (disabled by default for GUI)
    --onefile           Create single executable (slower startup)
    --clean             Clean build artifacts before building
    --framework QT|CTK  Specify framework for plugin selection
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path


class NuitkaBuildConfig:
    """Configuration manager for Nuitka builds."""
    
    FRAMEWORK_PLUGINS = {
        'pyside6': ['pyside6'],
        'pyqt6': ['pyqt6'],
        'pyqt5': ['pyqt5'],
        'qt': ['pyside6'],  # Default Qt to PySide6
        'ctk': ['tk-inter'],
        'tkinter': ['tk-inter'],
        'flet': [],  # Flet has no specific plugin
    }
    
    def __init__(self, args):
        self.main_file = Path(args.main)
        self.app_name = args.name or self._detect_app_name()
        self.icon = args.icon
        self.console = args.console
        self.onefile = args.onefile
        self.clean = args.clean
        self.framework = args.framework.lower() if args.framework else self._detect_framework()
        self.output_dir = Path('dist')
        self.build_dir = Path('build')
    
    def _detect_app_name(self) -> str:
        """Detect application name from main file or directory."""
        if self.main_file.stem != 'main':
            return self.main_file.stem
        return Path.cwd().name
    
    def _detect_framework(self) -> str:
        """Auto-detect GUI framework from imports."""
        try:
            content = self.main_file.read_text(encoding='utf-8')
            if 'PySide6' in content or 'pyside6' in content:
                return 'pyside6'
            elif 'PyQt6' in content:
                return 'pyqt6'
            elif 'PyQt5' in content:
                return 'pyqt5'
            elif 'customtkinter' in content or 'ctk' in content:
                return 'ctk'
            elif 'flet' in content:
                return 'flet'
            elif 'tkinter' in content:
                return 'tkinter'
        except Exception:
            pass
        return 'pyside6'  # Default
    
    def get_plugins(self) -> list:
        """Get Nuitka plugins for the framework."""
        return self.FRAMEWORK_PLUGINS.get(self.framework, [])
    
    def get_data_dirs(self) -> list:
        """Find data directories to include."""
        common_dirs = ['assets', 'resources', 'static', 'images', 'icons', 'fonts', 'themes']
        found = []
        for d in common_dirs:
            if Path(d).is_dir():
                found.append(d)
        return found


def run_build(config: NuitkaBuildConfig):
    """Execute Nuitka build with configuration."""
    
    # Validate main file exists
    if not config.main_file.exists():
        print(f"❌ Error: Main file '{config.main_file}' not found!")
        sys.exit(1)
    
    # Clean previous builds if requested
    if config.clean:
        print("🧹 Cleaning previous build artifacts...")
        for d in [config.output_dir, config.build_dir]:
            if d.exists():
                shutil.rmtree(d)
    
    # Build command
    cmd = [
        sys.executable, '-m', 'nuitka',
        '--standalone',
        f'--output-dir={config.output_dir}',
    ]
    
    # Mode: onefile or standalone
    if config.onefile:
        cmd.append('--onefile')
    
    # Console
    if sys.platform == 'win32' and not config.console:
        cmd.append('--windows-disable-console')
    elif sys.platform == 'darwin' and not config.console:
        cmd.append('--macos-disable-console')
    
    # Framework plugins
    for plugin in config.get_plugins():
        cmd.append(f'--enable-plugin={plugin}')
    
    # Data directories
    for data_dir in config.get_data_dirs():
        cmd.append(f'--include-data-dir={data_dir}={data_dir}')
    
    # Icon
    if config.icon:
        if sys.platform == 'win32':
            cmd.append(f'--windows-icon-from-ico={config.icon}')
        elif sys.platform == 'darwin':
            cmd.append(f'--macos-app-icon={config.icon}')
    
    # Product info (Windows)
    if sys.platform == 'win32':
        cmd.extend([
            f'--product-name={config.app_name}',
            f'--file-description={config.app_name}',
            '--file-version=1.0.0.0',
            '--product-version=1.0.0.0',
        ])
    
    # macOS bundle
    if sys.platform == 'darwin':
        cmd.extend([
            '--macos-create-app-bundle',
            f'--macos-app-name={config.app_name}',
        ])
    
    # Additional optimizations
    cmd.extend([
        '--assume-yes-for-downloads',
        '--remove-output',
    ])
    
    # Main file
    cmd.append(str(config.main_file))
    
    # Print command
    print(f"🚀 Building '{config.app_name}' with Nuitka...")
    print(f"📦 Framework: {config.framework}")
    print(f"📁 Output: {config.output_dir}")
    print(f"\n💻 Command:\n{' '.join(cmd)}\n")
    
    # Execute
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Build successful! Output in '{config.output_dir}'")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("\n❌ Nuitka not found! Install with: pip install nuitka")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Build Python GUI application with Nuitka',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--name', help='Application name')
    parser.add_argument('--main', default='main.py', help='Entry point file')
    parser.add_argument('--icon', help='Icon file path')
    parser.add_argument('--console', action='store_true', help='Enable console window')
    parser.add_argument('--onefile', action='store_true', help='Create single executable')
    parser.add_argument('--clean', action='store_true', help='Clean before building')
    parser.add_argument('--framework', choices=['pyside6', 'pyqt6', 'pyqt5', 'qt', 'ctk', 'tkinter', 'flet'],
                        help='GUI framework (auto-detected if not specified)')
    
    args = parser.parse_args()
    config = NuitkaBuildConfig(args)
    run_build(config)


if __name__ == '__main__':
    main()
