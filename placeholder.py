# -*- coding: utf-8 -*-
"""占位图生成器 - 零依赖生成不同分辨率的纯色 PNG

未上传图片之前，前台所有图片位统一显示按用途分辨率生成的纯色 PNG；
上传图片后由 img_url() 优先返回上传图地址。
"""
import os
import struct
import zlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PH_DIR = os.path.join(BASE_DIR, "static", "uploads", "placeholders")

# ============================================================
# 品牌色系（与前台 .ph-* 色块样式一一对应，朱红主导 + 蓝绿辅助）
# ============================================================
COLORS = {
    "ph-red":     (230, 33, 41),    # 朱红主色
    "ph-red-2":   (193, 19, 24),    # 深红
    "ph-am":      (208, 141, 68),   # 琥珀（膏剂·暖金）
    "ph-gy":      (212, 152, 69),   # 糖浆·金沙
    "ph-li":      (215, 120, 120),  # 搽剂·绛红
    "ph-pi":      (200, 163, 88),   # 丸剂·棕金
    "ph-ta":      (79, 163, 168),   # 片剂·碧青
    "ph-cp":      (93, 160, 196),   # 胶囊·远海蓝
    "ph-ti":      (90, 133, 180),   # 酊剂·青黛
    "ph-gr":      (58, 144, 152),   # 颗粒·湖青
    "ph-gray":    (153, 153, 153),  # 通用灰
}

# ============================================================
# 用途 → 分辨率（不同位置生成不同分辨率的占位图）
# ============================================================
SIZES = {
    "banner":          (1920, 750),  # 首页 Banner - 增高至 1920×750
    "factory":         (960, 540),   # 厂区图片轮播
    "form":            (480, 600),   # 剂型矩阵卡片 - 480×600
    "corp":            (370, 650),   # 企业相关卡片 - 370×650
    "product":         (480, 320),   # 产品列表卡片
    "product-detail":  (640, 640),   # 产品详情轮播
    "product-banner":  (480, 220),   # 产品详情宣传图
    "news-thumb":      (320, 220),   # 新闻列表缩略图
    "news-feature":    (960, 560),   # 首页焦点新闻大图
    "news-article":    (960, 520),   # 新闻正文配图
    "cat-hero":        (960, 300),   # 栏目页头图
    "cat-img":         (480, 300),   # 栏目页配图
}

DEFAULT_SIZE = (480, 320)
DEFAULT_COLOR = "ph-red"


def _png_chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def make_solid_png(path, w, h, rgb):
    """用 zlib + struct 直接写出一张纯色 8bit RGB PNG（无需 Pillow）"""
    row = b"\x00" + bytes(rgb) * w          # 每行：filter byte 0 + w 个像素
    raw = row * h
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)   # 8bit 真彩色
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_png_chunk(b"IHDR", ihdr))
        f.write(_png_chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(_png_chunk(b"IEND", b""))


def placeholder_url(kind, color=None):
    """生成（如缺失）并返回某种用途 + 某颜色的纯色占位 PNG 地址"""
    w, h = SIZES.get(kind, DEFAULT_SIZE)
    rgb = COLORS.get(color or DEFAULT_COLOR, COLORS[DEFAULT_COLOR])
    name = "%s_%dx%d_%02x%02x%02x.png" % (kind, w, h, rgb[0], rgb[1], rgb[2])
    os.makedirs(PH_DIR, exist_ok=True)
    path = os.path.join(PH_DIR, name)
    if not os.path.exists(path):
        make_solid_png(path, w, h, rgb)
    return "/static/uploads/placeholders/" + name


def img_url(image, kind, color=None):
    """模板辅助函数：有上传图片用上传图，否则生成对应分辨率的纯色 PNG 占位"""
    image = (image or "").strip()
    if image:
        return image
    return placeholder_url(kind, color)
