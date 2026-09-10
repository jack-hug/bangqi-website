# 邦琪药业官网 (bangqi-website)

> 广西邦琪药业集团有限公司企业官网 · Flask + Bootstrap 5.3

## 功能模块

- **首页**：Banner 轮播、公司简介、八大剂型卡片、新闻中心、企业相关
- **产品中心**：剂型/商标/功能/生产企业多维筛选，Excel+ZIP 批量上传
- **新闻资讯**：分类列表 + 详情页 + 上一篇/下一篇
- **公司介绍 / 研发生产 / 联系我们**：可编辑栏目页
- **后台管理** (`/admin`)：所有内容增删改查 + 仪表盘（UV/PV/趋势图/异常登录预警/SSL 证书监控）

## 技术栈

- 后端：Flask 3.1 + Flask-SQLAlchemy 3.1 + SQLite
- 前端：Bootstrap 5.3 + 原生 JS（无打包步骤）
- 生产部署：gunicorn + Nginx（推荐）

## 本地开发

```bash
# 1. 克隆
git clone https://github.com/<your-username>/bangqi-website.git
cd bangqi-website

# 2. 准备环境
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 准备环境变量
cp .env.example .env                 # 然后编辑 .env，至少设置 SECRET_KEY

# 4. 启动开发服务器
python app.py                        # http://localhost:5000
```

## 生产部署

```bash
# 1. 上传代码到服务器（不含 venv / .db / uploads）
scp -r . user@server:/srv/bangqi/

# 2. 在服务器上：
cd /srv/bangqi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env                            # 填入真实 SECRET_KEY / ADMIN_PASSWORD

# 3. 用 gunicorn 启动（不要使用 app.py 的 dev server）
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# 4. 用 systemd 管理（示例 /etc/systemd/system/bangqi.service）
# 5. Nginx 反向代理：listen 443 ssl + proxy_pass http://127.0.0.1:5000
```

## 安全

- `SECRET_KEY` / `ADMIN_PASSWORD` 必须通过环境变量注入，仓库内**绝不**硬编码。
- Session Cookie 默认 `HttpOnly` + `SameSite=Lax`；`COOKIE_SECURE=1` 或 `FLASK_ENV=production` 时启用 `Secure`。
- 后台登录端点自带 IP 维度的速率限制（5 分钟内连续 10 次失败 → 429 临时封禁）。
- 后台响应头默认带 `X-Content-Type-Options / X-Frame-Options / Referrer-Policy / Permissions-Policy`。
- 首次登录后请立即在后台「管理员」中修改默认密码。

## 目录结构

```
bangqi-website/
├── app.py                # Flask app 工厂
├── wsgi.py               # 生产入口（gunicorn）
├── config.py             # 配置（敏感值从环境变量读取）
├── extensions.py         # db / client_ip 等共享实例
├── models.py             # SQLAlchemy 模型
├── seed.py               # 初始种子数据
├── placeholder.py        # 占位图生成
├── routes/
│   ├── main.py           # 公共路由（页面 + 公开 API）
│   ├── api.py            # 后台 CRUD API（需登录）
│   ├── batch.py          # 产品批量上传
│   └── stats.py          # 仪表盘 / UV / PV / 告警
├── templates/            # Jinja2 模板
├── static/               # CSS / JS / uploads（uploads 不入库）
├── requirements.txt
├── .env.example
└── .gitignore
```

## License

© 2026 邦琪药业集团有限公司. All rights reserved.
