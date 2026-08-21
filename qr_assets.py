#!/usr/bin/env python3
"""QR-материалы под печать для адреса, на котором лежит визитка.

    python3 qr_assets.py "https://vanhaunder.github.io/incoming-uz/"

Кладёт в print/:
    qr.svg / qr.png   — только код
    qr-card.png       — карточка A6 (105×148 мм, 300 dpi) для стойки

Нужен пакет `qrcode`; карточка рендерится установленным Google Chrome,
чтобы подхватились те же шрифты, что и на самой странице.
"""
import base64
import pathlib
import subprocess
import sys

import qrcode
from qrcode.constants import ERROR_CORRECT_H

HERE = pathlib.Path(__file__).parent
OUTDIR = HERE / "print"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

VIOLET, GOLD, INK = "#650DB9", "#FBD800", "#26044A"


def qr_svg_path(data, ec=ERROR_CORRECT_H, quiet=3):
    """Матрицу QR — в один компактный SVG-путь: соседние модули в строке
    склеиваются в один прямоугольник."""
    q = qrcode.QRCode(error_correction=ec, border=quiet, box_size=1)
    q.add_data(data)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    parts = []
    for y in range(n):
        x = 0
        while x < n:
            if m[y][x]:
                x0 = x
                while x < n and m[y][x]:
                    x += 1
                parts.append(f"M{x0} {y}h{x - x0}v1h-{x - x0}z")
            else:
                x += 1
    return "".join(parts), n, q.version


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://vanhaunder.github.io/incoming-uz/"
    OUTDIR.mkdir(exist_ok=True)
    path, n, ver = qr_svg_path(url)

    # crispEdges — иначе браузер сглаживает модули и камера перестаёт читать код
    plain = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" '
             f'width="{n * 16}" height="{n * 16}" shape-rendering="crispEdges">'
             f'<rect width="{n}" height="{n}" fill="#fff"/>'
             f'<path fill="{INK}" d="{path}"/></svg>')
    (OUTDIR / "qr.svg").write_text(plain, encoding="utf-8")

    logo = base64.b64encode((HERE / "assets" / "logo512.webp").read_bytes()).decode()
    card = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;600;700&family=Oswald:wght@500;600&display=swap">
<style>
  @page{{size:105mm 148mm;margin:0}}
  *{{box-sizing:border-box;margin:0}}
  body{{width:1240px;height:1748px;background:#fff;
       font-family:"Golos Text",sans-serif;color:{INK};
       display:flex;flex-direction:column;align-items:center;
       padding:96px 84px 78px;position:relative;overflow:hidden}}
  .band{{position:absolute;left:0;right:0;top:298px;height:150px;background:{VIOLET}}}
  .band::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:7px;background:{GOLD}}}
  .crest{{position:relative;width:352px;height:352px;border-radius:50%;
         background:#fff;box-shadow:0 0 0 12px #fff}}
  .legal{{position:relative;margin-top:56px;font-family:Oswald,sans-serif;font-weight:600;
        font-size:62px;line-height:1.1;text-transform:uppercase;text-align:center}}
  .trading{{position:relative;margin-top:20px;font-size:22px;font-weight:700;
          letter-spacing:.3em;padding-left:.3em;text-transform:uppercase;color:{VIOLET}}}
  .qr{{position:relative;margin-top:auto;padding:34px;border:5px solid {VIOLET};border-radius:36px}}
  .qr svg{{display:block;width:520px;height:520px;shape-rendering:crispEdges}}
  .ask{{position:relative;margin-top:38px;font-size:32px;font-weight:700;text-align:center;line-height:1.35}}
  .ask span{{display:block;font-size:23px;font-weight:400;color:#5C5473;margin-top:12px}}
  .foot{{position:relative;margin-top:auto;padding-top:34px;font-size:23px;color:#5C5473;text-align:center;line-height:1.5}}
  .foot b{{color:{INK};font-weight:600}}
</style></head><body>
  <div class="band"></div>
  <img class="crest" src="data:image/webp;base64,{logo}" alt="">
  <div class="legal">ООО «GT&nbsp;Marketing<br>and&nbsp;Tourism»</div>
  <div class="trading">Incoming Uzbekistan Travel Agency</div>
  <div class="qr"><svg viewBox="0 0 {n} {n}">
    <rect width="{n}" height="{n}" fill="#fff"></rect>
    <path fill="{INK}" d="{path}"></path></svg></div>
  <div class="ask">Наведите камеру<span>Реквизиты, лицензия и документы компании</span></div>
  <div class="foot"><b>+998 90 978 67 86</b> · info@incoming.uz<br>Лицензия № 749920 · ИНН 312 097 521</div>
</body></html>"""
    (OUTDIR / "qr-card.html").write_text(card, encoding="utf-8")

    for src, out, size in [("qr.svg", "qr.png", (n * 16, n * 16)),
                           ("qr-card.html", "qr-card.png", (1240, 1748))]:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--virtual-time-budget=12000",
                        "--run-all-compositor-stages-before-draw",
                        "--default-background-color=00000000",
                        f"--screenshot={OUTDIR / out}",
                        f"--window-size={size[0]},{size[1]}",
                        f"file://{OUTDIR / src}"],
                       capture_output=True)

    print("адрес:", url)
    print(f"QR: версия {ver}, {n} модулей, коррекция H")
    for f in sorted(OUTDIR.iterdir()):
        print(f"  {f.name:16s} {f.stat().st_size / 1024:7.0f} KB")


if __name__ == "__main__":
    main()
