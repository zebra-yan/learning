# -*- coding: utf-8 -*-
from __future__ import annotations

import zipfile
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}

def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    paras = []
    for p in root.findall(".//w:p", NS):
        runs = []
        for t in p.findall(".//w:t", NS):
            if t.text:
                runs.append(t.text)
        line = "".join(runs).strip()
        if line:
            paras.append(line)
    return "\n".join(paras)


def pptx_slide_texts(path: Path) -> list[tuple[int, str]]:
    slides = []
    with zipfile.ZipFile(path) as z:
        names = sorted(
            [n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")],
            key=lambda n: int(re.search(r"slide(\d+)\.xml", n).group(1)),
        )
        for n in names:
            idx = int(re.search(r"slide(\d+)\.xml", n).group(1))
            xml = z.read(n)
            root = ET.fromstring(xml)
            texts = []
            for t in root.findall(".//a:t", NS):
                if t.text:
                    texts.append(t.text.strip())
            body = "\n".join([t for t in texts if t])
            slides.append((idx, body))
    return slides


def main():
    base = Path(r"D:\DeepLearning\严锐鹏213332980")
    thesis = base / "论文修改16.docx"
    ref1 = base / "毕业答辩_王涛.pptx"
    ref2 = Path(r"D:\DeepLearning\严锐鹏213332980\李玮毕业答辩.pptx")
    if not ref2.exists():
        # try glob
        for p in base.glob("*.pptx"):
            if "李玮" in p.name or "毕业答辩" in p.name:
                pass
    out_dir = Path(r"d:\repos\learning\_extract_out")
    out_dir.mkdir(exist_ok=True)

    if thesis.exists():
        (out_dir / "thesis.txt").write_text(docx_text(thesis), encoding="utf-8")
        print("thesis ok", thesis)
    else:
        print("thesis missing", thesis)

    for label, p in [("wangtao", ref1), ("liwei", ref2)]:
        if p.exists():
            lines = [f"=== slide {i} ===\n{t}\n" for i, t in pptx_slide_texts(p)]
            (out_dir / f"ref_{label}.txt").write_text("\n".join(lines), encoding="utf-8")
            print(label, "ok", p, "slides", len(lines))
        else:
            print(label, "missing", p)


if __name__ == "__main__":
    main()
