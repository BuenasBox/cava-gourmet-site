import json
import os
import hmac
import hashlib
import time
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
HMAC_SECRET  = os.environ.get("HMAC_SECRET", "")
ISSUER_ID    = "3388000000023147327"

def validar_token(email, token):
    expected = hmac.new(HMAC_SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)

def supabase_request(method, endpoint, body=None):
    url     = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation"
    }
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

def calcular_nivel(exp, es_enofilo=False):
    if es_enofilo and exp >= 25: return "🔐 Enófilo"
    if exp >= 10: return "🍷 Entusiasta"
    if exp >= 3:  return "🌱 Neófito"
    return "🚪 Invitado"

def mensaje_progreso(exp, es_enofilo=False):
    if es_enofilo:  return "Parte del círculo interno de CAVA. 🔐"
    if exp >= 25:   return "Candidato a Enófilo — pendiente de invitación."
    if exp >= 10:   return f"Faltan {25 - exp} experiencias para ser candidato a Enófilo."
    if exp >= 3:    return f"Faltan {10 - exp} para Entusiasta 🍷"
    return f"Faltan {3 - exp} para Neófito 🌱"

def get_google_token():
    import jwt
    key_data = json.loads(os.environ.get("GOOGLE_WALLET_KEY", "{}"))
    now      = int(time.time())
    claims   = {
        "iss":   key_data.get("client_email", ""),
        "sub":   key_data.get("client_email", ""),
        "aud":   "https://oauth2.googleapis.com/token",
        "iat":   now,
        "exp":   now + 3600,
        "scope": "https://www.googleapis.com/auth/wallet_object.issuer"
    }
    token = jwt.encode(claims, key_data.get("private_key", ""), algorithm="RS256")
    data  = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion":  token
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

def actualizar_wallet(email, exp, es_enofilo):
    try:
        nivel     = calcular_nivel(exp, es_enofilo)
        progreso  = mensaje_progreso(exp, es_enofilo)
        safe_id   = email.replace("@", "_at_").replace(".", "_")
        object_id = f"{ISSUER_ID}.{safe_id}"
        body = json.dumps({
            "loyaltyPoints":          {"label": "Experiencias", "balance": {"int": exp}},
            "secondaryLoyaltyPoints": {"label": "Nivel",        "balance": {"string": nivel}},
            "textModulesData": [{"id": "progreso", "header": "Tu progreso", "body": progreso}]
        }).encode()
        url = f"https://walletobjects.googleapis.com/walletobjects/v1/loyaltyObject/{urllib.parse.quote(object_id, safe='')}"
        access_token = get_google_token()
        req = urllib.request.Request(url, data=body, method="PATCH")
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as r:
            r.read()
    except Exception:
        pass

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        email  = params.get("email", [""])[0].strip().lower()
        token  = params.get("t", [""])[0]

        if not email or not token:
            self._html(400, self._page_error("Parámetros inválidos"))
            return

        if not validar_token(email, token):
            self._html(403, self._page_error("Código QR no válido"))
            return

        result = supabase_request("GET", f"miembros?email=eq.{urllib.parse.quote(email)}&select=*")
        if not result or isinstance(result, dict):
            self._html(404, self._page_error("Miembro no encontrado"))
            return

        miembro    = result[0]
        nombre     = miembro.get("nombre", "")
        nuevas_exp = miembro["experiencias"] + 1
        historial  = miembro.get("historial") or []
        historial.append({"fecha": time.strftime("%d/%m/%Y"), "nota": "Enofilios Cava — After Office"})

        supabase_request("PATCH", f"miembros?email=eq.{urllib.parse.quote(email)}", {
            "experiencias": nuevas_exp,
            "historial":    historial
        })
        actualizar_wallet(email, nuevas_exp, miembro.get("es_enofilo", False))

        nivel    = calcular_nivel(nuevas_exp, miembro.get("es_enofilo", False))
        progreso = mensaje_progreso(nuevas_exp, miembro.get("es_enofilo", False))

        self._html(200, self._page_ok(nombre, nuevas_exp, nivel, progreso))

    def _page_ok(self, nombre, exp, nivel, progreso):
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Visita registrada · CAVA</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;1,300&family=Jost:wght@300;400&display=swap" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#091522;color:#f6efe3;font-family:'Jost',system-ui,sans-serif;font-weight:300;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem}}
  .wrap{{max-width:340px;width:100%;text-align:center}}
  .check{{font-size:2.5rem;margin-bottom:1.25rem;color:#b8975a}}
  .nombre{{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.9rem;font-weight:300;font-style:italic;color:#d7b879;margin-bottom:.5rem;line-height:1.1}}
  .nivel{{display:inline-block;border:1px solid rgba(184,151,90,.4);color:#d7b879;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;padding:.3rem .85rem;border-radius:3px;margin-bottom:1.5rem}}
  .exp-num{{font-family:'Cormorant Garamond',serif;font-size:4rem;font-weight:300;color:#b8975a;line-height:1}}
  .exp-label{{font-size:.58rem;letter-spacing:.22em;text-transform:uppercase;color:rgba(246,239,227,.45);margin-bottom:1.25rem;margin-top:.2rem}}
  .progreso{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.05rem;color:rgba(246,239,227,.75);line-height:1.6;margin-bottom:2rem}}
  .divider{{width:36px;height:1px;background:rgba(184,151,90,.25);margin:0 auto 1.5rem}}
  .brand{{font-size:.56rem;letter-spacing:.22em;text-transform:uppercase;color:rgba(246,239,227,.28)}}
</style>
</head>
<body>
<div class="wrap">
  <div class="check">✓</div>
  <div class="nombre">{nombre}</div>
  <div class="nivel">{nivel}</div>
  <div class="exp-num">{exp}</div>
  <div class="exp-label">experiencias</div>
  <div class="progreso">{progreso}</div>
  <div class="divider"></div>
  <div class="brand">Enofilios Cava &middot; CAVA Vinoteca</div>
</div>
</body>
</html>"""

    def _page_error(self, msg):
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Error · CAVA</title>
<style>
  body{{background:#091522;color:#f0a0a0;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;padding:2rem;font-size:.9rem}}
</style>
</head>
<body><p>&#10060; {msg}</p></body>
</html>"""

    def _html(self, code, html):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass
