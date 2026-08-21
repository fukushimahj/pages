#!/usr/bin/env python3
"""arXiv の論文から図を取得して docs/img/feature/ に置くためのスクリプト.

トップページ (docs/index.md) の「特集」欄に載せる図を差し替えるときに使う。
標準ライブラリのみで動作する (Python 3.8+)。

使い方
------
# 1. その論文にどんな図があるか一覧する（画像 URL も表示される）
python3 tools/feature_fig.py --id 2604.21438 --list

# 2. 図 3 を取得して docs/img/feature/sfumato_fig3.png として保存する
python3 tools/feature_fig.py --id 2604.21438 --fig 3 --name sfumato_fig3

# 3. 貼り付け用の HTML スニペットも一緒に出す
python3 tools/feature_fig.py --id 2604.21438 --fig 3 --name sfumato_fig3 --snippet

# 4. 画像 URL が分かっているなら直接指定してもよい
python3 tools/feature_fig.py --url https://arxiv.org/html/2604.21438v1/x3.png --name sfumato_fig3

arXiv の HTML 版 (https://arxiv.org/html/<id>) を見に行くので、
HTML 版が用意されていない古い論文では取得できない。その場合は
--eprint を付けると投稿ソース (tar.gz) の中身を一覧できるので、
図のファイルを自分で取り出して docs/img/feature/ に置く。

うまくいかないときは --debug を付けると、解決したベース URL・
HTML 内の生の src・実際に叩いた URL がすべて表示される。
"""

from __future__ import annotations

import argparse
import html
import io
import os
import re
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional, Tuple

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT_DIR = os.path.join(REPO_ROOT, "docs", "img", "feature")

DEBUG = False


def log(*args) -> None:
    if DEBUG:
        print("[debug]", *args, file=sys.stderr)


# ----------------------------------------------------------------- helpers
def fetch(url: str, timeout: int = 60, referer: Optional[str] = None) -> Tuple[bytes, str]:
    """URL を取得して (中身, 最終的な URL) を返す."""
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    log("GET", url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.geturl()


def strip_tags(fragment: str) -> str:
    """HTML 断片からテキストだけ抜き出す (キャプション用の雑な処理)."""
    # MathML は annotation の TeX 表記があればそれを使う
    fragment = re.sub(
        r"<math\b[^>]*>.*?<annotation[^>]*>(.*?)</annotation>.*?</math>",
        lambda m: " $" + html.unescape(m.group(1)).strip() + "$ ",
        fragment,
        flags=re.S | re.I,
    )
    fragment = re.sub(r"<math\b[^>]*>.*?</math>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    text = html.unescape(fragment)
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------- arXiv HTML
def resolve_html_page(arxiv_id: str) -> Tuple[str, str]:
    """HTML 版を取得して (ページ本文, ベース URL) を返す.

    ベース URL は必ず末尾 '/' 付きで返す。ここを間違えると
    'x3.png' が https://arxiv.org/html/x3.png に化けて 404 になる。
    """
    tried: List[str] = []
    candidates = ["https://arxiv.org/html/{}".format(arxiv_id)]
    if not re.search(r"v\d+$", arxiv_id):
        # リダイレクトが効かない場合に備えてバージョン付きも試す
        candidates += ["https://arxiv.org/html/{}v{}".format(arxiv_id, v) for v in range(1, 6)]

    for url in candidates:
        tried.append(url)
        try:
            body, final = fetch(url)
        except urllib.error.HTTPError as exc:
            log("  ->", exc.code, url)
            continue
        except urllib.error.URLError as exc:
            raise SystemExit("ネットワークに繋がりませんでした: {}".format(exc))

        page = body.decode("utf-8", "replace")
        base = final

        # <base href="..."> があればそれを優先
        m = re.search(r"<base\b[^>]*\bhref=[\"']([^\"']+)[\"']", page, flags=re.I)
        if m:
            base = urllib.parse.urljoin(final, m.group(1))
            log("base tag:", base)

        # ページ内にバージョン付き URL があればそちらを採用（未バージョンの
        # ベースだと画像だけ 404 になることがあるため）
        if not re.search(r"v\d+/?$", base.rstrip("/") + "/"):
            m = re.search(r"/html/({}v\d+)".format(re.escape(arxiv_id)), page)
            if m:
                base = "https://arxiv.org/html/{}".format(m.group(1))
                log("version from page:", base)

        if not base.endswith("/"):
            base += "/"
        log("resolved base:", base)
        return page, base

    raise SystemExit(
        "arXiv の HTML 版を取得できませんでした。\n  試した URL: {}\n"
        "HTML 版が無い論文かもしれません。--eprint で投稿ソースを一覧してください。".format(
            ", ".join(tried)
        )
    )


def parse_figures(page: str, base_url: str) -> List[dict]:
    """<figure> ブロックを順に拾って [{n, src, raw, caption}, ...] を返す."""
    figures: List[dict] = []
    for block in re.findall(r"<figure\b.*?</figure>", page, flags=re.S | re.I):
        img = re.search(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", block, flags=re.I)
        if not img:
            continue
        cap = re.search(r"<figcaption\b[^>]*>(.*?)</figcaption>", block, flags=re.S | re.I)
        caption = strip_tags(cap.group(1)) if cap else ""
        raw = html.unescape(img.group(1))
        figures.append(
            {
                "n": len(figures) + 1,
                "raw": raw,
                "src": urllib.parse.urljoin(base_url, raw),
                "caption": caption,
            }
        )
    return figures


def candidate_urls(base_url: str, raw_src: str) -> List[str]:
    """画像 URL の候補を、確からしい順に並べて返す."""
    urls = [urllib.parse.urljoin(base_url, raw_src)]

    # ベースにバージョンが無い / ある場合の入れ替えを試す
    m = re.match(r"(https://arxiv\.org/html/)([^/]+?)(v\d+)?/$", base_url)
    if m:
        prefix, ident = m.group(1), m.group(2)
        variants = ["{}{}/".format(prefix, ident)]
        variants += ["{}{}v{}/".format(prefix, ident, v) for v in range(1, 6)]
        for var in variants:
            u = urllib.parse.urljoin(var, raw_src)
            if u not in urls:
                urls.append(u)
    return urls


def download_figure(base_url: str, raw_src: str, timeout: int = 120) -> Tuple[bytes, str]:
    """候補 URL を順に試して画像を落とす."""
    errors: List[str] = []
    for url in candidate_urls(base_url, raw_src):
        try:
            data, _ = fetch(url, timeout=timeout, referer=base_url)
            if not data:
                errors.append("{} -> 空のレスポンス".format(url))
                continue
            return data, url
        except urllib.error.HTTPError as exc:
            errors.append("{} -> HTTP {}".format(url, exc.code))
        except urllib.error.URLError as exc:
            errors.append("{} -> {}".format(url, exc))
    raise SystemExit(
        "画像を取得できませんでした。試した URL:\n  "
        + "\n  ".join(errors)
        + "\n\n--list で実際の画像 URL を確認するか、--debug を付けて再実行してください。"
    )


# ----------------------------------------------------------------- eprint
def list_eprint(arxiv_id: str) -> None:
    """投稿ソース (tar.gz) の中身を一覧する."""
    url = "https://arxiv.org/e-print/{}".format(arxiv_id)
    data, _ = fetch(url, timeout=120)
    try:
        tar = tarfile.open(fileobj=io.BytesIO(data))
    except tarfile.TarError:
        raise SystemExit("投稿ソースが tar.gz ではありませんでした ({} bytes)".format(len(data)))
    exts = (".pdf", ".eps", ".png", ".jpg", ".jpeg")
    print("# 投稿ソース内の図ファイル: {}".format(url))
    with tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.lower().endswith(exts):
                print("  {:>10,} B  {}".format(member.size, member.name))
    print("\n取り出したいファイルがあれば:")
    print("  curl -sL {} -o src.tar.gz && tar xzf src.tar.gz <ファイル名>".format(url))
    print("PDF/EPS は PNG に変換してから置く (例: pdftoppm -png -r 150 fig3.pdf fig3)")


# ------------------------------------------------------------------- main
def emit_snippet(arxiv_id: str, n: int, rel_path: str, caption: str) -> None:
    print("\n" + "=" * 72)
    print("docs/index.md の feature-box に貼り付ける HTML (キャプションは適宜和訳・要約):")
    print("=" * 72)
    print(
        """<figure class="feature-figure">
  <img src="{rel}"
       alt="arXiv:{aid} Figure {n}"
       onerror="this.style.display='none';var f=document.getElementById('feature-fig-fallback');if(f)f.style.display='block';">
  <div id="feature-fig-fallback" class="feature-fig-fallback" style="display:none;">
    図が未取得です。<code>python3 tools/feature_fig.py --id {aid} --fig {n}</code> を実行してください。
  </div>
  <figcaption>
    {cap}
    <span class="feature-credit">arXiv:{aid} Fig. {n}</span>
  </figcaption>
</figure>""".format(rel=rel_path, aid=arxiv_id, n=n, cap=html.escape(caption))
    )


def save(data: bytes, out_dir: str, stem: str, src_url: str) -> str:
    ext = os.path.splitext(urllib.parse.urlparse(src_url).path)[1].lower() or ".png"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, stem + ext)
    with open(dest, "wb") as fh:
        fh.write(data)
    return dest


def report(dest: str, size: int) -> str:
    rel_repo = os.path.relpath(dest, REPO_ROOT)
    rel_site = os.path.relpath(dest, os.path.join(REPO_ROOT, "docs")).replace(os.sep, "/")
    print("保存しました: {} ({:,} bytes)".format(rel_repo, size))
    print("index.md からの参照パス: {}".format(rel_site))
    return rel_site


def main(argv: Optional[List[str]] = None) -> int:
    global DEBUG
    p = argparse.ArgumentParser(description="arXiv から特集用の図を取得する")
    p.add_argument("--id", help="arXiv ID (例: 2604.21438 / 2604.21438v1)")
    p.add_argument("--fig", type=int, help="取得する図番号 (1 始まり)")
    p.add_argument("--url", help="画像 URL を直接指定する (--id の代わり)")
    p.add_argument("--list", action="store_true", help="図の一覧だけ表示する")
    p.add_argument("--eprint", action="store_true", help="投稿ソース (tar.gz) の図ファイルを一覧する")
    p.add_argument("--name", help="保存名 (拡張子なし). 既定は arxiv<id>_fig<N>")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="保存先ディレクトリ")
    p.add_argument("--snippet", action="store_true", help="index.md 貼り付け用 HTML も出力する")
    p.add_argument("--debug", action="store_true", help="解決した URL などを表示する")
    args = p.parse_args(argv)
    DEBUG = args.debug

    if args.url:
        stem = args.name or "feature_fig"
        data, _ = fetch(args.url, timeout=120, referer="https://arxiv.org/")
        dest = save(data, args.out_dir, stem, args.url)
        report(dest, len(data))
        return 0

    if not args.id:
        p.error("--id か --url のどちらかが必要です")

    if args.eprint:
        list_eprint(args.id)
        return 0

    page, base = resolve_html_page(args.id)
    figures = parse_figures(page, base)

    if not figures:
        raise SystemExit(
            "図を見つけられませんでした: {}\n--eprint で投稿ソースを確認してください。".format(base)
        )

    if args.list or args.fig is None:
        print("# {} の図一覧 ({} 枚)".format(base, len(figures)))
        for f in figures:
            cap = f["caption"]
            print("\n[{}] {}".format(f["n"], f["src"]))
            if DEBUG:
                print("    (raw src: {})".format(f["raw"]))
            print("    {}".format(cap[:300] + ("..." if len(cap) > 300 else "")))
        if args.fig is None:
            print("\n--fig <番号> を付けると保存します。")
        return 0

    match = [f for f in figures if f["n"] == args.fig]
    if not match:
        raise SystemExit("図 {} はありません (1〜{})".format(args.fig, len(figures)))
    fig = match[0]

    data, used_url = download_figure(base, fig["raw"])
    stem = args.name or "arxiv{}_fig{}".format(args.id.replace(".", "_"), fig["n"])
    dest = save(data, args.out_dir, stem, used_url)
    rel_site = report(dest, len(data))
    print("取得元: {}".format(used_url))
    print("\n--- 図 {} のキャプション (原文) ---\n{}".format(fig["n"], fig["caption"]))

    if args.snippet:
        emit_snippet(args.id, fig["n"], rel_site, fig["caption"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
