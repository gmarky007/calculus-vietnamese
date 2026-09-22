import fitz
import sys

sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf")

for p in range(42, 47):
    page = doc.load_page(p)
    print(f"\n==================== PAGE {p+1} (Book page {p-34}) ====================")
    rects = page.search_for("FIGURE")
    for r in rects:
        print(f"\n[FIGURE instance at {r}]")
        # Let's inspect surrounding text in a window
        surr_rect = fitz.Rect(max(0, r.x0 - 20), max(0, r.y0 - 200), min(page.rect.width, r.x1 + 300), min(page.rect.height, r.y1 + 80))
        lines = page.get_text("text", clip=surr_rect).strip().splitlines()
        for line in lines[:8]:
            print("   txt:", line.strip())

        # Check drawings in this area
        draw_count = 0
        draw_box = fitz.Rect()
        for d in page.get_drawings():
            if d["rect"].intersects(surr_rect):
                draw_count += 1
                draw_box |= d["rect"]
        print(f"   Drawings overlapping: {draw_count}, combined box: {draw_box}")
