import os
import sys
import glob
import re

CH01_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01"
PAGES_DIR = os.path.join(CH01_DIR, "pages")

overflow_pages = [77, 78, 79, 81, 82, 86, 87]

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

print(f"=== DANG TOI UU HOA KHOANG CACH CHO CAC TRANG OVERFLOW ===")

for p in overflow_pages:
    fpath = os.path.join(PAGES_DIR, f"page_{p:04d}.tex")
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Reduce large \vspace
    content = re.sub(r'\\vspace\*?\{[1-9]\d*(\.\d+)?(cm|mm|pt)\}', lambda m: f"\\vspace{{3pt}}", content)
    
    # 2. Tighten fontsize slightly if 9.5pt -> 9.0pt or 9.3pt -> 8.8pt
    content = re.sub(r'\\fontsize\{9\.[0-9]pt\}\{[0-9\.]+pt\}', r'\\fontsize{8.8pt}{11.5pt}', content)
    content = re.sub(r'\\fontsize\{10pt\}\{[0-9\.]+pt\}', r'\\fontsize{9pt}{12pt}', content)

    # 3. For exercises (multicols), ensure tight display skips and small font
    if "multicols" in content:
        if r"\setlength{\abovedisplayskip}" not in content:
            content = content.replace(r"\begin{multicols}{2}", "\\begin{multicols}{2}\n\\fontsize{8.3pt}{10.2pt}\\selectfont\n\\setlength{\\abovedisplayskip}{1.5pt}\n\\setlength{\\belowdisplayskip}{1.5pt}")
        # Tighten exercise image widths
        content = re.sub(r'\\includegraphics\[width=0\.8[5-9]\\linewidth\]', r'\\includegraphics[width=0.72\\linewidth]', content)
        content = re.sub(r'\\includegraphics\[width=0\.9[0-9]\\linewidth\]', r'\\includegraphics[width=0.75\\linewidth]', content)
    else:
        # Tighten main column images
        content = re.sub(r'\\includegraphics\[width=0\.9[0-9]\\linewidth\]', r'\\includegraphics[width=0.82\\linewidth]', content)
        content = re.sub(r'\\includegraphics\[width=0\.8[5-9]\\linewidth\]', r'\\includegraphics[width=0.78\\linewidth]', content)

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Đã tinh chỉnh khoảng cách trang {p}")

print("Hoàn tất tinh chỉnh.")
