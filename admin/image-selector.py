#!/usr/bin/env python3
"""
CAVA Journal — Image Selector
==============================
Automatiza la selección de imagen para artículos nuevos del Journal.

Uso:
  python admin/image-selector.py --topic "cuerpo del vino, cata, sensacion en boca"
  python admin/image-selector.py --article journal/que-significa-cuerpo-en-el-vino.html
  python admin/image-selector.py --prompt-only --topic "maridaje, gallo pinto, comida tipica"
  python admin/image-selector.py --convert imagen.jpg --slug mi-slug --alt "descripcion"

Flujo completo:
  1. --topic para ver inventario y sugerencia
  2. Si score < --min-score, genera prompt de IA automaticamente
  3. Guardar imagen generada en Assets/images/Nazareth/nombre.jpg
  4. --convert nombre.jpg --slug nombre --alt "texto" para generar webp set

Requiere: Python 3.8+, ImageMagick (convert)
"""

import re
import argparse
import subprocess
import textwrap
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
SITE_ROOT   = Path(__file__).parent.parent
NAZARETH_DIR = SITE_ROOT / "Assets" / "images" / "Nazareth"
JOURNAL_DIR  = SITE_ROOT / "journal"
SITEMAP      = SITE_ROOT / "sitemap.xml"
IMAGE_EXTS   = {".jpg", ".jpeg", ".png", ".webp"}

# ── Mapa semántico ─────────────────────────────────────────────────────────────
SEMANTIC_MAP = {
    "analisis":    ["cuerpo","textura","sensacion","boca","evaluar","observar"],
    "copa":        ["cuerpo","cata","beber","probar","color","aroma"],
    "catando":     ["cata","cuerpo","probar","evaluar","sensacion","boca"],
    "cata":        ["probar","evaluar","experiencia","aprender","descubrir"],
    "privada":     ["experiencia","exclusivo","personal","hospitalidad"],
    "grupal":      ["evento","grupo","compartir","social","mesa"],
    "wset":        ["educacion","certificacion","experta","autoridad","conocimiento"],
    "sommelier":   ["experta","conocimiento","vino","guia","autoridad"],
    "comunicadora":["voz","cultural","editorial","perspectiva","autoridad"],
    "editorial":   ["reflexion","perspectiva","opinion","voz","journal"],
    "fundadora":   ["historia","cava","origen","nazareth","identidad"],
    "retrato":     ["perfil","identidad","fundadora","nazareth"],
    "muro":        ["vinoteca","seleccion","vino","cava","ambiente","espacio"],
    "lounge":      ["ambiente","hospitalidad","relajado","after-office","premium"],
    "interior":    ["vinoteca","espacio","ambiente","cava","lugar"],
    "market":      ["tienda","seleccion","vinoteca","vinos","cava"],
    "bodega":      ["seleccion","vino","especialidad","criterio"],
    "evento":      ["social","grupo","compartir","celebracion","experiencia"],
    "sirviendo":   ["hospitalidad","servicio","after-office","evento","copa"],
    "experiencia": ["vivencia","sensorial","humano","momento","after-office"],
    "artesanal":   ["vino","autenticidad","seleccion","pequeño-productor"],
    "blanco":      ["vino-blanco","fresco","ligero","verano","cata"],
    "tinto":       ["vino-tinto","cuerpo","tanino","robusto","cata"],
    "botella":     ["vino","seleccion","presentacion","producto"],
    "presentacion":["producto","vino","seleccion","presentar"],
    "maridaje":    ["comida","queso","charcuteria","pairing","gastronomia"],
    "quesos":      ["maridaje","charcuteria","tabla","gastronomia"],
    "frutas":      ["maridaje","tabla","fresco","gastronomia"],
    "mesa":        ["compartir","social","maridaje","experiencia","hospitalidad"],
    "tabla":       ["maridaje","gastronomia","quesos","charcuteria"],
}

# ── Escenas para generacion de prompts IA ──────────────────────────────────────
SCENE_MAP = {
    "copa":       "holding a wine glass at eye level, observing color and clarity",
    "cata":       "leading a guided wine tasting, surrounded by glasses and bottles",
    "catando":    "swirling and examining a glass of wine, focused expression",
    "analisis":   "carefully analyzing a wine glass, noting its color and viscosity",
    "maridaje":   "presenting a cheese and charcuterie board alongside wine bottles",
    "tabla":      "arranging a rustic wooden board with cheeses, fruits, and wine",
    "muro":       "standing in front of a floor-to-ceiling wine wall with hundreds of bottles",
    "bodega":     "selecting a bottle from a well-lit wine display",
    "evento":     "serving wine to guests at an intimate evening gathering",
    "sirviendo":  "pouring wine gracefully into a glass at an outdoor event",
    "after":      "relaxed evening setting, group of people sharing wine and conversation",
    "social":     "small group of people around a table, wine glasses raised",
    "editorial":  "sitting thoughtfully with a glass of wine, natural window light",
    "retrato":    "professional portrait in a warm, intimate wine shop setting",
    "exterior":   "outdoor wine moment, warm golden hour lighting",
    "lounge":     "relaxed in a softly lit lounge area with wine and ambient decor",
}


# ── Funciones de inventario ────────────────────────────────────────────────────

def get_available_images():
    images = []
    for f in NAZARETH_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            images.append(f.name)
    return sorted(images)


def get_used_images():
    used = set()
    scan_paths = [JOURNAL_DIR, SITEMAP]
    all_img_names = {img.lower() for img in get_available_images()}

    for path in scan_paths:
        files = list(path.glob("*.html")) if path.is_dir() else ([path] if path.is_file() else [])
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                # Referencias con prefijo Nazareth/
                used.update(re.findall(r'Nazareth/([^"\'>\s]+\.(?:jpg|jpeg|png|webp))', content))
                # Referencias sin prefijo (verificar que existan en la carpeta)
                for m in re.findall(r'/images/([^"\'>\s]+\.(?:jpg|jpeg|png|webp))', content):
                    base = Path(m).name
                    if base.lower() in all_img_names:
                        used.add(base)
            except Exception:
                pass
    return used


# ── Scoring ────────────────────────────────────────────────────────────────────

def tokenize(filename):
    stem = Path(filename).stem.lower()
    for prefix in ["nazareth-padilla-", "cava-gourmet-", "cava-"]:
        stem = stem.replace(prefix, "")
    return set(stem.split("-"))


def score_image(filename, topic_tokens):
    img_tokens = tokenize(filename)
    score = len(img_tokens & topic_tokens) * 3
    for tok in img_tokens:
        score += len(set(SEMANTIC_MAP.get(tok, [])) & topic_tokens)
    try:
        mb = (NAZARETH_DIR / filename).stat().st_size / (1024 * 1024)
        if mb >= 1.0:
            score += 1
        if mb < 0.2:
            score -= 2
    except Exception:
        pass
    return score


def suggest_images(topic, available, top_n=5):
    tokens = set(re.split(r"[\s,;.]+", topic.lower())) - {""}
    scored = sorted([(img, score_image(img, tokens)) for img in available],
                    key=lambda x: x[1], reverse=True)
    return scored[:top_n]


# ── Generacion de prompts IA ───────────────────────────────────────────────────

def generate_ai_prompt(topic):
    tokens = set(re.split(r"[\s,;.]+", topic.lower())) - {""}

    scene = "holding a glass of wine thoughtfully, in a warm boutique wine bar"
    for tok in tokens:
        if tok in SCENE_MAP:
            scene = SCENE_MAP[tok]
            break

    wine = "wine"
    if tokens & {"blanco", "white", "fresco", "ligero"}:
        wine = "white wine"
    elif tokens & {"tinto", "red", "cuerpo", "tanino", "robusto"}:
        wine = "red wine"

    scene = scene.replace("wine", wine)

    full = (
        f"A Costa Rican woman in her early 30s with natural, warm presence — "
        f"dark hair, approachable and confident expression, {scene}, "
        f"inside a small premium boutique wine shop in southern Costa Rica. "
        f"Dark wood shelving with neatly arranged wine bottles in the background, "
        f"warm amber and soft white lighting, intimate and relaxed atmosphere. "
        f"Photorealistic editorial photography style. Natural depth of field, "
        f"sharp subject, slightly blurred background. Warm color grading, "
        f"high-end lifestyle aesthetic. No text, no logos, no watermarks. "
        f"Aspect ratio 3:2, high resolution suitable for web hero image."
    )

    mj = (
        f"Costa Rican woman {scene}, boutique wine shop interior, "
        f"warm amber lighting, dark wood wine shelves, editorial photography, "
        f"photorealistic --ar 3:2 --style raw --q 2"
    )

    return {"full": full, "midjourney": mj, "scene": scene, "wine": wine}


def print_ai_prompt(topic, slug_suggestion=""):
    result = generate_ai_prompt(topic)
    hr = "─" * 76

    print(f"\n{hr}")
    print("  ⚠  No hay imagen disponible con relevancia suficiente → prompt de IA")
    print(f"{hr}\n")
    print(f"  Escena:  {result['scene']}")
    print(f"  Vino:    {result['wine']}\n")

    print("  DALL-E 3 / Ideogram:")
    for line in textwrap.wrap(result["full"], width=70):
        print(f"    {line}")

    print("\n  Midjourney:")
    for line in textwrap.wrap(result["midjourney"], width=70):
        print(f"    {line}")

    if slug_suggestion:
        print(f"\n  Guardar resultado como:")
        print(f"    Assets/images/Nazareth/{slug_suggestion}.jpg")
        print(f"\n  Luego generar webp:")
        print(f"    python admin/image-selector.py \\")
        print(f"      --convert {slug_suggestion}.jpg \\")
        print(f"      --slug {slug_suggestion} \\")
        print(f'      --alt "[descripcion visual]"')

    print(f"\n{hr}\n")


# ── Conversion webp ────────────────────────────────────────────────────────────

def generate_webp_set(source_jpg, output_slug, sizes=(480, 800, 1280)):
    output_dir = SITE_ROOT / "Assets" / "images" / "Nazareth"
    generated = []
    for w in sizes:
        out = output_dir / f"{output_slug}-{w}.webp"
        cmd = ["convert", str(NAZARETH_DIR / source_jpg),
               "-resize", f"{w}>", "-quality", "85",
               "-define", "webp:method=6", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            kb = out.stat().st_size // 1024
            generated.append((f"{output_slug}-{w}.webp", w, kb))
            print(f"  ✓ {output_slug}-{w}.webp — {kb} KB")
        else:
            print(f"  ✗ Error {w}px: {r.stderr.strip()}")
    return generated


def print_srcset_snippet(slug, alt_text):
    base = "/Assets/images/Nazareth"
    print(f"""
── HTML snippet ─────────────────────────────────────────────────────────────
<picture>
  <source type="image/webp"
    srcset="{base}/{slug}-480.webp 480w,
            {base}/{slug}-800.webp 800w,
            {base}/{slug}-1280.webp 1280w"
    sizes="(max-width: 768px) 100vw, 800px" />
  <img src="{base}/{slug}-1280.webp"
    alt="{alt_text}"
    width="1280" loading="lazy" decoding="async" />
</picture>
─────────────────────────────────────────────────────────────────────────────
""")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="CAVA Journal — Image Selector")
    p.add_argument("--topic",       default="", help="Palabras clave del articulo")
    p.add_argument("--article",     default="", help="Path al HTML (extrae tema automaticamente)")
    p.add_argument("--convert",     default="", help="JPG fuente para convertir a webp")
    p.add_argument("--slug",        default="", help="Slug de salida del set webp")
    p.add_argument("--alt",         default="Nazareth Padilla en CAVA Vinoteca", help="Alt text")
    p.add_argument("--min-score",   type=int, default=6, help="Score minimo (default 6); si no se alcanza, genera prompt IA")
    p.add_argument("--prompt-only", action="store_true", help="Solo generar prompt IA")
    args = p.parse_args()

    print("\n══ CAVA Journal — Image Selector ══\n")
    topic = args.topic

    # Solo prompt
    if args.prompt_only:
        if not topic:
            print("ERROR: --prompt-only requiere --topic"); return
        slug_sug = "nazareth-padilla-" + re.sub(r"[^a-z0-9]+", "-", topic.lower())[:50].strip("-")
        print_ai_prompt(topic, slug_suggestion=slug_sug)
        return

    # Inventario
    all_imgs   = get_available_images()
    used_imgs  = get_used_images()
    available  = [img for img in all_imgs if img not in used_imgs]

    print(f"Carpeta Nazareth:   {len(all_imgs)} imágenes")
    print(f"En uso (Journal):   {len(used_imgs)}")
    print(f"Disponibles:        {len(available)}\n")

    print("── En uso " + "─" * 66)
    for img in sorted(used_imgs):
        print(f"  {img}")

    print("\n── Disponibles " + "─" * 61)
    for img in available:
        mb = (NAZARETH_DIR / img).stat().st_size / (1024 * 1024)
        print(f"  {img:62s}  {mb:.1f} MB")

    # Extraer tema del HTML si no viene en --topic
    if args.article and not topic:
        try:
            html = Path(args.article).read_text(encoding="utf-8", errors="ignore")
            parts = []
            m = re.search(r"<title>([^<]+)</title>", html)
            if m: parts.append(m.group(1))
            m = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
            if m: parts.append(m.group(1))
            topic = " ".join(parts)
            print(f"\nTema extraído: {topic}")
        except Exception as e:
            print(f"No se pudo leer el artículo: {e}")

    # Sugerencias y fallback IA
    if topic:
        if not available:
            print("\n⚠️  Carpeta vacía.")
            slug_sug = "nazareth-padilla-" + re.sub(r"[^a-z0-9]+", "-", topic.lower())[:50].strip("-")
            print_ai_prompt(topic, slug_suggestion=slug_sug)
        else:
            print(f"\n── Sugerencias para: '{topic}' " + "─" * 40)
            suggestions = suggest_images(topic, available)
            for i, (img, score) in enumerate(suggestions):
                mb = (NAZARETH_DIR / img).stat().st_size / (1024 * 1024)
                tag = "★ MEJOR" if i == 0 else f"  #{i+1}  "
                print(f"  {tag}  {img}  (score: {score}, {mb:.1f} MB)")

            best_img, best_score = suggestions[0] if suggestions else (None, 0)

            if best_score < args.min_score:
                slug_sug = "nazareth-padilla-" + re.sub(r"[^a-z0-9]+", "-", topic.lower())[:50].strip("-")
                print_ai_prompt(topic, slug_suggestion=slug_sug)
            else:
                stem = Path(best_img).stem
                print(f"\n✓  Seleccionada: {best_img}")
                print(f"   Generar webp:  python admin/image-selector.py \\")
                print(f"     --convert {best_img} --slug {stem} --alt \"[descripcion]\"")

    # Conversion a webp
    if args.convert and args.slug:
        print(f"\n── Generando set webp → {args.slug} " + "─" * 40)
        generated = generate_webp_set(args.convert, args.slug)
        if generated:
            print_srcset_snippet(args.slug, args.alt)

    print("\n══ Fin ══\n")


if __name__ == "__main__":
    main()
