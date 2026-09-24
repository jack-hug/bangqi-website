# -*- coding: utf-8 -*-
"""富文本内容规范化 —— 产品介绍 / 文章正文 / 栏目段落 三处共用

背景：这三处内容的历史数据是**纯文本**（段落之间用 \\n 分隔，批量导入的产品介绍
更是直接来自 Excel 单元格），后来后台换成 Quill 富文本编辑器，Quill 会把内容
重新包成 <p> 段落，于是同一份内容在「前台直出」和「编辑保存后」两种状态下长得
不一样：
  · 后台列表里直接露出 <p>…</p> 标签
  · 纯文本里的换行在编辑器里被折叠成一个空格，多段变一段
  · 保存后空段落 <p><br></p> 会在前台撑出大片空白

这里把两种输入统一成同一套规范 HTML：
  纯文本（不是以块级标签开头） → 转义后按 \\n 拆成 <p> 段落
  已经是 HTML                  → 清理危险标签/属性 + 去掉空段落
                                 （首尾空段删除、连续空段压成一个）

判定「是不是 HTML」用的是**开头必须是块级/行内结构标签**，不能太宽松：
Excel 导入的纯文本里可能出现「价格 a<b」这种裸尖括号，宽松匹配会把后面的
文字当成标签属性吞掉。

用法：
  to_html(raw)   → 规范 HTML（前台渲染 / 后端保存时调用）
  to_plain(raw)  → 纯文本（摘要、后台列表预览用）
"""
import html as _html
import re

# 「是 HTML」的判定：内容以结构标签开头（Quill 的输出必然如此）
_BLOCK_START_RE = re.compile(
    r"^\s*</?(?:p|div|h[1-6]|ul|ol|li|blockquote|pre|img|hr|table|br|"
    r"span|strong|em|u|s|sub|sup|a)\b", re.I)

# 危险标签：连内容一起删除
_DANGEROUS_BLOCK_RE = re.compile(
    r"<(script|style|iframe|object|embed|form|frame|frameset)\b[^>]*>.*?</\1\s*>",
    re.I | re.S)
# 危险标签：孤立的开/闭标签直接删除
_DANGEROUS_STRAY_RE = re.compile(
    r"</?(?:script|style|iframe|object|embed|form|frame|frameset|link|meta|base)\b[^>]*>",
    re.I)
# 事件属性 on*="..."
_EVENT_ATTR_RE = re.compile(r"\son[a-z]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
# href/src 属性（整体匹配，值里带 javascript: 的整条删掉，避免留下残缺引号）
_URL_ATTR_RE = re.compile(r"\s(href|src)\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)


def _drop_js_attr(match):
    return "" if "javascript:" in match.group(0).lower() else match.group(0)

# 形如 <p> </p> / <b>x</b> 的标签
_TAG_RE = re.compile(r"<[a-zA-Z/!][^>]*>")
# <img ...>（含自闭合写法），用于补加载属性
_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.I)
# 空段落：<p></p> / <p> </p> / <p><br></p> / <p>&nbsp;</p>
_EMPTY_P_RE = re.compile(r"<p>(?:[ \t\u00a0]|&nbsp;|<br\s*/?>)*</p>", re.I)
# 标签之间仅含换行与缩进的空白（Quill 输出美化时会出现），先折掉再判断空段
_TAG_GAP_RE = re.compile(r">[ \t]*\n[ \t]*<")
# 块级收尾标签 → 空格，避免 to_plain 时前后段文字粘在一起
_BLOCK_END_RE = re.compile(r"</(?:p|div|h[1-6]|li|tr|blockquote)\s*>", re.I)


def text_to_html(text):
    """纯文本 → <p> 段落（空行最多保留一个 <p><br></p>，首尾不留空）"""
    out = []
    pending_blank = False
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            if out:
                pending_blank = True
            continue
        if pending_blank and out:
            out.append("<p><br></p>")
        pending_blank = False
        out.append("<p>%s</p>" % _html.escape(line))
    return "".join(out)


def sanitize_html(html):
    """去掉脚本类标签与其内容、内联事件属性、javascript: 协议"""
    s = _DANGEROUS_BLOCK_RE.sub("", html or "")
    s = _DANGEROUS_STRAY_RE.sub("", s)
    s = _EVENT_ATTR_RE.sub("", s)
    s = _URL_ATTR_RE.sub(_drop_js_attr, s)
    return s


def ensure_img_attrs(html):
    """给正文 <img> 补 loading="lazy" decoding="async"（缺失才补，幂等）。

    正文插图都在首屏以下，懒加载能明显减少首屏流量；已有该属性（比如用户
    手写过 loading="eager"）则原样保留，不覆盖。
    """
    def _fix(m):
        tag = m.group(0)
        add = []
        if not re.search(r"\bloading\s*=", tag, re.I):
            add.append('loading="lazy"')
        if not re.search(r"\bdecoding\s*=", tag, re.I):
            add.append('decoding="async"')
        if not add:
            return tag
        body = tag[1:-1].strip()
        if body.endswith("/"):
            body = body[:-1].rstrip()
        return "<%s %s>" % (body, " ".join(add))

    return _IMG_TAG_RE.sub(_fix, html)


def clean_html(html):
    """清理：危险标签 → 空段落（<p></p> 去掉、连续压成一个、首尾删除）→ 图片属性"""
    s = sanitize_html(html).strip()
    if not s:
        return ""
    s = _TAG_GAP_RE.sub("><", s)
    # 先统一成 <p><br></p> 再折叠，便于识别各种写法
    s = _EMPTY_P_RE.sub("<p><br></p>", s)
    s = re.sub(r"(?:<p><br\s*/?></p>)+", "<p><br></p>", s)
    s = re.sub(r"^(?:<p><br\s*/?></p>)+", "", s)
    s = re.sub(r"(?:<p><br\s*/?></p>)+$", "", s)
    return ensure_img_attrs(s.strip())


def to_html(raw):
    """统一入口：纯文本或 HTML → 规范 HTML"""
    if raw is None:
        return ""
    s = str(raw).replace("\r\n", "\n").replace("\r", "\n").strip()
    if not s:
        return ""
    if _BLOCK_START_RE.match(s):
        return clean_html(s)
    return text_to_html(s)


def to_plain(raw):
    """规范后取纯文本：块级标签之间补空格，避免段落粘连（摘要、列表预览用）"""
    s = to_html(raw)
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = _BLOCK_END_RE.sub(" ", s)
    s = _TAG_RE.sub("", s)
    s = s.replace("&nbsp;", " ")
    s = _html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()
