# Plataforma Diplomado - Clase de Aislamiento a Ruido Aéreo

Versión V21 basada en la asesoría real del Edificio Institucional MINVU Magallanes.

## Contenido incorporado

- Modelo de placas simples de la tesis AKUZOFT.
- Sistemas dobles mediante Sharp.
- Ventanas dobles mediante Quirt, con las ecuaciones 2.28 y 2.29 de la tesis.
- Ejercicio profesional guiado: Sala de Reuniones Dirección.
- Aplicación didáctica de ISO 12354 y verificación de DnT,A.
- Comparación G-01, G-02 y solución real TA-01.
- Evaluación individual equivalente: Sala de Reuniones Licitaciones.
- Aislamiento compuesto de tabique y puerta.
- Optimización por cumplimiento, margen y costo.
- Intento único de evaluación, reiniciable solo desde la gestión docente.
- Clases en borrador completamente ocultas para los alumnos.

## Ejecución local

1. Instalar Python.
2. Instalar las dependencias:

   `pip install -r requirements.txt`

3. Configurar Supabase según `CONFIGURACION_SUPABASE.md`.
4. Ejecutar:

   `streamlit run app.py`

La clave docente de prueba es `docente123`. Cámbiela mediante los secretos de Streamlit antes de publicar.
