import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import journal_publish as publisher


def sample_item():
    return {
        "title": "Prueba editorial sobre el vino y la mesa",
        "slug": "prueba-editorial-vino-mesa",
        "category": "Cultura del vino",
        "date": "2026-09-28",
        "seo_title": "Prueba editorial del vino y la mesa | CAVA Journal",
        "description": "Una reflexión de Nazareth Padilla sobre el vino, la conversación y la mesa compartida desde CAVA Vinoteca en Pérez Zeledón.",
        "excerpt": "Una reflexión cercana sobre lo que ocurre cuando el vino deja de ser explicación y se convierte en conversación alrededor de la mesa.",
        "image_alt": "Nazareth conversa sobre vino alrededor de la mesa en CAVA Vinoteca",
        "keywords": ["vino", "mesa compartida", "Costa Rica"],
        "related": [
            "/journal/como-se-construye-cultura-del-vino",
            "/journal/vino-menos-elitismo-mas-experiencia",
        ],
        "related_titles": [
            "Cómo se construye cultura del vino",
            "Menos elitismo, más experiencia",
        ],
        "body_html": (
            "<p>" + "Palabra " * 220 + "</p><h2 class=\"reveal\">Uno</h2><p>"
            + "Texto " * 100 + "</p><h2>Dos</h2><p><a href=\"/nazareth\">Nazareth</a> "
            + "Cuerpo " * 100 + "</p>"
        ),
        "image": Image.new("RGB", (1400, 900)),
    }


def test_all_publication_transforms():
    item = sample_item()
    template = open("journal/que-significa-cuerpo-en-el-vino.html", encoding="utf-8").read()
    article = publisher.build_article(template, item)
    assert item["slug"] in article
    assert "<h1>Prueba editorial" in article

    journal = publisher.update_journal(open("journal.html", encoding="utf-8").read(), item)
    assert journal.count(item["slug"]) >= 3
    sitemap = publisher.update_sitemap(open("sitemap.xml", encoding="utf-8").read(), item)
    assert sitemap.count(item["slug"]) >= 2
    json.loads(publisher.update_feed(open("feed.json", encoding="utf-8").read(), item))
    json.loads(publisher.update_pages(open("data/pages.json", encoding="utf-8").read(), item))
    assert item["slug"] in publisher.update_llms(open("llms.txt", encoding="utf-8").read(), item)
    assert "ART-009" in publisher.update_registry(open("JOURNAL-REGISTRY.md", encoding="utf-8").read(), item)
    assert len(publisher.image_files(item["image"], item["slug"])) == 4
