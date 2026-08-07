# Motor unificado de actividades

La aplicación usa `core/activities.py` como única fuente para calcular el progreso formativo.

## Reglas

- Todas las respuestas formativas se guardan mediante `_save_formative()`.
- Los ejercicios numéricos, preguntas de desarrollo y preguntas de comprensión usan el botón **Comprobar y guardar**.
- Las evaluaciones oficiales `final_comprehension` y `final_integrated_design` no se incluyen en el progreso formativo.
- Para agregar una actividad nueva, se registra una sola vez en `FORMATIVE_PROGRESS_KEYS` dentro de `config/laboratorios.py`.
- `views/resultados.py` calcula el avance desde el catálogo central, evitando listas duplicadas.
- Cada respuesta nueva incorpora metadatos `_activity` dentro del JSON guardado, sin requerir cambios en el esquema de Supabase.
