# Pauta geométrica docente resuelta — B-308

**No mostrar en vistas Alumno ni Zoom.** Caso: Barrio Balmaceda, Lote 1, edificio A1; departamento B-308. Objetivo de diseño: ISO/TS 19488:2021, Clase B. Todos los cálculos acústicos deben desarrollarse en SONARA.

## Procedencia

- **Documental**: Anexo N.º 3, *3.1.1 Lote 1 – DS19.pdf*, lámina de plantas tipo de 2.º a 8.º pisos, página 3 del archivo PDF. Aparecen B-308, D-309 y B-408 al repetirse el mismo plano por nivel; la tipología B-E se indica como **52,06 m²** para la vivienda entera, **no** para un recinto.
- **Hipótesis de clase**: anexo técnico complementario AG/AC/VF y cotas suplementarias GC-01 a GC-06. Son una **idealización docente** sobre el sector de recintos; no deben presentarse como cotas reales del proyecto.
- **Precaución**: B-308 comparte medianera con D-309, pero sus tramos colindan con recintos distintos. No usar la longitud íntegra del muro para el caso dormitorio → estar.

## Geometría resuelta de referencia (cotas complementarias de alumno)

| Variable | Operación | Resultado | Origen |
|---|---|---|---|
| Estar-comedor B-308 · superficie | 3,80 × 5,30 m | **20,14 m²** | GC-01, docente |
| Estar-comedor B-308 · volumen | 20,14 × 2,50 | **50,35 m³** | GC-01 + AG-01, docente |
| Dormitorio D-309 · superficie | 2,70 × 2,90 m | **7,83 m²** | GC-02, docente |
| Dormitorio D-309 · volumen | 7,83 × 2,50 | **19,58 m³** | GC-02 + AG-01, docente |
| AI-01 · superficie común del tramo dormitorio–estar | 2,90 × 2,50 m | **7,25 m²** | GC-03 + AG-01, docente |
| IM-01 · superficie compartida de losa | 3,80 × 5,30 m | **20,14 m²** | GC-04, docente |
| FA-01 · superficie bruta de fachada estar | 3,80 × 2,50 m | **9,50 m²** | GC-05 + AG-01, docente |
| FA-01 · superficie ventana estar | 1,80 × 1,20 m | **2,16 m²** | VF-01, docente |
| FA-01 · superficie opaca estar | 9,50 − 2,16 | **7,34 m²** | derivado docente |
| IN-01 · superficie cierre baño D-309 → estar B-308 | 1,45 × 2,50 m | **3,63 m²** | GC-06 + AG-01, docente |

## Datos disponibles para SONARA

| Caso | Entradas geométricas disponibles | Faltantes / condicionantes |
|---|---|---|
| AI-01 | Emisor: dormitorio D-309 V=19,58 m³; receptor: estar B-308 V=50,35 m³; S separador=7,25 m²; muro HA180 mm | Método de flancos, Kij, trazabilidad R(f) y continuidad |
| IM-01 | Recinto superior B-408 sobre estar B-308; S losa=20,14 m²; V receptor=50,35 m³; HA160 mm | Características de revestimiento, s′ o ΔL(f), transmisiones laterales |
| FA-01 | S total=9,50 m²; S ventana=2,16 m²; S opaca=7,34 m²; V receptor=50,35 m³; TR estar 0,60 s; Lden 60 dB hipotético | Ensayo o curva del sistema completo de ventana, marco, cierre, exposición real |
| IN-01 | Cierre 3,63 m²; V receptor=50,35 m³; fuente WC6 L, espectro Lw docente 70/68/66/64/61/58/55 por bandas 63–4000 Hz | Tratamiento del contacto estructural; no inventar atenuación ni concluir desempeño global con vía aérea aislada |

**El curso no debe entregar automáticamente la Clase B:** el alumno debe seleccionar los descriptores, criterios, tabla y notas aplicables de ISO/TS 19488:2021 y justificar la decisión; no sustituirlo por Rw, Ln o niveles sin normalización.

## Control de calidad de la ficha

1. Comprobar que el alumno identificó las fuentes y el alcance documental.
2. Comprobar que no utilizó los 52,06 m² de departamento como área de un recinto.
3. Admitir tolerancia de redondeo de **±0,02 m² y ±0,05 m³** para esta idealización con dos decimales (criterio docente propuesto, no tolerancia normativa).
4. Confirmar que AI-01 usa el **tramo GC-03** y no el muro lateral completo.
5. Confirmar que el informe indica «supuesto docente» para AG/AC/VF/GC.
6. Exigir curvas, entradas y versiones de SONARA con tratamiento de flancos o limitaciones expresas.

**No es posible afirmar que los resultados acústicos originales o las variantes cumplen Clase B hasta completar y verificar los cálculos efectivos en SONARA.**
