#!/usr/bin/env python3
"""prompr mood board builder: search free image sources, download small previews, curate, assemble.

Search is cheap; generation is not. This script finds reference images on the web so a board
costs no image-generation credits. Every image keeps its source link so the team can trace it.
Mood boards are for internal reference only; the user is responsible for how images are used.

Two ways to get images:
  1. add      No key needed. The agent runs its own web search, picks visual pages (articles,
              portfolios, Pinterest, Behance, Are.na, brand sites) and passes their URLs here.
              The script pulls each page's preview image (og:image), or the image itself if the
              URL is a direct image link.
  2. search   Keyed image search APIs, used when set (in this order):
                brave      BRAVE_API_KEY            (general web image search)
                google     GOOGLE_CSE_KEY + GOOGLE_CSE_ID (Programmable Search, image mode)
                pexels     PEXELS_API_KEY           (photography)
                unsplash   UNSPLASH_ACCESS_KEY      (photography)
              Opt-in archives with no key, via --sources: openverse, wikimedia
              (good for art history, eras, places and materials; weak for mood).

Usage:
  python3 moodboard.py add OUT_DIR "<Board name>" URL [URL ...] [--line "one-line feel"] [--keywords "a, b, c"]
      Adds images from web pages or direct image links to a board (creates it if new),
      then rebuilds its numbered contact sheet.

  python3 moodboard.py search plan.json OUT_DIR [--per 6] [--sources brave,pexels,wikimedia]
      plan.json: {"boards": [{"name": "Sunlit Stillness", "keywords": ["..."], "queries": ["..."]}]}
      Downloads candidates to OUT_DIR/<board>/cand/, writes manifest.json and a numbered
      contact sheet per board (OUT_DIR/<board>/contact.jpg) to review in one look.

  python3 moodboard.py keep OUT_DIR <board-slug> 1,4,7,9 [...]
      Keeps those candidate numbers, copies them to OUT_DIR/<board>/kept/, extracts a palette.

  python3 moodboard.py html OUT_DIR
      Writes OUT_DIR/boards.html: every board with kept images, palette, keywords and credits.

Requires Python 3.9+ and Pillow.
"""
import html, io, json, os, re, shutil, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

UA = "prompr-moodboard/0.1 (+https://github.com/daibot/prompr)"
THUMB_W = 640


# ---------------------------------------------------------------- http
def curl(url, h, timeout):
    """Fallback for hosts the bundled Python TLS cannot reach (old LibreSSL builds)."""
    cmd = ["curl", "-sSfL", "--max-time", str(timeout), "--max-filesize", "15000000"]
    for k, v in h.items():
        cmd += ["-H", "%s: %s" % (k, v)]
    return subprocess.run(cmd + [url], capture_output=True, check=True).stdout


def get(url, headers=None, tries=2, timeout=20):
    h = {"User-Agent": UA}
    h.update(headers or {})
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404, 410, 429):  # blocked or gone: respect it, do not retry
                raise
            last = e
        except Exception as e:  # TLS, network errors, timeouts
            last = e
            if "SSL" in str(e) or "TLS" in str(e):
                try:
                    return curl(url, h, timeout)
                except Exception as e2:
                    last = e2
        time.sleep(1.5 * (i + 1))
    raise last


def get_json(url, headers=None):
    return json.loads(get(url, headers))


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


# ---------------------------------------------------------------- providers
class NoKey(Exception):
    pass


def brave(q, n):
    key = os.environ.get("BRAVE_API_KEY")
    if not key:
        raise NoKey()
    d = get_json("https://api.search.brave.com/res/v1/images/search?" + urllib.parse.urlencode({"q": q, "count": min(n, 50), "safesearch": "strict"}),
                 {"X-Subscription-Token": key, "Accept": "application/json"})
    return [{"provider": "brave", "thumb": (r.get("properties") or {}).get("url") or (r.get("thumbnail") or {}).get("src"),
             "creator": r.get("source", ""), "license": "web", "license_url": "", "source_url": r.get("url", ""),
             "title": r.get("title", "")} for r in d.get("results", [])]


def google(q, n):
    key, cx = os.environ.get("GOOGLE_CSE_KEY"), os.environ.get("GOOGLE_CSE_ID")
    if not (key and cx):
        raise NoKey()
    d = get_json("https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode({"key": key, "cx": cx, "q": q, "searchType": "image", "num": min(n, 10), "safe": "active"}))
    return [{"provider": "google", "thumb": it.get("link"), "creator": it.get("displayLink", ""), "license": "web", "license_url": "",
             "source_url": (it.get("image") or {}).get("contextLink") or it.get("link"), "title": it.get("title", "")} for it in d.get("items", [])]


def pexels(q, n):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        raise NoKey()
    d = get_json("https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": q, "per_page": n}), {"Authorization": key})
    return [{"provider": "pexels", "thumb": p["src"]["medium"], "creator": p.get("photographer", ""),
             "license": "Pexels License", "license_url": "https://www.pexels.com/license/",
             "source_url": p["url"], "title": p.get("alt") or ""} for p in d.get("photos", [])]


def unsplash(q, n):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        raise NoKey()
    d = get_json("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode({"query": q, "per_page": n}),
                 {"Authorization": "Client-ID " + key, "Accept-Version": "v1"})
    out = []
    for p in d.get("results", []):
        out.append({"provider": "unsplash", "thumb": p["urls"]["small"], "creator": p["user"]["name"],
                    "license": "Unsplash License", "license_url": "https://unsplash.com/license",
                    "source_url": p["links"]["html"] + "?utm_source=prompr&utm_medium=referral",
                    "title": p.get("alt_description") or "", "_ping": p["links"].get("download_location"), "_key": key})
    return out


def openverse(q, n):
    d = get_json("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q, "page_size": n, "mature": "false"}))
    return [{"provider": "openverse/" + r.get("provider", ""), "thumb": r.get("thumbnail") or r["url"], "creator": r.get("creator") or "",
             "license": ("CC " + r.get("license", "").upper() + " " + (r.get("license_version") or "")).strip(),
             "license_url": r.get("license_url") or "", "source_url": r.get("foreign_landing_url") or r["url"],
             "title": r.get("title") or ""} for r in d.get("results", [])]


def wikimedia(q, n):
    params = {"action": "query", "generator": "search", "gsrsearch": "filetype:bitmap " + q, "gsrnamespace": 6,
              "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": THUMB_W, "format": "json"}
    d = get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params))
    out = []
    for p in (d.get("query") or {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata") or {}
        out.append({"provider": "wikimedia", "thumb": ii.get("thumburl") or ii.get("url"),
                    "creator": strip_tags((md.get("Artist") or {}).get("value")),
                    "license": (md.get("LicenseShortName") or {}).get("value", ""),
                    "license_url": (md.get("LicenseUrl") or {}).get("value", ""),
                    "source_url": ii.get("descriptionurl", ""), "title": p.get("title", "").replace("File:", "")})
    return out


KEYED = [brave, google, pexels, unsplash]
ARCHIVES = {"openverse": openverse, "wikimedia": wikimedia}
ALL = {f.__name__: f for f in KEYED + list(ARCHIVES.values())}


# ---------------------------------------------------------------- images
def ahash(img):
    g = img.convert("L").resize((8, 8), Image.LANCZOS)
    px = list(g.getdata())
    avg = sum(px) / 64
    return sum(1 << i for i, v in enumerate(px) if v > avg)


def palette(images, k=6):
    strip = Image.new("RGB", (64 * len(images), 64))
    for i, im in enumerate(images):
        strip.paste(im.convert("RGB").resize((64, 64)), (64 * i, 0))
    q = strip.quantize(colors=k, method=Image.MEDIANCUT)
    pal = q.getpalette()[: 3 * k]
    counts = sorted(q.getcolors(), reverse=True)
    cols = [tuple(pal[3 * idx: 3 * idx + 3]) for _, idx in counts]
    cols.sort(key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2], reverse=True)
    return ["#%02X%02X%02X" % c for c in cols]


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def contact_sheet(files, out, cols=6, cell=220):
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * cell), (245, 243, 238))
    d = ImageDraw.Draw(sheet)
    f = font(22)
    for i, fp in enumerate(files):
        im = Image.open(fp).convert("RGB")
        im.thumbnail((cell - 8, cell - 8))
        x, y = (i % cols) * cell, (i // cols) * cell
        sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        d.rectangle([x + 4, y + 4, x + 40, y + 32], fill=(20, 20, 19))
        d.text((x + 9, y + 6), str(i + 1), fill=(255, 255, 255), font=f)
    sheet.save(out, quality=82)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ---------------------------------------------------------------- commands
def load_manifest(out):
    mp = out / "manifest.json"
    return json.loads(mp.read_text()) if mp.exists() else {"boards": {}}


def save_manifest(out, m):
    (out / "manifest.json").write_text(json.dumps(m, indent=1))


def board_entry(m, name, **kw):
    bs = slug(name)
    b = m["boards"].setdefault(bs, {"name": name, "keywords": [], "line": "", "queries": [], "candidates": [], "kept": [], "palette": []})
    for k, v in kw.items():
        if v:
            b[k] = v
    return bs, b


def add_candidate(out, bs, b, r, img_bytes=None):
    """Download, filter and store one candidate. Returns True if added."""
    seen_url = {c["source_url"] for c in b["candidates"]}
    if not r.get("thumb") or (r.get("source_url") and r["source_url"] in seen_url):
        return False
    try:
        im = Image.open(io.BytesIO(img_bytes or get(r["thumb"]))).convert("RGB")
    except Exception:
        return False
    if min(im.size) < 160:
        return False
    h = ahash(im)
    if any(bin(h ^ c["hash"]).count("1") <= 5 for c in b["candidates"] if "hash" in c):
        return False
    ping, key = r.pop("_ping", None), r.pop("_key", None)
    if ping:
        try:  # Unsplash API guideline: register the download
            get(ping, {"Authorization": "Client-ID " + key})
        except Exception:
            pass
    im.thumbnail((THUMB_W, THUMB_W))
    cand = out / bs / "cand"
    cand.mkdir(parents=True, exist_ok=True)
    n = max([c["n"] for c in b["candidates"]] + [0]) + 1
    fp = cand / ("%02d.jpg" % n)
    im.save(fp, quality=85)
    r.update({"n": n, "file": str(fp.relative_to(out)), "size": list(im.size), "hash": h})
    b["candidates"].append(r)
    return True


def rebuild_sheet(out, bs, b):
    if b["candidates"]:
        contact_sheet([out / c["file"] for c in b["candidates"]], out / bs / "contact.jpg")


META_IMG = re.compile(r'<meta[^>]+(?:property|name)=["\'](?:og:image(?::secure_url)?|twitter:image(?::src)?)["\'][^>]*>', re.I)
CONTENT = re.compile(r'content=["\']([^"\']+)["\']', re.I)
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def resolve(url):
    """Page or image URL -> (image bytes, image url, page title)."""
    raw = get(url, {"Accept": "text/html,image/*;q=0.9,*/*;q=0.5"}, timeout=20)
    if raw[:4] in (b"\x89PNG", b"GIF8") or raw[:2] == b"\xff\xd8" or raw[8:12] == b"WEBP":
        return raw, url, ""
    page = raw[:1500000].decode("utf-8", "ignore")
    t = TITLE.search(page)
    title = strip_tags(t.group(1))[:120] if t else ""
    for tag in META_IMG.findall(page):
        c = CONTENT.search(tag)
        if c:
            img_url = urllib.parse.urljoin(url, html.unescape(c.group(1)))
            return get(img_url), img_url, title
    raise ValueError("no preview image on page")


def cmd_add(out_dir, name, urls, line="", keywords=None):
    out = Path(out_dir)
    m = load_manifest(out)
    bs, b = board_entry(m, name, line=line, keywords=keywords)
    added, failed = 0, []
    for u in urls:
        try:
            data, img_url, title = resolve(u)
        except Exception as e:
            failed.append("%s (%s)" % (u[:70], str(e)[:40]))
            continue
        r = {"provider": "web", "thumb": img_url, "creator": urllib.parse.urlparse(u).netloc.replace("www.", ""),
             "license": "web", "license_url": "", "source_url": u, "title": title, "query": "web search"}
        if add_candidate(out, bs, b, r, data):
            added += 1
    rebuild_sheet(out, bs, b)
    save_manifest(out, m)
    print("%s: +%d (total %d) -> %s" % (b["name"], added, len(b["candidates"]), out / bs / "contact.jpg"))
    for f in failed:
        print("  skipped:", f)


def cmd_search(plan_path, out_dir, per=6, sources=None):
    plan = json.loads(Path(plan_path).read_text())
    out = Path(out_dir)
    m = load_manifest(out)
    provs = [ALL[x] for x in sources] if sources else list(KEYED)
    status = {}
    for b_plan in plan["boards"]:
        bs, b = board_entry(m, b_plan["name"], keywords=b_plan.get("keywords"), line=b_plan.get("line"))
        b["queries"] = sorted(set(b["queries"]) | set(b_plan["queries"]))
        before = len(b["candidates"])
        for q in b_plan["queries"]:
            got = 0
            for prov in provs:
                name = prov.__name__
                if got >= per or status.get(name, "").startswith(("error", "no key")):
                    continue
                try:
                    results = prov(q, per * 2)
                    status[name] = "ok"
                except NoKey:
                    status[name] = "no key"
                    continue
                except Exception as e:  # skip this source for the rest of the run
                    status[name] = "error: %s" % str(e)[:60]
                    continue
                for r in results:
                    if got >= per:
                        break
                    r["query"] = q
                    if add_candidate(out, bs, b, r):
                        got += 1
        rebuild_sheet(out, bs, b)
        print("%s: +%d candidates -> %s" % (b["name"], len(b["candidates"]) - before, out / bs / "contact.jpg"))
    save_manifest(out, m)
    print("sources:", json.dumps(status))
    if not any(v == "ok" for v in status.values()):
        print("No image search source worked. Use `add` with page URLs from a web search, "
              "set a key (BRAVE_API_KEY, GOOGLE_CSE_KEY + GOOGLE_CSE_ID, PEXELS_API_KEY, UNSPLASH_ACCESS_KEY), "
              "or pass --sources openverse,wikimedia.")


def cmd_keep(out_dir, board, ids):
    out = Path(out_dir)
    m = load_manifest(out)
    b = m["boards"][slug(board)]
    board = slug(board)
    want = [int(x) for x in re.split(r"[,\s]+", ids.strip()) if x]
    kept_dir = out / board / "kept"
    if kept_dir.exists():
        shutil.rmtree(kept_dir)
    kept_dir.mkdir(parents=True)
    by_n = {c["n"]: c for c in b["candidates"]}
    kept = []
    for i, n in enumerate(want, 1):
        c = dict(by_n[n])
        dst = kept_dir / ("%02d.jpg" % i)
        shutil.copy(out / c["file"], dst)
        c["kept_file"] = str(dst.relative_to(out))
        kept.append(c)
    b["kept"] = kept
    b["palette"] = palette([Image.open(out / c["kept_file"]) for c in kept]) if kept else []
    save_manifest(out, m)
    print("%s: kept %d, palette %s" % (b["name"], len(kept), " ".join(b["palette"])))


def cmd_html(out_dir):
    out = Path(out_dir)
    m = json.loads((out / "manifest.json").read_text())
    e = html.escape
    secs = []
    for bs, b in m["boards"].items():
        if not b["kept"]:
            continue
        imgs = "".join('<figure><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>' % (
            e(c["kept_file"]), e(c["title"][:80]),
            '%d · <a href="%s" target="_blank" rel="noopener">%s</a>%s' % (i, e(c["source_url"]), e(c["creator"][:40] or "source"),
                                                                        "" if c["license"] in ("", "web") else " · " + e(c["license"])))
            for i, c in enumerate(b["kept"], 1))
        chips = "".join('<span class="chip"><i style="background:%s"></i>%s</span>' % (h, h) for h in b["palette"])
        secs.append('<section><header><h2>%s</h2><p>%s</p><p class="kw">%s</p><div class="pal">%s</div></header><div class="grid">%s</div></section>' % (
            e(b["name"]), e(b.get("line", "")), e(" · ".join(b["keywords"])), chips, imgs))
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mood boards</title><style>
:root{--bg:#f6f4ef;--ink:#161614;--mute:#7b776f;--line:#e2ded5}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--ink:#f2efe9;--mute:#9a958c;--line:#2c2b28}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif;padding:40px 16px}
main{max-width:1280px;margin:0 auto}h1{font:400 44px/1 Georgia,serif;margin:0 0 8px}.note{color:var(--mute);margin:0 0 40px}
section{border-top:1px solid var(--line);padding:28px 0 40px}h2{font:400 32px/1.1 Georgia,serif;margin:0}
header p{margin:6px 0 0;color:var(--mute)}.kw{font-size:13px}.pal{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 18px}
.chip{display:inline-flex;align-items:center;gap:6px;font:12px ui-monospace,monospace;color:var(--mute)}.chip i{width:22px;height:22px;border-radius:4px;display:inline-block;border:1px solid var(--line)}
.grid{columns:3 240px;column-gap:12px}figure{margin:0 0 12px;break-inside:avoid}img{width:100%;display:block;border-radius:6px}
figcaption{font-size:11px;color:var(--mute);padding-top:4px}figcaption a{color:inherit}
</style></head><body><main><h1>Mood boards</h1><p class="note">For internal reference only. Images belong to their owners and are linked to their sources. You are responsible for how these images are used, including any rights or licensing needed before using them in work that is published or shared outside your team.</p>""" + "".join(secs) + "</main></body></html>"
    (out / "boards.html").write_text(page)
    print(out / "boards.html")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in ("add", "search", "keep", "html"):
        sys.exit(__doc__)
    def opt(flag):
        if flag in a:
            i = a.index(flag)
            v = a[i + 1]
            del a[i:i + 2]
            return v
        return None
    if a[0] == "add":
        line, kw = opt("--line"), opt("--keywords")
        cmd_add(a[1], a[2], a[3:], line or "", [k.strip() for k in kw.split(",")] if kw else None)
    elif a[0] == "search":
        per = int(a[a.index("--per") + 1]) if "--per" in a else 6
        src = a[a.index("--sources") + 1].split(",") if "--sources" in a else None
        cmd_search(a[1], a[2], per, src)
    elif a[0] == "keep":
        cmd_keep(a[1], a[2], " ".join(a[3:]))
    else:
        cmd_html(a[1])
