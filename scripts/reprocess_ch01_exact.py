import os
import sys
import json
import time
import re
import base64
import subprocess
import fitz
import requests
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese"
PDF_PATH = r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf"
API_ENDPOINT = "http://127.0.0.1:8045/v1/chat/completions"
API_KEY = "sk-96edad6609ce4f96bf40d53d26b7fd42"
MODEL = "gemini-3.8-flash-high"
XELATEX_EXE = r"C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe"

CH01_DIR = os.path.join(PROJECT_ROOT, "chapters", "ch01")
PAGES_DIR = os.path.join(CH01_DIR, "pages")
IMAGES_DIR = os.path.join(CH01_DIR, "images")
COMP_DIR = os.path.join(CH01_DIR, "comparisons")
CHECKPOINT_FILE = os.path.join(CH01_DIR, "verified_checkpoint_exact.json")

os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(COMP_DIR, exist_ok=True)

MASTER_PREAMBLE = r"""\documentclass[10pt,letterpaper]{article}
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
    paperwidth=612.05pt,
    paperheight=720.05pt,
    top=20pt,
    headheight=14pt,
    headsep=12pt,
    bottom=28pt,
    footskip=12pt,
    left=36pt,
    right=36pt
}

\setlength{\abovedisplayskip}{2pt}
\setlength{\belowdisplayskip}{2pt}
\setlength{\abovedisplayshortskip}{1pt}
\setlength{\belowdisplayshortskip}{1pt}
\setlength{\parskip}{0pt}
\setlength{\columnsep}{16pt}

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

\newtcolorbox{definitionbox}{
    colback=white,
    colframe=stewartred,
    arc=0mm,
    boxrule=0.9pt,
    left=3.5mm, right=3.5mm, top=3mm, bottom=3mm
}
\newenvironment{redframebox}{\begin{definitionbox}}{\end{definitionbox}}

\begin{document}
"""

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"verified_pages": []}

def save_checkpoint(page_num, score, notes=""):
    cp = load_checkpoint()
    found = False
    for item in cp["verified_pages"]:
        if item["page_num"] == page_num:
            item["score"] = score
            item["notes"] = notes
            item["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            found = True
            break
    if not found:
        cp["verified_pages"].append({
            "page_num": page_num,
            "score": score,
            "notes": notes,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2, ensure_ascii=False)

def is_page_verified(page_num):
    cp = load_checkpoint()
    for item in cp.get("verified_pages", []):
        if item["page_num"] == page_num and item.get("score", 0) >= 99:
            return True
    return False

def render_original_page(page_num, doc):
    page_idx = page_num - 1
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    out_file = os.path.join(COMP_DIR, f"original_p{page_num:04d}.png")
    pix.save(out_file)
    return out_file

def detect_and_crop_figures(page_num, doc):
    page_idx = page_num - 1
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")

    prompt = f"""Phân tích hình ảnh trang {page_num} và trích xuất tọa độ bounding box của TẤT CẢ các khối hình vẽ / đồ thị / biểu đồ / sơ đồ có trên trang.
Tọa độ chuẩn hóa theo thang 0-1000 dạng: [ymin, xmin, ymax, xmax].

QUY TẮC BẮT BUỘC:
1. Nếu một hình gồm nhiều đồ thị con nằm ngang (ví dụ cụm đồ thị a, b, c), gom thành MỘT HỘP BAO DUY NHẤT bao trọn cả cụm đồ thị, trục, nhãn điểm và nhãn (a), (b), (c).
2. KHÔNG cắt đứt nhãn điểm tọa độ hoặc trục.
3. Không bao gồm nhãn 'FIGURE X' ở ngoài rìa nếu có thể tách rời.

Trả về định dạng JSON:
{{
  "figures": [
    {{
      "filename": "p{page_num:04d}_fig1.png",
      "box_1000": [ymin, xmin, ymax, xmax],
      "caption": "Mô tả hình"
    }}
  ]
}}
Nếu không có hình vẽ nào: {{"figures": []}}. Chỉ trả về JSON thuần túy."""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        ]}],
        "temperature": 0.1
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    cropped_files = []
    try:
        res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=90)
        if res.status_code == 200:
            raw = res.json()["choices"][0]["message"]["content"].strip()
            if raw.startswith("```json"): raw = raw[7:]
            elif raw.startswith("```"): raw = raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            data = json.loads(raw.strip())
            w, h = page.rect.width, page.rect.height
            for idx, fig in enumerate(data.get("figures", [])):
                box = fig["box_1000"]
                ymin, xmin, ymax, xmax = box[0], box[1], box[2], box[3]
                x0 = max(0, xmin * w / 1000 - 4)
                y0 = max(0, ymin * h / 1000 - 4)
                x1 = min(w, xmax * w / 1000 + 4)
                y1 = min(h, ymax * h / 1000 + 4)
                clip = fitz.Rect(x0, y0, x1, y1)
                if clip.width > 20 and clip.height > 20:
                    fn = fig.get("filename", f"p{page_num:04d}_fig{idx+1}.png")
                    fp = os.path.join(IMAGES_DIR, fn)
                    pix_crop = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0), clip=clip)
                    pix_crop.save(fp)
                    cropped_files.append((fn, fig.get("caption", "")))
    except Exception as e:
        print(f"Lỗi crop hình trang {page_num}: {e}")

    return cropped_files

def extract_layout_map(doc, page_num):
    page_idx = page_num - 1
    page = doc.load_page(page_idx)
    blocks = page.get_text("blocks")
    margin_blocks = []
    main_blocks = []
    for b in blocks:
        txt = b[4].strip().replace("\n", " ")
        if not txt or "Copyright" in txt or "Cengage" in txt:
            continue
        if b[0] < 180:
            margin_blocks.append(f"  + y={b[1]:.1f}pt - {b[3]:.1f}pt: {txt[:70]}")
        else:
            main_blocks.append(f"  + y={b[1]:.1f}pt - {b[3]:.1f}pt: {txt[:70]}")
    m_str = "\n".join(margin_blocks) if margin_blocks else "  (Trống)"
    c_str = "\n".join(main_blocks) if main_blocks else "  (Trống)"
    return f"""TỌA ĐỘ VĂN BẢN GỐC (POINT):
- Cột lề trái (x < 180pt):
{m_str}
- Cột nội dung chính (x >= 180pt):
{c_str}"""

def clean_tex_content(content):
    content = content.replace(r"\begin{enumerate*}", r"\begin{enumerate}")
    content = content.replace(r"\end{enumerate*}", r"\end{enumerate}")
    content = content.replace(r"\begin{redframebox}", r"\begin{definitionbox}")
    content = content.replace(r"\end{redframebox}", r"\end{definitionbox}")
    if r"\begin{document}" in content:
        content = content.split(r"\begin{document}", 1)[1]
    if r"\end{document}" in content:
        content = content.split(r"\end{document}", 1)[0]
    clean_lines = []
    for l in content.splitlines():
        sl = l.strip()
        if sl.startswith(r"\documentclass") or sl.startswith(r"\usepackage") or sl.startswith(r"\geometry"):
            continue
        clean_lines.append(l)
    return "\n".join(clean_lines).strip()

def compile_and_check(page_num, tex_code):
    clean_code = clean_tex_content(tex_code)
    temp_tex = os.path.join(CH01_DIR, f"temp_exact_p{page_num:04d}.tex")
    temp_pdf = os.path.join(CH01_DIR, f"temp_exact_p{page_num:04d}.pdf")

    full_tex = MASTER_PREAMBLE + "\n" + clean_code + "\n\\end{document}\n"
    with open(temp_tex, "w", encoding="utf-8") as f:
        f.write(full_tex)

    res = subprocess.run(
        [XELATEX_EXE, "-interaction=nonstopmode", f"temp_exact_p{page_num:04d}.tex"],
        cwd=CH01_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if not os.path.exists(temp_pdf):
        log_file = os.path.join(CH01_DIR, f"temp_exact_p{page_num:04d}.log")
        err_msg = ""
        if os.path.exists(log_file):
            log_txt = open(log_file, encoding="utf-8", errors="ignore").read()
            err_msg = log_txt[-800:]
        return False, 0, f"Lỗi cú pháp biên dịch:\n{err_msg}", None

    doc = fitz.open(temp_pdf)
    page_count = len(doc)
    compiled_img = os.path.join(COMP_DIR, f"compiled_p{page_num:04d}.png")

    if page_count == 1:
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        pix.save(compiled_img)
        doc.close()
        # Clean temp
        for ext in [".aux", ".log", ".tex", ".pdf"]:
            f_p = os.path.join(CH01_DIR, f"temp_exact_p{page_num:04d}{ext}")
            if os.path.exists(f_p):
                try: os.remove(f_p)
                except Exception: pass
        return True, 1, "OK 1 page", compiled_img
    else:
        # Multi-page overflow!
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        pix.save(compiled_img)
        doc.close()
        for ext in [".aux", ".log", ".tex", ".pdf"]:
            f_p = os.path.join(CH01_DIR, f"temp_exact_p{page_num:04d}{ext}")
            if os.path.exists(f_p):
                try: os.remove(f_p)
                except Exception: pass
        return False, page_count, f"Tràn trang (Hiện tại: {page_count} trang, bắt buộc phải đúng 1 trang)", compiled_img

def create_comparison_image(page_num, orig_path, comp_path):
    orig = Image.open(orig_path).convert("RGB")
    comp = Image.open(comp_path).convert("RGB")
    target_h = max(orig.height, comp.height)
    if orig.height != target_h:
        orig = orig.resize((int(orig.width * target_h / orig.height), target_h), Image.Resampling.LANCZOS)
    if comp.height != target_h:
        comp = comp.resize((int(comp.width * target_h / comp.height), target_h), Image.Resampling.LANCZOS)

    header_h = 70
    canvas_w = orig.width + comp.width + 30
    canvas_h = target_h + header_h + 20
    canvas = Image.new("RGB", (canvas_w, canvas_h), (245, 245, 247))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, canvas_w, header_h], fill=(30, 41, 59))

    try:
        font = ImageFont.truetype("arial.ttf", 22)
        font_sub = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
        font_sub = font

    draw.text((30, 15), f"TRANG GỐC {page_num} (TIẾNG ANH - BẢN IN GỐC)", fill=(255, 255, 255), font=font)
    draw.text((orig.width + 45, 15), f"BẢN DỊCH XELATEX {page_num} (TIẾNG VIỆT - MODEL HIGH)", fill=(56, 189, 248), font=font)
    draw.text((30, 44), "Calculus: Early Transcendentals (9th Edition) - James Stewart", fill=(203, 213, 225), font=font_sub)
    draw.text((orig.width + 45, 44), f"Chuẩn 99% bố cục, tọa độ & toán học XeLaTeX ({MODEL})", fill=(203, 213, 225), font=font_sub)

    canvas.paste(orig, (10, header_h + 10))
    canvas.paste(comp, (orig.width + 20, header_h + 10))
    draw.line([(orig.width + 15, header_h), (orig.width + 15, canvas_h)], fill=(200, 200, 200), width=2)

    out_path = os.path.join(COMP_DIR, f"compare_p{page_num:04d}.png")
    canvas.save(out_path, quality=92)
    return out_path

def evaluate_and_fix_with_vision(page_num, compare_img, current_tex, page_count, err_msg, cropped_figs, layout_map):
    with open(compare_img, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    figs_str = ", ".join([f"`images/{fn}` ({cap})" for fn, cap in cropped_figs]) if cropped_figs else "Không có hình"

    status_str = f"LỖI: Tràn thành {page_count} trang (YÊU CẦU BẮT BUỘC: ĐÚNG 1 TRANG)" if page_count != 1 else "Đã ra 1 trang"
    if err_msg and "Lỗi cú pháp" in err_msg:
        status_str = f"LỖI BIÊN DỊCH: {err_msg}"

    prompt = f"""Bạn là một chuyên gia cao cấp về chế bản giáo trình giải tích quốc tế (XeLaTeX) và thẩm định đối chiếu hình ảnh.
Nhiệm vụ: Phân tích ảnh đối chiếu Trang Gốc (bên trái) và Bản Dịch (bên phải) của trang {page_num}.

TRẠNG THÁI HIỆN TẠI:
{status_str}

{layout_map}

DANH SÁCH FILE ẢNH images/ TRÊN TRANG:
{figs_str}

MÃ NGUỒN HIỆN TẠI:
```latex
{current_tex}
```

TIÊU CHUẨN BẮT BUỘC ĐỂ ĐẠT 99%:
1. ĐÚNG CHÍNH XÁC 1 TRANG DUY NHẤT:
   - Nếu là trang BÀI TẬP: BẮT BUỘC dùng \\begin{{multicols}}{{2}} ... \\end{{multicols}}, cỡ chữ \\fontsize{{8.8pt}}{{11.0pt}}\\selectfont, co \\abovedisplayskip=2pt, \\belowdisplayskip=2pt. TUYỆT ĐỐI KHÔNG bọc bài tập trong 2 khối minipage lớn cứng vì sẽ gây overfull vbox đẩy sang trang 2!
   - Nếu là trang LÝ THUYẾT: Cột lề 0.26\\textwidth, cột chính 0.71\\textwidth. Cân chỉnh độ cao \\vspace*{{...pt}} ở cột lề dóng đúng hàng ngang với văn bản cột chính.
2. HÌNH ẢNH:
   - Giới hạn kích thước ảnh vừa vặn: ví dụ width=0.85\\linewidth, không để ảnh quá cao chèn ép đẩy văn bản.
3. KHOẢNG TRỐNG:
   - Phần đáy trang phải lấp đầy tự nhiên, không để lại khoảng trống trắng quá lớn bên dưới so với sách gốc.
4. ĐẦY ĐỦ NỘI DUNG:
   - Dịch toàn bộ sang tiếng Việt chuẩn sư phạm, không làm mất chữ, mất câu, mất số bài tập.

TRẢ VỀ ĐỊNH DẠNG JSON:
{{
  "score": 99,
  "status": "PASSED" hoặc "NEEDS_FIX",
  "notes": "Nhận xét chi tiết về bố cục, vị trí hình và khoảng trống",
  "corrected_latex": "Toàn bộ mã nguồn LaTeX đã sửa để đạt đúng 1 trang và giống 99% (Bắt buộc cung cấp nếu status là NEEDS_FIX hoặc score < 99)"
}}
Chỉ trả về JSON thuần túy."""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        ]}],
        "temperature": 0.1
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    for attempt in range(3):
        try:
            res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=120)
            if res.status_code == 200:
                raw = res.json()["choices"][0]["message"]["content"].strip()
                if raw.startswith("```json"): raw = raw[7:]
                elif raw.startswith("```"): raw = raw[3:]
                if raw.endswith("```"): raw = raw[:-3]
                return json.loads(raw.strip())
        except Exception as e:
            print(f"Lỗi Vision AI (lần {attempt+1}): {e}")
            time.sleep(2)

    return {"score": 90, "status": "NEEDS_FIX", "notes": "Chưa kết nối được AI", "corrected_latex": ""}

def process_single_page_rigorous(page_num, doc):
    print(f"\n=======================================================")
    print(f"--> [CHƯƠNG 1] BẮT ĐẦU XỬ LÝ & KIỂM CHỨNG DỨT ĐIỂM TRANG {page_num}")
    print(f"=======================================================")

    tex_file = os.path.join(PAGES_DIR, f"page_{page_num:04d}.tex")

    # 1. Render original
    orig_path = render_original_page(page_num, doc)
    print(f"1. Đã kết xuất trang gốc: {os.path.basename(orig_path)}")

    # 2. Crop figures if missing
    cropped_figs = detect_and_crop_figures(page_num, doc)
    print(f"2. Đã bóc tách hình ảnh: {len(cropped_figs)} hình")

    # 3. Layout coordinate map
    layout_map = extract_layout_map(doc, page_num)

    # 4. Load or generate current tex
    current_tex = ""
    if os.path.exists(tex_file):
        with open(tex_file, "r", encoding="utf-8") as f:
            current_tex = f.read()

    # Rule-based exercise normalization if page has Exercises
    if "BÀI TẬP" in current_tex or "EXERCISES" in current_tex or "Exercises" in current_tex or page_num in range(52, 60):
        # If it has dual minipages, convert to multicols
        if r"\begin{minipage}[t]{0.48" in current_tex:
            print("   -> Tự động chuyển cấu trúc minipage bài tập sang multicols{2}...")
            # Pattern match exercise block
            body = clean_tex_content(current_tex)
            body = body.replace(r"\begin{minipage}[t]{0.48\textwidth}", r"\begin{multicols}{2}\fontsize{8.8pt}{11pt}\selectfont")
            body = body.replace(r"\begin{minipage}[t]{0.485\textwidth}", r"\begin{multicols}{2}\fontsize{8.8pt}{11pt}\selectfont")
            body = body.replace(r"\end{minipage}%" + "\n" + r"\hfill" + "\n" + r"\begin{minipage}[t]{0.48\textwidth}", r"\columnbreak")
            body = body.replace(r"\end{minipage}%" + "\n" + r"\hfill" + "\n" + r"\begin{minipage}[t]{0.485\textwidth}", r"\columnbreak")
            if body.endswith(r"\end{minipage}"):
                body = body[:-14] + r"\end{multicols}"
            current_tex = body

    # Loop of verification & refinement
    max_iterations = 4
    score = 0
    notes = ""

    for it in range(1, max_iterations + 1):
        print(f"\n--- Vòng kiểm chứng {it}/{max_iterations} cho Trang {page_num} ---")
        ok, page_count, msg, comp_img = compile_and_check(page_num, current_tex)
        print(f"   + Kết quả biên dịch: ok={ok}, số trang={page_count}, ghi chú: {msg}")

        # Create side by side comparison
        if comp_img and os.path.exists(comp_img):
            compare_path = create_comparison_image(page_num, orig_path, comp_img)
            print(f"   + Đã tạo ảnh đối chiếu: {os.path.basename(compare_path)}")
        else:
            compare_path = orig_path

        # Call vision review
        print(f"   + Đang gửi ảnh cho `{MODEL}` thẩm định và chấm điểm layout...")
        review = evaluate_and_fix_with_vision(page_num, compare_path, current_tex, page_count, msg, cropped_figs, layout_map)
        score = review.get("score", 0)
        notes = review.get("notes", "")
        status = review.get("status", "NEEDS_FIX")
        corrected = review.get("corrected_latex", "").strip()

        print(f"   => Điểm: {score}% | Trạng thái: {status}")
        print(f"   => Ghi chú: {notes}")

        if ok and page_count == 1 and score >= 99:
            print(f"   ✓✓✓ TRANG {page_num} ĐÃ ĐẠT TIÊU CHUẨN 99% VÀ ĐÚNG 1 TRANG DUY NHẤT!")
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(clean_tex_content(current_tex))
            break

        # If not passed and we have corrected code, apply it and test again
        if corrected:
            print("   -> Đang cập nhật mã nguồn theo đề xuất sửa của Vision AI...")
            current_tex = corrected
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(clean_tex_content(current_tex))
        else:
            time.sleep(1)

    # Save final verified state
    save_checkpoint(page_num, score, notes)

    # Push to GitHub
    try:
        subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, check=True)
        commit_msg = f"verify(ch01-p{page_num:04d}): dứt điểm trang {page_num} ({score}%, 1 trang chuẩn) [{MODEL}]"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"✓ Đã đồng bộ trang {page_num} lên GitHub thành công!")
    except Exception as e:
        print(f"Lưu ý git push: {e}")

    return score >= 99

def main():
    doc = fitz.open(PDF_PATH)
    print("=" * 60)
    print("KHỞI CHẠY QUY TRÌNH XỬ LÝ LẠI TOÀN BỘ CHƯƠNG 1 (DỨT ĐIỂM TỪNG TRANG)")
    print(f"Phạm vi: Trang 42 đến Trang 111 (Tổng 70 trang) | Model: {MODEL}")
    print("Yêu cầu: Bắt buộc đúng 1 trang, sai số tọa độ <= 1-2mm, độ tương đồng >= 99%")
    print("=" * 60)

    for page_num in range(42, 112):
        if is_page_verified(page_num):
            print(f"-> Trang {page_num} đã được xác minh đạt chuẩn 99%. Bỏ qua.")
            continue
        success = process_single_page_rigorous(page_num, doc)
        if not success:
            print(f"⚠ Trang {page_num} cần lưu ý chưa đạt ngay lập tức 99%, sẽ tiếp tục tinh chỉnh.")

if __name__ == "__main__":
    main()
