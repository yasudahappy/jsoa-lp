#!/usr/bin/env python3
"""JSOA ロゴをベクターで再構築する。

元データ（Illustrator等）が失われているため、126px の LOGO.png から起こし直す。
  ・中央のエンブレム（天秤・JSOA・握手）……… potrace でトレース
  ・外周のリングと文字 ………………………… 実測値をもとに作り直し

元画像では円周の文字が緑のリングから白く抜かれている。文字を生きたテキストに
することで、英語名の差し替えと、潰れて読めない日本語の復元ができる。

  python3 design/logo/build.py            → design/logo/logo.svg
"""
from PIL import Image
import numpy as np, potrace, pathlib, math

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC  = ROOT / 'assets/images/LOGO.png'
OUT  = ROOT / 'design/logo/logo.svg'

# --- 実測値（1008px 換算。build 内で正規化する） --------------------------
S       = 8            # トレース時の拡大率
SIZE    = 1008         # 作業カンバス
C       = SIZE / 2     # 中心
R_OUT   = 502.0        # リング外周
R_IN    = 437.0        # リング内周
R_EMB   = 432.0        # エンブレムを切り出す半径（リングより内側）
GREEN   = '#206a44'    # 元画像から採取

TEXT_JA = '訪問販売適正化推進協会'
TEXT_EN = 'JAPAN SALES OVERSIGHT ASSOCIATION'
FS_JA, LS_JA = 52, 6       # 日本語の級数と字送り
FS_EN, LS_EN = 55, 3       # 英語の級数と字送り
R_BASE_JA = 445            # 上の弧のベースライン半径（文字は外へ伸びる）
R_BASE_EN = 494            # 下の弧のベースライン半径（文字は内へ伸びる）


def trace_emblem() -> str:
    """中央のエンブレムだけを取り出してパスにする。"""
    src = Image.open(SRC).convert('RGBA')
    bg  = Image.new('RGBA', src.size, (255, 255, 255, 255))
    bg.alpha_composite(src)
    im  = bg.convert('L').resize((src.size[0] * S, src.size[1] * S), Image.LANCZOS)
    a   = np.array(im)

    h, w = a.shape
    Y, X = np.mgrid[0:h, 0:w]
    outside = np.hypot(Y - h / 2, X - w / 2) >= R_EMB * (w / SIZE)
    a = a.copy(); a[outside] = 255          # リングから外を白（＝背景）で塗り潰す

    # potrace は白を前景として渡したときに緑側が塗りになる（座標系の都合）
    path = potrace.Bitmap(a >= 170).trace(turdsize=10, alphamax=1.0)

    k = SIZE / w                            # 作業カンバスへ縮尺
    out = []
    for curve in path:
        p = curve.start_point
        seg = [f'M{p.x*k:.2f} {p.y*k:.2f}']
        for g in curve.segments:
            if g.is_corner:
                seg.append(f'L{g.c.x*k:.2f} {g.c.y*k:.2f}'
                           f'L{g.end_point.x*k:.2f} {g.end_point.y*k:.2f}')
            else:
                seg.append(f'C{g.c1.x*k:.2f} {g.c1.y*k:.2f} '
                           f'{g.c2.x*k:.2f} {g.c2.y*k:.2f} '
                           f'{g.end_point.x*k:.2f} {g.end_point.y*k:.2f}')
        seg.append('Z')
        out.append(''.join(seg))
    return ''.join(out)


def build(white: bool = False) -> str:
    """white=False … 緑版（元画像と同じく円の内側は白、外側は透明）
       white=True  … 白版（マーク全体が白。文字は穴として抜き、背景を透かす）"""
    emblem = trace_emblem()
    ring_r = (R_OUT + R_IN) / 2
    ring_w = R_OUT - R_IN
    ink = '#fff' if white else GREEN
    # 上の弧＝時計回り（sweep 1）、下の弧＝反時計回り（sweep 0）。
    # どちらも左から右へ進むので、文字は正立する。
    arc_ja = f'M{C-R_BASE_JA} {C} A{R_BASE_JA} {R_BASE_JA} 0 0 1 {C+R_BASE_JA} {C}'
    arc_en = f'M{C-R_BASE_EN} {C} A{R_BASE_EN} {R_BASE_EN} 0 0 0 {C+R_BASE_EN} {C}'
    texts = (f'<text font-size="{FS_JA}" letter-spacing="{LS_JA}">'
             f'<textPath href="#arcJa" startOffset="50%">{TEXT_JA}</textPath></text>'
             f'<text font-size="{FS_EN}" letter-spacing="{LS_EN}">'
             f'<textPath href="#arcEn" startOffset="50%">{TEXT_EN}</textPath></text>')
    font = ('font-family="Noto Sans JP, Noto Sans CJK JP, sans-serif" '
            'font-weight="700" text-anchor="middle"')

    if white:
        # 文字を黒で描いたマスクで、リングに穴を空ける
        body = f'''  <mask id="cut">
    <rect width="{SIZE}" height="{SIZE}" fill="#fff"/>
    <g fill="#000" {font}>{texts}</g>
  </mask>
  <g mask="url(#cut)">
    <circle cx="{C}" cy="{C}" r="{ring_r}" fill="none" stroke="{ink}" stroke-width="{ring_w}"/>
    <path fill="{ink}" fill-rule="evenodd" d="{emblem}"/>
  </g>'''
    else:
        body = f'''  <circle cx="{C}" cy="{C}" r="{R_OUT}" fill="#fff"/>
  <circle cx="{C}" cy="{C}" r="{ring_r}" fill="none" stroke="{ink}" stroke-width="{ring_w}"/>
  <path fill="{ink}" fill-rule="evenodd" d="{emblem}"/>
  <g fill="#fff" {font}>{texts}</g>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">
  <title>一般社団法人訪問販売適正化推進協会（JSOA）</title>
  <defs>
    <path id="arcJa" d="{arc_ja}"/>
    <path id="arcEn" d="{arc_en}"/>
  </defs>
{body}
</svg>
'''


if __name__ == '__main__':
    for path, w in ((OUT, False), (OUT.with_name('logo-white.svg'), True)):
        path.write_text(build(w), encoding='utf-8')
        print('書き出し:', path.name, f'{path.stat().st_size//1024} KB')
