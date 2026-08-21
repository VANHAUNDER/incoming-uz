#!/usr/bin/env python3
"""Собирает index.html: встраивает логотип, изображения документов и PDF в шаблон.

    python3 build.py

Всё из assets/ уходит в файл как data-URI, поэтому итоговый index.html
самодостаточен — его можно просто положить на любой хостинг.
"""
import base64
import pathlib

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / "assets"

SUBS = {
    "{{LOGO}}":       ("logo512.webp",  "image/webp"),
    "{{LIC_THUMB}}":  ("lic_thumb.webp",  "image/webp"),
    "{{CERT_THUMB}}": ("cert_thumb.webp", "image/webp"),
    "{{LIC_FULL}}":   ("lic_full.webp",   "image/webp"),
    "{{CERT_FULL}}":  ("cert_full.webp",  "image/webp"),
    "{{LIC_PDF}}":    ("lic.pdf",   "application/pdf"),
    "{{CERT_PDF}}":   ("cert.pdf",  "application/pdf"),
}


def data_uri(name, mime):
    raw = (ASSETS / name).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def main():
    tpl = (HERE / "card.template.html").read_text(encoding="utf-8")

    for placeholder, (name, mime) in SUBS.items():
        if placeholder not in tpl:
            print("!! в шаблоне нет плейсхолдера:", placeholder)
        tpl = tpl.replace(placeholder, data_uri(name, mime))

    if "{{" in tpl:
        print("!! остались неподставленные плейсхолдеры")

    dst = HERE / "index.html"
    dst.write_text(tpl, encoding="utf-8")
    print(f"index.html — {dst.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
