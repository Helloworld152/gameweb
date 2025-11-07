@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist "venv\Scripts\python.exe" (
  echo [ERROR] 未找到虚拟环境，请先在项目根目录执行: python -m venv venv
  exit /b 1
)

if not exist "backend\manage.py" (
  echo [ERROR] 未找到 backend\manage.py，请确认项目结构。
  exit /b 1
)

set "STEAM_KEY=%~1"
if not "%STEAM_KEY%"=="" (
  set "STEAM_API_KEY=%STEAM_KEY%"
)

echo 启动 Django 后端 (http://127.0.0.1:8000) ...
cd backend
"..\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000

endlocal

