#!/usr/bin/env python3
"""Собирает страницу из card.template.html.

    python3 build.py                 → index.html, ассеты отдельными файлами
    python3 build.py --standalone    → ещё и standalone.html, всё внутри одного файла

index.html — то, что лежит на хостинге. Логотип, изображения документов и PDF
подтягиваются из assets/ по мере надобности, поэтому страница весит ~35 КБ
и текст появляется сразу, не дожидаясь мегабайта вложений.

standalone.html пригодится, когда файл надо отправить одним куском —
почтой, в мессенджер, на хостинг без папки assets. Он тяжёлый (~1,5 МБ).
"""
import base64
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / "assets"

# плейсхолдер → (файл в assets/, MIME для data-URI)
SUBS = {
    "{{LOGO}}":       ("logo512.webp",    "image/webp"),
    "{{LIC_THUMB}}":  ("lic_thumb.webp",  "image/webp"),
    "{{CERT_THUMB}}": ("cert_thumb.webp", "image/webp"),
    "{{LIC_FULL}}":   ("lic_full.webp",   "image/webp"),
    "{{CERT_FULL}}":  ("cert_full.webp",  "image/webp"),
    "{{LIC_PDF}}":    ("lic.pdf",         "application/pdf"),
    "{{CERT_PDF}}":   ("cert.pdf",        "application/pdf"),
    "{{VCARD}}":      ("contact.vcf",     "text/vcard"),
}


def render(tpl, inline):
    for placeholder, (name, mime) in SUBS.items():
        if placeholder not in tpl:
            print("!! в шаблоне нет плейсхолдера:", placeholder)
        if inline:
            raw = (ASSETS / name).read_bytes()
            value = f"data:{mime};base64," + base64.b64encode(raw).decode()
        else:
            value = f"assets/{name}"
        tpl = tpl.replace(placeholder, value)
    if "{{" in tpl:
        print("!! остались неподставленные плейсхолдеры")
    return tpl


def main():
    tpl = (HERE / "card.template.html").read_text(encoding="utf-8")

    linked = HERE / "index.html"
    linked.write_text(render(tpl, inline=False), encoding="utf-8")
    print(f"index.html       {linked.stat().st_size / 1024:8.0f} KB   ассеты из assets/")

    if "--standalone" in sys.argv:
        single = HERE / "standalone.html"
        single.write_text(render(tpl, inline=True), encoding="utf-8")
        print(f"standalone.html  {single.stat().st_size / 1024:8.0f} KB   всё внутри файла")


if __name__ == "__main__":
    main()
