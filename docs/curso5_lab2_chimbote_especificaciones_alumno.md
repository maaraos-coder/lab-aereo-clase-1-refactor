# Curso 5 · Laboratorio 2 · Edificio Chimbote
## Ficha constructiva académica inicial · entrega al alumno

**Documento de ejercicio académico, NO especificación técnica emitida por el titular.** Proyecto real: Edificio Chimbote, La Florida, Torre A. Vivienda de estudio vigente: **Torre A, piso 5, hilera sur, tercer departamento desde poniente**, clave académica **CH-A-P05-S03**. Esta clave **no es la numeración oficial de una vivienda**. Planta de pisos tipo: *3.1 Planos de Arquitectura (Parte 1)*, pág. 8 del PDF. Corte transversal: pág. 12. Elevaciones y otros cortes: *Parte 2*.

### A · Condición constructiva original propuesta

| ID | Elemento | Composición inicial adoptada | Montaje inicial |
| --- | --- | --- | --- |
| M-01 | Separación aérea entre dos viviendas | Hormigón armado monolítico 180 mm, densidad supuesta 2.400 kg/m³ | Uniones rígidas con losas y muros; sin trasdosados |
| L-01 | Entrepiso | Losa HA 160 mm + mortero nivelador adherido 30 mm + cerámica 10 mm | No hay piso flotante ni cielo acústico |
| F-01 | Fachada opaca | HA 150 mm, densidad supuesta 2.400 kg/m³ | Sin revestimiento acústico interior |
| V-01 | Ventana del recinto seleccionado | DVH 4/12/4 mm en marco de aluminio convencional | La geometría del hueco debe medirse o completarse con una cota docente **si el alzado no es legible**; no asumir Rw certificado |
| S-01 | Cierre de baño o conducto | Yeso-cartón 12,5 mm por cara; perfilería metálica 70 mm; lana mineral 50 mm | Sistema docente convencional con pasos de instalaciones |
| IS-01 | Descarga sanitaria | PVC rígido DN110, abrazaderas rígidas, descarga WC de 6 L | PVC rígido es consistente con la DIA; diámetro, fijación y operación son **supuestos docentes**, no datos verificados |
| T-01 | Terminación interior de piso del estar | Cerámica adherida (parte de L-01) | Superficie de recinto por extraer del plano |
| T-02 | Terminación interior de muros y cielo del estar | Pintura sobre hormigón/yeso; cielo continuo pintado | Superficies por calcular según geometría real |
| T-03 | Terminación del dormitorio | Piso laminado rígidamente apoyado (hipótesis docente), muros pintados, cielo pintado | No atribuir propiedades acústicas sin catálogo |

### B · Reverberación — calcular en SONARA

**No se fija un TR por defecto.** El estudiante calculará en SONARA los tiempos de reverberación que utilice para sus recintos receptores a partir de:
- Geometría de la Etapa 2: volumen V y superficies internas (piso, cielo, muros y vanos).
- Coeficientes de absorción **por banda** elegidos de biblioteca/material de SONARA o fichas técnicas justificadas.
- Condición de ocupación y mobiliario que se declare. Adoptar como escenario docente **recintos sin mobiliario** para comparar modelos, salvo que se defina otra condición y se conserve en ambos.
- Evidencia de SONARA: datos, bandas, método, TR por banda y valor utilizado en normalizaciones.

Los acabados T-01 a T-03 se entregan como descripción física, **no como coeficientes alfa**. El estudiante debe seleccionar valores defendibles y documentar su fuente. Si SONARA solo admite materiales sin curva de absorción, deberá indicarlo como limitación y no inventar resultados.

### C · Condiciones de operación complementarias

- Fachada: la exposición exterior debe estimarse en la Etapa 6 con los datos académicos de tránsito y NoiseMap. La antigua referencia fija de **Lden = 60 dB** no debe utilizarse como resultado calculado ni como medición; el estudiante documentará método, geometría y limitaciones.
- Descarga docente: **WC 6 L; evento único**. Espectro ficticio Lw (dB) en bandas de octava 63–4000 Hz: **70, 68, 66, 64, 61, 58, 55**. No confundir espectro Lw con LAFmax,nT. A falta de información de transmisión estructural no declarar cumplimiento global.
- Los datos faltantes de huecos, shafts y geometrías de recintos se deben registrar como **pendientes** o cubrir con un suplemento aprobado por el docente; no se deducen de la materialidad.
