# -*- coding: utf-8 -*-
"""配置文件 - 敏感值一律从环境变量读取，启动前必须注入"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # SECRET_KEY：用于 Flask session 签名。
    # 生产环境必须通过环境变量 SECRET_KEY 注入一个 ≥ 32 字节的随机串；
    # 未注入时本类直接抛错，避免开发者无意中把弱密钥部署到线上。
    _secret_key = os.environ.get("SECRET_KEY")
    if not _secret_key:
        if os.environ.get("FLASK_ENV") == "production":
            raise RuntimeError(
                "[config] SECRET_KEY 未设置。在生产环境必须通过环境变量注入强随机密钥。"
                "可执行 `python -c \"import secrets; print(secrets.token_hex(32))\"` 生成。")
        # 仅开发模式允许回退到占位串，并在控制台显式提醒
        import secrets as _secrets
        _secret_key = "dev-" + _secrets.token_hex(16)
        print("[config] 警告：SECRET_KEY 未设置，已生成一次性开发占位串，"
              "重启服务或换机器即失效。生产部署前必须显式设置。")
    SECRET_KEY = _secret_key

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'bangqi.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    # 批量上传时 ZIP + Excel 可能很大，放宽到 200MB；单张图片上传仍受 api.py 内的 8MB 限制
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024

    # 管理员初始口令：仅在初始化空库时使用一次，之后由数据库 AdminUser 表保管哈希。
    # 生产环境必须通过环境变量 ADMIN_USERNAME / ADMIN_PASSWORD 注入；
    # 未注入时使用占位（开发期可在后台修改），不会硬编码到 git。
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    _admin_pwd = os.environ.get("ADMIN_PASSWORD")
    if not _admin_pwd:
        if os.environ.get("FLASK_ENV") == "production":
            raise RuntimeError(
                "[config] ADMIN_PASSWORD 未设置。生产环境必须通过环境变量注入管理员口令，"
                "或在初始化后立即通过数据库或后台修改默认密码。")
        import secrets as _secrets
        _admin_pwd = "dev-" + _secrets.token_hex(8) + "-change-me"
        print("[config] 警告：ADMIN_PASSWORD 未设置，已生成一次性开发口令：", _admin_pwd)
    ADMIN_PASSWORD = _admin_pwd

    # SSL 证书监控域名（后台仪表盘可随时修改，修改后存库优先）
    SSL_CHECK_HOST = os.environ.get("SSL_CHECK_HOST", "")
    # 资讯详情页尾文案默认值（后台「公司信息」可修改）
    NEWS_FOOTER_DEFAULT = ("邦琪药业将持续关注行业动态，不断提升产品质量与服务水平，"
                           "以专业与匠心回馈广大消费者的信赖。更多资讯，欢迎关注公司官方渠道。")

