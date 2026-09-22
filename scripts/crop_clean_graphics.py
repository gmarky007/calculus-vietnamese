import fitz
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

doc = fitz.open(r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf")
img_dir = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\images"
os.makedirs(img_dir, exist_ok=True)

# Pure graphic crops without English captions
clean_figures = [
    # (page_idx, rect, filename)
    (42, fitz.Rect(215, 345, 545, 510), "figure_1_clean.png"),
    (43, fitz.Rect(68, 85, 200, 142), "figure_2_clean.png"),
    (43, fitz.Rect(55, 188, 200, 285), "figure_3_clean.png"),
    (43, fitz.Rect(222, 365, 365, 485), "figure_4_clean.png"),
    (43, fitz.Rect(390, 365, 555, 485), "figure_5_clean.png"),
    (43, fitz.Rect(65, 510, 205, 620), "figure_6_clean.png"),
    (44, fitz.Rect(35, 105, 165, 215), "figure_7_clean.png"),
    (44, fitz.Rect(35, 238, 165, 350), "figure_8_clean.png"),
    (45, fitz.Rect(70, 320, 315, 485), "figure_9_clean.png"),
    (45, fitz.Rect(335, 320, 580, 485), "figure_10_clean.png"),
    (46, fitz.Rect(35, 155, 180, 240), "figure_11_clean.png"),
    (46, fitz.Rect(35, 365, 180, 455), "figure_12_clean.png")
]

for p_idx, r, fn in clean_figures:
    page = doc.load_page(p_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(4.0, 4.0), clip=r)
    pix.save(os.path.join(img_dir, fn))
    print(f"✓ Saved {fn}: {pix.width}x{pix.height}")

print("\nĐã bóc tách 100% hình ảnh đồ họa thuần túy (không dính caption tiếng Anh)!")
