# Calculus: Early Transcendentals (9th Edition) - Bản Việt Hóa XeLaTeX

Dự án dịch thuật và số hóa giáo trình **Calculus: Early Transcendentals (9th Edition)** của James Stewart, Daniel K. Clegg, và Saleem Watson sang tiếng Việt với tiêu chuẩn chất lượng cao:
- **Ngôn ngữ**: Chuẩn sư phạm giải tích Việt Nam, tự nhiên, chính xác về mặt toán học.
- **Bố cục & Hình thức**: Tương đồng >99% so với bản in gốc (bố cục 2 cột bất đối xứng, màu sắc Stewart Cyan & Stewart Red, hộp định nghĩa, hình vẽ vector trích xuất độ phân giải cao).
- **Quy trình kiểm soát**: Tinh chỉnh và đối chiếu trực quan từng trang một (side-by-side) trước khi đưa vào bản PDF hoàn chỉnh.

## Cấu trúc thư mục
- `chapters/ch01/`: Mã nguồn LaTeX và PDF Chương 1.
  - `pages/`: Các file mã nguồn TeX từng trang đơn lẻ (`page_0042.tex` đến `page_0111.tex`).
  - `images/`: Tập hợp toàn bộ hình vẽ vector và sơ đồ minh họa trích xuất từ sách.
  - `comparisons/`: Ảnh đối chiếu trực quan từng trang (Bản gốc vs Bản dịch XeLaTeX).
  - `chapter_01.tex`: File master tập hợp toàn bộ chương.
  - `chapter_01.pdf`: File PDF hoàn chỉnh đã biên dịch.
- `scripts/`: Bộ công cụ trích xuất hình, đối chiếu thị giác và biên dịch tự động.

## Công nghệ sử dụng
- Compiler: XeLaTeX (MiKTeX x64) với font Times New Roman & Arial.
- Image Extraction & Processing: PyMuPDF (Fitz) & Pillow.
- Vision AI Quality Check: Gemini Vision.
