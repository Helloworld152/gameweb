@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist "frontend\package.json" (
  echo [ERROR] 未找到 frontend\package.json，请确认项目结构。
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] 未检测到 npm，请先安装 Node.js。
  exit /b 1
)

echo 启动 Vue 前端开发服务器 (http://127.0.0.1:5173) ...
cd frontend
npm run dev

endlocal

