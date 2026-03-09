@echo off
chcp 65001 >nul
title 妆策AI · 一键启动

echo.
echo ============================================
echo   妆策AI · 美妆新零售智能推荐系统
echo   MiroMakeup - Beauty AI MVP v1.0
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到 Python，请先安装 Python 3.9+
    pause & exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到 Node.js，请先安装 Node.js 18+
    pause & exit /b 1
)

echo [OK] Python / Node.js 环境就绪
echo.

:: ── 安装后端依赖（首次运行）──
set BACKEND_DIR=%~dp0backend
if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo [1/4] 创建 Python 虚拟环境...
    python -m venv "%BACKEND_DIR%\venv"
)

echo [2/4] 安装后端 Python 依赖...
call "%BACKEND_DIR%\venv\Scripts\activate.bat"
pip install -r "%BACKEND_DIR%\requirements.txt" -q --disable-pip-version-check

:: ── 安装前端依赖（首次运行）──
set FRONTEND_DIR=%~dp0frontend
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [3/4] 安装前端 Node 依赖（首次约需 1-2 分钟）...
    pushd "%FRONTEND_DIR%"
    npm install --silent
    popd
) else (
    echo [3/4] 前端依赖已存在，跳过安装
)

echo [4/4] 启动后端 Flask (端口 5000) 和前端 Vite (端口 5173)...
echo.
echo  后端地址: http://localhost:5000
echo  前端地址: http://localhost:5173
echo.
echo  关闭此窗口将同时停止所有服务
echo ============================================

:: 新窗口启动后端
start "妆策AI · 后端 Flask" cmd /k "call \"%BACKEND_DIR%\venv\Scripts\activate.bat\" && python \"%BACKEND_DIR%\app.py\""

:: 新窗口启动前端
start "妆策AI · 前端 Vite" cmd /k "cd /d \"%FRONTEND_DIR%\" && npm run dev"

echo.
echo [启动中] 请稍等 3-5 秒，然后访问 http://localhost:5173
echo.
timeout /t 5 /nobreak >nul
start http://localhost:5173

pause
