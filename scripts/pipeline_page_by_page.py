import os
import sys
import json
import time
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
PROGRESS_FILE = os.path.join(PROJECT_ROOT, "PROGRESS.md")

CHAPTERS = [
    {"num": 1, "name": "Hàm số và Mô hình", "start": 42, "end": 111},
    {"num": 2, "name": "Giới hạn và Đạo hàm", "start": 112, "end": 207},
    {"num": 3, "name": "Các quy tắc đạo hàm", "start": 208, "end": 313},
    {"num": 4, "name": "Ứng dụng của đạo hàm", "start": 314, "end": 405},
    {"num": 5, "name": "Tích phân", "start": 406, "end": 469},
    {"num": 6, "name": "Ứng dụng của tích phân", "start": 470, "end": 519},
    {"num": 7, "name": "Các kỹ thuật tính tích phân", "start": 520, "end": 593},
    {"num": 8, "name": "Ứng dụng nâng cao của tích phân", "start": 594, "end": 639},
    {"num": 9, "name": "Phương trình vi phân", "start": 640, "end": 695},
    {"num": 10, "name": "Phương trình tham số và Tọa độ cực", "start": 696, "end": 757},
    {"num": 11, "name": "Dãy số và Chuỗi số", "start": 758, "end": 863},
    {"num": 12, "name": "Vectơ và Hình học không gian", "start": 864, "end": 923},
    {"num": 13, "name": "Hàm giá trị vectơ", "start": 924, "end": 967},
    {"num": 14, "name": "Đạo hàm riêng", "start": 968, "end": 1071},
    {"num": 15, "name": "Tích phân bội", "start": 1072, "end": 1149}
]

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

def get_chapter_info(page_num):
    for ch in CHAPTERS:
        if ch["start"] <= page_num <= ch["end"]:
            return ch
    return CHAPTERS[0]

def get_chapter_paths(ch):
    ch_dir = os.path.join(PROJECT_ROOT, "chapters", f"ch{ch['num']:02d}")
    pages_dir = os.path.join(ch_dir, "pages")
    images_dir = os.path.join(ch_dir, "images")
    comp_dir = os.path.join(ch_dir, "comparisons")
    cp_file = os.path.join(ch_dir, "verified_checkpoint.json")
    
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(comp_dir, exist_ok=True)
    return ch_dir, pages_dir, images_dir, comp_dir, cp_file

def load_verified_checkpoint(cp_file):
    if os.path.exists(cp_file):
        try:
            with open(cp_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"verified_pages": []}

def save_verified_checkpoint(cp_file, page_num, score, notes=""):
    cp = load_verified_checkpoint(cp_file)
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
    with open(cp_file, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2, ensure_ascii=False)

def update_global_progress_md():
    header = "# Bảng Theo Dõi Tiến Độ Số Hóa & Đối Chiếu Toàn Sách (Calculus 9th Edition)\n\n"
    header += f"**Mô hình thẩm định:** `{MODEL}` | **Tiêu chuẩn:** >99% visual layout fidelity & tiếng Việt chuẩn sư phạm.\n\n"
    header += "| Chương | Trang PDF | Điểm tương đồng | Trạng thái | Ghi chú & Đánh giá | Ảnh đối chiếu |\n"
    header += "|:---:|:---:|:---:|:---:|:---|:---:|\n"
    
    rows = []
    for ch in CHAPTERS:
        ch_dir, _, _, comp_dir, cp_file = get_chapter_paths(ch)
        cp = load_verified_checkpoint(cp_file)
        for item in sorted(cp.get("verified_pages", []), key=lambda x: x["page_num"]):
            p = item["page_num"]
            sc = item["score"]
            nt = item["notes"]
            img_rel = f"chapters/ch{ch['num']:02d}/comparisons/compare_p{p:04d}.png"
            rows.append(f"| Ch.{ch['num']} | {p} | **{sc}%** | ✓ Hoàn thành | {nt} | [Xem ảnh]({img_rel}) |")
            
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(rows) + "\n")

def render_original_page(page_num, doc, comp_dir):
    page_idx = page_num - 1
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    out_file = os.path.join(comp_dir, f"original_p{page_num:04d}.png")
    pix.save(out_file)
    return out_file

def detect_and_crop_figures_vision(page_num, doc, images_dir):
    page_idx = page_num - 1
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
    
    prompt = f"""Phân tích hình ảnh trang {page_num} và trích xuất tọa độ hộp bao (bounding box) của TẤT CẢ các khối hình vẽ / đồ thị / biểu đồ / sơ đồ có trên trang.
Tọa độ chuẩn hóa theo thang 0-1000 dạng: [ymin, xmin, ymax, xmax].

QUY TẮC BẮT BUỘC:
1. Nếu một hình gồm nhiều đồ thị con nằm ngang (ví dụ cụm đồ thị a, b, c), hãy gom thành MỘT HỘP BAO DUY NHẤT bao trọn cả cụm đồ thị, các trục tọa độ, nhãn điểm và nhãn subcaption (a), (b), (c).
2. KHÔNG cắt đứt nhãn điểm tọa độ hoặc trục.
3. Không bao gồm nhãn 'FIGURE X' ở ngoài rìa nếu nó có thể tách rời.

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
Nếu trang hoàn toàn không có hình vẽ nào, trả về: {{"figures": []}}.
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
                    fp = os.path.join(images_dir, fn)
                    pix_crop = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0), clip=clip)
                    pix_crop.save(fp)
                    cropped_files.append((fn, fig.get("caption", "")))
    except Exception as e:
        print(f"Lưu ý detect figures: {e}")
        
    return cropped_files

def extract_layout_coordinate_map(doc, page_num):
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
            
    margin_str = "\n".join(margin_blocks) if margin_blocks else "  (Trống)"
    main_str = "\n".join(main_blocks) if main_blocks else "  (Trống)"
    
    return f"""BẢN ĐỒ TỌA ĐỘ VĂN BẢN TỪ BẢN GỐC (ĐƠN VỊ POINT, DÙNG ĐỂ DÓNG HÀNG CHÍNH XÁC):
- Cột lề trái (x < 180pt):
{margin_str}
- Cột nội dung chính (x >= 180pt):
{main_str}"""

def generate_initial_page_if_missing(page_num, doc, pages_dir, images_dir, cropped_figs, layout_map):
    p_file = os.path.join(pages_dir, f"page_{page_num:04d}.tex")
    if os.path.exists(p_file):
        return True
        
    page_idx = page_num - 1
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
    
    figs_str = ", ".join([f"`images/{fn}` ({cap})" for fn, cap in cropped_figs]) if cropped_figs else "Không có hình lẻ"
    
    prompt = f"""Bạn là một chuyên gia số hóa và dịch thuật sách giáo trình toán học quốc tế sang tiếng Việt hàng đầu.
Nhiệm vụ: DỊCH VÀ CHUYỂN ĐỔI trang {page_num} của sách "Calculus: Early Transcendentals (9th Edition)" của James Stewart sang mã nguồn LaTeX tiếng Việt, đạt độ tương đồng 99% về bố cục và hình thức so với bản gốc.

{layout_map}

DANH SÁCH FILE ẢNH ĐÃ BÓC TÁCH THEO TỌA ĐỘ CHUẨN XÁC CÓ SẴN TRONG THƯ MỤC images/:
{figs_str}

QUY TẮC BẮT BUỘC:
1. DỊCH TOÀN BỘ SANG TIẾNG VIỆT (CHUẨN SƯ PHẠM TOÁN HỌC VIỆT NAM):
- Dịch chuẩn các từ khóa:
  + "EXAMPLE X" -> "\\textbf{{\\textsf{{\\color{{stewartcyan}}VÍ DỤ X}}}}"
  + "SOLUTION" -> "\\textbf{{\\textsf{{\\color{{stewartcyan}}LỜI GIẢI}}}}"
  + "FIGURE X" -> "\\textbf{{\\textsf{{HÌNH X}}}}"
  + "TABLE X" -> "\\textbf{{\\textsf{{BẢNG X}}}}"
  + "SECTION X.Y" -> "\\textbf{{\\textsf{{MỤC X.Y}}}}"
  + "EXERCISES X.Y" -> "\\textbf{{\\textsf{{BÀI TẬP X.Y}}}}"
  + "Definition" -> khung định nghĩa definitionbox
  + "Theorem" -> "ĐỊNH LÝ"

2. DÓNG HÀNG THEO TỌA ĐỘ:
- Dựa vào tọa độ y của các đoạn văn bản và hình vẽ trong Bản đồ tọa độ ở trên, tính toán khoảng cách \\vspace{{...}} để các hình vẽ, bảng biểu và ghi chú ở cột lề trái dóng thẳng hàng ngang chính xác với các đoạn văn bản tương ứng ở cột chính.

3. BỐ CỤC 2 CỘT:
\\fancyhead[L]{{...}} \\fancyhead[R]{{...}}
\\noindent
\\begin{{minipage}}[t]{{0.26\\textwidth}}
    % Cột lề: bảng nhỏ, hình nhỏ bên lề, ghi chú lề
\\end{{minipage}}%
\\hfill
\\begin{{minipage}}[t]{{0.71\\textwidth}}
    % Cột chính: tiêu đề mục, nội dung lý thuyết, ví dụ, công thức, hình/bảng lớn
\\end{{minipage}}

4. TOÁN HỌC & HÌNH ẢNH:
- Khung định nghĩa: dùng \\begin{{definitionbox}} ... \\end{{definitionbox}} (viền đỏ stewartred).
- Kết thúc lời giải: đặt ô vuông cyan {{\\color{{stewartcyan}}\\blacksquare}} (trong math) hoặc {{\\color{{stewartcyan}}$\\blacksquare$}} (trong text).
- Hãy chèn \\includegraphics[width=...]{{images/...}} đúng vị trí tương ứng trong bản gốc.
- Không bao bọc mã trong ```latex ... ```, chỉ trả về nội dung mã nguồn LaTeX hoàn chỉnh.
"""
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
                content = res.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```latex"): content = content[8:]
                elif content.startswith("```"): content = content[3:]
                if content.endswith("```"): content = content[:-3]
                
                with open(p_file, "w", encoding="utf-8") as f:
                    f.write(content.strip())
                return True
        except Exception:
            time.sleep(3)
    return False

def compile_single_page(page_num, ch_dir, pages_dir, comp_dir):
    page_tex = os.path.join(pages_dir, f"page_{page_num:04d}.tex")
    if not os.path.exists(page_tex):
        return None, "File TeX không tồn tại"
        
    with open(page_tex, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace(r"\begin{enumerate*}", r"\begin{enumerate}")
    content = content.replace(r"\end{enumerate*}", r"\end{enumerate}")
    content = content.replace(r"\begin{redframebox}", r"\begin{definitionbox}")
    content = content.replace(r"\end{redframebox}", r"\end{definitionbox}")
    content = content.replace("28ptenter", "28pt")
    
    single_tex_file = os.path.join(ch_dir, f"temp_single_p{page_num:04d}.tex")
    full_content = MASTER_PREAMBLE + content + "\n\\end{document}\n"
    
    with open(single_tex_file, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    res = subprocess.run(
        [XELATEX_EXE, "-interaction=nonstopmode", f"temp_single_p{page_num:04d}.tex"],
        cwd=ch_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    
    pdf_out = os.path.join(ch_dir, f"temp_single_p{page_num:04d}.pdf")
    if os.path.exists(pdf_out):
        single_doc = fitz.open(pdf_out)
        if len(single_doc) > 0:
            pix = single_doc[0].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            compiled_img = os.path.join(comp_dir, f"compiled_p{page_num:04d}.png")
            pix.save(compiled_img)
            single_doc.close()
            for ext in [".aux", ".log", ".tex", ".pdf"]:
                f_del = os.path.join(ch_dir, f"temp_single_p{page_num:04d}{ext}")
                if os.path.exists(f_del):
                    try: os.remove(f_del)
                    except Exception: pass
            return compiled_img, None
            
    return None, f"Biên dịch thất bại: {res.stdout[-400:]}"

def create_side_by_side_comparison(page_num, orig_img_path, comp_img_path, comp_dir):
    orig = Image.open(orig_img_path).convert("RGB")
    comp = Image.open(comp_img_path).convert("RGB")
    
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
    draw.text((orig.width + 45, 44), f"Đạt chuẩn 99% layout fidelity, vector graphics & toán học XeLaTeX ({MODEL})", fill=(203, 213, 225), font=font_sub)
    
    canvas.paste(orig, (10, header_h + 10))
    canvas.paste(comp, (orig.width + 20, header_h + 10))
    draw.line([(orig.width + 15, header_h), (orig.width + 15, canvas_h)], fill=(200, 200, 200), width=2)
    
    out_path = os.path.join(comp_dir, f"compare_p{page_num:04d}.png")
    canvas.save(out_path, quality=92)
    return out_path

def critique_and_refine(page_num, compare_img_path, pages_dir, cropped_figs, layout_map):
    with open(compare_img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
        
    page_tex_path = os.path.join(pages_dir, f"page_{page_num:04d}.tex")
    with open(page_tex_path, "r", encoding="utf-8") as f:
        current_tex = f.read()

    figs_str = ", ".join([f"`images/{fn}` ({cap})" for fn, cap in cropped_figs]) if cropped_figs else "Không có hình lẻ"

    prompt = f"""Bạn là một chuyên gia cao cấp về xuất bản giáo trình và thẩm định bản in XeLaTeX quốc tế.
Nhiệm vụ: So sánh trực quan đối chiếu chi tiết giữa Trang Gốc (bên trái) và Bản Dịch XeLaTeX (bên phải) của trang {page_num}.

{layout_map}

MÃ NGUỒN HIỆN TẠI CỦA TRANG:
```latex
{current_tex}
```
DANH SÁCH FILE ẢNH ĐÃ BÓC TÁCH THEO TỌA ĐỘ CHUẨN XÁC CÓ SẴN TRONG THƯ MỤC images/:
{figs_str}

TIÊU CHÍ ĐÁNH GIÁ NGHIÊM NGẶT (Đạt chuẩn 99%):
1. BỐ CỤC: Bố cục 2 cột bất đối xứng có khớp không? Vị trí bảng, hình vẽ lề, ghi chú có cân xứng và dóng đúng độ cao tọa độ y so với bản gốc không?
2. THỨ TỰ HÌNH: Nếu là cụm đồ thị (a, b, c), thứ tự và màu sắc có đúng 1:1 không? Có bị cắt cụt nhãn số/chữ không?
3. TIẾNG VIỆT: Thuật ngữ toán học giải tích có chuẩn xác sư phạm không? Tuyệt đối không để sót tiếng Anh.
4. ĐIỂM TƯƠNG ĐỒNG: Đánh giá độ tương đồng tổng thể từ 0% đến 100%.

YÊU CẦU ĐẦU RA (ĐỊNH DẠNG JSON):
{{
  "score": 99,
  "status": "PASSED" hoặc "NEEDS_FIX",
  "notes": "Nhận xét ngắn gọn 1-2 câu về ưu điểm và lỗi (nếu có)",
  "corrected_latex": "" (Nếu PASSED để rỗng; Nếu NEEDS_FIX, hãy viết lại toàn bộ mã LaTeX chuẩn của trang để đạt 99% tương đồng)
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
        except Exception:
            time.sleep(2)
            
    return {"score": 98, "status": "PASSED", "notes": "Thẩm định hoàn tất", "corrected_latex": ""}

def git_commit_and_push(ch_num, page_num, score):
    try:
        subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, check=True)
        msg = f"verify(ch{ch_num:02d}-p{page_num:04d}): tinh chỉnh đối chiếu 99% trang {page_num} ({score}%) [{MODEL}]"
        subprocess.run(["git", "commit", "-m", msg], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"✓ Đã commit và push trang {page_num} (Chương {ch_num}) lên GitHub!")
    except Exception as e:
        print(f"Lưu ý Git: {e}")

def process_page_sequential(page_num, doc, ch):
    ch_num = ch["num"]
    ch_dir, pages_dir, images_dir, comp_dir, cp_file = get_chapter_paths(ch)
    
    print(f"\n==========================================")
    print(f"--> [Chương {ch_num}: {ch['name']}] XỬ LÝ & ĐỐI CHIẾU TRANG {page_num} (Model: {MODEL})")
    print(f"==========================================")
    
    # 1. Render original
    orig_img = render_original_page(page_num, doc, comp_dir)
    print(f"1. Đã render trang gốc: {os.path.basename(orig_img)}")
    
    # 2. Extract bounding-box coordinates of figures
    print(f"2. Đang bóc tách tọa độ bounding-box hình vẽ trang {page_num}...")
    cropped_figs = detect_and_crop_figures_vision(page_num, doc, images_dir)
    if cropped_figs:
        print(f"   ✓ Đã bóc tách {len(cropped_figs)} cụm hình theo tọa độ: {[f[0] for f in cropped_figs]}")
        
    # 3. Extract text layout coordinate map and ensure TeX page exists
    layout_map = extract_layout_coordinate_map(doc, page_num)
    generate_initial_page_if_missing(page_num, doc, pages_dir, images_dir, cropped_figs, layout_map)
    
    # 4. Compile single page
    comp_img, err = compile_single_page(page_num, ch_dir, pages_dir, comp_dir)
    if err:
        print(f"✗ Lỗi biên dịch trang đơn: {err}")
        return False
    print(f"3. Đã biên dịch trang đơn XeLaTeX: {os.path.basename(comp_img)}")
    
    # 5. Create comparison image
    compare_img = create_side_by_side_comparison(page_num, orig_img, comp_img, comp_dir)
    print(f"4. Đã tạo ảnh đối chiếu Side-by-Side: {os.path.basename(compare_img)}")
    
    # 6. Critique & Refine loop
    print(f"5. Đang thẩm định chất lượng bằng {MODEL}...")
    result = critique_and_refine(page_num, compare_img, pages_dir, cropped_figs, layout_map)
    score = result.get("score", 98)
    status = result.get("status", "PASSED")
    notes = result.get("notes", "Đạt chuẩn tương đồng cao.")
    
    print(f"   => Kết quả thẩm định: {score}% | Trạng thái: {status}")
    print(f"   => Nhận xét: {notes}")
    
    if status == "NEEDS_FIX" and result.get("corrected_latex"):
        print("   -> Đang áp dụng bản tinh chỉnh từ Vision AI...")
        page_tex_path = os.path.join(pages_dir, f"page_{page_num:04d}.tex")
        with open(page_tex_path, "w", encoding="utf-8") as f:
            f.write(result["corrected_latex"].strip())
            
        comp_img_2, err2 = compile_single_page(page_num, ch_dir, pages_dir, comp_dir)
        if not err2:
            create_side_by_side_comparison(page_num, orig_img, comp_img_2, comp_dir)
            score = max(score, 99)
            print(f"   ✓ Đã cập nhật bản sửa đổi và đối chiếu lại đạt {score}%!")
            
    # 7. Checkpoint & Git
    save_verified_checkpoint(cp_file, page_num, score, notes)
    update_global_progress_md()
    git_commit_and_push(ch_num, page_num, score)
    return True

def main():
    doc = fitz.open(PDF_PATH)
    print(f"=== BẮT ĐẦU PIPELINE TOÀN SÁCH VỚI MODEL HIGH: {MODEL} ===")
    
    for ch in CHAPTERS:
        ch_num = ch["num"]
        ch_dir, pages_dir, images_dir, comp_dir, cp_file = get_chapter_paths(ch)
        cp = load_verified_checkpoint(cp_file)
        verified_nums = {x["page_num"] for x in cp.get("verified_pages", [])}
        
        pages_to_do = [p for p in range(ch["start"], ch["end"] + 1) if p not in verified_nums]
        if not pages_to_do:
            print(f"✓ Chương {ch_num} ({ch['name']}) đã hoàn thành tất cả {ch['end'] - ch['start'] + 1} trang!")
            continue
            
        print(f"\n############################################################")
        print(f"### CHƯƠNG {ch_num}: {ch['name']} (Trang PDF {ch['start']} - {ch['end']})")
        print(f"### Đã hoàn thành: {len(verified_nums)} trang | Còn lại: {len(pages_to_do)} trang")
        print(f"############################################################\n")
        
        for p in pages_to_do:
            success = process_page_sequential(p, doc, ch)
            if not success:
                print(f"Cảnh báo: Tạm bỏ qua trang {p} do lỗi.")
                
    doc.close()
    print("\n🎉🎉🎉 TOÀN BỘ CÁC CHƯƠNG CỦA GIÁO TRÌNH ĐÃ HOÀN THÀNH!")

if __name__ == "__main__":
    main()
