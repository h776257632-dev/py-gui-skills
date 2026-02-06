#!/bin/bash
# ============================================================
#  Python GUI Build Script (Linux/macOS)
#  Usage: ./build.sh [nuitka|pyinstaller] [options]
# ============================================================

set -e

# Default values
BUILDER="nuitka"
MAIN_FILE="main.py"
APP_NAME=""
ICON=""
ONEFILE=""
CLEAN=""

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        nuitka)
            BUILDER="nuitka"
            shift
            ;;
        pyinstaller)
            BUILDER="pyinstaller"
            shift
            ;;
        --main)
            MAIN_FILE="$2"
            shift 2
            ;;
        --name)
            APP_NAME="--name $2"
            shift 2
            ;;
        --icon)
            ICON="--icon $2"
            shift 2
            ;;
        --onefile)
            ONEFILE="--onefile"
            shift
            ;;
        --clean)
            CLEAN="--clean"
            shift
            ;;
        --help)
            echo ""
            echo "Usage: ./build.sh [nuitka|pyinstaller] [options]"
            echo ""
            echo "Builders:"
            echo "  nuitka        Use Nuitka compiler (default, recommended)"
            echo "  pyinstaller   Use PyInstaller"
            echo ""
            echo "Options:"
            echo "  --main FILE   Entry point file (default: main.py)"
            echo "  --name NAME   Application name"
            echo "  --icon FILE   Icon file (.icns for macOS)"
            echo "  --onefile     Create single executable"
            echo "  --clean       Clean before building"
            echo "  --help        Show this help"
            echo ""
            echo "Examples:"
            echo "  ./build.sh                          # Build with Nuitka defaults"
            echo "  ./build.sh pyinstaller --onefile    # Build single exe with PyInstaller"
            echo "  ./build.sh nuitka --clean --name MyApp"
            echo ""
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

echo ""
echo "========================================"
echo "  Python GUI Builder"
echo "  Builder: $BUILDER"
echo "========================================"
echo ""

if [ "$BUILDER" = "nuitka" ]; then
    echo "Running Nuitka build..."
    python3 "$SCRIPT_DIR/build_nuitka.py" --main "$MAIN_FILE" $APP_NAME $ICON $ONEFILE $CLEAN
else
    echo "Running PyInstaller build..."
    python3 "$SCRIPT_DIR/build_pyinstaller.py" --main "$MAIN_FILE" $APP_NAME $ICON $ONEFILE $CLEAN
fi

echo ""
echo "========================================"
echo "  Build completed!"
echo "========================================"
