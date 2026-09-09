# -*- coding: utf-8 -*-
"""前端路由 Blueprint - 从数据库读取数据渲染页面"""
from flask import Blueprint, render_template, request, abort, g, jsonify
from sqlalchemy import or_
from models import (Company, DosageForm, Trademark, FuncCategory, Manufacturer,
                    Product, News, NewsCategory, Page, PageSection, PageStat)
from extensions import db

bp = Blueprint("main", __name__)

# ============================================================
# 辅助函数
# ============================================================
def _get_company():
    c = Company.query.first()
    if not c:
        return {"name": "", "full_name": "", "intro": "", "address": "", "phone": "", "email": ""}
    return c.to_dict()


def _get_dosage_forms():
    return [f.name for f in DosageForm.query.order_by(DosageForm.sort_order).all()]


def _get_form_desc():
    return {f.name: f.description for f in DosageForm.query.all()}


def _get_news_categories():
    return [c.name for c in NewsCategory.query.order_by(NewsCategory.sort_order).all()]


def _get_hot_products():
    return [p.to_dict() for p in Product.query.order_by(Product.clicks.desc()).limit(20).all()]


def _get_hot_news():
    return [n.to_dict() for n in News.query.order_by(News.clicks.desc()).limit(10).all()]


def _get_latest_news():
    return [n.to_dict() for n in News.query.order_by(News.date.desc()).limit(5).all()]


def _build_pages_dict(section):
    """构建栏目页面字典，格式兼容模板：{title: {title, sections, stats}}"""
    pages = {}
    for page in Page.query.filter_by(section=section).order_by(Page.sort_order).all():
        pages[page.title] = {
            "title": page.title,
            "image": page.image,
            "color": page.color or "ph-green",
            "sections": [(s.subtitle, s.content) for s in page.sections],
            "stats": [(s.label, s.value) for s in page.stats],
        }
    return pages


def _qs(request, drop=None, extra=None):
    args = {k: v for k, v in request.args.items() if k not in ("page",) and k != drop}
    if extra:
        args.update(extra)
    return ("?" + "&".join(f"{k}={v}" for k, v in args.items())) if args else ""


# ============================================================
# 上下文处理器
# ============================================================
@bp.app_context_processor
def inject_globals():
    return {
        "COMPANY": _get_company(),
        "DOSAGE_FORMS": _get_dosage_forms(),
        "FORM_DESC": _get_form_desc(),
        "NEWS_CATEGORIES": _get_news_categories(),
        "hot_products": _get_hot_products(),
        "hot_news": _get_hot_news(),
        "latest_news": _get_latest_news(),
        "qs_except": lambda key: _qs(request, drop=key),
        "qs_append": lambda key, val: _qs(request, extra={key: val}),
        "qs_page": _qs(request),
    }


# ============================================================
# 路由
# ============================================================
@bp.route("/")
def index():
    from models import Banner, HomeStat, CompanyImage, EnterpriseCard
    return render_template("index.html",
                           banners=[b.to_dict() for b in Banner.query.filter_by(is_active=True).order_by(Banner.sort_order).all()],
                           home_stats=[s.to_dict() for s in HomeStat.query.order_by(HomeStat.sort_order).all()],
                           company_images=[c.to_dict() for c in CompanyImage.query.filter_by(is_active=True).order_by(CompanyImage.sort_order).all()],
                           enterprise_cards=[e.to_dict() for e in EnterpriseCard.query.order_by(EnterpriseCard.sort_order).all()],
                           dosage_form_cards=[f.to_dict() for f in DosageForm.query.order_by(DosageForm.sort_order).limit(8).all()])


@bp.route("/products")
def products():
    form = request.args.get("form")
    trademark = request.args.get("trademark")
    func = request.args.get("func")
    manufacturer = request.args.get("manufacturer")
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    query = Product.query
    if form:
        df = DosageForm.query.filter_by(name=form).first()
        query = query.filter_by(dosage_form_id=df.id) if df else query.filter(False)
    if trademark:
        tm = Trademark.query.filter_by(name=trademark).first()
        query = query.filter_by(trademark_id=tm.id) if tm else query.filter(False)
    if func:
        fc = FuncCategory.query.filter_by(name=func).first()
        query = query.filter_by(func_category_id=fc.id) if fc else query.filter(False)
    if manufacturer:
        mf = Manufacturer.query.filter_by(name=manufacturer).first()
        query = query.filter_by(manufacturer_id=mf.id) if mf else query.filter(False)

    query = query.order_by(Product.date.desc())
    total = query.count()
    per_page = 12
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return render_template("products.html",
                           products=[p.to_dict() for p in items],
                           page=page, pages=pages, total=total,
                           cur_form=form, cur_trademark=trademark, cur_func=func,
                           cur_manufacturer=manufacturer,
                           trademarks=[t.name for t in Trademark.query.order_by(Trademark.sort_order).all()],
                           functions=[f.name for f in FuncCategory.query.order_by(FuncCategory.sort_order).all()],
                           manufacturers=[m.name for m in Manufacturer.query.order_by(Manufacturer.sort_order).all()])


@bp.route("/products/<int:pid>")
def product_detail(pid):
    p = Product.query.get_or_404(pid)
    # 同剂型前后产品
    same_form = Product.query.filter_by(dosage_form_id=p.dosage_form_id).order_by(Product.id).all()
    idx = same_form.index(p)
    prev_p = same_form[idx - 1] if idx > 0 else same_form[-1]
    next_p = same_form[idx + 1] if idx < len(same_form) - 1 else same_form[0]

    # 点击量 +1
    p.clicks = (p.clicks or 0) + 1
    db.session.commit()

    # 产品图片（后台逐张上传；无图时前台显示纯色占位 PNG）
    images = [img.to_dict() for img in p.images]
    if not images:
        images = [
            {"title": p.name, "image": None, "color": p.color or "ph-green"},
            {"title": "包装实拍", "image": None, "color": "ph-gray"},
            {"title": "细节展示", "image": None, "color": "ph-green"},
        ]

    return render_template("product_detail.html",
                           p=p.to_dict(), images=images,
                           prev_p=prev_p.to_dict(), next_p=next_p.to_dict())


@bp.route("/news")
def news():
    category = request.args.get("category")
    query = News.query
    if category:
        nc = NewsCategory.query.filter_by(name=category).first()
        query = query.filter_by(category_id=nc.id) if nc else query.filter(False)
    items = query.order_by(News.date.desc()).all()
    return render_template("news.html", news_list=[n.to_dict() for n in items], cur_category=category)


@bp.route("/news/<int:nid>")
def news_detail(nid):
    n = News.query.get_or_404(nid)
    ordered = News.query.order_by(News.date.desc()).all()
    idx = ordered.index(n)
    prev_n = ordered[idx - 1] if idx > 0 else None
    next_n = ordered[idx + 1] if idx < len(ordered) - 1 else None

    # 点击量 +1
    n.clicks = (n.clicks or 0) + 1
    db.session.commit()

    return render_template("news_detail.html",
                           n=n.to_dict(),
                           prev_n=prev_n.to_dict() if prev_n else None,
                           next_n=next_n.to_dict() if next_n else None)


@bp.route("/about")
@bp.route("/about/<category>")
def about(category="集团介绍"):
    pages = _build_pages_dict("about")
    if category not in pages:
        abort(404)
    return render_template("category_page.html", pages=pages, active=category,
                           section_title="公司介绍", base_url="about")


@bp.route("/research")
@bp.route("/research/<category>")
def research(category="产品研发"):
    pages = _build_pages_dict("research")
    if category not in pages:
        abort(404)
    return render_template("category_page.html", pages=pages, active=category,
                           section_title="研发生产", base_url="research")


@bp.route("/contact")
@bp.route("/contact/<category>")
def contact(category="联系方式"):
    pages = _build_pages_dict("contact")
    if category not in pages:
        abort(404)
    return render_template("category_page.html", pages=pages, active=category,
                           section_title="联系我们", base_url="contact")


# ============================================================
# 公共 API：产品实时搜索（顶部导航「产品查询」下拉使用）
# ============================================================
@bp.route("/api/search/product")
def api_search_product():
    """根据关键字模糊匹配产品名称 / 规格 / 功能主治，返回前 10 条。
    前台不展示产品编号，因此不参与匹配。公开接口，不要求登录。"""
    kw = (request.args.get("q") or "").strip()
    if not kw:
        return jsonify(items=[], total=0)
    like = f"%{kw}%"
    # SQLAlchemy `ilike` 在 SQLite 下会走 lower() LIKE；中文 LIKE 不区分大小写已可用
    query = Product.query.filter(
        or_(
            Product.name.like(like),
            Product.spec.like(like),
            Product.indications.like(like),
        )
    ).order_by(Product.date.desc(), Product.id.desc()).limit(10)
    items = []
    for p in query.all():
        d = p.to_dict()
        # 仅返回下拉需要的字段，减小 payload
        items.append({
            "id": d["id"],
            "name": d["name"],
            "form": d.get("form") or "",
            "trademark": d.get("trademark") or "",
            "indications": (d.get("indications") or "")[:60],
            "image": d.get("image") or "",
            "color": d.get("color") or "ph-green",
        })
    return jsonify(items=items, total=len(items), q=kw)
