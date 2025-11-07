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
- Steam 时长缓存：后端写入数据库，前端配合 `localStorage`。

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
| 获取 Steam 时长 | GET | `/api/steamgameinfo/` | 需 Token，支持 `force=true` 刷新 |
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

### SteamOwnedGame
- `user`：一对一关联 `User`
- `data`：缓存 Steam 拥有游戏列表（JSON）
- `fetched_at`：最后刷新时间

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

---

# Django + Vue 学习指南（基于本项目）

## A. 工程总揽

- **定位**：Steam 游戏社区，全栈使用 Django + DRF（后端）与 Vue3 + Vite（前端）。
- **功能概览**：账号注册与 Token 登录、Steam 账号绑定与时长统计、帖子评论、Steam 折扣展示。
- **目录结构**：
  ```
  gameweb/
  ├─ backend/                # Django 后端
  │  ├─ api/                 # 应用（模型/视图/序列化器/Steam 接口）
  │  ├─ gameweb/             # 项目配置
  │  ├─ manage.py
  │  ├─ db.sqlite3
  │  └─ requirements.txt
  └─ frontend/               # Vue 前端
     ├─ src/
     │  ├─ api/              # Axios 封装层
     │  ├─ components/       # UI 组件
     │  ├─ router/           # Vue Router
     │  ├─ stores/           # Pinia Store
     │  ├─ views/            # 页面
     │  └─ style.css
     ├─ package.json
     └─ vite.config.js
  ```

### 请求流转

1. 用户访问 `frontend` 构建的 SPA → Vue Router 渲染页面。
2. 前端通过 `src/api/http.js` 统一发送 Axios 请求，自动附加 Token。
3. Django/DRF 在 `backend/api/views.py` 中处理请求，使用模型/序列化器。
4. 若需 Steam 数据，则在 `api/SteamGame.py` 调用 Steam Web API。
5. Django ORM 与 SQLite 交互 → 返回 JSON 给前端。

## B. Django 学习要点（结合代码）

### 1. 自定义用户与模型关系

- `api/models.py` 定义：
  - `User(AbstractUser)`：增加 `steamUserName`。
  - `Post`、`Comment`：关联 `User`，使用 `ForeignKey`。
- `settings.py` 中 `AUTH_USER_MODEL = "api.User"`，告知 Django 使用自定义模型。

### 2. 序列化器与数据校验

- `api/serializers.py`：
  - `UserSerializer` 写入时处理密码、Steam 名。
  - `PostSerializer`/`CommentSerializer` 暴露作者名称、创建时间。
- 序列化器保证输入合法且输出结构统一。

### 3. API 视图与权限

- `api/views.py`：
  - `register/login` 完成注册/登录与 Token 下发。
  - `getSteamGameInfo` 支持缓存：优先读 `SteamOwnedGame` 表，`force=true` 时刷新并写回。
  - `getSteamDiscounts` 从 Steam Specials 获取折扣列表。
  - 帖子/评论 API 使用 `TokenAuthentication + IsAuthenticated`，实现 CRUD。
- 前端携带 Token 后，Django 在 `request.user` 中识别用户。

### 4. Steam API 封装

- 位置：`api/SteamGame.py`
  - 写死 `STEAM_API_KEY`、地区/语言、代理、超时时间。
  - `_get()` 统一处理 `requests.get` 与异常。
  - `getOwnedGames(username)`：先解析 vanity URL → SteamID → 获取拥有游戏（含时长）。
  - `getDiscountedGames()`：请求 `featuredcategories`，兼容多种返回结构后格式化数据。

## C. Vue 学习要点（结合代码）

### 1. 项目结构与入口

- `main.js`：创建 app、注册 Pinia/Router、处理路由守卫（需登录的路由跳转 login）。
- `router/index.js`：定义 `/posts`、`/dashboard`、`/deals` 等页面；`meta.requiresAuth` 控制登录访问。

### 2. 状态管理 Pinia

- `stores/auth.js`：
  - `token`、`user`、`loading`、`error`。
  - `login/ register/ refreshProfile/ logout`。
  - `initFromStorage()`：App 启动时从 `localStorage` 恢复 Token。

### 3. Axios 封装

- `api/http.js`：
  - `baseURL` 默认 `http://localhost:8000/api/`。
  - 请求拦截器为所有请求加 `Authorization: Token xxx`。
  - 响应拦截器提取错误信息，统一错误提示。

### 4. 关键页面解析

#### Dashboard（`views/DashboardView.vue`）

- 功能：显示 Steam 时长、绑定账号、统计最常游玩游戏、搜索/排序/视图切换。
- 缓存：
  - 缓存键 `steam-games-cache-{userId}`（`localStorage`）。
  - `readCache()` 判断是否过期（默认 10 分钟，可通过 `VITE_STEAM_GAME_CACHE_TTL` 配置）。
  - 绑定/解绑均调用 `clearCache()`。
- 数据处理：`mappedGames` 生成封面、类型标签、价格；`filteredGames` 根据搜索/排序返回视图数据。

#### SteamDeals（`views/SteamDealsView.vue` + `DiscountGameCard.vue`）

- 逻辑：请求 `/api/steamdiscounts/` → `heroDeals` 显示顶部精选 → `restDeals` 展示网格或列表。
- 功能：搜索、折扣排序、价格筛选、切换视图、手动刷新。
- 组件 `DiscountGameCard`：展示折扣百分比、原价/折扣价、评价摘要、商店链接。

#### 认证页（`LoginView.vue` / `RegisterView.vue`）

- 使用 `reactive` 维护表单，调用 Pinia `authStore` 的 `login`、`register`。
- 登录成功后根据 `redirect` query 跳转。

#### 帖子页

- `PostListView.vue`：通过 `fetchAllPosts`/`fetchMyPosts` 切换数据；路由 query 同步过滤状态。
- `PostDetailView.vue`：懒加载详情、显示评论、支持发布/删除评论。

## D. 前后端联调指南

1. **启动后端**：
   ```powershell
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py runserver 0.0.0.0:8000
   ```
2. **启动前端**：
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
3. **调试技巧**：
   - 使用浏览器 DevTools 查看网络请求、响应。
   - Postman/Curl 测试 API。
   - 后端在视图里打印日志；或 `python manage.py shell` 直接调用 `SteamApi`。
   - 代理问题：若 Steam API 超时，先确认本地代理 `127.0.0.1:7890` 可用。

## E. 学习路径建议

1. **Django 基础**：模型 → 迁移 → 视图 → 序列化 → 认证机制。
2. **Django REST Framework**：APIView/函数视图、权限、异常处理、测试。
3. **Vue3**：Composition API、组件通信、Router 守卫、Pinia 状态管理。
4. **Axios & 请求管理**：封装请求、错误提示、Token 刷新。
5. **Steam API 集成**：理解第三方 API 调用，处理代理、异常、不同返回结构。
6. **缓存策略**：本地缓存（localStorage）、后端缓存（可扩展 Redis）。
7. **扩展练习**：
   - 帖子编辑、点赞/收藏。
   - Steam 折扣缓存到后端或前端，以加速展示。
   - 引入图表库展示游戏时长趋势。
   - 部署：Nginx + Waitress/Uvicorn + 前端静态构建。

## F. 推荐学习资源

- Django 官方文档：https://docs.djangoproject.com
- Django REST Framework：https://www.django-rest-framework.org
- Vue 官方文档：https://cn.vuejs.org
- Pinia：https://pinia.vuejs.org
- Axios：https://axios-http.com
- Steam Web API 文档：https://partner.steamgames.com/doc/webapi

## G. 常见问题排查

- **Steam API 超时**：检查代理是否运行；可直接 `Invoke-WebRequest https://store.steampowered.com` 测试。
- **Token 失效**：前端 `localStorage` 清空后重新登录；后端确保 `TokenAuthentication` 正常。
- **CORS**：`settings.py` 中启用了 `corsheaders`，默认允许全部来源；生产环境需收紧。
- **静态资源**：`collectstatic` 收集后部署到 Nginx；前端 `npm run build` 生成 `dist`。
- **数据库迁移**：修改模型后运行 `python manage.py makemigrations && python manage.py migrate`。

---

通过逐步阅读与实践上述模块，你可以在本项目中系统掌握 Django 与 Vue 全栈开发流程：从用户认证、REST API、Steam 第三方集成到前端状态管理、路由、多页面交互与样式设计。建议按“后端 API → 前端请求 → UI 展示 → 第三方集成 → 缓存与优化”的顺序反复练习。祝你学习顺利！
