import requests
import json
import base64
import fitz
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf"
doc = fitz.open(PDF_PATH)
page = doc.load_page(48) # page 49
pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
doc.close()

prompt = """Phân tích hình ảnh trang 14 này và trích xuất tọa độ hộp bao (bounding box) của TẤT CẢ các khối hình vẽ / đồ thị có trên trang.
Tọa độ chuẩn hóa theo thang 0-1000 dạng: [ymin, xmin, ymax, xmax].

LƯU Ý QUAN TRỌNG:
1. Với Figure 14 gồm 3 đồ thị con (a, b, c) nằm dàn ngang: Hãy bóc trọn vẹn cả 3 đồ thị này vào MỘT HỘP BAO DUY NHẤT (bao gồm cả trục tọa độ, nhãn (-2, 0) và nhãn subcaption (a), (b), (c)).
2. Với Figure 15 ở cột lề trái: Bóc trọn vẹn đồ thị và hệ trục tọa độ của nó.

Trả về định dạng JSON:
{
  "figures": [
    {
      "id": "figure_14",
      "box_1000": [ymin, xmin, ymax, xmax],
      "description": "Hình 14 gồm cả 3 đồ thị parabol và 2 nửa nhánh"
    },
    {
      "id": "figure_15",
      "box_1000": [ymin, xmin, ymax, xmax],
      "description": "Hình 15 hàm từng khúc ở cột lề trái"
    }
  ]
}
Chỉ trả về JSON thuần túy.
"""

payload = {
    "model": "gemini-3.8-flash-medium",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
    ]}],
    "temperature": 0.1
}

res = requests.post(
    "http://127.0.0.1:8045/v1/chat/completions",
    json=payload,
    headers={"Authorization": "Bearer sk-96edad6609ce4f96bf40d53d26b7fd42"}
)

print(res.json()["choices"][0]["message"]["content"])
