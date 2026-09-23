import os, glob, fitz, subprocess, sys, json, time, requests, base64

sys.path.insert(0, 'scripts')
from pipeline_page_by_page import CHAPTERS, get_chapter_paths, get_chapter_info, MASTER_PREAMBLE, XELATEX_EXE, PROJECT_ROOT, MODEL, API_ENDPOINT, API_KEY, create_side_by_side_comparison

def clean_file_on_disk(fp):
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        c = f.read()
    
    modified = False
    if r'\begin{document}' in c:
        c = c.split(r'\begin{document}', 1)[1]
        modified = True
    if r'\end{document}' in c:
        c = c.split(r'\end{document}', 1)[0]
        modified = True
        
    lines = []
    for l in c.splitlines():
        sl = l.strip()
        if sl.startswith(r'\documentclass') or sl.startswith(r'\usepackage') or sl.startswith(r'\geometry'):
            modified = True
            continue
        lines.append(l)
        
    clean_c = '\n'.join(lines).strip()
    if modified:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(clean_c + '\n')
    return clean_c

def compile_and_check(pno, clean_c):
    ch = get_chapter_info(pno)
    ch_dir, pages_dir, images_dir, comp_dir, _ = get_chapter_paths(ch)
    
    temp_tex = os.path.join(ch_dir, f'batch_check_p{pno:04d}.tex')
    full = MASTER_PREAMBLE + clean_c + '\n\\end{document}\n'
    with open(temp_tex, 'w', encoding='utf-8') as f:
        f.write(full)
        
    res = subprocess.run([XELATEX_EXE, '-interaction=nonstopmode', f'batch_check_p{pno:04d}.tex'], cwd=ch_dir, capture_output=True)
    pdf_out = os.path.join(ch_dir, f'batch_check_p{pno:04d}.pdf')
    
    status = 'ERROR'
    n_pages = 0
    if os.path.exists(pdf_out):
        try:
            doc = fitz.open(pdf_out)
            n_pages = len(doc)
            if n_pages == 1:
                status = 'OK'
                pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                comp_img = os.path.join(comp_dir, f'compiled_p{pno:04d}.png')
                pix.save(comp_img)
                orig_img = os.path.join(comp_dir, f'original_p{pno:04d}.png')
                if os.path.exists(orig_img):
                    create_side_by_side_comparison(pno, orig_img, comp_img, comp_dir)
            else:
                status = 'OVERFLOW'
            doc.close()
        except Exception as e:
            status = 'ERROR'
            
    for ext in ['.aux', '.log', '.tex', '.pdf']:
        f_del = os.path.join(ch_dir, f'batch_check_p{pno:04d}{ext}')
        if os.path.exists(f_del):
            try: os.remove(f_del)
            except Exception: pass
            
    return status, n_pages

def main():
    tex_files = sorted(glob.glob(os.path.join(PROJECT_ROOT, 'chapters', 'ch*', 'pages', 'page_*.tex')))
    print(f'Starting batch clean & recompile for {len(tex_files)} pages...')
    
    ok_list = []
    overflow_list = []
    error_list = []
    
    for idx, fp in enumerate(tex_files):
        pno = int(os.path.basename(fp).replace('page_', '').replace('.tex', ''))
        clean_c = clean_file_on_disk(fp)
        status, n_pages = compile_and_check(pno, clean_c)
        
        if status == 'OK':
            ok_list.append(pno)
        elif status == 'OVERFLOW':
            overflow_list.append((pno, n_pages))
        else:
            error_list.append(pno)
            
        if (idx + 1) % 25 == 0 or (idx + 1) == len(tex_files):
            print(f'Progress: {idx+1}/{len(tex_files)} | OK: {len(ok_list)} | Overflow: {len(overflow_list)} | Error: {len(error_list)}')
            
    summary = {
        'total': len(tex_files),
        'ok': ok_list,
        'overflow': overflow_list,
        'error': error_list
    }
    with open('batch_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
        
    print(f'Batch complete! OK: {len(ok_list)}, Overflow: {len(overflow_list)}, Error: {len(error_list)}')

if __name__ == '__main__':
    main()
