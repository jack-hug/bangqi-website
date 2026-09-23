# -*- coding: utf-8 -*-
"""产品批量上传 Blueprint
- GET  /api/product/batch_template  下载 Excel 模板 (.xlsx)
- POST /api/product/batch_upload    Excel + 图片 ZIP 一次性入库
"""
import datetime
import io
import os
import re
import shutil
import tempfile
import time
import uuid
import zipfile
from collections import defaultdict

from flask import Blueprint, request, jsonify, send_file
from openpyxl import Workbook, load_workbook
from sqlalchemy import inspect

from extensions import db
from models import (Product, ProductImage,
                    DosageForm, Trademark, FuncCategory, Manufacturer)
from routes.api import login_required
from richtext import to_html as rich_to_html

bp = Blueprint("batch", __name__, url_prefix="/api/product")


# ============================================================
# Excel 模板字段定义（顺序即列顺序；header 为表头中文）
# ============================================================
TEMPLATE_COLUMNS = [
    ("code",            "产品编号(SKU)*",  "BQ-001"),
    ("name",            "产品名称*",       "示例：阿胶益寿口服液"),
    ("manufacturer",    "生产企业",       "邦琪"),
    ("dosage_form",     "剂型",           "丸剂"),
    ("trademark",       "商标",           "琪康牌"),
    ("func_category",   "功能分类",       "补益气血"),
    ("spec",            "规格",           "200粒/瓶"),
    ("indications",     "功能主治",       "补中益气，升阳举陷。…"),
    ("usage",           "用法用量",       "口服，一次 8 丸，一日 2~3 次"),
    ("content",         "产品介绍",       "公司丸剂代表性品种之一，…"),
    ("date",            "上市日期",       "2025-09-01"),
    ("cover",           "封面图文件名",   "cover.jpg（ZIP 内的文件名，可留空）"),
]
COL_WIDTHS = [18, 28, 12, 12, 12, 14, 14, 40, 30, 40, 14, 28]


def _safe_filename(name):
    """清洗图片文件名，避免路径穿越和特殊字符"""
    name = (name or "").strip().replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._\-\u4e00-\u9fff]", "_", name)
    return name or ("img_%d" % int(time.time() * 1000))


def _norm_key(s):
    """SKU 目录名归一化：去首尾空白（大小写由调用方用 .lower() 统一处理）"""
    return (s or "").strip()


@bp.route("/batch_template", methods=["GET"])
@login_required
def batch_template():
    """生成 Excel 模板下载"""
    wb = Workbook()
    ws = wb.active
    ws.title = "产品批量上传"
    # 表头
    for ci, (key, header, _) in enumerate(TEMPLATE_COLUMNS, start=1):
        cell = ws.cell(row=1, column=ci, value=header)
        cell.font = cell.font.copy(bold=True)
        ws.column_dimensions[cell.column_letter].width = COL_WIDTHS[ci - 1]
    # 示例行（上市日期用当天，与后台新增产品的默认值一致）
    for ci, (key, _, sample) in enumerate(TEMPLATE_COLUMNS, start=1):
        if key == "date":
            sample = time.strftime("%Y-%m-%d")
        ws.cell(row=2, column=ci, value=sample)
    # 顶部说明
    ws.insert_rows(1)
    note_cell = ws.cell(row=1, column=1,
        value="说明：带 * 的列为必填；生产企业/剂型/商标/功能分类 不存在将自动新建；"
              "图片请按 ZIP 目录 <产品编号>/<图片文件名> 整理；"
              "封面图文件名留空则取该 SKU 第一张图片作为封面；"
              "上市日期留空则默认取当天。")
    note_cell.font = note_cell.font.copy(italic=True, color="666666")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(TEMPLATE_COLUMNS))

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    fname = "products_template_%s.xlsx" % time.strftime("%Y%m%d_%H%M%S")
    return send_file(bio, as_attachment=True, download_name=fname,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@bp.route("/batch_upload", methods=["POST"])
@login_required
def batch_upload():
    """Excel + ZIP 批量上传

    表单字段:
      excel: .xlsx 文件
      zip:   .zip 图片包（顶层目录为产品编号，内含图片）
    """
    excel_f = request.files.get("excel")
    zip_f = request.files.get("zip")
    if not excel_f or not zip_f:
        return jsonify({"error": "请同时上传 Excel 文件和图片 ZIP"}), 400

    # 临时目录（处理完删除）
    tmpdir = tempfile.mkdtemp(prefix="bq_batch_")
    try:
        excel_path = os.path.join(tmpdir, _safe_filename(excel_f.filename or "products.xlsx"))
        zip_path = os.path.join(tmpdir, _safe_filename(zip_f.filename or "photos.zip"))
        excel_f.save(excel_path)
        zip_f.save(zip_path)

        # 1) 解析 Excel
        try:
            wb = load_workbook(excel_path, data_only=True, read_only=True)
        except Exception as e:
            return jsonify({"error": "Excel 解析失败：%s" % e}), 400
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))

        def _norm_header(s):
            """表头归一化：全角空格→半角、去空白、去尾部 * 标记"""
            return str(s or "").replace("\u3000", " ").strip().rstrip("*").strip()

        # 找表头行：取「匹配到模板列名最多」的一行，并跳过顶部合并的说明行。
        # 注意：说明行文案里含「产品编号 / 生产企业 / 剂型 / 商标 / 功能分类 / 封面…」
        # 等词，旧逻辑（第一行含「产品编号」即当表头）会把说明行误认成表头，
        # 于是 产品名称 列永远匹配不到 → 每一行都报「缺少产品名称」。
        header_idx, best_score = None, 0
        for ri, row in enumerate(rows[:10]):
            cells = [_norm_header(c) for c in row if c is not None and str(c).strip()]
            if not cells:
                continue
            if cells[0].startswith("说明"):
                continue
            score = 0
            for _key, _header_cn, _sample in TEMPLATE_COLUMNS:
                target = _norm_header(_header_cn)
                if any(target == c or target in c for c in cells):
                    score += 1
            if score > best_score:
                header_idx, best_score = ri, score
        # 至少要认出 产品编号 + 产品名称 两列，才认为这行是表头
        if header_idx is None or best_score < 2:
            return jsonify({"error": "未识别到表头，请确认存在包含「产品编号(SKU)*」「产品名称*」的表头行"}), 400

        header = [_norm_header(c) for c in rows[header_idx]]

        # 按列名映射：先与模板表头精确比对，再退化为关键字包含匹配
        HEADER_ALIASES = {
            "code":         ["产品编号", "code", "sku"],
            "name":         ["产品名称", "名称", "name"],
            "manufacturer": ["生产企业", "厂商"],
            "dosage_form":  ["剂型"],
            "trademark":    ["商标"],
            "func_category": ["功能分类", "分类"],
            "spec":         ["规格"],
            "indications":  ["功能主治", "主治"],
            "usage":        ["用法用量", "用法"],
            "content":      ["产品介绍", "介绍"],
            "date":         ["上市日期", "日期", "date"],
            "cover":        ["封面图文件名", "封面"],
        }
        col_map = {}
        for key, header_cn, _sample in TEMPLATE_COLUMNS:
            target = _norm_header(header_cn)
            if target in header:
                col_map[key] = header.index(target)
                continue
            for alias in HEADER_ALIASES.get(key, []):
                hit = next((hj for hj, h in enumerate(header)
                            if h and (alias in h or h.lower() == alias.lower())), None)
                if hit is not None:
                    col_map[key] = hit
                    break

        # 数据行：带真实 Excel 行号（1 起），空行已剔除，行号仍可对上原表
        body = [(ri + 1, r) for ri, r in enumerate(rows)
                if ri > header_idx and r and any(c not in (None, "") for c in r)]

        # 2) 解压 ZIP，建立 SKU -> 图片文件名列表 映射
        sku_images = defaultdict(list)   # {code_lower: [filename1, filename2, ...]}
        sku_dirs = {}                     # {code_lower: folder_name_in_zip}
        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                # 路径以 "/" 分隔，取第一段作为 SKU 目录
                parts = info.filename.replace("\\", "/").split("/", 1)
                if len(parts) < 2 or not parts[1]:
                    # 顶层散落文件：忽略
                    continue
                dir_name = parts[0].strip()
                fname = parts[1]
                if not dir_name or not fname:
                    continue
                key = _norm_key(dir_name).lower()
                sku_images[key].append(fname)
                sku_dirs[key] = dir_name
        # 文件名排序（保证 1,2,3... 与 01,02,03... 顺序一致）
        for k in sku_images:
            sku_images[k] = sorted(
                sku_images[k],
                key=lambda x: (len(re.match(r"^(\d+)", x).group(1)) if re.match(r"^(\d+)", x) else 99, x))

        # 3) 加载 / 缓存 FK 表
        form_cache = {f.name: f for f in DosageForm.query.all()}
        tm_cache = {t.name: t for t in Trademark.query.all()}
        fc_cache = {c.name: c for c in FuncCategory.query.all()}
        mfg_cache = {m.name: m for m in Manufacturer.query.all()}

        # 已存在 SKU 索引
        code_index = {p.code: p for p in Product.query.all() if p.code}

        # 图片落地目录
        products_img_dir = os.path.join("static", "uploads", "products")
        os.makedirs(products_img_dir, exist_ok=True)

        created = updated = images_added = 0
        errors = []

        def get_or_create(cls, cache, raw_name, **extra):
            n = (raw_name or "").strip()
            if not n:
                return None
            if n in cache:
                return cache[n]
            obj = cls(name=n, **extra)
            db.session.add(obj)
            db.session.flush()
            cache[n] = obj
            return obj

        # 4) 逐行处理
        with zipfile.ZipFile(zip_path, "r") as zf:
            zip_names = set(zf.namelist())
            for ri, row in body:
                def cell(k):
                    idx = col_map.get(k)
                    if idx is None or idx >= len(row):
                        return ""
                    v = row[idx]
                    if v is None:
                        return ""
                    # 日期统一成 YYYY-MM-DD（Excel 里可能是 datetime，也可能是日期序列号）
                    if isinstance(v, (datetime.datetime, datetime.date)):
                        return v.strftime("%Y-%m-%d")
                    if k == "date" and isinstance(v, (int, float)) and 20000 <= float(v) <= 60000:
                        return (datetime.datetime(1899, 12, 30)
                                + datetime.timedelta(days=float(v))).strftime("%Y-%m-%d")
                    if isinstance(v, (int, float)) and float(v).is_integer():
                        return str(int(v))
                    return str(v).strip()

                code = cell("code")
                name = cell("name")
                if not code and not name:
                    continue  # 空行
                if not code:
                    errors.append({"row": ri, "code": "", "message": "缺少产品编号"})
                    continue
                if not name:
                    errors.append({"row": ri, "code": code, "message": "缺少产品名称"})
                    continue
                # 名称按 code 去重
                existing = code_index.get(code)
                was_new = existing is None
                try:
                    df = get_or_create(DosageForm, form_cache, cell("dosage_form"))
                    tm = get_or_create(Trademark, tm_cache, cell("trademark"))
                    fc = get_or_create(FuncCategory, fc_cache, cell("func_category"))
                    mf = get_or_create(Manufacturer, mfg_cache, cell("manufacturer"))

                    if existing:
                        p = existing
                    else:
                        # 先把 name 等字段全设上，再 flush，避免 NOT NULL 失败
                        p = Product(code=code, name=name)
                        db.session.add(p)
                        code_index[code] = p

                    # 始终覆盖/更新产品字段（若新值非空则更新，否则保留旧值）
                    p.name = name
                    if df:  p.dosage_form_id = df.id
                    if tm:  p.trademark_id = tm.id
                    if fc:  p.func_category_id = fc.id
                    if mf:  p.manufacturer_id = mf.id
                    for fk in ("spec", "indications", "usage", "content", "date"):
                        v = cell(fk)
                        if v:
                            # 产品介绍是富文本字段：Excel 单元格是纯文本，统一按
                            # 段落规范化，避免与后台编辑器保存的格式不一致
                            setattr(p, fk, rich_to_html(v) if fk == "content" else v)
                    # 上市日期留空时默认当天（与后台新增产品的默认值保持一致）
                    if not p.date:
                        p.date = time.strftime("%Y-%m-%d")
                    db.session.flush()

                    # 5) 处理图片
                    key = code.lower()
                    dir_name = sku_dirs.get(key, code)
                    images_added_for_row = 0
                    cover_name = cell("cover")
                    # 用行内计数器，避免 relationship 缓存导致 sort_order 重复
                    existing_max = max([i.sort_order for i in (p.images or [])], default=-1)
                    for img_idx, fname in enumerate(sku_images.get(key, [])):
                        # 跳过非图片
                        ext = os.path.splitext(fname)[1].lower()
                        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                            continue
                        zip_entry = "%s/%s" % (dir_name, fname)
                        if zip_entry not in zip_names:
                            continue
                        # 目标目录：static/uploads/products/<code>/
                        target_dir = os.path.join(products_img_dir, _norm_key(code))
                        os.makedirs(target_dir, exist_ok=True)
                        safe_name = _safe_filename(fname)
                        target_path = os.path.join(target_dir, safe_name)
                        # 解压单文件
                        with zf.open(zip_entry) as src, open(target_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        # 计算 URL 路径（用正斜杠）
                        url_path = "/%s/%s/%s" % (products_img_dir.replace("\\", "/"),
                                                  _norm_key(code), safe_name)
                        # 查重：同 URL 不重复插入
                        exists_img = any(img.image == url_path for img in (p.images or []))
                        if exists_img:
                            continue
                        title = os.path.splitext(fname)[0]
                        sort_order = existing_max + 1 + img_idx
                        img = ProductImage(product_id=p.id, title=title,
                                           color="ph-gray", image=url_path,
                                           sort_order=sort_order)
                        db.session.add(img)
                        images_added_for_row += 1
                        # 封面图
                        if cover_name and fname.strip() == cover_name.strip():
                            p.image = url_path
                        elif not cover_name and not p.image and images_added_for_row == 1:
                            p.image = url_path
                    images_added += images_added_for_row
                    if was_new:
                        created += 1
                    else:
                        updated += 1
                    db.session.flush()
                except Exception as e:
                    errors.append({"row": ri, "code": code, "message": str(e)})
                    db.session.rollback()

        db.session.commit()

        return jsonify({
            "ok": True,
            "summary": {
                "rows_total": len(body),
                "products_created": created,
                "products_updated": updated,
                "images_added": images_added,
                "errors_count": len(errors),
            },
            "errors": errors[:50],
            "unmatched_zips": sorted(set(sku_dirs.keys()) - {c.lower() for c in code_index.keys()})[:20],
        })
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
