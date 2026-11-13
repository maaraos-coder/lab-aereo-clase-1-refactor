# Pauta docente reservada · Chimbote C5L2
## Selección y auditoría geométrica, sin números inventados

**Proyecto verificado:** Edificio Chimbote, dos torres; Torre A de 16 pisos, Torre B de 10 pisos; planta tipo de Torre A, cortes y elevaciones en Anexo 3.

**Caso provisional:** CH-A-P05-S03, piso 5 Torre A, hilera sur, tercer departamento desde poniente. **No es departamento identificado por número oficial**. La planta contiene cotas para varios estares; **las cotas de 2,56 m y 2,35 m antes señaladas no se atribuyen a esta nueva vivienda sin verificación**. Algunas cotas de corte se leen como 2,34 m, **sin demostrar todavía el significado de altura libre hasta cielos terminados**.

### Tabla de auditoría de la ficha del alumno
| Magnitud o relación | Evidencia disponible | Verificación docente necesaria | Estado |
|---|---|---|---|
| Torre A, planta tipo | Parte 1, PDF pág. 8 | Confirmar cartela y posición | Identificable |
| Límites del departamento CH-A-P05-S03 | Planta tipo | Comprobar muros medianeros y accesos; asociar vivienda completa | **Pendiente de cierre** |
| Estar y zonas abiertas | Cotas específicas de CH-A-P05-S03 pendientes de comprobación | Comprobar continuidad con cocina/comedor y delimitación interior | Parcial |
| Altura libre útil | Parte 1, corte pág. 12 | Confirmar altura suelo terminado–cielo terminado con acabados | Parcial |
| Medianero entre unidades | Planta | Seleccionar recintos efectivos y longitud; excluir tabiques internos | Pendiente |
| Entrepiso repetido | Planta tipo | Verificar proyección exacta de habitaciones del piso superior | Parcial |
| Fachada y ventanas | Planta tipo + elevaciones Parte 2 | Localizar vano del recinto, ancho, alto y paño total | Parcial |
| Cierre/shaft sanitario | Baños/cocinas en planta | Verificar fuente/receptor y vía directa, flancos y fijaciones | Parcial |
| Superficies de absorción | Geometría + acabados académicos | Revisar piso, cielo, muros, vidrio, puertas y datos alfa por banda | Calculables tras geometría |
| TR en SONARA | Materiales + superficies + volumen | Revisar parámetros y método, curva por banda y coherencia | Pendiente de ejecución |

### Estado de factibilidad para SONARA
- **AI-01:** se necesita un tramo separador cierto entre dos recintos y los flancos; todavía no hay S medido de forma concluyente para esta unidad.
- **IM-01:** la planta tipo permite la repetición vertical, pero se debe comprobar el área de losa común.
- **FA-01:** falta cierre definitivo del paño con alto y ancho de ventana para el recinto elegido.
- **IN-01:** escenario docente de PVC rígido; la DIA confirma PVC pero no el diámetro DN110 ni su montaje. Comprobar comunicación geométrica del recinto y distinguir vía aérea de estructural.
- **TR:** no adoptar 0,5 ni 0,6 s prefijados; calcular en SONARA con superficies y absorciones aportadas.

### Política docente de datos faltantes
Si las cotas no se leen en el expediente seleccionado, emitir un **plano complementario con dimensión y justificación** o una hipótesis claramente rotulada, conservando la geometría del caso. No asignar valores no verificados a la fuente original. **No publicar una pauta docente numérica "completa" hasta resolver esos controles.**

### Revisión de entrega
La Etapa 1 evalúa criterio de Clase B (descriptores, condiciones, sentido y referencia ISO); Etapa 2 ficha geométrica del alumno; Etapa 3 materialidad y TR en SONARA; Etapas 4–7 predicciones/variantes; Etapa 8 comparación; Etapas 9/10: 30 + 70 puntos.

**Uso exclusivo docente. No incluir en el ZIP del alumno.**


## Selección definitiva del caso académico
Se fija **Torre A, piso 5, hilera sur de la planta tipo, tercer departamento contando desde el extremo poniente**. Código identificador interno **CH-A-P05-S03**. Emisor aéreo: estar de vivienda inmediatamente al poniente, sujeto a selección de recintos realmente contiguos; impacto: vivienda directamente superpuesta del piso 6; fachada: paño exterior sur del estar; instalaciones: **descarga WC del baño de la vivienda superpuesta del piso 6** como fuente intermitente de vivienda vecina; receptor dormitorio de CH-A-P05-S03 en el piso 5. La bajada sanitaria y el recorrido hasta el receptor son **hipótesis de modelación**, no trazados acreditados. Esta selección espacial sí es definitiva, pero las áreas y alturas no se rellenan sin leer cotas completas.

## Inspección adicional de la vivienda fijada, lámina planta tipo

En la unidad resaltada del lado sur de Torre A se pueden leer estas **cotas parciales**:
- **Dormitorio:** etiquetas horizontales **2,60 m** y verticales **3,10 m**, directamente junto al símbolo de cama. Un recinto rectangular *idealizado* a partir de esas dos cotas tendría **8,06 m²**; comprobar si los paramentos internos y salientes alteran el área efectiva antes de aceptarla.
- **Estar:** se aprecian **2,43 m** y una cota vertical próxima a **3,75 m**. No asumir directamente que toda el área rectangular **9,11 m²** es el estar, porque puede haber continuidad con otros espacios o un límite en el trazo.
- **Cocina:** se observan cotas **2,45 m** y **3,00 m**; confirmar que estas corresponden al módulo útil del lado de la vivienda y no a la cocina adyacente por simetría.

**No corresponde sumar automáticamente dormitorio + estar + cocina** para obtener el área total; la geometría es irregular y las circulaciones, baño, terraza y tabiques deben tratarse separadamente. Para SONARA, determinar el área real y el volumen del recinto receptor según sus límites acústicos (en espacios abiertos estar-cocina, justificar si se consideran un único recinto).

**Fuentes:** `3.1 Planos de Arquitectura (Parte 1).pdf`, pág. 8 (planta tipo original). El realce amarillo y borde rojo son auxiliares, y no se usan para medir.

**No cerrados aún:** superficie total de recinto en planta irregular, altura libre a cielo terminado, ancho/alto exactos de vano del estar, geometría del shaft sanitario y uniones flanqueantes. Estos datos necesitan cotejo del original/cortes o suplemento técnico académico específico.
