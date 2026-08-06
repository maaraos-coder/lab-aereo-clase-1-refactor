# Arquitectura del proyecto

## Punto de entrada

- `app.py`: configuración de Streamlit, composición de módulos, navegación principal y registro de funciones activas.

## Configuración

- `config/laboratorios.py`: cursos, laboratorios, etapas, títulos, tiempos y puntajes.
- `config/features.py`: activación del formulario y desactivación temporal del visor CAD y cuaderno técnico.

## Núcleo

- `core/database.py`: conexión con Supabase, autorización y persistencia del progreso.
- `core/acoustics.py`: cálculos acústicos puros.
- `core/evaluations.py`: respuestas formativas, puntajes, cierres y resúmenes de evaluación.

## Laboratorios

- `labs/laboratorio_1.py`: etapas activas 0–10 del Laboratorio 1.
- `labs/laboratorio_2.py`: etapas activas 0–10 del Laboratorio 2.

## Vistas

- `views/acceso.py`: autenticación de alumnos y docentes.
- `views/cursos.py`: Mis clases, selección y laboratorios futuros.
- `views/docente.py`: gestión docente y centro de resultados.
- `views/resultados.py`: resultados visibles para alumnos.
- `views/formulario.py`: formulario técnico.
- `views/proyeccion.py`: ventana independiente para proyección en Zoom.

## Interfaz

- `ui/components.py`: componentes visuales reutilizables.
- `ui/styles.py`: CSS global de la aplicación.

## Código histórico

- `archive/legacy_stages.py`: versiones antiguas del Laboratorio 2 y etapas históricas identificadas previamente.
- `archive/legacy_lab1_app_stages.py`: antiguas copias `stage0()`–`stage10()` que ya no participan en la navegación activa.

## Funciones activas

`LAB_STAGE_FUNCTIONS`, definido en `app.py`, es la fuente de verdad que enlaza la navegación con las etapas activas de cada laboratorio.

## Reglas para modificaciones futuras

1. Modificar las etapas en `labs/`, no las versiones de `archive/`.
2. Mantener las claves de widgets y de `st.session_state` salvo que se migren los datos guardados.
3. Mantener sincronizadas las consultas con `supabase_schema.sql`.
4. Ejecutar `python -m compileall -q .` antes de desplegar.
5. Probar acceso de alumno, acceso docente, etapas 0–10, resultados, autosave y vista Zoom.
