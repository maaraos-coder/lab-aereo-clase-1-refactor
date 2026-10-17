"""Solución desarrollada de referencia para la vista Docente del C4·L2."""

import math


VERTICES = [
    {"Vértice":"A","Latitud":-33.6126705,"Longitud":-70.5715419},
    {"Vértice":"B","Latitud":-33.6124714,"Longitud":-70.5701802},
    {"Vértice":"C","Latitud":-33.6124894,"Longitud":-70.5701805},
    {"Vértice":"D","Latitud":-33.6125562,"Longitud":-70.5706021},
    {"Vértice":"E","Latitud":-33.6128998,"Longitud":-70.5705329},
    {"Vértice":"F","Latitud":-33.6127983,"Longitud":-70.5700029},
    {"Vértice":"G","Latitud":-33.6131420,"Longitud":-70.5699229},
    {"Vértice":"H","Latitud":-33.6132253,"Longitud":-70.5704633},
    {"Vértice":"I","Latitud":-33.6135960,"Longitud":-70.5703838},
    {"Vértice":"J","Latitud":-33.6135037,"Longitud":-70.5698432},
    {"Vértice":"K","Latitud":-33.6138563,"Longitud":-70.5697742},
    {"Vértice":"L","Latitud":-33.6139396,"Longitud":-70.5703146},
    {"Vértice":"M","Latitud":-33.6143826,"Longitud":-70.5702257},
    {"Vértice":"N","Latitud":-33.6145330,"Longitud":-70.5711661},
]

PARTS = [
    {"Parte / obra":"Torres habitacionales","Cantidad":"6","Ubicación / sector":"Predio del proyecto"},
    {"Parte / obra":"Departamentos","Cantidad":"360","Ubicación / sector":"6 torres de 4 pisos"},
    {"Parte / obra":"Estacionamientos vehiculares","Cantidad":"276","Ubicación / sector":"Superficie y subterráneo"},
    {"Parte / obra":"Estacionamientos de bicicletas","Cantidad":"138","Ubicación / sector":"Proyecto"},
    {"Parte / obra":"Locales comerciales","Cantidad":"4","Ubicación / sector":"Proyecto"},
    {"Parte / obra":"Sedes sociales","Cantidad":"3","Ubicación / sector":"Proyecto"},
    {"Parte / obra":"Superficie del terreno","Cantidad":"22.701 m² aprox.","Ubicación / sector":"Puente Alto"},
]

PHASES = [
    {"N°":1,"Etapa / frente":"Escenario 1 · Movimiento de tierra","Actividad principal":"Movimiento de tierra","Respaldo":"Anexo 05 · Tabla 13 / Figura 10"},
    {"N°":2,"Etapa / frente":"Escenario 2 · Obra gruesa, terminaciones y urbanización","Actividad principal":"Obra gruesa a nivel de suelo y altura, terminaciones y urbanización","Respaldo":"Anexo 05 · Tablas 14–17 / Figura 11"},
    {"N°":3,"Etapa / frente":"Escenario 3 · Obras IMIV","Actividad principal":"Obras de mitigación vial","Respaldo":"Anexo 05 · Tabla 18 / Figura 12"},
]

MACHINERY = [
    {"Frente":"Escenario 1 · Movimiento de tierra","Maquinaria":"Minicargador · Retroexcavadora · Excavadora","Cantidad":"1 de cada tipo","Fuente":"Tabla 13"},
    {"Frente":"Escenario 2 · Obra gruesa suelo","Maquinaria":"Rodillo compactador · Minicargador · Retroexcavadora · Camión mixer + bomba","Cantidad":"1 de cada tipo","Fuente":"Tabla 14"},
    {"Frente":"Escenario 2 · Obra gruesa altura","Maquinaria":"Grúa pluma · Vibrador de inmersión","Cantidad":"1 de cada tipo","Fuente":"Tabla 15"},
    {"Frente":"Escenario 2 · Urbanización","Maquinaria":"Rodillo · Minicargador · Retroexcavadora · Motoniveladora · Mixer + bomba","Cantidad":"1 de cada tipo","Fuente":"Tabla 16"},
    {"Frente":"Escenario 2 · Terminaciones","Maquinaria":"Minicargador · Alzahombre","Cantidad":"1 de cada tipo","Fuente":"Tabla 17"},
    {"Frente":"Escenario 3 · Obras IMIV","Maquinaria":"Cango · Mixer + bomba · Vibrador · Rodillo compactador","Cantidad":"1 de cada tipo","Fuente":"Tabla 18"},
]

CHRONOLOGY = [
    {"Etapa":"Constructiva 1","Inicio":"2° semestre 2025","Término":"1° semestre 2027","Superposición":"Sí","Detalle":"Edificios 1 y 5"},
    {"Etapa":"Constructiva 2","Inicio":"1° semestre 2026","Término":"2° semestre 2027","Superposición":"Sí","Detalle":"Edificios 2 y 3"},
    {"Etapa":"Constructiva 3","Inicio":"2° semestre 2026","Término":"1° semestre 2028","Superposición":"Sí","Detalle":"Edificios 4 y 6"},
    {"Etapa":"Fase de construcción","Inicio":"Septiembre 2025","Término":"Enero 2028 aprox.","Superposición":"Sí","Detalle":"Duración aproximada: 29 meses"},
]

RECEPTORS = [
    {"Receptor":"R01","Uso":"Complejo educacional","Latitud":-33.6119671,"Longitud":-70.5708285,"Altura [m]":1.5,"Dist. al predio [m]":67,"Condición":"No colindante"},
    {"Receptor":"R02","Uso":"Vivienda","Latitud":-33.6127289,"Longitud":-70.5704974,"Altura [m]":1.5,"Dist. al predio [m]":0,"Condición":"Colindante"},
    {"Receptor":"R03","Uso":"Vivienda","Latitud":-33.6128730,"Longitud":-70.5697995,"Altura [m]":1.5,"Dist. al predio [m]":16,"Condición":"No colindante"},
    {"Receptor":"R04","Uso":"Vivienda","Latitud":-33.6134444,"Longitud":-70.5702517,"Altura [m]":1.5,"Dist. al predio [m]":0,"Condición":"Colindante"},
    {"Receptor":"R05","Uso":"Vivienda","Latitud":-33.6137228,"Longitud":-70.5696316,"Altura [m]":1.5,"Dist. al predio [m]":15,"Condición":"No colindante"},
    {"Receptor":"R06","Uso":"Vivienda","Latitud":-33.6139859,"Longitud":-70.5702185,"Altura [m]":1.5,"Dist. al predio [m]":0,"Condición":"Colindante"},
    {"Receptor":"R07","Uso":"Vivienda","Latitud":-33.6144599,"Longitud":-70.5705289,"Altura [m]":1.5,"Dist. al predio [m]":0,"Condición":"Colindante"},
    {"Receptor":"R08","Uso":"Vivienda","Latitud":-33.6145446,"Longitud":-70.5709615,"Altura [m]":1.5,"Dist. al predio [m]":0,"Condición":"Colindante"},
    {"Receptor":"R09","Uso":"Vivienda","Latitud":-33.6139433,"Longitud":-70.5714464,"Altura [m]":1.5,"Dist. al predio [m]":0,"Condición":"Colindante"},
]


SOURCE_ROWS = [
    ("Escenario 1 · Movimiento de tierra","Minicargador","C4 · 14",[68,67,63,62,62,61,54,47],67),
    ("Escenario 1 · Movimiento de tierra","Retroexcavadora","C2 · 8",[74,66,64,64,63,60,59,50],68),
    ("Escenario 1 · Movimiento de tierra","Excavadora","C2 · 23",[79,81,68,69,66,65,61,52],73),
    ("Escenario 2 · Obra gruesa suelo","Rodillo compactador","C2 · 40",[82,78,67,71,67,64,60,57],73),
    ("Escenario 2 · Obra gruesa suelo","Minicargador","C4 · 14",[68,67,63,62,62,61,54,47],67),
    ("Escenario 2 · Obra gruesa suelo","Retroexcavadora","C2 · 8",[74,66,64,64,63,60,59,50],68),
    ("Escenario 2 · Obra gruesa suelo","Mixer + bomba","C4 · 32",[73,73,77,76,72,70,65,62],78),
    ("Escenario 2 · Obra gruesa altura","Grúa pluma","C4 · 46",[78,69,67,64,62,57,49,40],67),
    ("Escenario 2 · Obra gruesa altura","Vibrador de inmersión","C4 · 34",[62,70,70,64,62,61,59,56],69),
    ("Escenario 2 · Urbanización","Rodillo compactador","C2 · 40",[82,78,67,71,67,64,60,57],73),
    ("Escenario 2 · Urbanización","Minicargador","C4 · 14",[68,67,63,62,62,61,54,47],67),
    ("Escenario 2 · Urbanización","Retroexcavadora","C2 · 8",[74,66,64,64,63,60,59,50],68),
    ("Escenario 2 · Urbanización","Motoniveladora","Consultor",[72,75,67,59,60,56,49,44],65),
    ("Escenario 2 · Urbanización","Mixer + bomba","C4 · 32",[73,73,77,76,72,70,65,62],78),
    ("Escenario 2 · Terminaciones","Minicargador","C4 · 14",[68,67,63,62,62,61,54,47],67),
    ("Escenario 2 · Terminaciones","Alzahombre","C4 · 57",[78,76,62,63,60,59,58,49],67),
    ("Escenario 3 · Obras IMIV","Cango","C1 · 8",[77,72,73,69,68,66,64,60],74),
    ("Escenario 3 · Obras IMIV","Mixer + bomba","C4 · 32",[73,73,77,76,72,70,65,62],78),
    ("Escenario 3 · Obras IMIV","Vibrador de inmersión","C4 · 34",[62,70,70,64,62,61,59,56],69),
    ("Escenario 3 · Obras IMIV","Rodillo compactador","C2 · 40",[82,78,67,71,67,64,60,57],73),
]

FRONTS = [
    ("Escenario 1 · Movimiento de tierra",75,103,"R02","Eyzaguirre_E1_Original"),
    ("Escenario 2 · Obra gruesa suelo",80,108,"R02 / R06","Eyzaguirre_E2_Suelo_Original"),
    ("Escenario 2 · Obra gruesa altura",71,99,"R06","Eyzaguirre_E2_Altura_Original"),
    ("Escenario 2 · Urbanización",80,108,"R04 / R06","Eyzaguirre_E2_Urbanizacion_Original"),
    ("Escenario 2 · Terminaciones",70,98,"R07 / R08","Eyzaguirre_E2_Terminaciones_Original"),
    ("Escenario 3 · Obras IMIV",80,108,"RIMIV05 / RIMIV06","Eyzaguirre_E3_IMIV_Original"),
]

ORIGINAL_MATRIX = {
    "R01":{"Escenario 1":51,"Escenario 2":48,"Escenario 3":66},
    "R02":{"Escenario 1":66,"Escenario 2":72,"Escenario 3":70},
    "R03":{"Escenario 1":59,"Escenario 2":67,"Escenario 3":64},
    "R04":{"Escenario 1":65,"Escenario 2":71,"Escenario 3":45},
    "R05":{"Escenario 1":59,"Escenario 2":67,"Escenario 3":64},
    "R06":{"Escenario 1":64,"Escenario 2":72,"Escenario 3":58},
    "R07":{"Escenario 1":62,"Escenario 2":69,"Escenario 3":59},
    "R08":{"Escenario 1":62,"Escenario 2":67,"Escenario 3":48},
    "R09":{"Escenario 1":55,"Escenario 2":59,"Escenario 3":45},
    "RIMIV01":{"Escenario 3":74},"RIMIV02":{"Escenario 3":70},
    "RIMIV03":{"Escenario 3":73},"RIMIV04":{"Escenario 3":73},
    "RIMIV05":{"Escenario 3":78},"RIMIV06":{"Escenario 3":78},
    "RIMIV07":{"Escenario 3":77},"RIMIV08":{"Escenario 3":73},
    "RIMIV09":{"Escenario 3":76},
}

REDUCTIONS = {
    "Escenario 1":{"R01":3,"R02":3,"R03":4,"R04":3,"R05":4,"R06":3,"R07":3,"R08":3,"R09":2},
    "Escenario 2":{"R01":4,"R02":8,"R03":5,"R04":8,"R05":5,"R06":8,"R07":6,"R08":5,"R09":4},
    "Escenario 3":{"R01":4,"R02":6,"R03":4,"R04":3,"R05":4,"R06":4,"R07":4,"R08":3,"R09":3,
                   "RIMIV01":10,"RIMIV02":7,"RIMIV03":9,"RIMIV04":9,"RIMIV05":14,"RIMIV06":14,
                   "RIMIV07":13,"RIMIV08":9,"RIMIV09":12},
}

CONTROL_DESIGN = [
    {"Frente / condición":"Escenario 1 · Movimiento de tierra","Receptor crítico":"R02","LAeq original [dB(A)]":66,"Medida seleccionada":"Barrera acústica","Especificación":"Pantalla móvil de 4,0 m; panel continuo ≥12 kg/m²; sin holguras; cercana al frente y extendida lateralmente","Justificación":"Interrumpe la visual acústica sin impedir el desplazamiento del frente.","Proyecto controlado":"Eyzaguirre_E1_Controlado"},
    {"Frente / condición":"Escenario 2 · Obra gruesa suelo","Receptor crítico":"R02 / R06","LAeq original [dB(A)]":72,"Medida seleccionada":"Encierro completo","Especificación":"Encierro modular para bomba; 4×3×3 m; panel doble OSB 18 mm con absorbente interior; puertas selladas","Justificación":"Controla la fuente estacionaria dominante y mantiene accesos desmontables.","Proyecto controlado":"Eyzaguirre_E2_Suelo_Controlado"},
    {"Frente / condición":"Escenario 2 · Obra gruesa altura","Receptor crítico":"R06","LAeq original [dB(A)]":72,"Medida seleccionada":"Reducción directa","Especificación":"Equipo eléctrico de menor emisión y mantenimiento; reducción de fuente adoptada: 8 dB","Justificación":"Una barrera pierde eficacia en altura; se controla la emisión del equipo.","Proyecto controlado":"Eyzaguirre_E2_Altura_Controlado"},
    {"Frente / condición":"Escenario 2 · Urbanización","Receptor crítico":"R04 / R06","LAeq original [dB(A)]":72,"Medida seleccionada":"Semiencierro","Especificación":"Tres caras y cubierta, 3,5 m; cara abierta orientada al interior del predio; revestimiento absorbente","Justificación":"Permite alimentación de materiales y evita orientar la abertura hacia viviendas.","Proyecto controlado":"Eyzaguirre_E2_Urbanizacion_Controlado"},
    {"Frente / condición":"Escenario 2 · Terminaciones","Receptor crítico":"R07 / R08","LAeq original [dB(A)]":69,"Medida seleccionada":"Silenciador","Especificación":"Silenciador disipativo en descarga/ventilación; IL 10–15 dB entre 250 Hz y 2 kHz","Justificación":"Reduce la trayectoria dominante sin bloquear ventilación ni operación.","Proyecto controlado":"Eyzaguirre_E2_Terminaciones_Controlado"},
    {"Frente / condición":"Escenario 3 · Obras IMIV","Receptor crítico":"RIMIV05 / RIMIV06","LAeq original [dB(A)]":78,"Medida seleccionada":"Encierro + silenciador","Especificación":"Cabina desmontable del compresor asociado al cango; panel doble; absorción interior; ventilación silenciada","Justificación":"El exceso exige controlar transmisión por paneles y aberturas de ventilación.","Proyecto controlado":"Eyzaguirre_E3_IMIV_Controlado"},
]


def _source_table():
    labels=["63 Hz","125 Hz","250 Hz","500 Hz","1 kHz","2 kHz","4 kHz","8 kHz"]
    rows=[]
    for front,machine,reference,bands,npseq in SOURCE_ROWS:
        row={"Frente":front,"Maquinaria":machine,"Referencia":reference,"NPSeq @10 m [dB(A)]":npseq,"LWA aprox. [dB(A)]":npseq+28}
        row.update(dict(zip(labels,bands)))
        rows.append(row)
    return rows


def _original_rows():
    return [
        {"Frente":scenario,"Receptor":receptor,"LAeq original [dB(A)]":level,"Límite [dB(A)]":65,
         "Excedencia [dB]":max(0,level-65),"Resultado":"Sobre el límite" if level>65 else "Bajo o en el límite"}
        for receptor,scenarios in ORIGINAL_MATRIX.items() for scenario,level in scenarios.items()
    ]


def _comparison_rows():
    rows=[]
    for receptor,scenarios in ORIGINAL_MATRIX.items():
        for scenario,original in scenarios.items():
            reduction=REDUCTIONS.get(scenario,{}).get(receptor,0)
            controlled=original-reduction
            rows.append({
                "Frente":scenario,"Receptor":receptor,"Original [dB(A)]":original,
                "Controlado [dB(A)]":controlled,"Reducción [dB]":reduction,
                "Límite ref. [dB(A)]":65,"Margen [dB]":65-controlled,
                "Resultado":"Bajo el límite" if controlled<65 else "En el límite",
            })
    return rows


def _tl_panel():
    mass=650*0.018
    return [
        {"Material":"OSB","Densidad [kg/m³]":650,"Espesor [mm]":18,"Masa superficial [kg/m²]":round(mass,1),
         "Banda":f"{frequency:g} Hz","TL estimado [dB]":round(20*math.log10(mass*frequency)-47,1)}
        for frequency in (63,125,250,500,1000,2000,4000,8000)
    ]


def build_reference_report():
    comparisons=_comparison_rows()
    controlled=[{"Frente":r["Frente"],"Receptor":r["Receptor"],"LAeq controlado [dB(A)]":r["Controlado [dB(A)]"]} for r in comparisons]
    final=[]
    for row in CONTROL_DESIGN:
        scenario="Escenario 1" if "Escenario 1" in row["Frente / condición"] else "Escenario 2" if "Escenario 2" in row["Frente / condición"] else "Escenario 3"
        related=[r for r in comparisons if r["Frente"]==scenario]
        final.append({
            "Frente / condición":row["Frente / condición"],"Medida definitiva":row["Medida seleccionada"],
            "Máximo controlado [dB(A)]":max(r["Controlado [dB(A)]"] for r in related),
            "Reducción media [dB]":round(sum(r["Reducción [dB]"] for r in related)/len(related),1),
            "Decisión final":"Mantener con inspección y mantenimiento",
            "Especificación final":row["Especificación"],"Proyecto definitivo":row["Proyecto controlado"],
        })
    relevance=[
        {"Receptor":r["Receptor"],"Justificación":"Receptor sensible representativo del entorno y de la exposición más próxima.","Observación espacial":("Colindante; evaluar a 3,5 m del deslinde." if r["Condición"]=="Colindante" else f"No colindante; distancia al predio {r['Dist. al predio [m]']} m.")}
        for r in RECEPTORS
    ]
    scenarios=[{"Frente":f,"NPSeq total @10 m [dB(A)]":nps,"LWA equivalente aprox. [dB(A)]":lwa,"Receptor objetivo":receptor,"Proyecto Noise Map":project} for f,nps,lwa,receptor,project in FRONTS]
    return {
        "version":"c4l2_teacher_reference_v1","report_meta":{"author":"Pauta docente · solución desarrollada"},
        "reference":{"period":"Diurno","limit_db":65.0,"standard":"Referencia normativa del laboratorio"},
        "maps":{},
        "stage_1":{"vertices":VERTICES,"parts":PARTS,"phases":PHASES,"machinery":MACHINERY,"chronology":CHRONOLOGY},
        "stage_2":{"receptors":RECEPTORS,"relevance":relevance},
        "stage_3":{"sources":_source_table(),"bs_assignments":[{"Maquinaria":r["Maquinaria"],"Frente":r["Frente"],"Referencia BS / consultor":r["Referencia"]} for r in _source_table()]},
        "stage_4":{"scenarios":scenarios,"front_configs":[
            {"Parámetro":"Método","Valor":"ISO 9613"},{"Parámetro":"Temperatura","Valor":"10 °C"},
            {"Parámetro":"Humedad relativa","Valor":"70 %"},{"Parámetro":"Viento","Valor":"1–5 m/s, ±45° hacia el receptor"},
            {"Parámetro":"Reflexiones","Valor":"Orden 1"},{"Parámetro":"Condición","Valor":"Una unidad de cada tipo operando simultáneamente"},
        ],"results":_original_rows()},
        "stage_5":{"results":_original_rows(),"critical":{"Frente":"Escenario 3","Receptor":"RIMIV05 / RIMIV06","LAeq":78,"Excedencia":13},
            "spatial_note":"La condición global más desfavorable corresponde al Escenario 3 en RIMIV05 y RIMIV06, con 78 dB(A). Entre R01–R09, el máximo es 72 dB(A) en R02 y R06 durante el Escenario 2.",
            "spectral_note":"El expediente publica espectros de las fuentes y niveles globales en receptores, pero no espectros de recepción. Esos espectros deben obtenerse del modelo del alumno y verificarse por consistencia energética."},
        "stage_6":{"design":CONTROL_DESIGN,"configurations":[{"Frente":r["Frente / condición"],"Medida":r["Medida seleccionada"],"Configuración":r["Especificación"]} for r in CONTROL_DESIGN],
            "tl_calculator":_tl_panel(),"treatment_study":{"Tipo":"Encierro completo de referencia","Geometría":"4,0 × 3,0 × 3,0 m","Superficies":"Panel doble OSB 18 mm; cavidad absorbente; uniones selladas","Ventilación":"Entrada y descarga silenciadas"},
            "treatment_results":[{"Indicador":"TL del panel","Resultado":"Espectro calculado mediante ley de masa educativa"},{"Indicador":"Criterio de diseño","Resultado":"Aberturas y ventilación se incluyen en el balance; el TL no se resta directamente al receptor"}]},
        "stage_7":{"controlled_results":controlled,"comparison":comparisons,
            "comparability":{"Fuentes":"Iguales","Geometría":"Igual","Receptores":"Iguales","Configuración":"Igual","Cambio":"Solo medidas de control"},
            "project_names":{r["Frente / condición"]:r["Proyecto controlado"] for r in CONTROL_DESIGN},
            "effectiveness":"La solución de referencia reduce todos los máximos a 64 dB(A) o menos. La mayor reducción se obtiene en los receptores IMIV, donde el encierro con ventilación silenciada controla la trayectoria dominante.",
            "differences":"La reducción final no coincide necesariamente con el TL del panel: intervienen aberturas, orientación, difracción, contribución simultánea de otras fuentes y propagación."},
        "stage_8":{"final_strategy":final,
            "conclusion":"La condición original presenta excedencias de hasta 13 dB. La estrategia definitiva combina controles de trayectoria y de fuente según la geometría de cada frente. En la pauta modelada, todos los receptores quedan bajo la referencia diurna de 65 dB(A).",
            "implementation":"Implementar primero los controles en los frentes críticos, verificar sellos y continuidad, orientar las aberturas al interior del predio y mantener accesos desmontables. Inspeccionar paneles, uniones, absorbentes y silenciadores antes de cada cambio de frente.",
            "limitations":"Los resultados son predictivos y dependen de la geometría, potencias, simultaneidad y configuración ingresadas. El espectro recibido debe obtenerse en Noise Map Lab. La modelación no reemplaza una verificación normativa mediante medición.",
            "verification":"Repetir el cálculo con igual malla y receptores; comprobar visualmente la interrupción F–R y la orientación de aberturas; revisar reducción por bandas; inspeccionar en terreno dimensiones y sellos; contrastar luego mediante mediciones representativas.",
            "checks":{"Trazabilidad":"Cumple","Especificación":"Cumple","Viabilidad":"Cumple","Resultados":"Cumple"}},
    }
