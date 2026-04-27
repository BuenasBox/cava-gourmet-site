# GITHUB PAGES - GUÍA DE DESPLIEGUE

## Estado de tu sitio

✅ **Listo para GitHub Pages**  
✅ **Sin configuración Jekyll requerida**  
✅ **Todas las rutas son relativas**  

---

## Opción 1: Despliegue simple (Recomendado)

### 1. Inicializar Git (si no está)
```bash
cd "Mi sitio Web CAVA"
git init
git add .
git commit -m "Initial commit: CAVA Gourmet optimizado"
```

### 2. Crear repositorio en GitHub
- Ir a https://github.com/new
- Nombre: `cavagourmet` (o `mi-sitio-web-cava`)
- Descripción: "CAVA Gourmet - Del Muro a la Mesa"
- Public (para que sea visible)
- NO inicializar con README (ya tienes archivos)

### 3. Conectar y subir
```bash
git remote add origin https://github.com/tuusuario/cavagourmet.git
git branch -M main
git push -u origin main
```

### 4. Activar GitHub Pages
- Repo → Settings → Pages
- Source: Deploy from a branch
- Branch: `main` → `/root`
- Save

### 5. Tu sitio estará en
- `https://tuusuario.github.io/cavagourmet` (si es repo personal)
- O `https://cavagourmet-tuusuario.github.io` (si configuras custom domain)

---

## Opción 2: Con dominio personalizado

Si quieres que sea `https://cavagourmet.com`:

### 1. Comprar dominio
- Recomendado: Namecheap, Google Domains, GoDaddy

### 2. Configurar DNS
En tu registrador, agregar registros:
```
A           → 185.199.108.153
A           → 185.199.109.153
A           → 185.199.110.153
A           → 185.199.111.153
CNAME www   → tuusuario.github.io
```

### 3. En GitHub Pages settings
- Custom domain: `cavagourmet.com`
- ✅ Enforce HTTPS
- Save

### 4. Esperar ~15 min (propagación DNS)

---

## Estructura actual - GitHub Pages compatible

```
cavagourmet/
├── index.html              ✅ Archivo principal
├── AUDITORIA-OPTIMIZACION.md
├── assets/
│   ├── logo-cava-wordmark.webp
│   ├── logo-cava-wordmark.jpg
│   ├── logo-cava-mark.jpg
│   ├── logo-cava-mark.webp
│   ├── images/
│   │   ├── og/
│   │   │   └── og-cava-gourmet.jpg
│   │   ├── nazareth/
│   │   └── ... (fotos reales cuando estén)
│   └── ... (otros assets)
├── Fotografías/            ✅ Será navegable via GitHub
├── Repaldos Index/         ✅ Será navegable via GitHub
└── .git/                   (generado por git)
```

---

## ⚠️ NOTAS IMPORTANTES

### Lo que SÍ funciona
- ✅ HTML puro
- ✅ CSS inline o externo
- ✅ JavaScript vanilla
- ✅ Imágenes en subdirectorios
- ✅ Fuentes externas (Google Fonts)

### Lo que NO funciona
- ❌ Backend (PHP, Node, Python)
- ❌ Bases de datos
- ❌ Servidor de formularios (necesitas Formspree, Netlify Forms, etc.)
- ❌ Jekyll (a menos que lo configures explícitamente)

### Sobre tu formulario de contacto
- Actualmente usas WhatsApp links ✅ (funciona en GitHub Pages)
- Si quieres email, usa:
  - **Formspree**: https://formspree.io/
  - **Netlify Forms**: Cambiar hosting a Netlify
  - **EmailJS**: JavaScript para enviar emails

---

## 📱 Testing después del despliegue

1. Abre tu URL en navegador
2. Verifica que funcionen los links internos (#mesa, #after-office)
3. Prueba los botones WhatsApp
4. En DevTools (F12):
   - Console: Sin errores 🔴
   - Network: Images cargan con lazy loading
   - Lighthouse: Score 80+ en Performance

---

## 🔄 Actualizar el sitio

Después de hacer cambios locales:

```bash
git add .
git commit -m "Update: descripción del cambio"
git push
```

GitHub Pages se actualizará automáticamente en ~1 minuto.

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Sitio muestra 404 | Settings → Pages → verificar rama y carpeta |
| CSS no carga | Revisar rutas (deben ser relativas) |
| Imágenes no se ven | `assets/imagen.jpg` no `/assets/imagen.jpg` |
| WhatsApp links no funcionan | Verificar que URL sea `https://wa.me/...` |
| Cache viejo | Ctrl+Shift+R (hard refresh) o Dev Tools → Disable cache |

---

**¡Listo para el despliegue! 🚀**
