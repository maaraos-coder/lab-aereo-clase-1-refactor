from ui.styles import apply_global_styles
from views import proyeccion as _projection_views
from ui import components as _ui_components
from views import docente as _teacher_views
from views import acceso as _access_views
from views import cursos as _course_views
from views import resultados as _result_views
from views import formulario as _formula_views
from views.impresion import render_print_view
import base64
import datetime as dt
import io
import json
import math
import mimetypes
import re
import sqlite3
import hashlib
import tempfile
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    from future_labs import COURSE_LABS, FUTURE_LABS
except ImportError:
    COURSE_LABS, FUTURE_LABS = [], {}
try:
    from diploma_formulas import build_formulary_html
except ImportError:
    def build_formulary_html(*args, **kwargs):
        return "<div class='card'><b>Formulario no disponible en esta copia local.</b></div>"
from student_results import release_controls

from config.features import ENABLE_CAD_VIEWER, ENABLE_CALCULATION_NOTEBOOK

from config.laboratorios import (
    ACADEMIC_COURSES,
    APPLICATION_POINTS,
    APPLICATION_TOTAL,
    BREAK_AFTER_STAGE,
    BREAK_MINUTES,
    COURSE_ID,
    FINAL_EXAM_STAGE,
    LAB1_STAGE_TITLES,
    LAB2_ACTIVE_MINUTES,
    LAB2_BREAK_AFTER_STAGE,
    LAB2_BREAK_MINUTES,
    LAB2_MINUTES,
    LAB2_STAGE_TITLES,
    LAB2_TOTAL_MINUTES,
    LABORATORIES,
    LAB_ACTIVITY_STAGES,
    FORMATIVE_PROGRESS_KEYS,
    LAB_POINT_SCHEMAS,
    LAB_STAGE_TITLES,
    ROUTE_SUMMARIES,
    STAGES,
    STAGE_GUIDE,
    STAGE_INTROS,
    STAGE_MINUTES,
    TOTAL_CLASS_MINUTES,
)


from core.database import (
    _activity_db,
    _authorized_student,
    _class_row,
    _clear_course_cache,
    _course_classes,
    _effective_opening,
    _is_answer_state,
    _is_open,
    _make_user_key,
    _normalize_identification,
    _normalize_name,
    _now,
    _opening_label,
    _parse_opening,
    _progress_value,
    _register_user,
    _remote_rows,
    _supabase,
    load_user_progress as _db_load_user_progress,
    save_user_progress as _db_save_user_progress,
)

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from core import acoustics as _acoustics
from core import evaluations as _evaluations
from core.word_export import build_evaluation_docx, build_evaluation_zip, safe_filename
import streamlit.components.v1 as components
try:
    from supabase import create_client
except ImportError:
    create_client = None
if ENABLE_CAD_VIEWER:
    try:
        import ezdxf
        from ezdxf.addons.drawing import Frontend, RenderContext
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        import matplotlib.pyplot as plt
    except ImportError:
        ezdxf = Frontend = RenderContext = MatplotlibBackend = plt = None
else:
    ezdxf = Frontend = RenderContext = MatplotlibBackend = plt = None

st.set_page_config(
    page_title="Laboratorios | Diplomado en Acústica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
ROOT = Path(__file__).parent

FREQS = np.array([100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150])
ACTIVITY_DB = ROOT / "formative_responses.sqlite3"
SANTIAGO_TZ = ZoneInfo("America/Santiago")
if st.query_params.get("lab") in ("1","2"):
    st.session_state["active_lab"]=int(st.query_params["lab"])
ACTIVE_LAB = int(st.session_state.get("active_lab", 1))
CLASS_ID = LABORATORIES[ACTIVE_LAB]["id"]
CLASS_NUMBER = ACTIVE_LAB

def save_user_progress():
    return _db_save_user_progress(CLASS_ID)

def load_user_progress(user_key):
    return _db_load_user_progress(user_key, CLASS_ID)

apply_global_styles(st)

ACADEMIC_CONTENT = {0: '## Etapa 0 · Introducción y ruta de la clase\n\nDuración propuesta: 10 minutos\n\nIncluirá:\n\nPresentación general de la clase.\n\nObjetivo de aprendizaje.\n\nExplicación breve de cómo funcionará la clase interactiva.\n\nUn pequeño resumen de cada etapa:\n\nDiferencia entre aislamiento y absorción.\n\nTransmisión de la energía sonora.\n\nLey de masa, frecuencia y rigidez.\n\nAbsorción acústica en recintos.\n\nElementos constructivos compuestos.\n\nEvaluación técnico-económica de soluciones.\n\nCaso profesional integrador.\n\nEvaluación final.\n\nDuración, pausa y sistema de puntajes.\n\nResultados que se espera que alcance el alumno al finalizar.\n\nPuede presentarse mediante una línea de tiempo visual, donde cada etapa tenga un ícono, una descripción de dos o tres líneas y su duración.\n\nNo colocaría fórmulas, cálculos ni ejercicios en esta etapa. Su función será que el estudiante comprenda desde el comienzo qué aprenderá, en qué orden y para qué le servirá profesionalmente.', 1: '## Etapa 1 · Principios del control de ruido\n\nDuración propuesta: 25 minutos\n\n1. Definición de control de ruido\n\nEl control de ruido comprende el conjunto de medidas destinadas a reducir la generación, propagación o recepción del sonido no deseado.\n\nTodo problema puede analizarse mediante tres componentes:\n\nFuente: elemento que genera el ruido.\n\nTrayectoria: medio por el cual se propaga.\n\nReceptor: persona, comunidad o recinto afectado.\n\n2. Propagación del sonido\n\nLa explicación mostrará que el sonido:\n\nSe origina en la fuente.\n\nSe propaga por el aire y las estructuras.\n\nPuede reflejarse, absorberse o desviarse durante su recorrido.\n\nFinalmente alcanza al receptor.\n\nTambién se diferenciarán brevemente:\n\nTransmisión aérea.\n\nTransmisión estructural.\n\nTrayectorias directas.\n\nTrayectorias indirectas.\n\n3. Soluciones según su ubicación\n\n| Zona de intervención | Ejemplos de soluciones |\n| --- | --- |\n| Fuente | Sustituir el equipo, reducir velocidad, balancear, lubricar, instalar soportes antivibratorios o encapsular |\n| Trayectoria | Barreras, cerramientos, silenciadores, aumento de distancia, sellado y tratamiento de ductos |\n| Receptor | Cabina acústica, fachada aislante, redistribución del espacio, alejamiento o protección auditiva |\n\nDebe indicarse que, en general, es preferible actuar primero sobre la fuente, después sobre la trayectoria y, como última alternativa, sobre el receptor.\n\nImagen interactiva propuesta\n\nLa escena mostrará una máquina industrial a la izquierda, la trayectoria al centro y una oficina con una persona a la derecha:\n\nNo será una imagen estática. Tendrá tres botones:\n\nIntervenir en la fuente\n\nIntervenir en la trayectoria\n\nProteger al receptor\n\nAl presionar cada botón, la escena cambiará:\n\nFuente: aparece un encapsulamiento y apoyos antivibratorios; disminuye la cantidad de ondas emitidas.\n\nTrayectoria: aparece una barrera o cerramiento; las ondas se bloquean, desvían y atenúan.\n\nReceptor: aparece una cabina o mejora de fachada; el ruido sigue existiendo, pero llega con menor intensidad.\n\nAdemás, un medidor cualitativo mostrará el cambio:\n\nSituación inicial: 85 dB\n\nControl en la fuente: 75 dB\n\nControl en la trayectoria: 68 dB\n\nProtección del receptor: 63 dB\n\nSe aclarará que estos valores son ilustrativos y no se suman ni se restan directamente sin realizar una evaluación acústica.\n\nEjercicio intercalado\n\nSe presentará un grupo electrógeno que afecta una oficina vecina. El alumno deberá ubicar distintas soluciones en:\n\nFuente.\n\nTrayectoria.\n\nReceptor.\n\nPor ejemplo: mantenimiento del motor, silenciador de escape, soportes antivibratorios, barrera, encapsulamiento, mejora de ventanas y reubicación del puesto de trabajo.\n\nLa retroalimentación explicará que una misma solución puede intervenir más de un mecanismo, pero debe clasificarse según su función principal.\n\nAsí, la etapa termina con esta idea:\n\nPara controlar correctamente el ruido, primero debemos identificar dónde se genera, cómo se propaga y quién lo recibe. Solo entonces podemos seleccionar la intervención más eficaz.', 2: '## Etapa 2 · Aislamiento acústico y absorción acústica\n\nDuración propuesta: 25 minutos\n\n1. ¿Qué es el aislamiento acústico?\n\nEl aislamiento acústico es la capacidad de una separación constructiva —como un muro, puerta, ventana, piso o techo— para reducir la transmisión del sonido desde un recinto emisor hacia otro recinto receptor.\n\nSu objetivo principal es:\n\nEvitar o disminuir que el sonido atraviese una separación.\n\nEjemplo: impedir que el ruido de una sala de máquinas llegue a una oficina contigua.\n\nEl aislamiento depende, entre otros factores, de:\n\nMasa del elemento.\n\nRigidez.\n\nEstanqueidad.\n\nDesacoplamiento entre sus capas.\n\nFrecuencia del sonido.\n\nPuertas, ventanas, uniones y otras vías indirectas.\n\nEn esta etapa solo se presentarán estos factores; se desarrollarán posteriormente.\n\n2. ¿Qué es la absorción acústica?\n\nLa absorción acústica es la capacidad de un material o superficie para transformar parte de la energía sonora incidente, principalmente en calor, reduciendo la energía que se refleja nuevamente dentro del mismo recinto.\n\nSu objetivo principal es:\n\nDisminuir las reflexiones y controlar la reverberación dentro de un espacio.\n\nEjemplo: instalar paneles absorbentes en un aula para mejorar la claridad de la palabra.\n\nLa absorción depende de:\n\nTipo y espesor del material.\n\nFrecuencia del sonido.\n\nPorosidad.\n\nCámara de aire posterior.\n\nSuperficie cubierta.\n\nForma de instalación.\n\n3. Diferencia fundamental\n\n| Aspecto | Aislamiento acústico | Absorción acústica |\n| --- | --- | --- |\n| Actúa sobre | Sonido que atraviesa una separación | Sonido reflejado dentro del recinto |\n| Objetivo | Reducir la transmisión a otro espacio | Reducir reflexiones y reverberación |\n| Lugar del resultado | Recinto receptor | Mismo recinto donde se instala |\n| Soluciones comunes | Muros, puertas herméticas, ventanas dobles, sellos y sistemas desacoplados | Paneles porosos, lana mineral, cielos absorbentes y revestimientos acústicos |\n| Indicadores asociados | , , STC, | , absorción equivalente y tiempo de reverberación |\n| Pregunta clave | ¿Cuánto sonido pasa al otro lado? | ¿Cuánto sonido deja de reflejarse? |\n\nImagen interactiva propuesta\n\nLa visualización mostrará dos recintos separados por un muro:\n\nEn el recinto emisor habrá un parlante.\n\nLas ondas llegarán a la separación.\n\nUna parte se reflejará.\n\nOtra será absorbida.\n\nOtra atravesará el muro y llegará al recinto receptor.\n\nEl alumno podrá seleccionar tres situaciones:\n\nSin tratamiento: muchas reflexiones y alta transmisión.\n\nAgregar absorción: disminuyen las reflexiones dentro del recinto emisor, pero el aislamiento del muro no cambia significativamente.\n\nMejorar el aislamiento: disminuye claramente el sonido que atraviesa hacia el recinto receptor.\n\nLa animación debe mostrar siempre la dirección correcta:\n\nLa onda incidente avanza desde la fuente hacia el muro.\n\nLa onda reflejada regresa al recinto emisor.\n\nLa energía absorbida se atenúa dentro del material.\n\nLa onda transmitida continúa hacia el recinto receptor.\n\nDebajo aparecerá el balance energético:\n\nDonde:\n\n: energía incidente.\n\n: energía reflejada.\n\n: energía absorbida.\n\n: energía transmitida.\n\nEjemplo sencillo\n\nUn vecino escucha música proveniente del departamento contiguo:\n\nInstalar espuma acústica dentro del departamento emisor puede reducir la reverberación, pero no necesariamente evitará que la música atraviese el muro.\n\nMejorar la masa, estanqueidad o desacoplamiento del muro sí apunta directamente a reducir la transmisión hacia el vecino.\n\nEjercicio breve de aplicación\n\nEl alumno clasificará cada solución como absorción, aislamiento o combinación de ambas:\n\nPanel absorbente en un aula.\n\nPuerta acústica con sellos perimetrales.\n\nMuro doble desacoplado con lana mineral interior.\n\nCortina liviana decorativa.\n\nCielo absorbente en un restaurante.\n\nVentana termopanel acústica.\n\nLa retroalimentación no solo indicará la respuesta correcta, sino también el fenómeno físico involucrado.\n\nLa etapa cerrará con esta idea central:\n\nLa absorción controla cómo se comporta el sonido dentro de un recinto; el aislamiento controla cuánto sonido se transmite hacia otro recinto. Un material absorbente no es necesariamente un buen aislante.\n\n## Etapa 2 · Aislamiento, absorción y acústica interior\n\nAdemás de definir aislamiento y absorción, incorporaremos:\n\nTiempo de reverberación\n\nEs el tiempo que tarda el nivel sonoro en disminuir 60 dB después de detenerse la fuente sonora.\n\nUn tiempo de reverberación alto produce una sala más reverberante.\n\nUn tiempo bajo produce un sonido más seco y controlado.\n\nEl tiempo adecuado depende del uso del recinto.\n\nEn aulas y salas de reuniones se necesita controlar la reverberación para facilitar la comunicación.\n\nEn salas destinadas a música puede requerirse una reverberación mayor, pero equilibrada.\n\nSe mostrará la ecuación de Sabine como introducción conceptual:\n\nDonde:\n\n: tiempo de reverberación, en segundos.\n\n: volumen del recinto, en m³.\n\n: área de absorción acústica equivalente, en m² sabin.\n\nEn esta etapa la ecuación se explicará visualmente, sin exigir todavía cálculos complejos.\n\nInteligibilidad de la palabra\n\nEs el grado en que un mensaje hablado puede escucharse y comprenderse correctamente dentro de un recinto.\n\nDepende principalmente de:\n\nTiempo de reverberación.\n\nNivel del ruido de fondo.\n\nDistancia entre quien habla y quien escucha.\n\nRelación señal/ruido.\n\nReflexiones tardías.\n\nCaracterísticas del sistema de amplificación, si existe.\n\nLa idea fundamental será:\n\nEscuchar una voz no significa necesariamente comprenderla.\n\nRelación entre absorción, reverberación e inteligibilidad\n\nLa secuencia conceptual será:\n\nSe aclarará que esto tiene límites: una sala excesivamente absorbente también puede reducir la sensación de naturalidad y disminuir el nivel de la voz a distancia.\n\nDiferencia respecto del aislamiento\n\nAquí reforzaremos que:\n\nEl aislamiento controla el sonido que entra o sale del recinto.\n\nLa absorción controla las reflexiones interiores.\n\nLa reverberación describe la persistencia del sonido dentro del recinto.\n\nLa inteligibilidad describe cuánto se comprende la palabra.\n\nPor ejemplo, un aula puede tener:\n\nBuen aislamiento, pero mala inteligibilidad debido a una reverberación excesiva.\n\nBuena absorción interior, pero mal aislamiento frente al tránsito exterior.\n\nProblemas simultáneos de aislamiento y acondicionamiento acústico.\n\nImagen interactiva\n\nPropongo una sala de clases con una docente y varios alumnos. Tendrá tres controles:\n\nSala reflectante\n\nAgregar absorción\n\nAumentar ruido exterior\n\nLa visualización mostrará:\n\nCantidad y duración de las reflexiones.\n\nTiempo de reverberación cualitativo.\n\nRuido de fondo.\n\nClaridad de una frase hablada.\n\nResultado estimado de inteligibilidad: baja, media o alta.\n\nAsí el alumno verá que agregar absorción reduce la reverberación, mientras que mejorar el aislamiento reduce el ingreso del ruido exterior.\n\nLuego, en la Etapa 3, sí podremos preguntar con propiedad:\n\nQué solución mejora la inteligibilidad.\n\nQué fenómeno provoca la persistencia del sonido.\n\nSi un problema corresponde a aislamiento o acondicionamiento acústico.\n\nQué ocurre al incorporar materiales absorbentes.\n\nQué intervención corresponde cuando el problema es ruido exterior.\n\nTambién cambiaría el ejercicio que decía solamente “mucha reverberación y mala inteligibilidad” por uno más completo, porque ahora el alumno contará con las definiciones necesarias para responderlo. Esta modificación mejora mucho la coherencia entre contenido, actividad y evaluación.', 3: '## Etapa 3 · Aplicación conceptual interactiva\n\nDuración propuesta: 25 minutos\nPuntaje formativo: 10 puntos\n\nObjetivo\n\nQue el alumno sea capaz de:\n\nIdentificar la fuente, la trayectoria y el receptor.\n\nClasificar medidas de control según dónde actúan.\n\nDiferenciar aislamiento acústico y absorción acústica.\n\nSeleccionar una solución coherente para cada problema.\n\nJustificar brevemente su decisión.\n\nFuncionamiento\n\nLa etapa comenzará con instrucciones claras:\n\nTendrá varios ejercicios interactivos.\n\nCada ejercicio contará con tiempo limitado.\n\nEl temporizador solo comenzará al presionar “Iniciar ejercicio”.\n\nUna vez enviada la respuesta, no podrá modificarse.\n\nSe mostrará retroalimentación inmediatamente.\n\nEl puntaje quedará registrado en el progreso del alumno.\n\nEn la vista docente se verá la respuesta, tiempo utilizado y puntaje obtenido.\n\nEjercicio 1 · Identificar el problema acústico\n\nTiempo: 2 minutos · 2 puntos\n\nEscenario:\n\nUn grupo electrógeno instalado en el exterior genera ruido que atraviesa una ventana y afecta a los trabajadores de una oficina.\n\nEl alumno deberá identificar:\n\nFuente: grupo electrógeno.\n\nTrayectoria: propagación aérea y entrada por la ventana.\n\nReceptor: trabajadores de la oficina.\n\nLa actividad puede presentarse mediante una imagen interactiva en la que el alumno seleccione cada elemento.\n\nEjercicio 2 · Ubicar las medidas de control\n\nTiempo: 4 minutos · 2 puntos\n\nEl alumno deberá arrastrar o clasificar estas soluciones:\n\n| Solución | Clasificación principal |\n| --- | --- |\n| Mantenimiento del motor | Fuente |\n| Soportes antivibratorios | Fuente |\n| Silenciador de escape | Fuente/trayectoria, según su explicación |\n| Barrera acústica | Trayectoria |\n| Encapsulamiento | Fuente/trayectoria |\n| Mejoramiento de la ventana | Receptor |\n| Reubicación del puesto de trabajo | Receptor |\n\nCuando una medida pueda pertenecer a más de una categoría, la retroalimentación explicará que se acepta su función predominante.\n\nEjercicio 3 · ¿Aislamiento o absorción?\n\nTiempo: 3 minutos · 2 puntos\n\nEl alumno clasificará varias situaciones:\n\nPaneles absorbentes en un aula → absorción.\n\nPuerta hermética y pesada → aislamiento.\n\nCielo acústico de un restaurante → absorción.\n\nMuro doble desacoplado → aislamiento.\n\nLana mineral dentro de una partición → parte de un sistema de aislamiento, aunque el material sea absorbente.\n\nRevestimiento poroso dentro de una sala → absorción.\n\nEste último ejemplo será importante para evitar la idea equivocada de que todo material absorbente instalado dentro de un muro “aísla” por sí solo.\n\nEjercicio 4 · Seleccionar la solución correcta\n\nTiempo: 4 minutos · 2 puntos\n\nSe presentarán tres problemas breves:\n\nMucha reverberación y mala inteligibilidad en una sala.\n\nMúsica que atraviesa hacia el departamento vecino.\n\nRuido de una máquina que llega directamente a una oficina.\n\nEl alumno deberá elegir la solución más apropiada entre varias alternativas. No bastará con marcar una opción: después verá una explicación del fenómeno involucrado.\n\nEjercicio 5 · Mini caso de decisión\n\nTiempo: 5 minutos · 2 puntos\n\nCaso:\n\nEn una sala de reuniones se escucha el ruido de un taller contiguo y, además, existe demasiada reverberación dentro de la propia sala.\n\nEl alumno deberá proponer dos intervenciones:\n\nUna para reducir la transmisión desde el taller.\n\nOtra para mejorar el comportamiento acústico interior.\n\nRespuesta esperada:\n\nMejorar el aislamiento de la separación, puerta o encuentros.\n\nIncorporar absorción acústica dentro de la sala.\n\nTiempo y puntaje\n\nDurante la etapa se mostrará:\n\nTiempo disponible por ejercicio.\n\nCuenta regresiva.\n\nBarra de avance.\n\nPuntaje conseguido.\n\nPuntaje máximo.\n\nCantidad de intentos completados.\n\nSi se acaba el tiempo, el ejercicio se cerrará automáticamente y mostrará la explicación correcta. El temporizador no debería eliminar todo lo respondido antes de vencer.\n\nRetroalimentación\n\nDespués de cada respuesta aparecerá uno de estos resultados:\n\nCorrecto: explicación de por qué.\n\nParcialmente correcto: identificación del acierto y del concepto que falta.\n\nIncorrecto: respuesta correcta y explicación del error conceptual.\n\nLa etapa terminará con un resumen personalizado:\n\nObtuviste 8 de 10 puntos. Reconoces correctamente la diferencia entre aislamiento y absorción, pero debes reforzar la clasificación de las medidas aplicadas en la trayectoria.\n\nAsí la Etapa 3 funcionará como una comprobación práctica de las etapas anteriores antes de introducir contenidos más avanzados.', 4: '## Etapa 4 · Aislamiento acústico y costo-beneficio\n\nDuración propuesta: 30 minutos\n\n1. ¿Qué es el análisis costo-beneficio?\n\nConsiste en comparar:\n\nEl costo total de implementar una solución acústica.\n\nLa mejora acústica que se espera obtener.\n\nLos beneficios económicos y operacionales que genera.\n\nLos costos o pérdidas que se evitan.\n\nEn términos sencillos:\n\nUna solución es conveniente cuando el beneficio que produce justifica el dinero invertido.\n\n2. El costo de mejorar el aislamiento\n\nEl costo de una solución no incluye solamente los materiales. También deben considerarse:\n\nDiseño y evaluación acústica.\n\nMateriales y elementos constructivos.\n\nMano de obra.\n\nSellos, puertas, ventanas y encuentros.\n\nModificaciones estructurales.\n\nInterrupción de las actividades durante la obra.\n\nMantención.\n\nVida útil de la solución.\n\nTambién se explicará que el costo no aumenta necesariamente de manera proporcional al aislamiento. Obtener los últimos decibeles de mejora suele ser más difícil y costoso.\n\nPor ejemplo:\n\n| Alternativa | Costo | Mejora estimada |\n| --- | --- | --- |\n| Sellar encuentros y filtraciones | $500.000 | 5 dB |\n| Mejorar puerta y ventana | $2.000.000 | 10 dB |\n| Construir una segunda partición desacoplada | $5.000.000 | 15 dB |\n| Solución de máxima especificación | $9.000.000 | 17 dB |\n\nLa última alternativa cuesta mucho más, pero solo entrega 2 dB adicionales. Esto permitirá introducir el concepto de rendimiento decreciente de la inversión.\n\n3. Costo por decibel de mejora\n\nComo indicador comparativo simple, puede calcularse:\n\nEste indicador sirve para comparar alternativas, pero se aclarará que no basta por sí solo. También se debe comprobar:\n\nSi la solución permite cumplir el objetivo.\n\nSi actúa sobre la trayectoria dominante.\n\nSi es constructivamente viable.\n\nSi su desempeño se mantiene en el tiempo.\n\nLa alternativa más barata por decibel no será útil si no permite alcanzar el aislamiento mínimo requerido.\n\n4. ¿Qué es el ROI?\n\nEl ROI, o retorno de la inversión, expresa cuánto beneficio económico se obtiene en relación con el dinero invertido.\n\nExplicación sencilla:\n\nSi invertimos $5 millones y la solución genera o evita pérdidas por $7 millones, recuperamos los $5 millones y obtenemos un beneficio adicional de $2 millones.\n\nPor lo tanto, el retorno de la inversión es del 40 %.\n\n5. ¿De dónde proviene el beneficio acústico?\n\nEn acústica, el beneficio no siempre corresponde a nuevas ventas directas. También puede representar costos evitados:\n\nEvitar multas o sanciones.\n\nEvitar paralizaciones.\n\nReducir reclamos de la comunidad.\n\nEvitar rehacer una obra.\n\nAumentar la productividad.\n\nMejorar la concentración y comunicación.\n\nReducir errores asociados al ruido.\n\nPermitir que un recinto continúe funcionando.\n\nProteger la reputación de una empresa.\n\nAumentar el valor o la utilidad de un inmueble.\n\nAlgunos beneficios pueden calcularse monetariamente y otros deberán explicarse cualitativamente.\n\n6. Punto de equilibrio\n\nEl punto de equilibrio se alcanza cuando los beneficios acumulados igualan el costo de la inversión.\n\nEn ese momento:\n\nLa inversión ya se recuperó.\n\nTodavía no existe ganancia neta acumulada.\n\nDesde ese punto, los beneficios adicionales representan un retorno positivo.\n\nEjemplo:\n\nInversión acústica: $6.000.000.\n\nPérdidas evitadas mensualmente: $500.000.\n\nEl proyecto alcanza su punto de equilibrio al finalizar el mes 12.\n\n7. Diferencia entre ROI y recuperación de la inversión\n\n| Concepto | Pregunta que responde |\n| --- | --- |\n| Costo-beneficio | ¿Los beneficios justifican el costo? |\n| Costo por dB | ¿Cuánto cuesta cada decibel de mejora estimada? |\n| Punto de equilibrio | ¿Cuándo se recupera exactamente lo invertido? |\n| Periodo de recuperación o payback | ¿Cuánto tiempo demora en recuperarse la inversión? |\n| ROI | ¿Qué rentabilidad produce la inversión? |\n\n8. Visualización interactiva\n\nLa etapa puede incluir un simulador con tres alternativas acústicas. El alumno podrá modificar:\n\nCosto de inversión.\n\nMejora acústica estimada.\n\nBeneficio o pérdida evitada mensual.\n\nVida útil de la solución.\n\nObjetivo mínimo de aislamiento.\n\nLa aplicación mostrará automáticamente:\n\nCosto por dB.\n\nMes en que se alcanza el punto de equilibrio.\n\nBeneficio acumulado.\n\nROI al finalizar el periodo.\n\nSi la alternativa cumple o no el objetivo acústico.\n\nUn gráfico presentará dos líneas:\n\nCosto acumulado de la solución.\n\nBeneficios económicos acumulados.\n\nEl punto donde ambas líneas se cruzan será señalado como:\n\nPunto de equilibrio: inversión recuperada.\n\n9. Ejercicio aplicado\n\nSe presentarán tres soluciones para el ruido de una sala de máquinas. El alumno deberá seleccionar la alternativa más conveniente considerando simultáneamente:\n\nCumplimiento del objetivo acústico.\n\nInversión inicial.\n\nCosto por dB.\n\nTiempo de recuperación.\n\nROI.\n\nRiesgo de que la solución sea insuficiente.\n\nLa respuesta correcta no será necesariamente la alternativa más barata ni la que entregue más decibeles, sino la que:\n\nCumpla el objetivo acústico con un costo razonable y un beneficio justificable.\n\nLa etapa cerrará con esta idea:\n\nEl objetivo no es comprar la solución acústica más costosa, sino alcanzar el desempeño necesario con una inversión técnica y económicamente conveniente.', 5: '## Etapa 5 · Aplicación conceptual técnico-económica\n\nSerá la aplicación práctica de los conceptos vistos en la Etapa 4. No incorporará teoría nueva; evaluará si el alumno puede interpretar el costo-beneficio de distintas soluciones acústicas.\n\nDuración propuesta: 25 minutos\nPuntaje formativo: 10 puntos\n\nEl alumno deberá aplicar:\n\nCumplimiento del objetivo acústico.\n\nInversión total.\n\nMejora estimada en dB.\n\nCosto por dB.\n\nBeneficios o pérdidas evitadas.\n\nROI.\n\nPunto de equilibrio y periodo de recuperación.\n\nViabilidad técnica y económica.\n\nCaso interactivo\n\nUna sala de máquinas genera ruido hacia una oficina. Se necesita una reducción mínima de 10 dB. La empresa estima que resolver el problema evitará pérdidas por $500.000 mensuales.\n\n| Alternativa | Inversión | Mejora estimada |\n| --- | --- | --- |\n| A · Sellado de filtraciones | $1.500.000 | 6 dB |\n| B · Puerta acústica y sellado | $4.000.000 | 11 dB |\n| C · Partición desacoplada completa | $7.000.000 | 16 dB |\n\nEjercicios con tiempo y puntaje\n\nVerificar cumplimiento — 2 minutos, 2 puntos\nIdentificar qué alternativas alcanzan la reducción mínima de 10 dB.\n\nCalcular costo por dB — 4 minutos, 2 puntos\nComparar el rendimiento económico de las tres alternativas.\n\nDeterminar el punto de equilibrio — 4 minutos, 2 puntos\nCalcular en cuántos meses se recupera cada inversión mediante las pérdidas evitadas.\n\nInterpretar el ROI — 5 minutos, 2 puntos\nCalcular o seleccionar el ROI correcto para un periodo definido, por ejemplo, 24 meses.\n\nTomar una decisión profesional — 5 minutos, 2 puntos\nEscoger la alternativa más conveniente y justificarla considerando desempeño, costo y riesgo.\n\nDecisión esperada\n\nLa alternativa A sería económica, pero no cumple el objetivo acústico. La alternativa C entrega el mejor aislamiento, pero exige una inversión considerable. La alternativa B probablemente representa la mejor relación técnico-económica porque supera la meta con una inversión intermedia.\n\nNo obstante, la aplicación enseñará que esta decisión depende de los beneficios acumulados, la vida útil, el riesgo técnico y la confiabilidad de la mejora estimada.\n\nFuncionamiento interactivo\n\nTemporizador iniciado por el alumno.\n\nDatos visibles durante todo el caso.\n\nCalculadora integrada.\n\nGráfico de inversión frente a beneficios acumulados.\n\nPunto de equilibrio marcado automáticamente.\n\nRespuesta bloqueada después del envío.\n\nRetroalimentación inmediata.\n\nRegistro de puntaje y tiempo para la vista docente.\n\nLa etapa terminará con una síntesis personalizada, por ejemplo:\n\nCumples correctamente el objetivo acústico y calculas el punto de equilibrio, pero debes recordar que la alternativa con menor costo por dB no siempre es válida si no alcanza la reducción requerida.\n\nAsí, las etapas 4 y 5 formarán una unidad coherente: primero se enseñan los conceptos económicos y luego se aplican en una decisión acústica profesional.', 6: '## Etapa 6 · Fundamentos físicos del aislamiento acústico\n\nDuración propuesta: 45 minutos\n\nObjetivo\n\nQue el alumno comprenda:\n\nCómo se caracteriza un sonido mediante su frecuencia.\n\nCómo se mide la transmisión sonora por bandas.\n\nQué propiedades físicas controlan el aislamiento.\n\nCómo funciona la ley de la masa.\n\nQué representa la frecuencia crítica.\n\nCómo interpretar el coeficiente de transmisión y el índice de reducción sonora.\n\nPor qué el aislamiento cambia con la frecuencia.\n\n1. Frecuencia del sonido\n\nLa frecuencia indica cuántas oscilaciones se producen por segundo y se expresa en hercios:\n\nDonde:\n\n: frecuencia, en Hz.\n\n: periodo de la oscilación, en segundos.\n\nLa frecuencia se relaciona con la percepción del tono:\n\nFrecuencias bajas: sonidos graves.\n\nFrecuencias medias: gran parte de la voz humana.\n\nFrecuencias altas: sonidos agudos.\n\nTambién se introducirá la longitud de onda:\n\nDonde:\n\n: longitud de onda, en metros.\n\n: velocidad del sonido, aproximadamente en aire a 20 °C.\n\n: frecuencia, en Hz.\n\nEsto permitirá comprender por qué las bajas frecuencias son más difíciles de controlar: poseen longitudes de onda mayores y pueden excitar con mayor facilidad los elementos constructivos.\n\n2. Bandas de octava y tercios de octava\n\nEl aislamiento no debe evaluarse mediante un único nivel global, porque una pared no se comporta igual frente a todas las frecuencias.\n\nBandas de octava\n\nEn una banda de octava, la frecuencia superior es aproximadamente el doble de la inferior. Sus frecuencias centrales habituales son:\n\nBandas de tercio de octava\n\nCada octava se divide en tres bandas, lo que entrega mayor resolución. Algunas frecuencias centrales son:\n\nLa aplicación mostrará una señal y permitirá alternar entre:\n\nNivel global.\n\nBandas de octava.\n\nBandas de tercio de octava.\n\nLa idea central será:\n\nUna solución puede aislar adecuadamente en frecuencias medias y altas, pero presentar un desempeño deficiente en bajas frecuencias.\n\n3. Propiedades físicas del elemento constructivo\n\nAntes de estudiar la ley de la masa, deben explicarse las propiedades que caracterizan una partición.\n\nDensidad\n\nLa densidad representa la masa contenida por unidad de volumen:\n\nSe expresa normalmente en .\n\nEspesor\n\nEl espesor corresponde a la distancia entre las dos caras del elemento. Se expresa en metros o milímetros.\n\nEl espesor influye en:\n\nLa masa superficial.\n\nLa rigidez a la flexión.\n\nLa frecuencia crítica.\n\nLa resistencia mecánica del elemento.\n\nMasa superficial\n\nLa masa superficial es la masa del elemento por unidad de área:\n\nDonde:\n\n: masa superficial, en .\n\n: densidad, en .\n\n: espesor, en metros.\n\nEjemplo:\n\nUna placa de densidad y espesor tendrá:\n\nLa masa superficial será uno de los parámetros principales de la ley de la masa.\n\n4. Módulo de Young y rigidez del material\n\nMódulo de Young\n\nEl módulo de Young representa la resistencia de un material a deformarse elásticamente.\n\nUn módulo de Young alto corresponde a un material más rígido.\n\nUn módulo bajo corresponde a un material más flexible.\n\nSe expresa en pascales:\n\nNo indica directamente cuánto aísla un material. Su efecto aparece principalmente en la respuesta vibratoria, la rigidez a la flexión y la frecuencia crítica.\n\nCoeficiente de Poisson\n\nEl coeficiente de Poisson describe la deformación transversal que experimenta un material al ser sometido a una deformación longitudinal. Es necesario para calcular con mayor precisión la rigidez a la flexión.\n\nRigidez a la flexión\n\nPara una placa homogénea:\n\nDonde:\n\n: rigidez a la flexión.\n\n: módulo de Young.\n\n: espesor.\n\n: coeficiente de Poisson.\n\nDebe destacarse que el espesor aparece elevado al cubo. Por lo tanto, un pequeño aumento del espesor puede producir un incremento importante de la rigidez.\n\n5. Coeficiente de transmisión sonora\n\nCuando el sonido incide sobre una partición, una pequeña fracción de la energía logra atravesarla.\n\nEl coeficiente de transmisión sonora se define como:\n\nDonde:\n\n: potencia sonora transmitida.\n\n: potencia sonora incidente.\n\n: coeficiente de transmisión, sin unidad.\n\nSu valor se encuentra entre 0 y 1:\n\n: se transmite toda la energía.\n\n: se transmite el 10 %.\n\n: se transmite el 1 %.\n\n: se transmite el 0,1 %.\n\nMientras menor sea , mayor será el aislamiento.\n\n6. Índice de reducción sonora\n\nEl índice de reducción sonora expresa en decibeles la capacidad de un elemento para reducir la transmisión sonora:\n\nEjemplos:\n\n| Coeficiente | Energía transmitida | Índice |\n| --- | --- | --- |\n| 0,1 | 10 % | 10 dB |\n| 0,01 | 1 % | 20 dB |\n| 0,001 | 0,1 % | 30 dB |\n| 0,0001 | 0,01 % | 40 dB |\n\nSe aclarará que debe expresarse por banda de frecuencia:\n\nPor eso, el desempeño real se representa mediante una curva de aislamiento acústico.\n\nTambién se anticiparán brevemente los indicadores únicos:\n\n: índice ponderado de reducción sonora.\n\nSTC: clasificación utilizada principalmente bajo criterios ASTM.\n\ny : términos de adaptación espectral.\n\nEstos indicadores podrán desarrollarse posteriormente; en esta etapa lo fundamental es comprender primero la curva .\n\n7. Ley de la masa\n\nLa ley de la masa describe aproximadamente el comportamiento de una partición simple, homogénea y estanca en una determinada región de frecuencias.\n\nUna expresión simplificada es:\n\nDonde:\n\n: índice de reducción sonora, en dB.\n\n: masa superficial, en .\n\n: frecuencia, en Hz.\n\nInterpretación\n\nSegún este modelo:\n\nAl duplicar la masa superficial, el aislamiento aumenta aproximadamente 6 dB.\n\nAl duplicar la frecuencia, el aislamiento aumenta aproximadamente 6 dB.\n\nPor tanto:\n\nUna partición simple tiende a aislar mejor a medida que aumenta su masa superficial y la frecuencia del sonido.\n\nSe advertirá que esta es una aproximación y no describe por sí sola todo el comportamiento real.\n\nDemostración interactiva\n\nEl alumno podrá modificar:\n\nDensidad.\n\nEspesor.\n\nMasa superficial.\n\nFrecuencia.\n\nLa aplicación calculará y mostrará la curva estimada. Al duplicar la masa o la frecuencia, aparecerá visualmente el aumento aproximado de 6 dB.\n\n8. Regiones de comportamiento de una partición simple\n\nLa ley de la masa no se cumple exactamente en todas las frecuencias. La curva real puede organizarse en distintas regiones:\n\nRegión controlada por la rigidez: predominante en bajas frecuencias.\n\nRegión de resonancia: pueden producirse pérdidas de aislamiento.\n\nRegión controlada por la masa: el aislamiento aumenta aproximadamente 6 dB por octava.\n\nRegión de coincidencia: aparece una disminución alrededor de la frecuencia crítica.\n\nRegión posterior a la coincidencia: el aislamiento vuelve a aumentar.\n\nEsto permitirá que el alumno entienda por qué una curva medida no es una línea recta perfecta.\n\n9. Frecuencia crítica y efecto de coincidencia\n\nLa frecuencia crítica es aquella a partir de la cual puede producirse una coincidencia eficiente entre las ondas sonoras del aire y las ondas de flexión que se propagan por la placa.\n\nDe manera simplificada:\n\nEn la frecuencia crítica, el sonido puede excitar muy eficazmente la vibración del elemento, aumentando la transmisión y disminuyendo temporalmente el aislamiento.\n\nUna expresión general para una placa homogénea es:\n\nDonde:\n\n: frecuencia crítica.\n\n: velocidad del sonido en el aire.\n\n: masa superficial.\n\n: rigidez a la flexión.\n\nLa frecuencia crítica depende de:\n\nDensidad.\n\nEspesor.\n\nMódulo de Young.\n\nCoeficiente de Poisson.\n\nRigidez a la flexión.\n\nLa aplicación mostrará una curva de aislamiento con una caída visible alrededor de , denominada valle de coincidencia.\n\n10. Amortiguamiento interno\n\nEl amortiguamiento o factor de pérdidas describe la capacidad del material o sistema para disipar la energía vibratoria.\n\nUn mayor amortiguamiento puede:\n\nReducir la amplitud de las resonancias.\n\nSuavizar el valle de coincidencia.\n\nMejorar el comportamiento en determinadas bandas.\n\nEsto ayudará a explicar por qué dos elementos con masa superficial semejante pueden presentar curvas de aislamiento diferentes.\n\n11. Absorción acústica y superficie de absorción equivalente\n\nPara no mezclar conceptos, se recordará que la absorción no corresponde al aislamiento de la partición.\n\nEl coeficiente de absorción se define como:\n\nDonde:\n\n: energía o potencia no reflejada por absorción.\n\n: energía incidente.\n\n: coeficiente de absorción.\n\nLa superficie de absorción equivalente de un recinto es:\n\nDonde:\n\n: área de absorción equivalente, en sabin.\n\n: coeficiente de absorción de cada superficie.\n\n: área de cada superficie.\n\nEsta magnitud se relaciona con el tiempo de reverberación estudiado en la Etapa 2:\n\nSe explicará que, en mediciones de laboratorio, la absorción del recinto receptor forma parte del procedimiento para determinar , pero no significa que el coeficiente sea un indicador de aislamiento.\n\n12. Relación lógica entre los parámetros\n\n| Tipo | Parámetros | Función |\n| --- | --- | --- |\n| Sonido | , , bandas de octava y tercio | Describen el contenido frecuencial |\n| Material | , , , amortiguamiento | Describen sus propiedades físicas |\n| Elemento | , , , | Describen su comportamiento constructivo y vibratorio |\n| Transmisión | , , , STC | Describen cuánto sonido atraviesa |\n| Acústica interior | , , | Describen absorción y reverberación |\n\nVisual interactivo principal\n\nLa etapa tendrá un simulador de una placa simple con controles para:\n\nMaterial.\n\nDensidad.\n\nEspesor.\n\nMódulo de Young.\n\nCoeficiente de Poisson.\n\nAmortiguamiento.\n\nFrecuencia.\n\nEl simulador mostrará automáticamente:\n\nMasa superficial.\n\nRigidez a la flexión.\n\nFrecuencia crítica estimada.\n\nCoeficiente de transmisión.\n\nÍndice de reducción sonora.\n\nCurva de aislamiento por tercio de octava.\n\nZona controlada por masa.\n\nValle de coincidencia.\n\nLa etapa cerrará con esta idea:\n\nEl aislamiento de una partición no depende solamente de que el material sea “pesado”. Depende de la interacción entre masa superficial, frecuencia, rigidez, amortiguamiento, resonancias, frecuencia crítica y condiciones constructivas reales.\n\nHa pensado durante 21s', 7: '## Etapa 7 · Aplicación práctica del aislamiento acústico\n\nDuración propuesta: 35 minutos\nPuntaje: 20 puntos\nModalidad: ejercicios interactivos con tiempo, calculadora integrada y retroalimentación inmediata.\n\nObjetivo\n\nQue el alumno pueda:\n\nInterpretar frecuencias y bandas de octava o tercio de octava.\n\nCalcular la masa superficial de una partición.\n\nAplicar e interpretar la ley de la masa.\n\nRelacionar el coeficiente de transmisión con el índice .\n\nIdentificar la frecuencia crítica y el valle de coincidencia.\n\nInterpretar una curva de aislamiento.\n\nDiferenciar parámetros de aislamiento y absorción.\n\nComparar técnicamente materiales y soluciones constructivas.\n\nEjercicio 1 · Frecuencia y bandas\n\nTiempo: 4 minutos · 2 puntos\n\nEl alumno observará un espectro y deberá:\n\nReconocer frecuencias graves, medias y agudas.\n\nIdentificar bandas de octava y tercio de octava.\n\nDeterminar en qué banda existe una mayor transmisión sonora.\n\nExplicar por qué un valor global no describe completamente el aislamiento.\n\nEjercicio 2 · Masa superficial\n\nTiempo: 4 minutos · 3 puntos\n\nSe entregarán la densidad y el espesor de una placa:\n\nEl alumno deberá calcular:\n\nTambién deberá comparar dos placas y seleccionar cuál posee mayor masa superficial.\n\nLa retroalimentación advertirá sobre el error frecuente de utilizar el espesor en milímetros sin convertirlo a metros.\n\nEjercicio 3 · Aplicación de la ley de la masa\n\nTiempo: 5 minutos · 3 puntos\n\nUtilizando:\n\nel alumno deberá estimar para una masa superficial y una frecuencia determinadas.\n\nLuego utilizará un simulador para observar qué ocurre al:\n\nDuplicar la masa superficial.\n\nDuplicar la frecuencia.\n\nDuplicar simultáneamente ambas variables.\n\nResultados conceptuales esperados:\n\nDuplicar la masa: aproximadamente .\n\nDuplicar la frecuencia: aproximadamente .\n\nDuplicar ambas: aproximadamente .\n\nSe recordará que estos resultados corresponden a la región controlada por la masa y no necesariamente al comportamiento completo de una partición real.\n\nEjercicio 4 · Coeficiente de transmisión e índice\n\nTiempo: 5 minutos · 3 puntos\n\nEl alumno relacionará los siguientes valores:\n\n|  | Energía transmitida |  |\n| --- | --- | --- |\n| 0,1 | 10 % | 10 dB |\n| 0,01 | 1 % | 20 dB |\n| 0,001 | 0,1 % | 30 dB |\n| 0,0001 | 0,01 % | 40 dB |\n\nDespués deberá responder preguntas como:\n\nSi una partición tiene , ¿qué fracción de la energía incidente transmite?\n\nRespuesta:\n\nPor lo tanto, transmite aproximadamente el 0,1 % de la energía incidente.\n\nEjercicio 5 · Rigidez y frecuencia crítica\n\nTiempo: 4 minutos · 2 puntos\n\nSe presentarán dos materiales con distinta:\n\nDensidad.\n\nEspesor.\n\nMódulo de Young.\n\nRigidez a la flexión.\n\nFrecuencia crítica.\n\nEl alumno deberá identificar cómo se relacionan estos parámetros y reconocer que:\n\nEl módulo de Young no entrega directamente el aislamiento.\n\nEl espesor afecta simultáneamente la masa superficial y la rigidez.\n\nLa rigidez a la flexión aumenta con .\n\nLa frecuencia crítica depende de la relación entre masa superficial y rigidez.\n\nNo será necesario desarrollar manualmente cálculos complejos de o ; se evaluará principalmente su interpretación física.\n\nEjercicio 6 · Interpretación de la curva de aislamiento\n\nTiempo: 5 minutos · 3 puntos\n\nSe mostrará una curva por tercios de octava. El alumno deberá marcar:\n\nLa zona de bajas frecuencias.\n\nLa región controlada por la masa.\n\nEl valle de coincidencia.\n\nLa frecuencia crítica aproximada.\n\nLa banda con menor aislamiento.\n\nLa banda con mayor aislamiento.\n\nTambién deberá explicar por qué la curva real no coincide completamente con la línea teórica de la ley de la masa.\n\nEjercicio 7 · Aislamiento o absorción\n\nTiempo: 3 minutos · 2 puntos\n\nEl alumno clasificará cada parámetro:\n\n| Parámetro | Fenómeno principal |\n| --- | --- |\n|  | Aislamiento |\n|  | Transmisión sonora |\n|  | Elemento constructivo |\n|  | Comportamiento vibratorio |\n|  | Absorción |\n|  | Absorción equivalente del recinto |\n|  | Reverberación |\n|  | Aislamiento ponderado |\n\nEsto reforzará que y no son indicadores directos del aislamiento de una partición.\n\nEjercicio 8 · Mini caso integrador\n\nTiempo: 5 minutos · 2 puntos\n\nCaso:\n\nUna sala de máquinas emite principalmente ruido en 125 Hz y 250 Hz. Se comparan dos particiones: una liviana con buen desempeño en frecuencias medias y otra de mayor masa superficial con mejor respuesta en bajas frecuencias. Sin embargo, esta última presenta un valle de coincidencia en frecuencias altas.\n\nEl alumno deberá:\n\nRevisar las curvas de ambas soluciones.\n\nIdentificar las bandas críticas de la fuente.\n\nSeleccionar la partición más apropiada.\n\nJustificar su elección usando la información espectral.\n\nLa enseñanza central será:\n\nNo debe elegirse una partición únicamente por su ; también debe compararse su curva de aislamiento con el espectro de la fuente sonora.\n\nFuncionamiento de la etapa\n\nLa aplicación incluirá:\n\nTemporizador independiente por ejercicio.\n\nBarra de avance.\n\nCalculadora científica integrada.\n\nConversión asistida de unidades.\n\nGráficos interactivos.\n\nRespuestas bloqueadas después del envío.\n\nPuntaje parcial para procedimientos correctos.\n\nRetroalimentación inmediata.\n\nRegistro del tiempo, respuesta y resultado.\n\nResumen final de fortalezas y conceptos por reforzar.\n\nUn error aritmético menor no debería anular completamente una respuesta si el procedimiento y la interpretación son correctos.\n\nResultado final personalizado\n\nAl terminar, el alumno recibirá una síntesis como:\n\nObtuviste 16 de 20 puntos. Calculas correctamente la masa superficial y relacionas con . Debes reforzar la identificación del valle de coincidencia y recordar que la ley de la masa solo representa una región del comportamiento real.', 8: '## Etapa 8 · Índices globales de aislamiento acústico\n\nDuración propuesta: 45 minutos\nCarácter: contenido teórico con demostraciones interactivas.\n\nEsta etapa enseñará cómo una curva de aislamiento por bandas de frecuencia se transforma en un valor único. El alumno deberá comprender que , STC y los demás índices simplifican la información, pero no reemplazan completamente la curva espectral.\n\nObjetivos\n\nAl finalizar, el alumno podrá:\n\nDiferenciar una curva de un índice global.\n\nComprender cómo se obtiene .\n\nInterpretar los términos y .\n\nComparar conceptualmente y STC.\n\nDistinguir resultados de laboratorio y mediciones en terreno.\n\nReconocer los índices aplicables a elementos, recintos y fachadas.\n\nSeleccionar el indicador adecuado según la fuente sonora.\n\nEvitar comparaciones incorrectas entre indicadores distintos.\n\n1. De una curva a un valor único\n\nEn la Etapa 6 se explicó que el índice de reducción sonora varía con la frecuencia:\n\nUna partición puede tener, por ejemplo:\n\nen 125 Hz.\n\nen 500 Hz.\n\nen 2000 Hz.\n\nPor lo tanto, no existe inicialmente “un solo aislamiento”, sino una curva completa .\n\nPara facilitar:\n\nLa comparación de productos.\n\nLa especificación de proyectos.\n\nLa elaboración de requisitos normativos.\n\nLa comunicación entre fabricantes, proyectistas y clientes.\n\nSe utilizan índices globales o magnitudes de número único.\n\nUn índice global resume la curva en un número, pero inevitablemente pierde parte de la información espectral.\n\nEste número no se obtiene mediante un promedio aritmético de los valores de .\n\n2. Índice ponderado de reducción sonora\n\nEl es una magnitud de número único utilizada para caracterizar el aislamiento a ruido aéreo de un elemento constructivo ensayado en laboratorio.\n\nPuede aplicarse, por ejemplo, a:\n\nMuros.\n\nTabiques.\n\nEntrepisos.\n\nPuertas.\n\nVentanas.\n\nElementos de fachada.\n\nSe obtiene a partir de los valores del índice de reducción sonora medidos por bandas de tercio de octava conforme al procedimiento de referencia correspondiente.\n\nLa norma internacional vigente para su evaluación es ISO 717-1:2020.\n\nForma de expresión\n\nAunque suele expresarse en decibeles, debe explicarse que es una valoración obtenida mediante un procedimiento normalizado y no simplemente el aislamiento medido en una frecuencia determinada.\n\n3. ¿Cómo se determina ?\n\nSe utiliza una curva de referencia normalizada que se compara con la curva medida.\n\nEl procedimiento conceptual será:\n\nSe obtiene la curva por tercios de octava.\n\nSe superpone la curva de referencia de ISO 717-1.\n\nLa curva de referencia se desplaza verticalmente.\n\nSe calculan las desviaciones desfavorables.\n\nSe busca la posición más alta que cumpla el límite establecido para la suma de esas desviaciones.\n\nEl valor de la curva desplazada en 500 Hz corresponde al .\n\nPara el intervalo habitual de 100 a 3150 Hz, la suma de las desviaciones desfavorables no puede superar 32 dB.\n\nDesviación desfavorable\n\nExiste una desviación desfavorable cuando el valor medido está por debajo de la curva de referencia:\n\nLa aplicación no debe presentar el como el promedio de todos los valores de la curva.\n\nDemostración interactiva\n\nEl alumno podrá mover verticalmente la curva de referencia y observar:\n\nLas bandas con desviaciones desfavorables.\n\nLa suma de las desviaciones.\n\nCuándo se cumple o incumple el criterio.\n\nEl valor resultante de .\n\n4. ¿Qué información oculta el ?\n\nDos particiones pueden tener el mismo , pero curvas muy diferentes.\n\nPor ejemplo:\n\n| Banda | Partición A | Partición B |\n| --- | --- | --- |\n| 125 Hz | 25 dB | 36 dB |\n| 500 Hz | 45 dB | 42 dB |\n| 2000 Hz | 55 dB | 47 dB |\n| Resultado global | dB | dB |\n\nLa partición A tiene mejor desempeño en frecuencias altas, mientras que la B presenta mejor respuesta en bajas frecuencias.\n\nPor eso:\n\nUn mayor no garantiza automáticamente la mejor solución para cualquier fuente sonora.\n\nSiempre que la fuente tenga un espectro particular —maquinaria, bajos musicales, grupos electrógenos o tráfico— debe revisarse también la curva por bandas.\n\n5. Términos de adaptación espectral y\n\nEl puede complementarse con términos de adaptación espectral que consideran diferentes tipos de ruido.\n\nTérmino\n\nSe utiliza para espectros con una proporción relativamente importante de frecuencias medias y altas, como:\n\nConversaciones.\n\nActividades domésticas.\n\nRadio y televisión.\n\nJuegos infantiles.\n\nCiertos tipos de tránsito rápido.\n\nRuido de trenes a velocidades medias o altas.\n\nEjemplo:\n\nPor lo tanto:\n\nTérmino\n\nDa mayor importancia al ruido con contenido significativo de bajas frecuencias, como:\n\nTránsito urbano.\n\nCamiones.\n\nBuses.\n\nAeronaves a cierta distancia.\n\nMúsica con bajos intensos.\n\nAlgunas fuentes industriales.\n\nEn el ejemplo:\n\nLa partición posee un de 48 dB, pero frente a un espectro semejante al tránsito su valoración adaptada disminuye a 42 dB.\n\nInterpretación fundamental\n\ny normalmente son cero o negativos.\n\nNo son aislamientos independientes.\n\nDeben sumarse algebraicamente al .\n\nMientras más negativo sea , más débil puede ser el desempeño relativo frente a fuentes con bajas frecuencias.\n\n6. Diferencia entre , y\n\n| Indicador | Uso principal |\n| --- | --- |\n|  | Valor global general del elemento |\n|  | Evaluación adaptada a fuentes predominantemente medias y altas |\n|  | Evaluación adaptada a tránsito y fuentes con mayor contenido grave |\n\nEjemplo:\n\nEntonces:\n\nEl alumno deberá entender que anunciar únicamente “52 dB de aislamiento” puede resultar insuficiente si el problema real corresponde a tránsito pesado o música con bajos.\n\n7. Sound Transmission Class — STC\n\nLa Sound Transmission Class, o STC, es el indicador utilizado principalmente en Norteamérica para clasificar el aislamiento frente al ruido aéreo.\n\nSe determina mediante el procedimiento de ASTM E413 a partir de valores de pérdida por transmisión sonora medidos en bandas de tercio de octava. Para laboratorio, estos datos suelen proceder de ASTM E90.\n\nEl procedimiento considera normalmente las bandas desde 125 hasta 4000 Hz.\n\nAl igual que con :\n\nSe utiliza una curva de referencia.\n\nLa curva se desplaza verticalmente.\n\nSe calculan las deficiencias respecto de los valores medidos.\n\nEl resultado corresponde a un número único.\n\nASTM E413 establece además límites para las deficiencias: en su edición activa, la suma no debe exceder 32 dB y ninguna deficiencia individual puede superar 8 dB. ASTM E413-22\n\n8. Comparación entre y STC\n\n| Característica |  | STC |\n| --- | --- | --- |\n| Sistema normativo | ISO | ASTM |\n| Norma de clasificación | ISO 717-1 | ASTM E413 |\n| Intervalo habitual | 100–3150 Hz | 125–4000 Hz |\n| Datos utilizados | Tercios de octava | Tercios de octava |\n| Uso frecuente | Europa, Latinoamérica y otros países | Estados Unidos y Canadá |\n| Adaptación espectral | y | No incorporada de la misma forma |\n| Resultado | Número único ponderado | Clase numérica |\n\nPara muchas particiones, ambos resultados pueden ser próximos, pero no son equivalentes ni deben convertirse mediante una resta o suma fija. ASTM señala que, para muchas particiones, la diferencia puede ser de uno o dos puntos, pero esto no constituye una regla universal. ASTM E413-22\n\nNo debe afirmarse automáticamente que .\n\nLa diferencia puede aumentar cuando la curva presenta:\n\nBajo aislamiento en 100 Hz.\n\nValles pronunciados.\n\nCoincidencia dentro del intervalo de evaluación.\n\nComportamientos espectrales irregulares.\n\n9. Laboratorio frente a terreno\n\nEsta distinción debe ocupar una sección central de la etapa.\n\n: elemento ensayado en laboratorio\n\nRepresenta el desempeño del elemento bajo condiciones controladas:\n\nCámaras de ensayo.\n\nMontaje definido.\n\nDimensiones determinadas.\n\nMenor influencia de transmisiones laterales.\n\nSellado y ejecución cuidadosamente controlados.\n\n: aislamiento aparente en terreno\n\nEl símbolo prima indica que el resultado incluye el comportamiento del elemento instalado y las transmisiones presentes en el edificio.\n\nPuede verse afectado por:\n\nTransmisiones laterales o flanking.\n\nEncuentros con pisos y cielos.\n\nDuctos y canalizaciones.\n\nCajas eléctricas.\n\nFisuras y filtraciones.\n\nPuertas o ventanas débiles.\n\nDeficiencias de montaje.\n\nNormalmente:\n\npero no debe establecerse una diferencia fija universal, porque depende completamente de la construcción.\n\n10. Diferencia de niveles estandarizada\n\nEn terreno también puede evaluarse la diferencia de niveles entre dos recintos.\n\nPor banda:\n\nDonde:\n\n: nivel medio en el recinto emisor.\n\n: nivel medio en el recinto receptor.\n\nSin embargo, el nivel del recinto receptor depende de su absorción y tiempo de reverberación. Por eso se emplea una corrección:\n\nDonde:\n\n: tiempo de reverberación medido en el recinto receptor.\n\n: tiempo de reverberación de referencia, habitualmente en viviendas.\n\n: diferencia de niveles estandarizada.\n\nSu número único ponderado es:\n\nEste indicador representa el aislamiento entre recintos como experiencia del edificio, no la propiedad exclusiva de una pared.\n\n11. Diferencia de niveles normalizada\n\nTambién puede normalizarse la diferencia de niveles mediante el área de absorción equivalente:\n\nDonde:\n\n: área de absorción equivalente del recinto receptor.\n\n: área de absorción de referencia, generalmente .\n\nSu valor ponderado se expresa como:\n\nLa diferencia principal es:\n\n: estandariza mediante tiempo de reverberación.\n\n: normaliza mediante absorción equivalente.\n\n12. Índices de fachada\n\nPara fachadas se utilizan indicadores específicos, porque la fuente se encuentra en el exterior y la medición depende también de la posición del micrófono exterior.\n\nUno de los principales es:\n\nRepresenta la diferencia de niveles de una fachada, estandarizada por tiempo de reverberación, con el nivel exterior medido aproximadamente a 2 metros de la fachada.\n\nTambién puede expresarse con adaptaciones espectrales:\n\nPara fachadas expuestas a tránsito, normalmente será especialmente relevante:\n\n13. OITC para ruido exterior\n\nLa Outdoor-Indoor Transmission Class se emplea principalmente bajo el sistema ASTM para evaluar elementos de fachada frente a fuentes de transporte exterior.\n\nSu espectro de referencia contiene una proporción importante de bajas frecuencias y considera datos entre 80 y 4000 Hz.\n\nSe utiliza para:\n\nFachadas.\n\nVentanas.\n\nPuertas exteriores.\n\nMuros exteriores.\n\nSistemas combinados de envolvente.\n\nLa OITC puede ser más representativa que STC cuando el problema corresponde a:\n\nTránsito vehicular.\n\nFerrocarriles.\n\nAeronaves.\n\nFuentes exteriores con contenido grave.\n\nASTM advierte que dos elementos con igual OITC pueden producir espectros interiores diferentes y que debe revisarse la curva cuando el ruido real difiere del espectro de referencia. ASTM E1332-22\n\n14. Otros indicadores que deben presentarse\n\n| Indicador | Qué representa | Contexto |\n| --- | --- | --- |\n|  | Reducción sonora ponderada de un elemento | Laboratorio |\n|  | Reducción sonora aparente ponderada | Terreno |\n|  | Diferencia de niveles estandarizada | Entre recintos |\n|  | Diferencia de niveles normalizada | Entre recintos |\n|  | Diferencia estandarizada de fachada | Fachadas |\n| STC | Clasificación de transmisión sonora | Sistema ASTM |\n| ASTC | STC aparente de una construcción instalada | Terreno, ASTM |\n| NIC | Clase de aislamiento entre espacios | Terreno, ASTM |\n| OITC | Aislamiento exterior-interior | Fachadas, ASTM |\n| CAC | Atenuación a través de cielos y plenums compartidos | Cielos suspendidos |\n|  | Adaptación para espectros medios-altos | Complementa índices ISO |\n|  | Adaptación para tránsito y contenido grave | Complementa índices ISO |\n\n15. Lo que no debe confundirse\n\nno es\n\n: resultado en cada banda.\n\n: valoración única obtenida desde toda la curva.\n\nno es\n\n: propiedad del elemento en laboratorio.\n\n: aislamiento global entre dos recintos terminados.\n\nno es\n\n: laboratorio.\n\n: terreno, incluyendo transmisiones laterales.\n\nSTC no es OITC\n\nSTC: particiones y ruido interior general.\n\nOITC: fachadas y ruido exterior con mayor contenido de bajas frecuencias.\n\nno es absorción\n\nUn muro puede presentar:\n\n: aislamiento.\n\n: absorción superficial.\n\nSon propiedades diferentes y no pueden compararse entre sí.\n\n16. Cómo interpretar una ficha técnica\n\nLa etapa mostrará una ficha como esta:\n\nTabique acústico:\nSTC 53\nEnsayo de laboratorio.\n\nEl alumno deberá interpretar:\n\n.\n\n.\n\n.\n\nSTC 53 corresponde a otro método de clasificación.\n\nEl resultado fue obtenido en laboratorio.\n\nNo garantiza que en obra se consigan 52 dB.\n\nPara tránsito o bajos intensos, el resultado de 45 dB puede ser más representativo que el aislado.\n\n17. Selección del indicador según el problema\n\n| Problema | Indicador principal recomendado |\n| --- | --- |\n| Comparar tabiques ensayados bajo ISO | , , |\n| Comparar tabiques bajo ASTM | STC |\n| Verificar aislamiento construido entre viviendas | o , según el requisito |\n| Evaluar fachada frente a tránsito |  |\n| Comparar ventanas bajo criterio estadounidense | OITC, además de STC |\n| Evaluar transmisión por cielo compartido | CAC |\n| Fuente industrial tonal o espectro particular | Curva completa por bandas, no solamente un índice único |\n\nVisual interactivo principal\n\nLa aplicación mostrará dos particiones con curvas modificables. El alumno podrá seleccionar:\n\nFuente de voz.\n\nMúsica.\n\nTránsito.\n\nMaquinaria.\n\nRuido de espectro medio-alto.\n\nRuido con predominio grave.\n\nLa aplicación presentará:\n\nCurva .\n\nCurva de referencia desplazable.\n\n.\n\ny .\n\nSTC estimado.\n\nOITC, cuando corresponda.\n\nBandas críticas de la fuente.\n\nDiferencia entre resultado de laboratorio y desempeño aparente.\n\nLa simulación debe demostrar que una partición puede ganar la comparación por , pero perderla frente a tránsito debido a su o a su bajo aislamiento en frecuencias graves.\n\nIdea de cierre\n\nLos índices únicos permiten comparar y especificar soluciones, pero solo son correctos cuando corresponden al método de ensayo, al lugar de medición y al espectro de la fuente. Una decisión profesional no debe basarse únicamente en el número más alto.', 9: '## Etapa 9 · Aplicación práctica de los índices de aislamiento\n\nDuración propuesta: 40 minutos\nPuntaje: 20 puntos\nModalidad: ejercicios interactivos, análisis de curvas y resolución de casos.\n\nObjetivos\n\nAl finalizar, el alumno podrá:\n\nDeterminar gráficamente el desde una curva .\n\nInterpretar correctamente y .\n\nComparar , STC y OITC sin tratarlos como equivalentes.\n\nDiferenciar índices de laboratorio, terreno y fachada.\n\nInterpretar fichas técnicas reales.\n\nElegir el índice apropiado según la fuente y el problema.\n\nReconocer cuándo debe analizarse la curva completa por bandas.\n\nEjercicio 1 · De la curva al\n\nTiempo: 7 minutos\nPuntaje: 4 puntos\n\nLa aplicación mostrará:\n\nLa curva medida entre 100 y 3150 Hz.\n\nLa curva de referencia de ISO 717-1.\n\nUn control para desplazar verticalmente la curva de referencia.\n\nLa desviación desfavorable de cada banda.\n\nLa suma de desviaciones.\n\nEl alumno deberá desplazar la curva hasta encontrar la posición más alta que cumpla el criterio establecido.\n\nPara cada banda:\n\nLuego deberá:\n\nIdentificar las bandas con desviaciones desfavorables.\n\nCalcular o verificar la suma de desviaciones.\n\nComprobar que no supere 32 dB.\n\nLeer en 500 Hz el valor de la curva de referencia desplazada.\n\nInformar el .\n\nLa retroalimentación aclarará que el :\n\nNo es el promedio de la curva.\n\nNo es necesariamente el valor medido en 500 Hz.\n\nCorresponde al valor de la curva de referencia desplazada en 500 Hz.\n\nEjercicio 2 · Interpretación de y\n\nTiempo: 4 minutos\nPuntaje: 3 puntos\n\nSe entregará el siguiente resultado:\n\nEl alumno deberá calcular:\n\nDespués responderá:\n\n¿Cuál es el ?\n52 dB\n\n¿Qué valor sería más representativo para conversación o actividades domésticas?\n\n¿Qué valor sería más representativo para tránsito urbano o una fuente con contenido grave?\n\n¿El valor corresponde al aislamiento de la partición?\nNo. Es un término de adaptación espectral.\n\nEjercicio 3 · Dos particiones con el mismo\n\nTiempo: 5 minutos\nPuntaje: 3 puntos\n\nSe compararán dos soluciones:\n\n| Indicador | Partición A | Partición B |\n| --- | --- | --- |\n|  | 50 dB | 50 dB |\n|  | −1 dB | −3 dB |\n|  | −8 dB | −4 dB |\n|  | 49 dB | 47 dB |\n|  | 42 dB | 46 dB |\n\nEl alumno deberá seleccionar:\n\nPara separar oficinas con predominio de voz: Partición A.\n\nPara una fachada expuesta a tránsito: Partición B.\n\nSi ambas son equivalentes por tener el mismo : No.\n\nLa aplicación mostrará las dos curvas para comprobar que la partición B presenta mejor comportamiento relativo en las bandas graves.\n\nDos soluciones con el mismo pueden responder de forma diferente frente a una fuente determinada.\n\nEjercicio 4 · frente a STC\n\nTiempo: 4 minutos\nPuntaje: 2 puntos\n\nSe presentará una ficha con:\n\nEl alumno deberá identificar las afirmaciones correctas:\n\nAmbos son indicadores de número único.\n\nSe obtienen mediante procedimientos normativos diferentes.\n\nSus intervalos de frecuencia no son idénticos.\n\nPueden entregar valores próximos para algunas particiones.\n\nNo existe una conversión fija y universal entre ambos.\n\nLa afirmación siguiente deberá marcarse como falsa:\n\nPara cualquier elemento, el STC siempre equivale a .\n\nLa aplicación mostrará dos curvas con valles diferentes para demostrar por qué una conversión fija puede fallar.\n\nEjercicio 5 · Laboratorio o terreno\n\nTiempo: 4 minutos\nPuntaje: 2 puntos\n\nEl alumno deberá asociar cada situación con el indicador correspondiente:\n\n| Situación | Indicador |\n| --- | --- |\n| Tabique ensayado en laboratorio |  |\n| Elemento instalado con transmisiones laterales |  |\n| Aislamiento global entre dos recintos, corregido por reverberación |  |\n| Fachada medida con micrófono exterior a 2 m |  |\n| Clasificación ASTM aparente en terreno | ASTC |\n| Fachada frente a ruido de transporte | OITC |\n\nDespués deberá responder:\n\nUn tabique posee en laboratorio, pero una vez instalado se mide . ¿El ensayo de laboratorio estaba necesariamente equivocado?\n\nRespuesta: No. La diferencia puede deberse a transmisiones laterales, encuentros, sellos, instalaciones, fisuras o errores de ejecución.\n\nEjercicio 6 · Seleccionar el índice correcto\n\nTiempo: 5 minutos\nPuntaje: 2 puntos\n\nSe mostrarán distintos problemas:\n\nCaso A: tabique entre oficinas\n\nFuente dominante: conversaciones.\n\nIndicadores relevantes:\n\nCaso B: fachada frente a avenida\n\nFuente dominante: buses y camiones.\n\nIndicadores relevantes:\n\no, bajo el sistema ASTM:\n\nCaso C: separación terminada entre departamentos\n\nIndicador relevante:\n\no , dependiendo del requisito normativo utilizado.\n\nCaso D: maquinaria con un tono dominante en 125 Hz\n\nRespuesta correcta:\n\nRevisar la curva completa por bandas, especialmente en 125 Hz. Un índice global no basta para evaluar una fuente tonal.\n\nEjercicio 7 · Interpretación de una ficha técnica\n\nTiempo: 5 minutos\nPuntaje: 2 puntos\n\nLa aplicación mostrará:\n\nTabique de doble estructura\nSTC 57\nEnsayo realizado en laboratorio\nCurva disponible entre 100 y 5000 Hz\n\nEl alumno deberá concluir:\n\n.\n\n.\n\n.\n\nSTC 57 no significa que el elemento aísle 57 dB en todas las frecuencias.\n\nEl resultado corresponde a laboratorio.\n\nNo garantiza el mismo desempeño en obra.\n\nPara una fuente grave debe revisarse y la curva por bandas.\n\nPara comparar con otro producto deben revisarse las normas y condiciones de ensayo.\n\nTambién deberá detectar información faltante:\n\nNorma de ensayo.\n\nConfiguración y dimensiones del sistema.\n\nTipo y separación de montantes.\n\nMaterial absorbente interior.\n\nSellado perimetral.\n\nCondiciones de montaje.\n\nLaboratorio responsable.\n\nNúmero y fecha del informe.\n\nEjercicio 8 · Caso integrador de selección\n\nTiempo: 6 minutos\nPuntaje: 2 puntos\n\nProblema\n\nUn dormitorio se encuentra junto a una avenida con tránsito de buses. Se comparan dos ventanas:\n\n| Indicador | Ventana A | Ventana B |\n| --- | --- | --- |\n|  | 42 dB | 40 dB |\n|  | −1 dB | −2 dB |\n|  | −8 dB | −3 dB |\n|  | 34 dB | 37 dB |\n| OITC | 31 | 35 |\n\nEl alumno deberá elegir la solución más apropiada.\n\nRespuesta esperada: Ventana B.\n\nAunque posee un menor, presenta:\n\nMejor .\n\nMayor OITC.\n\nMejor desempeño relativo frente al espectro de tránsito.\n\nMenor penalización en bajas frecuencias.\n\nLa enseñanza central será:\n\nEl producto con el más alto no siempre es el más adecuado para el problema real.\n\nFuncionamiento de la aplicación\n\nLa Etapa 9 incorporará:\n\nCurvas interactivas por tercios de octava.\n\nCurva de referencia desplazable.\n\nCálculo automático de desviaciones desfavorables.\n\nComparador de , STC y OITC.\n\nCalculadora de y .\n\nFichas técnicas simuladas.\n\nSelección de fuentes sonoras.\n\nRetroalimentación inmediata.\n\nPuntaje parcial por procedimiento.\n\nRegistro de respuestas y tiempo.\n\nResumen personalizado al finalizar.\n\nResultado final personalizado\n\nEjemplo:\n\nObtuviste 17 de 20 puntos. Interpretas correctamente y , y distingues los índices de laboratorio y terreno. Debes reforzar el desplazamiento de la curva de referencia para obtener y recordar que STC no se convierte a mediante una relación fija.', 10: '## Etapa 10 · Evaluación final del Curso 1\n\nCantidad total: 30 preguntas\n\nDistribución: 29 preguntas teórico-aplicadas y 1 caso práctico integrador.\n\nDuración propuesta: 60 minutos · Puntaje total: 100 puntos · Exigencia de aprobación: 60 %.\n\nLas primeras 29 preguntas suman 80 puntos. La pregunta 30 suma 20 puntos. La aplicación podrá aleatorizar el orden de las alternativas, bloquear cada respuesta después del envío y entregar retroalimentación al finalizar.\n\nDistribución temática\n\n• Principios de control del ruido y selección fuente–trayectoria–receptor: 4 preguntas.\n• Aislamiento, absorción, reverberación e inteligibilidad: 5 preguntas.\n• Análisis técnico-económico y costo-beneficio: 5 preguntas.\n• Fundamentos físicos e interpretación de curvas de aislamiento: 8 preguntas.\n• Índices globales, laboratorio, terreno y fachadas: 7 preguntas.\n• Caso práctico integrador: 1 pregunta.\n\nPreguntas 1 a 29'}

ACADEMIC_CONTENT[10] = ACADEMIC_CONTENT[10].replace(
    "Evaluación final del Curso 1",
    "Evaluación final · Aislamiento a Ruido Aéreo",
)

# Precisión conceptual de la Etapa 1: la distancia es una condición geométrica
# independiente, mientras que la barrera actúa directamente en la trayectoria.
ACADEMIC_CONTENT[1] = ACADEMIC_CONTENT[1].replace(
    "| Trayectoria | Barreras, cerramientos, silenciadores, aumento de distancia, sellado y tratamiento de ductos |",
    "| Trayectoria | Barrera acústica interpuesta en el camino de propagación |",
).replace(
    "| Receptor | Cabina acústica, fachada aislante, redistribución del espacio, alejamiento o protección auditiva |",
    "| Receptor | Protección auditiva, cabina acústica o mejora del aislamiento de fachada |",
).replace(
    "Trayectoria: aparece una barrera o cerramiento; las ondas se bloquean, desvían y atenúan.",
    "Trayectoria: aparece una barrera acústica; las ondas se bloquean, desvían y atenúan.",
)


# La sesión completa dura 4 horas: 230 minutos de trabajo y 10 minutos de pausa.



def stage_overview(*args, **kwargs):
    return _ui_components.run_component('stage_overview', globals(), *args, **kwargs)

def header(*args, **kwargs):
    return _ui_components.run_component('header', globals(), *args, **kwargs)

def image_data_uri(*args, **kwargs):
    return _ui_components.run_component('image_data_uri', globals(), *args, **kwargs)

def institutional_header(*args, **kwargs):
    return _ui_components.run_component('institutional_header', globals(), *args, **kwargs)

def _academic_blocks(*args, **kwargs):
    return _ui_components.run_component('_academic_blocks', globals(), *args, **kwargs)

def _student_card_body(*args, **kwargs):
    return _ui_components.run_component('_student_card_body', globals(), *args, **kwargs)

STUDENT_LESSONS = {
1:[
("¿Qué es el ruido?","Es un sonido que resulta no deseado, molesto o perjudicial en un contexto determinado. La misma señal puede ser útil para una persona y ruido para otra.","Observe que la calificación depende de la fuente, el momento, el lugar y el receptor.","stage1_noise.webp",None),
("Control de ruido","Es el conjunto de medidas destinadas a reducir la generación, la propagación o la recepción del sonido no deseado.","Antes de elegir una solución, identifique dónde nace el problema y cuál es su vía dominante.","stage1_noise_control.webp",None),
("Fuente → trayectoria → receptor","La fuente genera energía sonora; la trayectoria es el camino aéreo o estructural; el receptor es la persona o recinto afectado.","Una medida es eficaz cuando actúa sobre el mecanismo que realmente domina la exposición.","stage1_source_path_receiver.webp",None),
("Propagación aérea","La presión acústica se propaga por el aire desde la fuente. Con distancia y obstáculos, el nivel puede disminuir, aunque el entorno modifica esa atenuación.","Siga las ondas azules desde la máquina hasta el receptor.","stage1_airborne.webp",None),
("Propagación estructural","La vibración entra a pisos, muros o soportes y puede radiar sonido en otro punto del edificio.","La vía naranja recorre el sólido y vuelve a radiar energía en el recinto receptor.","stage1_structure_borne.webp",None),
("Reflexión, absorción y transmisión","Al llegar a una superficie, una parte de la energía vuelve, otra se disipa y otra atraviesa el elemento.","La energía incidente se reparte: no confunda absorción superficial con aislamiento entre recintos.","stage1_energy_split.webp",None),
("¿Dónde intervenir?","En la fuente: mantenimiento, encapsulamiento o antivibratorios. En la trayectoria: barrera acústica. En el receptor: protección auditiva, cabina o mejora de fachada. La distancia es una condición geométrica independiente.","Priorice la fuente cuando sea viable y compruebe siempre la vía dominante.","stage1_interventions.webp",None),
],
2:[
("Aislamiento acústico","Capacidad de un muro, puerta, ventana, piso o techo para reducir el sonido transmitido desde un recinto emisor hacia otro receptor. Se evalúa comparando lo que incide con lo que logra atravesar la separación.","Observe el panel central: las ondas son intensas en el recinto emisor y mucho más débiles después de atravesarlo.","stage2_insulation.png",None),
("Absorción acústica","Capacidad de una superficie para disipar parte de la energía sonora incidente y reducir las reflexiones dentro del mismo recinto. No equivale a impedir el paso del sonido a otro espacio.","Compare el sector rígido, con muchas reflexiones, con el sector tratado, donde la energía se disipa en paneles y nubes acústicas.","stage2_absorption.png",None),
("Tiempo de reverberación","T₆₀ es el tiempo necesario para que el nivel sonoro decaiga 60 dB después de detener la fuente. Si el volumen se mantiene, aumentar la absorción equivalente normalmente reduce ese tiempo.","Siga cómo las reflexiones pierden intensidad progresivamente después de que la fuente deja de emitir.","stage2_reverberation.png",None),
("Inteligibilidad de la palabra","Expresa cuánto del mensaje hablado puede comprender el receptor. Depende del sonido directo, las reflexiones tardías, el ruido de fondo, la distancia y la relación señal/ruido.","Distinga la señal directa y nítida de las reflexiones tardías que llegan superpuestas y reducen la claridad.","stage2_intelligibility.png",None),
],
4:[
("Suficiencia antes que rentabilidad","Una alternativa solo entra a la comparación económica si alcanza el objetivo acústico y actúa sobre la vía dominante. Primero se verifica el desempeño; después se optimiza el costo.","Compare las dos separaciones: la alternativa económicamente evaluable es la que realmente protege al receptor.","stage4_sufficiency.webp",None),
("Costo del ciclo de vida","El costo real incluye diseño, materiales, instalación, interrupciones, mantención, reposición y vida útil. Comparar solo el precio inicial puede cambiar equivocadamente la decisión.","Siga el ciclo completo alrededor del sistema constructivo: todas sus etapas generan costos o requerimientos.","stage4_lifecycle.webp",None),
("Rendimiento decreciente","Los primeros cambios pueden producir mejoras importantes, pero los últimos decibeles suelen exigir soluciones mucho más complejas y costosas. El máximo aislamiento no siempre entrega el mejor valor.","Observe cómo la complejidad continúa aumentando mientras la reducción adicional de ruido se hace cada vez menor.","stage4_diminishing_returns.webp",None),
("ROI y payback","El ROI expresa la ganancia o pérdida porcentual respecto del costo total en un período definido. El payback estima cuánto tarda en recuperarse la inversión inicial mediante el flujo neto anual.","El encapsulamiento debe cumplir primero su función acústica; luego el ciclo económico permite estudiar rentabilidad, recuperación, mantención y beneficio.","stage4_roi_payback.webp",None),
],
6:[
("Energía transmitida y reducción sonora","El coeficiente τ expresa la fracción de energía incidente que atraviesa el elemento. La reducción sonora R aumenta cuando la energía transmitida disminuye.","Distinga la onda incidente, la energía reflejada y la pequeña fracción que llega al recinto receptor.","stage6_transmission.webp",None),
("Ley de masa","La masa superficial m′ combina densidad y espesor. En la región ideal, aumentar la masa o la frecuencia eleva el aislamiento; duplicar m′ aporta aproximadamente 6 dB.","Compare la hoja liviana, que vibra y transmite más, con la hoja pesada sometida a una excitación equivalente.","stage6_mass_law.webp",None),
("Frecuencia crítica y coincidencia","Cuando la onda aérea y la onda de flexión del panel se acoplan eficientemente, aumenta la radiación hacia el otro lado y aparece un valle en la curva de aislamiento.","La situación central muestra mayor transmisión que las frecuencias vecinas: esa banda puede dominar el diseño.","stage6_coincidence.webp",None),
("Sistema doble masa–aire–masa","Dos hojas separadas pueden superar a una hoja simple si están desacopladas, la cámara es suficiente y se controlan la resonancia y los puentes rígidos. El absorbente amortigua la cavidad, pero no sustituye el desacoplamiento.","Identifique las dos hojas independientes, la cámara con lana mineral y la ausencia de una unión rígida directa.","stage6_double_wall.webp",None),
("Elementos débiles, fugas y flancos","Una puerta, ventana, rendija o vía lateral puede dominar el aislamiento global aunque ocupe poca superficie. El resultado se obtiene combinando transmisiones, no promediando decibeles.","Observe por dónde escapa realmente la energía: reforzar el paño que ya funciona bien puede no mejorar el conjunto.","stage6_weak_elements.webp",None),
],
8:[
("R(f): aislamiento por frecuencia","El aislamiento no es constante: R(f) describe la reducción sonora en cada banda. Las ondas graves, medias y agudas pueden atravesar una misma separación en proporciones distintas.","Compare las longitudes de onda y relaciónelas con los distintos puntos de la curva: siempre revise la banda que domina la fuente.","stage8_frequency_curve.webp",None),
("Rw: índice ponderado ISO","Rw resume la curva mediante una referencia normalizada que se desplaza hasta cumplir el límite de desviaciones desfavorables. No es un promedio ni equivale necesariamente a R en todas las bandas.","Observe las dos curvas y las separaciones desfavorables; el número único nace de un procedimiento, no de escoger el punto más alto.","stage8_weighted_index.webp",None),
("Laboratorio y terreno","R y Rw caracterizan un elemento bajo condiciones controladas. R′ y R′w describen el comportamiento aparente instalado e incorporan encuentros, montaje y transmisiones laterales.","En el laboratorio domina el elemento ensayado; en la obra aparecen caminos por piso, cielo y uniones.","stage8_lab_field.webp",None),
("C, Ctr y el espectro de la fuente","C y Ctr adaptan Rw a espectros distintos. C se asocia mejor con espectros medios-altos; Ctr penaliza especialmente las bajas frecuencias frecuentes en tránsito.","La misma fachada enfrenta ondas distintas: para buses y camiones revise Rw+Ctr y la curva de bajas frecuencias.","stage8_spectral_terms.webp",None),
],
}


TEACHER_GUIDES = {
1:("Explique primero las siete figuras y recién después abra el laboratorio. Contraste propagación aérea con estructural y recalque que la distancia no es una medida ubicada en la trayectoria.",
[
("¿Qué elemento es la fuente en esta escena?","La máquina o equipo que genera la energía sonora y vibratoria."),
("¿Qué camino seguiría existiendo si se instala una barrera?","La transmisión estructural y cualquier vía aérea indirecta que no quede interceptada por la barrera."),
("¿Por qué una orejera protege al trabajador pero no controla el ruido ambiental?","Porque actúa únicamente en el receptor: reduce su exposición personal, pero la fuente continúa emitiendo y el ruido sigue propagándose al entorno."),
]),
2:("Use los dos recintos para separar tres magnitudes: R del panel, absorción equivalente del receptor y T₆₀. Al agregar absorbentes, R debe permanecer constante.",
[
("¿Qué cambia al reemplazar el panel?","Cambia la transmisión entre recintos y, por tanto, el valor R de la separación. También puede cambiar el nivel recibido."),
("¿Qué cambia al revestir el recinto receptor?","Aumenta la absorción equivalente, disminuyen las reflexiones y baja T₆₀; el R propio del panel no cambia."),
("¿Puede disminuir el nivel receptor sin haber mejorado el R del panel?","Sí. Al reducir el campo reverberante puede bajar el nivel medio del recinto receptor, aunque la propiedad aislante del panel permanezca igual."),
("¿Por qué una sala puede oírse menos ruidosa sin estar mejor aislada?","Porque el acondicionamiento absorbente reduce la energía reflejada dentro de la sala, pero no necesariamente la energía que atraviesa la separación."),
]),
3:("Pida justificaciones breves y detecte si el estudiante clasifica por el objeto o por el mecanismo físico predominante.",
[
("¿Cuál es la vía dominante?","La que aporta la mayor energía al receptor; debe determinarse con inspección, medición por bandas y pruebas de intervención cuando corresponda."),
("¿La solución controla transmisión o reverberación?","Si modifica la separación entre espacios controla transmisión; si modifica reflexiones dentro del recinto controla reverberación."),
("¿Qué dato adicional pedirías antes de diseñar?","Espectro por bandas, geometría, composición constructiva, área de elementos débiles, encuentros, sellos, uso y meta acústica."),
]),
4:("Explique las cuatro figuras en orden: filtro de suficiencia, costo del ciclo, rendimiento decreciente y recuperación. En la primera figura haga que el curso descarte la separación que no protege al receptor. En la segunda identifique costos omitidos. Use la tercera para buscar el punto de mejora marginal y la cuarta solo después de verificar el desempeño acústico.",
[
("¿Cuál alternativa puede entrar a la comparación económica y por qué?","Solo una alternativa que cumpla la meta acústica y controle la vía dominante; la economía compara soluciones técnicamente suficientes."),
("¿Qué costo del ciclo podría cambiar la decisión?","Mantención, reposición, consumo energético, detenciones, accesibilidad, pérdida de producción o una vida útil menor que la prevista."),
("¿En qué punto la mejora adicional deja de justificar el aumento de complejidad?","Cuando el costo marginal de obtener más reducción supera el beneficio marginal y la solución ya satisface la meta con un margen de seguridad razonable."),
("¿Por qué un buen ROI no rescata una solución acústicamente insuficiente?","Porque el beneficio económico supuesto depende de resolver el problema. Si no alcanza la meta, no entrega el servicio para el cual se invierte."),
("¿Qué diferencia existe entre ROI y payback?","El ROI expresa rentabilidad acumulada respecto del costo total; el payback expresa tiempo para recuperar la inversión inicial con el flujo anual neto."),
]),
5:("Conduzca la comparación como una decisión en dos etapas: filtro acústico y optimización económica.",
[
("¿Qué alternativa se elimina primero?","La que no cumple la meta acústica o no controla la vía dominante."),
("¿Qué indicador económico ayuda, pero no decide por sí solo?","ROI, payback o costo del ciclo: todos deben interpretarse junto con suficiencia técnica, riesgo y vida útil."),
]),
6:("Recorra las figuras desde la energía hasta el sistema construido. Relacione τ con R; compare hoja liviana y pesada; identifique la transmisión adicional en coincidencia; explique las dos masas desacopladas; y cierre siguiendo la fuga o el elemento débil. Después use cada pestaña del simulador para comprobar el fenómeno.",
[
("¿Qué ocurre con R cuando disminuye τ?","R aumenta logarítmicamente, porque una fracción menor de la energía incidente logra transmitirse."),
("¿Bajo qué condiciones duplicar masa aporta cerca de 6 dB?","En la región ideal de ley de masa de una hoja simple, lejos de resonancias, coincidencia, fugas y transmisiones laterales."),
("¿Por qué aparece un valle en coincidencia?","Porque el acoplamiento entre la onda aérea y las ondas de flexión del panel vuelve más eficiente su radiación hacia el recinto receptor."),
("¿Qué se pierde si ambas hojas quedan unidas rígidamente?","Se pierde desacoplamiento y aparecen puentes que transmiten vibración, reduciendo la ventaja del sistema doble."),
("¿Por qué una rendija pequeña puede dominar el resultado?","Porque presenta una transmisión mucho mayor que el paño opaco y su contribución energética puede dominar la combinación global."),
]),
7:("Solicite que cada propuesta nombre la banda crítica, la vía dominante y la variable que se modificará antes de volver a verificar la meta.",
[
("¿Qué banda controla el diseño?","La banda que produce el incumplimiento o el mayor nivel receptor, considerando también el espectro real de la fuente."),
("¿Conviene reforzar el muro o el elemento débil?","El elemento o vía que domina la transmisión; reforzar el componente que ya funciona bien suele entregar poca mejora global."),
("¿Cómo comprobarías la mejora?","Repitiendo la evaluación en condiciones comparables y revisando la curva por bandas, no solo un índice único."),
]),
8:("Empiece por R(f), porque el índice único solo tiene sentido después de comprender la curva. Explique visualmente el ajuste de Rw, compare la cámara de ensayo con las vías laterales de obra y termine contrastando voz con tránsito. Vincule después cada fila de la tabla con método, lugar y espectro.",
[
("¿Por qué Rw no representa el mismo aislamiento en todas las bandas?","Porque es un índice único calculado ajustando una curva de referencia; la curva R(f) conserva las diferencias reales por frecuencia."),
("¿Qué incorpora la prima en R′w?","El comportamiento aparente en obra, incluidas transmisiones laterales, encuentros, montaje y otras vías presentes en el edificio."),
("¿Qué combinación revisarías frente a buses y camiones?","Rw+Ctr y la curva en bajas frecuencias; bajo ASTM también puede ser pertinente OITC."),
("¿Cuándo la curva completa es más importante que el índice único?","Ante fuentes tonales, espectros graves o irregulares, valles pronunciados y decisiones donde una banda específica controla el resultado."),
]),
9:("Pida primero leer la curva y luego el número único. Enfatice que dos soluciones con igual Rw pueden responder distinto frente a tránsito.",
[
("¿Dónde están las desviaciones desfavorables?","En las bandas donde la curva medida queda por debajo de la curva de referencia desplazada."),
("¿Qué partición conviene para voz?","La que presenta mejor Rw+C y desempeño en bandas medias, siempre que corresponda al problema evaluado."),
("¿Cuál conviene para bajas frecuencias y por qué?","La que tenga mejor Rw+Ctr y una curva más robusta en graves, aunque ambas compartan el mismo Rw."),
]),
10:("Use los resultados para retroalimentación final. En el caso 30 exija suficiencia acústica, bandas críticas, costo incremental y vida útil.",
[
("¿La recomendación se apoya en el índice correcto?","Debe corresponder al método, al lugar de evaluación y al espectro de la fuente; para ruido grave se debe revisar además la curva completa."),
("¿El mayor Rw es necesariamente la mejor solución?","No. Puede rendir peor frente a la fuente real, costar más sin beneficio útil o no resolver elementos débiles y flancos."),
]),
}

def _visual_path(*args, **kwargs):
    return _ui_components.run_component('_visual_path', globals(), *args, **kwargs)

def _fallback_figure(*args, **kwargs):
    return _ui_components.run_component('_fallback_figure', globals(), *args, **kwargs)

def student_lesson(*args, **kwargs):
    return _ui_components.run_component('student_lesson', globals(), *args, **kwargs)

TEACHER_SLIDE_SUPPORT = {
1:[
("Explique que «ruido» no describe una propiedad física distinta del sonido: incorpora contexto, receptor y efecto. Señale en la figura cómo una misma emisión puede ser útil para uno y molesta para otro.","¿El mismo sonido siempre es ruido?","No. Depende de su nivel y características, pero también del lugar, momento, actividad y receptor.","Evite definir ruido solo como «sonido fuerte». Un sonido moderado, tonal o inoportuno también puede ser ruido."),
("Recorra las tres posibilidades de control: reducir la emisión, interrumpir la propagación o proteger al receptor. Haga que el alumno identifique qué parte cambia en la figura.","¿Dónde conviene actuar primero?","Preferentemente en la fuente, si es técnica y operacionalmente viable, porque evita que la energía se genere o se propague.","Pida siempre identificar la vía dominante antes de ofrecer una solución; una medida bien construida sobre la vía equivocada será poco eficaz."),
("Señale de izquierda a derecha la fuente, la trayectoria y el receptor. Explique que este modelo ordena el diagnóstico, pero no implica que exista una sola vía.","¿Qué debe conocerse antes de seleccionar una medida?","Qué genera el ruido, por qué vías llega y qué receptor o criterio debe protegerse.","Use un caso real y solicite tres sustantivos: fuente, vía dominante y receptor. Luego recién permita proponer controles."),
("Siga las ondas que se propagan por el aire. Explique que la distancia puede reducir el nivel en campo libre, pero reflexiones, geometría y directividad modifican el resultado real.","¿Duplicar la distancia siempre reduce exactamente 6 dB?","No. Ese valor corresponde a una fuente puntual ideal en campo libre; otras geometrías y entornos producen comportamientos distintos.","Diferencie atenuación geométrica de aislamiento: alejarse no mejora el cerramiento ni cambia su R."),
("Siga la vía naranja a través del apoyo y la estructura hasta su nueva radiación. Destaque que una barrera aérea no interrumpe este camino sólido.","¿Por qué una barrera puede no resolver el problema?","Porque puede permanecer la transmisión estructural o una trayectoria aérea indirecta que la barrera no intercepta.","Para demostrarlo, pida imaginar el equipo apagado del aire pero vibrando sobre la losa: el sólido puede transportar energía a otro recinto."),
("Use la figura como balance energético cualitativo: parte de la energía se refleja, parte se absorbe y parte se transmite. No presente estos fenómenos como sinónimos.","¿Agregar absorción a una cara garantiza mayor aislamiento?","No. Puede reducir la reflexión en ese recinto, pero el aislamiento depende del sistema completo y de la energía transmitida.","Pregunte siempre «¿en qué recinto cambia el fenómeno?»; esa frase separa con claridad absorción interior de aislamiento entre espacios."),
("Relacione cada intervención con el elemento que modifica. Recalque que distancia es una condición geométrica independiente y que la protección auditiva no reduce el ruido ambiental.","¿Qué medida protege solo al trabajador?","La protección auditiva: reduce la exposición en el receptor, pero la fuente continúa emitiendo al entorno.","Solicite que toda propuesta indique mecanismo, ubicación y verificación. Evite aceptar listas de productos sin explicar cómo actúan."),
],
2:[
("Señale los dos recintos, el panel separador y la diferencia entre energía incidente y transmitida. Explique que R caracteriza la separación, no el ambiente interior por sí solo.","¿Qué debe cambiar para aumentar el aislamiento entre ambos recintos?","La transmisión del sistema separador: su masa, desacoplamiento, estanqueidad o elementos débiles, según el mecanismo dominante.","Use la pregunta «¿atraviesa el panel o rebota dentro de la sala?» para distinguir transmisión de reverberación."),
("Muestre que el material absorbente actúa sobre la energía reflejada en el mismo recinto. Su incorporación no cambia automáticamente el R propio del panel.","¿Qué magnitud aumenta al instalar material absorbente?","La absorción equivalente del recinto; normalmente disminuyen las reflexiones y el tiempo de reverberación.","Aclare que el nivel medio receptor puede bajar por menor campo reverberante sin que el panel haya mejorado su aislamiento."),
("Explique el instante en que la fuente se detiene y cómo se observa el decaimiento. Relacione T₆₀ con volumen y absorción equivalente mediante Sabine dentro de sus supuestos.","¿Qué ocurre con T₆₀ si aumenta la absorción y el volumen permanece constante?","Disminuye, porque la energía reflejada decae con mayor rapidez.","Advierta que Sabine es una aproximación de campo difuso; salas muy absorbentes o con distribución no uniforme pueden requerir otros modelos."),
("Diferencie señal directa, reflexiones útiles tempranas, reflexiones tardías y ruido de fondo. La inteligibilidad no depende solo de «tener absorción».","¿Qué dos condiciones suelen mejorar la comprensión de la palabra?","Una relación señal/ruido favorable y control de reflexiones tardías o reverberación excesiva.","Conecte la figura con una experiencia: una frase puede oírse fuerte y aun así entenderse mal por superposición temporal."),
],
4:[
("Explique el filtro técnico antes del económico: una alternativa que no cumple la meta o no controla la vía dominante no debe ganar por ser barata.","¿Puede compararse económicamente una solución que no cumple?","Puede registrarse su costo, pero no considerarse una alternativa válida para decidir, porque no entrega el desempeño requerido.","Defina por escrito la meta, la banda crítica y el margen antes de mostrar precios; así evita que el costo sesgue la evaluación técnica."),
("Recorra inversión, instalación, operación, mantención, reposición y retiro. Distinga egresos iniciales de costos recurrentes y lleve todos al mismo horizonte.","¿Por qué la opción más barata al comprar puede ser más costosa?","Porque puede exigir más mantención, reposición, energía, detenciones o tener menor vida útil.","Para una comparación rigurosa use valor presente y una tasa de descuento; no sume flujos de años distintos como si valieran lo mismo."),
("Señale cómo la mejora adicional disminuye mientras el costo y la complejidad continúan creciendo. Relacione la decisión con suficiencia, riesgo y margen razonable.","¿Cuándo deja de justificarse otro decibel?","Cuando el costo y riesgo marginal superan el beneficio marginal, una vez satisfecha la meta con margen adecuado.","No convierta el gráfico en una regla universal: el valor de un decibel adicional depende del incumplimiento, el receptor y las consecuencias."),
("Separe dos preguntas: payback indica cuándo se recupera la inversión; ROI indica la ganancia o pérdida porcentual en un horizonte. En el ejemplo, inversión $2,0 millones y flujo neto anual $0,6 millones producen payback 3,33 años; el ROI se calcula aparte con beneficios acumulados y costos totales del mismo período.","Si dos soluciones tienen el mismo payback, ¿tienen necesariamente el mismo ROI?","No. Pueden tener distinta vida útil, flujos posteriores, mantención y beneficio acumulado; el payback ignora lo que ocurre después de recuperar la inversión.","Dibuje una línea de tiempo de caja. ROI = (beneficios acumulados − costos totales)/costos totales × 100; payback = inversión/flujo neto anual solo si el flujo es aproximadamente constante."),
],
6:[
("Identifique energía incidente, reflejada y transmitida. Vincule τ con R=-10 log₁₀τ y enfatice que la escala es logarítmica.","Si τ disminuye diez veces, ¿cuánto aumenta R?","Aumenta 10 dB, porque R depende del logaritmo decimal de la fracción transmitida.","Use valores simples: τ=0,01 corresponde a R=20 dB; τ=0,001 corresponde a R=30 dB."),
("Compare las dos hojas bajo excitación equivalente. Explique la tendencia ideal de ley de masa y sus límites físicos.","¿Duplicar masa siempre agrega 6 dB?","No. Es una aproximación en la región controlada por masa, lejos de resonancia, coincidencia, fugas y flancos.","Antes de aplicar la ley de masa, pregunte si el elemento se comporta como hoja simple y en qué rango de frecuencia."),
("Señale la banda donde el acoplamiento entre onda aérea y flexión del panel aumenta la radiación. Relaciónela con el valle de R(f).","¿Por qué la coincidencia empeora el aislamiento?","Porque el acoplamiento excita eficientemente ondas de flexión que radián energía al recinto receptor.","No confunda frecuencia crítica con resonancia masa–aire–masa: corresponden a mecanismos diferentes."),
("Identifique masa, cámara y segunda masa. Explique que desacoplamiento, profundidad, absorbente y ausencia de puentes trabajan en conjunto.","¿Qué ocurre si un montante une rígidamente ambas hojas?","Aparece un puente mecánico que aumenta la transmisión y reduce la ventaja del sistema doble.","El absorbente de cámara amortigua resonancias, pero no sustituye la separación mecánica entre las hojas."),
("Siga la rendija o el flanco mostrado, no solo el paño principal. Explique la suma energética de vías y por qué no se promedian decibeles.","¿Por qué una puerta pequeña puede controlar el aislamiento global?","Porque su coeficiente de transmisión puede ser muy superior al del muro y dominar la energía total transmitida.","Antes de engrosar un muro, revise puertas, ventanas, sellos, cajas eléctricas, cielos y encuentros."),
],
8:[
("Recorra la curva banda por banda y relaciónela con el espectro de la fuente. Destaque que una cifra global puede ocultar un valle determinante.","¿Qué banda controla una fuente tonal de 125 Hz?","La respuesta del sistema alrededor de 125 Hz; el índice global por sí solo no demuestra suficiencia.","Pida siempre superponer espectro emisor y R(f): la banda crítica nace de ambos, no solo del cerramiento."),
("Explique el desplazamiento de la curva de referencia y las desviaciones desfavorables. Rw es un descriptor calculado, no un promedio aritmético.","¿Rw=50 significa R=50 dB en todas las bandas?","No. La curva real puede estar sobre o bajo 50 dB según la frecuencia.","Muestre dos curvas con igual Rw pero valles distintos; es la forma más rápida de evitar una lectura literal del índice."),
("Compare la cámara controlada con la obra y siga los caminos laterales. Diferencie R/Rw de R′/R′w.","¿Por qué R′w suele ser menor que Rw de laboratorio?","Porque en obra intervienen flancos, encuentros, sellos, montaje y otras vías que no pertenecen solo al elemento ensayado.","No atribuya toda diferencia a «mala instalación» sin diagnóstico: geometría, flancos y condiciones de medición también influyen."),
("Compare el contenido grave del tránsito con un espectro más medio-agudo. Explique que C y Ctr adaptan la lectura de Rw a fuentes distintas.","¿Qué descriptor revisarías frente a buses y camiones?","Rw+Ctr junto con la curva de bajas frecuencias; según el sistema normativo también puede corresponder OITC.","Las correcciones espectrales no reemplazan la curva completa cuando existe tonalidad o una banda dominante."),
],
}

def full_matter(*args, **kwargs):
    return _ui_components.run_component('full_matter', globals(), *args, **kwargs)

def lesson(*args, **kwargs):
    return _ui_components.run_component('lesson', globals(), *args, **kwargs)

def formula_card(*args, **kwargs):
    return _ui_components.run_component('formula_card', globals(), *args, **kwargs)

def check(*args, **kwargs):
    return _ui_components.run_component('check', globals(), *args, **kwargs)

def development_answer(*args, **kwargs):
    return _ui_components.run_component('development_answer', globals(), *args, **kwargs)























def _set_projection(*args, **kwargs):
    return _projection_views.run_view("_set_projection", globals(), *args, **kwargs)

def projection_view():
    return _projection_views.run_view("projection_view", globals())

def _question_points(*args, **kwargs):
    return _evaluations.run_evaluation('_question_points', globals(), *args, **kwargs)


def _score_from_level(*args, **kwargs):
    return _evaluations.run_evaluation('_score_from_level', globals(), *args, **kwargs)


def _save_formative(*args, **kwargs):
    return _evaluations.run_evaluation('_save_formative', globals(), *args, **kwargs)


def _student_scores(*args, **kwargs):
    return _evaluations.run_evaluation('_student_scores', globals(), *args, **kwargs)


def _scores_for_class(*args, **kwargs):
    return _evaluations.run_evaluation('_scores_for_class', globals(), *args, **kwargs)


def _effective_score(*args, **kwargs):
    return _evaluations.run_evaluation('_effective_score', globals(), *args, **kwargs)


def _grade_from_percent(*args, **kwargs):
    return _evaluations.run_evaluation('_grade_from_percent', globals(), *args, **kwargs)


def _result_summary(*args, **kwargs):
    return _evaluations.run_evaluation('_result_summary', globals(), *args, **kwargs)


def score_counter(*args, **kwargs):
    return _evaluations.run_evaluation('score_counter', globals(), *args, **kwargs)


def _keyword_level(*args, **kwargs):
    return _evaluations.run_evaluation('_keyword_level', globals(), *args, **kwargs)


def formative_development(*args, **kwargs):
    return _evaluations.run_evaluation('formative_development', globals(), *args, **kwargs)


def formative_numeric(*args, **kwargs):
    return _evaluations.run_evaluation('formative_numeric', globals(), *args, **kwargs)


def teacher_group_review(stage,solutions):
    return _teacher_views.run_view('teacher_group_review', globals(), stage, solutions)

def teacher_student_management():
    return _teacher_views.run_view('teacher_student_management', globals(), )

def teacher_publication_management():
    return _teacher_views.run_view('teacher_publication_management', globals(), )

def formula_reference():
    return _formula_views.run_view("formula_reference", globals())

def formula_popup_button():
    return _formula_views.run_view("formula_popup_button", globals())



CAD_BUCKET = "cad-plans"

def _dxf_preview(file_bytes):
    """Render DXF and return its preview plus drawing-units-per-image-pixel."""
    if ezdxf is None or plt is None:
        raise RuntimeError("Falta instalar ezdxf o matplotlib.")
    with tempfile.NamedTemporaryFile(suffix=".dxf") as source:
        source.write(file_bytes)
        source.flush()
        document=ezdxf.readfile(source.name)
    dpi=150
    fig=plt.figure(figsize=(14,9),dpi=dpi)
    axis=fig.add_axes([0.01,0.01,0.98,0.98])
    axis.set_facecolor("#ffffff")
    Frontend(RenderContext(document),MatplotlibBackend(axis)).draw_layout(
        document.modelspace(),finalize=True)
    axis.set_aspect("equal")
    axis.axis("off")
    fig.canvas.draw()
    xmin,xmax=axis.get_xlim()
    _,_,axis_width,_=axis.get_window_extent().bounds
    drawing_units_per_pixel=abs(xmax-xmin)/axis_width
    output=io.BytesIO()
    fig.savefig(output,format="png",dpi=dpi,facecolor="white")
    plt.close(fig)
    return output.getvalue(),drawing_units_per_pixel

def _cad_record(stage):
    client=_supabase()
    if client is None:
        return None
    try:
        rows=(client.table("cad_documents").select("*")
              .eq("class_id",LABORATORIES[2]["id"]).eq("stage",stage)
              .limit(1).execute().data or [])
        return rows[0] if rows else None
    except Exception:
        return None

def _cad_signed_url(path):
    if not path:
        return None
    try:
        result=_supabase().storage.from_(CAD_BUCKET).create_signed_url(path,3600)
        return result.get("signedURL") or result.get("signed_url")
    except Exception:
        return None

def _save_cad_document(stage,uploaded,display_name,unit_label):
    client=_supabase()
    if client is None:
        raise RuntimeError("Supabase no está conectado.")
    raw=uploaded.getvalue()
    suffix=Path(uploaded.name).suffix.lower()
    if suffix!=".dxf":
        raise RuntimeError("El plano medible debe estar en formato DXF.")
    preview,drawing_units_per_pixel=_dxf_preview(raw)
    stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    base=f"{LABORATORIES[2]['id']}/stage-{stage}/{stamp}"
    original_path=f"{base}{suffix}"
    preview_path=f"{base}-preview.png"
    bucket=client.storage.from_(CAD_BUCKET)
    bucket.upload(original_path,raw,{"content-type":uploaded.type or "application/octet-stream"})
    bucket.upload(preview_path,preview,{"content-type":"image/png"})
    previous=_cad_record(stage)
    data={
        "class_id":LABORATORIES[2]["id"],"stage":stage,
        "display_name":display_name.strip() or uploaded.name,
        "original_name":uploaded.name,"original_path":original_path,
        "preview_path":preview_path,"units_per_pixel":float(drawing_units_per_pixel),
        "unit_label":unit_label.strip() or "m","updated_at":_now(),
    }
    client.table("cad_documents").upsert(data,on_conflict="class_id,stage").execute()
    if previous:
        for old in (previous.get("original_path"),previous.get("preview_path")):
            if old and old not in (original_path,preview_path):
                try:
                    bucket.remove([old])
                except Exception:
                    pass

def _cad_measure_html(image_url,units_per_pixel,unit_label):
    safe_url=json.dumps(image_url)
    safe_unit=json.dumps(unit_label)
    return f"""
    <div class="cad-shell">
      <div class="tools"><button onclick="resetView()">⌂ Ajustar</button>
      <button onclick="clearMeasure()">⌫ Borrar medición</button>
      <b id="result">Haz clic en dos puntos</b></div>
      <canvas id="cad"></canvas>
      <div class="hint">Rueda: zoom · arrastrar: desplazar · clic en dos puntos: medir</div>
    </div>
    <style>
    body{{margin:0;font-family:Arial;background:#07172b;color:white}}
    .cad-shell{{padding:10px}}.tools{{display:flex;gap:8px;align-items:center;margin-bottom:8px}}
    button{{background:#0b69d1;color:#fff;border:1px solid #65ddf3;border-radius:8px;padding:8px 12px;font-weight:700}}
    #result{{margin-left:auto;color:#8ee9ff}}canvas{{width:100%;height:680px;background:white;border-radius:10px;cursor:crosshair}}
    .hint{{font-size:12px;color:#ccefff;margin-top:6px}}
    </style>
    <script>
    const canvas=document.getElementById('cad'),ctx=canvas.getContext('2d'),img=new Image();
    const unitPerPixel={float(units_per_pixel)},unit={safe_unit}; let scale=1,ox=0,oy=0,points=[],drag=false,last=null;
    function size(){{canvas.width=canvas.clientWidth*devicePixelRatio;canvas.height=canvas.clientHeight*devicePixelRatio;draw();}}
    function resetView(){{scale=Math.min(canvas.width/img.width,canvas.height/img.height);ox=(canvas.width-img.width*scale)/2;oy=(canvas.height-img.height*scale)/2;points=[];draw();}}
    function clearMeasure(){{points=[];document.getElementById('result').textContent='Haz clic en dos puntos';draw();}}
    function draw(){{ctx.clearRect(0,0,canvas.width,canvas.height);if(img.complete)ctx.drawImage(img,ox,oy,img.width*scale,img.height*scale);
      if(points.length){{ctx.fillStyle='#ef3b2d';ctx.strokeStyle='#ef3b2d';ctx.lineWidth=3*devicePixelRatio;
      points.forEach(p=>{{ctx.beginPath();ctx.arc(p.x*scale+ox,p.y*scale+oy,5*devicePixelRatio,0,Math.PI*2);ctx.fill();}});
      if(points.length===2){{ctx.beginPath();ctx.moveTo(points[0].x*scale+ox,points[0].y*scale+oy);ctx.lineTo(points[1].x*scale+ox,points[1].y*scale+oy);ctx.stroke();}}}}}}
    img.onload=()=>{{size();resetView();}};img.src={safe_url};window.onresize=size;
    canvas.onwheel=e=>{{e.preventDefault();let r=canvas.getBoundingClientRect(),mx=(e.clientX-r.left)*devicePixelRatio,my=(e.clientY-r.top)*devicePixelRatio;
      let wx=(mx-ox)/scale,wy=(my-oy)/scale,f=e.deltaY<0?1.15:.87;scale*=f;ox=mx-wx*scale;oy=my-wy*scale;draw();}};
    canvas.onmousedown=e=>{{drag=true;last=[e.clientX,e.clientY];}};
    canvas.onmousemove=e=>{{if(drag&&e.buttons){{ox+=(e.clientX-last[0])*devicePixelRatio;oy+=(e.clientY-last[1])*devicePixelRatio;last=[e.clientX,e.clientY];draw();}}}};
    canvas.onmouseup=e=>{{if(!drag)return;let moved=Math.hypot(e.clientX-last[0],e.clientY-last[1]);drag=false;if(moved>2)return;
      let r=canvas.getBoundingClientRect(),x=((e.clientX-r.left)*devicePixelRatio-ox)/scale,y=((e.clientY-r.top)*devicePixelRatio-oy)/scale;
      if(points.length===2)points=[];points.push({{x,y}});if(points.length===2){{let px=Math.hypot(points[1].x-points[0].x,points[1].y-points[0].y);
      document.getElementById('result').textContent=(px*unitPerPixel).toFixed(3)+' '+unit;}}draw();}};
    </script>"""

@st.dialog("Visor CAD",width="large")
def cad_viewer_dialog(stage):
    record=_cad_record(stage)
    if st.session_state.get("role")=="Docente":
        with st.expander("Subir o reemplazar plano",expanded=record is None):
            uploaded=st.file_uploader("Plano medible (DXF)",type=["dxf"],
                                      key=f"cad_upload_{stage}")
            display_name=st.text_input("Nombre visible",value=(record or {}).get("display_name",""),
                                       key=f"cad_name_{stage}")
            unit=st.selectbox("Unidad utilizada al dibujar el DXF",["m","cm","mm"],index=["m","cm","mm"].index((record or {}).get("unit_label","m"))
                              if (record or {}).get("unit_label","m") in ["m","cm","mm"] else 0,
                              key=f"cad_unit_{stage}")
            st.caption("La escala se obtiene automáticamente de las coordenadas del DXF. Verifica la unidad antes de publicarlo.")
            if st.button("Publicar plano",type="primary",key=f"cad_publish_{stage}"):
                if uploaded is None:
                    st.warning("Selecciona un archivo.")
                else:
                    try:
                        _save_cad_document(stage,uploaded,display_name,unit)
                        st.success("Plano publicado para este caso.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"No fue posible publicar el plano: {exc}")
    record=_cad_record(stage)
    if not record:
        st.info("El docente todavía no ha publicado un plano para este caso.")
        return
    st.markdown(f"### {record.get('display_name') or record.get('original_name')}")
    preview_url=_cad_signed_url(record.get("preview_path"))
    original_url=_cad_signed_url(record.get("original_path"))
    if preview_url:
        components.html(_cad_measure_html(
            preview_url,float(record.get("units_per_pixel") or 0.01),
            record.get("unit_label") or "m"),height=760,scrolling=False)
    else:
        st.error("No fue posible abrir la vista previa.")
    if original_url:
        st.link_button("Descargar archivo original",original_url,use_container_width=True)

def cad_viewer_button(stage):
    if not ENABLE_CAD_VIEWER:
        return
    if st.button("📏 Abrir visor CAD y medir",key=f"open_cad_{stage}",
                 use_container_width=True,type="secondary"):
        cad_viewer_dialog(stage)

def line_chart(*args, **kwargs):
    return _ui_components.run_component('line_chart', globals(), *args, **kwargs)





def economic_inputs(prefix="eco"):
    names=["Solución A","Solución B","Solución C"]
    data=[]
    defaults=[(32,1200000,180000,8,900000),(40,1900000,220000,12,1150000),(47,3200000,260000,15,1250000)]
    for i,n in enumerate(names):
        with st.expander(n,expanded=i<2):
            d=defaults[i]
            r=st.number_input("Aislamiento esperado (dB)",20,70,d[0],key=f"{prefix}r{i}")
            inv=st.number_input("Inversión inicial ($)",0,20000000,d[1],step=100000,key=f"{prefix}i{i}")
            maint=st.number_input("Mantenimiento anual ($)",0,3000000,d[2],step=50000,key=f"{prefix}m{i}")
            life=st.number_input("Vida útil (años)",1,30,d[3],key=f"{prefix}l{i}")
            ben=st.number_input("Beneficio anual estimado ($)",0,10000000,d[4],step=50000,key=f"{prefix}b{i}")
        total=inv+maint*life; benefit=ben*life; roi=(benefit-total)/total*100 if total else 0
        payback=inv/(ben-maint) if ben>maint else math.inf
        data.append([n,r,inv,total,benefit,roi,payback])
    return pd.DataFrame(data,columns=["Solución","Aislamiento","Inversión","Costo ciclo","Beneficio acumulado","ROI","Payback"])



def mass_r(m, f):
    return _acoustics.mass_r(m, f)


def compound_r(areas, ratings):
    return _acoustics.compound_r(areas, ratings)


def geometry_term(volume, separating_area):
    return _acoustics.geometry_term(volume, separating_area)


def quirt_window_curve(m1, m2, gap, height, width, alpha, freqs=FREQS):
    return _acoustics.quirt_window_curve(m1, m2, gap, height, width, alpha, freqs)




REF=np.array([33,36,39,42,45,48,51,52,53,54,55,56,56,56,56,56])
def rw_from_curve(curve):
    return _acoustics.rw_from_curve(curve, REF)




QUESTIONS=[
("La trayectoria incluye principalmente:",["La partición y sus fugas","Solo el oído","Solo la fuente"],0),
("La absorción reduce principalmente:",["La reverberación interior","La masa del muro","El ruido emitido"],0),
("A = Σ(S·α) representa:",["Absorción equivalente","Masa superficial","Costo del ciclo"],0),
("Sabine relaciona:",["V, A y T₆₀","R, STC y OITC","Costo, ROI y vida útil"],0),
("Si A aumenta con V constante, T₆₀:",["Disminuye","Aumenta","No cambia"],0),
("Antes de comparar ROI se debe:",["Verificar suficiencia acústica","Elegir lo más barato","Promediar dB"],0),
("ROI compara:",["Beneficio neto con costo total","R con frecuencia","Área con volumen"],0),
("Payback expresa:",["Tiempo de recuperación","Vida útil acústica","Frecuencia crítica"],0),
("El punto de equilibrio es:",["Donde el beneficio adicional deja de justificar el costo","El mayor R posible","El menor precio siempre"],0),
("Una solución que no cumple la meta:",["Se descarta o rediseña","Gana si tiene buen ROI","Se aprueba por vida útil"],0),
("τ es:",["Energía transmitida/incidente","R promedio","Absorción total"],0),
("R se expresa en:",["dB","sabin","segundos"],0),
("Duplicar masa en ley de masa aporta cerca de:",["6 dB","1 dB","20 dB"],0),
("La coincidencia puede producir:",["Una caída de R","Aislamiento infinito","Mayor absorción Sabine"],0),
("La lana en una cámara ayuda a:",["Amortiguar resonancias","Crear puentes rígidos","Eliminar sellos"],0),
("Una rendija puede:",["Dominar la transmisión","Mejorar R","Aumentar masa"],0),
("Los R de elementos compuestos se combinan mediante:",["τ ponderado por área","Promedio aritmético","Suma directa"],0),
("Transmisión flanqueante significa:",["Vía indirecta alrededor del separador","Reflexión interior","Medición a 2 m"],0),
("R(f) es:",["Resultado por banda","Un único índice","Costo por dB"],0),
("Rw corresponde principalmente a:",["Laboratorio ISO","Terreno ASTM","Absorción"],0),
("R′w incorpora:",["Comportamiento aparente en obra","Solo el material aislado","ROI"],0),
("DₙT,w corrige mediante:",["Tiempo de reverberación","Costo de montaje","Masa"],0),
("D₂m,nT,w se usa en:",["Fachadas","Cielos plenums","ROI"],0),
("OITC es especialmente útil para:",["Ruido exterior de transporte","Eco interior","Impactos exclusivamente"],0),
("Cₜᵣ se asocia a:",["Tránsito y contenido grave","Solo agudos","Reverberación"],0),
("STC y Rw:",["No tienen conversión fija universal","Siempre difieren en 2","Son idénticos"],0),
("CAC evalúa:",["Paso por cielos y plenums","Fachada a 2 m","Tiempo de recuperación"],0),
("Para una fuente tonal debe priorizarse:",["Curva por bandas","Solo el índice mayor","Solo el costo"],0),
("Rw es:",["Valor de referencia ajustada en 500 Hz","Promedio de R","R medido siempre en 500 Hz"],0),
]













LAB1_QUESTIONS = [('La trayectoria incluye principalmente:', ['La partición y sus fugas', 'Solo el oído', 'Solo la fuente'], 0), ('La absorción reduce principalmente:', ['La reverberación interior', 'La masa del muro', 'El ruido emitido'], 0), ('A = Σ(S·α) representa:', ['Absorción equivalente', 'Masa superficial', 'Costo del ciclo'], 0), ('Sabine relaciona:', ['V, A y T₆₀', 'R, STC y OITC', 'Costo, ROI y vida útil'], 0), ('Si A aumenta con V constante, T₆₀:', ['Disminuye', 'Aumenta', 'No cambia'], 0), ('Antes de comparar ROI se debe:', ['Verificar suficiencia acústica', 'Elegir lo más barato', 'Promediar dB'], 0), ('ROI compara:', ['Beneficio neto con costo total', 'R con frecuencia', 'Área con volumen'], 0), ('Payback expresa:', ['Tiempo de recuperación', 'Vida útil acústica', 'Frecuencia crítica'], 0), ('El punto de equilibrio es:', ['Donde el beneficio adicional deja de justificar el costo', 'El mayor R posible', 'El menor precio siempre'], 0), ('Una solución que no cumple la meta:', ['Se descarta o rediseña', 'Gana si tiene buen ROI', 'Se aprueba por vida útil'], 0), ('τ es:', ['Energía transmitida/incidente', 'R promedio', 'Absorción total'], 0), ('R se expresa en:', ['dB', 'sabin', 'segundos'], 0), ('Duplicar masa en ley de masa aporta cerca de:', ['6 dB', '1 dB', '20 dB'], 0), ('La coincidencia puede producir:', ['Una caída de R', 'Aislamiento infinito', 'Mayor absorción Sabine'], 0), ('La lana en una cámara ayuda a:', ['Amortiguar resonancias', 'Crear puentes rígidos', 'Eliminar sellos'], 0), ('Una rendija puede:', ['Dominar la transmisión', 'Mejorar R', 'Aumentar masa'], 0), ('Los R de elementos compuestos se combinan mediante:', ['τ ponderado por área', 'Promedio aritmético', 'Suma directa'], 0), ('Transmisión flanqueante significa:', ['Vía indirecta alrededor del separador', 'Reflexión interior', 'Medición a 2 m'], 0), ('R(f) es:', ['Resultado por banda', 'Un único índice', 'Costo por dB'], 0), ('Rw corresponde principalmente a:', ['Laboratorio ISO', 'Terreno ASTM', 'Absorción'], 0), ('R′w incorpora:', ['Comportamiento aparente en obra', 'Solo el material aislado', 'ROI'], 0), ('DₙT,w corrige mediante:', ['Tiempo de reverberación', 'Costo de montaje', 'Masa'], 0), ('D₂m,nT,w se usa en:', ['Fachadas', 'Cielos plenums', 'ROI'], 0), ('OITC es especialmente útil para:', ['Ruido exterior de transporte', 'Eco interior', 'Impactos exclusivamente'], 0), ('Cₜᵣ se asocia a:', ['Tránsito y contenido grave', 'Solo agudos', 'Reverberación'], 0), ('STC y Rw:', ['No tienen conversión fija universal', 'Siempre difieren en 2', 'Son idénticos'], 0), ('CAC evalúa:', ['Paso por cielos y plenums', 'Fachada a 2 m', 'Tiempo de recuperación'], 0), ('Para una fuente tonal debe priorizarse:', ['Curva por bandas', 'Solo el índice mayor', 'Solo el costo'], 0), ('Rw es:', ['Valor de referencia ajustada en 500 Hz', 'Promedio de R', 'R medido siempre en 500 Hz'], 0)]





# ---------------------------------------------------------------------------
# Laboratorio 1 · implementación modularizada
# ---------------------------------------------------------------------------
from labs import laboratorio_1 as _laboratorio_1

def _run_lab1_stage(stage_index):
    return _laboratorio_1.run_stage(stage_index, globals())

def _run_lab1_helper(name, *args, **kwargs):
    return _laboratorio_1.run_helper(name, globals(), *args, **kwargs)

def _lab1_final_submission():
    return _run_lab1_helper("_lab1_final_submission")

def _lab1_case_score(calc, diff, pct, bands, choice, justification):
    return _run_lab1_helper("_lab1_case_score", calc, diff, pct, bands, choice, justification)

def _finish_lab1_final(reason="submitted"):
    return _run_lab1_helper("_finish_lab1_final", reason)

def lab1_stage0():
    return _run_lab1_stage(0)

def lab1_stage1():
    return _run_lab1_stage(1)

def lab1_stage2():
    return _run_lab1_stage(2)

def lab1_stage3():
    return _run_lab1_stage(3)

def lab1_stage4():
    return _run_lab1_stage(4)

def lab1_stage5():
    return _run_lab1_stage(5)

def lab1_stage6():
    return _run_lab1_stage(6)

def lab1_stage7():
    return _run_lab1_stage(7)

def lab1_stage8():
    return _run_lab1_stage(8)

def lab1_stage9():
    return _run_lab1_stage(9)

def lab1_stage10():
    return _run_lab1_stage(10)



# ---------------------------------------------------------------------------
# Laboratorio 2 · ruta profesional MINVU / CES / ISO 12354
# Esta ruta es independiente del Laboratorio 1. No reutiliza sus etapas.
# ---------------------------------------------------------------------------
# Version histórica conservada: no participa en LAB_STAGE_FUNCTIONS.
LEGACY_V1_LAB2_MINUTES = [15, 20, 25, 35, 35, 25, 35, 20, 20, 10, 60]

def _glass_panel_tl(thickness_mm, loss_factor, frequencies=FREQS):
    """TL por bandas de un vidrio monolítico mediante integración angular."""
    density = 2500.0
    young = 70.0e9
    poisson = 0.23
    thickness = float(thickness_mm) / 1000.0
    surface_mass = density * thickness
    stiffness = young * thickness**3 / (12 * (1 - poisson**2))
    critical = (
        343.0**2 / (2 * math.pi)
        * math.sqrt(surface_mass / stiffness)
    )
    _, tl, _, _, _ = _panel_simple_field_tl(
        np.asarray(frequencies, dtype=float),
        surface_mass,
        stiffness,
        float(loss_factor),
    )
    return np.asarray(tl), surface_mass, stiffness, critical


def _double_window_model(
    g1_mm, g2_mm, gap_m, height, width, alpha, eta1, eta2,
    frequencies=FREQS,
):
    """Cálculo de cada vidrio y acoplamiento de la ventana doble con Quirt."""
    tl1, m1, b1, fc1 = _glass_panel_tl(g1_mm, eta1, frequencies)
    tl2, m2, b2, fc2 = _glass_panel_tl(g2_mm, eta2, frequencies)
    rho0 = 1.21
    sound_speed = 343.0
    f1 = (1 / (2 * math.pi)) * math.sqrt(
        ((m1 + m2) * rho0 * sound_speed**2) / (gap_m * m1 * m2)
    )
    equivalent = mass_r(m1 + m2, np.asarray(frequencies, dtype=float))
    geometry = (
        10 * math.log10(max(alpha, 1e-9))
        + 10 * math.log10(max(gap_m, 1e-9))
        + 10 * math.log10((height + width) / (height * width))
        + 3
    )
    upper = tl1 + tl2 + geometry
    total = np.where(np.asarray(frequencies, dtype=float) < f1, equivalent, upper)
    return total, tl1, tl2, equivalent, f1, (m1, m2), (fc1, fc2), geometry


# ---------------------------------------------------------------------------
# Laboratorio 2 · Clase de 4 horas con pausa de 30 minutos
# Modelos de predicción del aislamiento a ruido aéreo
# ---------------------------------------------------------------------------
# Laboratorio 2: jornada de 4 horas.
# 210 minutos de trabajo + 30 minutos de pausa después de la Etapa 5.
# Los dos bloques tienen 105 minutos efectivos de trabajo cada uno.
LAB2_FREQS = np.array([63, 80, 100, 125, 160, 200, 250, 315, 400, 500,
                       630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000])

LAB2_ASSET_DIR = ROOT / "assets" / "lab2"
LAB2_IMAGES = {
    # Cambia cualquiera de estos archivos manteniendo el mismo nombre.
    "panel_simple": "panel_simple_transmision_profesional.png",
    "panel_doble": "etapa4_sistema_doble_profesional.webp",
    "metalcon": "metalcon_simple_vs_doble.svg",
    "yeso_carton": "panel_simple_yeso_carton.png",
    "madera": "panel_simple_madera.png",
    "vidrio": "material_vidrio_monolitico.svg",
    "hormigon": "muro_simple_hormigon.png",
    "comparador_hormigon": "comparador_panel_hormigon.svg",
    "comparador_tabique": "comparador_tabique_doble.svg",
    "s2_punto1": "punto1_placa_masa_superficial_profesional.webp",
    "s2_punto2": "punto2_tipos_incidencia_profesional.webp",
    "s2_punto3": "punto3_rigidez_flexion_profesional.webp",
    "s2_punto4": "punto4_promedio_campo_profesional.webp",
    "s2_tau_angulo": "punto3_tau_angulo_profesional.png",
    "s2_ley_masa": "punto6_impedancia_ley_masa_profesional.png",
    "s2_frecuencia_critica": "punto7_frecuencia_critica_profesional.png",
    "s4_propiedades_placas": "etapa4_propiedades_placas_profesional.webp",
    "s4_resonancia": "etapa4_resonancia_profesional.webp",
    "s4_regiones": "etapa4_tres_regiones_profesional.webp",
    "s5_tabique_real": "etapa5_tabique_real_profesional.webp",
    "s5_ideal_vs_conectado": "etapa5_ideal_vs_conectado_profesional.webp",
    "s5_conexion_lineal_metal": "etapa5_conexion_lineal_metal_profesional.png",
    "s5_conexion_lineal_madera": "etapa5_conexion_lineal_madera_profesional.png",
    "s5_conexion_puntual": "etapa5_conexion_puntual_profesional.png",
    "s5_geometria_camara_montantes": "etapa5_geometria_camara_montantes_profesional.png",
}
LAB2_IMAGES.update({
    "stage7_espectro_a_bandas": "stage7_espectro_a_bandas.png",
    "stage7_octava_vs_tercio": "stage7_octava_vs_tercio.png",
    "stage8_airborne_rw": "stage8_airborne_rw.png",
})

def _lab2_image(image_key, caption=None):
    """Load every replaceable Lab 2 illustration from assets/lab2."""
    filename = LAB2_IMAGES.get(image_key)
    path = LAB2_ASSET_DIR / filename if filename else None
    if path and path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
        return True
    expected = f"assets/lab2/{filename or image_key}"
    st.warning(f"No se encontró la imagen: {expected}")
    st.caption("Súbela a GitHub con ese nombre exacto; no es necesario modificar el código.")
    return False

def _lab2_plain_language_cards(simple, observe, mistake):
    """Three visible conceptual bridges for students without an engineering background."""
    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
        gap:.8rem;margin:.85rem 0 1.15rem">
          <div style="background:#eef8ff;border:1px solid #b9def5;border-radius:14px;padding:1rem">
            <div style="font-size:.76rem;font-weight:800;color:#0877c5">💡 EN PALABRAS SIMPLES</div>
            <div style="margin-top:.45rem;color:#17324d;line-height:1.5">{simple}</div>
          </div>
          <div style="background:#f1fbf7;border:1px solid #bfe8d5;border-radius:14px;padding:1rem">
            <div style="font-size:.76rem;font-weight:800;color:#13845f">👀 QUÉ DEBES OBSERVAR</div>
            <div style="margin-top:.45rem;color:#17324d;line-height:1.5">{observe}</div>
          </div>
          <div style="background:#fff8ec;border:1px solid #f1d39b;border-radius:14px;padding:1rem">
            <div style="font-size:.76rem;font-weight:800;color:#a56108">⚠️ ERROR FRECUENTE</div>
            <div style="margin-top:.45rem;color:#17324d;line-height:1.5">{mistake}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _lab2_incidence_figure(theta, tau=1.0):
    """Return incidence geometry; transmitted-ray weight follows calculated tau."""
    rad = math.radians(theta)
    origin = np.array([0.0, 0.0])
    incident = np.array([-math.cos(rad), -math.sin(rad)])
    reflected = np.array([-math.cos(rad), math.sin(rad)])
    fig = go.Figure()
    fig.add_shape(type="rect", x0=-.03, x1=.03, y0=-1.0, y1=1.0,
                  fillcolor="#8095aa", line_color="#173f63")
    fig.add_shape(type="line", x0=-1.15, x1=1.15, y0=0, y1=0,
                  line=dict(color="#60718a", width=2, dash="dash"))
    for name, start, end, color, width in [
        ("Onda incidente", incident, origin, "#0967d2", 6),
        ("Onda reflejada", origin, reflected, "#ef8b2c", 4),
        ("Onda transmitida", origin, np.array([1.05, 0]), "#17a779",
         max(1.5, 7*math.sqrt(max(tau, 0)))),
    ]:
        fig.add_trace(go.Scatter(
            x=[start[0], end[0]], y=[start[1], end[1]],
            mode="lines+markers", name=name,
            line=dict(color=color, width=width), marker=dict(size=[5, 10])))
    fig.add_annotation(x=-.34, y=-.12, text=f"θ = {theta:.0f}°", showarrow=False)
    fig.update_layout(
        height=390, margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(range=[-1.25, 1.25], visible=False, scaleanchor="y"),
        yaxis=dict(range=[-1.05, 1.05], visible=False),
        legend=dict(orientation="h", y=1.08), hovermode=False,
        title="Incidencia, reflexión y transmisión")
    return fig

def _lab2_incidence_plot(theta, tau=1.0):
    """Backward-compatible incidence renderer."""
    st.plotly_chart(
        _lab2_incidence_figure(theta, tau),
        use_container_width=True,
        key=f"lab2_incidence_{theta}",
    )

def _mass_sheet_tau(mass, frequency, theta, rho_air=1.21, sound_speed=343.0):
    return _acoustics.mass_sheet_tau(mass, frequency, theta, rho_air, sound_speed)


def _critical_frequency(rho, h_mm, young_gpa, poisson, sound_speed=343.0):
    return _acoustics.critical_frequency(rho, h_mm, young_gpa, poisson, sound_speed)


def _mass_law_curve(mass):
    return _acoustics.mass_law_curve(mass, LAB2_FREQS)


def _simple_real_curve(mass, fc, loss=9):
    return _acoustics.simple_real_curve(mass, fc, LAB2_FREQS, loss)


def _sharp_parameters(m1, m2, depth):
    return _acoustics.sharp_parameters(m1, m2, depth)


def _sharp_curve(m1, m2, depth, connection="Independiente"):
    return _acoustics.sharp_curve(m1, m2, depth, LAB2_FREQS, connection)


def _plot_curves(series, title, markers=None, highlight=None):
    fig = go.Figure()
    if highlight:
        x0, x1, label, color = highlight
        x0 = max(float(LAB2_FREQS[0]), float(x0))
        x1 = min(float(LAB2_FREQS[-1]), float(x1))
        if x1 > x0:
            fig.add_vrect(
                x0=x0,
                x1=x1,
                fillcolor=color,
                opacity=.22,
                line_width=0,
                layer="below",
                annotation_text=label,
                annotation_position="top left",
                annotation_font=dict(color="#17324d", size=12),
            )
    for name, values, style in series:
        fig.add_trace(go.Scatter(
            x=LAB2_FREQS, y=values, mode="lines+markers", name=name,
            line=dict(width=3, dash=style), marker=dict(size=6)))
    if markers:
        for x, label in markers:
            fig.add_vline(x=x, line_dash="dot", line_color="#ef8b2c")
            fig.add_annotation(x=x, y=1, yref="paper", text=label, showarrow=False,
                               yanchor="bottom", font=dict(color="#9b5415"))
    fig.update_layout(
        title=title, xaxis_title="Frecuencia central (Hz)", yaxis_title="TL / R (dB)",
        xaxis_type="log", hovermode="x unified", height=430,
        margin=dict(l=35,r=20,t=65,b=40), legend=dict(orientation="h",y=1.12))
    fig.update_xaxes(tickvals=[63,125,250,500,1000,2000,4000],
                     ticktext=["63","125","250","500","1k","2k","4k"],
                     range=[math.log10(50),math.log10(5000)],
                     autorange=False)
    st.plotly_chart(fig, use_container_width=True)

from labs import laboratorio_2 as _laboratorio_2

# Puente estable: conserva los nombres públicos usados por navegación y resultados.
def _run_lab2_stage(stage_index):
    return _laboratorio_2.run_stage(stage_index, globals())

def _lab2_heading(stage, title, purpose):
    # Compatibilidad para llamadas externas; las etapas usan su copia interna.
    _laboratorio_2._bind_runtime(globals())
    return _laboratorio_2._lab2_heading(stage, title, purpose)

def lab2_stage0():
    return _run_lab2_stage(0)

def lab2_stage1():
    return _run_lab2_stage(1)

def lab2_stage2():
    return _run_lab2_stage(2)

def lab2_stage3():
    return _run_lab2_stage(3)

def lab2_stage4():
    return _run_lab2_stage(4)

def lab2_stage5():
    return _run_lab2_stage(5)

def lab2_stage6():
    return _run_lab2_stage(6)

def lab2_stage7():
    return _run_lab2_stage(7)

def lab2_stage8():
    return _run_lab2_stage(8)

def lab2_stage9():
    return _run_lab2_stage(9)

def lab2_stage10():
    return _run_lab2_stage(10)





def _panel_simple_tau(frequency, angles_rad, surface_mass, stiffness, loss_factor, rho_air=1.18, sound_speed=343.0):
    return _acoustics.panel_simple_tau(frequency, angles_rad, surface_mass, stiffness, loss_factor, rho_air, sound_speed)



def _panel_simple_field_tl(frequencies, surface_mass, stiffness, loss_factor):
    return _acoustics.panel_simple_field_tl(frequencies, surface_mass, stiffness, loss_factor)





def _lab2_pending(stage, title):
    _lab2_heading(stage,title,"Contenido reservado para la segunda mitad de la Clase 1.")
    st.info("Esta etapa se desarrollará después de validar en aula las primeras dos horas.")



STAGE9_QUESTIONS = [
    {
        "title":"Aislamiento y absorción",
        "question":"Una sala presenta mucha reverberación y, además, el ruido se escucha en el recinto contiguo. ¿Qué solución aborda correctamente ambos problemas?",
        "options":[
            "Instalar únicamente espuma absorbente sobre el muro divisorio.",
            "Aumentar únicamente el volumen del sistema de amplificación.",
            "Incorporar absorción dentro de la sala y mejorar constructivamente el elemento separador.",
            "Pintar el muro divisorio con una pintura de mayor espesor.",
        ],
        "correct":2,
        "explanation":"La absorción reduce reflexiones y reverberación dentro del recinto. El aislamiento exige intervenir la solución separadora, su masa, hermeticidad, uniones y configuración.",
    },
    {
        "title":"Influencia de elementos débiles",
        "question":"Un muro presenta un aislamiento elevado, pero contiene una puerta liviana con separaciones visibles en sus bordes. ¿Qué comportamiento es más probable?",
        "options":[
            "El aislamiento total será prácticamente igual al del muro.",
            "La puerta y sus filtraciones reducirán significativamente el aislamiento del conjunto.",
            "La puerta solo afectará la absorción interior del recinto.",
            "Las aberturas mejorarán el aislamiento en frecuencias bajas.",
        ],
        "correct":1,
        "explanation":"El desempeño global puede quedar controlado por el elemento que transmite más energía. Una puerta liviana y sus rendijas pueden degradar fuertemente el aislamiento del conjunto.",
    },
    {
        "title":"Ley de masa",
        "question":"Si se duplica la masa superficial de un elemento simple y se mantienen las demás condiciones, ¿qué cambio predice aproximadamente la ley de masa en la zona controlada por masa?",
        "options":["Aumenta 3 dB.","Aumenta 6 dB.","Aumenta 12 dB.","No cambia."],
        "correct":1,
        "explanation":"En la región ideal controlada por masa, duplicar la masa superficial aumenta aproximadamente 6 dB la pérdida por transmisión.",
    },
    {
        "title":"Suma energética de niveles",
        "question":"Dos máquinas independientes e idénticas producen 80 dB cada una en el mismo punto receptor. ¿Cuál es el nivel total aproximado cuando funcionan simultáneamente?",
        "options":["80 dB.","83 dB.","86 dB.","160 dB."],
        "correct":1,
        "explanation":"Dos fuentes independientes de igual nivel agregan aproximadamente 3 dB: 10·log₁₀(10⁸ + 10⁸) ≈ 83 dB. Los decibeles no se suman aritméticamente.",
    },
    {
        "title":"Aislamiento global de muro y puerta",
        "question":"Un tabique ocupa el 90 % de una separación y tiene R = 55 dB. Una puerta ocupa el 10 % y tiene R = 25 dB. ¿Cuál afirmación describe mejor el resultado?",
        "options":[
            "El aislamiento total será cercano a 52 dB por promedio ponderado de R.",
            "El aislamiento total será exactamente 40 dB por promedio aritmético.",
            "La puerta puede dominar la transmisión y reducir considerablemente el aislamiento total.",
            "La puerta no tendrá efecto porque ocupa menos del 50 % de la superficie.",
        ],
        "correct":2,
        "explanation":"Deben combinarse coeficientes de transmisión ponderados por área, no valores de R directamente. Aunque sea pequeña, la puerta transmite mucha más energía y puede controlar el resultado.",
    },
    {
        "title":"Fenómeno de coincidencia",
        "question":"Una pared simple aumenta progresivamente su aislamiento con la frecuencia, presenta una caída pronunciada alrededor de 2.000 Hz y luego vuelve a aumentar. ¿Cuál es la explicación más probable?",
        "options":[
            "La resonancia masa–aire–masa.",
            "El fenómeno de coincidencia o frecuencia crítica.",
            "Un aumento repentino de la absorción del recinto receptor.",
            "La suma energética de dos fuentes iguales.",
        ],
        "correct":1,
        "explanation":"Cerca de la frecuencia crítica, la coincidencia entre la onda incidente y las ondas de flexión del panel aumenta la transmisión y produce una caída de aislamiento.",
    },
    {
        "title":"Sistema masa–aire–masa",
        "question":"Dos tabiques dobles tienen las mismas placas y cámara. En A, las hojas comparten montantes rígidos; en B, están desacopladas y la cámara contiene absorbente poroso. ¿Cuál comportamiento es más probable?",
        "options":[
            "A aislará más porque los montantes transmiten mejor las cargas.",
            "Ambos tendrán necesariamente el mismo aislamiento por tener igual masa.",
            "B aislará más porque reduce puentes mecánicos y amortigua resonancias de la cámara.",
            "El absorbente de B reemplaza completamente la función de las placas.",
        ],
        "correct":2,
        "explanation":"El desacoplamiento reduce la transmisión estructural entre hojas y el absorbente amortigua resonancias en la cámara; no sustituye la masa ni la hermeticidad.",
    },
    {
        "title":"Ajuste de la curva de referencia",
        "question":"La suma de desviaciones desfavorables es 29 dB. Al subir la referencia 1 dB, aumenta a 35 dB. ¿Qué posición corresponde para determinar Rw?",
        "options":[
            "La posición con 29 dB, por ser la más alta que aún cumple el límite de 32 dB.",
            "La posición con 35 dB, porque está más cerca del límite.",
            "Una posición intermedia desplazada 0,5 dB.",
            "La posición más baja posible, aunque la suma sea 0 dB.",
        ],
        "correct":0,
        "explanation":"La referencia se mueve en pasos enteros de 1 dB y se conserva la posición más alta cuya suma de desviaciones desfavorables no supera 32 dB.",
    },
    {
        "title":"Desviaciones desfavorables",
        "question":"En cuatro bandas, Rmedido − Rreferencia vale −4, +3, −2 y +5 dB. ¿Cuánto aportan estas bandas a la suma de desviaciones desfavorables?",
        "options":["0 dB.","2 dB.","6 dB.","14 dB."],
        "correct":2,
        "explanation":"Solo se contabilizan los déficits: 4 + 2 = 6 dB. Los excedentes favorables no compensan las deficiencias de otras bandas.",
    },
    {
        "title":"Interpretación comparativa de Ctr",
        "question":"A: Rw(C;Ctr) = 54(−1;−8) dB. B: Rw(C;Ctr) = 52(−1;−3) dB. Para una fachada expuesta principalmente a tránsito urbano, ¿cuál presenta el mayor valor adaptado?",
        "options":[
            "A, porque tiene el mayor Rw.",
            "B, porque 52 − 3 = 49 dB, mientras en A 54 − 8 = 46 dB.",
            "Ambas, porque sus valores de C son iguales.",
            "No pueden compararse porque Ctr no se relaciona con ruido de tránsito.",
        ],
        "correct":1,
        "explanation":"Para tránsito se compara Rw + Ctr. B alcanza 49 dB y A 46 dB; un Rw mayor no garantiza mejor respuesta frente a un espectro con contenido grave.",
    },
]

def _stage9_submission(*args, **kwargs):
    return _evaluations.run_evaluation('_stage9_submission', globals(), *args, **kwargs)


def _stage9_answer_payload(*args, **kwargs):
    return _evaluations.run_evaluation('_stage9_answer_payload', globals(), *args, **kwargs)


def teacher_stage9_results(compact=False):
    return _teacher_views.run_view('teacher_stage9_results', globals(), compact)

def teacher_stage9_answer_key():
    return _teacher_views.run_view('teacher_stage9_answer_key', globals(), )

def _teacher_lab1_final_results(compact=False):
    return _teacher_views.run_view('_teacher_lab1_final_results', globals(), compact)

def teacher_course_results(compact=False):
    return _teacher_views.run_view('teacher_course_results', globals(), compact)

def _teacher_lab2_integrated_results(compact=False):
    return _teacher_views.run_view('_teacher_lab2_integrated_results', globals(), compact)

def _finish_stage9(*args, **kwargs):
    return _evaluations.run_evaluation('_finish_stage9', globals(), *args, **kwargs)


@st.fragment(run_every=1)
def _stage9_clock(deadline_iso):
    deadline=dt.datetime.fromisoformat(str(deadline_iso).replace("Z","+00:00"))
    remaining=max(0,int((deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()))
    minutes,seconds=divmod(remaining,60)
    color="#0f9d78" if remaining>300 else "#d97706" if remaining>60 else "#c62828"
    st.markdown(
        f'<div style="border:2px solid {color};border-radius:16px;padding:.8rem 1rem;'
        f'background:#fff;text-align:center"><b style="color:{color};font-size:1.35rem">'
        f'⏱️ {minutes:02d}:{seconds:02d}</b><br><span>Tiempo restante</span></div>',
        unsafe_allow_html=True,
    )
    if remaining<=0 and not st.session_state.get("e9_submitted"):
        _finish_stage9("timeout")
        st.rerun()

LAB2_S10_FREQS=np.array([100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150],dtype=float)
LAB2_S10_MATERIALS={
    "Madera contrachapada":{"rho":600.,"E":6.e9,"nu":.30,"eta":.020,"th":[9,12,15,18,21]},
    "Vidrio":{"rho":2500.,"E":70.e9,"nu":.23,"eta":.010,"th":[4,5,6,8,10,12]},
    "Hormigón":{"rho":2400.,"E":30.e9,"nu":.20,"eta":.010,"th":[80,100,120,150,200]},
    "Ladrillo cerámico":{"rho":1800.,"E":15.e9,"nu":.20,"eta":.015,"th":[70,100,120,140,200]},
}
LAB2_S10_LEAVES={
    "Yeso-cartón estándar":{"rho":800.,"E":2.5e9,"eta":.030,"th":[10.,12.5,15.]},
    "Yeso-cartón alta densidad":{"rho":1000.,"E":3.0e9,"eta":.030,"th":[12.5,15.]},
    "Madera contrachapada":{"rho":600.,"E":6.e9,"eta":.020,"th":[9.,12.,15.,18.,21.]},
}
LAB2_S10_DOORS={
    "P1 · Interior hueca, sin sello":18,
    "P2 · Aglomerada 35 mm":25,
    "P3 · Madera maciza 45 mm, con sellos":32,
    "P4 · Acústica simple con sellos y sello inferior":38,
    "P5 · Acústica de alta prestación":43,
    "P6 · Acústica reforzada":48,
}
LAB2_S10_QUESTIONS=[
    ("¿Por qué el Rw combinado no se obtiene promediando los Rw individuales?",["Porque los decibeles dependen del color del material","Porque deben combinarse los coeficientes de transmisión ponderados por superficie","Porque siempre se usa el menor Rw","Porque la puerta se excluye"],1),
    ("¿Qué elemento puede controlar el resultado aunque ocupe poca superficie?",["El de menor aislamiento, especialmente si tiene fugas","Solo el muro de mayor área","El cielo del pasillo","El piso de la sala"],0),
    ("Para voces y actividades interiores del pasillo, ¿qué resultado complementa principalmente a Rw?",["Rw+C","Rw+Ctr exclusivamente","La media aritmética de TL","T60"],0),
    ("¿Qué ventaja puede aportar una ventana doble con vidrios de espesores diferentes?",["Elimina toda transmisión lateral","Evita superponer exactamente las coincidencias de ambas hojas","Hace innecesario el marco","Convierte Ctr en cero"],1),
    ("Si el muro tiene Rw muy alto pero la puerta es débil, ¿qué mejora suele ser más eficiente?",["Seguir aumentando únicamente la masa del muro","Mejorar puerta, sellos y encuentros","Reducir el área del muro","Agregar absorción dentro del aula"],1),
]
LAB2_S10_EXPLANATIONS=[
    "El aislamiento compuesto se obtiene convirtiendo cada aislamiento por banda en coeficiente de transmisión, ponderándolo por su superficie y convirtiendo luego el resultado nuevamente a decibeles.",
    "Una puerta, ventana o junta con bajo aislamiento puede transmitir mucha más energía que el resto del paramento, incluso cuando su superficie es relativamente pequeña.",
    "El término C adapta Rw a espectros de ruido con predominio medio y alto, como voces y actividades interiores; por eso el resultado de referencia es Rw+C.",
    "Usar vidrios de espesores diferentes ayuda a separar sus zonas de coincidencia y evita que ambas hojas presenten exactamente la misma pérdida de aislamiento en las mismas bandas.",
    "Cuando la puerta es la vía dominante, seguir aumentando el aislamiento del muro entrega muy poco beneficio. La intervención eficiente es mejorar la hoja, los sellos perimetrales, el encuentro inferior y la instalación.",
]

def teacher_lab2_stage10_answer_key():
    return _teacher_views.run_view('teacher_lab2_stage10_answer_key', globals(), )

def _lab2_s10_indices(curve):
    curve=np.asarray(curve,dtype=float)
    rw_data=rw_from_curve(curve)
    rw=int(rw_data[0]) if rw_data else 0
    sc=np.array([-29,-26,-23,-21,-19,-17,-15,-13,-12,-11,-10,-9,-9,-9,-9,-9],dtype=float)
    stc=np.array([-20,-20,-18,-16,-15,-14,-13,-12,-11,-9,-8,-9,-10,-11,-13,-15],dtype=float)
    c=int(round(-10*np.log10(np.sum(10**((sc-curve)/10)))-rw))
    ctr=int(round(-10*np.log10(np.sum(10**((stc-curve)/10)))-rw))
    return rw,c,ctr

def _lab2_s10_single(material,thickness):
    p=LAB2_S10_MATERIALS[material]; h=float(thickness)/1000
    m=p["rho"]*h; b=p["E"]*h**3/(12*(1-p["nu"]**2))
    _,tl,_,_,_=_panel_simple_field_tl(LAB2_S10_FREQS,m,b,p["eta"])
    return np.asarray(tl,dtype=float)

def _lab2_s10_double(mat1,th1,layers1,mat2,th2,layers2,gap_mm,absorbent):
    p1,p2=LAB2_S10_LEAVES[mat1],LAB2_S10_LEAVES[mat2]
    h1=float(th1)*int(layers1)/1000; h2=float(th2)*int(layers2)/1000; d=float(gap_mm)/1000
    m1,m2=p1["rho"]*h1,p2["rho"]*h2
    b1=p1["E"]*h1**3/12; b2=p2["E"]*h2**3/12
    _,tl1,_,_,_=_panel_simple_field_tl(LAB2_S10_FREQS,m1,b1,p1["eta"])
    _,tl2,_,_,_=_panel_simple_field_tl(LAB2_S10_FREQS,m2,b2,p2["eta"])
    _,tleq,_,_,_=_panel_simple_field_tl(LAB2_S10_FREQS,m1+m2,b1+b2,p1["eta"]+p2["eta"])
    f0=(1/(2*math.pi))*math.sqrt(1.18*343**2)*math.sqrt((m1+m2)/(m1*m2*d)); f1=343/(2*math.pi*d)
    tl=np.where(LAB2_S10_FREQS<f0,tleq,np.where(LAB2_S10_FREQS<f1,tl1+tl2+20*np.log10(LAB2_S10_FREQS*d)-29,tl1+tl2+6))
    bonus={"Sin absorbente":0.,"Lana de vidrio 15 kg/m³":2.,"Lana de vidrio 32 kg/m³":3.,"Lana mineral 40 kg/m³":4.,"Lana mineral 60 kg/m³":5.}[absorbent]
    return np.asarray(tl+bonus*(1-np.exp(-LAB2_S10_FREQS/315)),dtype=float)

def _lab2_s10_door_curve(target):
    shape=np.array([-12,-10,-8,-6,-4,-2,0,1,2,3,4,5,6,7,8,9],dtype=float)
    base=REF.astype(float)+shape*.18
    current=_lab2_s10_indices(base)[0]
    return base+(float(target)-current)

def _lab2_s10_teacher_solved_examples():
    return _teacher_views.run_view('_lab2_s10_teacher_solved_examples', globals(), )

def _lab2_s10_plot(title,curves):
    fig=go.Figure()
    for name,curve in curves:
        fig.add_trace(go.Scatter(x=LAB2_S10_FREQS,y=curve,mode="lines+markers",name=name))
    fig.update_layout(title=title,height=430,xaxis_type="log",xaxis_title="Frecuencia (Hz)",yaxis_title="TL / R (dB)",margin=dict(l=30,r=20,t=55,b=35))
    fig.update_xaxes(tickvals=LAB2_S10_FREQS,ticktext=[str(int(x)) for x in LAB2_S10_FREQS])
    st.plotly_chart(fig,use_container_width=True)

def _lab2_s10_index_workbench(combined):
    """Interactive ISO-style workbench using the combined 16-band TL curve."""
    combined=np.asarray(combined,dtype=float)
    st.markdown("### Herramientas para construir Rw, C y Ctr")
    st.caption(
        "La curva de entrada es la TL combinada que acabas de obtener. Usa las "
        "herramientas para desarrollar los índices; luego ingresa tus resultados."
    )

    st.markdown("#### A · Construcción de Rw con la curva de referencia")
    automatic=_lab2_s10_indices(combined)[0]
    candidate=st.slider(
        "Posición de la curva de referencia en 500 Hz (Rw candidato)",
        min_value=max(0,automatic-15),max_value=min(100,automatic+10),
        value=max(0,automatic-5),step=1,key="l2s10_rw_candidate",
    )
    shifted=REF.astype(float)+(candidate-52)
    deviations=np.maximum(0.0,shifted-combined)
    deviation_sum=float(np.sum(deviations))
    next_deviations=np.maximum(0.0,(shifted+1)-combined)
    next_sum=float(np.sum(next_deviations))
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=LAB2_S10_FREQS,y=combined,mode="lines+markers",name="TL combinada",line=dict(color="#25d6b2",width=4)))
    fig.add_trace(go.Scatter(x=LAB2_S10_FREQS,y=shifted,mode="lines+markers",name="Referencia desplazada",line=dict(color="#ff9f43",width=3,shape="hv")))
    for i in np.where(deviations>0)[0]:
        fig.add_trace(go.Scatter(x=[LAB2_S10_FREQS[i],LAB2_S10_FREQS[i]],y=[combined[i],shifted[i]],mode="lines",line=dict(color="#ff4d6d",width=5),showlegend=False,hovertemplate=f"{int(LAB2_S10_FREQS[i])} Hz<br>Desviación: {deviations[i]:.1f} dB<extra></extra>"))
    fig.update_layout(height=430,xaxis_type="log",xaxis_title="Frecuencia (Hz)",yaxis_title="TL / R (dB)",hovermode="x unified",margin=dict(l=30,r=20,t=35,b=35))
    fig.update_xaxes(tickvals=LAB2_S10_FREQS,ticktext=[str(int(v)) for v in LAB2_S10_FREQS])
    st.plotly_chart(fig,use_container_width=True)
    a,b,c=st.columns(3)
    a.metric("Rw candidato",f"{candidate} dB")
    b.metric("Σ desviaciones",f"{deviation_sum:.1f} dB")
    c.metric("Referencia +1 dB",f"{next_sum:.1f} dB")
    if deviation_sum<=32 and next_sum>32:
        st.success("Posición final encontrada: cumple Σdᵢ ≤ 32 dB y al subir 1 dB deja de cumplir.")
    elif deviation_sum<=32:
        st.info("Esta posición cumple, pero todavía debes comprobar si la referencia puede subir 1 dB.")
    else:
        st.error("Esta posición no cumple: baja la curva hasta que Σdᵢ sea menor o igual que 32 dB.")
    with st.expander("Ver desviaciones banda por banda"):
        st.dataframe(pd.DataFrame({"Frecuencia (Hz)":LAB2_S10_FREQS.astype(int),"TL combinada (dB)":np.round(combined,1),"Referencia (dB)":shifted.astype(int),"dᵢ desfavorable (dB)":np.round(deviations,1)}),hide_index=True,use_container_width=True)

    st.markdown("#### B · Construcción de C y Ctr")
    spectrum_c=np.array([-29,-26,-23,-21,-19,-17,-15,-13,-12,-11,-10,-9,-9,-9,-9,-9],dtype=float)
    spectrum_ctr=np.array([-20,-20,-18,-16,-15,-14,-13,-12,-11,-9,-8,-9,-10,-11,-13,-15],dtype=float)
    x1=float(-10*np.log10(np.sum(10**((spectrum_c-combined)/10))))
    x2=float(-10*np.log10(np.sum(10**((spectrum_ctr-combined)/10))))
    st.latex(r"X_1=-10\log_{10}\left(\sum_i10^{(L_{1,i}-R_i)/10}\right),\qquad C=X_1-R_w")
    st.latex(r"X_2=-10\log_{10}\left(\sum_i10^{(L_{2,i}-R_i)/10}\right),\qquad C_{tr}=X_2-R_w")
    step=st.select_slider(
        "Recorre el cálculo espectral",options=[1,2,3,4],value=1,
        format_func=lambda n:{1:"1 · Curva TL combinada",2:"2 · Aplicar espectros",3:"3 · Suma energética",4:"4 · Obtener C y Ctr"}[n],
        key="l2s10_adaptation_step",
    )
    spectral=go.Figure()
    spectral.add_trace(go.Scatter(x=LAB2_S10_FREQS,y=combined,mode="lines+markers",name="TL combinada",line=dict(color="#25d6b2",width=4)))
    if step>=2:
        spectral.add_trace(go.Bar(x=LAB2_S10_FREQS,y=spectrum_c,name="Espectro 1",marker_color="#56a8ff",opacity=.55))
        spectral.add_trace(go.Bar(x=LAB2_S10_FREQS,y=spectrum_ctr,name="Espectro 2",marker_color="#b06cff",opacity=.45))
    if step>=3:
        spectral.add_trace(go.Scatter(x=LAB2_S10_FREQS,y=spectrum_c-combined,mode="lines+markers",name="L1−R",line=dict(color="#ff9f43",width=3)))
        spectral.add_trace(go.Scatter(x=LAB2_S10_FREQS,y=spectrum_ctr-combined,mode="lines+markers",name="L2−R",line=dict(color="#ff4d6d",width=3)))
    spectral.update_layout(height=410,barmode="overlay",xaxis_type="log",xaxis_title="Frecuencia (Hz)",yaxis_title="Nivel relativo / TL (dB)",margin=dict(l=30,r=20,t=25,b=35))
    spectral.update_xaxes(tickvals=LAB2_S10_FREQS,ticktext=[str(int(v)) for v in LAB2_S10_FREQS])
    st.plotly_chart(spectral,use_container_width=True)
    if step>=3:
        u,v=st.columns(2); u.metric("X₁",f"{x1:.1f} dB"); v.metric("X₂",f"{x2:.1f} dB")
    if step==4:
        st.info("Usa el Rw final obtenido en la herramienta A y calcula C = X₁ − Rw y Ctr = X₂ − Rw. Ingresa esos tres resultados abajo.")
    with st.expander("Ver cálculo espectral banda por banda"):
        st.dataframe(pd.DataFrame({"Frecuencia (Hz)":LAB2_S10_FREQS.astype(int),"TL combinada Rᵢ (dB)":np.round(combined,1),"L₁ (dB)":spectrum_c.astype(int),"L₁−Rᵢ (dB)":np.round(spectrum_c-combined,1),"L₂ (dB)":spectrum_ctr.astype(int),"L₂−Rᵢ (dB)":np.round(spectrum_ctr-combined,1)}),hide_index=True,use_container_width=True)





LAB_STAGE_FUNCTIONS = {
    1: [lab1_stage0,lab1_stage1,lab1_stage2,lab1_stage3,lab1_stage4,lab1_stage5,
        lab1_stage6,lab1_stage7,lab1_stage8,lab1_stage9,lab1_stage10],
    2: [lab2_stage0,lab2_stage1,lab2_stage2,lab2_stage3,lab2_stage4,lab2_stage5,
        lab2_stage6,lab2_stage7,lab2_stage8,lab2_stage9,lab2_stage10],
}










def _results_catalog():
    return _result_views.run_view("_results_catalog", globals())

def results_view(client, catalog, user_key):
    return _result_views.run_view("results_view", globals(), client, catalog, user_key)

def student_sidebar_summary(client, user_key):
    return _result_views.run_view("student_sidebar_summary", globals(), client, user_key)

def course_dashboard():
    return _course_views.run_view("course_dashboard", globals())

def _future_saved(class_id):
    return _course_views.run_view("_future_saved", globals(), class_id)

def _save_future_state(class_id, state):
    return _course_views.run_view("_save_future_state", globals(), class_id, state)

def future_lab_view(lab):
    return _course_views.run_view("future_lab_view", globals(), lab)

def future_print_view(lab):
    return _course_views.run_view("future_print_view", globals(), lab)

def calculation_notebook():
    if not ENABLE_CALCULATION_NOTEBOOK:
        return
    header(f"MESA DE CÁLCULO · LABORATORIO {ACTIVE_LAB}","Cuaderno técnico personal",
           "Desarrolla el ejercicio dentro de la plataforma y guarda datos, conversiones, fórmula, sustitución, resultado e interpretación.")
    question_key=st.text_input("Código o nombre del ejercicio",key="notebook_question")
    title=st.text_input("Título del desarrollo",value="Desarrollo de ejercicio",key="notebook_title")
    c1,c2=st.columns(2)
    known=c1.text_area("1. Datos conocidos",key="notebook_known")
    conversions=c2.text_area("2. Conversión de unidades",key="notebook_conversions")
    selected_formula=st.text_area("3. Fórmula seleccionada",key="notebook_formula")
    substitution=st.text_area("4. Sustitución numérica",key="notebook_substitution")
    result=st.text_area("5. Resultado con unidad",key="notebook_result")
    interpretation=st.text_area("6. Interpretación física o decisión",key="notebook_interpretation")
    if st.button("Guardar desarrollo",type="primary"):
        client=_supabase()
        if client is None:
            st.warning("Configura Supabase para guardar este cuaderno permanentemente.")
        else:
            existing=client.table("notebook_entries").select("id").eq(
                "class_id",CLASS_ID).eq("user_key",st.session_state.user_key).eq(
                "question_key",question_key or "general").limit(1).execute().data or []
            data={"course_id":COURSE_ID,"class_id":CLASS_ID,"user_key":st.session_state.user_key,
                  "question_key":question_key or "general","title":title,"known_data":known,
                  "unit_conversions":conversions,"selected_formula":selected_formula,
                  "substitution":substitution,"result":result,"interpretation":interpretation,
                  "updated_at":_now()}
            if existing:
                client.table("notebook_entries").update(data).eq("id",existing[0]["id"]).execute()
            else:
                client.table("notebook_entries").insert(data).execute()
            st.success("Desarrollo guardado permanentemente.")
    client=_supabase()
    if client is not None:
        saved=client.table("notebook_entries").select("*").eq(
            "class_id",CLASS_ID).eq("user_key",st.session_state.user_key).order(
            "updated_at",desc=True).execute().data or []
        with st.expander(f"Mis desarrollos guardados ({len(saved)})"):
            for entry in saved:
                st.markdown(f"**{entry.get('title')} · {entry.get('question_key')}**")
                st.caption(entry.get("updated_at","").replace("T"," ")[:19])
                st.write(entry.get("result") or "Sin resultado registrado")

def login():
    return _access_views.run_view("login", globals())

if st.query_params.get("projection")=="1":
    projection_view()
    st.stop()

# El formulario es una herramienta de consulta independiente y puede abrirse
# en otra pestaña sin crear una segunda sesión de alumno o docente.
if st.query_params.get("formulas")=="1":
    formula_reference()
    st.stop()

# Vista visual de impresión del laboratorio completo. No usa el generador editorial
# ni reconstruye el contenido: renderiza las etapas reales con estilos de impresión.
if st.query_params.get("print_lab") in ("1", "2"):
    print_lab_number = int(st.query_params["print_lab"])
    render_print_view(globals(), print_lab_number)
    st.stop()

future_print_id = st.query_params.get("print_future_lab")
if future_print_id in FUTURE_LABS:
    future_print_view(FUTURE_LABS[future_print_id])
    st.stop()

st.session_state.pop("projection_mode",None)

if not st.session_state.get("access"):
    login();st.stop()

# Laboratories 3–10 use their own renderer and class identifier.
future_lab_id=st.session_state.get("future_lab_id")
if future_lab_id in FUTURE_LABS:
    future_lab=FUTURE_LABS[future_lab_id]
    if st.session_state.get("role")=="Alumno":
        client=_supabase()
        allowed=False
        if client is not None:
            try:
                row=_class_row(future_lab_id)
                rows=[row] if row else []
                allowed=bool(rows and rows[0].get("status")=="published" and
                             _is_open(rows[0].get("opens_at") or future_lab["opens_at"]))
            except Exception:
                allowed=False
        if not allowed:
            st.session_state.pop("future_lab_id",None)
            st.warning("Ese laboratorio todavía no está publicado para alumnos.")
            st.rerun()
    future_lab_view(future_lab)
    st.stop()

# A student can never keep or reopen a laboratory that the teacher has hidden.
if st.session_state.get("role")=="Alumno":
    client=_supabase()
    if client is not None:
        try:
            selected_row_cached=_class_row(CLASS_ID)
            selected_status=[selected_row_cached] if selected_row_cached else []
            selected_row=selected_status[0] if selected_status else {}
            selected_opening=_effective_opening(
                ACTIVE_LAB,
                selected_row.get("opens_at"),
                ACADEMIC_COURSES[0]["labs"][ACTIVE_LAB-1]["opens_at"],
            )
            if (selected_row.get("status")!="published" or
                    not _is_open(selected_opening)):
                st.session_state["active_lab"]=1
                st.session_state["main_view"]="🏠 Mis clases"
                st.warning("Ese laboratorio todavía no está habilitado para alumnos.")
                st.rerun()
        except Exception:
            st.error("No fue posible comprobar la disponibilidad del laboratorio.")
            st.stop()

# Load only the selected laboratory's saved answers.
if st.session_state.get("_loaded_lab") != ACTIVE_LAB:
    for state_key in list(st.session_state.keys()):
        if _is_answer_state(state_key):
            del st.session_state[state_key]
    load_user_progress(st.session_state.get("user_key"))
    st.session_state["_loaded_lab"]=ACTIVE_LAB
if st.session_state.pop("_open_lab_requested",False):
    st.session_state["main_view"]=f"📚 Laboratorio {ACTIVE_LAB} y actividades"

with st.sidebar:
    uc=ROOT/"assets/logos/logo_uc.png";decon=ROOT/"assets/logos/logo_decon_uc.png"
    if uc.exists(): st.image(str(uc),width=75)
    if decon.exists(): st.image(str(decon),width=130)
    st.markdown("## ◉ LABORATORIO")
    st.markdown(
        f'<div style="background:#0b4f83;border:1px solid #59d4ef;border-radius:12px;'
        f'padding:.75rem .85rem;margin:.35rem 0 .8rem"><b>LABORATORIO {ACTIVE_LAB}</b><br>'
        f'<span style="font-size:.78rem;color:#d9f5ff">AISLAMIENTO A RUIDO AÉREO</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN")
    st.markdown(f"**{st.session_state.name}**  \n{st.session_state.role}")
    results_view_label=(
        "📝 Evaluaciones entregadas"
        if st.session_state.get("role")=="Docente"
        else "🎓 Mi desempeño"
    )
    lab_view_label=f"📚 Laboratorio {ACTIVE_LAB} y actividades"
    view_options=[
        "🏠 Mis clases",
        results_view_label,
        lab_view_label,
    ]
    if st.session_state.get("main_view") not in view_options:
        st.session_state["main_view"]="🏠 Mis clases"

    st.markdown(
        """
        <div style="margin:.45rem 0 .35rem">
          <div style="font-size:.72rem;font-weight:850;letter-spacing:.08em;color:#8eddf2">
            NAVEGACIÓN
          </div>
          <div style="font-size:.72rem;color:#b8d5e5;margin-top:.08rem">
            Accesos principales
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    active_view=st.session_state.get("main_view")

    st.markdown(
        """
        <style>
        /* Navegación principal inicial: mismas tarjetas-radio de los laboratorios.
           Se apunta a la key del widget para no depender de :has()/aria-label,
           cuyo DOM puede variar en el primer render de Streamlit. */
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [role="radiogroup"] {
            gap: .44rem !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [role="radiogroup"] > label {
            width: 100% !important;
            margin: 0 !important;
            padding: .62rem .68rem !important;
            border: 1px solid rgba(142, 221, 242, .28) !important;
            border-radius: 12px !important;
            background: rgba(12, 73, 112, .30) !important;
            transition: background .16s ease, border-color .16s ease, box-shadow .16s ease, transform .08s ease !important;
            cursor: pointer !important;
            align-items: flex-start !important;
            text-align: left !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [role="radiogroup"] > label:hover {
            background: rgba(21, 111, 160, .34) !important;
            border-color: rgba(89, 212, 239, .58) !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [role="radiogroup"] > label:active {
            transform: translateY(1px);
        }
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(135deg, rgba(8, 94, 143, .72), rgba(12, 125, 166, .52)) !important;
            border-color: #59d4ef !important;
            box-shadow: inset 3px 0 0 #59d4ef, 0 0 0 1px rgba(89, 212, 239, .08) !important;
        }
        /* Mantener visible el círculo del radio desde el primer render. */
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [data-baseweb="radio"] {
            display: flex !important;
            opacity: 1 !important;
            visibility: visible !important;
            flex: 0 0 auto !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] input[type="radio"] {
            accent-color: #59d4ef !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [data-testid="stMarkdownContainer"] p {
            font-weight: 700 !important;
            line-height: 1.22 !important;
            text-align: left !important;
        }
        section[data-testid="stSidebar"] div[class*="st-key-main_nav_radio_"] [data-testid="stCaptionContainer"] {
            color: #a9cada !important;
            font-size: .69rem !important;
            line-height: 1.18 !important;
            margin-top: .12rem !important;
            text-align: left !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    nav_titles={
        "🏠 Mis clases":"📚  Mis clases",
        results_view_label:(
            "📝  Evaluaciones entregadas"
            if st.session_state.get("role")=="Docente"
            else "📊  Mi desempeño"
        ),
        lab_view_label:(
            f"🧪  Laboratorio {ACTIVE_LAB}"
            if st.session_state.get("role")=="Docente"
            else "🧪  Laboratorios y actividades"
        ),
    }
    nav_captions=[
        "Cursos y laboratorios",
        (
            "Respuestas y puntajes"
            if st.session_state.get("role")=="Docente"
            else "Evaluaciones, notas y avance formativo"
        ),
        (
            "Ruta y actividades del laboratorio actual"
            if st.session_state.get("role")=="Docente"
            else "Ruta, ejercicios y progreso"
        ),
    ]
    nav_key=f"main_nav_radio_{ACTIVE_LAB}"
    if st.session_state.get(nav_key) not in view_options:
        st.session_state[nav_key]=active_view

    selected_view=st.radio(
        "Navegación principal",
        view_options,
        index=view_options.index(active_view),
        format_func=lambda option: nav_titles[option],
        captions=nav_captions,
        key=nav_key,
        label_visibility="collapsed",
        help="Selecciona el espacio al que quieres ir.",
    )
    if selected_view!=active_view:
        st.session_state["main_view"]=selected_view
        st.rerun()

    view=st.session_state["main_view"]
    # Resumen académico del alumno: separa avance formativo de notas oficiales.
    # Las únicas calificaciones del curso provienen del Laboratorio 2,
    # etapas 9 y 10; el resto se muestra como progreso de aprendizaje.
    if st.session_state.role=="Alumno":
        student_sidebar_summary(_supabase(), st.session_state.get("user_key", ""))
    formula_popup_button()
    st.link_button(
        "📕 Generar apunte visual (PDF)",
        f"?print_lab={ACTIVE_LAB}",
        width="stretch",
        help="Abre una vista limpia del laboratorio para imprimirla o guardarla como PDF.",
    )
    if st.session_state.role=="Docente":
        st.link_button(
            "🖥️ Abrir vista para Zoom",
            f"?projection=1&lab={ACTIVE_LAB}",
            use_container_width=True,
            help="Ábrela en otra ventana y comparte solo esa ventana en Zoom.",
        )
        projection_options={
            f"{prefix} · {title}":stage_number
            for stage_number,(prefix,title) in enumerate(LAB_STAGE_TITLES[ACTIVE_LAB])
            if stage_number in LABORATORIES[ACTIVE_LAB]["stages"]
        }
        projection_label=st.selectbox(
            "Contenido visible en Zoom",
            list(projection_options),
            key=f"projection_stage_selector_lab_{ACTIVE_LAB}",
        )
        projection_stage=projection_options[projection_label]
        if st.button("Mostrar etapa en Zoom",use_container_width=True):
            _set_projection(stage=projection_stage)
            st.success(f"{projection_label} del Laboratorio {ACTIVE_LAB} enviada a Zoom. Pulsa ‘Actualizar pantalla’ en la ventana de Zoom.")
        with st.expander("⚙️ Gestión de alumnos"):
            teacher_student_management()
        with st.expander("🔒 Publicación de laboratorios"):
            teacher_publication_management()
        st.caption("Las evaluaciones de los alumnos se revisan en la vista “Evaluaciones entregadas”.")
    active_titles=LAB_STAGE_TITLES[ACTIVE_LAB]
    active_minutes=STAGE_MINUTES if ACTIVE_LAB==1 else dict(enumerate(LAB2_MINUTES))
    labels=[
        f"{number} · {title} · {active_minutes[i]} min"
        for i,(number,title) in enumerate(active_titles)
    ]
    selected=None
    if view==view_options[2]:
        lab_stages=LABORATORIES[ACTIVE_LAB]["stages"]
        lab_labels=[labels[i] for i in lab_stages]
        stage_state_key=f"selected_stage_lab_{ACTIVE_LAB}"
        if st.session_state.get(stage_state_key) not in lab_labels:
            st.session_state[stage_state_key]=lab_labels[0]
        selected=st.radio("Ruta de aprendizaje",lab_labels,label_visibility="collapsed",
                          key=stage_state_key)
    if st.button("Cerrar sesión",use_container_width=True):
        st.session_state.clear();st.rerun()
    st.caption("Docente: Marco Araos Barría")

if view=="🏠 Mis clases":
    course_dashboard()
elif view==results_view_label:
    if st.session_state.get("role")=="Docente":
        teacher_course_results(compact=False)
    else:
        results_view(_supabase(), _results_catalog(), st.session_state.get("user_key", ""))
elif view==view_options[2]:
    lab_stages=LABORATORIES[ACTIVE_LAB]["stages"]
    if selected not in labels:
        selected=labels[lab_stages[0]]
    idx=labels.index(selected)
    st.session_state["_current_stage"] = idx
    st.session_state["_current_lab"] = ACTIVE_LAB
    st.caption(f"Curso: Aislamiento a ruido aéreo · Laboratorio {ACTIVE_LAB} de 2")
    LAB_STAGE_FUNCTIONS[ACTIVE_LAB][idx]()

# Autosave after every interaction. Closing the browser or changing tabs does not erase work.
save_user_progress()
