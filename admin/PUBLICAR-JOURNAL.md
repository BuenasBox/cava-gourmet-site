# Publicar en el Journal sin tocar código

El editor crea el artículo, optimiza la imagen y actualiza en una sola publicación:

- la página del artículo;
- la portada de `/journal`;
- `sitemap.xml`;
- `feed.json`;
- `llms.txt`;
- `data/pages.json`;
- `JOURNAL-REGISTRY.md`.

## Uso de Nazareth

1. Abrir `https://www.cavagourmet.com/admin/editor-articulo-cava`.
2. Iniciar sesión con la cuenta administrativa de CAVA.
3. Completar los datos, escribir el artículo y seleccionar una imagen horizontal de al menos 1280 × 630 px.
4. Revisar que todo el checklist esté verde y abrir **Vista previa**.
5. Presionar **Publicar en Journal** una sola vez.
6. Esperar el mensaje `Publicado · Vercel está desplegando los cambios`.

El despliegue de Vercel puede tardar unos minutos. El editor abre la URL final; si todavía muestra 404, basta con recargar después de que termine el despliegue.

El borrador se guarda automáticamente en el navegador. La imagen debe seleccionarse otra vez después de cerrar o recargar la página, porque el navegador no permite conservar archivos locales.

## Configuración única del administrador técnico

El publicador requiere una variable secreta de Vercel:

```text
CAVA_GITHUB_TOKEN
```

Debe ser un token de acceso de GitHub de alcance limitado al repositorio `BuenasBox/cava-gourmet-site`, con permiso **Contents: Read and write**. Configurarlo en Production y Preview. No debe guardarse en el repositorio ni enviarse al navegador.

Valores opcionales — ya tienen defaults correctos:

```text
CAVA_GITHUB_REPOSITORY=BuenasBox/cava-gourmet-site
CAVA_GITHUB_BRANCH=master
```

La rama debe aceptar actualizaciones directas del token. Cada publicación queda registrada como un commit independiente y puede revertirse desde GitHub.
