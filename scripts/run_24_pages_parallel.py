import os
import sys
import json
import time
import base64
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import fitz
from PIL import Image, ImageChops

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PDF_PATH = r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf"
API_ENDPOINT = "http://127.0.0.1:8045/v1/chat/completions"
API_KEY = "sk-antigravity"
MODEL = "gemini-3.8-flash-high"
XELATEX_EXE = r"C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe"

CH01_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01"
PAGES_DIR = os.path.join(CH01_DIR, "pages")
IMAGES_DIR = os.path.join(CH01_DIR, "images")
COMPS_DIR = os.path.join(CH01_DIR, "comparisons")
TESTS_DIR = os.path.join(CH01_DIR, "tests")

os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(COMPS_DIR, exist_ok=True)
os.makedirs(TESTS_DIR, exist_ok=True)

PAGE_TEMPLATE_HEADER = r"""\documentclass[10pt,oneside]{article}
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

\graphicspath{{images/}{../images/}}

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

PAGE_TEMPLATE_FOOTER = r"""
\end{document}
"""

def trim_white(im):
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        w, h = im.size
        bbox = (max(0, bbox[0]-6), max(0, bbox[1]-6), min(w, bbox[2]+6), min(h, bbox[3]+6))
        return im.crop(bbox)
    return im

def extract_page_figures(doc, page_num):
    page_idx = page_num - 1
    page = doc[page_idx]
    drawings = page.get_drawings()
    extracted_figs = []

    caption_blocks = []
    for b in page.get_text("blocks"):
        text = b[4].strip()
        m = re.match(r"^FIGURE\s*(\d+[a-z]?)", text)
        if m:
            caption_blocks.append((m.group(1), fitz.Rect(b[:4]), text))

    found_fnums = set()
    for fnum, cap_rect, cap_text in caption_blocks:
        found_fnums.add(fnum)
        fig_drawings = []
        for d in drawings:
            dr = d["rect"]
            if dr.y1 <= cap_rect.y1 + 10 and dr.y0 >= cap_rect.y0 - 280:
                if abs(dr.x0 - cap_rect.x0) < 220 or abs(dr.x1 - cap_rect.x1) < 220:
                    fig_drawings.append(dr)
        
        if fig_drawings:
            u = fitz.Rect(fig_drawings[0])
            for dr in fig_drawings[1:]:
                u |= dr
            u.y1 = min(u.y1, cap_rect.y0 - 2)
            if u.width > 20 and u.height > 20:
                pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0), clip=u)
                im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                im = trim_white(im)
                fn = f"p{page_num:04d}_fig{fnum}.png"
                im.save(os.path.join(IMAGES_DIR, fn))
                pos_desc = "Cột lề trái" if cap_rect.x0 < 200 else "Cột chính bên phải"
                extracted_figs.append({
                    "filename": fn,
                    "type": f"HÌNH {fnum}",
                    "caption": cap_text.splitlines()[0],
                    "position": pos_desc,
                    "y_coord": round(cap_rect.y0, 1),
                    "width_pt": round(u.width, 1),
                    "height_pt": round(u.height, 1)
                })

    for img_idx, img_info in enumerate(page.get_images()):
        xref = img_info[0]
        for rect in page.get_image_rects(xref):
            if rect.width > 30 and rect.height > 30:
                pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0), clip=rect)
                fn = f"p{page_num:04d}_raster_{img_idx+1}.png"
                pix.save(os.path.join(IMAGES_DIR, fn))
                pos_desc = "Cột lề trái" if rect.x0 < 200 else "Cột chính bên phải"
                extracted_figs.append({
                    "filename": fn,
                    "type": f"Hình đồ họa {img_idx+1}",
                    "caption": "",
                    "position": pos_desc,
                    "y_coord": round(rect.y0, 1),
                    "width_pt": round(rect.width, 1),
                    "height_pt": round(rect.height, 1)
                })

    if not extracted_figs and len(drawings) > 10:
        rects = [d["rect"] for d in drawings if d["rect"].width > 15 and d["rect"].height > 15]
        clusters = []
        for r in rects:
            merged = False
            for c in clusters:
                if (fitz.Rect(c.x0-18, c.y0-18, c.x1+18, c.y1+18)).intersects(r):
                    c |= r
                    merged = True
                    break
            if not merged:
                clusters.append(fitz.Rect(r))
        
        clust_idx = 1
        for c in clusters:
            if c.width > 28 and c.height > 25 and c.width < 500 and c.height < 600:
                pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0), clip=c)
                im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                im = trim_white(im)
                fn = f"p{page_num:04d}_graph_{clust_idx}.png"
                im.save(os.path.join(IMAGES_DIR, fn))
                col_desc = "Cột trái (Bài tập)" if c.x0 < 300 else "Cột phải (Bài tập)"
                extracted_figs.append({
                    "filename": fn,
                    "type": f"Đồ thị Bài tập {clust_idx}",
                    "caption": "",
                    "position": col_desc,
                    "y_coord": round(c.y0, 1),
                    "width_pt": round(c.width, 1),
                    "height_pt": round(c.height, 1)
                })
                clust_idx += 1

    return extracted_figs

def build_refined_prompt(page_num, extracted_figs, is_exercise_page):
    figs_text = ""
    if extracted_figs:
        figs_text = "DANH SÁCH FILE ĐỒ THỊ/HÌNH ẢNH ĐÃ CROP SẴN (CHÈN ĐÚNG FILE VÀO VỊ TRÍ):\n"
        for f in extracted_figs:
            figs_text += f"- `images/{f['filename']}`: {f['type']} | Vị trí: {f['position']} (y ≈ {f['y_coord']}pt)\n"
    else:
        figs_text = "Trang này không có file hình rời.\n"

    if is_exercise_page:
        structure_guide = r"""
BỐ CỤC BÀI TẬP:
- Dùng môi trường 2 cột:
\begin{multicols}{2}
\fontsize{8.5pt}{10.8pt}\selectfont
\setlength{\abovedisplayskip}{2pt}
\setlength{\belowdisplayskip}{2pt}
% Liệt kê các bài tập theo thứ tự, chèn đồ thị tương ứng:
% \includegraphics[width=0.88\linewidth]{images/...}
\end{multicols}
- BẮT BUỘC đóng đủ \end{multicols}.
"""
    else:
        structure_guide = r"""
BỐ CỤC LÝ THUYẾT:
- Dùng cấu trúc 2 cột (cột lề phụ bên trái + cột chính bên phải):
\fancyhead[LE]{\fontsize{8.5pt}{10pt}\selectfont\textbf{\textsf{\thepage}}\quad \textbf{\textsf{CHƯƠNG 1}}\quad \textsf{Các hàm số và Mô hình}}
\fancyhead[RO]{\fontsize{8.5pt}{10pt}\selectfont\textsf{MỤC 1.1}\quad \textbf{\textsf{\thepage}}}

\noindent
\begin{minipage}[t]{0.265\textwidth}
    \fontsize{8pt}{10pt}\selectfont
    % Cột lề: chèn hình lề \includegraphics[width=0.92\linewidth]{images/...}
    % Căn chỉnh vspace phù hợp để ngang hàng với nội dung chính bên phải.
\end{minipage}%
\hfill
\begin{minipage}[t]{0.708\textwidth}
    \fontsize{9.3pt}{13.2pt}\selectfont
    % Cột chính: văn bản lý thuyết, VÍ DỤ X, LỜI GIẢI, định nghĩa
\end{minipage}
- BẮT BUỘC đóng đủ cả hai môi trường \end{minipage}.
"""

    prompt = f"""Bạn là một chuyên gia số hóa tài liệu toán học và giảng viên đại học.
Nhiệm vụ: Chuyển đổi và số hóa trang bài giảng toán giải tích (Trang {page_num}) trong ảnh đính kèm thành mã nguồn LaTeX tiếng Việt chuẩn sư phạm.

{figs_text}

QUY TẮC BẮT BUỘC:
1. ĐÚNG ĐỒ THỊ VÀ HÌNH ẢNH:
- Đặt đúng mọi hình ảnh/đồ thị đã crop ở trên vào đúng vị trí tương ứng.
- Cột lề: `\\includegraphics[width=0.92\\linewidth]{{images/filename}}`.
- Cột chính: `\\includegraphics[width=0.48\\linewidth]{{images/filename}}` (nếu song song) hoặc `0.85\\linewidth`.

2. ĐÚNG NỘI DUNG VÀ CÔNG THỨC TOÁN:
- Dịch toàn bộ văn bản sang tiếng Việt chuẩn sư phạm giải tích đại học.
- Giữ nguyên 100% tất cả các công thức toán, ký hiệu, số liệu, bảng biểu.
- "VÍ DỤ X" -> `\\textbf{{\\textsf{{\\color{{stewartcyan}}VÍ DỤ X}}}}`
- "LỜI GIẢI" -> `\\textbf{{\\textsf{{\\color{{stewartcyan}}LỜI GIẢI}}}}`
- "HÌNH X" -> `\\textbf{{\\textsf{{HÌNH X}}}}`
- Khung định nghĩa: `\\begin{{definitionbox}} ... \\end{{definitionbox}}`
- Kết thúc lời giải: `\\hfill{{\\color{{stewartcyan}}$\\blacksquare$}}`

3. TIÊU ĐỀ ĐẦU TRANG:
- Dùng \\fancyhead đơn giản, bỏ qua các vạch màu xanh phức tạp ở đầu trang.

{structure_guide}

4. ĐỊNH DẠNG ĐẦU RA:
- BẮT BUỘC đóng đủ tất cả các môi trường mở (minipage, multicols, center, definitionbox).
- Chỉ trả về nội dung thân mã LaTeX (bắt đầu từ \\fancyhead hoặc \\noindent), không bọc trong ```latex ... ```.
"""
    return prompt

def call_vision_api(prompt, b64_img):
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
                ]
            }
        ],
        "max_tokens": 8192,
        "temperature": 0.1
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(3):
        try:
            res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=120)
            if res.status_code == 200:
                raw = res.json()["choices"][0]["message"]["content"].strip()
                if raw.startswith("```latex"):
                    raw = raw[8:]
                elif raw.startswith("```"):
                    raw = raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                return raw.strip()
            elif res.status_code == 429:
                time.sleep((attempt + 1) * 5)
            else:
                time.sleep(2)
        except Exception:
            time.sleep(2)
    return None

def compile_and_compare(page_num, tex_body):
    test_tex_path = os.path.join(CH01_DIR, f"temp_p{page_num:04d}.tex")
    full_tex = PAGE_TEMPLATE_HEADER + "\n" + tex_body + "\n" + PAGE_TEMPLATE_FOOTER
    with open(test_tex_path, "w", encoding="utf-8") as f:
        f.write(full_tex)

    cmd = [XELATEX_EXE, "-interaction=nonstopmode", f"temp_p{page_num:04d}.tex"]
    res = subprocess.run(cmd, cwd=CH01_DIR, capture_output=True, text=True)

    test_pdf_path = os.path.join(CH01_DIR, f"temp_p{page_num:04d}.pdf")
    page_count = 0
    compiled_ok = os.path.exists(test_pdf_path)

    if compiled_ok:
        try:
            c_doc = fitz.open(test_pdf_path)
            page_count = len(c_doc)
            c_page = c_doc[0]
            c_pix = c_page.get_pixmap(dpi=150)
            c_doc.close()

            o_doc = fitz.open(PDF_PATH)
            o_page = o_doc[page_num - 1]
            o_pix = o_page.get_pixmap(dpi=150)
            o_doc.close()

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
        except Exception as e:
            print(f"Error making comparison for P{page_num}: {e}")

        for ext in [".aux", ".log", ".tex", ".pdf"]:
            tmp_f = os.path.join(CH01_DIR, f"temp_p{page_num:04d}{ext}")
            if os.path.exists(tmp_f):
                try:
                    os.remove(tmp_f)
                except Exception:
                    pass

    return compiled_ok, page_count

def process_page_worker(page_num):
    print(f"[*] Đang xử lý Trang {page_num}...")
    doc = fitz.open(PDF_PATH)
    page_idx = page_num - 1
    page = doc[page_idx]
    
    page_text = page.get_text()
    is_exercise = ("EXERCISES" in page_text) or ("BÀI TẬP" in page_text) or (page_num in [53, 54, 55, 56, 67, 68, 69, 77, 78, 79, 80, 87, 88])

    figs = extract_page_figures(doc, page_num)
    
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    b64_img = base64.b64encode(pix.tobytes("png")).decode("utf-8")
    doc.close()

    prompt = build_refined_prompt(page_num, figs, is_exercise)
    tex_body = call_vision_api(prompt, b64_img)

    if not tex_body:
        print(f"[!] Trang {page_num}: API không phản hồi.")
        return {"page": page_num, "status": "FAIL_API", "pages": 0, "figs": len(figs)}

    # Ensure minipages are closed if accidentally omitted
    open_minis = tex_body.count(r"\begin{minipage}")
    close_minis = tex_body.count(r"\end{minipage}")
    if open_minis > close_minis:
        tex_body += "\n" + (r"\end{minipage}" * (open_minis - close_minis))

    open_multis = tex_body.count(r"\begin{multicols}")
    close_multis = tex_body.count(r"\end{multicols}")
    if open_multis > close_multis:
        tex_body += "\n" + (r"\end{multicols}" * (open_multis - close_multis))

    page_tex_path = os.path.join(PAGES_DIR, f"page_{page_num:04d}.tex")
    with open(page_tex_path, "w", encoding="utf-8") as f:
        f.write(tex_body)

    compiled_ok, page_count = compile_and_compare(page_num, tex_body)
    status = "OK" if (compiled_ok and page_count == 1) else ("OVERFLOW" if page_count > 1 else "COMPILE_ERROR")
    print(f"[+] Hoàn thành Trang {page_num}: {status} (Số trang: {page_count}, Hình ảnh: {len(figs)})")

    return {
        "page": page_num,
        "status": status,
        "pages": page_count,
        "figs": len(figs),
        "compiled": compiled_ok
    }

def main():
    target_pages = list(range(70, 94))
    print(f"=== CHẠY THỬ 24 TRANG (P70 ĐẾN P93) VỚI PROMPT V2 & 12 WORKERS ===")
    start_time = time.time()

    results = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_page = {executor.submit(process_page_worker, p): p for p in target_pages}
        for future in as_completed(future_to_page):
            p = future_to_page[future]
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                print(f"[!] Lỗi ngoại lệ tại Trang {p}: {e}")
                results.append({"page": p, "status": f"EXCEPTION: {e}", "pages": 0, "figs": 0, "compiled": False})

    results.sort(key=lambda x: x["page"])
    elapsed = time.time() - start_time

    print("\n" + "="*60)
    print(f"=== BÁO CÁO KẾT QUẢ 24 TRANG PROMPT V2 (Thời gian: {elapsed:.1f}s) ===")
    print("="*60)
    ok_count = sum(1 for r in results if r["status"] == "OK")
    overflow_count = sum(1 for r in results if r["status"] == "OVERFLOW")
    err_count = sum(1 for r in results if r["status"] in ["COMPILE_ERROR", "FAIL_API"] or "EXCEPTION" in r["status"])

    for r in results:
        status_symbol = "✓" if r["status"] == "OK" else ("⚠" if r["status"] == "OVERFLOW" else "✗")
        print(f"Trang {r['page']:04d}: {status_symbol} {r['status']:<15} | Số trang PDF: {r['pages']} | Hình đã bóc: {r['figs']}")

    print("-"*60)
    print(f"Tổng kết: Đạt chuẩn 1 trang (OK): {ok_count}/24 | Tràn trang (OVERFLOW): {overflow_count}/24 | Lỗi biên dịch: {err_count}/24")
    print("="*60)

if __name__ == "__main__":
    main()
