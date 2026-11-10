# Anexo técnico complementario — Curso 5, Laboratorio 2

**Proyecto documental:** Proyecto Inmobiliario DS19 y DS49 Barrio Balmaceda, Renca.  
**Planos base:** Anexo N.º 3, *3.1.1 Lote 1 - DS19.pdf*, planta de pisos tipo 2.º al 8.º.  
**Caso académico:** Lote 1, edificio A1, departamento **B-308**; contiguo **D-309** y superpuesto **B-408**. Se debe confirmar qué *recintos* comparten muro o losa antes de asignar áreas al modelo.

> **ADVERTENCIA DE TRAZABILIDAD:** Los valores de este anexo son **supuestos docentes**, NO dimensiones, materialidades ni prestaciones verificadas del proyecto inmobiliario real. Se entregan para permitir un ejercicio homogéneo donde los planos no especifican todos los datos. No sustituir con ellos cotas legibles.

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

## E. Pauta docente de comprobación

Para validar la ficha, comprobar el área efectiva de cada recinto (no la superficie de tipología completa), longitud separadora real, S = longitud × altura pertinente, V = área útil × altura libre, área bruta de fachada, áreas de vanos solamente del recinto evaluado, área opaca = área bruta − vanos; identificar fuentes y uniones. Toda cifra derivada debe señalar plano y operación. La solución numérica final docente debe cerrarse con lectura a resolución suficiente de cotas de la vivienda, nunca con estimaciones presentadas como definitivas.

**Versión 1.0 — documento didáctico, NO memoria técnica del titular.**
