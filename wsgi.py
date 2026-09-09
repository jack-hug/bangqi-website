# -*- coding: utf-8 -*-
"""生产环境 WSGI 入口
- 启动方式: `gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app`
- 配合反向代理（Nginx）时,建议关闭 `proxy_headers` 信任以外的 `X-Forwarded-*`。
- 启动前必须设置环境变量: SECRET_KEY / ADMIN_PASSWORD / FLASK_ENV=production
"""
import os

# 强制声明生产模式，便于 config.py 校验关键环境变量
os.environ.setdefault("FLASK_ENV", "production")

from app import create_app  # noqa: E402

app = create_app()
