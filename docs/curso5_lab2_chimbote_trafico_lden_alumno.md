# Curso 5 · Laboratorio 2 · Tráfico vial y fachada

**Edificio Chimbote · Torre A · CH-A-P05-S03 · ejercicio FA-01**

## Encargo del alumno

La fachada seleccionada es la **sur**, orientada al corredor del **Pasaje Chimbote**. El alumno debe consultar el plano de emplazamiento y determinar si la vía tiene circulación de vehículos, su eje y su distancia horizontal a la fachada, y la cota vertical del receptor en piso 5. No atribuir a la vivienda exposición directa a **Mirador Azul**, cuya relación espacial es diferente.

### A · Tránsito supuesto para un ejercicio didáctico

Los siguientes datos son **inventados para enseñanza, no aforos reales**. Cada cifra es flujo horario promedio por categoría dentro de cada período.

| Período | Duración | Vehículos livianos/h | Pesados medianos/h | Pesados/h | Motocicletas/h |
|---|---:|---:|---:|---:|---:|
| Día | 12 h | 80 | 3 | 1 | 7 |
| Tarde | 4 h | 45 | 1 | 0 | 4 |
| Noche | 8 h | 10 | 0 | 0 | 1 |

**Hipótesis adicional:** velocidad media inicial 30 km/h, pavimento asfáltico convencional, pendiente 0 % salvo pendiente medida. Las categorías deben cotejarse con las categorías 1–5 del método CNOSSOS-EU antes de introducirlas en un motor conforme a ese procedimiento. No sustituir directamente motocicletas por una categoría de pesados. La asignación de períodos usa el régimen europeo de ejercicio (12/4/8 horas).

### B · Ubicación del receptor

- En la fachada del recinto habitable del piso 5, en la posición y altura que derive el alumno del corte, planta y alzado.
- **Altura y distancia:** NO proporcionadas resueltas. Deben determinarse del expediente o documentarse como hipótesis docente antes de comparar resultados.
- Modelar el eje vial, geometría real, suelo, edificios, reflexiones, meteorología y alturas conforme al alcance del motor que se utilice.

### C · Alcance y procedimiento en la versión actual de NoiseMap

La versión actual de `maaraos-coder/noisemap` implementa la **emisión espectral vial CNOSSOS-EU §2.2 para categorías 1, 2, 3, 4a y 4b**, con coeficientes por octavas y correcciones configurables mediante la biblioteca `phonometry`. La **propagación al receptor** utiliza un motor exterior **educativo basado en ISO 9613-2:2024**: incorpora geometría, efecto del suelo, absorción atmosférica, difracción y reflexiones especulares de primer orden, pero **no implementa CNOSSOS-EU §2.5 íntegra**. En consecuencia, el Lden de receptor se documenta como **estimación académica no normativa**.

#### Procedimiento para la Etapa 6, dentro de NoiseMap

1. Abre la **dirección oficial**: https://noisemap-akuzoft.vercel.app/ y revisa el plano del emplazamiento.
2. Utiliza **Tráfico vial** para dibujar el eje de **Pasaje Chimbote** en el lado sur del edificio. Finaliza la vía siguiendo los controles de dibujo.
3. Utiliza **Edificio** y marca el perímetro exterior en planta; pulsa **Cerrar edificio** y ajusta su altura. Si en la auditoría se lee «Dibuja el edificio», no hay un polígono de edificio activo: vuelve al mapa y créalo.
4. Con **Receptor**, ubica el punto exterior a unos **0,1 m** de la fachada **sur** correspondiente al caso **CH-A-P05-S03**, en dirección a la calle; evita esquinas e interior del inmueble. Introduce la altura **sobre rasante del piso 5** según corte o hipótesis documentada.
5. Selecciona la vía y configura categorías **1, 2, 3, 4a y 4b**, velocidades, tipo de pavimento, pendiente, sentidos y, cuando corresponda, el cruce. Los flujos del ejercicio son **supuestos**, no aforos.
6. En **Lden de tránsito · tres períodos**, cambia los valores iniciales de NoiseMap por los flujos de día (12 h), tarde (4 h) y noche (8 h) establecidos en la ficha. Coloca **7 / 4 / 1 motos/h** en la categoría **4b** para día/tarde/noche y no en «Pesados». Los ciclomotores 4a solo se introducen si la hipótesis de tráfico los contempla.
7. En **Auditoría del receptor en fachada**, elige el **edificio** y el **receptor** dibujados. La herramienta comprobará la orientación hacia la calle, la distancia receptor–fachada, la distancia fachada–calle y la altura.
8. Pulsa **Calcular Lden en receptor**. Si NoiseMap señala que el receptor está dentro, detrás, demasiado lejos de la fachada o cerca de una esquina, corrige la geometría antes de volver a calcular.
9. Revisa **Lday, Levening, Lnight y Lden**. El cálculo de incidencia ya **excluye la reflexión especular de la propia fachada**, de modo que **no se resta otro 3 dB**. Conserva la descripción de método académico.
10. Usa **Exportar resultados JSON** y regresa a la **Etapa 6**. Importa el archivo en «Importar resultado desde NoiseMap», confirma la coincidencia de vía/edificio/receptor y pulsa «Importar niveles a la ficha de fachada». Completa la documentación geométrica y diseña el sistema de fachada en SONARA.

**Nota sobre fuentes y receptores:** el dibujo del edificio es obligatorio **para la auditoría de incidencia en fachada** de este ejercicio, no para todos los cálculos posibles de NoiseMap. El edificio permite identificar qué pared corresponde al receptor para excluir **solo esa reflexión**, sin aplicar una corrección fija universal.

**Los aforos permiten calcular la emisión CNOSSOS-EU por bandas, pero NO un Lden reglamentario de fachada sin propagación normativa.** Para declarar resultados de receptor **CNOSSOS-EU completos** debe utilizarse un motor de propagación 2.5 documentado y validado, como NoiseModelling; anotar motor, versión, entorno, fecha y detalle de la propagación. No reutilizar como Lden un mapa de nivel puntual estacionario calculado con el motor genérico de NoiseMap.

La agregación correcta es:

```
Lden = 10 log10{[12·10^(Lday/10) + 4·10^((Levening+5)/10)
                + 8·10^((Lnight+10)/10)] / 24}
```

Esta **fórmula no reemplaza los cálculos de emisión y propagación**.

### D · Diseño de fachada en SONARA

Una vez obtenida una estimación trazable de la exposición exterior en la posición del receptor, calcular la composición de fachada en SONARA. Registrar la **geometría del recinto, ventanas, paños opacos, TR calculado, curvas y prestaciones del sistema de ventana completo** y proponer una mejora. Comprobar el requisito Clase B de ISO/TS 19488:2021 consultando descriptor, tabla y condiciones; Lden exterior no equivale al aislamiento de fachada.

### E · Evidencias que se guardarán en la Etapa 6

- Datos de tráfico por categoría/horario y velocidad.
- Distancia, altura y referencia planimétrica del receptor.
- Lday/Levening/Lnight, método de predicción y Lden calculado.
- Modelo original y solución mejorada de fachada en SONARA.
- Limitaciones y conclusión sustentada en ISO/TS 19488:2021.

**Fuente de metodología:** Directiva 2002/49/CE, Anexo I (Lden); Directivas 2015/996 y 2021/1226 (CNOSSOS-EU, método y revisiones). La ficha es docente.

**Archivos NoiseMap disponibles:** exportación de emisión por bandas, exportación de estimación en receptor etiquetada no normativa y exportación de niveles de período documentados. La Etapa 6 admite importar el JSON de receptor; el alumno debe conservar y citar la advertencia metodológica.
