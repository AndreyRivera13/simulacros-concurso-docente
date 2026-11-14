"""Conversor Markdown mínimo (sin dependencias) para content/temas/*.md.
Soporta: ## / ### títulos, párrafos, listas con viñetas (- ) y numeradas (1. ) con anidación por sangría,
bloques de código ``` , **negrita**, *cursiva* y `código`. Todo el texto se escapa antes de dar formato."""
import html, re

def inline(s):
    parts = re.split(r"(`[^`]+`)", s)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append("<code>" + html.escape(p[1:-1]) + "</code>")
        else:
            t = html.escape(p, quote=False)
            t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
            t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
            out.append(t)
    return "".join(out)

ITEM = re.compile(r"^( *)(-|\d+\.) (.*)$")

def convert(md):
    lines = md.splitlines()
    out, para, stack = [], [], []  # stack: [(indent, tag)]
    def flush_para():
        if para: out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>"); para.clear()
    def close_lists(to=-1):
        while stack and stack[-1][0] > to:
            out.append("</li></%s>" % stack.pop()[1])
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            flush_para(); close_lists()
            code = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>"); i += 1; continue
        m = ITEM.match(ln)
        if m:
            flush_para()
            ind, mark, txt = len(m.group(1)), m.group(2), m.group(3)
            tag = "ul" if mark == "-" else "ol"
            if stack and ind < stack[-1][0]: close_lists(ind)
            if stack and stack[-1][0] == ind:
                if stack[-1][1] != tag:
                    out.append("</li></%s>" % stack.pop()[1]); out.append("<%s><li>" % tag); stack.append((ind, tag))
                else:
                    out.append("</li><li>")
            else:
                if stack and ind < stack[-1][0]: pass
                out.append("<%s><li>" % tag); stack.append((ind, tag))
            out.append(inline(txt)); i += 1; continue
        if stack and ln.startswith(" ") and ln.strip():
            out.append(" " + inline(ln.strip())); i += 1; continue
        if ln.startswith("### "):
            flush_para(); close_lists(); out.append("<h5>" + inline(ln[4:]) + "</h5>")
        elif ln.startswith("## "):
            flush_para(); close_lists(); out.append("<h4>" + inline(ln[3:]) + "</h4>")
        elif not ln.strip():
            flush_para(); close_lists()
        else:
            close_lists(); para.append(ln)
        i += 1
    flush_para(); close_lists()
    return "\n".join(out)

def parse_file(text):
    meta = {}
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for l in fm.strip().splitlines():
            k, v = l.split(":", 1); meta[k.strip()] = [x.strip() for x in v.split(",") if x.strip()]
    else:
        body = text
    return meta, convert(body.strip())
