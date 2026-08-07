# Vista alumno · Mi desempeño

## Regla académica implementada

- Las únicas calificaciones oficiales del Curso 1 son:
  - Laboratorio 2 · Etapa 9: 40 puntos.
  - Laboratorio 2 · Etapa 10: 60 puntos.
- El Laboratorio 1 y las actividades preparatorias del Laboratorio 2 se muestran como progreso formativo, sin nota oficial.
- La nota del curso se calcula únicamente cuando existen ambas evaluaciones oficiales.

## Vista alumno

La opción lateral `Mis resultados` fue reemplazada por `Mi desempeño`.

La pantalla muestra:

- evaluaciones oficiales completadas y revisadas;
- puntaje y nota del curso;
- respuestas originales del alumno;
- respuesta correcta o esperada;
- retroalimentación técnica;
- rúbrica y puntaje por criterio;
- observación general del docente;
- porcentaje de avance de las actividades formativas.

La pauta completa se muestra cuando la evaluación fue revisada o cuando el docente liberó las respuestas finales.

## Vista docente

La Etapa 10 del Laboratorio 2 tiene una rúbrica editable con dos criterios:

- Diseño técnico del paramento: 40 puntos.
- Comprensión e interpretación: 20 puntos.

La rúbrica se guarda dentro del campo `answer` de la respuesta existente, bajo `rubric_scores`; no requiere modificar el esquema de Supabase.
