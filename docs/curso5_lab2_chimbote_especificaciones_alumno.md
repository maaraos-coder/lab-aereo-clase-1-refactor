# Curso 5 · Laboratorio 2 · Edificio Chimbote
## Ficha constructiva académica inicial · entrega al alumno

**Documento de ejercicio académico, NO especificación técnica emitida por el titular.** Proyecto real: Edificio Chimbote, La Florida, Torre A. Vivienda de estudio vigente: **Torre A, piso 5, hilera sur, tercer departamento desde poniente**, clave académica **CH-A-P05-S03**. Esta clave **no es la numeración oficial de una vivienda**. Planta de pisos tipo: *3.1 Planos de Arquitectura (Parte 1)*, pág. 8 del PDF. Corte transversal: pág. 12. Elevaciones y otros cortes: *Parte 2*.

**Referencia arquitectónica complementaria:** para evaluar la fachada F-01/V-01 debe consultarse la **elevación sur de Torre A (Parte 2, página 5)** y cotejarla con la planta tipo (Parte 1, página 8). Los paños, balcones y ventanas del alzado son **geometría del proyecto**; los materiales y espesores de la tabla siguiente siguen siendo **supuestos docentes** y no se infieren del render conceptual.

### A · Condición constructiva original propuesta

| ID | Elemento | Composición inicial adoptada | Montaje inicial |
| --- | --- | --- | --- |
| M-01 | Separación aérea entre dos viviendas | Hormigón armado monolítico 180 mm, densidad supuesta 2.400 kg/m³ | Uniones rígidas con losas y muros; sin trasdosados |
| L-01 | Entrepiso | Losa HA 160 mm + mortero nivelador adherido 30 mm + cerámica 10 mm | No hay piso flotante ni cielo acústico |
| F-01 | Fachada opaca | HA 150 mm, densidad supuesta 2.400 kg/m³ | Sin revestimiento acústico interior |
| V-01 | Ventana del recinto seleccionado | DVH 4/12/4 mm en marco de aluminio convencional | La geometría del hueco debe medirse o completarse con una cota docente **si el alzado no es legible**; no asumir Rw certificado |
| S-01 | Cierre de baño o conducto | Yeso-cartón 12,5 mm por cara; perfilería metálica 70 mm; lana mineral 50 mm | Sistema docente convencional con pasos de instalaciones |
| IS-01 | Descarga sanitaria | PVC rígido DN110, abrazaderas rígidas y descarga WC de 6 L de la **vivienda superior (piso 6)**; receptor dormitorio de CH-A-P05-S03 (piso 5) | PVC rígido es consistente con la DIA; diámetro, fijación y operación son **supuestos docentes**, no datos verificados |
| T-01 | Terminación interior de piso del estar | Cerámica adherida (parte de L-01) | Superficie de recinto por extraer del plano |
| T-02 | Terminación interior de muros y cielo del estar | Pintura sobre hormigón/yeso; cielo continuo pintado | Superficies por calcular según geometría real |
| T-03 | Terminación del dormitorio | Piso laminado rígidamente apoyado (hipótesis docente), muros pintados, cielo pintado | No atribuir propiedades acústicas sin catálogo |

### B · Reverberación — materiales compatibles con SONARA

**El material constructivo está descrito en la sección A.** Para el cálculo de reverberación, SONARA incorpora **presets genéricos de absorción**, accesibles en `Reverberación · predicción de proyecto → Material genérico`. Las bandas y los tres primeros presets se contrastaron con SONARA (`maaraos-coder/sonara`, `app.py`, función `app_reverberacion_iso`). El preset de **puerta de madera maciza** se incorporó después al mismo módulo utilizando una referencia bibliográfica identificada. **Son coeficientes genéricos de modelación, no resultados de ensayos de los productos que se construirán ni especificaciones del Edificio Chimbote.**

| Preset genérico SONARA | α 125 Hz | α 250 Hz | α 500 Hz | α 1.000 Hz | α 2.000 Hz | α 4.000 Hz |
|---|---:|---:|---:|---:|---:|---:|
| Hormigón / superficie dura | 0,01 | 0,01 | 0,02 | 0,02 | 0,02 | 0,03 |
| Yeso pintado | 0,10 | 0,05 | 0,04 | 0,07 | 0,09 | 0,10 |
| Vidrio | 0,18 | 0,06 | 0,04 | 0,03 | 0,02 | 0,02 |
| Puerta de madera maciza | 0,14 | 0,10 | 0,06 | 0,08 | 0,10 | 0,10 |

**Asignación inicial para los dos recintos (sin soluciones mejoradas):**

| Superficie | Acabado constructivo definido en A | Preset genérico para SONARA | Condición |
|---|---|---|---|
| Dormitorio: piso | Piso laminado rígido T-03 | **Hormigón / superficie dura** | Aproximación reflectante: el preset no es una curva ensayada del laminado. |
| Estar: piso | Cerámica adherida T-01 | **Hormigón / superficie dura** | Aproximación reflectante: el preset no es una curva ensayada de la cerámica. |
| Ambos: cielo | Cielo continuo pintado T-02 | **Yeso pintado** | Preset equivalente de acabado pintado. |
| Ambos: muros opacos | Pintura sobre superficies rígidas T-02 | **Yeso pintado** | Preset equivalente; no determina la transmisión del muro. |
| Ambos: puerta interior | **Puerta de madera maciza** (hipótesis docente) | **Puerta de madera maciza** | Curva genérica de referencia bibliográfica adoptada también en SONARA; no ensayo de una puerta del proyecto. |
| Estar: ventana | DVH V-01 | **Vidrio** | Valor genérico superficial; no representa el aislamiento acústico del DVH. |
| Dormitorio: ventana | Solo si se identifica o adopta un vano | **Vidrio** | Si no se incluye una ventana en el submodelo, **omitir esa superficie** del cálculo en SONARA; no reemplazarla por un vano ficticio. |

**Procedimiento:** el alumno registra en la Etapa 3 las superficies de piso, cielo, muros opacos, puerta y ventana **del dormitorio y del estar**, selecciona los **mismos presets** en SONARA y calcula los tiempos de reverberación por banda de **125, 250, 500, 1.000, 2.000 y 4.000 Hz**, utilizando **Sabine o Eyring** con el método declarado y la geometría definida. **No se fija un TR por defecto.** La condición de cálculo será de **recintos vacíos/sin mobiliario**, para mantener comparabilidad. La Etapa 3 contiene tablas de α(f) y de TR(f), y permite guardar avances parciales.

**Origen de la puerta de madera:** curva para puerta maciza cerrada atribuida a NBR 12179:1992, reproducida en una publicación de acústica de la UFRJ (https://www.scielo.br/j/ac/a/yNvTbGMXxGxBYVbWYzDk3mP/). Esta curva se añadió al módulo de reverberación de SONARA y se usa únicamente como referencia docente. **Los materiales absorbentes para mejoras no se incluyen en la tabla de condición original.** La biblioteca de materiales elásticos para **aislamiento** de SONARA no sustituye estas curvas de **absorción**.

### C · Condiciones de operación complementarias

- Fachada: la exposición exterior debe estimarse en la Etapa 6 con los datos académicos de tránsito y NoiseMap. La antigua referencia fija de **Lden = 60 dB** no debe utilizarse como resultado calculado ni como medición; el estudiante documentará método, geometría y limitaciones.
- Descarga docente: **WC 6 L; evento único**. Espectro ficticio Lw (dB) en bandas de octava 63–4000 Hz: **70, 68, 66, 64, 61, 58, 55**. No confundir espectro Lw con LAFmax,nT. A falta de información de transmisión estructural no declarar cumplimiento global.
- Para los huecos, shafts y geometrías que no puedan obtenerse de forma inequívoca de los planos, utilizar exclusivamente la geometría base del **Suplemento de cotas e hipótesis docentes**, identificando cada valor como supuesto académico; no deducirlo de la materialidad.
