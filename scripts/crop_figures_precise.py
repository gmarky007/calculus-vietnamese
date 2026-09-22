import fitz
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

doc = fitz.open(r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf")
img_dir = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\images"
os.makedirs(img_dir, exist_ok=True)

# Precise coordinates for all figures
figures = [
    # (page_idx, rect, filename)
    (42, fitz.Rect(215, 345, 475, 505), "figure_1.png"),
    (43, fitz.Rect(68, 85, 200, 172), "figure_2.png"),
    (43, fitz.Rect(55, 188, 200, 315), "figure_3.png"),
    (43, fitz.Rect(222, 365, 365, 502), "figure_4.png"),
    (43, fitz.Rect(412, 365, 555, 502), "figure_5.png"),
    (43, fitz.Rect(65, 510, 205, 636), "figure_6.png"),
    (44, fitz.Rect(35, 105, 165, 232), "figure_7.png"),
    (44, fitz.Rect(35, 238, 165, 366), "figure_8.png"),
    (45, fitz.Rect(70, 320, 315, 502), "figure_9.png"),
    (45, fitz.Rect(335, 320, 580, 502), "figure_10.png"),
    (46, fitz.Rect(35, 155, 180, 258), "figure_11.png"),
    (46, fitz.Rect(35, 365, 180, 475), "figure_12.png")
]

for p_idx, r, fn in figures:
    page = doc.load_page(p_idx)
    # 4x zoom for ultra sharp rendering
    pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0), clip=r)
    target_path = os.path.join(img_dir, fn)
    pix.save(target_path)
    print(f"✓ Saved {fn}: size {pix.width}x{pix.height}")

print("\nAll 12 figures cropped successfully with 4x DPI precision!")
