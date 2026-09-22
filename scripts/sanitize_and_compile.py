import os
import sys
import re
import subprocess
import glob

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PAGES_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01\pages"
CH01_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01"
XELATEX_EXE = r"C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe"

def clean_page(content):
    # Remove markdown code blocks if any
    content = re.sub(r"^```(?:latex|tex)?\s*", "", content, flags=re.MULTILINE)
    content = re.sub(r"```\s*$", "", content, flags=re.MULTILINE)

    # Remove documentclass and preamble if present
    if r"\begin{document}" in content:
        content = content.split(r"\begin{document}", 1)[1]
    if r"\end{document}" in content:
        content = content.split(r"\end{document}", 1)[0]

    # Remove any stray preamble commands
    content = re.sub(r"\\documentclass(\[.*?\])?\{.*?\}", "", content)
    content = re.sub(r"\\usepackage(\[.*?\])?\{.*?\}", "", content)
    content = re.sub(r"\\geometry\{.*?\}", "", content)
    content = re.sub(r"\\definecolor\{.*?\}\{.*?\}\{.*?\}", "", content)
    content = re.sub(r"\\setmainfont\{.*?\}", "", content)
    content = re.sub(r"\\setsansfont\{.*?\}", "", content)
    content = re.sub(r"\\pagestyle\{.*?\}", "", content)
    content = re.sub(r"\\fancyhf\{\}", "", content)
    content = re.sub(r"\\renewcommand\{\\headrulewidth\}\{.*?\}", "", content)
    content = re.sub(r"\\newtcolorbox\{.*?\}\{.*?\}", "", content, flags=re.DOTALL)

    # Replace enumerate* with enumerate
    content = content.replace(r"\begin{enumerate*}", r"\begin{enumerate}")
    content = content.replace(r"\end{enumerate*}", r"\end{enumerate}")

    # Fix tag* with blacksquare without math mode
    content = re.sub(r"\\tag\*\{\\color\{([a-zA-Z]+)\}\\blacksquare\}", r"\\tag*{{\\color{\1}$\\blacksquare$}}", content)
    content = re.sub(r"\\tag\*\{\\blacksquare\}", r"\\tag*{$\\blacksquare$}", content)

    # Fix align* inside parbox / fcolorbox
    if r"\fcolorbox" in content and r"\begin{align*}" in content:
        content = content.replace(r"\begin{align*}", r"\[\begin{aligned}")
        content = content.replace(r"\end{align*}", r"\end{aligned}\]")

    # Fix redframebox
    content = content.replace(r"\begin{redframebox}", r"\begin{definitionbox}")
    content = content.replace(r"\end{redframebox}", r"\end{definitionbox}")

    # Fix valign in includegraphics
    content = content.replace("28ptenter", "28pt")
    content = re.sub(r",\s*valign=[a-z]+", "", content)
    content = re.sub(r"\[valign=[a-z]+,", "[", content)
    content = re.sub(r"\[valign=[a-z]+\]", "", content)

    # Fix page 75 extra brace
    content = content.replace(r"Các hàm số và Mô hình}}}", r"Các hàm số và Mô hình}}")

    return content.strip()

def main():
    files = sorted(glob.glob(os.path.join(PAGES_DIR, "page_*.tex")))
    print(f"Tìm thấy {len(files)} file trang.")

    cleaned_count = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            orig = fp.read()
        cleaned = clean_page(orig)
        if cleaned != orig:
            cleaned_count += 1
            with open(f, "w", encoding="utf-8") as fp:
                fp.write(cleaned)

    print(f"Đã chuẩn hóa và làm sạch {cleaned_count} file trang.")

    # Generate master tex
    master_tex_file = os.path.join(CH01_DIR, "chapter_01.tex")
    includes = []
    for f in files:
        rel_path = "pages/" + os.path.basename(f)
        includes.append(f"\\input{{{rel_path}}}\n\\newpage\n")

    header = r"""\documentclass[10pt,letterpaper]{article}
\usepackage{fontspec}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tcolorbox}
\tcbuselibrary{skins}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{colortbl}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage[shortlabels,inline]{enumitem}
\usepackage{tabularx}
\usepackage{array}
\usepackage{multicol}
\usepackage{tikz}

\setmainfont{Times New Roman}
\setsansfont{Arial}

\geometry{
    letterpaper,
    top=1.2cm,
    bottom=1.2cm,
    left=1.2cm,
    right=1.2cm,
    headheight=14pt,
    headsep=0.4cm,
    footskip=0.4cm
}

\definecolor{stewartcyan}{RGB}{0, 118, 186}
\definecolor{stewartred}{RGB}{218, 41, 28}
\definecolor{stewarttableheader}{RGB}{210, 224, 238}
\definecolor{stewarttablehead}{RGB}{210, 224, 238}
\definecolor{tableblue}{RGB}{210, 224, 238}
\definecolor{stewartlightblue}{RGB}{235, 243, 250}
\definecolor{stewartblue}{RGB}{0, 118, 186}
\definecolor{stewartgray}{RGB}{120, 120, 120}
\definecolor{stewartlightgray}{RGB}{240, 240, 240}
\definecolor{stewartpurple}{RGB}{85, 30, 95}
\definecolor{stewartpurplebg}{RGB}{243, 238, 245}
\definecolor{stewartpurpletext}{RGB}{85, 30, 95}
\definecolor{darkgray}{RGB}{40, 40, 40}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}

\providecommand{\makecell}[2][c]{\begin{tabular}[#1]{@{}c@{}}#2\end{tabular}}
\providecommand{\faDesktop}{\textbf{[Máy tính]}}
\providecommand{\casicon}{\textbf{\textsf{[CAS]}}}
\providecommand{\ticon}{\textbf{\textsf{[T]}}}
\providecommand{\captionof}[2]{\par\vspace{2pt}{\small\textbf{#1}: #2}\par}
\NewDocumentEnvironment{tasks}{o d()}{\begin{enumerate}}{\end{enumerate}}
\providecommand{\task}{\item}
\newenvironment{redframebox}{\begin{definitionbox}}{\end{definitionbox}}

\newtcolorbox{definitionbox}{
    colback=white,
    colframe=stewartred,
    arc=0mm,
    boxrule=0.9pt,
    left=3.5mm, right=3.5mm, top=3mm, bottom=3mm
}

\begin{document}
"""
    footer = r"\end{document}"

    with open(master_tex_file, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(includes) + footer)

    print(f"Đã tạo {master_tex_file} với {len(includes)} trang.")
    print("Bắt đầu biên dịch XeLaTeX...")

    res = subprocess.run([XELATEX_EXE, "-interaction=nonstopmode", "chapter_01.tex"], cwd=CH01_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"XeLaTeX return code: {res.returncode}")
    if res.returncode == 0:
        print("✓ BIÊN DỊCH THÀNH CÔNG RỰC RỠ!")
    else:
        print("Gặp lỗi khi biên dịch, kiểm tra log:")
        with open(os.path.join(CH01_DIR, "chapter_01.log"), "r", encoding="utf-8", errors="replace") as lf:
            lines = lf.readlines()
            err_lines = [l for l in lines if l.startswith("!") or "Error" in l or "Fatal" in l]
            for el in err_lines[:20]:
                print(el.strip())


if __name__ == "__main__":
    main()
