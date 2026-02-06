@echo off
REM ============================================================
REM  Python GUI Build Script (Windows)
REM  Usage: build.bat [nuitka|pyinstaller] [options]
REM ============================================================

setlocal enabledelayedexpansion

REM Default values
set BUILDER=nuitka
set MAIN_FILE=main.py
set APP_NAME=
set ICON=
set ONEFILE=
set CLEAN=

REM Parse arguments
:parse_args
if "%~1"=="" goto :run_build
if /i "%~1"=="nuitka" (
    set BUILDER=nuitka
    shift
    goto :parse_args
)
if /i "%~1"=="pyinstaller" (
    set BUILDER=pyinstaller
    shift
    goto :parse_args
)
if /i "%~1"=="--main" (
    set MAIN_FILE=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--name" (
    set APP_NAME=--name %~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--icon" (
    set ICON=--icon %~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--onefile" (
    set ONEFILE=--onefile
    shift
    goto :parse_args
)
if /i "%~1"=="--clean" (
    set CLEAN=--clean
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:run_build
echo.
echo ========================================
echo   Python GUI Builder
echo   Builder: %BUILDER%
echo ========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0

if /i "%BUILDER%"=="nuitka" (
    echo Running Nuitka build...
    python "%SCRIPT_DIR%build_nuitka.py" --main %MAIN_FILE% %APP_NAME% %ICON% %ONEFILE% %CLEAN%
) else (
    echo Running PyInstaller build...
    python "%SCRIPT_DIR%build_pyinstaller.py" --main %MAIN_FILE% %APP_NAME% %ICON% %ONEFILE% %CLEAN%
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Build completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Build failed!
    echo ========================================
)

goto :eof

:show_help
echo.
echo Usage: build.bat [nuitka^|pyinstaller] [options]
echo.
echo Builders:
echo   nuitka        Use Nuitka compiler (default, recommended)
echo   pyinstaller   Use PyInstaller
echo.
echo Options:
echo   --main FILE   Entry point file (default: main.py)
echo   --name NAME   Application name
echo   --icon FILE   Icon file (.ico)
echo   --onefile     Create single executable
echo   --clean       Clean before building
echo   --help        Show this help
echo.
echo Examples:
echo   build.bat                          # Build with Nuitka defaults
echo   build.bat pyinstaller --onefile    # Build single exe with PyInstaller
echo   build.bat nuitka --clean --name MyApp
echo.
goto :eof
