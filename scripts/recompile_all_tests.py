import os
import sys
import subprocess
import glob
import fitz
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PDF_PATH = r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf"
XELATEX_EXE = r"C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe"

CH01_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01"
PAGES_DIR = os.path.join(CH01_DIR, "pages")
COMPS_DIR = os.path.join(CH01_DIR, "comparisons")
os.makedirs(COMPS_DIR, exist_ok=True)

TEMPLATE_HEADER = r"""\documentclass[10pt,oneside]{article}
\usepackage{fontspec}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{colortbl}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{tabularx}
\usepackage{multicol}
\usepackage{tikz}

\graphicspath{{images/}}

\setmainfont{Times New Roman}
\setsansfont{Arial}

\geometry{
    paperwidth=612.05pt,
    paperheight=720.05pt,
    top=24pt,
    headheight=14pt,
    headsep=14pt,
    bottom=28pt,
    footskip=14pt,
    left=34pt,
    right=34pt
}

\definecolor{stewartcyan}{RGB}{0, 121, 193}
\definecolor{stewartred}{RGB}{238, 48, 36}
\definecolor{stewarttableheader}{RGB}{225, 234, 247}
\definecolor{darkgray}{RGB}{60, 60, 60}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}

\newtcolorbox{definitionbox}{
    colback=white,
    colframe=stewartred,
    arc=0mm,
    boxrule=0.9pt,
    left=3.5mm, right=3.5mm, top=3mm, bottom=3mm
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}

\begin{document}
"""

TEMPLATE_FOOTER = r"""
\end{document}
"""

def compile_and_compare_page(page_num):
    page_tex = os.path.join(PAGES_DIR, f"page_{page_num:04d}.tex")
    if not os.path.exists(page_tex):
        return page_num, "FILE_NOT_FOUND", 0

    with open(page_tex, "r", encoding="utf-8") as f:
        body = f.read()

    # Wrap in template
    test_tex = os.path.join(CH01_DIR, f"temp_p{page_num:04d}.tex")
    with open(test_tex, "w", encoding="utf-8") as f:
        f.write(TEMPLATE_HEADER + "\n" + body + "\n" + TEMPLATE_FOOTER)

    # Run XeLaTeX in CH01_DIR where images/ is directly accessible
    cmd = [XELATEX_EXE, "-interaction=nonstopmode", f"temp_p{page_num:04d}.tex"]
    res = subprocess.run(cmd, cwd=CH01_DIR, capture_output=True, text=True)

    test_pdf = os.path.join(CH01_DIR, f"temp_p{page_num:04d}.pdf")
    if not os.path.exists(test_pdf):
        # Read log to see error
        test_log = os.path.join(CH01_DIR, f"temp_p{page_num:04d}.log")
        err_snippet = ""
        if os.path.exists(test_log):
            with open(test_log, "r", encoding="utf-8", errors="ignore") as lf:
                err_lines = [l.strip() for l in lf if l.startswith("!") or "Error" in l]
                err_snippet = "; ".join(err_lines[:2])
        return page_num, f"COMPILE_FAIL: {err_snippet}", 0

    c_doc = fitz.open(test_pdf)
    page_count = len(c_doc)
    c_page = c_doc[0]
    c_pix = c_page.get_pixmap(dpi=150)
    c_doc.close()

    # Original page
    o_doc = fitz.open(PDF_PATH)
    o_page = o_doc[page_num - 1]
    o_pix = o_page.get_pixmap(dpi=150)
    o_doc.close()

    # Compare image
    im_orig = Image.frombytes("RGB", [o_pix.width, o_pix.height], o_pix.samples)
    im_comp = Image.frombytes("RGB", [c_pix.width, c_pix.height], c_pix.samples)

    target_h = max(im_orig.height, im_comp.height)
    target_w_orig = int(im_orig.width * (target_h / im_orig.height))
    target_w_comp = int(im_comp.width * (target_h / im_comp.height))

    im_orig_resized = im_orig.resize((target_w_orig, target_h), Image.Resampling.LANCZOS)
    im_comp_resized = im_comp.resize((target_w_comp, target_h), Image.Resampling.LANCZOS)

    comp_im = Image.new("RGB", (target_w_orig + target_w_comp + 10, target_h), (200, 200, 200))
    comp_im.paste(im_orig_resized, (0, 0))
    comp_im.paste(im_comp_resized, (target_w_orig + 10, 0))

    comp_path = os.path.join(COMPS_DIR, f"compare_p{page_num:04d}.png")
    comp_im.save(comp_path)

    # Clean temp files
    for ext in [".aux", ".log", ".tex"]:
        tmp_f = os.path.join(CH01_DIR, f"temp_p{page_num:04d}{ext}")
        if os.path.exists(tmp_f):
            try:
                os.remove(tmp_f)
            except Exception:
                pass

    status = "OK" if page_count == 1 else "OVERFLOW"
    return page_num, status, page_count

def main():
    print("=== KIỂM THỬ BIÊN DỊCH VÀ XUẤT ẢNH SO SÁNH 24 TRANG (P70-P93) ===")
    for p in range(70, 94):
        p_num, status, pages = compile_and_compare_page(p)
        sym = "✓" if status == "OK" else ("⚠" if status == "OVERFLOW" else "✗")
        print(f"Trang {p_num:04d}: {sym} {status} (Số trang: {pages})")

if __name__ == "__main__":
    main()
