import os
import sys
import base64
import time
import requests
import fitz

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PDF_PATH = r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf"
API_ENDPOINT = "http://127.0.0.1:8045/v1/chat/completions"
API_KEY = "sk-96edad6609ce4f96bf40d53d26b7fd42"
MODEL = "gemini-3.8-flash-medium"

BASE_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese"
OUTPUT_DIR = os.path.join(BASE_DIR, "output_md")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

PROMPT_SYSTEM = r"""Bạn là một giáo sư toán học và chuyên gia số hóa sách giáo trình quốc tế hàng đầu.

Nhiệm vụ của bạn: Dịch và số hóa trang sách giáo trình "Calculus: Early Transcendentals (9th Edition)" của James Stewart sang tiếng Việt với tiêu chuẩn chất lượng cao nhất:
1. **NGÔN TỪ SƯ PHẠM DỄ HIỂU**: Dịch thuật ngữ toán học chuẩn mực của Việt Nam, văn phong trong sáng, tự nhiên, sư phạm, giải thích tường minh, gãy gọn, giúp người học nắm bắt bản chất một cách dễ dàng nhất.
2. **BẢO TOÀN BỐ CỤC TRÊN 95%**:
   - Giữ nguyên cấu trúc phân cấp: Tiêu đề chương, tên mục (Section), tiểu mục, số trang sách gốc.
   - Định nghĩa (Definition), Định lý (Theorem), Quy tắc đóng khung: Sử dụng Markdown callout chuẩn như `> [!NOTE] **ĐỊNH NGHĨA**` hoặc `> [!IMPORTANT] **QUY TẮC**`.
   - Các ví dụ (Example): Trình bày nổi bật: `### 📌 VÍ DỤ X` và `**Lời giải:**`.
   - Bảng biểu (Table): Trình bày bằng Markdown Table chuẩn.
   - Ghi chú bên lề (Margin notes / Figure captions): Đặt đúng vị trí tương ứng trong dòng đọc.
3. **CÔNG THỨC TOÁN HỌC (LATEX CHUẨN XÁC 100%)**:
   - Tất cả ký hiệu, biến số, công thức toán học PHẢI dùng LaTeX chuẩn:
     - Công thức nội dòng: `$f(x) = x^2$`
     - Công thức khối: `$$A = \pi r^2$$` hoặc các hệ phương trình / hàm phân nhánh dùng `\begin{cases} ... \end{cases}`.
   - Giữ nguyên mọi ký hiệu toán học đặc thù ($\pi, \in, \subseteq, \approx, \to, \Delta, \le, \ge, \pm, \cup, \cap, \infty$).
4. **HÌNH VẼ & ĐỒ THỊ MINH HỌA**:
   - Với mỗi hình xuất hiện trên trang, chèn đúng định dạng: `![Tên hình](images/figure_X.png)` (trong đó X là số thứ tự hình, ví dụ `figure_1.png`, `figure_2.png`...).
   - Dưới mỗi hình, dịch chú thích gốc sang tiếng Việt và bổ sung một đoạn **[Mô tả trực quan của đồ thị]** ngắn gọn (trục tọa độ, dạng đường cong/hình khối, các điểm đặc biệt) để người học hình dung đầy đủ.
5. **TÍNH TOÀN VẸN**:
   - Không tóm tắt, không lược bỏ bất kỳ ý toán học nào của trang sách.
   - Trả về trực tiếp văn bản Markdown hoàn chỉnh, không bao bọc trong code block ```markdown ... ``` ngoài cùng, không thêm lời chào hay kết luận của AI.
"""

def render_page_to_base64(doc, page_idx, zoom=2.0):
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    return base64.b64encode(pix.tobytes("png")).decode("utf-8")

def translate_page(page_num, max_retries=3):
    page_idx = page_num - 1
    doc = fitz.open(PDF_PATH)
    print(f"\n[Trang {page_num}] Đang render ảnh...")
    b64_img = render_page_to_base64(doc, page_idx)
    doc.close()

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Hãy dịch và tái hiện trang {page_num} của sách sang tiếng Việt theo đúng các nguyên tắc trên."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
                ]
            }
        ],
        "temperature": 0.1
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    for attempt in range(max_retries):
        try:
            print(f"[Trang {page_num}] Đang gửi API (lần thử {attempt + 1})...")
            res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=180)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```markdown"):
                    content = content[11:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                return content.strip()
            elif res.status_code == 429:
                wait_time = (attempt + 1) * 10
                print(f"[429 Quota/Rate Limit] Chờ {wait_time}s thử lại...")
                time.sleep(wait_time)
            else:
                print(f"[Lỗi {res.status_code}] {res.text}")
                time.sleep(5)
        except Exception as e:
            print(f"[Exception] {e}")
            time.sleep(5)
    return None

def main():
    pages_to_process = [43, 44, 45, 46, 47]
    all_pages_content = []

    print(f"=== BẮT ĐẦU XỬ LÝ 5 TRANG MẪU: {pages_to_process} ===")
    for p in pages_to_process:
        out_file = os.path.join(OUTPUT_DIR, f"page_{p:04d}.md")
        
        # Nếu đã có trang 43 thì đọc lại để tiết kiệm token
        if p == 43 and os.path.exists(out_file):
            print(f"[Trang 43] Đã tồn tại sẵn từ bài test trước, sử dụng lại.")
            with open(out_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = translate_page(p)
            if content:
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✓ Đã lưu trang {p} vào: {out_file}")
            else:
                print(f"✗ Không thể xử lý trang {p}")
                continue
        
        all_pages_content.append(f"<!-- ===== TRANG PDF {p} ===== -->\n\n{content}\n\n---\n")
        time.sleep(2)

    # Ghép thành 1 file hoàn chỉnh
    if all_pages_content:
        master_file = os.path.join(OUTPUT_DIR, "calculus_section_1.1_vietnamese.md")
        with open(master_file, "w", encoding="utf-8") as f:
            f.write("# GIẢI TÍCH: CALCULUS (EARLY TRANSCENDENTALS - 9TH EDITION)\n\n")
            f.write("Tác giả: James Stewart, Daniel K. Clegg, Saleem Watson\n\n")
            f.write("Bản dịch tiếng Việt sư phạm - Tái hiện chuẩn xác bố cục, công thức LaTeX & đồ thị minh họa\n\n")
            f.write("---\n\n")
            f.write("\n".join(all_pages_content))
        print(f"\n🎉 HOÀN TẤT 5 TRANG! File tổng hợp tại: {master_file}")

if __name__ == "__main__":
    main()
