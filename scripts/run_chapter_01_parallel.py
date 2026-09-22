import os
import sys
import json
import time
import base64
import subprocess
import threading
import requests
import fitz
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PDF_PATH = r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf"
API_ENDPOINT = "http://127.0.0.1:8045/v1/chat/completions"
API_KEY = "sk-96edad6609ce4f96bf40d53d26b7fd42"
MODEL = "gemini-3.8-flash-medium"
XELATEX_EXE = r"C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe"

CH01_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01"
PAGES_DIR = os.path.join(CH01_DIR, "pages")
IMAGES_DIR = os.path.join(CH01_DIR, "images")
CHECKPOINT_FILE = os.path.join(CH01_DIR, "checkpoint.json")

os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

cp_lock = threading.Lock()

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed_pages": []}

def mark_page_completed(page_num):
    with cp_lock:
        cp = load_checkpoint()
        if page_num not in cp["completed_pages"]:
            cp["completed_pages"].append(page_num)
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(cp, f, indent=2, ensure_ascii=False)

def auto_crop_figures(doc, page_idx):
    page = doc.load_page(page_idx)
    drawings = page.get_drawings()
    crops = []
    
    rects = []
    for d in drawings:
        r = d["rect"]
        if r.width > 15 and r.height > 15:
            rects.append(r)
            
    clusters = []
    for r in rects:
        merged = False
        for c in clusters:
            expanded = fitz.Rect(c.x0 - 25, c.y0 - 25, c.x1 + 25, c.y1 + 25)
            if expanded.intersects(r):
                c |= r
                merged = True
                break
        if not merged:
            clusters.append(fitz.Rect(r))
            
    for i, c in enumerate(clusters):
        clip_rect = fitz.Rect(max(0, c.x0 - 10), max(0, c.y0 - 10), min(page.rect.width, c.x1 + 10), min(page.rect.height, c.y1 + 10))
        if clip_rect.width > 30 and clip_rect.height > 30:
            fn = f"p{page_idx+1:04d}_fig{i+1}.png"
            pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0), clip=clip_rect)
            pix.save(os.path.join(IMAGES_DIR, fn))
            crops.append(fn)
            
    return crops

def call_vision_llm(page_num, b64_img, available_figs):
    figs_info = ", ".join([f"`images/{f}`" for f in available_figs]) if available_figs else "Không có hình lẻ"
    
    prompt = f"""Bạn là một chuyên gia số hóa và dịch thuật sách giáo trình toán học quốc tế sang tiếng Việt hàng đầu.
Nhiệm vụ: DỊCH VÀ CHUYỂN ĐỔI trang {page_num} của sách "Calculus: Early Transcendentals (9th Edition)" của James Stewart sang mã nguồn LaTeX tiếng Việt, đạt độ tương đồng 99% về bố cục và hình thức so với bản gốc.

QUY TẮC BẮT BUỘC:
1. DỊCH TOÀN BỘ SANG TIẾNG VIỆT (CHUẨN SƯ PHẠM TOÁN HỌC VIỆT NAM):
- Tuyệt đối không để sót tiếng Anh trong nội dung (trừ tên riêng người hoặc thuật ngữ gốc chú giải thêm trong ngoặc).
- Dịch chuẩn các từ khóa:
  + "EXAMPLE X" -> "\\textbf{{\\textsf{{\\color{{stewartcyan}}VÍ DỤ X}}}}"
  + "SOLUTION" -> "\\textbf{{\\textsf{{\\color{{stewartcyan}}LỜI GIẢI}}}}"
  + "FIGURE X" -> "\\textbf{{\\textsf{{HÌNH X}}}}"
  + "TABLE X" -> "\\textbf{{\\textsf{{BẢNG X}}}}"
  + "SECTION X.Y" -> "\\textbf{{\\textsf{{MỤC X.Y}}}}" (hoặc "BÀI X.Y")
  + "EXERCISES X.Y" -> "\\textbf{{\\textsf{{BÀI TẬP X.Y}}}}"
  + "Definition" -> khung định nghĩa definitionbox
  + "Theorem" -> "ĐỊNH LÝ"
  + "Note" -> "Ghi chú"
  + "Proof" -> "Chứng minh"

2. BỐ CỤC 2 CỘT:
Mỗi trang nằm trọn vẹn trong cấu trúc sau:
\\fancyhead[L]{{...}} \\fancyhead[R]{{...}}
\\noindent
\\begin{{minipage}}[t]{{0.26\\textwidth}}
    % Cột lề: bảng nhỏ, hình nhỏ bên lề, ghi chú lề
\\end{{minipage}}%
\\hfill
\\begin{{minipage}}[t]{{0.71\\textwidth}}
    % Cột chính: tiêu đề mục, nội dung lý thuyết, ví dụ, công thức, hình/bảng lớn
\\end{{minipage}}

(Trường hợp trang là toàn bộ Bài tập - Exercises, vẫn giữ bố cục 2 cột hoặc chia 2 cột bài tập trong cột chính).

3. TOÁN HỌC & HÌNH ẢNH:
- Khung định nghĩa: dùng \\begin{{definitionbox}} ... \\end{{definitionbox}} (viền đỏ stewartred).
- Kết thúc lời giải: đặt ô vuông cyan {{\\color{{stewartcyan}}\\blacksquare}} (trong math) hoặc {{\\color{{stewartcyan}}$\\blacksquare$}} (trong text).
- Các hình khả dụng trên trang này đã crop sẵn trong thư mục images: {figs_info}. Hãy chèn \\includegraphics[width=...]{{images/...}} đúng vị trí tương ứng trong bản gốc.
- Không bao bọc mã trong ```latex ... ```, chỉ trả về nội dung mã nguồn LaTeX hoàn chỉnh.
"""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
            ]}
        ],
        "temperature": 0.1
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    for attempt in range(4):
        try:
            res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=180)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```latex"):
                    content = content[8:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                return content.strip()
            elif res.status_code == 429:
                time.sleep((attempt + 1) * 6)
            else:
                time.sleep(3)
        except Exception:
            time.sleep(3)
    return None

def process_single_page(page_num):
    p_file = os.path.join(PAGES_DIR, f"page_{page_num:04d}.tex")
    if os.path.exists(p_file):
        mark_page_completed(page_num)
        return page_num, True
        
    doc = fitz.open(PDF_PATH)
    page_idx = page_num - 1
    
    # Crop figures
    available_figs = auto_crop_figures(doc, page_idx)
    
    # Render page
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    b64_img = base64.b64encode(pix.tobytes("png")).decode("utf-8")
    doc.close()
    
    # Call Vision API
    tex_content = call_vision_llm(page_num, b64_img, available_figs)
    if tex_content:
        with open(p_file, "w", encoding="utf-8") as f:
            f.write(tex_content)
        mark_page_completed(page_num)
        return page_num, True
    return page_num, False

def compile_master_pdf():
    cp = load_checkpoint()
    completed = sorted(cp.get("completed_pages", []))
    if not completed:
        return
    
    master_tex_file = os.path.join(CH01_DIR, "chapter_01.tex")
    includes = []
    for p in completed:
        p_file = f"pages/page_{p:04d}.tex"
        if os.path.exists(os.path.join(CH01_DIR, p_file)):
            includes.append(f"\\input{{{p_file}}}\n\\newpage\n")
            
    header = r"""\documentclass[10pt,letterpaper]{article}
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

\setmainfont{Times New Roman}
\setsansfont{Arial}

\geometry{
    letterpaper,
    top=1.8cm,
    bottom=1.8cm,
    left=1.5cm,
    right=1.5cm,
    headheight=14pt,
    headsep=0.6cm,
    footskip=0.6cm
}

\definecolor{stewartcyan}{RGB}{0, 118, 186}
\definecolor{stewartred}{RGB}{218, 41, 28}
\definecolor{stewarttableheader}{RGB}{210, 224, 238}
\definecolor{stewartpurplebg}{RGB}{243, 238, 245}
\definecolor{stewartpurpletext}{RGB}{85, 30, 95}
\definecolor{darkgray}{RGB}{40, 40, 40}

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

\begin{document}
"""
    footer = r"\end{document}"
    
    with open(master_tex_file, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(includes) + footer)
        
    print(f"\n--> Đang biên dịch chapter_01.pdf ({len(completed)} trang)...")
    res = subprocess.run([XELATEX_EXE, "-interaction=nonstopmode", "chapter_01.tex"], cwd=CH01_DIR, capture_output=True)
    if res.returncode == 0:
        print(f"✓ Biên dịch thành công chapter_01.pdf!")
    else:
        print(f"Cảnh báo: Biên dịch có mã lỗi {res.returncode}")

def main():
    START_PAGE = 42
    END_PAGE = 111
    NUM_WORKERS = 12
    
    cp = load_checkpoint()
    all_pages = list(range(START_PAGE, END_PAGE + 1))
    pending_pages = [p for p in all_pages if p not in cp.get("completed_pages", [])]
    
    print(f"=== KHỞI CHẠY PARALLEL CHƯƠNG 1 (12 WORKERS) ===")
    print(f"Tổng số trang: {len(all_pages)} (Trang PDF {START_PAGE} - {END_PAGE})")
    print(f"Đã hoàn thành: {len(cp.get('completed_pages', []))} trang")
    print(f"Còn lại: {len(pending_pages)} trang cần xử lý\n")
    
    if not pending_pages:
        print("Tất cả các trang đã hoàn thành!")
        compile_master_pdf()
        return

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        future_to_page = {executor.submit(process_single_page, p): p for p in pending_pages}
        for future in as_completed(future_to_page):
            page_num = future_to_page[future]
            try:
                p_num, success = future.result()
                if success:
                    print(f"✓ [Worker] Hoàn thành trang {p_num}")
                else:
                    print(f"✗ [Worker] Lỗi ở trang {p_num}")
            except Exception as e:
                print(f"✗ [Worker Exception] Trang {page_num}: {e}")
                
    compile_master_pdf()
    print("\n🎉 TOÀN BỘ 12 WORKERS ĐÃ HOÀN TẤT CHƯƠNG 1!")

if __name__ == "__main__":
    main()
