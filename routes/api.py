# -*- coding: utf-8 -*-
"""后台管理 REST API Blueprint - 所有内容的增删改查"""
import os
import time
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from functools import wraps
from extensions import db, client_ip
from models import (Company, Banner, HomeStat, CompanyImage, EnterpriseCard,
                    DosageForm, Trademark, FuncCategory, Manufacturer, Product, ProductImage,
                    NewsCategory, News, Page, PageSection, PageStat, AdminUser,
                    LoginLog, ActivityLog)
from config import Config
from richtext import to_html as rich_to_html

bp = Blueprint("api", __name__, url_prefix="/api")

# 富文本字段（content）：保存时统一规范化成 <p> 段落格式。
# 历史数据是纯文本（用 \n 分行），Quill 编辑器会重新包 <p>；
# 不统一的话，同一份内容「前台直出」与「编辑保存后」呈现会不一致，
# 后台列表还会直接露出 <p></p> 标签。见 richtext.py。
RICH_FIELDS = {
    Product: ("content",),
    News: ("content",),
    PageSection: ("content",),
}


def normalize_rich(model, data):
    keys = RICH_FIELDS.get(model)
    if not keys:
        return data
    for key in keys:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            data[key] = rich_to_html(val)
    return data

# ============================================================
# 模块映射（用于操作审计 / 模块最后更新时间）
# ============================================================
MODULE_MAP = {
    Company: ("company", "公司信息"),
    Banner: ("banner", "首页 Banner"),
    HomeStat: ("home_stat", "首页数据"),
    CompanyImage: ("company_image", "公司形象图"),
    EnterpriseCard: ("enterprise_card", "企业卡片"),
    DosageForm: ("dosage_form", "剂型管理"),
    Trademark: ("trademark", "商标管理"),
    FuncCategory: ("func_category", "功能分类"),
    Manufacturer: ("manufacturer", "生产企业"),
    Product: ("product", "产品中心"),
    ProductImage: ("product_image", "产品图片"),
    NewsCategory: ("news_category", "新闻分类"),
    News: ("news", "新闻资讯"),
    Page: ("page", "栏目页面"),
    PageSection: ("page_section", "栏目段落"),
    PageStat: ("page_stat", "栏目统计"),
}


def _target_name(item):
    for attr in ("name", "title", "label", "subtitle"):
        val = getattr(item, attr, None)
        if val:
            return str(val)[:200]
    return "#%s" % (getattr(item, "id", "?"))


def log_activity(model, action, item):
    """记录后台增删改操作（失败不影响主流程）"""
    try:
        key, label = MODULE_MAP.get(model, (model.__tablename__, model.__tablename__))
        db.session.add(ActivityLog(
            module=key, module_label=label, action=action,
            target_id=getattr(item, "id", None),
            target_name=_target_name(item),
            admin=session.get("admin_user", ""),
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()

# ============================================================
# 认证
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "未登录"}), 401
        return f(*args, **kwargs)
    return decorated


# ============================================================
# 图片上传
# ============================================================
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(_BASE_DIR, "static", "uploads")
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_UPLOAD = 8 * 1024 * 1024   # 8MB


@bp.route("/upload", methods=["POST"])
@login_required
def upload_image():
    """通用图片上传：multipart 表单字段 file，按年月归档到 static/uploads/"""
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": "未选择文件"}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": "不支持的格式，仅支持 PNG/JPG/JPEG/GIF/WEBP"}), 400
    data = f.read()
    if not data:
        return jsonify({"error": "文件为空"}), 400
    if len(data) > MAX_UPLOAD:
        return jsonify({"error": "文件超过 8MB 限制"}), 400

    subdir = time.strftime("%Y%m")
    save_dir = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(save_dir, exist_ok=True)
    fname = "%d_%s%s" % (int(time.time() * 1000), uuid.uuid4().hex[:8], ext)
    with open(os.path.join(save_dir, fname), "wb") as fp:
        fp.write(data)
    return jsonify({"url": "/static/uploads/%s/%s" % (subdir, fname),
                    "size": len(data)})


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    ip = client_ip()
    ua = (request.user_agent.string or "")[:300]
    # ---- 同一 IP 5 分钟内连续 10 次失败 → 临时封禁 ----
    from datetime import timedelta
    ban_window = datetime.utcnow() - timedelta(minutes=5)
    recent_fails = LoginLog.query.filter(
        LoginLog.ip == ip, LoginLog.success == False,
        LoginLog.created_at >= ban_window
    ).count()
    if recent_fails >= 10:
        return jsonify({"error": "尝试过于频繁，请 5 分钟后再试"}), 429
    user = AdminUser.query.filter_by(username=username).first()
    ok = bool(user and user.check_password(password))
    try:
        db.session.add(LoginLog(username=username[:50], ip=ip, ua=ua, success=ok,
                                reason="" if ok else "用户名或密码错误"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    if ok:
        session["admin_logged_in"] = True
        session["admin_user"] = username
        return jsonify({"ok": True, "username": username})
    return jsonify({"error": "用户名或密码错误"}), 401


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@bp.route("/auth/check")
def auth_check():
    if session.get("admin_logged_in"):
        return jsonify({"logged_in": True, "username": session.get("admin_user", "")})
    return jsonify({"logged_in": False})


# ============================================================
# 通用 CRUD 工厂
# ============================================================
def _get_list(model, order_field=None):
    q = model.query
    if order_field is not None:
        q = q.order_by(order_field)
    return jsonify([item.to_dict() for item in q.all()])


def _get_one(model, item_id):
    item = model.query.get_or_404(item_id)
    return jsonify(item.to_dict())


def _create(model, data):
    data = normalize_rich(model, data)
    item = model()
    for key, val in data.items():
        if hasattr(item, key) and val is not None:
            setattr(item, key, val)
    db.session.add(item)
    db.session.commit()
    log_activity(model, "create", item)
    return jsonify(item.to_dict())


def _update(model, item_id, data):
    data = normalize_rich(model, data)
    item = model.query.get_or_404(item_id)
    for key, val in data.items():
        if hasattr(item, key) and val is not None:
            setattr(item, key, val)
    db.session.commit()
    log_activity(model, "update", item)
    return jsonify(item.to_dict())


def _delete(model, item_id):
    item = model.query.get_or_404(item_id)
    log_activity(model, "delete", item)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"ok": True})


def _read_body():
    return request.get_json(silent=True) or {}


# ============================================================
# 通用排序（后台列表内的「上移 / 下移」）
# ============================================================
# 前端 resource key → 模型。只放行真正按 sort_order 展示且列表不分页的模块。
_SORT_MODELS = {
    "banner": Banner,
    "home-stat": HomeStat,
    "company-image": CompanyImage,
    "enterprise-card": EnterpriseCard,
    "dosage-form": DosageForm,
    "trademark": Trademark,
    "func-category": FuncCategory,
    "manufacturer": Manufacturer,
    "news-category": NewsCategory,
}


@bp.route("/sort/<module>", methods=["POST"])
@login_required
def sort_reorder(module):
    """按前端传来的 id 顺序，把该模块的 sort_order 重排为 0..n-1。

    供后台列表的「上移 / 下移」使用：一次整表重排，顺带把历史数据里
    重复或缺失的排序值归一化，避免 order_by(sort_order) 结果错乱。
    """
    model = _SORT_MODELS.get(module)
    if model is None:
        return jsonify({"error": "该模块不支持排序: %s" % module}), 400
    ids = _read_body().get("ids") or []
    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "缺少 ids 参数"}), 400
    try:
        ids = [int(i) for i in ids]
    except (TypeError, ValueError):
        return jsonify({"error": "ids 必须是整数数组"}), 400

    items = {it.id: it for it in model.query.filter(model.id.in_(ids)).all()}
    missing = [i for i in ids if i not in items]
    if missing:
        return jsonify({"error": "记录不存在: %s" % missing}), 404
    for pos, iid in enumerate(ids):
        items[iid].sort_order = pos
    db.session.commit()
    return jsonify({"ok": True, "count": len(ids)})


# ============================================================
# 公司信息（单条）
# ============================================================
@bp.route("/company", methods=["GET"])
@login_required
def company_get():
    c = Company.query.first()
    return jsonify(c.to_dict() if c else {})


@bp.route("/company", methods=["PUT"])
@login_required
def company_update():
    c = Company.query.first()
    if not c:
        c = Company()
        db.session.add(c)
    data = _read_body()
    for key in ["name", "full_name", "intro", "address", "phone", "email", "news_footer"]:
        if key in data:
            setattr(c, key, data[key])
    db.session.commit()
    log_activity(Company, "update", c)
    return jsonify(c.to_dict())


# ============================================================
# Banner
# ============================================================
@bp.route("/banner", methods=["GET"])
@login_required
def banner_list():
    return _get_list(Banner, Banner.sort_order)

@bp.route("/banner/<int:item_id>", methods=["GET"])
@login_required
def banner_one(item_id):
    return _get_one(Banner, item_id)

@bp.route("/banner", methods=["POST"])
@login_required
def banner_create():
    return _create(Banner, _read_body())

@bp.route("/banner/<int:item_id>", methods=["PUT"])
@login_required
def banner_update(item_id):
    return _update(Banner, item_id, _read_body())

@bp.route("/banner/<int:item_id>", methods=["DELETE"])
@login_required
def banner_delete(item_id):
    return _delete(Banner, item_id)


# ============================================================
# 首页统计
# ============================================================
@bp.route("/home-stat", methods=["GET"])
@login_required
def home_stat_list():
    return _get_list(HomeStat, HomeStat.sort_order)

@bp.route("/home-stat/<int:item_id>", methods=["GET"])
@login_required
def home_stat_one(item_id):
    return _get_one(HomeStat, item_id)

@bp.route("/home-stat", methods=["POST"])
@login_required
def home_stat_create():
    return _create(HomeStat, _read_body())

@bp.route("/home-stat/<int:item_id>", methods=["PUT"])
@login_required
def home_stat_update(item_id):
    return _update(HomeStat, item_id, _read_body())

@bp.route("/home-stat/<int:item_id>", methods=["DELETE"])
@login_required
def home_stat_delete(item_id):
    return _delete(HomeStat, item_id)


# ============================================================
# 公司图片
# ============================================================
@bp.route("/company-image", methods=["GET"])
@login_required
def company_image_list():
    return _get_list(CompanyImage, CompanyImage.sort_order)

@bp.route("/company-image/<int:item_id>", methods=["GET"])
@login_required
def company_image_one(item_id):
    return _get_one(CompanyImage, item_id)

@bp.route("/company-image", methods=["POST"])
@login_required
def company_image_create():
    return _create(CompanyImage, _read_body())

@bp.route("/company-image/<int:item_id>", methods=["PUT"])
@login_required
def company_image_update(item_id):
    return _update(CompanyImage, item_id, _read_body())

@bp.route("/company-image/<int:item_id>", methods=["DELETE"])
@login_required
def company_image_delete(item_id):
    return _delete(CompanyImage, item_id)


# ============================================================
# 企业卡片
# ============================================================
@bp.route("/enterprise-card", methods=["GET"])
@login_required
def enterprise_card_list():
    return _get_list(EnterpriseCard, EnterpriseCard.sort_order)

@bp.route("/enterprise-card/<int:item_id>", methods=["GET"])
@login_required
def enterprise_card_one(item_id):
    return _get_one(EnterpriseCard, item_id)

@bp.route("/enterprise-card", methods=["POST"])
@login_required
def enterprise_card_create():
    return _create(EnterpriseCard, _read_body())

@bp.route("/enterprise-card/<int:item_id>", methods=["PUT"])
@login_required
def enterprise_card_update(item_id):
    return _update(EnterpriseCard, item_id, _read_body())

@bp.route("/enterprise-card/<int:item_id>", methods=["DELETE"])
@login_required
def enterprise_card_delete(item_id):
    return _delete(EnterpriseCard, item_id)


# ============================================================
# 剂型
# ============================================================
@bp.route("/dosage-form", methods=["GET"])
@login_required
def dosage_form_list():
    return _get_list(DosageForm, DosageForm.sort_order)

@bp.route("/dosage-form/<int:item_id>", methods=["GET"])
@login_required
def dosage_form_one(item_id):
    return _get_one(DosageForm, item_id)

@bp.route("/dosage-form", methods=["POST"])
@login_required
def dosage_form_create():
    return _create(DosageForm, _read_body())

@bp.route("/dosage-form/<int:item_id>", methods=["PUT"])
@login_required
def dosage_form_update(item_id):
    return _update(DosageForm, item_id, _read_body())

@bp.route("/dosage-form/<int:item_id>", methods=["DELETE"])
@login_required
def dosage_form_delete(item_id):
    return _delete(DosageForm, item_id)


# ============================================================
# 商标
# ============================================================
@bp.route("/trademark", methods=["GET"])
@login_required
def trademark_list():
    return _get_list(Trademark, Trademark.sort_order)

@bp.route("/trademark/<int:item_id>", methods=["GET"])
@login_required
def trademark_one(item_id):
    return _get_one(Trademark, item_id)

@bp.route("/trademark", methods=["POST"])
@login_required
def trademark_create():
    return _create(Trademark, _read_body())

@bp.route("/trademark/<int:item_id>", methods=["PUT"])
@login_required
def trademark_update(item_id):
    return _update(Trademark, item_id, _read_body())

@bp.route("/trademark/<int:item_id>", methods=["DELETE"])
@login_required
def trademark_delete(item_id):
    return _delete(Trademark, item_id)


# ============================================================
# 功能分类
# ============================================================
@bp.route("/func-category", methods=["GET"])
@login_required
def func_category_list():
    return _get_list(FuncCategory, FuncCategory.sort_order)

@bp.route("/func-category/<int:item_id>", methods=["GET"])
@login_required
def func_category_one(item_id):
    return _get_one(FuncCategory, item_id)

@bp.route("/func-category", methods=["POST"])
@login_required
def func_category_create():
    return _create(FuncCategory, _read_body())

@bp.route("/func-category/<int:item_id>", methods=["PUT"])
@login_required
def func_category_update(item_id):
    return _update(FuncCategory, item_id, _read_body())

@bp.route("/func-category/<int:item_id>", methods=["DELETE"])
@login_required
def func_category_delete(item_id):
    return _delete(FuncCategory, item_id)


# ============================================================
# 生产企业（集团下属企业）
# ============================================================
@bp.route("/manufacturer", methods=["GET"])
@login_required
def manufacturer_list():
    return _get_list(Manufacturer, Manufacturer.sort_order)

@bp.route("/manufacturer/<int:item_id>", methods=["GET"])
@login_required
def manufacturer_one(item_id):
    return _get_one(Manufacturer, item_id)

@bp.route("/manufacturer", methods=["POST"])
@login_required
def manufacturer_create():
    return _create(Manufacturer, _read_body())

@bp.route("/manufacturer/<int:item_id>", methods=["PUT"])
@login_required
def manufacturer_update(item_id):
    return _update(Manufacturer, item_id, _read_body())

@bp.route("/manufacturer/<int:item_id>", methods=["DELETE"])
@login_required
def manufacturer_delete(item_id):
    return _delete(Manufacturer, item_id)


# ============================================================
# 产品
# ============================================================
@bp.route("/product", methods=["GET"])
@login_required
def product_list():
    return _get_list(Product, Product.date.desc())

@bp.route("/product/<int:item_id>", methods=["GET"])
@login_required
def product_one(item_id):
    item = Product.query.get_or_404(item_id)
    d = item.to_dict()
    d["images"] = [img.to_dict() for img in item.images]
    return jsonify(d)

@bp.route("/product", methods=["POST"])
@login_required
def product_create():
    data = normalize_rich(Product, _read_body())
    item = Product()
    for key in ["code", "name", "dosage_form_id", "trademark_id", "func_category_id",
                "manufacturer_id", "spec", "indications", "usage", "content",
                "date", "clicks", "color", "image"]:
        if key in data:
            setattr(item, key, data[key])
    db.session.add(item)
    db.session.commit()
    log_activity(Product, "create", item)
    return jsonify(item.to_dict())

@bp.route("/product/<int:item_id>", methods=["PUT"])
@login_required
def product_update(item_id):
    data = normalize_rich(Product, _read_body())
    item = Product.query.get_or_404(item_id)
    for key in ["code", "name", "dosage_form_id", "trademark_id", "func_category_id",
                "manufacturer_id", "spec", "indications", "usage", "content",
                "date", "clicks", "color", "image"]:
        if key in data:
            setattr(item, key, data[key])
    db.session.commit()
    log_activity(Product, "update", item)
    return jsonify(item.to_dict())

@bp.route("/product/<int:item_id>", methods=["DELETE"])
@login_required
def product_delete(item_id):
    return _delete(Product, item_id)


# ============================================================
# 产品图片
# ============================================================
@bp.route("/product-image", methods=["GET"])
@login_required
def product_image_list():
    product_id = request.args.get("product_id", type=int)
    q = ProductImage.query
    if product_id:
        q = q.filter_by(product_id=product_id)
    return jsonify([img.to_dict() for img in q.order_by(ProductImage.sort_order).all()])

@bp.route("/product-image/<int:item_id>", methods=["GET"])
@login_required
def product_image_one(item_id):
    return _get_one(ProductImage, item_id)

@bp.route("/product-image", methods=["POST"])
@login_required
def product_image_create():
    return _create(ProductImage, _read_body())

@bp.route("/product-image/<int:item_id>", methods=["PUT"])
@login_required
def product_image_update(item_id):
    return _update(ProductImage, item_id, _read_body())

@bp.route("/product-image/<int:item_id>", methods=["DELETE"])
@login_required
def product_image_delete(item_id):
    return _delete(ProductImage, item_id)


@bp.route("/product/<int:product_id>/images", methods=["POST"])
@login_required
def product_images_batch_upload(product_id):
    """产品图片批量上传：一次接收多个文件（字段名 file），自动追加到该产品的图片集"""
    product = Product.query.get_or_404(product_id)
    files = request.files.getlist("file")
    if not files:
        return jsonify({"error": "未选择文件"}), 400

    subdir = time.strftime("%Y%m")
    save_dir = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(save_dir, exist_ok=True)

    base_order = db.session.query(db.func.max(ProductImage.sort_order)).filter_by(
        product_id=product_id).scalar() or 0

    created, skipped = [], []
    for f in files:
        if not f or not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            skipped.append({"name": f.filename, "reason": "不支持的格式"})
            continue
        data = f.read()
        if not data or len(data) > MAX_UPLOAD:
            skipped.append({"name": f.filename, "reason": "文件为空或超过 8MB"})
            continue
        fname = "%d_%s%s" % (int(time.time() * 1000), uuid.uuid4().hex[:8], ext)
        with open(os.path.join(save_dir, fname), "wb") as fp:
            fp.write(data)
        base_order += 1
        img = ProductImage(product_id=product_id,
                           title=os.path.splitext(f.filename)[0][:100],
                           image="/static/uploads/%s/%s" % (subdir, fname),
                           sort_order=base_order)
        db.session.add(img)
        created.append(img)

    db.session.commit()
    return jsonify({"created": [i.to_dict() for i in created],
                    "skipped": skipped,
                    "total": len(product.images)})


# ============================================================
# 新闻分类
# ============================================================
@bp.route("/news-category", methods=["GET"])
@login_required
def news_category_list():
    return _get_list(NewsCategory, NewsCategory.sort_order)

@bp.route("/news-category/<int:item_id>", methods=["GET"])
@login_required
def news_category_one(item_id):
    return _get_one(NewsCategory, item_id)

@bp.route("/news-category", methods=["POST"])
@login_required
def news_category_create():
    return _create(NewsCategory, _read_body())

@bp.route("/news-category/<int:item_id>", methods=["PUT"])
@login_required
def news_category_update(item_id):
    return _update(NewsCategory, item_id, _read_body())

@bp.route("/news-category/<int:item_id>", methods=["DELETE"])
@login_required
def news_category_delete(item_id):
    return _delete(NewsCategory, item_id)


# ============================================================
# 新闻
# ============================================================
@bp.route("/news", methods=["GET"])
@login_required
def news_list():
    return _get_list(News, News.date.desc())

@bp.route("/news/<int:item_id>", methods=["GET"])
@login_required
def news_one(item_id):
    return _get_one(News, item_id)

@bp.route("/news", methods=["POST"])
@login_required
def news_create():
    return _create(News, _read_body())

@bp.route("/news/<int:item_id>", methods=["PUT"])
@login_required
def news_update(item_id):
    return _update(News, item_id, _read_body())

@bp.route("/news/<int:item_id>", methods=["DELETE"])
@login_required
def news_delete(item_id):
    return _delete(News, item_id)


# ============================================================
# 栏目页面
# ============================================================
@bp.route("/page", methods=["GET"])
@login_required
def page_list():
    section = request.args.get("section")
    q = Page.query
    if section:
        q = q.filter_by(section=section)
    return jsonify([p.to_dict() for p in q.order_by(Page.sort_order).all()])

@bp.route("/page/<int:item_id>", methods=["GET"])
@login_required
def page_one(item_id):
    return _get_one(Page, item_id)

@bp.route("/page", methods=["POST"])
@login_required
def page_create():
    return _create(Page, _read_body())

@bp.route("/page/<int:item_id>", methods=["PUT"])
@login_required
def page_update(item_id):
    return _update(Page, item_id, _read_body())

@bp.route("/page/<int:item_id>", methods=["DELETE"])
@login_required
def page_delete(item_id):
    return _delete(Page, item_id)


# ============================================================
# 栏目页面 - 段落
# ============================================================
@bp.route("/page-section", methods=["GET"])
@login_required
def page_section_list():
    page_id = request.args.get("page_id", type=int)
    q = PageSection.query
    if page_id:
        q = q.filter_by(page_id=page_id)
    return jsonify([s.to_dict() for s in q.order_by(PageSection.sort_order).all()])

@bp.route("/page-section/<int:item_id>", methods=["GET"])
@login_required
def page_section_one(item_id):
    return _get_one(PageSection, item_id)

@bp.route("/page-section", methods=["POST"])
@login_required
def page_section_create():
    return _create(PageSection, _read_body())

@bp.route("/page-section/<int:item_id>", methods=["PUT"])
@login_required
def page_section_update(item_id):
    return _update(PageSection, item_id, _read_body())

@bp.route("/page-section/<int:item_id>", methods=["DELETE"])
@login_required
def page_section_delete(item_id):
    return _delete(PageSection, item_id)


# ============================================================
# 栏目页面 - 统计
# ============================================================
@bp.route("/page-stat", methods=["GET"])
@login_required
def page_stat_list():
    page_id = request.args.get("page_id", type=int)
    q = PageStat.query
    if page_id:
        q = q.filter_by(page_id=page_id)
    return jsonify([s.to_dict() for s in q.order_by(PageStat.sort_order).all()])

@bp.route("/page-stat/<int:item_id>", methods=["GET"])
@login_required
def page_stat_one(item_id):
    return _get_one(PageStat, item_id)

@bp.route("/page-stat", methods=["POST"])
@login_required
def page_stat_create():
    return _create(PageStat, _read_body())

@bp.route("/page-stat/<int:item_id>", methods=["PUT"])
@login_required
def page_stat_update(item_id):
    return _update(PageStat, item_id, _read_body())

@bp.route("/page-stat/<int:item_id>", methods=["DELETE"])
@login_required
def page_stat_delete(item_id):
    return _delete(PageStat, item_id)


# ============================================================
# 仪表盘统计
# ============================================================
@bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return jsonify({
        "products": Product.query.count(),
        "news": News.query.count(),
        "banners": Banner.query.count(),
        "dosage_forms": DosageForm.query.count(),
        "trademarks": Trademark.query.count(),
        "news_categories": NewsCategory.query.count(),
        "pages": Page.query.count(),
    })
