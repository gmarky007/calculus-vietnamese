import os
import sys
import base64
import requests
import fitz

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PDF_PATH = r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf"
API_ENDPOINT = "http://127.0.0.1:8045/v1/chat/completions"
API_KEY = "sk-96edad6609ce4f96bf40d53d26b7fd42"
MODEL = "gemini-3.8-flash-medium"

OUTPUT_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese"
os.makedirs(os.path.join(OUTPUT_DIR, "output_md"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)

PROMPT_SYSTEM = """Bạn là một giáo sư toán học và chuyên gia số hóa sách giáo trình quốc tế hàng đầu.

Nhiệm vụ của bạn: Chuyển đổi và dịch trang sách giáo trình "Calculus: Early Transcendentals (9th Edition)" của James Stewart sang tiếng Việt với chất lượng cao nhất:
1. **NGÔN TỪ SƯ PHẠM DỄ HIỂU**: Dịch thuật ngữ toán học chuẩn mực của Việt Nam, lời văn tự nhiên, sư phạm, giải thích sáng sủa, gãy gọn, giúp người đọc dễ dàng tiếp thu.
2. **BẢO TOÀN BỐ CỤC TRÊN 95%**:
   - Giữ nguyên cấu trúc phân cấp: Tiêu đề chương, tên mục (Section), các tiểu mục, số trang gốc.
   - Các định nghĩa (Definition), định lý (Theorem), quy tắc đóng khung: Sử dụng Markdown callout chuẩn như `> [!NOTE] **ĐỊNH NGHĨA**` hoặc `> [!IMPORTANT] **ĐỊNH LÝ**`.
   - Các ví dụ (Example): Trình bày rõ ràng `### 📌 VÍ DỤ X` và `**Lời giải:**`.
   - Bảng biểu (Table): Dùng Markdown table chuẩn.
   - Ghi chú bên lề (Margin notes / Figure captions): Đặt đúng vị trí tương ứng trong dòng đọc.
3. **CÔNG THỨC TOÁN HỌC (LATEX CHUẨN XÁC 100%)**:
   - Tất cả các ký hiệu, biến số, biểu thức toán học PHẢI được viết bằng LaTeX chuẩn:
     - Công thức nội dòng: `$f(x) = x^2$`
     - Công thức khối: `$$A = \pi r^2$$`
   - Tuyệt đối không làm mất các ký hiệu toán học đặc thù ($\pi, \in, \subseteq, \approx, \to, \Delta, \le, \ge, \pm$).
4. **MÔ TẢ HÌNH VẼ & ĐỒ THỊ**:
   - Tại vị trí có hình vẽ/đồ thị, chèn thẻ: `![Tên hình](images/page_XXXX_figure_Y.png)`.
   - Ngay dưới hình, cung cấp chú thích gốc dịch sang tiếng Việt và một đoạn **[Mô tả trực quan của đồ thị]** (trục hoành, trục tung, dạng đường cong, các điểm mốc) để người học nắm bắt trọn vẹn bản chất hình học.
5. **TÍNH TOÀN VẸN**:
   - Không tóm tắt, không bỏ sót nội dung toán học nào trên trang sách.
   - Trả về trực tiếp văn bản Markdown hoàn chỉnh. Không bọc trong ```markdown ... ``` ngoài cùng, không thêm lời chào hay kết luận của AI.
"""

def render_page_to_base64(doc, page_idx, zoom=2.0):
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    return base64.b64encode(pix.tobytes("png")).decode("utf-8")

def process_page(page_num):
    page_idx = page_num - 1
    doc = fitz.open(PDF_PATH)
    print(f"--> Đang render trang {page_num}...")
    b64_img = render_page_to_base64(doc, page_idx)
    doc.close()

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Hãy dịch và tái hiện trang {page_num} của cuốn sách sang tiếng Việt theo đúng các nguyên tắc trên."},
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

    print(f"--> Đang gửi trang {page_num} đến API proxy...")
    res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=180)
    if res.status_code != 200:
        print(f"Lỗi API: {res.status_code} - {res.text}")
        return None
    
    data = res.json()
    content = data["choices"][0]["message"]["content"].strip()
    if content.startswith("```markdown"):
        content = content[11:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()

if __name__ == "__main__":
    content = process_page(43)
    if content:
        out_file = os.path.join(OUTPUT_DIR, "output_md", "page_0043.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Đã lưu thành công trang 43 vào: {out_file}")
