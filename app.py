# -*- coding: utf-8 -*-
"""邦琪药业企业官网 - App 工厂"""
import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, g
from config import Config
from extensions import db, client_ip


# 访问埋点：这些前缀的请求不计入 PV/UV（静态资源、接口、后台自身）
TRACK_SKIP_PREFIX = ("/static", "/api", "/admin")


def _migrate_db():
    """为已有数据库补充新增列（SQLite: ALTER TABLE ADD COLUMN）"""
    from sqlalchemy import inspect, text
    from extensions import db as _db
    insp = inspect(_db.engine)
    new_cols = {
        "banner": ["image"],
        "company_image": ["image"],
        "enterprise_card": ["image"],
        "dosage_form": ["color", "image"],
        "product": ["image", "code", "manufacturer_id"],
        "product_image": ["image"],
        "news": ["image"],
        "page": ["color", "image"],
        "company": ["news_footer"],
    }
    changed = False
    for table, cols in new_cols.items():
        if not insp.has_table(table):
            continue
        existing = {c["name"] for c in insp.get_columns(table)}
        for col in cols:
            if col not in existing:
                # code 是产品编号，单独类型；manufacturer_id 是外键；其它都是图片/文本字段
                if col == "code":
                    col_type = "VARCHAR(50)"
                elif col.endswith("_id"):
                    col_type = "INTEGER"
                else:
                    col_type = "VARCHAR(300)"
                _db.session.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                changed = True
                print(f"[migrate] {table} + {col}")
    if changed:
        _db.session.commit()

    # 回填资讯页尾文案默认值（仅当为空时，不覆盖后台已填写的值）
    if insp.has_table("company"):
        _db.session.execute(
            text("UPDATE company SET news_footer = :v WHERE news_footer IS NULL OR news_footer = ''"),
            {"v": Config.NEWS_FOOTER_DEFAULT})
        _db.session.commit()

    # 回填现有产品的 code（按 id 升序生成 BQ-001、BQ-002 ...）
    if insp.has_table("product"):
        # 用 PRAGMA 实时判断，避免 SQLAlchemy inspector 缓存导致漏判
        code_exists = _db.session.execute(
            text("SELECT COUNT(*) FROM pragma_table_info('product') WHERE name = 'code'")).scalar()
        if code_exists:
            rows = _db.session.execute(
                text("SELECT id FROM product WHERE code IS NULL OR code = '' ORDER BY id")).fetchall()
            for idx, (pid,) in enumerate(rows, start=1):
                _db.session.execute(
                    text("UPDATE product SET code = :c WHERE id = :pid"),
                    {"c": "BQ-%03d" % idx, "pid": pid})
            if rows:
                _db.session.commit()
                print(f"[migrate] product.code 回填 {len(rows)} 条")

    # 初始化 3 个默认生产企业（仅当表为空时）
    if insp.has_table("manufacturer"):
        mfg_count = _db.session.execute(text("SELECT COUNT(*) FROM manufacturer")).scalar()
        if mfg_count == 0:
            _db.session.execute(text(
                "INSERT INTO manufacturer (name, description, sort_order) VALUES "
                "('邦琪', '广西邦琪药业集团有限公司主体生产基地', 0)"))
            _db.session.execute(text(
                "INSERT INTO manufacturer (name, description, sort_order) VALUES "
                "('百琪', '下属子公司·侧重口服液/糖浆类制剂', 1)"))
            _db.session.execute(text(
                "INSERT INTO manufacturer (name, description, sort_order) VALUES "
                "('葛洪堂', '下属子公司·侧重经典名方与传统膏方', 2)"))
            _db.session.commit()
            print("[migrate] manufacturer 种子: 邦琪 / 百琪 / 葛洪堂")

    # 回填现有产品的 manufacturer_id（默认归「邦琪」）
    if insp.has_table("product") and insp.has_table("manufacturer"):
        mf_id_exists = _db.session.execute(
            text("SELECT COUNT(*) FROM pragma_table_info('product') WHERE name = 'manufacturer_id'")).scalar()
        bq_id = _db.session.execute(
            text("SELECT id FROM manufacturer WHERE name='邦琪'")).scalar()
        if mf_id_exists and bq_id:
            updated = _db.session.execute(
                text("UPDATE product SET manufacturer_id = :mid WHERE manufacturer_id IS NULL"),
                {"mid": bq_id}).rowcount
            _db.session.commit()
            if updated:
                print(f"[migrate] product.manufacturer_id 默认邦琪：{updated} 条")

    # 补 updated_at 列（模块最后更新时间），并为历史数据回填当前时间
    _updated_tables = ["company", "banner", "home_stat", "company_image",
                       "enterprise_card", "dosage_form", "trademark",
                       "func_category", "manufacturer", "product",
                       "product_image", "news_category", "news", "page",
                       "page_section", "page_stat"]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for table in _updated_tables:
        if not insp.has_table(table):
            continue
        has_col = _db.session.execute(
            text("SELECT COUNT(*) FROM pragma_table_info('%s') WHERE name = 'updated_at'" % table)).scalar()
        if has_col:
            continue
        _db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN updated_at DATETIME"))
        _db.session.execute(
            text(f"UPDATE {table} SET updated_at = :v WHERE updated_at IS NULL"), {"v": now_str})
        _db.session.commit()
        print(f"[migrate] {table} + updated_at")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---- 会话安全：根据部署环境自动决定 Cookie 的 Secure 标志 ----
    # 反向代理常见情况下由 Nginx 终结 HTTPS，但应用本身无法直接感知。
    # 约定：环境变量 COOKIE_SECURE=1 时强制启用 Secure Cookie。
    is_prod = os.environ.get("FLASK_ENV") == "production" or os.environ.get("COOKIE_SECURE") == "1"
    # Flask 3.x 的 SessionIdent 类已经把 SAMESITE 键放在 config 里（默认 None），
    # 所以这里用「缺失或 falsy」模式赋值，避免被 setdefault 静默忽略。
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = app.config.get("SESSION_COOKIE_SAMESITE") or "Lax"
    app.config["SESSION_COOKIE_SECURE"] = is_prod
    # session 寿命保持 Flask 默认（timedelta(days=31)）。
    # 注意：如果想「关闭浏览器即退出」，那么在登录时不要调 session.permanent = True 即可。

    db.init_app(app)

    # 注册蓝图
    from routes.main import bp as main_bp
    from routes.api import bp as api_bp
    from routes.batch import bp as batch_bp
    from routes.stats import bp as stats_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(stats_bp)

    # ---- 基础安全 HTTP 响应头 ----
    @app.after_request
    def _security_headers(resp):
        # 防止浏览器嗅探 MIME，缓解类型混淆
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        # 整站禁止被嵌入到 iframe，缓解点击劫持
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        # 限制 referer 泄露
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        # 限制浏览器特性（生产环境无外部域交互，按需收紧）
        resp.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return resp

    # ---- 访问埋点：记录 PV / UV，并在响应里写入访客 cookie ----
    @app.before_request
    def _track_visit_start():
        g.visit_id = None
        g.new_vid = None
        if request.method != "GET":
            return
        path = request.path or ""
        if path == "/favicon.ico" or path.startswith(TRACK_SKIP_PREFIX):
            return
        try:
            from models import VisitLog
            vid = request.cookies.get("bq_vid")
            if not vid:
                vid = uuid.uuid4().hex[:32]
                g.new_vid = vid
            log = VisitLog(
                visitor_id=vid,
                path=path[:300],
                ip=client_ip()[:64],
                ua=(request.user_agent.string or "")[:300],
                referer=(request.referrer or "")[:300],
                date_key=datetime.now().strftime("%Y-%m-%d"),
            )
            db.session.add(log)
            db.session.commit()
            g.visit_id = log.id
        except Exception:
            db.session.rollback()

    @app.after_request
    def _track_visit_finish(resp):
        if getattr(g, "new_vid", None):
            resp.set_cookie("bq_vid", g.new_vid, max_age=365 * 24 * 3600,
                            httponly=True, samesite="Lax")
        if getattr(g, "visit_id", None):
            try:
                from models import VisitLog
                db.session.execute(
                    VisitLog.__table__.update()
                    .where(VisitLog.__table__.c.id == g.visit_id)
                    .values(status_code=resp.status_code))
                db.session.commit()
            except Exception:
                db.session.rollback()
        return resp

    # 模板全局函数：未上传图片时返回对应分辨率的纯色 PNG 占位图
    from placeholder import img_url, placeholder_url
    app.add_template_global(img_url)
    app.add_template_global(placeholder_url)

    # 后台管理页面
    @app.route("/admin")
    def admin_page():
        return render_template("admin.html")

    # 初始化数据库 & 种子数据 & 旧库迁移
    with app.app_context():
        from seed import seed_all
        from models import Company
        db.create_all()
        _migrate_db()
        if not Company.query.first():
            seed_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
