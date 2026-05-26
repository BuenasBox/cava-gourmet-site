# Security Reports

## Objetivo de la auditoria

Esta carpeta organiza auditorias externas controladas para `https://www.cavagourmet.com`.

El objetivo es ejecutar pruebas eticas, pasivas o baseline, desde entorno local, sin afectar produccion, sin probar credenciales y sin escanear rutas autenticadas o sensibles.

## Contexto de infraestructura

- El sitio esta detras de Cloudflare con proxy activo.
- El backend corre en Vercel.
- Auth y APIs usan Supabase.
- Headers como `cf-ray`, `x-vercel-id`, `server: cloudflare`, `x-vercel-cache` y `cf-cache-status` son esperados y no son hallazgos por si solos.
- Respuestas `403` en rutas como `/wp-admin` son mitigaciones de Vercel/Cloudflare o rutas inexistentes protegidas, no evidencia de WordPress ni CMS.
- Algunas paginas usan `Content-Security-Policy-Report-Only` por headers HTTP y aun existen meta CSP heredadas. Advertencias CSP deben interpretarse con ese contexto hasta que se unifique la fuente de verdad.

## Herramientas soportadas

- ZAP Baseline via Docker.
- Nikto en modo no interactivo y no agresivo.
- Nuclei solo como fase independiente, limitada por tags, severidad y rate limit.

Antes de usar herramientas, verificar disponibilidad sin instalar nada global:

```bash
nikto -Version
docker info
nuclei -version
```

Si una herramienta no esta instalada, documentar el resultado y pedir confirmacion antes de instalar.

## Rutas excluidas

No escanear rutas autenticadas ni dinamicas sensibles:

- `/admin/*`
- `/api/registrar*`
- `/api/wallet*`
- `/api/link*`
- `/api/setup`
- `/api/miembros`

## Comandos seguros

Antes de cada scan, registrar fecha y commit activo del sitio:

```bash
echo "Fecha/hora: $(date -u)" >> security-reports/scan-log.txt
echo "Commit activo del sitio: $(git rev-parse HEAD)" >> security-reports/scan-log.txt
```

El commit debe ser el del repositorio del sitio `cavagourmet.com`, no el de la herramienta.

ZAP Baseline via Docker, solo si se puede mantener fuera de rutas excluidas:

```bash
docker run --rm -t -v "$(pwd)/security-reports/zap:/zap/wrk" \
  owasp/zap2docker-stable zap-baseline.py \
  -t https://www.cavagourmet.com \
  -r zap-report.html
```

Nikto fallback:

```bash
nikto -h https://www.cavagourmet.com -ssl -nointeractive \
  -output security-reports/nikto/reporte-nikto.txt
```

Nuclei, solo como segunda fase separada si ZAP o Nikto completaron sin errores:

```bash
nuclei -u https://www.cavagourmet.com \
  -tags headers,misconfig,exposure \
  -severity medium,high,critical \
  -rate-limit 3 \
  -o ./security-reports/nuclei/reporte.txt
```

Usar maximo una herramienta activa a la vez y maximo un scan concurrente.

## Comandos prohibidos

- Fuzzing.
- Fuerza bruta.
- Scans agresivos o intensivos contra produccion.
- Pruebas de credenciales.
- Payloads contra `/admin/*`.
- Payloads contra APIs sensibles.
- Opciones de threading agresivo.
- Evasion de WAF, CAPTCHA, Cloudflare Managed Challenge, rate limits o bloqueos automaticos.
- Guardar tokens, cookies, Authorization headers, contrasenas o credenciales en reportes.
- Subir reportes generados al repo.

Si una herramienta detecta rate limiting, WAF challenge, CAPTCHA, Cloudflare Managed Challenge o bloqueo automatico:

1. Detener el scan.
2. Documentarlo en `security-reports/scan-log.txt` como proteccion activa detectada.
3. No intentar evasion.

## Como interpretar reportes

- Tratar `cf-ray`, `x-vercel-id`, Cloudflare, Vercel y cache headers como contexto operativo normal.
- No marcar `403` en rutas inexistentes o CMS comunes como vulnerabilidad automaticamente.
- Revisar hallazgos CSP considerando que CSP esta en Report-Only y que existen meta CSP heredadas.
- Validar si un hallazgo aplica al stack real: Vercel, Cloudflare, Supabase, HTML/CSS/JS vanilla.
- Si aparece severidad alta o critica, no explotarla. Documentar, reproducir solo de forma minima y segura, y proponer mitigacion antes de cualquier validacion adicional.

## Advertencia de no subir resultados al repo

Los reportes generados, logs, capturas, HTML de resultados, cookies, tokens y cualquier evidencia sensible deben quedarse fuera de Git.

Esta carpeta esta configurada para ignorar outputs por defecto. Solo este `README.md` y los marcadores `.gitkeep` de estructura deben versionarse.

## Instalacion de herramientas

No instalar sin confirmacion explicita.

Referencias generales:

- Docker Desktop: instalar desde el sitio oficial de Docker para Windows/macOS/Linux.
- Nikto:
  - macOS: `brew install nikto`
  - Debian/Ubuntu/Kali: `sudo apt install nikto`
  - Windows: preferir WSL o contenedor Docker.
- Nuclei:
  - macOS: `brew install nuclei`
  - Go: `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest`
  - Windows: usar binario oficial de ProjectDiscovery o WSL.
