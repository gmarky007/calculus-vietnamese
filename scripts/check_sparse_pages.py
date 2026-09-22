import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open(r'C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01\chapter_01.pdf')
print(f'Total pages: {len(doc)}')
sparse = []
for p in range(len(doc)):
    txt = doc[p].get_text().strip()
    if len(txt) < 300:
        sparse.append((p+1, len(txt), repr(txt[:80])))

print(f'Sparse pages count: {len(sparse)}')
for p, l, t in sparse:
    print(f'Page {p:2d} ({l:3d} chars): {t}')
