"""Ejemplos y diseñador de tratamientos de la Etapa 6."""
import json
import math
from copy import deepcopy
from pathlib import Path
from labs import curso4_control_models as model

KINDS={'Reducción directa':'direct','Silenciador':'silencer','Encierro completo':'enclosure','Semiencierro':'semi','Encierro + silenciador':'enclosure_silencer'}
LININGS={'Sin revestimiento':'unlined','Absorción baja':'low','Absorción media':'medium','Absorción alta':'high','Personalizada':'custom'}
STATES={'Cerrada':'closed','Abierta':'open','Parcial':'partial'}
FACE_ICONS={'front':'⬆','back':'⬇','left':'⬅','right':'➡','roof':'▱','floor':'▰'}
TREATMENT_META={
    'direct':('◉','Reducción en la fuente','Aplica una reducción respaldada al nivel de potencia de la fuente.'),
    'silencer':('▰','Silenciador','Define la pérdida por inserción del elemento por bandas de octava.'),
    'enclosure':('▣','Encierro completo','Configura las seis superficies, el revestimiento interior y la orientación.'),
    'semi':('◩','Semiencierro','Mantiene una o más caras abiertas o parciales y considera su orientación.'),
    'enclosure_silencer':('▣◖','Encierro + silenciador','Combina las superficies del encierro con una ventilación silenciada.'),
}
MATERIALS={
    'OSB':{'density':650.0,'thickness':18.0,'note':'Tablero estructural de virutas orientadas'},
    'Terciado estructural':{'density':550.0,'thickness':15.0,'note':'Tablero contrachapado de madera'},
    'MDF':{'density':750.0,'thickness':15.0,'note':'Tablero de fibra de densidad media'},
    'Yeso-cartón':{'density':800.0,'thickness':12.5,'note':'Placa estándar; usar ficha real si se conoce'},
    'Fibrocemento':{'density':1350.0,'thickness':8.0,'note':'Placa cementicia genérica'},
    'Acero':{'density':7850.0,'thickness':1.0,'note':'Plancha continua de acero'},
    'Personalizado':{'density':700.0,'thickness':10.0,'note':'Ingresa densidad y espesor del producto'},
}


def _table(st,pd,rows):
    st.dataframe(pd.DataFrame(rows).round(2),hide_index=True,use_container_width=True)


def _designer_styles(st):
    st.markdown("""
    <style>
      .treatment-hero{border:1px solid #cfe0ea;border-radius:18px;padding:16px 18px;
        background:linear-gradient(135deg,#f8fcff 0%,#eef7fb 100%);margin:.25rem 0 .85rem}
      .treatment-hero-top{display:flex;align-items:center;gap:13px}
      .treatment-hero-icon{width:46px;height:46px;border-radius:14px;background:#0b7898;color:white;
        display:flex;align-items:center;justify-content:center;font-size:1.45rem;font-weight:900;
        box-shadow:0 7px 18px rgba(11,120,152,.20)}
      .treatment-hero small{display:block;color:#08789b;font-size:.67rem;font-weight:900;
        letter-spacing:.1em;text-transform:uppercase;margin-bottom:2px}
      .treatment-hero strong{display:block;color:#173b53;font-size:1.02rem}
      .treatment-hero p{color:#567181;line-height:1.5;margin:7px 0 0 59px;font-size:.88rem}
      .surface-intro{border-left:4px solid #0b7898;border-radius:12px;padding:11px 14px;
        background:#f3f8fb;color:#496777;margin:.15rem 0 .8rem}
      .surface-intro strong{color:#173b53}
      .face-summary{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:7px;margin:.2rem 0 1rem}
      .face-chip{border:1px solid #d7e4eb;border-radius:12px;padding:9px 7px;background:white;text-align:center;
        box-shadow:0 2px 8px rgba(31,61,78,.05)}
      .face-chip b{display:block;color:#173b53;font-size:.76rem;margin-bottom:3px}
      .face-chip span{font-size:.67rem;color:#6b8290}
      .face-chip.open{border-color:#f0bd7b;background:#fff8ed}.face-chip.partial{border-color:#87d2ca;background:#f0fbf9}
      .stTabs [data-baseweb="tab-list"]{gap:7px;background:#eef4f7;padding:5px;border-radius:13px}
      .stTabs [data-baseweb="tab"]{border-radius:9px;padding:8px 14px;height:auto;color:#496777}
      .stTabs [aria-selected="true"]{background:white;color:#08789b!important;
        box-shadow:0 2px 8px rgba(30,67,87,.12)}
      div[data-testid="stExpander"]{border:1px solid #d5e2e9!important;border-radius:14px!important;
        background:#fff!important;overflow:hidden;box-shadow:0 3px 12px rgba(31,61,78,.05);margin:.48rem 0}
      div[data-testid="stExpander"] details>summary{background:linear-gradient(90deg,#f7fafc,#fff);padding:.15rem .35rem}
      div[data-testid="stExpander"] details[open]>summary{border-bottom:1px solid #e1eaf0;background:#f1f8fb}
      div[data-testid="stVerticalBlockBorderWrapper"]{border-radius:16px!important;border-color:#d7e4eb!important}
      @media(max-width:900px){.face-summary{grid-template-columns:repeat(3,minmax(0,1fr))}}
    </style>
    """,unsafe_allow_html=True)


def _metrics(st,before,after):
    a,b,c=st.columns(3)
    a.metric('LAeq original · ejemplo [dB(A)]',f'{before:.1f}')
    b.metric('LAeq controlado · ejemplo [dB(A)]','Sin emisión hacia R' if after is None else f'{after:.1f}')
    c.metric('Reducción en R · ejemplo [dB]','—' if after is None else f'{before-after:.1f}')


def _spectrum(st,pd,key,label,values,maximum=100.0):
    st.caption(label)
    result={}
    for row in range(2):
        cols=st.columns(4)
        for i,f in enumerate(model.OCTAVE_BANDS[row*4:row*4+4]):
            result[str(f)]=cols[i].number_input(f'{f} Hz',min_value=0.0,max_value=float(maximum),value=float(values.get(str(f),0)),step=0.5,key=f'{key}_{f}')
    return result


def render_tl_calculator(st,pd,prefix,initial=None):
    """Educational single-leaf mass-law calculator feeding the map TL spectrum."""
    initial=dict(initial or {})
    st.markdown('### 3 · Calculadora de TL para diseñar el encierro')
    st.markdown(
        'Selecciona el material y construye el panel que utilizarás en las caras del encierro. '
        'La calculadora obtiene la **masa superficial** y un **TL estimado por bandas** que luego puedes aplicar directamente en el diseñador de Noise Map Lab.'
    )
    st.dataframe(pd.DataFrame([
        {'Material':name,'Densidad nominal [kg/m³]':data['density'],'Espesor inicial [mm]':data['thickness'],'Referencia de uso':data['note']}
        for name,data in MATERIALS.items() if name!='Personalizado'
    ]),hide_index=True,use_container_width=True)

    material_names=list(MATERIALS)
    material=st.selectbox(
        'Material del panel',material_names,
        index=material_names.index(initial.get('material','OSB')) if initial.get('material','OSB') in material_names else 0,
        key=prefix+'_material',
    )
    preset=MATERIALS[material]
    a,b,c=st.columns(3)
    density=a.number_input(
        'Densidad [kg/m³]',min_value=50.0,max_value=10000.0,
        value=float(initial.get('density',preset['density'])) if initial.get('material')==material else preset['density'],
        step=10.0,key=prefix+'_'+material+'_density',
    )
    thickness=b.number_input(
        'Espesor por capa [mm]',min_value=.1,max_value=100.0,
        value=float(initial.get('thickness_mm',preset['thickness'])) if initial.get('material')==material else preset['thickness'],
        step=.5,key=prefix+'_'+material+'_thickness',
    )
    layers=c.number_input(
        'Número de capas unidas',min_value=1,max_value=10,
        value=int(initial.get('layers',1)) if initial.get('material')==material else 1,
        step=1,key=prefix+'_'+material+'_layers',
    )
    d,e=st.columns(2)
    panel_width=d.number_input('Ancho del panel [m]',min_value=.1,max_value=20.0,value=float(initial.get('panel_width_m',1.22)),step=.01,key=prefix+'_width')
    panel_height=e.number_input('Alto del panel [m]',min_value=.1,max_value=20.0,value=float(initial.get('panel_height_m',2.44)),step=.01,key=prefix+'_height')

    surface_mass,tl=model.mass_law_tl_spectrum(density,thickness,layers)
    panel_area=panel_width*panel_height
    panel_weight=surface_mass*panel_area
    m1,m2,m3=st.columns(3)
    m1.metric('Masa superficial',f'{surface_mass:.1f} kg/m²')
    m2.metric('Superficie del panel',f'{panel_area:.2f} m²')
    m3.metric('Peso estimado del panel',f'{panel_weight:.1f} kg')
    st.latex(r'm_s=\rho\,e\,n')
    st.latex(r'TL(f)\approx20\log_{10}(m_s f)-47')
    st.dataframe(pd.DataFrame([
        {'Banda [Hz]':f,'TL estimado [dB]':round(tl[str(f)],1)} for f in model.OCTAVE_BANDS
    ]),hide_index=True,use_container_width=True)
    if surface_mass<10:
        st.warning('La masa superficial es inferior a 10 kg/m². Revisa además que el panel sea continuo, sin ranuras y estructuralmente apto para funcionar como cerramiento acústico.')
    st.warning(
        'Resultado orientativo mediante ley de masa para una hoja simple, homogénea y estanca. No representa resonancia, frecuencia crítica, juntas, puertas, transmisión estructural ni una cámara entre placas. '
        'Si existe un ensayo o ficha certificada del sistema completo, usa ese espectro TL en vez de esta estimación.'
    )
    config={'material':material,'density':density,'thickness_mm':thickness,'layers':layers,
            'panel_width_m':panel_width,'panel_height_m':panel_height,'surface_mass_kgm2':surface_mass,
            'panel_weight_kg':panel_weight,'tl_db':tl}
    return config,tl


def _geometry_plot(st,config,key):
    import plotly.graph_objects as go
    l=config['enclosure_length_m']; w=config['enclosure_width_m']; h=config['enclosure_height_m']
    faces={'front':[(0,l,0),(w,l,0),(w,l,h),(0,l,h)],'back':[(0,0,0),(w,0,0),(w,0,h),(0,0,h)],
           'left':[(0,0,0),(0,l,0),(0,l,h),(0,0,h)],'right':[(w,0,0),(w,l,0),(w,l,h),(w,0,h)],
           'roof':[(0,0,h),(w,0,h),(w,l,h),(0,l,h)],'floor':[(0,0,0),(w,0,0),(w,l,0),(0,l,0)]}
    fig=go.Figure()
    colors={'closed':'#176b9b','open':'#f1a24a','partial':'#31a49a'}
    for name,points in faces.items():
        state=config['enclosure_faces'][name]['state']; xs,ys,zs=zip(*points)
        label=model.FACE_LABELS[name]+' · '+next(k for k,v in STATES.items() if v==state)
        if state!='open':
            fig.add_trace(go.Mesh3d(x=xs,y=ys,z=zs,i=[0,0],j=[1,2],k=[2,3],color=colors[state],opacity=.22,name=label,showlegend=True))
        closed=points+[points[0]]; x,y,z=zip(*closed)
        fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode='lines',line=dict(color=colors[state],width=5,dash='dash' if state=='open' else 'solid'),name=label,showlegend=state=='open'))
    fig.add_trace(go.Scatter3d(x=[w/2],y=[l/2],z=[min(1.5,h/2)],mode='markers+text',text=['F'],marker=dict(size=6,color='#de623d'),showlegend=False))
    fig.update_layout(height=340,margin=dict(l=0,r=0,t=15,b=0),scene=dict(xaxis_title='Ancho [m]',yaxis_title='Largo [m]',zaxis_title='Altura [m]',aspectmode='data'),legend=dict(font=dict(size=10)))
    st.plotly_chart(fig,use_container_width=True,key=key)
    st.caption(f'Frente = azimut {config["enclosure_azimuth_deg"]:.0f}° desde el norte; fondo = lado opuesto. Naranja indica una cara abierta. La rotación se aplica en el cálculo; la vista muestra los ejes locales.')


def render_designer(st,pd,prefix,initial=None,fixed_kind=None,suggested_tl=None):
    _designer_styles(st)
    initial=deepcopy(initial or model.default_treatment())
    labels=list(KINDS)
    if fixed_kind:
        initial['noise_control_type']=fixed_kind
    default=next((k for k,v in KINDS.items() if v==initial.get('noise_control_type')),labels[2])
    label=st.selectbox('Tipo de tratamiento',labels,index=labels.index(default),disabled=fixed_kind is not None,key=prefix+'_kind')
    kind=KINDS[label]
    icon,short_title,short_copy=TREATMENT_META[kind]
    st.markdown(f"""
    <div class="treatment-hero">
      <div class="treatment-hero-top">
        <div class="treatment-hero-icon">{icon}</div>
        <div><small>Tratamiento seleccionado</small><strong>{short_title}</strong></div>
      </div>
      <p>{short_copy}</p>
    </div>
    """,unsafe_allow_html=True)
    prefix=prefix+'_'+kind
    cfg=deepcopy(initial)
    cfg['noise_control_type']=kind
    # The map initially opens a face when switching to a semi-enclosure.
    if kind=='semi' and not any(f.get('state') in ('open','partial') for f in cfg['enclosure_faces'].values()):
        cfg['enclosure_faces']['back']['state']='open'
    enclosed=kind in ('enclosure','semi','enclosure_silencer')
    tabs=st.tabs(['Geometría','Superficies (TL / Rw)','Resultados y cálculo']) if enclosed else st.tabs(['Reducción por bandas','Resultados y cálculo'])
    with tabs[0]:
        if enclosed:
            a,b,c,d=st.columns(4)
            for col,field,label_,fallback in [(a,'enclosure_length_m','Largo [m]',2.),(b,'enclosure_width_m','Ancho [m]',2.),(c,'enclosure_height_m','Alto [m]',2.5)]:
                cfg[field]=col.number_input(label_,min_value=.1,max_value=1000.,value=float(cfg.get(field,fallback)),step=.1,key=prefix+'_'+field)
            cfg['enclosure_azimuth_deg']=d.number_input('Azimut del frente [°]',min_value=0.,max_value=359.9,value=float(cfg.get('enclosure_azimuth_deg',0)),step=1.,key=prefix+'_azimuth')
            lining=st.selectbox('Revestimiento absorbente interior',list(LININGS),index=list(LININGS.values()).index(cfg.get('enclosure_lining_mode','medium')),key=prefix+'_lining')
            cfg['enclosure_lining_mode']=LININGS[lining]
            if LININGS[lining]=='custom':
                coeff={}
                cols=st.columns(4)
                for i,f in enumerate(model.OCTAVE_BANDS):
                    coeff[str(f)]=cols[i%4].number_input(f'α · {f} Hz',min_value=0.,max_value=.99,value=float(cfg.get('enclosure_absorption_coeff',{}).get(str(f),.05)),step=.01,key=f'{prefix}_alpha_{f}')
                cfg['enclosure_absorption_coeff']=coeff
            else:
                cfg['enclosure_absorption_coeff']=dict(model.ENCLOSURE_ABSORPTION_PRESETS[LININGS[lining]])
                _table(st,pd,[{'Hz':f,'α interior':cfg['enclosure_absorption_coeff'][str(f)]} for f in model.OCTAVE_BANDS])
            st.caption('Los perfiles de absorción son valores docentes genéricos, iguales a los de Noise Map Lab. Para un material real, ingresa sus datos por bandas.')
        else:
            field='silencer_il_db' if kind=='silencer' else 'control_reduction_db'
            cfg[field]=_spectrum(st,pd,prefix+'_simple','IL del silenciador [dB]' if kind=='silencer' else 'Reducción directa ΔLw [dB]',cfg.get(field,model.DEFAULT_IL),80.)
            st.latex(r'L_{w,controlado}(f)=L_{w,original}(f)-IL(f)' if kind=='silencer' else r'L_{w,controlado}(f)=L_{w,original}(f)-\Delta L_w(f)')
            st.caption('La reducción directa debe provenir de datos técnicos o mediciones. El silenciador se aplica a una emisión canalizada compatible con el equipo.')
    if enclosed:
        with tabs[1]:
            st.markdown('''
            <div class="surface-intro">
              <strong>Seis superficies independientes</strong><br>
              Cada cara puede ser cerrada, abierta o parcial y tener su propio Rw o espectro TL.
            </div>
            ''',unsafe_allow_html=True)
            face_chips=[]
            for face_name,face_title in model.FACE_LABELS.items():
                preview=cfg['enclosure_faces'][face_name]
                state_value=preview.get('state','closed')
                state_text=next((title for title,value in STATES.items() if value==state_value),'Cerrada')
                acoustic_text='Abierta' if state_value=='open' else ('TL bandas' if preview.get('acoustic_mode')=='spectrum' else f"Rw {float(preview.get('rw_db') or 0):.0f} dB")
                face_chips.append(
                    f'<div class="face-chip {state_value}"><b>{FACE_ICONS[face_name]} {face_title}</b><span>{state_text} · {acoustic_text}</span></div>'
                )
            st.markdown('<div class="face-summary">'+''.join(face_chips)+'</div>',unsafe_allow_html=True)
            for name,face_label in model.FACE_LABELS.items():
                face=deepcopy(cfg['enclosure_faces'][name])
                state_preview=next((title for title,value in STATES.items() if value==face.get('state','closed')),'Cerrada')
                mode_preview='Abierta' if face.get('state')=='open' else ('TL por bandas' if face.get('acoustic_mode')=='spectrum' else f"Rw {float(face.get('rw_db') or 0):.0f} dB")
                with st.expander(f"{FACE_ICONS[name]}  {face_label}   ·   {state_preview}   ·   {mode_preview}",expanded=name=='front'):
                    st.caption(f'Configura la superficie **{face_label.lower()}** del cerramiento.')
                    a,b,c,d=st.columns(4)
                    state=a.selectbox('Estado',list(STATES),index=list(STATES.values()).index(face.get('state','closed')),key=prefix+'_'+name+'_state')
                    face['state']=STATES[state]
                    fraction=b.number_input('% abierta',min_value=0.,max_value=100.,value=float(face.get('opening_pct',25)),disabled=face['state']!='partial',key=prefix+'_'+name+'_opening')
                    face['opening_pct']=100. if face['state']=='open' else fraction if face['state']=='partial' else 0.
                    acoustic=c.selectbox('Caracterización',['Rw único','TL por bandas'],index=1 if face.get('acoustic_mode')=='spectrum' else 0,disabled=face['state']=='open',key=prefix+'_'+name+'_mode')
                    face['acoustic_mode']='spectrum' if acoustic=='TL por bandas' else 'rw'
                    face['rw_db']=d.number_input('Rw [dB]',min_value=0.,max_value=100.,value=float(face.get('rw_db',30)),disabled=face['state']=='open' or face['acoustic_mode']=='spectrum',key=prefix+'_'+name+'_rw')
                    if face['acoustic_mode']=='spectrum' and face['state']!='open':
                        use_calculated=bool(suggested_tl) and st.checkbox(
                            'Usar TL de la calculadora',
                            value=bool(face.get('use_calculated_tl',False)),
                            key=prefix+'_'+name+'_use_calculated_tl',
                        )
                        face['use_calculated_tl']=use_calculated
                        if use_calculated:
                            face['tl_db']={str(f):float(suggested_tl[str(f)]) for f in model.OCTAVE_BANDS}
                            _table(st,pd,[{'Hz':f,'TL aplicado desde calculadora [dB]':face['tl_db'][str(f)]} for f in model.OCTAVE_BANDS])
                        else:
                            face['tl_db']=_spectrum(st,pd,prefix+'_'+name+'_tl','TL del panel por bandas [dB]',face.get('tl_db',model.DEFAULT_TL))
                    else:
                        _table(st,pd,[{'Hz':f,'TL panel estimado [dB]':model._rw_estimated_tl_db(face['rw_db'],f),'% abierta efectivo':face['opening_pct']} for f in model.OCTAVE_BANDS])
                cfg['enclosure_faces'][name]=face
            st.caption('Rw único genera el mismo espectro estimado que Noise Map Lab: offsets −25, −16, −7, 0, +3, +4, +4, +4 dB. Un espectro certificado tiene prioridad. La cara abierta transmite directamente; su TL no atenúa la abertura.')
            if kind=='enclosure_silencer':
                a,b=st.columns(2)
                cfg['enclosure_vent_area_m2']=a.number_input('Área de ventilación con silenciador [m²]',min_value=0.,max_value=1000.,value=float(cfg.get('enclosure_vent_area_m2',.1)),step=.01,key=prefix+'_vent_area')
                names=list(model.FACE_LABELS)
                cfg['enclosure_vent_face']=b.selectbox('Cara del conducto',names,index=names.index(cfg.get('enclosure_vent_face','back')),format_func=model.FACE_LABELS.get,key=prefix+'_vent_face')
                cfg['silencer_il_db']=_spectrum(st,pd,prefix+'_vent_il','IL del silenciador por bandas [dB]',cfg.get('silencer_il_db',model.DEFAULT_IL),80.)
                src=model.SimpleNamespace(lat=0.,lon=0.,height_m=1.5,**cfg)
                area=model._enclosure_face_geometry(src)[cfg['enclosure_vent_face']]['area_m2']
                available=area*(1-model._face_open_fraction(cfg['enclosure_faces'][cfg['enclosure_vent_face']]))
                if cfg['enclosure_vent_area_m2']>available:
                    st.warning(f'El área solicitada supera el panel disponible ({available:.2f} m²). El motor limita la ventilación a esa área; corrige la geometría o la cara seleccionada.')
            if kind=='semi' and not any(model._face_open_fraction(f)>0 for f in cfg['enclosure_faces'].values()):
                st.warning('Un semiencierro requiere al menos una cara abierta o parcial.')
            if kind=='enclosure' and any(model._face_open_fraction(f)>0 for f in cfg['enclosure_faces'].values()):
                st.info('Este encierro tiene aberturas. El motor las incluye como emisión directa en el balance energético.')
    # Draw only after all surface controls have been evaluated to avoid a stale rerun.
    if enclosed:
        with tabs[0]: _geometry_plot(st,cfg,prefix+'_geometry')
    with tabs[-1]:
        st.markdown('**Ejemplo exterior calculado: una fuente puntual, terreno plano, sin otros obstáculos.**')
        a,b,c=st.columns(3)
        distance=a.number_input('Distancia horizontal F–R [m]',min_value=5.,max_value=1000.,value=20.,step=1.,key=prefix+'_distance')
        bearing=b.number_input('Azimut del receptor desde F [°]',min_value=0.,max_value=359.9,value=0.,step=5.,key=prefix+'_bearing')
        height=c.number_input('Altura del receptor [m]',min_value=.1,max_value=100.,value=1.5,step=.1,key=prefix+'_rheight')
        if enclosed and distance<=max(cfg['enclosure_length_m'],cfg['enclosure_width_m']):
            st.warning('Sitúa el receptor en campo exterior: aumenta F–R respecto de las dimensiones del encierro.')
        with st.expander('Espectro Lw de la fuente del ejemplo',expanded=False):
            lw=_spectrum(st,pd,prefix+'_lw','Lw no ponderado por octavas [dB]',model.EXAMPLE_LW,150.)
        rows,before,after=model.treatment_results(cfg,lw,distance,bearing,height)
        _metrics(st,before,after); _table(st,pd,rows)
        if enclosed:
            st.latex(r'A_{perdidas}=\sum_i[S_{panel,i}\min(1,\alpha+\tau_i)+S_{abierta,i}+S_{vent,i}]')
            st.latex(r'T_i=S_{panel,i}\tau_i+S_{abierta,i}+S_{vent,i}10^{-IL/10},\quad L_{w,i}=L_w+10\log_{10}(T_i/A_{perdidas})')
            st.latex(r'Q_i(\theta)=4\cos\theta,\quad L_{p,R}=10\log_{10}\sum_{i\ visibles}10^{(L_{w,i}+10\log_{10}Q_i-A_{div,i})/10}')
            freq=st.selectbox('Banda para revisar el balance',list(model.OCTAVE_BANDS),index=3,key=prefix+'_balance_band')
            balance,_=model.enclosure_balance(cfg,freq); _table(st,pd,balance)
        st.caption('El cerramiento y su directividad usan las mismas funciones del motor. Este ejemplo exterior usa solo divergencia geométrica (G=0, sin absorción atmosférica, reflexiones ni edificios). La reducción de potencia emitida y ΔLp en R son magnitudes distintas. Calcula el escenario completo en Noise Map Lab.')
        st.download_button('Descargar parámetros del tratamiento (.json)',json.dumps(cfg,ensure_ascii=False,indent=2),file_name='parametros-tratamiento.json',mime='application/json',key=prefix+'_download')
        st.caption('Este archivo contiene parámetros para reproducir el tratamiento; no es un proyecto completo para cargar en el mapa.')
    return cfg,{'bands':rows,'original_dba':before,'controlled_dba':after,'receiver_distance_m':distance,'receiver_bearing_deg':bearing,'receiver_height_m':height,'source_lw_bands':lw}


def render_examples(st,pd):
    st.markdown('### 2 · Ejemplos resueltos de cada medida')
    st.caption('Medidas implementadas en Noise Map Lab. Datos docentes ilustrativos; el alumno diseña su solución para Eyzaguirre.')
    examples=[
        ('Barrera acústica','Excavadora junto al deslinde: pantalla continua de 3 m de alto y 20 m de largo, a 5 m de F; R a 20 m. El frente de trabajo conserva su ubicación.','barrera',None),
        ('Reducción directa','Equipo fijo: reducción técnica acreditada de 8 dB por banda.','reduccion_directa_mesa_vibratoria','direct'),
        ('Silenciador','Descarga canalizada de un equipo: IL = 3, 6, 10, 15, 20, 22, 20, 16 dB entre 63 y 8000 Hz.','silenciador','silencer'),
        ('Encierro completo','Equipo fijo que admite encapsulado: 2 × 2 × 2,5 m; seis caras cerradas, Rw 30 dB y absorción media.','encierro','enclosure'),
        ('Semiencierro','Puesto fijo de corte: mismo volumen, fondo abierto y orientado al lado opuesto al receptor; compara R al frente y detrás.','semiencierro','semi'),
        ('Encierro + silenciador','Equipo fijo con ventilación: mismo encierro, conducto de 0,10 m² en el fondo y espectro IL del silenciador.','encierro_silenciador','enclosure_silencer'),
    ]
    for number,(title,description,image,kind) in enumerate(examples,1):
        with st.container(border=True):
            st.markdown(f'#### {number} · {title}')
            visual,explanation=st.columns([1,2])
            with visual:
                asset=Path(__file__).resolve().parents[1]/'assets'/'controles'/(image+'.png')
                if asset.exists(): st.image(str(asset),use_container_width=True)
            with explanation:
                st.markdown(description)
                if kind is None:
                    rows,before,after,los,delta=model.barrier_results()
                    st.markdown(f'Visual F–R en la pantalla: **{los:.2f} m**. Diferencia de recorrido sobre el borde: **{delta:.3f} m**.')
                    st.caption('Pantalla finita: borde superior, ambos extremos y transición cerca de extremos; G=0, límite de atenuación 20 dB. Abar no es el TL del panel.')
                else:
                    cfg=model.default_treatment(kind)
                    rows,before,after=model.treatment_results(cfg)
                    if kind=='semi':
                        _,_,back=model.treatment_results(cfg,bearing=180.)
                        st.markdown(f'Receptor al lado de la cara abierta: **{back:.1f} dB(A)**. La orientación modifica el resultado.')
            _metrics(st,before,after)
            _table(st,pd,rows)
    st.info('Los ejemplos usan terreno plano y campo libre. Los renders ilustran la construcción; los datos numéricos de cada ejemplo se indican en su texto.')


def render_barrier_calculator(st,pd,prefix,initial=None):
    cfg=dict(initial or {})
    cols=st.columns(3)
    specs=[('altura_m','Altura de barrera [m]',3.,.1,20.),('longitud_m','Longitud [m]',20.,.1,500.),('distancia_fr_m','Distancia F–R [m]',20.,1.,1000.),('distancia_fb_m','Distancia F–barrera [m]',5.,.1,999.),('altura_fuente_m','Altura de F [m]',1.5,.1,100.),('altura_receptor_m','Altura de R [m]',1.5,.1,100.)]
    for i,(field,label,value,minimum,maximum) in enumerate(specs):
        cfg[field]=cols[i%3].number_input(label,min_value=minimum,max_value=maximum,value=float(cfg.get(field,value)),step=.1,key=prefix+'_'+field)
    if cfg['distancia_fb_m']>=cfg['distancia_fr_m']:
        st.warning('La pantalla debe ubicarse entre F y R.'); return cfg,None
    rows,before,after,los,delta=model.barrier_results(cfg['altura_m'],cfg['longitud_m'],cfg['distancia_fb_m'],cfg['distancia_fr_m'],cfg['altura_fuente_m'],cfg['altura_receptor_m'])
    if cfg['altura_m']<=los: st.warning('La barrera no corta la visual F–R: el cálculo de apantallamiento es 0 dB.')
    st.markdown(f'Altura de visual en B: **{los:.2f} m** · diferencia de recorrido sobre borde: **{delta:.3f} m**.')
    _metrics(st,before,after); _table(st,pd,rows)
    st.caption('Pantalla centrada y perpendicular a F–R, terreno plano, G=0, sin atmósfera ni reflexiones. Reproduce altura, longitud y posición en Noise Map Lab para evaluar el escenario real. El panel debe ser continuo y con aislamiento suficiente para el apantallamiento previsto.')
    return cfg,{'bands':rows,'original_dba':before,'controlled_dba':after}
