import base64
import html
import io
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler

from PIL import Image, ImageOps

try:
    from ._auth import (
        AuthError,
        add_cors_headers,
        audit,
        handle_options,
        require_admin,
        require_server_config,
        respond_auth_error,
    )
except ImportError:
    from _auth import (
        AuthError,
        add_cors_headers,
        audit,
        handle_options,
        require_admin,
        require_server_config,
        respond_auth_error,
    )


GITHUB_TOKEN = os.environ.get("CAVA_GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.environ.get("CAVA_GITHUB_REPOSITORY", "BuenasBox/cava-gourmet-site")
GITHUB_BRANCH = os.environ.get("CAVA_GITHUB_BRANCH", "master")
MAX_BODY_BYTES = 14 * 1024 * 1024
BASE_URL = "https://www.cavagourmet.com"
TEMPLATE_PATH = "journal/que-significa-cuerpo-en-el-vino.html"
Image.MAX_IMAGE_PIXELS = 40_000_000


class PublishError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class ArticleSanitizer(HTMLParser):
    allowed = {"p", "h2", "h3", "blockquote", "ul", "ol", "li", "strong", "em", "a", "br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.allowed:
            return
        if tag == "blockquote":
            self.parts.append('<p class="art-quote reveal quote-emphasis">')
            return
        if tag == "h2":
            self.parts.append('<h2 class="reveal">')
            return
        if tag == "h3":
            self.parts.append('<h3 class="reveal">')
            return
        if tag == "a":
            href = next((v for k, v in attrs if k == "href"), "")
            if not (href.startswith("/") or href.startswith("https://www.cavagourmet.com/")):
                return
            self.parts.append(f'<a href="{html.escape(href, quote=True)}">')
            return
        self.parts.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag == "blockquote":
            self.parts.append("</p>")
        elif tag in self.allowed and tag != "br":
            self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(html.escape(data))

    def get_html(self):
        return "".join(self.parts).strip()


def github_request(path, method="GET", body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"https://api.github.com/repos/{GITHUB_REPOSITORY}{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CAVA-Journal-Publisher/1.0",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 404:
            raise PublishError(404, "No se encontró el repositorio o archivo requerido")
        if exc.code in (401, 403):
            raise PublishError(503, "GitHub rechazó las credenciales de publicación")
        if exc.code in (409, 422):
            raise PublishError(409, "El sitio cambió durante la publicación; vuelve a intentarlo")
        raise PublishError(502, f"GitHub no pudo completar la publicación ({exc.code})") from exc
    except Exception as exc:
        raise PublishError(502, "No se pudo conectar con GitHub") from exc


def get_repo_text(path, ref):
    quoted = "/".join(urllib.parse.quote(part) for part in path.split("/"))
    result = github_request(f"/contents/{quoted}?ref={urllib.parse.quote(ref)}")
    return base64.b64decode(result["content"]).decode("utf-8")


def clean_text(value, limit):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return value[:limit]


def validate_payload(data):
    title = clean_text(data.get("title"), 160)
    slug = clean_text(data.get("slug"), 100)
    category = clean_text(data.get("category"), 80)
    date = clean_text(data.get("date"), 10)
    seo_title = clean_text(data.get("seoTitle"), 80)
    description = clean_text(data.get("metaDescription"), 180)
    excerpt = clean_text(data.get("excerpt"), 260)
    image_alt = clean_text(data.get("imageAlt"), 220)
    keywords = [clean_text(x, 70) for x in data.get("keywords", []) if clean_text(x, 70)][:8]
    related = [clean_text(x, 140) for x in data.get("related", []) if clean_text(x, 140)][:2]
    related_titles = [clean_text(x, 180) for x in data.get("relatedTitles", []) if clean_text(x, 180)][:2]

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise PublishError(400, "El slug solo puede contener minúsculas, números y guiones")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError as exc:
        raise PublishError(400, "La fecha de publicación no es válida") from exc
    if len(title.split()) < 4 or not category:
        raise PublishError(400, "Completa el título y la categoría")
    if not 35 <= len(seo_title) <= 70:
        raise PublishError(400, "El título SEO debe tener entre 35 y 70 caracteres")
    if not 100 <= len(description) <= 165:
        raise PublishError(400, "La meta descripción debe tener entre 100 y 165 caracteres")
    if len(excerpt) < 60:
        raise PublishError(400, "El extracto debe tener al menos 60 caracteres")
    if len(related) != 2 or len(related_titles) != 2 or related[0] == related[1]:
        raise PublishError(400, "Selecciona dos artículos relacionados diferentes")
    if any(not re.fullmatch(r"/journal/[a-z0-9]+(?:-[a-z0-9]+)*", path) for path in related):
        raise PublishError(400, "Los artículos relacionados no son válidos")

    sanitizer = ArticleSanitizer()
    sanitizer.feed(str(data.get("bodyHtml") or ""))
    body_html = sanitizer.get_html()
    plain_body = re.sub(r"<[^>]+>", " ", body_html)
    words = re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b", html.unescape(plain_body))
    if len(words) < 400:
        raise PublishError(400, f"El artículo tiene {len(words)} palabras; necesita al menos 400")
    if len(re.findall(r"<h2\b", body_html)) < 2:
        raise PublishError(400, "Agrega al menos dos subtítulos H2")
    if not re.search(r'href="/(?!journal(?:/|"))', body_html):
        raise PublishError(400, "Agrega al menos un enlace a otra página de CAVA")

    image_data = data.get("imageData") or ""
    if not image_data or not image_alt:
        raise PublishError(400, "La imagen de portada y su descripción son obligatorias")
    match = re.fullmatch(r"data:image/(?:jpeg|jpg|png|webp);base64,([A-Za-z0-9+/=]+)", image_data)
    if not match:
        raise PublishError(400, "La imagen debe ser JPG, PNG o WebP")
    try:
        image_bytes = base64.b64decode(match.group(1), validate=True)
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise PublishError(400, "No se pudo leer la imagen de portada") from exc
    if image.width * image.height > 40_000_000:
        raise PublishError(400, "La imagen es demasiado grande")
    if image.width < 1280 or image.height < 630:
        raise PublishError(400, "La imagen debe medir al menos 1280 × 630 píxeles")

    return {
        "title": title, "slug": slug, "category": category, "date": date,
        "seo_title": seo_title, "description": description, "excerpt": excerpt,
        "image_alt": image_alt, "keywords": keywords, "related": related,
        "related_titles": related_titles, "body_html": body_html, "image": image,
    }


def image_files(image, slug):
    result = {}
    for width in (640, 960, 1280):
        height = round(image.height * width / image.width)
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        resized.save(out, "WEBP", quality=84, method=6)
        result[f"Assets/images/journal/{slug}-{width}.webp"] = out.getvalue()
    og = ImageOps.fit(image, (1200, 630), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    out = io.BytesIO()
    og.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    result[f"Assets/images/journal/{slug}-og-1200x630.jpg"] = out.getvalue()
    return result


def article_schema(item):
    url = f"{BASE_URL}/journal/{item['slug']}"
    image_url = f"{BASE_URL}/Assets/images/journal/{item['slug']}-1280.webp"
    date_iso = f"{item['date']}T12:00:00-06:00"
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting", "@id": f"{url}#article", "headline": item["title"],
                "name": item["title"], "description": item["description"], "url": url,
                "datePublished": date_iso, "dateModified": date_iso, "inLanguage": "es",
                "author": {"@id": f"{BASE_URL}/nazareth#person"},
                "publisher": {"@id": f"{BASE_URL}/#organization"},
                "isPartOf": {"@id": f"{BASE_URL}/journal#journal"},
                "image": {"@type": "ImageObject", "url": image_url, "width": 1280},
                "keywords": ", ".join(item["keywords"]), "articleSection": item["category"],
            },
            {
                "@type": "BreadcrumbList", "@id": f"{url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Journal", "item": f"{BASE_URL}/journal"},
                    {"@type": "ListItem", "position": 3, "name": item["title"]},
                ],
            },
            {"@type": "Person", "@id": f"{BASE_URL}/nazareth#person", "name": "Nazareth Padilla Montero", "alternateName": "Nazareth Wine Journey", "url": f"{BASE_URL}/nazareth", "sameAs": ["https://www.instagram.com/nazarethwinejourney", "https://www.facebook.com/nazarethwinejourney", "https://www.linkedin.com/in/nazarethpm", "https://www.tiktok.com/@nazarethwinejourney", "https://www.wikidata.org/wiki/Q139959656"]},
            {"@type": "Organization", "@id": f"{BASE_URL}/#organization", "name": "CAVA Gourmet Market", "url": BASE_URL},
        ],
    }
    return json.dumps(graph, ensure_ascii=False, indent=2)


def replace_once(text, pattern, replacement, label, flags=re.S):
    updated, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=flags)
    if count != 1:
        raise PublishError(500, f"No se pudo actualizar {label}")
    return updated


def build_article(template, item):
    esc = lambda value: html.escape(value, quote=True)
    slug = item["slug"]
    date_iso = f"{item['date']}T12:00:00-06:00"
    month = datetime.strptime(item["date"], "%Y-%m-%d").strftime("%B %Y")
    months = {"January":"Enero","February":"Febrero","March":"Marzo","April":"Abril","May":"Mayo","June":"Junio","July":"Julio","August":"Agosto","September":"Septiembre","October":"Octubre","November":"Noviembre","December":"Diciembre"}
    for en, es in months.items():
        month = month.replace(en, es)
    image_base = f"../Assets/images/journal/{slug}"
    url = f"{BASE_URL}/journal/{slug}"

    text = replace_once(template, r"<title>.*?</title>", f"<title>{esc(item['seo_title'])}</title>", "title")
    text = replace_once(text, r'<meta name="description"\s+content=".*?"\s*/>', f'<meta name="description" content="{esc(item["description"])}" />', "meta descripción")
    text = replace_once(text, r'<meta name="keywords"\s+content=".*?"\s*/>', f'<meta name="keywords" content="{esc(", ".join(item["keywords"]))}" />', "keywords")
    text = replace_once(text, r'<link rel="canonical" href=".*?"\s*/>', f'<link rel="canonical" href="{url}" />', "canonical")
    og = f'''<!-- Open Graph -->
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="CAVA Gourmet Market" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{esc(item['title'])}" />
  <meta property="og:description" content="{esc(item['description'])}" />
  <meta property="og:image" content="{BASE_URL}/Assets/images/journal/{slug}-og-1200x630.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{esc(item['image_alt'])}" />
  <meta property="og:locale" content="es_CR" />
  <meta property="article:author" content="{BASE_URL}/nazareth#person" />
  <meta property="article:section" content="{esc(item['category'])}" />
  <meta property="article:published_time" content="{date_iso}" />
  <meta property="article:modified_time" content="{date_iso}" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(item['title'])}" />
  <meta name="twitter:description" content="{esc(item['description'])}" />
  <meta name="twitter:image" content="{BASE_URL}/Assets/images/journal/{slug}-og-1200x630.jpg" />'''
    text = replace_once(text, r"<!-- Open Graph -->.*?(?=\n\s*<meta name=\"geo.region\")", og, "Open Graph")
    schema = f'<script type="application/ld+json">\n{article_schema(item)}\n  </script>'
    text = replace_once(text, r'<script type="application/ld\+json">.*?</script>', schema, "schema")
    preload = f'''<link rel="preload" as="image"
    href="{image_base}-1280.webp"
    imagesrcset="{image_base}-640.webp 640w, {image_base}-960.webp 960w, {image_base}-1280.webp 1280w"
    imagesizes="100vw">'''
    text = replace_once(text, r'<link rel="preload" as="image".*?>', preload, "preload")
    header = f'''<header class="art-header">
      <div class="wrap">
        <p class="art-cat">{esc(item['category'])}</p>
        <h1>{esc(item['title'])}</h1>
        <div class="art-meta">
          <div class="naz-thumb"><img src="../Assets/images/professional/06-nazareth-wine-journey-wset-960.webp" alt="Nazareth Padilla Montero" width="44" height="44" loading="eager"></div>
          <div class="art-meta-info"><strong>Nazareth Padilla Montero</strong>Comunicadora del vino · {month}</div>
        </div>
      </div>
    </header>'''
    text = replace_once(text, r'<header class="art-header">.*?</header>', header, "encabezado")
    cover = f'''<figure class="art-cover">
      <picture>
        <source type="image/webp" srcset="{image_base}-640.webp 640w, {image_base}-960.webp 960w, {image_base}-1280.webp 1280w" sizes="100vw">
        <img src="{image_base}-1280.webp" alt="{esc(item['image_alt'])}" width="1280" loading="eager" fetchpriority="high" decoding="async">
      </picture>
    </figure>'''
    text = replace_once(text, r'<figure class="art-cover">.*?</figure>', cover, "portada")
    breadcrumb = f'''<nav class="art-breadcrumb" aria-label="Breadcrumb"><div class="art-breadcrumb-inner">
        <a href="/">Inicio</a><span aria-hidden="true">/</span><a href="/journal">Journal</a><span aria-hidden="true">/</span><span aria-current="page">{esc(item['title'])}</span>
      </div></nav>'''
    text = replace_once(text, r'<nav class="art-breadcrumb".*?</nav>', breadcrumb, "breadcrumb")
    article = f'<article class="art-prose" id="articulo">\n{item["body_html"]}\n      </article>'
    text = replace_once(text, r'<article class="art-prose" id="articulo">.*?</article>', article, "contenido")
    related = f'''<nav class="art-footnav" aria-label="Más artículos"><div class="art-footnav-inner">
        <a href="/journal" class="art-back">Volver al journal</a><div class="art-more"><span class="art-more-label">Más artículos</span>
          <a href="{esc(item['related'][0])}" class="art-more-link">{esc(item['related_titles'][0])}</a>
          <a href="{esc(item['related'][1])}" class="art-more-link">{esc(item['related_titles'][1])}</a>
        </div></div></nav>'''
    return replace_once(text, r'<nav class="art-footnav".*?</nav>', related, "artículos relacionados")


def update_journal(text, item):
    slug, title = item["slug"], html.escape(item["title"])
    schema_id = f'          {{ "@id": "{BASE_URL}/journal/{slug}#article" }},\n'
    text, count = re.subn(r'("blogPost": \[\s*\n)', lambda match: match.group(1) + schema_id, text, count=1)
    if count != 1:
        raise PublishError(500, "No se pudo actualizar schema del Journal")
    date_label = datetime.strptime(item["date"], "%Y-%m-%d").strftime("%B %Y")
    for en, es in {"January":"Enero","February":"Febrero","March":"Marzo","April":"Abril","May":"Mayo","June":"Junio","July":"Julio","August":"Agosto","September":"Septiembre","October":"Octubre","November":"Noviembre","December":"Diciembre"}.items():
        date_label = date_label.replace(en, es)
    card = f'''          <!-- Publicado desde el editor del Journal -->
          <article class="blog-card reveal" role="listitem">
            <a href="/journal/{slug}" class="blog-card-img" aria-label="Leer: {title}">
              <img src="Assets/images/journal/{slug}-640.webp" srcset="Assets/images/journal/{slug}-640.webp 640w, Assets/images/journal/{slug}-960.webp 960w" sizes="(max-width: 600px) 90vw, (max-width: 960px) 45vw, 380px" alt="{html.escape(item['image_alt'])}" width="960" loading="lazy" decoding="async">
            </a>
            <div class="blog-card-body"><p class="blog-card-cat">{html.escape(item['category'])}</p><h3 class="blog-card-title"><a href="/journal/{slug}">{title}</a></h3>
              <p class="blog-card-excerpt">{html.escape(item['excerpt'])}</p><div class="blog-card-footer"><span class="blog-card-date">{date_label}</span><a href="/journal/{slug}" class="blog-card-link" aria-label="Leer artículo: {title}">Leer</a></div>
            </div>
          </article>

'''
    text, count = re.subn(r'(<div class="blog-grid" role="list">\s*\n)', lambda match: match.group(1) + "\n" + card, text, count=1)
    if count != 1:
        raise PublishError(500, "No se pudo agregar la tarjeta del Journal")
    return text


def update_sitemap(text, item):
    block = f'''  <url>
    <loc>{BASE_URL}/journal/{item['slug']}</loc>
    <lastmod>{item['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
    <image:image><image:loc>{BASE_URL}/Assets/images/journal/{item['slug']}-1280.webp</image:loc><image:title>{html.escape(item['title'])}</image:title><image:caption>{html.escape(item['image_alt'])}</image:caption></image:image>
  </url>

'''
    return text.replace("</urlset>", block + "</urlset>")


def update_feed(text, item):
    data = json.loads(text)
    entry = {"id": f"{BASE_URL}/journal/{item['slug']}", "url": f"{BASE_URL}/journal/{item['slug']}", "title": item["title"], "summary": item["description"], "date_published": f"{item['date']}T12:00:00-06:00", "author": {"name": "Nazareth Padilla Montero", "url": f"{BASE_URL}/nazareth"}, "tags": item["keywords"]}
    data["items"].insert(0, entry)
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def update_pages(text, item):
    data = json.loads(text)
    next_id = max(page.get("id", 0) for page in data["pages"]) + 1
    data["pages"].append({"id": next_id, "hub": "journal", "slug": f"/journal/{item['slug']}", "title": item["title"], "status": "publicado", "canal": ["sitio"]})
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def update_llms(text, item):
    line = f'- [{item["title"]}]({BASE_URL}/journal/{item["slug"]}): {item["excerpt"]}\n'
    text, count = re.subn(r'(## Artículos del Journal\s*\n)', lambda match: match.group(1) + "\n" + line, text, count=1)
    if count != 1:
        raise PublishError(500, "No se pudo actualizar llms.txt")
    return text


def update_registry(text, item):
    numbers = [int(x) for x in re.findall(r"### ART-(\d+)", text)]
    number = max(numbers or [0]) + 1
    text = re.sub(r"Artículos publicados: \d+", f"Artículos publicados: {number}", text, count=1)
    section = f'''### ART-{number:03d} · {item['title']}

| Campo | Valor |
|---|---|
| **Slug** | `/journal/{item['slug']}` |
| **Título completo** | {item['title']} |
| **Fecha publicación** | {item['date']} |
| **Fecha última edición** | {item['date']} |
| **Tipo** | Artículo editorial publicado desde el editor CAVA |
| **Cluster temático** | {item['category']} |
| **Keywords primarias** | {', '.join(item['keywords'])} |
| **Entidad reforzada** | Nazareth Padilla Montero · CAVA Vinoteca · Pérez Zeledón |
| **Artículos relacionados** | {' · '.join(item['related'])} |
| **Imagen** | `Assets/images/journal/{item['slug']}-1280.webp` |
| **Status** | Publicado ✅ |

---

'''
    return text.replace("## Artículos en evaluación / pendientes", section + "## Artículos en evaluación / pendientes")


def create_commit(files, parent_sha, base_tree_sha, actor_email, title):
    tree_entries = []
    for path, content in files.items():
        raw = content.encode("utf-8") if isinstance(content, str) else content
        blob = github_request("/git/blobs", "POST", {"content": base64.b64encode(raw).decode("ascii"), "encoding": "base64"})
        tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    tree = github_request("/git/trees", "POST", {"base_tree": base_tree_sha, "tree": tree_entries})
    commit = github_request("/git/commits", "POST", {"message": f"publish(journal): {title}", "tree": tree["sha"], "parents": [parent_sha], "author": {"name": "Nazareth Padilla Montero", "email": actor_email or "nazareth@cavagourmet.com"}})
    github_request(f"/git/refs/heads/{urllib.parse.quote(GITHUB_BRANCH)}", "PATCH", {"sha": commit["sha"], "force": False})
    return commit


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            require_server_config(GITHUB_TOKEN=GITHUB_TOKEN)
            require_admin(self)
            ref = github_request(f"/git/ref/heads/{urllib.parse.quote(GITHUB_BRANCH)}")
            feed = json.loads(get_repo_text("feed.json", ref["object"]["sha"]))
            articles = [{"url": urllib.parse.urlparse(x["url"]).path, "title": x["title"]} for x in feed.get("items", [])]
            self._json(200, {"ok": True, "articles": articles, "branch": GITHUB_BRANCH})
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, POST, OPTIONS")
        except PublishError as exc:
            self._json(exc.status, {"ok": False, "error": exc.message})

    def do_POST(self):
        ctx = None
        try:
            require_server_config(GITHUB_TOKEN=GITHUB_TOKEN)
            ctx = require_admin(self)
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                raise PublishError(413, "La publicación supera el tamaño permitido")
            data = json.loads(self.rfile.read(length))
            item = validate_payload(data)

            ref = github_request(f"/git/ref/heads/{urllib.parse.quote(GITHUB_BRANCH)}")
            parent_sha = ref["object"]["sha"]
            if data.get("preview") is True:
                template = get_repo_text(TEMPLATE_PATH, parent_sha)
                preview_html = build_article(template, item)
                self._json(200, {"ok": True, "html": preview_html})
                return
            parent = github_request(f"/git/commits/{parent_sha}")
            article_path = f"journal/{item['slug']}.html"
            try:
                get_repo_text(article_path, parent_sha)
                raise PublishError(409, "Ya existe un artículo con ese slug")
            except PublishError as exc:
                if exc.status != 404:
                    raise

            needed = [TEMPLATE_PATH, "journal.html", "sitemap.xml", "feed.json", "llms.txt", "data/pages.json", "JOURNAL-REGISTRY.md"]
            current = {path: get_repo_text(path, parent_sha) for path in needed}
            files = {
                article_path: build_article(current[TEMPLATE_PATH], item),
                "journal.html": update_journal(current["journal.html"], item),
                "sitemap.xml": update_sitemap(current["sitemap.xml"], item),
                "feed.json": update_feed(current["feed.json"], item),
                "llms.txt": update_llms(current["llms.txt"], item),
                "data/pages.json": update_pages(current["data/pages.json"], item),
                "JOURNAL-REGISTRY.md": update_registry(current["JOURNAL-REGISTRY.md"], item),
            }
            files.update(image_files(item.pop("image"), item["slug"]))
            profile = (ctx or {}).get("profile") or {}
            commit = create_commit(files, parent_sha, parent["tree"]["sha"], profile.get("email"), item["title"])
            audit(self, ctx, result="ok", action="journal.publish", object_type="journal_article", object_id=item["slug"])
            self._json(201, {"ok": True, "url": f"{BASE_URL}/journal/{item['slug']}", "commit": commit.get("html_url"), "files": len(files)})
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, POST, OPTIONS")
        except PublishError as exc:
            if ctx:
                audit(self, ctx, result="error", action="journal.publish", object_type="journal_article")
            self._json(exc.status, {"ok": False, "error": exc.message})
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"ok": False, "error": "Solicitud inválida"})
        except Exception:
            self._json(500, {"ok": False, "error": "No se pudo completar la publicación"})

    def do_OPTIONS(self):
        handle_options(self, methods="GET, POST, OPTIONS")

    def _json(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        add_cors_headers(self, methods="GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def log_message(self, *args):
        pass
