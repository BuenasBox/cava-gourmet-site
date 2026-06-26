# Configuración de CAVA Control en Supabase

Este archivo describe cómo configurar la base de datos en Supabase para el control de consignaciones.

## 1. Crear las tablas en Supabase

Accede al editor SQL en tu proyecto Supabase y ejecuta el siguiente código:

```sql
-- Tabla para guardar el estado del control (stocks y ventas)
CREATE TABLE consignacion_state (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  data JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- Tabla para pagos/abonos a proveedores
CREATE TABLE consignacion_pagos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  proveedor TEXT NOT NULL, -- 'mesa' o 'cinco'
  monto DECIMAL(12, 2) NOT NULL,
  fecha TEXT NOT NULL,
  nota TEXT,
  paid BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT valid_proveedor CHECK (proveedor IN ('mesa', 'cinco'))
);

-- Índices para mejor performance
CREATE INDEX idx_consignacion_state_user_id ON consignacion_state(user_id);
CREATE INDEX idx_consignacion_pagos_user_id ON consignacion_pagos(user_id);
CREATE INDEX idx_consignacion_pagos_proveedor ON consignacion_pagos(proveedor);

-- RLS (Row Level Security)
ALTER TABLE consignacion_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE consignacion_pagos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only view own state"
  ON consignacion_state FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can only update own state"
  ON consignacion_state FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can only insert own state"
  ON consignacion_state FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can only view own pagos"
  ON consignacion_pagos FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can only insert own pagos"
  ON consignacion_pagos FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can only delete own pagos"
  ON consignacion_pagos FOR DELETE
  USING (auth.uid() = user_id);
```

## 2. Crear usuario para acceso

1. Accede a **Authentication > Users** en tu panel de Supabase
2. Haz clic en **"Add user"**
3. Completa:
   - **Email**: (el email que usarás para login)
   - **Password**: (contraseña segura)
4. Guarda

Ahora Nazareth o quien administre el control podrá acceder con ese email/contraseña.

## 3. Variables de entorno

El archivo `/api/auth_config.py` ya está configurado para usar las variables de entorno:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

En Vercel, asegúrate de que estén definidas en **Settings > Environment Variables**.

## 4. Estructura de datos

### `consignacion_state` (JSON)
Guarda el estado completo del control en formato JSON:

```javascript
{
  "m01": { "vendidas": 2, "fecha": "26/06/2026", "stockExtra": 0 },
  "m02": { "vendidas": 1, "fecha": "26/06/2026", "stockExtra": 1 },
  // ... más productos
}
```

### `consignacion_pagos` (Tabla normalizada)
Registra cada pago de forma normalizada para facilitar búsquedas y reportes.

## 5. Prueba rápida

1. Abre `/admin/cava_control_v3.html` en tu navegador
2. Deberías ver una pantalla de login
3. Ingresa el email y contraseña que creaste
4. ¡Listo! Ahora los datos se guardan en Supabase en lugar de localStorage

## 6. Notas de seguridad

- ✅ La URL está protegida con `meta robots="noindex,nofollow"`
- ✅ Requiere autenticación con email/password
- ✅ RLS (Row Level Security) garantiza que cada usuario solo ve sus propios datos
- ✅ El ANON_KEY de Supabase tiene permisos limitados a lectura/escritura solo en sus filas

## 7. Troubleshooting

### "Supabase no está configurado"
- Verifica que las variables de entorno `SUPABASE_URL` y `SUPABASE_ANON_KEY` estén en Vercel

### "Acceso denegado" en login
- Asegúrate de que creaste un usuario en Supabase (**Authentication > Users**)
- Verifica email y contraseña

### Los datos no se guardan
- Abre la consola del navegador (F12) y busca errores
- Verifica que las políticas RLS estén bien configuradas
- Asegúrate de que el usuario en login está autenticado correctamente

## 8. Migración desde localStorage (opcional)

Si ya tienes datos en localStorage, puedes migrarlos manualmente:

1. Abre DevTools (F12) en la versión anterior con localStorage
2. En la consola, ejecuta: `JSON.parse(localStorage.getItem('cava_state_v2'))`
3. Copia el JSON resultado
4. Accede a Supabase > SQL Editor
5. Ejecuta:
```sql
INSERT INTO consignacion_state (user_id, data) 
VALUES ('[TU_USER_ID]', '[EL_JSON_QUE_COPIASTE]')
```

---

**Última actualización**: 26 de junio de 2026
**Autor**: Claude Code
