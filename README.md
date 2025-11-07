# Steam 游戏社区项目文档

## 1. 项目简介
Steam 游戏社区是一个面向玩家的论坛与数据聚合网站，前端使用 Vue 构建互动界面，后端采用 Django + Django REST Framework 提供 API 服务，并可绑定 Steam 账号同步游戏库与游玩时长。系统目标：
- 让玩家展示 Steam 游戏数据、查看他人数据。
- 提供发帖、评论等社区互动功能。
- 规划扩展更多游戏相关内容（榜单、成就分享等）。

## 2. 系统架构
- **前端**：Vue 3 + Vite，Pinia 负责状态管理，Vue Router 控制路由，Axios 封装后端请求。
- **后端**：Django 4 + Django REST Framework，Token 认证，SQLite（默认）或 PostgreSQL。
- **第三方服务**：Steam Web API（通过自封装 `SteamApi` 类访问）。
- **部署建议**：Nginx 反向代理，Gunicorn/Uvicorn 托管 Django，前端静态资源经 CI/CD 构建后部署至 CDN 或 Nginx。

示意流程：
```
Vue 前端 → REST API → Django 服务 → SQLite/PostgreSQL
                  ↘ Steam Web API
```

## 3. 功能清单
- 前端界面：登录/注册、帖子列表与详情、评论区、个人中心（含 Steam 绑定与游玩时长展示）。
- Steam 促销页面：展示实时折扣、搜索/过滤与多视图切换。
- 后端 API：用户、帖子、评论、Steam 数据同步。

### 规划增强
- 支持帖子编辑、点赞/收藏、评论回复。
- 接入 WebSocket 实现实时通知。
- 定时任务刷新 Steam 数据缓存。
- 角色权限（管理员、版主）。

## 4. API 概览
| 功能 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| 健康检查 | GET | `/api/test/` | 返回服务状态 |
| 注册 | POST | `/api/register/` | 创建用户（用户名+密码） |
| 登录 | POST | `/api/login/` | 返回 Token |
| 获取个人信息 | GET | `/api/userinfo/` | 需 Token |
| 绑定 Steam | POST | `/api/bindsteam/` | 需 Token，提交 `steamUserName` |
| 获取 Steam 数据 | GET | `/api/steamgameinfo/` | 需 Token（需先绑定） |
| 解绑 Steam | GET | `/api/unbindsteam/` | 需 Token |
| 获取 Steam 促销 | GET | `/api/steamdiscounts/` | 公共 |
| 创建帖子 | POST | `/api/newpost/` | 需 Token |
| 全部帖子 | GET | `/api/allposts/` | 公共 |
| 我的帖子 | GET | `/api/myposts/` | 需 Token |
| 帖子详情/删除 | GET/DELETE | `/api/posts/{id}/` | 需 Token，作者或管理员可删 |
| 帖子评论 | GET/POST | `/api/posts/{id}/comments/` | 需 Token |
| 删除评论 | DELETE | `/api/comments/{id}/` | 需 Token，作者或管理员 |

> 实际 URL 以前端路由和 `api/urls.py` 为准，后端可根据需要调整命名。

## 5. 数据模型
### User (`api.models.User`)
- 继承 Django `AbstractUser`
- 扩展字段：`steamUserName`

### Post
- `title`：帖子标题
- `content`：正文
- `author`：外键关联 `User`
- `create_time`：自动创建时间

### Comment
- `post`：外键关联 `Post`
- `author`：外键关联 `User`
- `content`：评论内容
- `create_time`：自动创建时间

后续可新增模型：点赞、附件、标签、通知等。

## 6. 本地开发指南
### 6.1 项目结构
```
gameweb/
├─ backend/            # Django 后端
│  ├─ api/             # 业务应用
│  ├─ gameweb/         # 项目配置
│  ├─ manage.py
│  ├─ requirements.txt
│  └─ db.sqlite3
└─ frontend/           # Vue 前端
   ├─ src/
   │  ├─ api/          # Axios 封装
   │  ├─ components/
   │  ├─ router/
   │  ├─ stores/
   │  ├─ views/
   │  └─ style.css
   ├─ package.json
   └─ vite.config.js
```

### 6.2 后端开发环境
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

调试说明：
- 管理后台：`python manage.py createsuperuser`
- REST API：使用 Postman/Insomnia 或 `curl` 搭配 Token。
- 更换数据库：编辑 `gameweb/settings.py` 的 `DATABASES` 配置。

### 6.3 前端开发环境
```powershell
cd frontend
npm install
npm run dev
```

如需修改后端地址，在 `frontend/.env.development` 写入：
```
VITE_API_BASE_URL=http://localhost:8000/api/
```

### 6.4 快速启动脚本（Windows）
- 后端：双击或在命令行执行 `start_backend.bat`，如需临时指定 Steam Key 可附加参数：`start_backend.bat 你的SteamKey`
- 前端：双击或在命令行执行 `start_frontend.bat`

### 6.5 环境变量
- 后端读取系统环境变量：`DJANGO_SECRET_KEY`、`DJANGO_DEBUG`、`DJANGO_ALLOWED_HOSTS`、`DJANGO_CORS_ALLOWED_ORIGINS`、`STEAM_API_KEY`、`DJANGO_STATIC_ROOT`。
- 前端：`VITE_API_BASE_URL`（默认 `http://localhost:8000/api/`）。

## 7. 部署建议
### 7.1 Windows 无 Docker 部署流程
1. **准备环境**：安装 Python 3.11+、Node.js 18+，并确保已安装 Git；在 PowerShell 中执行 `python -m venv venv`、`venv\Scripts\activate`、`pip install -r requirements.txt`。
2. **配置环境变量**：通过 PowerShell 或“系统环境变量”面板设置 `DJANGO_SECRET_KEY`、`DJANGO_DEBUG=0`、`DJANGO_ALLOWED_HOSTS=your.domain,localhost`、`STEAM_API_KEY` 等变量（示例：`setx DJANGO_SECRET_KEY your_secret`）。
3. **同步数据库与静态资源**：执行 `python manage.py migrate`、`python manage.py collectstatic --noinput`，并按需创建超级用户。
4. **生产服务**：使用 Waitress 启动 `waitress-serve --listen=0.0.0.0:8000 gameweb.wsgi:application`，可通过 NSSM/Windows 服务管理器将命令注册为后台服务。
5. **前端构建**（待开发）：在 `frontend` 目录执行 `npm install`、`npm run build`，将 `dist` 目录发布至 IIS 或 Nginx；若暂未开发前端，可跳过。
6. **反向代理与 HTTPS**：推荐使用 IIS URL Rewrite 或 Nginx for Windows，将外部流量转发至 Waitress，配置证书（Let’s Encrypt/企业 CA），并设置静态文件缓存。
7. **日志与监控**：启用 Django 日志输出到文件，借助 Windows 事件查看器或 Sentry 采集异常；可结合 Prometheus Windows exporter 监控资源。

### 7.2 其他建议
- 使用 Docker Compose：一个服务运行 Django + Gunicorn，另一个服务运行 PostgreSQL；Nginx 作为反向代理与静态资源服务器。
- 配置定时任务 `cron`/`Celery Beat` 同步 Steam 数据。
- 启用 HTTPS，前端静态资源通过 CI/CD 自动构建并发布。
- 监控：接入 Sentry（前后端）、Prometheus + Grafana 监控性能。

## 8. 测试与质量保障
- 后端：使用 `pytest` 或 Django TestCase（`api/tests.py`），覆盖注册登录、Steam API Mock、帖子评论操作。
- 前端：使用 `Vitest` + `Testing Library` 进行组件与路由测试。
- 集成：编写端到端测试（Playwright/Cypress）。

## 9. 更新日志
- 2024-xx-xx：完成 Django 后端基础功能（用户、帖子、评论、Steam 同步）。
- 2025-xx-xx：规划前端与部署方案（当前文档）。

## 10. 未来规划
- 完善权限体系与操作审计。
- 提供多语言支持（中/英）。
- 引入推荐算法，依据游玩时间推荐帖子或游戏。
- 允许用户上传截图、视频等多媒体内容。
