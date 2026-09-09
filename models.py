# -*- coding: utf-8 -*-
"""数据库模型 - 邦琪药业官网全部内容表"""
from datetime import datetime

from extensions import db


def _now():
    """统一使用服务器本地时间"""
    return datetime.now()


# ============================================================
# 公司基本信息（单条记录 id=1）
# ============================================================
class Company(db.Model):
    __tablename__ = "company"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200))
    intro = db.Column(db.Text)
    address = db.Column(db.String(300))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    news_footer = db.Column(db.Text)  # 资讯详情页尾文案

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "full_name": self.full_name,
            "intro": self.intro, "address": self.address,
            "phone": self.phone, "email": self.email,
            "news_footer": self.news_footer,
        }


# ============================================================
# 首页 Banner 轮播
# ============================================================
class Banner(db.Model):
    __tablename__ = "banner"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(300))
    kicker = db.Column(db.String(100))
    btn_text = db.Column(db.String(50))
    btn_link = db.Column(db.String(200))
    color = db.Column(db.String(20), default="ph-green")
    image = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "subtitle": self.subtitle,
            "kicker": self.kicker, "btn_text": self.btn_text,
            "btn_link": self.btn_link, "color": self.color, "image": self.image,
            "sort_order": self.sort_order, "is_active": self.is_active,
        }


# ============================================================
# 首页公司简介 - 三个数据圆环
# ============================================================
class HomeStat(db.Model):
    __tablename__ = "home_stat"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(20), nullable=False)
    unit = db.Column(db.String(10))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "label": self.label, "value": self.value,
            "unit": self.unit, "sort_order": self.sort_order,
        }


# ============================================================
# 首页公司简介 - 左侧厂区图片轮播
# ============================================================
class CompanyImage(db.Model):
    __tablename__ = "company_image"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    color = db.Column(db.String(20), default="ph-green")
    image = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "color": self.color,
            "image": self.image,
            "sort_order": self.sort_order, "is_active": self.is_active,
        }


# ============================================================
# 首页企业相关 - 四张上浮卡片
# ============================================================
class EnterpriseCard(db.Model):
    __tablename__ = "enterprise_card"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    link = db.Column(db.String(200))
    color = db.Column(db.String(20), default="ph-green")
    image = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "link": self.link, "color": self.color, "image": self.image,
            "sort_order": self.sort_order,
        }


# ============================================================
# 剂型
# ============================================================
class DosageForm(db.Model):
    __tablename__ = "dosage_form"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    color = db.Column(db.String(20), default="ph-green")
    image = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name,
            "description": self.description, "color": self.color,
            "image": self.image, "sort_order": self.sort_order,
        }


# ============================================================
# 商标
# ============================================================
class Trademark(db.Model):
    __tablename__ = "trademark"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "sort_order": self.sort_order}


# ============================================================
# 功能主治分类
# ============================================================
class FuncCategory(db.Model):
    __tablename__ = "func_category"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "sort_order": self.sort_order}


# ============================================================
# 生产企业（集团公司下属企业）
# ============================================================
class Manufacturer(db.Model):
    __tablename__ = "manufacturer"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {"id": self.id, "name": self.name,
                "description": self.description, "sort_order": self.sort_order}


# ============================================================
# 产品
# ============================================================
class Product(db.Model):
    __tablename__ = "product"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, index=True)   # 产品编号 (SKU)，批量上传匹配键
    name = db.Column(db.String(100), nullable=False)
    dosage_form_id = db.Column(db.Integer, db.ForeignKey("dosage_form.id"))
    trademark_id = db.Column(db.Integer, db.ForeignKey("trademark.id"))
    func_category_id = db.Column(db.Integer, db.ForeignKey("func_category.id"))
    manufacturer_id = db.Column(db.Integer, db.ForeignKey("manufacturer.id"))
    spec = db.Column(db.String(100))
    indications = db.Column(db.Text)
    usage = db.Column(db.Text)
    content = db.Column(db.Text)
    date = db.Column(db.String(20))
    clicks = db.Column(db.Integer, default=0)
    color = db.Column(db.String(20), default="ph-green")
    image = db.Column(db.String(300))

    dosage_form = db.relationship("DosageForm", backref="products")
    trademark = db.relationship("Trademark", backref="products")
    func_category = db.relationship("FuncCategory", backref="products")
    manufacturer = db.relationship("Manufacturer", backref="products")
    images = db.relationship("ProductImage", backref="product",
                             cascade="all, delete-orphan",
                             order_by="ProductImage.sort_order")

    def to_dict(self):
        df = self.dosage_form
        tm = self.trademark
        fc = self.func_category
        mf = self.manufacturer
        return {
            "id": self.id, "code": self.code, "name": self.name,
            "dosage_form_id": self.dosage_form_id,
            "trademark_id": self.trademark_id,
            "func_category_id": self.func_category_id,
            "manufacturer_id": self.manufacturer_id,
            "form": df.name if df is not None else "",
            "trademark": tm.name if tm is not None else "",
            "func": fc.name if fc is not None else "",
            "manufacturer": mf.name if mf is not None else "",
            "spec": self.spec, "indications": self.indications,
            "usage": self.usage, "content": self.content,
            "date": self.date, "clicks": self.clicks, "color": self.color,
            "image": self.image,
        }


# ============================================================
# 产品图片
# ============================================================
class ProductImage(db.Model):
    __tablename__ = "product_image"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    title = db.Column(db.String(100))
    color = db.Column(db.String(20), default="ph-gray")
    image = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "product_id": self.product_id,
            "title": self.title, "color": self.color, "image": self.image,
            "sort_order": self.sort_order,
        }


# ============================================================
# 新闻分类
# ============================================================
class NewsCategory(db.Model):
    __tablename__ = "news_category"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "sort_order": self.sort_order}


# ============================================================
# 新闻文章
# ============================================================
class News(db.Model):
    __tablename__ = "news"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("news_category.id"))
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text)
    date = db.Column(db.String(20))
    clicks = db.Column(db.Integer, default=0)
    image = db.Column(db.String(300))

    category = db.relationship("NewsCategory", backref="news_list")

    def to_dict(self):
        cat = self.category
        return {
            "id": self.id, "category_id": self.category_id,
            "category": cat.name if cat is not None else "",
            "title": self.title, "content": self.content,
            "date": self.date, "clicks": self.clicks, "image": self.image,
        }


# ============================================================
# 栏目页面（公司介绍 / 研发生产 / 联系我们）
# ============================================================
class Page(db.Model):
    __tablename__ = "page"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(20), nullable=False)  # about / research / contact
    title = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default="ph-green")
    image = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)

    sections = db.relationship("PageSection", backref="page",
                               cascade="all, delete-orphan",
                               order_by="PageSection.sort_order")
    stats = db.relationship("PageStat", backref="page",
                            cascade="all, delete-orphan",
                            order_by="PageStat.sort_order")

    def to_dict(self):
        return {
            "id": self.id, "section": self.section,
            "title": self.title, "color": self.color, "image": self.image,
            "sort_order": self.sort_order,
            "sections": [s.to_dict() for s in self.sections],
            "stats": [s.to_dict() for s in self.stats],
        }


# ============================================================
# 栏目页面 - 段落（小标题 + 正文）
# ============================================================
class PageSection(db.Model):
    __tablename__ = "page_section"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey("page.id"), nullable=False)
    subtitle = db.Column(db.String(100))
    content = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "page_id": self.page_id,
            "subtitle": self.subtitle, "content": self.content,
            "sort_order": self.sort_order,
        }


# ============================================================
# 栏目页面 - 统计数据
# ============================================================
class PageStat(db.Model):
    __tablename__ = "page_stat"
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey("page.id"), nullable=False)
    label = db.Column(db.String(50))
    value = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "page_id": self.page_id,
            "label": self.label, "value": self.value,
            "sort_order": self.sort_order,
        }


# ============================================================
# 管理员用户
# ============================================================
class AdminUser(db.Model):
    __tablename__ = "admin_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


# ============================================================
# 站点访问日志（PV / UV 统计）
# visitor_id 为浏览器 cookie 标识，用于 UV 去重；ip 作为兜底去重
# ============================================================
class VisitLog(db.Model):
    __tablename__ = "visit_log"
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(64), index=True)
    path = db.Column(db.String(300))
    ip = db.Column(db.String(64))
    ua = db.Column(db.String(300))
    referer = db.Column(db.String(300))
    status_code = db.Column(db.Integer, default=200)
    date_key = db.Column(db.String(10), index=True)   # YYYY-MM-DD（本地日期）
    created_at = db.Column(db.DateTime, default=_now, index=True)

    def to_dict(self):
        return {
            "id": self.id, "visitor_id": self.visitor_id, "path": self.path,
            "ip": self.ip, "ua": self.ua, "referer": self.referer,
            "status_code": self.status_code, "date_key": self.date_key,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }


# ============================================================
# 后台登录日志（成功 / 失败全记录，用于安全审计与预警）
# ============================================================
class LoginLog(db.Model):
    __tablename__ = "login_log"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    ip = db.Column(db.String(64), index=True)
    ua = db.Column(db.String(300))
    success = db.Column(db.Boolean, default=False, index=True)
    reason = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=_now, index=True)

    def to_dict(self):
        return {
            "id": self.id, "username": self.username, "ip": self.ip,
            "ua": self.ua, "success": bool(self.success), "reason": self.reason,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }


# ============================================================
# 后台操作审计（各页面/模块最后更新时间的数据来源）
# ============================================================
class ActivityLog(db.Model):
    __tablename__ = "activity_log"
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(50), index=True)        # 模块 key：product / news ...
    module_label = db.Column(db.String(50))              # 模块中文名
    action = db.Column(db.String(20))                    # create / update / delete
    target_id = db.Column(db.Integer)
    target_name = db.Column(db.String(200))
    admin = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=_now, index=True)

    def to_dict(self):
        return {
            "id": self.id, "module": self.module, "module_label": self.module_label,
            "action": self.action, "target_id": self.target_id,
            "target_name": self.target_name, "admin": self.admin,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }


# ============================================================
# 站点配置（KV 存储，如 SSL 监控域名）
# ============================================================
class Setting(db.Model):
    __tablename__ = "setting"
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)

    def to_dict(self):
        return {"key": self.key, "value": self.value,
                "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None}


def get_setting(key, default=None):
    row = Setting.query.get(key)
    return row.value if row and row.value is not None else default


def set_setting(key, value):
    row = Setting.query.get(key)
    if row is None:
        row = Setting(key=key)
        db.session.add(row)
    row.value = "" if value is None else str(value)
    db.session.commit()
    return row
