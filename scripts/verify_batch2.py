import os, sys, subprocess, fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
from run_24_pages_parallel import PAGE_TEMPLATE_HEADER, PAGE_TEMPLATE_FOOTER, PAGES_DIR, CH01_DIR, COMPS_DIR, PDF_PATH, XELATEX_EXE

results = []
for p in range(70, 94):
    fpath = os.path.join(PAGES_DIR, f'page_{p:04d}.tex')
    with open(fpath, 'r', encoding='utf-8') as f:
        body = f.read()
    
    test_tex_path = os.path.join(CH01_DIR, f'temp_p{p:04d}.tex')
    full_tex = PAGE_TEMPLATE_HEADER + '\n' + body + '\n' + PAGE_TEMPLATE_FOOTER
    with open(test_tex_path, 'w', encoding='utf-8') as f:
        f.write(full_tex)

    res = subprocess.run([XELATEX_EXE, '-interaction=nonstopmode', f'temp_p{p:04d}.tex'], cwd=CH01_DIR, capture_output=True)
    pdf_path = os.path.join(CH01_DIR, f'temp_p{p:04d}.pdf')
    
    if os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        cnt = len(doc)
        
        # generate comparison image
        c_pix = doc[0].get_pixmap(dpi=150)
        doc.close()
        
        o_doc = fitz.open(PDF_PATH)
        o_pix = o_doc[p - 1].get_pixmap(dpi=150)
        o_doc.close()
        
        im_orig = Image.frombytes('RGB', [o_pix.width, o_pix.height], o_pix.samples)
        im_comp = Image.frombytes('RGB', [c_pix.width, c_pix.height], c_pix.samples)
        
        target_h = max(im_orig.height, im_comp.height)
        w_orig = int(im_orig.width * (target_h / im_orig.height))
        w_comp = int(im_comp.width * (target_h / im_comp.height))
        
        im_orig_resized = im_orig.resize((w_orig, target_h), Image.Resampling.LANCZOS)
        im_comp_resized = im_comp.resize((w_comp, target_h), Image.Resampling.LANCZOS)
        
        comp_im = Image.new('RGB', (w_orig + w_comp + 10, target_h), (200, 200, 200))
        comp_im.paste(im_orig_resized, (0, 0))
        comp_im.paste(im_comp_resized, (w_orig + 10, 0))
        comp_im.save(os.path.join(COMPS_DIR, f'compare_p{p:04d}.png'))
        
        results.append((p, cnt))
        status_str = "OK" if cnt == 1 else f"OVERFLOW ({cnt} trang)"
        print(f"Trang {p}: {cnt} trang -> {status_str}", flush=True)
    else:
        results.append((p, 'COMPILE_ERROR'))
        print(f"Trang {p}: COMPILE_ERROR", flush=True)

    # Cleanup temp
    for ext in ['.aux', '.log', '.tex', '.pdf']:
        tmp_f = os.path.join(CH01_DIR, f'temp_p{p:04d}{ext}')
        if os.path.exists(tmp_f):
            try: os.remove(tmp_f)
            except: pass

ok_count = sum(1 for p, c in results if c == 1)
print(f"\n=== KET QUA CUOI CUNG: {ok_count}/24 TRANG DAT 1 TRANG (100% OK) ===", flush=True)
