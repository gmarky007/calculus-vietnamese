import os, glob, fitz, subprocess, sys

sys.path.insert(0, 'scripts')
from pipeline_page_by_page import CHAPTERS, get_chapter_paths, get_chapter_info, MASTER_PREAMBLE, XELATEX_EXE, PROJECT_ROOT

def run_audit():
    tex_files = sorted(glob.glob(os.path.join(PROJECT_ROOT, 'chapters', 'ch*', 'pages', 'page_*.tex')))
    print(f'Starting audit for {len(tex_files)} pages...')

    results = {'ok': [], 'overflow': [], 'error': []}

    for idx, fp in enumerate(tex_files):
        fn = os.path.basename(fp)
        pno = int(fn.replace('page_', '').replace('.tex', ''))
        ch = get_chapter_info(pno)
        ch_dir, pages_dir, images_dir, comp_dir, _ = get_chapter_paths(ch)
        
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            c = f.read()
            
        if r'\begin{document}' in c:
            c = c.split(r'\begin{document}', 1)[1]
        if r'\end{document}' in c:
            c = c.split(r'\end{document}', 1)[0]
        lines = [l for l in c.splitlines() if not (l.strip().startswith(r'\documentclass') or l.strip().startswith(r'\usepackage') or l.strip().startswith(r'\geometry'))]
        clean_c = '\n'.join(lines)
        
        temp_tex = os.path.join(ch_dir, f'audit_temp_p{pno:04d}.tex')
        full = MASTER_PREAMBLE + clean_c + '\n\\end{document}\n'
        with open(temp_tex, 'w', encoding='utf-8') as f:
            f.write(full)
            
        res = subprocess.run([XELATEX_EXE, '-interaction=nonstopmode', f'audit_temp_p{pno:04d}.tex'], cwd=ch_dir, capture_output=True)
        pdf_out = os.path.join(ch_dir, f'audit_temp_p{pno:04d}.pdf')
        
        if os.path.exists(pdf_out):
            try:
                doc = fitz.open(pdf_out)
                n_pages = len(doc)
                doc.close()
                if n_pages == 1:
                    results['ok'].append(pno)
                else:
                    results['overflow'].append((pno, n_pages))
            except Exception:
                results['error'].append(pno)
        else:
            results['error'].append(pno)
            
        for ext in ['.aux', '.log', '.tex', '.pdf']:
            f_del = os.path.join(ch_dir, f'audit_temp_p{pno:04d}{ext}')
            if os.path.exists(f_del):
                try: os.remove(f_del)
                except Exception: pass

        if (idx + 1) % 50 == 0 or (idx + 1) == len(tex_files):
            print(f"Audited {idx+1}/{len(tex_files)} pages... OK: {len(results['ok'])}, Overflow: {len(results['overflow'])}, Error: {len(results['error'])}")

    print('=== KET QUA AUDIT CHI TIET ===')
    print('Trang OK:', len(results['ok']))
    print('Trang Overflow:', len(results['overflow']), results['overflow'][:30])
    print('Trang Error:', len(results['error']), results['error'][:30])

if __name__ == '__main__':
    run_audit()
