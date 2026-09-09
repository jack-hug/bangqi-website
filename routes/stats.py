# -*- coding: utf-8 -*-
"""站点统计与安全监控 API

提供后台仪表盘所需的全部数据：
  · 今日 / 昨日 PV、UV
  · 近 N 天访问趋势（7 / 30 天可切换）
  · 最近登录记录（含 IP、UA、成功失败）
  · 异常登录 / 攻击预警
  · 各页面 & 模块最后更新时间
  · SSL 证书到期天数
"""
import json
import os
import socket
import ssl
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from sqlalchemy import func, text

from extensions import db
from models import (VisitLog, LoginLog, ActivityLog, Company, Banner, HomeStat,
                    CompanyImage, EnterpriseCard, DosageForm, Trademark,
                    FuncCategory, Manufacturer, Product, ProductImage,
                    NewsCategory, News, Page, PageSection, PageStat,
                    get_setting, set_setting)
from config import Config
from routes.api import login_required

bp = Blueprint("stats", __name__, url_prefix="/api/stats")

# SSL 检查结果缓存时长（秒）
SSL_CACHE_TTL = 6 * 3600


# ============================================================
# 工具
# ============================================================
def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _date_str(d):
    return d.strftime("%Y-%m-%d")


def _uv_between(start_date, end_date):
    q = db.session.query(
        func.count(func.distinct(func.coalesce(VisitLog.visitor_id, VisitLog.ip)))
    ).filter(VisitLog.date_key >= start_date, VisitLog.date_key <= end_date)
    return q.scalar() or 0


def _pv_between(start_date, end_date):
    return db.session.query(func.count(VisitLog.id)).filter(
        VisitLog.date_key >= start_date, VisitLog.date_key <= end_date).scalar() or 0


# ============================================================
# 概览：今日 PV / UV
# ============================================================
@bp.route("/overview")
@login_required
def overview():
    today = _today()
    yesterday = _date_str(datetime.now() - timedelta(days=1))
    d7 = _date_str(datetime.now() - timedelta(days=6))

    today_pv = _pv_between(today, today)
    today_uv = _uv_between(today, today)
    y_pv = _pv_between(yesterday, yesterday)
    y_uv = _uv_between(yesterday, yesterday)

    today_ip = db.session.query(
        func.count(func.distinct(VisitLog.ip))
    ).filter(VisitLog.date_key == today).scalar() or 0

    # 热门页面 TOP 8（今日）
    top_rows = (db.session.query(VisitLog.path, func.count(VisitLog.id).label("c"))
                .filter(VisitLog.date_key == today)
                .group_by(VisitLog.path)
                .order_by(text("c DESC")).limit(8).all())
    top_paths = [{"path": r[0], "count": r[1]} for r in top_rows]

    # 最近 7 天累计
    uv_7d = _uv_between(d7, today)
    pv_7d = _pv_between(d7, today)

    return jsonify({
        "today": {"pv": today_pv, "uv": today_uv, "ip": today_ip},
        "yesterday": {"pv": y_pv, "uv": y_uv},
        "last7": {"pv": pv_7d, "uv": uv_7d},
        "total": {
            "pv": db.session.query(func.count(VisitLog.id)).scalar() or 0,
            "uv": _uv_between("1970-01-01", "2999-12-31"),
        },
        "top_paths": top_paths,
    })


# ============================================================
# 访问趋势：近 N 天（7 / 30）
# ============================================================
@bp.route("/visits")
@login_required
def visits():
    try:
        days = int(request.args.get("days", 7))
    except ValueError:
        days = 7
    days = 7 if days not in (7, 30) else days

    today = datetime.now().date()
    start = today - timedelta(days=days - 1)

    rows = (db.session.query(VisitLog.date_key,
                             func.count(VisitLog.id).label("pv"),
                             func.count(func.distinct(
                                 func.coalesce(VisitLog.visitor_id, VisitLog.ip))).label("uv"))
            .filter(VisitLog.date_key >= _date_str(start), VisitLog.date_key <= _date_str(today))
            .group_by(VisitLog.date_key).all())
    data = {r[0]: {"pv": r[1], "uv": r[2]} for r in rows}

    series = []
    for i in range(days):
        d = start + timedelta(days=i)
        key = _date_str(d)
        item = data.get(key, {"pv": 0, "uv": 0})
        series.append({
            "date": key,
            "label": d.strftime("%m-%d"),
            "pv": item["pv"], "uv": item["uv"],
        })

    total_pv = sum(s["pv"] for s in series)
    total_uv = sum(s["uv"] for s in series)
    return jsonify({"days": days, "series": series,
                    "total_pv": total_pv, "total_uv": total_uv,
                    "avg_pv": round(total_pv / days, 1),
                    "peak": max(series, key=lambda s: s["pv"]) if series else None})


# ============================================================
# 最近登录记录（含 IP）
# ============================================================
@bp.route("/logins")
@login_required
def logins():
    try:
        limit = min(int(request.args.get("limit", 15)), 100)
    except ValueError:
        limit = 15
    rows = LoginLog.query.order_by(LoginLog.created_at.desc()).limit(limit).all()

    today = _today()
    today_start = datetime.strptime(today, "%Y-%m-%d")
    today_fail = LoginLog.query.filter(
        LoginLog.success.is_(False), LoginLog.created_at >= today_start).count()
    total_fail = LoginLog.query.filter(LoginLog.success.is_(False)).count()
    total_ok = LoginLog.query.filter(LoginLog.success.is_(True)).count()

    last = LoginLog.query.filter(LoginLog.success.is_(True)).order_by(
        LoginLog.created_at.desc()).first()

    return jsonify({
        "items": [r.to_dict() for r in rows],
        "stats": {
            "today_fail": today_fail,
            "total_fail": total_fail,
            "total_ok": total_ok,
            "last_login": last.to_dict() if last else None,
        },
    })


# ============================================================
# 异常登录 / 攻击预警
# ============================================================
@bp.route("/alerts")
@login_required
def alerts():
    now = datetime.now()
    alerts_out = []

    # 1) 暴力破解：同一 IP 近 30 分钟内失败 >= 5 次
    since30 = now - timedelta(minutes=30)
    rows = (db.session.query(LoginLog.ip, func.count(LoginLog.id).label("c"),
                             func.max(LoginLog.created_at).label("last"))
            .filter(LoginLog.success.is_(False), LoginLog.created_at >= since30)
            .group_by(LoginLog.ip).having(func.count(LoginLog.id) >= 5).all())
    for ip, c, last in rows:
        alerts_out.append({
            "level": "high", "type": "暴力破解",
            "title": "同一 IP 频繁登录失败",
            "detail": "近 30 分钟内登录失败 %d 次，疑似密码爆破" % c,
            "ip": ip, "count": c,
            "last_at": last.strftime("%Y-%m-%d %H:%M:%S") if last else None,
        })

    # 2) 持续性失败：24 小时内失败 >= 15 次（30 分钟规则未命中时的补充）
    since24 = now - timedelta(days=1)
    caught = {a["ip"] for a in alerts_out}
    rows = (db.session.query(LoginLog.ip, func.count(LoginLog.id).label("c"),
                             func.max(LoginLog.created_at).label("last"))
            .filter(LoginLog.success.is_(False), LoginLog.created_at >= since24)
            .group_by(LoginLog.ip).having(func.count(LoginLog.id) >= 15).all())
    for ip, c, last in rows:
        if ip in caught:
            continue
        alerts_out.append({
            "level": "medium", "type": "持续失败",
            "title": "24 小时内登录失败次数偏高",
            "detail": "累计失败 %d 次，建议核查该来源" % c,
            "ip": ip, "count": c,
            "last_at": last.strftime("%Y-%m-%d %H:%M:%S") if last else None,
        })

    # 3) 账号枚举：同一 IP 24 小时内尝试 >= 3 个不同用户名
    rows = (db.session.query(LoginLog.ip,
                             func.count(func.distinct(LoginLog.username)).label("uc"),
                             func.count(LoginLog.id).label("c"),
                             func.max(LoginLog.created_at).label("last"))
            .filter(LoginLog.created_at >= since24)
            .group_by(LoginLog.ip)
            .having(func.count(func.distinct(LoginLog.username)) >= 3).all())
    for ip, uc, c, last in rows:
        alerts_out.append({
            "level": "medium", "type": "账号枚举",
            "title": "同一 IP 尝试多个账号",
            "detail": "24 小时内尝试 %d 个不同账号（共 %d 次请求）" % (uc, c),
            "ip": ip, "count": c,
            "last_at": last.strftime("%Y-%m-%d %H:%M:%S") if last else None,
        })

    # 4) 新 IP 登录：最近一次成功登录的 IP 与该账号历史 IP 不同
    ok_rows = (LoginLog.query.filter(LoginLog.success.is_(True))
               .order_by(LoginLog.created_at.desc(), LoginLog.id.desc())
               .limit(20).all())
    if ok_rows:
        latest = ok_rows[0]
        history = {r.ip for r in ok_rows[1:]}
        if history and latest.ip not in history:
            alerts_out.append({
                "level": "low", "type": "异地登录",
                "title": "检测到新 IP 登录后台",
                "detail": "账号 %s 从新 IP 登录成功" % (latest.username or "-"),
                "ip": latest.ip, "count": 1,
                "last_at": latest.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

    # 5) 404 扫描：同一 IP 24 小时内 404 >= 20 次
    rows = (db.session.query(VisitLog.ip, func.count(VisitLog.id).label("c"),
                             func.max(VisitLog.created_at).label("last"))
            .filter(VisitLog.status_code == 404, VisitLog.created_at >= since24)
            .group_by(VisitLog.ip).having(func.count(VisitLog.id) >= 20).all())
    for ip, c, last in rows:
        alerts_out.append({
            "level": "medium", "type": "目录扫描",
            "title": "大量 404 请求，疑似漏洞扫描",
            "detail": "24 小时内 404 响应 %d 次" % c,
            "ip": ip, "count": c,
            "last_at": last.strftime("%Y-%m-%d %H:%M:%S") if last else None,
        })

    # 6) 高频访问：同一 IP 1 小时内 PV >= 300（疑似 CC / 爬虫）
    since1h = now - timedelta(hours=1)
    rows = (db.session.query(VisitLog.ip, func.count(VisitLog.id).label("c"),
                             func.max(VisitLog.created_at).label("last"))
            .filter(VisitLog.created_at >= since1h)
            .group_by(VisitLog.ip).having(func.count(VisitLog.id) >= 300).all())
    for ip, c, last in rows:
        alerts_out.append({
            "level": "medium", "type": "高频访问",
            "title": "单 IP 访问量异常偏高",
            "detail": "近 1 小时请求 %d 次，疑似采集或 CC 攻击" % c,
            "ip": ip, "count": c,
            "last_at": last.strftime("%Y-%m-%d %H:%M:%S") if last else None,
        })

    order = {"high": 0, "medium": 1, "low": 2}
    alerts_out.sort(key=lambda a: (order.get(a["level"], 9), a.get("last_at") or ""),
                    reverse=False)
    return jsonify({"items": alerts_out,
                    "counts": {
                        "high": sum(1 for a in alerts_out if a["level"] == "high"),
                        "medium": sum(1 for a in alerts_out if a["level"] == "medium"),
                        "low": sum(1 for a in alerts_out if a["level"] == "low"),
                    }})


# ============================================================
# 各页面 / 模块最后更新时间
# ============================================================
MODULES = [
    ("company",        "公司信息",   Company,        "/admin"),
    ("banner",         "首页 Banner", Banner,        "/admin"),
    ("home_stat",      "首页数据",   HomeStat,       "/admin"),
    ("company_image",  "公司形象图", CompanyImage,   "/admin"),
    ("enterprise_card", "企业卡片",  EnterpriseCard, "/admin"),
    ("product",        "产品中心",   Product,        "/products"),
    ("product_image",  "产品图片",   ProductImage,   "/admin"),
    ("news",           "新闻资讯",   News,           "/news"),
    ("news_category",  "新闻分类",   NewsCategory,   "/admin"),
    ("page",           "栏目页面",   Page,           "/admin"),
    ("page_section",   "栏目段落",   PageSection,    "/admin"),
    ("page_stat",      "栏目统计",   PageStat,       "/admin"),
    ("dosage_form",    "剂型管理",   DosageForm,     "/admin"),
    ("trademark",      "商标管理",   Trademark,      "/admin"),
    ("func_category",  "功能分类",   FuncCategory,   "/admin"),
    ("manufacturer",   "生产企业",   Manufacturer,   "/admin"),
]

ACTION_LABEL = {"create": "新增", "update": "修改", "delete": "删除"}


@bp.route("/module_updates")
@login_required
def module_updates():
    out = []
    for key, label, model, url in MODULES:
        table = model.__tablename__
        try:
            row = db.session.execute(text(
                "SELECT COUNT(*), MAX(updated_at) FROM %s" % table)).first()
            count = row[0] or 0
            updated_at = row[1]
        except Exception:
            count, updated_at = 0, None

        if isinstance(updated_at, str):
            try:
                updated_at = datetime.strptime(updated_at[:19], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                updated_at = None

        act = (ActivityLog.query.filter_by(module=key)
               .order_by(ActivityLog.created_at.desc()).first())

        # 取更新时间：模型 updated_at 与操作日志取较新者
        final_at = updated_at
        if act and act.created_at:
            if final_at is None or act.created_at > final_at:
                final_at = act.created_at

        out.append({
            "module": key, "label": label, "url": url,
            "count": count,
            "updated_at": final_at.strftime("%Y-%m-%d %H:%M:%S") if final_at else None,
            "last_action": ACTION_LABEL.get(act.action, act.action) if act else None,
            "last_target": act.target_name if act else None,
            "last_admin": act.admin if act else None,
        })

    out.sort(key=lambda m: (m["updated_at"] or ""), reverse=True)
    return jsonify({"items": out})


# ============================================================
# 最近操作动态
# ============================================================
@bp.route("/activities")
@login_required
def activities():
    try:
        limit = min(int(request.args.get("limit", 12)), 50)
    except ValueError:
        limit = 12
    rows = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
    return jsonify({"items": [r.to_dict() for r in rows]})


# ============================================================
# SSL 证书到期天数
# ============================================================
def _ssl_check(host):
    """连接 host:443 读取证书信息"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    with socket.create_connection((host, 443), timeout=6) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()

    not_before = datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notBefore"]))
    not_after = datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]))
    days_left = (not_after - datetime.now()).days

    issuer = ""
    for rdn in cert.get("issuer", ()):
        for k, v in rdn:
            if k in ("organizationName", "commonName"):
                issuer = v
                break
        if issuer:
            break

    subject = ""
    for rdn in cert.get("subject", ()):
        for k, v in rdn:
            if k == "commonName":
                subject = v
    sans = cert.get("subjectAltName", ())
    dns_names = [v for k, v in sans if k == "DNS"][:6]

    if days_left < 0:
        status = "expired"
    elif days_left <= 7:
        status = "danger"
    elif days_left <= 30:
        status = "warning"
    else:
        status = "ok"

    return {
        "host": host,
        "subject": subject,
        "issuer": issuer,
        "dns_names": dns_names,
        "valid_from": not_before.strftime("%Y-%m-%d"),
        "valid_to": not_after.strftime("%Y-%m-%d %H:%M"),
        "days_left": days_left,
        "status": status,
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None,
    }


@bp.route("/ssl", methods=["GET", "POST"])
@login_required
def ssl_info():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        host = (data.get("host") or "").strip().lower()
        host = host.replace("https://", "").replace("http://", "").split("/")[0]
        set_setting("ssl_host", host)
        set_setting("ssl_cache", "")
        if not host:
            return jsonify({"configured": False, "message": "已清除监控域名"})

    host = (get_setting("ssl_host") or getattr(Config, "SSL_CHECK_HOST", "") or "").strip()
    if not host:
        return jsonify({"configured": False, "host": "",
                        "message": "尚未配置监控域名"})

    force = request.args.get("refresh") == "1" or request.method == "POST"
    if not force:
        cached = get_setting("ssl_cache")
        if cached:
            try:
                data = json.loads(cached)
                checked = datetime.strptime(data["checked_at"], "%Y-%m-%d %H:%M:%S")
                if (datetime.now() - checked).total_seconds() < SSL_CACHE_TTL:
                    data["cached"] = True
                    return jsonify(data)
            except Exception:
                pass

    try:
        result = _ssl_check(host)
        result["configured"] = True
        result["cached"] = False
    except Exception as e:
        # 本地/内网环境或证书异常时给出可读信息，不抛 500
        result = {"configured": True, "host": host, "status": "error",
                  "error": "%s: %s" % (type(e).__name__, str(e)[:120]),
                  "days_left": None,
                  "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    set_setting("ssl_cache", json.dumps(result, ensure_ascii=False))
    return jsonify(result)
