# Ficha de especificaciones técnicas complementarias · condición original
**Curso 5 · Laboratorio 2 · Vivienda B-308 · Barrio Balmaceda**

**Versión docente 1.0 | Alcance académico para modelación predictiva en SONARA**

> **Procedencia y alcance:** Los planos arquitectónicos de Barrio Balmaceda sirven para seleccionar la vivienda y definir su geometría. Las composiciones, espesores no documentados, características de montaje y condiciones acústicas que siguen son **supuestos académicos**, y **NO** se atribuyen al diseño construido ni a las especificaciones reales del titular. Deben modelarse como una **condición original docente única y reproducible**. No se garantiza que cumpla o incumpla Clase B sin cálculo.

## 1. Materialidad inicial común para las cuatro situaciones

| ID | Elemento del ejercicio | Sistema de partida y composición (de emisor a receptor) | Condiciones de montaje | Naturaleza del antecedente |
|---|---|---|---|---|
| **M-01** | Separador entre dormitorio D-309 y estar B-308, tramo GC-03 | Hormigón armado monolítico **180 mm**, densidad nominal **2.400 kg/m³**, acabado de pintura en ambas caras | Continuo hasta losas, encuentros rígidos; no considerar trasdosado ni aislante de cámaras en la condición original | **Supuesto docente** AG-05 y AG-07 |
| **L-01** | Entrepiso estar B-408 / estar B-308 | Losa de hormigón armado **160 mm**, densidad nominal **2.400 kg/m³**; mortero nivelador **30 mm** y baldosa cerámica **10 mm** en cara superior, **sin capa resiliente** | Mortero y baldosa adheridos rígidamente a la losa; cielo inferior pintado, sin cielo suspendido; continuidad de uniones rígidas | **Supuesto docente** AG-03, AG-04 y AG-07 (se desglosan los 40 mm de terminación) |
| **F-01** | Paño opaco de la fachada del estar B-308, GC-05 | Hormigón armado monolítico **150 mm**, densidad nominal **2.400 kg/m³**, pintura exterior/interior | Paño continuo rígido, sin trasdosado aislante en el modelo original | **Supuesto docente** AG-06 y AG-07 |
| **V-01** | Ventana del estar B-308, VF-01 | Acristalamiento doble **4/12/4 mm** (vidrio 4 mm + cámara de aire 12 mm + vidrio 4 mm), marco de aluminio convencional | Una ventana practicable; sellos perimetrales habituales **sin dato de ensayo**; no asumir hermeticidad acústica certificada | **Supuesto docente nuevo**; la dimensión del vano proviene de VF-01 |
| **S-01** | Cierre interior asociado a la descarga sanitaria del baño D-309 hacia estar B-308, GC-06 | Tabique liviano con **1 placa de yeso-cartón de 12,5 mm por cara**, perfilería metálica **70 mm**, cámara con **lana mineral 50 mm** | Montantes compartidos, fijaciones convencionales; uniones y pasos de tubería requieren evaluación específica | **Supuesto docente nuevo**, no descripción del proyecto real |
| **IS-01** | Sistema de tubería de descarga del caso IN-01 | Tubería sanitaria PVC rígido, diámetro nominal **110 mm**; descarga WC de **6 L**, un evento sin simultaneidad | Abrazaderas rígidas convencionales como condición docente inicial; paso por cierre S-01 no dotado de aislamiento acústico certificado | **Supuesto docente nuevo**, fuente AC-04/AC-05 |

**Nota importante sobre S-01:** es un cierre sanitario localizado representativo para el ejercicio; no implica que la totalidad del muro entre B-308 y D-309 sea liviana. El caso AI-01 utiliza el sector **M-01**, mientras que IN-01 estudia el sector **S-01** indicado por GC-06.

## 2. Parámetros comunes del modelo

- Geometría complementaria **AG-01 a AG-07, VF-01/VF-02 y GC-01 a GC-06**: ver *Anexo técnico complementario*.
- Altura interior: **2,50 m**; no confundir con altura piso a piso **2,70 m**.
- Reverberación adoptada: estar B-308 **0,60 s**; dormitorio **0,50 s** (hipótesis AC-01/AC-02).
- Fachada: **Lden = 60 dB**, valor hipotético didáctico (AC-03), no medición ni mapa de exposición verificado.
- Descarga WC: **6 L**, una operación; espectro hipotético **Lw = 70 / 68 / 66 / 64 / 61 / 58 / 55 dB** en 63 / 125 / 250 / 500 / 1.000 / 2.000 / 4.000 Hz respectivamente (AC-04/05). **No equivale a un dato medido ni garantiza el nivel máximo FAST**.
- Las condiciones de flanqueo, uniones, transmisión estructural e infiltraciones **no se infieren automáticamente** de los espesores. El alumno debe caracterizarlas en SONARA o declarar expresamente sus limitaciones.

## 3. Trabajo que conserva el alumno en la Etapa 3

1. Identificar el elemento base correspondiente a cada caso (M-01, L-01, F-01 + V-01, S-01 + IS-01).
2. Llevar la composición inicial a SONARA, verificando que no se mezclen propiedades de una **placa aislada** con prestaciones del sistema construido.
3. Elegir fuentes justificadas para parámetros que la ficha **no fija**: curvas R(f), espectros de impacto, datos de ventanas completas, características de uniones, efectos de flancos, rigidez y energía transmitida por fijaciones.
4. Registrar qué valores proceden de esta ficha, qué datos se obtuvieron de catálogo o SONARA y qué valores son hipótesis adicionales propuestas.
5. **No introducir medidas de mejora en el modelo original**. Los trasdosados, pavimentos flotantes, vidrios especiales, sellos mejorados, soportes resilientes y otros controles se proponen por el alumno en las Etapas 4–7.
6. Comparar siempre **condición original y variante** conservando geometría, fuente y condiciones de evaluación.

## 4. Entradas mínimas por caso en SONARA

| Caso | Materialidad original | Geometría a derivar de la Etapa 2 | Cuestión pendiente a justificar |
|---|---|---|---|
| AI-01 · Aéreo | M-01 y sus uniones rígidas | Área del tramo GC-03, volumen emisor/receptor, longitudes de encuentro | Curva espectral, vías flanqueantes y compatibilidad del modelo |
| IM-01 · Impacto | L-01 sin capa resiliente | Área de losa compartida, volumen receptor, conexiones | Espectro Ln de referencia y transmisión por vías laterales |
| FA-01 · Fachada | F-01 + V-01 | Áreas bruta, acristalada y opaca; volumen receptor | Curva del **conjunto vidrio-marco-sello**, no solamente del vidrio |
| IN-01 · Instalaciones | S-01 + IS-01 | Área del cierre sanitario y volumen receptor | Potencia/fuente por banda, condición temporal y transmisión por abrazaderas |

## 5. Verificación de Clase B

Los valores y descriptores de **ISO/TS 19488:2021** son responsabilidad del alumno desde la Etapa 1. Esta ficha **no entrega ni modifica requisitos normativos**. Solo sirve como **condición original** para calcular y después diseñar una solución que pueda justificarse frente a la meta Clase B. El informe será una predicción académica, no una certificación de obra.

**Uso:** material del alumno. La **pauta geométrica numérica resuelta** y los futuros resultados de referencia de SONARA permanecen en la **Vista Docente**.
