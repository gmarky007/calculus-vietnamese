import os
import re
import glob

PAGES_DIR = r"C:\Users\TONY\.gemini\antigravity\scratch\calculus_vietnamese\chapters\ch01\pages"

def tighten_content(content):
    # Add enlargethispage at top of each page if not present
    if r"\enlargethispage" not in content:
        content = r"\enlargethispage{1.5\baselineskip}" + "\n" + content

    # Scale down large vspace
    def scale_vspace(match):
        val = float(match.group(1))
        unit = match.group(2)
        new_val = round(val * 0.82, 2)
        return f"\\vspace{{{new_val}{unit}}}"

    content = re.sub(r"\\vspace\{([0-9\.]+)(cm|em)\}", scale_vspace, content)
    content = re.sub(r"\\vspace\*\{([0-9\.]+)(cm|em)\}", scale_vspace, content)
    return content

def main():
    files = sorted(glob.glob(os.path.join(PAGES_DIR, "page_*.tex")))
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            c = fp.read()
        c_new = tighten_content(c)
        if c_new != c:
            with open(f, "w", encoding="utf-8") as fp:
                fp.write(c_new)
    print(f"Tightened {len(files)} pages.")

if __name__ == "__main__":
    main()
