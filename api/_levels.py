"""Enófilos loyalty tiers — single source of truth.

`calcular_nivel` was copy-pasted byte-for-byte in member.py, miembros.py,
registrar_experiencia.py and scan.py. The per-endpoint `mensaje_progreso`
wording deliberately differs between surfaces (scan confirmation page vs.
registrar API response) and is intentionally NOT centralised here.
"""


def calcular_nivel(exp, es_enofilo=False):
    if es_enofilo and exp >= 25:
        return "🔐 Enófilo"
    if exp >= 10:
        return "🍷 Entusiasta"
    if exp >= 3:
        return "🌱 Neófito"
    return "🚪 Invitado"
