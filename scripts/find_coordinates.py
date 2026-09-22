import fitz
import sys

sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"E:\01_Math & Physics\Math\Calculus Early Transcendentals Ninth Edition by James Stewart, Daniel K. Clegg, Saleem Watson (z-lib.org).pdf")

def find_elements(p_idx):
    page = doc.load_page(p_idx)
    print(f"\n==================== Page {p_idx+1} ====================")
    # Print all blocks
    blocks = page.get_text("blocks")
    for b in blocks:
        text = " ".join(b[4].split())
        if any(w in text for w in ["FIGURE", "Figure", "Table", "TABLE", "EXAMPLE", "Example", "Definition", "DEFINITION"]):
            print(f"Text block ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}): {text[:90]}")

for p in range(42, 47):
    find_elements(p)
