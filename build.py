#!/usr/bin/env python3
"""Собирает index.html: встраивает логотип, документы и PDF в шаблон."""
import base64, pathlib, sys

HERE = pathlib.Path(__file__).parent
SCRATCH = pathlib.Path(
    "/private/tmp/claude-501/-Users-sayber-al/928fc77b-c7d1-4eac-8293-aabac9d4b7b7/scratchpad"
)
OUT = SCRATCH / "out"


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    tpl = (HERE / "card.template.html").read_text(encoding="utf-8")

    subs = {
        "{{LOGO}}":        data_uri(OUT / "logo512.webp", "image/webp"),
        "{{LIC_THUMB}}":   data_uri(OUT / "lic_thumb.webp", "image/webp"),
        "{{CERT_THUMB}}":  data_uri(OUT / "cert_thumb.webp", "image/webp"),
        "{{LIC_FULL}}":    data_uri(OUT / "lic_full.webp", "image/webp"),
        "{{CERT_FULL}}":   data_uri(OUT / "cert_full.webp", "image/webp"),
        "{{LIC_PDF}}":     data_uri(SCRATCH / "lic.pdf", "application/pdf"),
        "{{CERT_PDF}}":    data_uri(SCRATCH / "cert.pdf", "application/pdf"),
    }

    for k, v in subs.items():
        if k not in tpl:
            print("!! placeholder не найден:", k)
        tpl = tpl.replace(k, v)

    if "{{" in tpl:
        print("!! в шаблоне остались неподставленные плейсхолдеры")

    dst = HERE / "index.html"
    dst.write_text(tpl, encoding="utf-8")
    print(f"index.html  {dst.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
