#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -gt 0 ]]; then
  export STEAM_API_KEY="${1}"
fi

cd "${PROJECT_ROOT}/backend"
echo "启动 Django 后端 (http://127.0.0.1:8000) ..."
"${PROJECT_ROOT}/venv/bin/python" manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

trap "kill ${BACKEND_PID} 2>/dev/null" EXIT

cd "${PROJECT_ROOT}/frontend"
echo "启动 Vue 前端开发服务器 (http://127.0.0.1:5173) ..."
npm run dev

