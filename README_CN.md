# Python GUI 工程化技能

<p align="center">
  <strong>生产级 Python 桌面应用开发规范</strong>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">中文</a>
</p>

---

## 概述

此技能指导 AI 助手创建高质量、可发布的 Python 桌面应用程序，确保：

- ✅ 现代化 UI/UX 美学（告别"复古"风格）
- ✅ 线程安全、非阻塞架构
- ✅ 跨平台兼容性
- ✅ 开箱即用的打包方案

## 支持的框架

| 框架 | 适用场景 | 核心优势 |
|------|----------|----------|
| **PySide6** | 商业应用 | 行业标准，组件丰富 |
| **CustomTkinter** | 轻量工具 | 简单易用，现代外观 |
| **Flet** | 高端界面 | 像素级精度，支持 Web |

## 快速开始

### 1. 复制到 AI 技能目录

```bash
# 常见位置：
# Cursor:    ~/.cursor/skills/
# Windsurf:  ~/.windsurf/skills/
# 自定义:    你配置的技能路径
```

### 2. 在提示词中使用

直接让 AI 构建 GUI 应用 - 相关功能会自动激活：

```
用 PySide6 构建一个文件管理器
使用 CustomTkinter 创建系统监控仪表盘
```

## 构建脚本

本技能包含自动化打包脚本：

```bash
# Windows
scripts\build.bat                    # Nuitka（默认）
scripts\build.bat pyinstaller        # PyInstaller
scripts\build.bat --onefile --clean  # 单文件可执行

# Linux/macOS
./scripts/build.sh
./scripts/build.sh pyinstaller --onefile
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--main FILE` | 入口文件（默认: main.py） |
| `--name NAME` | 应用名称 |
| `--icon FILE` | 图标文件（.ico/.icns） |
| `--onefile` | 生成单文件可执行程序 |
| `--clean` | 构建前清理 |

## 项目结构

生成的项目遵循以下结构：

```
project/
├── assets/          # 图标、字体、主题
├── src/
│   ├── ui/          # 视图和组件
│   ├── core/        # 业务逻辑
│   └── utils/       # 工具函数
├── scripts/         # 构建脚本
├── main.py          # 入口文件
└── requirements.txt
```

## 核心原则

1. **MVVM 架构** - UI 与业务逻辑分离
2. **60 FPS 法则** - 永不阻塞主线程
3. **资源管理** - 健壮的路径处理，兼容打包
4. **现代美学** - 高 DPI、暗色模式、流畅动画

## 许可证

MIT License - 可自由用于任何项目。
