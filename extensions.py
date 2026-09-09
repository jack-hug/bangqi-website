# -*- coding: utf-8 -*-
"""Flask 扩展实例 & 通用工具"""
from flask import request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def client_ip():
    """取真实客户端 IP（兼容 Nginx / CDN 反向代理）"""
    for header in ("X-Forwarded-For", "X-Real-IP", "CF-Connecting-IP"):
        val = request.headers.get(header, "")
        if val:
            return val.split(",")[0].strip()
    return request.remote_addr or ""
