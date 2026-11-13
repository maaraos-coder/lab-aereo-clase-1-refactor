# Curso 5 · Laboratorio 2 · Edificio Chimbote
## Suplemento de cotas e hipótesis docentes · versión para el alumno

**Vivienda asignada:** Torre A, piso 5, hilera sur, tercer departamento desde poniente. Código académico **CH-A-P05-S03** (no corresponde a una numeración oficial acreditada).

**Finalidad:** completar, de manera controlada y transparente, **únicamente los datos geométricos que no puedan obtenerse de los planos originales**. Los casos emisores y receptores ya están definidos por el encargo; **el alumno calcula las dimensiones, superficies y volúmenes**, no selecciona otras viviendas o recintos.

> **¿Qué es una cota?** Es una dimensión indicada en un plano mediante líneas de acotación y una cifra (por ejemplo, 2,60 m entre dos paramentos). Una **cota documental** se lee de la lámina; una **hipótesis docente** se proporciona aquí solo para suplir un dato faltante y no debe atribuirse al edificio construido.

### 1 · Documentación que prevalece

- **Planta tipo de Torre A:** `3.1 Planos de Arquitectura (Parte 1)`, página 8 del PDF de origen, cuya escala y cartela se deben verificar.
- **Corte:** `Parte 1`, página 12 del PDF de origen. Verificar qué alturas corresponden al recinto, estructura y terminaciones.
- **Elevaciones y cortes complementarios:** `3.1 Planos de Arquitectura (Parte 2)`.
- **Ficha geométrica del alumno:** define los cuatro casos, sus recintos y los datos que se deben calcular.

Se han identificado como **posibles referencias parciales** del sector dormitorio las cifras **2,60 m y 3,10 m** y, en el sector cocina-estar, **2,45 m, 2,43 m y 3,03 m**. **No se certifica aquí que sean dimensiones completas de los recintos**: deben cotejarse sobre la planta, su orientación y extremos de acotación. No reutilizar las cotas **2,56 m y 2,35 m** de otro estar. Tampoco asumir que una cifra del corte corresponde automáticamente a altura libre.

### 2 · Casos y recintos asignados

| Código | Fuente / recinto emisor | Recinto receptor de estudio | Elemento principal |
|---|---|---|---|
| **AI-01 · Aéreo** | **Estar** de la vivienda inmediatamente al **poniente**, piso 5 | **Dormitorio** de CH-A-P05-S03, piso 5 | **Muro separador M-01** y vías laterales |
| **IM-01 · Impacto** | **Dormitorio superpuesto** de piso 6 | **Dormitorio** de CH-A-P05-S03, piso 5 | **Entrepiso L-01**, acabado y flancos |
| **FA-01 · Fachada** | Ruido exterior del **Pasaje Chimbote** | **Estar** de CH-A-P05-S03, piso 5 | Fachada **sur F-01**, ventana(s) **V-01** y sellos |
| **IN-01 · Instalación** | Descarga WC del baño de CH-A-P05-S03, piso 5 | **Dormitorio** de CH-A-P05-S03, piso 5 | Cierre/shaft **S-01** y descarga **IS-01**, con vías aérea y estructural cuando corresponda |

**Verificación del plano (Parte 1, página 8):** se aprecia el muro compartido entre **estar de vivienda poniente** y **dormitorio receptor** (AI-01), y la orientación exterior del **estar receptor** (FA-01). La planta tipo se aplica a **pisos 3–16 de Torre A**, por lo que la superposición de dormitorios de **pisos 5 y 6** es coherente con la planta de referencia (IM-01), sin que eso determine propiedades acústicas de la losa. En IN-01, el baño está en la misma vivienda, pero el plano **no demuestra una transmisión directa simple WC–dormitorio ni el trazado real de la descarga**; ese recorrido se trata como modelo docente y debe explicitarse.

### 3 · Cotas y condiciones complementarias para el ejercicio

| Código | Dato **supuesto docente** | Valor o criterio | Aplicación y restricción |
|---|---|---|---|
| **HG-01** | Altura interior útil provisional | **2,50 m** | Solo cuando el corte no permita justificar la altura libre del **recinto asignado**. No es altura verificada del proyecto. |
| **HV-02** | Ventana didáctica del **estar** hacia fachada sur | **1,80 × 1,20 m** (ancho × alto) | Exclusivamente **FA-01**, si el alzado y planta no permiten obtener las dimensiones del vano. No aplicar a un dormitorio. |
| **HI-01** | Tramo de cierre sanitario didáctico | **1,40 m** de longitud; altura **HG-01** cuando proceda | **IN-01**, solo si el trayecto y cerramiento aplicables se verifican o se documenta un modelo académico simplificado. No presupone adyacencia física. |
| **HC-01** | Operación y configuración de descarga | WC **6 L**; PVC **DN110**; abrazaderas rígidas | **IN-01**: condiciones de funcionamiento/modelo, **no cotas** de recintos ni evidencia de configuración constructiva real. |

**No se fija aquí un ancho de muro medianero, una superficie de losa, largo y ancho completos de los recintos ni una longitud de fachada.** Deben determinarse de los planos de las viviendas asignadas. Si falta un dato imprescindible, registrar **PENDIENTE** y justificar su solicitud al docente.

La antigua hipótesis **HV-01** (ventana del dormitorio) y **HF-01** (longitud de fachada del dormitorio) **no forman parte del caso FA-01 vigente**, que estudia el **estar**; no deben utilizarse para dimensionar su fachada.

### 4 · Qué calcula el alumno

**Para cada recinto receptor asignado:** largo, ancho o descomposición geométrica apropiada, altura útil documentada, **área de piso [m²]** y **volumen [m³]**. No se entrega ningún resultado resuelto.

**AI-01:** área real del muro separador, dimensiones y uniones relevantes; además, comprobar la relación entre el estar vecino y el dormitorio receptor.

**IM-01:** área y composición del entrepiso que corresponde a la proyección del dormitorio del piso 6 sobre el dormitorio receptor.

**FA-01:** área bruta de la fachada **sur del estar**, área transparente y área opaca, medidas de vanos y referencias del alzado. Si utiliza HV-02, debe rotularse **SUPUESTO DOCENTE**.

**IN-01:** geometría del recinto dormitorio, trayectoria y superficies del cierre/shaft **si corresponde**; identificar separadamente la condición de operación de WC y las vías de transmisión.

### 5 · Reverberación en SONARA

El alumno obtiene las superficies internas de **piso, cielo, muros, puertas y ventanas** de los recintos receptores, determina el volumen y selecciona los coeficientes de absorción **por banda** con su referencia. Calcula y registra el **TR por bandas** en SONARA; **no se entrega ningún tiempo de reverberación prefijado**.

### 6 · Registro y trazabilidad

Cada dimensión y parámetro debe clasificarse como **DOCUMENTAL** (cota leída con lámina y localización), **CALCULADO** (operación identificada), **SUPUESTO DOCENTE** (código de este suplemento) o **PROPUESTA DEL ALUMNO** (justificada). Si se desconoce, escribir **PENDIENTE**, sin presentar valores inventados como información del proyecto.

Este suplemento **no reemplaza los planos originales**, no proporciona superficies ni volúmenes calculados y no certifica dimensiones reales de una obra construida.
