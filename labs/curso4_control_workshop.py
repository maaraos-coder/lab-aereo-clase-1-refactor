"""Ejemplos y diseñador de tratamientos de la Etapa 6."""
import json
import math
from copy import deepcopy
from pathlib import Path
from labs import curso4_control_models as model

KINDS={'Reducción directa':'direct','Silenciador':'silencer','Encierro completo':'enclosure','Semiencierro':'semi','Encierro + silenciador':'enclosure_silencer'}
LININGS={'Sin revestimiento':'unlined','Absorción baja':'low','Absorción media':'medium','Absorción alta':'high','Personalizada':'custom'}
STATES={'Cerrada':'closed','Abierta':'open','Parcial':'partial'}


def _table(st,pd,rows):
    st.dataframe(pd.DataFrame(rows).round(2),hide_index=True,use_container_width=True)


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


def render_designer(st,pd,prefix,initial=None,fixed_kind=None):
    initial=deepcopy(initial or model.default_treatment())
    labels=list(KINDS)
    if fixed_kind:
        initial['noise_control_type']=fixed_kind
    default=next((k for k,v in KINDS.items() if v==initial.get('noise_control_type')),labels[2])
    label=st.selectbox('Tipo de tratamiento',labels,index=labels.index(default),disabled=fixed_kind is not None,key=prefix+'_kind')
    kind=KINDS[label]
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
            st.markdown('**Seis caras independientes, igual que en Noise Map Lab.**')
            for name,face_label in model.FACE_LABELS.items():
                face=deepcopy(cfg['enclosure_faces'][name])
                with st.expander(face_label,expanded=name=='front'):
                    a,b,c,d=st.columns(4)
                    state=a.selectbox('Estado',list(STATES),index=list(STATES.values()).index(face.get('state','closed')),key=prefix+'_'+name+'_state')
                    face['state']=STATES[state]
                    fraction=b.number_input('% abierta',min_value=0.,max_value=100.,value=float(face.get('opening_pct',25)),disabled=face['state']!='partial',key=prefix+'_'+name+'_opening')
                    face['opening_pct']=100. if face['state']=='open' else fraction if face['state']=='partial' else 0.
                    acoustic=c.selectbox('Caracterización',['Rw único','TL por bandas'],index=1 if face.get('acoustic_mode')=='spectrum' else 0,disabled=face['state']=='open',key=prefix+'_'+name+'_mode')
                    face['acoustic_mode']='spectrum' if acoustic=='TL por bandas' else 'rw'
                    face['rw_db']=d.number_input('Rw [dB]',min_value=0.,max_value=100.,value=float(face.get('rw_db',30)),disabled=face['state']=='open' or face['acoustic_mode']=='spectrum',key=prefix+'_'+name+'_rw')
                    if face['acoustic_mode']=='spectrum' and face['state']!='open':
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
    st.caption('Datos docentes ilustrativos. La selección de medidas para Eyzaguirre queda a cargo del alumno.')
    examples=[
        ('Barrera acústica perimetral','Excavadora junto al deslinde: pantalla continua de 3 m de alto y 20 m de largo, a 5 m de F; R a 20 m. No se desplaza el frente de trabajo.','barrera',None),
        ('Barrera trasladable IMIV','Cango en vía pública: pantalla de 2,5 m × 6 m, a 2 m de F; R a 10 m. Verifica extremos libres y estabilidad.','barrera',None),
        ('Reducción directa','Equipo fijo: reducción técnica acreditada de 8 dB por banda.','reduccion_directa_mesa_vibratoria','direct'),
        ('Silenciador','Descarga canalizada de un equipo: IL = 3, 6, 10, 15, 20, 22, 20, 16 dB entre 63 y 8000 Hz.','silenciador','silencer'),
        ('Encierro completo','Equipo fijo que admite encapsulado: 2 × 2 × 2,5 m; seis caras cerradas, Rw 30 dB y absorción media.','encierro','enclosure'),
        ('Semiencierro','Puesto fijo de corte: mismo volumen, fondo abierto y orientado al lado opuesto al receptor; compara R al frente y detrás.','semiencierro','semi'),
        ('Encierro + silenciador','Equipo fijo con ventilación: mismo encierro, conducto de 0,10 m² en el fondo y espectro IL del silenciador.','encierro_silenciador','enclosure_silencer'),
        ('Cierre de vanos','Trabajo interior: cara frontal con 25% abierto → cara cerrada, Rw 30 dB; compara el mismo receptor.','encierro',None),
        ('Secuencialidad operacional','Cuatro máquinas idénticas de 70 dB(A) cada una en R → una máquina simultánea. Mantén la tarea y justifica la programación.','',None),
        ('Reemplazo / restricción de maquinaria','Equipo original LwA=105 dB(A) → reemplazo LwA=97 dB(A). Su reducción propia es 8 dB; revisa el aporte de las otras fuentes.','reduccion_directa_mesa_vibratoria',None),
    ]
    for title,description,image,kind in examples:
        with st.expander(title,expanded=False):
            st.markdown(description)
            asset=Path(__file__).resolve().parents[1]/'assets'/'controles'/(image+'.png')
            if image and asset.exists(): st.image(str(asset),width=420)
            if title.startswith('Barrera'):
                if 'IMIV' in title: rows,before,after,los,delta=model.barrier_results(2.5,6.,2.,10.)
                else: rows,before,after,los,delta=model.barrier_results()
                st.markdown(f'Visual F–R en la pantalla: **{los:.2f} m**. Diferencia de recorrido sobre el borde: **{delta:.3f} m**.')
                _metrics(st,before,after); _table(st,pd,rows)
                st.caption('Mismo cálculo de pantalla finita de Noise Map Lab: borde superior, ambos extremos y transición cerca de extremos; G=0, límite de atenuación 20 dB. Abar no es el TL del panel.')
            elif kind:
                cfg=model.default_treatment(kind)
                rows,before,after=model.treatment_results(cfg)
                _metrics(st,before,after); _table(st,pd,rows)
                if kind=='semi':
                    _,_,back=model.treatment_results(cfg,bearing=180.)
                    st.markdown(f'Receptor al lado de la cara abierta: **{back:.1f} dB(A)**. La orientación modifica el resultado.')
            elif title=='Cierre de vanos':
                opened=model.default_treatment(); opened['enclosure_faces']['front'].update(state='partial',opening_pct=25.)
                closed=model.default_treatment()
                _,_,before=model.treatment_results(opened); _,_,after=model.treatment_results(closed)
                a,b,c=st.columns(3); a.metric('Vano abierto [dB(A)]',f'{before:.1f}'); b.metric('Vano cerrado [dB(A)]',f'{after:.1f}'); c.metric('Reducción [dB]',f'{before-after:.1f}')
                st.caption('Esta comparación modifica una superficie de una envolvente; conserva la geometría y absorción interior.')
            elif title=='Secuencialidad operacional':
                st.latex(r'L_{antes}=70+10\log_{10}(4)=76.02\ dB(A),\quad L_{despues}=70\ dB(A),\quad\Delta=6.02\ dB')
                st.caption('Para máquinas distintas suma sus contribuciones energéticamente. Cambiar el horario, por sí solo, no reduce la emisión instantánea.')
            else:
                st.latex(r'\Delta L_w=105-97=8\ dB')
                st.caption('La reducción de la fuente no equivale a restar 8 dB al total de varias fuentes en el receptor.')
    st.info('Los ejemplos de tratamientos usan terreno plano y campo libre. Los renders ilustran la construcción; los datos numéricos de cada ejemplo se indican en su texto.')


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
