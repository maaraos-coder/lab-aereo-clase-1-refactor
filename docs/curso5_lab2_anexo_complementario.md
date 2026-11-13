# Anexo técnico complementario — Curso 5, Laboratorio 2

**Proyecto documental:** Proyecto Inmobiliario DS19 y DS49 Barrio Balmaceda, Renca.  
**Planos base:** Anexo N.º 3, *3.1.1 Lote 1 - DS19.pdf*, planta de pisos tipo 2.º al 8.º.  
**Caso académico:** Lote 1, edificio A1, departamento **B-308**; contiguo **D-309** y superpuesto **B-408**. Se debe confirmar qué *recintos* comparten muro o losa antes de asignar áreas al modelo.

> **ADVERTENCIA DE TRAZABILIDAD:** Los valores de este anexo son **supuestos docentes**, NO dimensiones, materialidades ni prestaciones verificadas del proyecto inmobiliario real. Se entregan para permitir un ejercicio homogéneo donde los planos no especifican todos los datos. No sustituir con ellos cotas legibles.

## Materialidad original del ejercicio

La **condición constructiva de partida** para los modelos de ruido aéreo, impacto, fachada e instalaciones se encuentra en la [Ficha de especificaciones técnicas complementarias](./curso5_lab2_especificaciones_originales.md). Su composición es un **supuesto académico** y no una especificación verificada del titular. Debe mantenerse fija en los modelos originales; las soluciones mejoradas son propuestas del alumno.

## A. Geometría complementaria (supuestos docentes)

| Código | Parámetro | Valor |
|---|---|---|
| AG-01 | Altura interior libre piso terminado–cielo terminado | **2,50 m** |
| AG-02 | Altura piso a piso | **2,70 m** |
| AG-03 | Espesor de losa estructural inicial | **160 mm** |
| AG-04 | Espesor agregado de acabados del entrepiso | **40 mm** (sin atribuir aislamiento) |
| AG-05 | Espesor inicial de muro separador de hormigón | **180 mm** |
| AG-06 | Espesor inicial de hoja opaca de fachada | **150 mm** |
| AG-07 | Densidad nominal de hormigón | **2.400 kg/m³** |
| VF-01 | Vano referencial para estar B-308 | **1,80 m × 1,20 m** |
| VF-02 | Vano referencial para dormitorio B-308 | **1,20 m × 1,20 m** |

**Restricción geométrica:** localizar VF-01 y VF-02 en el dibujo; no asignar ambas ventanas al mismo recinto si el plano no lo permite. Si la lámina contiene cotas legibles diferentes, el estudiante debe registrar y justificar la discrepancia, prevaleciendo la cota del plano.

## B. Condiciones académicas para los modelos (supuestos docentes)

| Código | Condición | Valor |
|---|---|---|
| AC-01 | Tiempo de reverberación del estar | **0,60 s** |
| AC-02 | Tiempo de reverberación del dormitorio | **0,50 s** |
| AC-03 | Exposición exterior convencional | **Lden = 60 dB** (no medido) |
| AC-04 | Instalación sanitaria | **Descarga de WC de 6 L**, un evento sin otras fuentes simultáneas |
| AC-05 | Espectro hipotético Lw por bandas de octava | **63/125/250/500/1000/2000/4000 Hz:** 70/68/66/64/61/58/55 dB |

AC-05 es un **espectro ficticio docente** que NO proviene de una ficha de fabricante ni de las mediciones del proyecto. No atribuir al modelo componentes estructurales desconocidos sin declarar sus hipótesis.

## C. Geometría que el alumno debe extraer, no entregar resuelta

1. **AI-01 — Ruido aéreo:** recintos verdaderamente contiguos entre D-309 y B-308; longitud efectiva de muro separador, altura libre AG-01, superficie separadora, volumen receptor y aristas de unión.
2. **IM-01 — Impacto:** recintos efectivamente superpuestos entre B-408 y B-308; superficie de losa compartida, volumen receptor, perímetro y uniones.
3. **FA-01 — Fachada:** recinto de B-308 con orientación al exterior, longitud del paño, altura, vanos atribuibles a ese recinto, superficie bruta, acristalada y opaca.
4. **IN-01 — Instalaciones:** ubicación de shaft o descarga y recintos relacionados; área de cierre y transmisiones aérea/estructural justificadas. Cuando falta plano sanitario, declarar el escenario académico.

Las superficies y los volúmenes se calculan por el estudiante. Cada valor debe indicar si es **DOCUMENTAL** (cota y lámina), **DERIVADO** (operación y cotas), **SUPUESTO DOCENTE** (código AG/AC/VF) o **PROPUESTA DEL ALUMNO** (variante propia).

## D. Cálculo y evaluación

- Todos los cálculos acústicos de original/variante se realizan en **SONARA**.
- El alumno consulta **ISO/TS 19488:2021** y documenta descriptor, requisito Clase B, sentido, tabla/nota y las limitaciones de cobertura.
- La app reúne ficha geométrica, referencias documentales, resultados y evidencia; **no revela valores geométricos calculados en la vista alumno**, ni certifica automáticamente la vivienda.
- El objetivo es la **predicción de diseño** para las situaciones seleccionadas, no afirmar clasificación global ni sustituir ensayos de obra.


## F. Plano docente complementario de cotas para el ejercicio B-308 (NO es el plano del titular)

La geometría de las parejas de recintos que se modelará se **idealiza** para que el problema tenga entradas reproducibles. Estos datos se entregan al alumno **como cotas suplementarias**, sin resolver superficies ni volúmenes:

| Código | Sector / cota complementaria | Longitud o dimensión |
|---|---|---|
| GC-01 | Estar-comedor B-308: ancho × largo | **3,80 × 5,30 m** |
| GC-02 | Dormitorio D-309 (emisor aéreo): ancho × largo | **2,70 × 2,90 m** |
| GC-03 | Tramo del separador común entre dormitorio D-309 y estar B-308 | **2,90 m lineales** |
| GC-04 | Estar B-408, repetición del estar B-308 en planta superior | **3,80 × 5,30 m** |
| GC-05 | Fachada exterior del estar B-308, longitud de paño | **3,80 m** |
| GC-06 | Tramo de cierre baño D-309 / estar B-308 para caso sanitario | **1,45 m lineales** |

**La altura efectiva que corresponda proviene de AG-01 (2,50 m).** Las áreas y volúmenes deben ser calculados por el alumno, no se entregan en esta tabla.

Para distinguir las transmisiones: **AI-01** usa exclusivamente el tramo GC-03, no el muro completo entre ambos departamentos. **IN-01** usa GC-06, al lado de un recinto sanitario, y **IM-01** usa GC-04 sobre GC-01. En **FA-01** combina GC-05 con VF-01 y su orientación real según lámina. La dimensión del baño fuente, cuando se requiera, será un dato adicional declarado del ejercicio y no se deduce del dormitorio.

**Croquis conceptual (no a escala):**
```text
                        FACHADA EXTERIOR
                  <---- GC-05 = 3,80 m ---->
               +----------------------------+-----------------------+
               |                            | Baño de D-309        |
               |   ESTAR B-308              | <---- GC-06 ---->    |
               |   GC-01                    +-----------------------+
               |   3,80 x 5,30 m            | Dormitorio D-309     |
               |                            | GC-02                |
               |                            | 2,70 x 2,90 m        |
               +----------------------------+-----------------------+
                              | GC-03: tramo común con dormitorio
              Sobre el estar B-308: estar B-408 (GC-04).
```
Este croquis representa los **tramos funcionales que se adoptan para la modelación**, no una sustitución de la distribución arquitectónica real. En caso de discrepancia, el alumno debe documentar la diferencia en su informe.

**Versión 1.0 — documento didáctico, NO memoria técnica del titular.**
