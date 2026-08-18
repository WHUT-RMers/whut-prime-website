# -*- coding: utf-8 -*-
"""Maple Mono NF CN 子集化：从完整 TTF 生成页面用 woff2（常规 + 粗体）。

用法: python scripts/subset_font.py
"""
import sys
import zipfile
from pathlib import Path

from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "fonts-src"
DEST = ROOT / "src" / "assets" / "fonts"

# 页面源码文件，收集其中出现的字符
CHAR_SOURCES = [
    ROOT / "index.html",
    ROOT / "src",
]

# GB2312 一级 + 二级字库（共 6763 汉字）程序化生成
def gb2312_chars():
    chars = []
    for b1 in range(0xB0, 0xF8):
        for b2 in range(0xA1, 0xFF):
            try:
                chars.append(bytes([b1, b2]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    return "".join(chars)

# 常用符号（页面点缀 + 拉丁补充）
EXTRA = "！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～　、。·―《》〈〉「」『』【】〖〗—…～×÷→←↑↓↗✦●○■□▲△◇◆★☆°½¼¾ "

def collect_chars() -> str:
    seen = set()
    def add(text: str):
        for ch in text:
            seen.add(ch)
    for p in CHAR_SOURCES:
        if p.is_file():
            add(p.read_text(encoding="utf-8"))
        else:
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in {".vue", ".ts", ".css", ".html"}:
                    add(f.read_text(encoding="utf-8", errors="ignore"))
    add(gb2312_chars())
    add(EXTRA)
    ascii_chars = "".join(chr(i) for i in range(0x20, 0x7F))
    add(ascii_chars)
    return "".join(sorted(seen))

def extract_ttfs():
    zpath = SRC / "MapleMono-NF-CN.zip"
    out = SRC / "extracted"
    if not zpath.exists():
        sys.exit(f"zip 不存在: {zpath}")
    ttfs = list(out.rglob("*.ttf")) if out.exists() else []
    if not ttfs:
        with zipfile.ZipFile(zpath) as z:
            z.extractall(out)
        ttfs = list(out.rglob("*.ttf"))
    return ttfs

def pick(ttfs, bold: bool):
    cands = [t for t in ttfs if "NL" not in t.name and "Normal" not in t.name and "Italic" not in t.name]
    if bold:
        exact = [t for t in cands if t.name == "MapleMono-NF-CN-Bold.ttf"]
        if exact:
            return exact[0]
        cands = [t for t in cands if "Bold" in t.name]
    else:
        # 优先精确 Regular 文件；否则排除所有修饰字重
        reg = [t for t in cands if t.name.endswith("Regular.ttf")]
        if reg:
            return reg[0]
        cands = [t for t in cands if "Bold" not in t.name
                 and "Light" not in t.name and "Thin" not in t.name
                 and "Medium" not in t.name and "SemiBold" not in t.name
                 and "Extra" not in t.name]
    if not cands:
        sys.exit("未找到目标 TTF")
    cands.sort(key=lambda t: t.stat().st_size)
    return cands[0]

def make_woff2(src_ttf: Path, out_woff2: Path, text: str):
    DEST.mkdir(parents=True, exist_ok=True)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.notdef_outline = True
    options.name_IDs = ["*"]  # 保留原名
    options.recalc_bounds = True
    font = subset.load_font(src_ttf, options)
    ss = subset.Subsetter(options=options)
    ss.populate(text=text)
    ss.subset(font)
    subset.save_font(font, out_woff2, options)
    print(f"OK: {out_woff2.name} ({out_woff2.stat().st_size / 1024:.0f} KB) <- {src_ttf.name}")

def main():
    ttfs = extract_ttfs()
    print("zip 内 TTF 列表:")
    for t in sorted(ttfs)[:30]:
        print("  ", t.name)
    text = collect_chars()
    print(f"字符集大小: {len(text)}")
    make_woff2(pick(ttfs, bold=False), DEST / "MapleMonoNF-CN-400.woff2", text)
    make_woff2(pick(ttfs, bold=True), DEST / "MapleMonoNF-CN-700.woff2", text)

if __name__ == "__main__":
    main()
