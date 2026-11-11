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

### C · Qué puede y qué no puede hacer la versión actual de NoiseMap

La versión actual de `maaraos-coder/noisemap` (Streamlit) dispone de fuentes puntuales y propagación simplificada, pero **no tiene implementadas las tablas de emisión de CNOSSOS-EU ni toda su propagación**. Se incorporó una pestaña **Tránsito y Lden** para registrar los aforos supuestos, la ubicación del receptor y **comprobar el cálculo energético de Lden desde los niveles Lday, Levening y Lnight aportados**.

**No se obtiene un Lden vial válido únicamente ingresando la tabla de aforos.** Para declarar resultados CNOSSOS-EU debe utilizarse una implementación documentada y validada del método, por ejemplo un motor especializado; anotar motor, versión, entorno, fecha y detalle de la propagación. No reutilizar como Lden un mapa de nivel puntual estacionario calculado con el motor genérico de NoiseMap.

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
