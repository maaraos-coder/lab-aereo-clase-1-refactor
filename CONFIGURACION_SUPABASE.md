# Configuración de Supabase

## 1. Crear las tablas

1. Entra a tu proyecto de Supabase.
2. Abre **SQL Editor**.
3. Pulsa **New query**.
4. Copia todo el contenido de `supabase_schema.sql`.
5. Pulsa **Run**.

Este paso crea la plataforma, registra la Clase 1 y activa seguridad para impedir el acceso directo mediante la clave pública.

## 2. Obtener las credenciales

En Supabase abre **Project Settings → API** y copia:

- Project URL.
- `service_role` key.

La `service_role` es secreta. No debe pegarse en GitHub, enviarse por correo ni escribirse dentro de `app.py`.

## 3. Configurar Streamlit Cloud

1. Abre la aplicación en Streamlit Community Cloud.
2. Entra a **Manage app → Settings → Secrets**.
3. Pega:

```toml
[supabase]
url = "https://TU-PROYECTO.supabase.co"
service_role_key = "TU_SERVICE_ROLE_KEY"

[teacher]
password = "TU_CLAVE_DOCENTE"
```

4. Guarda los Secrets y reinicia la aplicación.

## 4. Actualizar GitHub

Sube al mismo repositorio:

- `app.py`
- `requirements.txt`
- la carpeta `assets`

No subas `.streamlit/secrets.toml`. El archivo `secrets.toml.example` solo sirve como modelo y no contiene claves reales.

## 5. Prueba mínima

1. Ingresa como alumno de prueba con el mismo RUT y correo.
2. Responde una actividad y guarda un desarrollo en **Mesa de cálculo**.
3. Cierra sesión y vuelve a ingresar.
4. Comprueba que la respuesta, puntaje y desarrollo siguen visibles.
5. En Supabase, revisa **Table Editor → responses**, `user_progress` y `notebook_entries`.

## Estructura para las próximas clases

Cada clase nueva tendrá un identificador permanente y se agregará a `classes`. Las respuestas anteriores no se reemplazan. Para incorporar una clase, entrega su PowerPoint, PDF, Word o apuntes e indica: “Adapta este material como Clase N de la plataforma del Diplomado”.
