# SUPABASE PROJECT MAP — CAVA GOURMET

> **AUTHORITATIVE PROJECT OWNERSHIP DOCUMENT.**
>
> Este archivo define de forma autoritativa qué proyecto Supabase pertenece
> a CAVA Gourmet y cuáles pertenecen a otros sistemas.
>
> Antes de auditar, migrar, cambiar variables de entorno, CSP, RLS, Auth o
> código relacionado con Supabase en este repositorio: **LEER ESTE ARCHIVO
> PRIMERO.**
>
> No inferir la propiedad de un proyecto solo porque su URL aparezca en
> código histórico, documentación, CSP o variables antiguas.
>
> Orden de autoridad ante contradicciones:
> 1. `SUPABASE-PROJECT-MAP.md` (este archivo)
> 2. configuración REAL verificada en Supabase / Vercel
> 3. código actualmente desplegado
> 4. documentación histórica (`SECURITY-HARDENING.md`, etc.)
>
> La documentación histórica NO prevalece sobre este mapa ni sobre la
> configuración real.

---

## 1. Mapa rápido

| Sistema | Nombre Supabase | Project Ref | URL |
|---|---|---|---|
| **CAVA Gourmet** | `cava-after-office` | `rbfctmcfweckbpgxlkqf` | `https://rbfctmcfweckbpgxlkqf.supabase.co` |
| EpistemicLab / WSET-AI-System | `EpistemicaLab` | `hylknjjhmxsuuwbsslkr` | `https://hylknjjhmxsuuwbsslkr.supabase.co` |
| Referencia legacy en repo CAVA | — (NO ASIGNAR) | `qkmgzyxknhhkucndbdsh` | NXDOMAIN — no resuelve |

---

## 2. CAVA Gourmet — proyecto Supabase oficial

- **Nombre:** `cava-after-office`
- **Project Ref:** `rbfctmcfweckbpgxlkqf`
- **URL:** `https://rbfctmcfweckbpgxlkqf.supabase.co`
- **Repositorio:** `BuenasBox/cava-gourmet-site`
- **Producción:** `https://www.cavagourmet.com`

Este es el **único** proyecto Supabase activo de CAVA. Verificado directamente
(2026-09-06): `/api/auth_config` en producción devuelve este ref; `/api/config`
opera contra él; `SUPABASE_KEY` es su service-role key.

### Funciones asociadas (arquitectura vigente)

- `miembros` — programa Enófilos
- `configuracion` — configuración pública (beneficios, promoción)
- `admin_profiles` — autorización de las superficies administrativas de CAVA
- `consignacion_state`, `consignacion_pagos` — control de consignaciones
- registro de experiencias, QR / scan, Google Wallet loyalty
- Supabase Auth (GoTrue) para el login de los paneles admin de CAVA

### Estado de la base de datos (verificado 2026-09-06)

| Tabla | RLS | Policies |
|---|---|---|
| `admin_profiles` | ON | 0 (default deny para anon/authenticated) |
| `configuracion` | ON | 0 (default deny) |
| `miembros` | ON | 0 (default deny) |
| `consignacion_state` | ON | 3 (SELECT/INSERT/UPDATE, `auth.uid() = user_id`) |
| `consignacion_pagos` | ON | 3 (SELECT/INSERT/DELETE, `auth.uid() = user_id`) |

El backend accede a todas las tablas mediante **service-role** (bypassa RLS).
`miembros`, `configuracion` y `admin_profiles` NO deben tener policies públicas.

### Regla

Cuando se trabaje en `BuenasBox/cava-gourmet-site`, el proyecto Supabase de
CAVA es `rbfctmcfweckbpgxlkqf`. No sustituirlo por otro ref sin una migración
explícitamente aprobada y documentada.

---

## 3. EpistemicLab — proyecto completamente separado

- **Nombre:** `EpistemicaLab`
- **Project Ref:** `hylknjjhmxsuuwbsslkr`
- **URL:** `https://hylknjjhmxsuuwbsslkr.supabase.co`
- **Pertenece a:** EpistemicLab / WSET-AI-System — **NO a CAVA Gourmet**.

Este proyecto NO aparece en el repositorio de CAVA y **no debe** utilizarse
para: miembros de CAVA, Enófilos, consignaciones, Google Wallet de CAVA,
paneles admin de CAVA, Auth de CAVA ni configuración de `cavagourmet.com`.

CAVA (`rbfctmcfweckbpgxlkqf`) y EpistemicLab (`hylknjjhmxsuuwbsslkr`) son
sistemas completamente independientes. **No consolidarlos. No migrar tablas
entre ambos. No copiar variables de entorno ni keys entre ambos.**

---

## 4. Referencia legacy / residual

- **Project Ref:** `qkmgzyxknhhkucndbdsh`
- **Estado:** LEGACY / RESIDUAL / **NXDOMAIN** (no resuelve en DNS).

**No es** un segundo proyecto activo de CAVA. **No es** EpistemicLab. El
hallazgo previo de "split brain / dos proyectos Supabase activos en CAVA"
queda descartado como **FALSO POSITIVO**.

Aparece únicamente como deuda histórica en documentación y configuración del
repo (p.ej. `SECURITY-HARDENING.md`, y hasta esta fase también en el
`connect-src` de la CSP de `vercel.json`). Debe retirarse de documentación y
configuración cuando corresponda. Si `SECURITY-HARDENING.md` afirma que
`qkmgzyxknhhkucndbdsh` es el proyecto de producción de CAVA, esa afirmación es
**HISTÓRICA / DESACTUALIZADA**.

---

## 5. Reglas para agentes IA y auditorías

1. Leer este archivo antes de analizar cualquier cosa de Supabase.
2. No inferir que dos project refs encontrados en un repo implican dos bases
   de datos activas de ese producto.
3. No confundir CAVA Gourmet con EpistemicLab. No proponer consolidarlos.
4. No migrar tablas ni copiar env vars / keys entre CAVA y EpistemicLab.
5. `qkmgzyxknhhkucndbdsh` es legacy / NXDOMAIN — no clasificarlo como activo.
6. Si aparece un project ref distinto a los documentados aquí: marcarlo como
   **UNKNOWN** y verificarlo antes de actuar.
7. No modificar la CSP para añadir o quitar hosts Supabase sin verificar
   primero si la referencia es activa o legacy.

---

## 6. Regla de seguridad

Los **project refs** y las **URLs públicas** de Supabase pueden documentarse.

**Nunca** documentar aquí (ni en logs, commits, informes o mensajes):

- `SUPABASE_SERVICE_ROLE_KEY` / service-role key
- anon key o publishable key (completa o parcial)
- JWT secret
- database password
- access tokens / refresh tokens
- Google Wallet private key
- cualquier secreto de producción

Las credenciales viven exclusivamente en los gestores de secretos/variables
correspondientes (Vercel Environment Variables, Supabase Dashboard).

### Distinción de keys de `rbfctmcfweckbpgxlkqf`

| Tipo | Uso | Dónde |
|---|---|---|
| **anon key** (legacy) / **publishable key** (moderna) | pública por diseño; cliente en el navegador | `SUPABASE_ANON_KEY` (env) → servida por `/api/auth_config` a los paneles admin |
| **service-role key** | solo servidor; bypassa RLS | `SUPABASE_KEY` (env) — usada por `/api/*`. **Nunca** enviar al navegador. |

Una publishable/anon key **no** es una service-role key. No confundirlas. Que
la publishable/anon key aparezca en el frontend **no** es una fuga de secreto.

---

## 7. Variables de entorno — realidad actual (2026-09-06)

| Variable | Estado | Nota |
|---|---|---|
| `SUPABASE_URL` | ✅ `rbfctmcfweckbpgxlkqf` | correcta |
| `SUPABASE_KEY` | ✅ service-role funcional | actúa como service-role; nomenclatura legacy (esperado: `SUPABASE_SERVICE_ROLE_KEY`) — **no cambiar ahora** |
| `SUPABASE_ANON_KEY` | ❌ ausente | leída por `api/auth_config.py`; su ausencia deja los paneles admin fuera de servicio |
| `SUPABASE_SERVICE_ROLE_KEY` | ❌ ausente | `api/_auth.py` cae a `SUPABASE_KEY` |
| `CAVA_ALLOWED_ORIGINS` | ❌ ausente | `api/_auth.py` usa lista hardcodeada por defecto; CORS verificado OK |
| `HMAC_SECRET`, `SCAN_PIN`, `GOOGLE_WALLET_KEY` | ✅ presentes | — |
| `NEXT_PUBLIC_SUPABASE_URL` / `_ANON_KEY` / `_PUBLISHABLE_KEY` | ⚠️ CONFIGURATION DEBT | el sitio es 100% vanilla (sin Next.js); `git grep` → 0 consumidores. Además `_ANON_KEY` y `_PUBLISHABLE_KEY` contienen una URL en vez de una key. Retirables sin riesgo (fuera de alcance de la fase actual). |
| `SCAN_KEY` | ⚠️ CONFIGURATION DEBT | presente en Vercel, 0 referencias en código |

---

## 8. Historial de reconciliación

- **2026-09-06** — Fase -1 (discovery) + Fase 0A: se establece este mapa como
  fuente autoritativa. Verificado: un solo proyecto CAVA (`rbfctmcfweckbpgxlkqf`),
  `qkmgzyxknhhkucndbdsh` = legacy/NXDOMAIN, EpistemicLab = separado.
  `SECURITY-HARDENING.md` (snapshot 2026-05-25) queda marcado como histórico en
  lo referente al project ref.
