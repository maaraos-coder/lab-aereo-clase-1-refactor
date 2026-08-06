import base64
import datetime as dt
import json
import math
import mimetypes
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Laboratorio | Aislamiento a Ruido Aéreo", page_icon="🔊", layout="wide")
ROOT = Path(__file__).parent
FREQS = np.array([100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150])
ACTIVITY_DB = ROOT / "formative_responses.sqlite3"
APPLICATION_POINTS = {
    3: {"s3q1": 2, "s3q2": 2, "s3q3": 2, "s3q4": 2, "s3q5": 2},
    5: {"s5q1": 4, "s5q2": 3, "s5q3": 3},
    7: {"s7q1": 2, "s7q2": 2, "s7q3": 2, "s7q4": 2, "s7q5": 2,
        "s7q6": 2, "s7q7": 2, "s7q8": 2, "s7q9": 1, "s7q10": 1, "s7q11": 2},
    9: {"e9_pairs": 20},
    10: {"final_exam": 100},
}
APPLICATION_TOTAL = sum(sum(stage.values()) for stage in APPLICATION_POINTS.values())

st.markdown("""
<style>
:root{--navy:#07172b;--blue:#0967d2;--cyan:#17c3e6;--ink:#14243a;--muted:#60718a;--line:#dce6f2;--soft:#f3f8fd;--green:#0f9d78;--orange:#ef8b2c}
.stApp{background:#f5f8fc;color:var(--ink)} .block-container{padding-top:1.2rem;max-width:1280px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#06172b,#0a2b4d);color:white}
[data-testid="stSidebar"] *{color:white}.hero{background:linear-gradient(125deg,#07172b,#075da9 70%,#11a8cc);
color:white;border-radius:24px;padding:2rem 2.2rem;margin:.4rem 0 1.2rem;box-shadow:0 18px 42px #14395a25}
.hero h1{font-size:2.35rem;margin:.2rem 0}.hero p{max-width:850px;font-size:1.05rem}.tag{font-size:.73rem;font-weight:900;letter-spacing:.13em;color:#8ee9ff}
.time-badge{display:inline-flex;align-items:center;gap:.42rem;margin-top:.55rem;padding:.42rem .78rem;border-radius:999px;
background:#ffffff1c;border:1px solid #8ee9ff88;color:#fff;font-size:.83rem;font-weight:900}
.class-clock{background:linear-gradient(135deg,#072b4d,#0967a8);color:#fff;border-radius:18px;padding:1rem 1.2rem;
margin:.8rem 0 1rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;box-shadow:0 10px 25px #092d5320}
.class-clock strong{font-size:1.1rem}.class-clock span{color:#ccefff;font-size:.9rem}
.score-counter{background:linear-gradient(135deg,#092b50,#0878bd);color:#fff;border-radius:18px;padding:1rem 1.2rem;
margin:.8rem 0 1.1rem;display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:center;box-shadow:0 10px 26px #092d5325}
.score-counter b{font-size:1.05rem}.score-counter small{display:block;color:#ccefff;margin-top:.2rem}
.score-number{font-size:1.65rem;font-weight:950;white-space:nowrap}.score-track{height:8px;background:#ffffff2e;border-radius:999px;margin-top:.65rem;overflow:hidden}
.score-fill{height:100%;background:#65efbe;border-radius:999px}
[data-testid="stSidebar"] .sidebar-score{background:linear-gradient(135deg,#0b4f83,#0878bd);border:1px solid #5ed8f0;
padding:.85rem .9rem;grid-template-columns:minmax(0,1fr) auto;gap:.55rem}
[data-testid="stSidebar"] .sidebar-score b,[data-testid="stSidebar"] .sidebar-score .score-number{color:#fff!important}
[data-testid="stSidebar"] .sidebar-score small{color:#d9f5ff!important;font-size:.72rem;white-space:normal}
[data-testid="stSidebar"] .sidebar-score .score-number{font-size:1.25rem;text-align:right}
.route-time{display:inline-flex;margin-top:.45rem;padding:.25rem .58rem;border-radius:999px;background:#eaf7ff;
color:#0871bd;font-size:.75rem;font-weight:900}
.break-card{background:#fff8e9;border:1px solid #f2cf8d;border-radius:16px;padding:1rem;display:grid;
grid-template-columns:48px 1fr;gap:.8rem;align-items:center;box-shadow:0 7px 20px #5c43140c}
.break-card b{display:block;color:#704b08}.break-card p{margin:.15rem 0 0;color:#7d673d;font-size:.88rem}
.card,.lesson,.answer{background:white;border:1px solid var(--line);border-radius:17px;padding:1.1rem 1.25rem;
box-shadow:0 6px 18px #17324d0b;margin:.55rem 0}.lesson{border-left:5px solid var(--blue)}
.formula{background:linear-gradient(135deg,#06172b,#0a4f86);color:white;border-radius:18px;padding:1.35rem;
margin:1rem 0;text-align:center;font-size:1.28rem;box-shadow:0 12px 28px #06172b28;border:1px solid #39c8e633}
.good{background:#eaf9f4;border-left:5px solid var(--green);padding:1rem;border-radius:12px}.warn{background:#fff5e8;border-left:5px solid var(--orange);padding:1rem;border-radius:12px}
.step{display:inline-flex;width:34px;height:34px;border-radius:50%;background:var(--blue);color:white;align-items:center;justify-content:center;font-weight:900}
.stage-title{font-size:1.7rem;font-weight:900;color:#092342;margin:.3rem 0}.muted{color:var(--muted)}
.overview{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin:0 0 1.15rem}
.overview-card{background:white;border:1px solid var(--line);border-radius:18px;padding:1rem 1.1rem;min-height:128px;
box-shadow:0 8px 24px #17324d10;position:relative;overflow:hidden}
.overview-card:before{content:"";position:absolute;inset:0 auto 0 0;width:5px;background:linear-gradient(#0b69d1,#1fc6df)}
.overview-icon{font-size:1.45rem}.overview-title{font-size:.78rem;letter-spacing:.08em;font-weight:900;color:#0871bd;margin:.35rem 0}
.overview-text{font-size:.92rem;line-height:1.45;color:#40536b}
.route-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.8rem}
.route-card{background:#fff;color:#14243a;border:1px solid #d8e6f3;border-radius:16px;padding:1rem;display:grid;
grid-template-columns:48px 1fr;gap:.8rem;align-items:start;box-shadow:0 7px 20px #17324d0c}
.route-card b{display:block;color:#0a2d52;margin-bottom:.25rem}.route-card p{margin:0;color:#566b84;font-size:.88rem;line-height:1.4}
.route-card .step{width:42px;height:42px;background:linear-gradient(135deg,#0967d2,#17b9db)}
.question-box{background:linear-gradient(135deg,#eef7ff,#fff);border:2px solid #8ec7ef;border-radius:18px;padding:1.2rem 1.35rem;margin:1.1rem 0 .5rem}
.question-label{font-size:.76rem;letter-spacing:.12em;font-weight:900;color:#0871bd}.question-text{font-size:1.18rem;font-weight:850;color:#102b49;margin-top:.35rem}
.scene-pro{position:relative;min-height:300px;border-radius:22px;overflow:hidden;border:1px solid #bdd4e8;
background:linear-gradient(#dff3ff 0 61%,#d8dde2 61%);margin:1rem 0;box-shadow:0 12px 30px #17324d16}
.machine,.person,.barrier,.waves,.distance-label{position:absolute}.machine{left:8%;bottom:18%;font-size:4rem;z-index:3;transition:left .45s ease}
.machine-box{position:absolute;left:5%;bottom:13%;width:125px;height:125px;border:7px solid #ef8b2c;border-radius:12px;background:#ffedd9aa;z-index:2;transition:left .45s ease}
.mounts{position:absolute;left:8%;bottom:13%;font-size:1.5rem;letter-spacing:18px;z-index:4;transition:left .45s ease}
.person{right:9%;bottom:18%;font-size:4.2rem;z-index:3;transition:right .45s ease}.headphones{position:absolute;right:9%;bottom:32%;font-size:3rem;z-index:4;transition:right .45s ease}
.receiver-cabin{position:absolute;right:5%;bottom:12%;width:125px;height:145px;border:6px solid #1976b9;border-radius:12px;background:#dff3ff66;z-index:2;transition:right .45s ease}
.receiver-facade{position:absolute;right:3%;bottom:8%;width:155px;height:175px;background:#e9edf2;border:8px solid #657789;border-radius:5px;z-index:1;transition:right .45s ease}
.receiver-facade:before{content:"";position:absolute;left:20px;top:20px;width:92px;height:92px;background:linear-gradient(135deg,#bfe9ff,#effaff);border:9px double #176fa8;box-shadow:inset 0 0 0 2px #fff}
.receiver-facade:after{content:"FACHADA AISLANTE";position:absolute;left:12px;right:12px;bottom:9px;text-align:center;font-size:.63rem;font-weight:900;color:#32465a}
.scene-pro.distance-on .machine{left:3%}.scene-pro.distance-on .machine-box{left:1%}.scene-pro.distance-on .mounts{left:4%}
.scene-pro.distance-on .person{right:3%}.scene-pro.distance-on .headphones{right:3%}.scene-pro.distance-on .receiver-cabin{right:1%}.scene-pro.distance-on .receiver-facade{right:0}
.barrier{left:48%;bottom:13%;width:30px;height:155px;background:repeating-linear-gradient(90deg,#27394c,#27394c 8px,#50677c 8px,#50677c 14px);z-index:4}
.waves{left:24%;right:25%;top:38%;font-size:2rem;letter-spacing:.5rem;color:#0a80ce;white-space:nowrap;overflow:hidden}
.distance-label{left:36%;bottom:5%;font-size:.8rem;font-weight:800;color:#40536b}
.scene-caption{position:absolute;left:1rem;top:1rem;background:#07172be8;color:white;padding:.5rem .8rem;border-radius:10px;font-weight:800}
.section-band{display:flex;align-items:center;gap:.8rem;margin:1.45rem 0 .6rem}.section-band span{font-size:1.5rem}.section-band h3{margin:0;color:#0a2d52}
.matter-wrap{background:white;border:1px solid var(--line);border-radius:18px;padding:.3rem 1.25rem 1rem}
.matter-heading{display:flex;align-items:center;gap:.85rem;margin:1.35rem 0 .75rem}
.matter-heading-icon{display:flex;width:46px;height:46px;align-items:center;justify-content:center;border-radius:14px;
background:linear-gradient(135deg,#0967d2,#17b9db);color:white;font-size:1.35rem;box-shadow:0 8px 20px #0967d233}
.matter-heading h2{font-size:1.4rem;color:#092342;margin:0}.matter-heading p{margin:.12rem 0 0;color:var(--muted);font-size:.9rem}
.didactic-card-title{display:flex;gap:.55rem;align-items:center;color:#092d53;font-size:1.03rem;font-weight:900;
margin:0 0 .55rem}.didactic-card-title span{display:flex;width:29px;height:29px;border-radius:9px;align-items:center;
justify-content:center;background:#e7f4ff;font-size:.9rem}
.didactic-duration{display:inline-flex;align-items:center;gap:.4rem;background:#eaf9f4;color:#08765d;border:1px solid #bde9db;
border-radius:999px;padding:.36rem .7rem;font-size:.78rem;font-weight:850;margin-bottom:.7rem}
.didactic-note{background:linear-gradient(135deg,#eef7ff,#fff);border:1px solid #c7e0f3;border-radius:14px;
padding:.8rem .9rem;color:#334b64;font-size:.88rem;margin:.45rem 0}
.teacher-only{background:linear-gradient(135deg,#241548,#493285);color:white;border-radius:18px;padding:1rem 1.2rem;
margin:1.2rem 0 .6rem;box-shadow:0 10px 28px #25164a22;border:1px solid #9d87d755}
.teacher-only b{font-size:1.02rem}.teacher-only span{display:block;color:#ddd4f6;font-size:.86rem;margin-top:.22rem}
.st-key-academic_card{height:100%}
div[data-testid="stMetric"]{background:white;border:1px solid var(--line);padding:.7rem 1rem;border-radius:14px}
.scene{display:grid;grid-template-columns:1fr 80px 1fr;min-height:230px;border:1px solid #bcd0e4;border-radius:18px;overflow:hidden;background:white}
.room{display:flex;align-items:center;justify-content:center;font-size:3rem;position:relative;background:linear-gradient(#edf7ff,#fff)}
.wall{background:#25374a;display:flex;align-items:center;justify-content:center;color:white;font-size:.72rem;writing-mode:vertical-rl;font-weight:800}
.two-room-lab{display:grid;grid-template-columns:1fr 74px 1fr;min-height:330px;border:1px solid #b8cfe3;
border-radius:22px;overflow:hidden;background:white;box-shadow:0 12px 30px #17324d16;margin:1rem 0}
.lab-room{position:relative;overflow:hidden;background:linear-gradient(#eaf7ff 0 72%,#d9c8aa 72%);padding:1rem}
.lab-room.receiver{background:linear-gradient(#f1f8fc 0 72%,#d9c8aa 72%)}
.room-name{position:absolute;top:14px;left:14px;background:#07172be8;color:white;padding:.45rem .7rem;
border-radius:9px;font-size:.75rem;font-weight:900;letter-spacing:.05em;z-index:5}
.speaker-visual{position:absolute;left:14%;bottom:17%;font-size:4.3rem}.listener-visual{position:absolute;right:13%;bottom:17%;font-size:4.1rem}
.incident-wave{position:absolute;left:38%;top:42%;font-size:2.1rem;color:#0877c5;letter-spacing:.2rem;font-weight:900}
.transmitted-wave{position:absolute;left:12%;top:42%;font-size:2rem;color:#0877c5;font-weight:900}
.lab-panel{position:relative;display:flex;align-items:center;justify-content:center;color:white;text-align:center;
font-size:.69rem;font-weight:900;padding:.35rem;writing-mode:vertical-rl;transform:rotate(180deg)}
.lab-panel.light{background:repeating-linear-gradient(90deg,#8795a4,#8795a4 9px,#aeb9c4 9px,#aeb9c4 16px)}
.lab-panel.masonry{background:repeating-linear-gradient(0deg,#974f3e,#974f3e 22px,#d5a18d 23px,#d5a18d 26px)}
.lab-panel.double{background:linear-gradient(90deg,#263849 0 25%,#dce8f2 25% 75%,#263849 75% 100%)}
.absorber{position:absolute;background:repeating-linear-gradient(135deg,#15a6b8,#15a6b8 8px,#79d6df 8px,#79d6df 16px);
border:4px solid #087585;border-radius:6px;box-shadow:0 4px 10px #083f4b28}
.absorber.a1{left:9%;top:20%;width:72px;height:32px}.absorber.a2{right:9%;top:20%;width:72px;height:32px}
.absorber.a3{left:35%;top:20%;width:72px;height:32px}.absorber.ceiling{left:20%;right:20%;top:8%;width:auto;height:20px}
.echo-wave{position:absolute;color:#7c94a9;font-size:1.25rem;opacity:.8}.echo-wave.e1{left:18%;top:38%}.echo-wave.e2{right:22%;top:31%}.echo-wave.e3{left:38%;bottom:16%}
.concept-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem;margin:1rem 0}
.concept-result{background:white;border:1px solid var(--line);border-radius:15px;padding:1rem;text-align:center}
.concept-result b{display:block;color:#0a2d52;font-size:1.18rem;margin:.25rem 0}.concept-result span{font-size:.79rem;color:var(--muted)}
.learning-grid{margin:1rem 0 .7rem}
.learning-card{max-width:920px;margin:0 auto;background:#fff;border:1px solid var(--line);border-radius:22px;overflow:hidden;box-shadow:0 14px 34px #17324d1a}
.learning-figure{aspect-ratio:16/9;min-height:300px;background:linear-gradient(145deg,#e8f6ff,#f8fbff);display:flex;align-items:center;justify-content:center;overflow:hidden}
.learning-figure img{width:100%;height:100%;object-fit:cover;object-position:center;display:block}
.learning-copy{padding:1.35rem 1.55rem 1.5rem}.learning-kicker{font-size:.72rem;letter-spacing:.11em;font-weight:900;color:#0871bd}
.learning-copy h3{color:#092d53;margin:.3rem 0 .55rem;font-size:1.5rem}.learning-copy p{color:#40536b;line-height:1.6;margin:.35rem 0;font-size:1rem}
.observe{margin-top:.8rem;background:#eef8ff;border-left:4px solid #17a8d2;border-radius:10px;padding:.7rem .8rem;color:#294861;font-size:.88rem}
.slide-status{text-align:center;color:#536b84;font-size:.85rem;font-weight:800;margin:.55rem 0 .2rem}
.slide-dots{text-align:center;letter-spacing:.3rem;font-size:1.05rem;color:#bed2e3;margin:.2rem 0 .65rem}.slide-dots .active{color:#087bc1}
.worked-example{background:linear-gradient(135deg,#062f55,#0b5385);color:#fff;border-radius:18px;padding:1.15rem 1.25rem;margin:1rem 0;box-shadow:0 10px 25px #0b355b22}
.worked-example h3{margin:.1rem 0 .65rem;color:#fff}.worked-step{background:#ffffff12;border:1px solid #ffffff25;border-radius:12px;padding:.72rem .85rem;margin:.55rem 0;line-height:1.5}
.worked-step strong{color:#82e7ff}.worked-result{background:#eaf9ff;color:#07375d;border-radius:12px;padding:.8rem .9rem;margin-top:.65rem;font-weight:800}
.mini-scene{width:100%;height:100%;position:relative;border-radius:14px;overflow:hidden;background:linear-gradient(#dff3ff 0 70%,#d9dee3 70%)}
.mini-source,.mini-receiver,.mini-wall,.mini-wave,.mini-floorwave{position:absolute}.mini-source{left:8%;bottom:17%;font-size:3.3rem}
.mini-receiver{right:8%;bottom:17%;font-size:3.2rem}.mini-wave{left:30%;top:39%;color:#0877c5;font-size:1.7rem;font-weight:900}
.mini-wall{left:48%;bottom:10%;height:70%;width:18px;background:#344b60;border-radius:4px}.mini-floorwave{left:25%;right:23%;bottom:8%;border-bottom:5px dashed #ef8b2c}
.teacher-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.8rem}.teacher-card{background:#fff;color:#2a2141;border-radius:14px;padding:1rem;border:1px solid #d7ccef}
.teacher-card b{display:block;color:#432675;margin-bottom:.4rem}.teacher-card p,.teacher-card li{font-size:.9rem;line-height:1.48}
.small{font-size:.85rem}.route{font-size:.8rem;padding:.25rem 0;color:#d7ecff}
.institutional{display:flex;align-items:center;justify-content:space-between;gap:2rem;
background:#fff;border:1px solid var(--line);border-radius:20px;padding:1rem 1.5rem;
margin:.25rem 0 1rem;box-shadow:0 7px 25px #173b6810;overflow:hidden}
.institutional-left{display:flex;align-items:center;gap:1rem;min-width:0}
.institutional-uc{width:78px;height:92px;object-fit:contain;display:block;flex:0 0 auto}
.institutional-copy{border-left:1px solid var(--line);padding-left:1rem;min-width:0}
.institutional-title{font-size:1.02rem;font-weight:900;color:#14243a;line-height:1.25}
.institutional-sub{margin-top:.25rem;font-size:.84rem;color:var(--muted);line-height:1.3}
.institutional-decon{width:185px;max-width:28vw;height:64px;object-fit:contain;display:block;flex:0 1 auto}
@media(max-width:700px){
  .block-container{padding-top:.75rem}
  .institutional{gap:.75rem;padding:.8rem 1rem;border-radius:16px}
  .institutional-uc{width:52px;height:64px}
  .institutional-copy{padding-left:.7rem}
  .institutional-title{font-size:.82rem}
  .institutional-sub{font-size:.7rem}
  .institutional-decon{width:105px;max-width:26vw;height:45px}
  .overview,.route-grid{grid-template-columns:1fr}
  .hero{padding:1.35rem}.hero h1{font-size:1.75rem}
  .scene-pro{min-height:260px}.machine{left:4%;font-size:3.2rem}.person{right:4%;font-size:3.4rem}
  .machine-box{left:2%;width:95px}.receiver-cabin{right:2%;width:95px}.waves{left:24%;right:22%;font-size:1.35rem}
  .receiver-facade{width:112px;height:150px}.receiver-facade:before{left:12px;width:66px;height:78px}
  .two-room-lab{grid-template-columns:1fr 46px 1fr;min-height:270px}.speaker-visual,.listener-visual{font-size:3rem}
  .incident-wave,.transmitted-wave{font-size:1.25rem}.absorber{transform:scale(.75)}
  .concept-grid{grid-template-columns:1fr}
  .learning-grid,.teacher-grid{grid-template-columns:1fr}.learning-figure{min-height:210px}.learning-copy{padding:1rem}
}
</style>
""", unsafe_allow_html=True)

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

STAGES = [
("Etapa 0","Introducción y ruta del curso"),
("Etapa 1","Control del ruido: fuente, trayectoria y receptor"),
("Etapa 2","Aislamiento y absorción acústica"),
("Etapa 3","Aplicación: absorción, reverberación e inteligibilidad"),
("Etapa 4","Aislamiento y análisis costo-beneficio"),
("Etapa 5","Aplicación conceptual técnico-económica"),
("Etapa 6","Fundamentos físicos del aislamiento acústico"),
("Etapa 7","Aplicación práctica del aislamiento acústico"),
("Etapa 8","Índices de aislamiento acústico"),
("Etapa 9","Aplicación práctica de los índices"),
("Etapa 10","Evaluación final · Aislamiento a Ruido Aéreo"),
]

# La sesión completa dura 4 horas: 230 minutos de trabajo y 10 minutos de pausa.
STAGE_MINUTES = {0:10, 1:20, 2:25, 3:20, 4:20, 5:15, 6:30, 7:25, 8:20, 9:20, 10:25}
BREAK_AFTER_STAGE = 5
BREAK_MINUTES = 10
TOTAL_CLASS_MINUTES = sum(STAGE_MINUTES.values()) + BREAK_MINUTES

STAGE_GUIDE = {
0:("🧭","CONOCERÁS","La ruta completa del laboratorio y el propósito profesional de cada etapa.",
   "🎯","AL FINAL","Sabrás qué aprenderás, cómo experimentarás y cómo se evaluará tu avance.",
   "⏱️","RECORRIDO","240 minutos totales: 230 de trabajo guiado y una pausa de 10 minutos."),
1:("🏭","COMPRENDERÁS","Fuente, trayectoria y receptor; propagación aérea, estructural, directa e indirecta.",
   "🧪","EXPERIMENTARÁS","Encapsulado, barrera, separación física, cabina, fachada y protección auditiva sobre una escena dinámica.",
   "✅","APLICARÁS","La intervención correcta según el lugar donde nace, viaja o se recibe el ruido."),
2:("🧱","DIFERENCIARÁS","Aislamiento, absorción, reverberación e inteligibilidad sin confundir sus funciones.",
   "🔊","OBSERVARÁS","Qué energía se refleja, absorbe y transmite entre dos recintos.",
   "📐","CALCULARÁS","Cómo la absorción equivalente modifica el tiempo de reverberación."),
3:("🏫","RESOLVERÁS","Casos de acondicionamiento de aulas, reuniones y recintos con ruido exterior.",
   "🧮","CALCULARÁS","Absorción equivalente y tiempo de reverberación con la ecuación de Sabine.",
   "💬","INTERPRETARÁS","La relación entre reverberación, ruido de fondo y claridad de la palabra."),
4:("💰","COMPRENDERÁS","Costo total, rendimiento decreciente, ROI, recuperación y punto de equilibrio.",
   "📊","COMPARARÁS","Mejora acústica, inversión, mantención, vida útil y beneficios evitados.",
   "🎯","DECIDIRÁS","Solo entre soluciones que primero cumplen la meta acústica."),
5:("⚖️","ANALIZARÁS","Alternativas técnico-económicas bajo una meta acústica común.",
   "📈","EVALUARÁS","Costo del ciclo, ROI, payback, riesgo y suficiencia técnica.",
   "✅","RECOMENDARÁS","La opción justificable, no simplemente la más barata o la de mayor aislamiento."),
6:("🌊","COMPRENDERÁS","Transmisión, ley de masa, resonancia, coincidencia y sistemas dobles.",
   "🧪","EXPERIMENTARÁS","Masa, frecuencia, cámaras, absorbentes, sellos y elementos débiles.",
   "📉","INTERPRETARÁS","Curvas por bandas y las causas físicas de sus valles y pendientes."),
7:("🛠️","RESOLVERÁS","Ejercicios prácticos de cerramientos simples, dobles y compuestos.",
   "🔎","DIAGNOSTICARÁS","La banda crítica, el elemento débil y la vía dominante.",
   "✅","VERIFICARÁS","El cumplimiento de una meta sin sobredimensionar componentes secundarios."),
8:("📏","CONOCERÁS","R, Rw, C, Ctr, STC, OITC e índices de laboratorio, terreno y fachada.",
   "🗂️","INTERPRETARÁS","Fichas técnicas, normas, contextos y adaptaciones espectrales.",
   "🎯","SELECCIONARÁS","El indicador que representa correctamente la fuente y el problema real."),
9:("📉","CALCULARÁS","Rw mediante la curva de referencia y sus desviaciones desfavorables.",
   "🔄","COMPARARÁS","Particiones con igual índice global pero distinto comportamiento espectral.",
   "✅","DECIDIRÁS","Según voz, tránsito, bajas frecuencias, laboratorio o terreno."),
10:("📝","RESPONDERÁS","29 preguntas teórico-aplicadas de todas las etapas.",
    "🏢","RESOLVERÁS","Un caso profesional con T60, bandas críticas e índices acústicos.",
    "💰","JUSTIFICARÁS","La solución final mediante desempeño, costo, vida útil y objetivo de diseño."),
}

ROUTE_SUMMARIES = [
("Fuente, trayectoria y receptor","Ubica dónde nace el ruido, cómo viaja y dónde conviene intervenir."),
("Aislamiento y absorción","Distingue transmisión entre recintos de reflexiones y reverberación interior."),
("Aplicación acústica interior","Calcula T₆₀ y mejora la inteligibilidad mediante decisiones concretas."),
("Costo-beneficio","Relaciona meta acústica, inversión, ROI, vida útil y costos evitados."),
("Decisión técnico-económica","Compara alternativas y descarta las que no cumplen técnicamente."),
("Fundamentos físicos","Explora masa, frecuencia, resonancia, coincidencia y sistemas dobles."),
("Diseño práctico","Detecta bandas críticas, elementos débiles y vías dominantes."),
("Índices acústicos","Interpreta Rw, C, Ctr, STC, OITC y resultados de terreno."),
("Aplicación de índices","Trabaja con curvas, desviaciones, fuentes y fichas técnicas."),
("Evaluación final","Integra acústica y costo-beneficio en una decisión profesional."),
]

def stage_overview(stage_number):
    items=STAGE_GUIDE[stage_number]
    cards=[items[0:3],items[3:6],items[6:9]]
    html='<div class="overview">'
    for icon,title,text in cards:
        html+=f'<div class="overview-card"><div class="overview-icon">{icon}</div><div class="overview-title">{title}</div><div class="overview-text">{text}</div></div>'
    st.markdown(html+'</div>',unsafe_allow_html=True)

def header(kicker,title,desc):
    match=re.search(r"ETAPA\s+(\d+)",kicker)
    stage_number=int(match.group(1)) if match else None
    duration=(f'<div class="time-badge">⏱️ Tiempo de aplicación: {STAGE_MINUTES[stage_number]} minutos</div>'
              if stage_number in STAGE_MINUTES else "")
    st.markdown(f'<div class="hero"><span class="tag">{kicker}</span><h1>{title}</h1><p>{desc}</p>{duration}</div>',unsafe_allow_html=True)
    if match:
        stage_overview(stage_number)

def image_data_uri(path):
    if not path.exists():
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

def institutional_header():
    uc = ROOT/"assets/logos/logo_uc.png"
    decon = ROOT/"assets/logos/logo_decon_uc.png"
    st.markdown(
        f"""
        <div class="institutional">
          <div class="institutional-left">
            <img class="institutional-uc" src="{image_data_uri(uc)}" alt="Pontificia Universidad Católica de Chile">
            <div class="institutional-copy">
              <div class="institutional-title">Diplomado en Acústica en la Edificación</div>
              <div class="institutional-sub">Escuela de Construcción Civil · Facultad de Ingeniería</div>
            </div>
          </div>
          <img class="institutional-decon" src="{image_data_uri(decon)}" alt="DECON UC">
        </div>
        """,
        unsafe_allow_html=True,
    )

def _academic_blocks(content):
    """Transform the approved Word text into short, readable teaching cards."""
    hidden_phrases=(
        "Puede presentarse","No colocaría","Imagen interactiva propuesta",
        "Visual interactivo principal","Propongo una","La aplicación mostrará",
        "La aplicación podrá","La animación debe","Funcionamiento de la aplicación",
        "También cambiaría","Esta modificación mejora"
    )
    paragraphs=[
        p.strip() for p in content.split("\n\n") if p.strip()
        and not any(phrase.lower() in p.lower() for phrase in hidden_phrases)
    ]
    duration=""
    useful=[]
    for paragraph in paragraphs:
        if paragraph.startswith("## Etapa"):
            continue
        if paragraph.lower().startswith(("duración propuesta:", "tiempo:")) and not duration:
            duration=paragraph
            continue
        useful.append(paragraph)

    heading_pattern=re.compile(
        r"^(?:\d+\.\s+|#{1,4}\s+|Ejercicio(?:\s+\d+)?|Ejemplo(?:\s+sencillo)?|"
        r"Problema|Caso\s+[A-Z0-9]|Idea central|Resultado final|Distribución temática)",
        re.IGNORECASE,
    )
    blocks=[]
    title=""
    body=[]

    def flush():
        nonlocal title,body
        if title or body:
            blocks.append((title or f"Fundamento para la explicación {len(blocks)+1}", "\n\n".join(body)))
        title,body="",[]

    for paragraph in useful:
        first_line=paragraph.splitlines()[0].strip()
        is_short_heading=len(paragraph)<95 and not paragraph.rstrip().endswith((".",":",";"))
        if heading_pattern.match(first_line) or is_short_heading:
            flush()
            title=re.sub(r"^#{1,4}\s*","",paragraph).strip()
        else:
            body.append(paragraph)
            if sum(len(p) for p in body)>1250:
                flush()
    flush()
    return duration,[(t,b) for t,b in blocks if t or b]

def _student_card_body(body):
    """Keep the learner-facing card focused while preserving complete tables."""
    if not body:
        return ""
    if "| ---" in body:
        return body
    paragraphs=[p for p in body.split("\n\n") if p.strip()]
    selected=[]
    length=0
    for paragraph in paragraphs:
        if length+len(paragraph)>720 and selected:
            break
        selected.append(paragraph)
        length+=len(paragraph)
    summary="\n\n".join(selected)
    if len(selected)<len(paragraphs):
        summary+="\n\n> **Idea para recordar:** identifica el fenómeno, la variable que cambia y el efecto esperado antes de aplicar una fórmula."
    return summary

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
("ROI y payback","El ROI relaciona el beneficio neto con el costo total. El payback estima cuánto tarda en recuperarse la inversión inicial mediante el beneficio anual neto.","El encapsulamiento debe cumplir primero su función acústica; luego el ciclo económico permite estudiar recuperación, mantención y beneficio.","stage4_roi_payback.webp",None),
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

STAGE_INTROS = {
3:("Ahora aplicarás lo aprendido","Identifica el fenómeno, clasifica la intervención y responde cada ejercicio en pantalla. La retroalimentación te mostrará por qué una opción es correcta."),
5:("Decidir exige dos filtros","Primero comprueba el desempeño acústico; después compara inversión, vida útil, ROI y costo del ciclo."),
7:("Diseño guiado por la banda crítica","Modifica el cerramiento y el elemento débil. La curva mostrará qué banda y qué vía dominan el nivel receptor."),
9:("Del espectro al indicador","Trabaja con curvas por bandas antes de tomar una decisión basada en Rw, C, Ctr, STC u OITC."),
10:("Evaluación final","Responde 29 preguntas de alternativas y un caso integrador directamente en pantalla."),
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

def _visual_path(filename):
    if not filename:
        return None
    candidates=[ROOT/"assets/course_visuals"/filename,ROOT/"LAB_AEREO_CLASE_1/assets/course_visuals"/filename]
    return next((p for p in candidates if p.exists()),None)

def _fallback_figure(symbol):
    if "━━━" in (symbol or ""):
        return '<div class="mini-scene"><div class="mini-source">🏭</div><div class="mini-wave">))) )))</div><div class="mini-receiver">🧑</div><div class="mini-floorwave"></div></div>'
    return f'<div style="font-size:4rem;text-align:center">{symbol or "🔎"}</div>'

def student_lesson(stage_number):
    lessons=STUDENT_LESSONS.get(stage_number,[])
    if lessons:
        st.markdown('<div class="section-band"><span>🖼️</span><h3>Conceptualización</h3></div>',unsafe_allow_html=True)
        st.caption("Avanza como en una presentación: revisa una figura y su explicación antes de pasar a la siguiente.")
        key=f"lesson_slide_{stage_number}"
        if key not in st.session_state:
            st.session_state[key]=0
        index=max(0,min(st.session_state[key],len(lessons)-1))
        title,definition,observe,image_name,symbol=lessons[index]
        path=_visual_path(image_name)
        visual=f'<img src="{image_data_uri(path)}" alt="{title}">' if path else _fallback_figure(symbol)
        st.markdown(
            f'<div class="learning-grid"><article class="learning-card"><div class="learning-figure">{visual}</div>'
            f'<div class="learning-copy"><div class="learning-kicker">DIAPOSITIVA {index+1} DE {len(lessons)} · DEFINICIÓN ILUSTRADA</div>'
            f'<h3>{title}</h3><p>{definition}</p><div class="observe"><b>Qué observar:</b> {observe}</div></div></article></div>',
            unsafe_allow_html=True,
        )
        dots="".join(f'<span class="{"active" if i==index else ""}">●</span>' for i in range(len(lessons)))
        st.markdown(f'<div class="slide-status">{index+1} / {len(lessons)}</div><div class="slide-dots">{dots}</div>',unsafe_allow_html=True)
        previous,next_col=st.columns(2)
        if previous.button("← Anterior",key=f"prev_slide_{stage_number}",use_container_width=True,disabled=index==0):
            st.session_state[key]=index-1
            st.rerun()
        if next_col.button("Siguiente →",key=f"next_slide_{stage_number}",use_container_width=True,disabled=index==len(lessons)-1):
            st.session_state[key]=index+1
            st.rerun()
    elif stage_number in STAGE_INTROS:
        title,text=STAGE_INTROS[stage_number]
        st.markdown(f'<div class="lesson"><div class="overview-title">ANTES DE COMENZAR</div><h3>{title}</h3><span class="muted">{text}</span></div>',unsafe_allow_html=True)

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
("Separe dos preguntas: payback indica cuándo se recupera la inversión; ROI indica rentabilidad acumulada en un horizonte. En el ejemplo, inversión $2,0 millones y beneficio neto anual $0,6 millones producen payback 3,33 años; a cinco años, beneficio neto acumulado $1,0 millón y ROI 50 %.","Si dos soluciones tienen el mismo payback, ¿tienen necesariamente el mismo ROI?","No. Pueden tener distinta vida útil, flujos posteriores, mantención y beneficio acumulado; el payback ignora lo que ocurre después de recuperar la inversión.","Dibuje una línea de tiempo de caja. ROI = (beneficios acumulados − costos acumulados)/inversión × 100; payback = inversión/flujo neto anual solo si el flujo es aproximadamente constante."),
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

def full_matter(stage_number):
    """Render curated learner content and a separate, role-protected teacher guide."""
    student_lesson(stage_number)
    if stage_number==0 or st.session_state.get("role")!="Docente":
        return
    guide=TEACHER_GUIDES.get(stage_number)
    if not guide:
        return
    explanation,questions=guide
    slide_support=TEACHER_SLIDE_SUPPORT.get(stage_number)
    if slide_support:
        slide_index=max(0,min(st.session_state.get(f"lesson_slide_{stage_number}",0),len(slide_support)-1))
        slide_title=STUDENT_LESSONS[stage_number][slide_index][0]
        explanation,question,answer,tip=slide_support[slide_index]
    st.markdown(
        '<div class="teacher-only"><b>🔐 Profundización técnica exclusiva para el docente</b>'
        '<span>La orientación cambia junto con la figura que está visible para el alumno.</span></div>',
        unsafe_allow_html=True,
    )
    with st.expander("Abrir guía docente de esta etapa",expanded=False):
        st.markdown('<div class="teacher-grid">',unsafe_allow_html=True)
        if slide_support:
            st.markdown(f'<div class="teacher-card"><b>Figura visible · {slide_title}</b><p>{explanation}</p></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="teacher-card"><b>Pregunta vinculada a esta figura</b><p><strong>{question}</strong></p><p><span>Respuesta esperada: {answer}</span></p></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="teacher-card"><b>Tip técnico para explicarla</b><p>{tip}</p></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="teacher-card"><b>Conexión con el laboratorio</b><p>{TEACHER_GUIDES[stage_number][0]}</p></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="teacher-card"><b>Cómo conducir la actividad o laboratorio</b><p>{explanation}</p></div>',unsafe_allow_html=True)
            qhtml="".join(f"<li><strong>{q}</strong><br><span>Respuesta esperada: {answer}</span></li>" for q,answer in questions)
            st.markdown(f'<div class="teacher-card"><b>Preguntas y soluciones para el docente</b><ol>{qhtml}</ol></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

def lesson(title, text):
    st.markdown(f'<div class="lesson"><div class="overview-title">CONCEPTO CLAVE</div><h3>{title}</h3><span class="muted">{text}</span></div>',unsafe_allow_html=True)

def formula_card(title, latex, variables, use):
    st.markdown(f'<div class="formula"><div style="font-size:.75rem;letter-spacing:.12em;color:#8ee9ff;font-weight:900">ECUACIÓN VISUAL</div><h3 style="color:white;margin:.35rem 0">{title}</h3></div>',unsafe_allow_html=True)
    st.latex(latex)
    c1,c2=st.columns(2)
    c1.markdown(f'<div class="card"><div class="overview-title">VARIABLES Y UNIDADES</div>{variables}</div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><div class="overview-title">CUÁNDO SE UTILIZA</div>{use}</div>',unsafe_allow_html=True)

def check(key,q,options,correct,explanation):
    st.markdown(f'<div class="question-box"><div class="question-label">PREGUNTA DE COMPRENSIÓN</div><div class="question-text">{q}</div></div>',unsafe_allow_html=True)
    choice=st.radio("Selecciona tu respuesta",options,index=None,key=key,label_visibility="collapsed")
    if st.button("Comprobar",key=f"b_{key}"):
        if choice==correct: st.success(f"Correcto. {explanation}")
        elif choice is None: st.warning("Selecciona una respuesta.")
        else: st.error(f"No es correcto. {explanation}")

def development_answer(key,q,guide):
    """Visible written response with explicit submission and formative guidance."""
    st.markdown(
        f'<div class="question-box"><div class="question-label">EJERCICIO DE DESARROLLO</div>'
        f'<div class="question-text">{q}</div></div>',
        unsafe_allow_html=True,
    )
    answer=st.text_area(
        "Escribe tu respuesta y justificación",
        key=key,
        placeholder="Explica tu decisión utilizando los conceptos estudiados…",
    )
    if st.button("Enviar desarrollo",key=f"b_{key}"):
        if len(answer.strip())<20:
            st.warning("Desarrolla un poco más tu respuesta antes de enviarla.")
        else:
            st.session_state[f"sent_{key}"]=True
            st.success("Respuesta enviada. Compárala con la pauta formativa.")
    if st.session_state.get(f"sent_{key}"):
        st.markdown(
            f'<div class="good"><b>Pauta de comparación:</b> {guide}</div>',
            unsafe_allow_html=True,
        )

def _activity_db():
    con=sqlite3.connect(ACTIVITY_DB)
    con.execute(
        """CREATE TABLE IF NOT EXISTS formative_responses(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
        student TEXT NOT NULL, stage INTEGER NOT NULL, question_key TEXT NOT NULL,
        question TEXT NOT NULL, answer TEXT NOT NULL, auto_level TEXT,
        feedback TEXT, teacher_level TEXT, auto_score REAL DEFAULT 0,
        max_score REAL DEFAULT 0, teacher_score REAL,
        teacher_note TEXT, UNIQUE(student,stage,question_key))"""
    )
    existing={row[1] for row in con.execute("PRAGMA table_info(formative_responses)")}
    for column,definition in (
        ("auto_score","REAL DEFAULT 0"),("max_score","REAL DEFAULT 0"),
        ("teacher_score","REAL"),("teacher_note","TEXT"),
    ):
        if column not in existing:
            con.execute(f"ALTER TABLE formative_responses ADD COLUMN {column} {definition}")
    con.commit()
    return con

def _question_points(stage,key):
    return float(APPLICATION_POINTS.get(stage,{}).get(key,0))

def _score_from_level(level,max_score):
    return max_score if level=="Correcta" else max_score*.5 if level=="Parcialmente correcta" else 0.0

def _save_formative(stage,key,question,answer,level,feedback,score=None,max_score=None):
    student=st.session_state.get("name","Alumno")
    max_score=_question_points(stage,key) if max_score is None else float(max_score)
    score=_score_from_level(level,max_score) if score is None else float(score)
    with _activity_db() as con:
        con.execute(
            """INSERT INTO formative_responses
            (created_at,student,stage,question_key,question,answer,auto_level,feedback,auto_score,max_score)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(student,stage,question_key) DO UPDATE SET
            created_at=excluded.created_at,question=excluded.question,
            answer=excluded.answer,auto_level=excluded.auto_level,feedback=excluded.feedback,
            auto_score=excluded.auto_score,max_score=excluded.max_score""",
            (dt.datetime.now().isoformat(timespec="seconds"),student,stage,key,question,str(answer),level,feedback,score,max_score),
        )

def _student_scores(student=None):
    student=student or st.session_state.get("name","Alumno")
    with _activity_db() as con:
        rows=con.execute(
            """SELECT stage,question_key,auto_score,max_score,teacher_score
            FROM formative_responses WHERE student=?""",(student,)).fetchall()
    return rows

def score_counter(stage=None,compact=False):
    rows=_student_scores()
    if stage is not None:
        rows=[row for row in rows if row[0]==stage]
        maximum=sum(APPLICATION_POINTS.get(stage,{}).values())
        title=f"Puntaje de la Etapa {stage}"
    else:
        maximum=APPLICATION_TOTAL
        title="Puntaje acumulado"
    earned=sum((row[4] if row[4] is not None else row[2]) or 0 for row in rows)
    completed=len({row[1] for row in rows})
    expected=len(APPLICATION_POINTS.get(stage,{})) if stage is not None else sum(len(x) for x in APPLICATION_POINTS.values())
    pct=100*earned/maximum if maximum else 0
    if compact:
        st.markdown(
            f'<div class="score-counter sidebar-score"><div><b>🏆 {title}</b>'
            f'<small>{completed} de {expected} actividades respondidas</small>'
            f'<div class="score-track"><div class="score-fill" style="width:{min(pct,100):.1f}%"></div></div></div>'
            f'<div class="score-number">{earned:g}/{maximum:g}<small>{pct:.0f}%</small></div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="score-counter"><div><b>🏆 {title}</b>'
            f'<small>{completed} de {expected} actividades respondidas · {pct:.0f}% del puntaje</small>'
            f'<div class="score-track"><div class="score-fill" style="width:{min(pct,100):.1f}%"></div></div></div>'
            f'<div class="score-number">{earned:g} / {maximum:g} pts</div></div>',
            unsafe_allow_html=True,
        )

def _keyword_level(answer,groups):
    text=re.sub(r"\s+"," ",answer.lower())
    hits=sum(any(term.lower() in text for term in group) for group in groups)
    if hits>=max(2,math.ceil(len(groups)*.70)): return "Correcta",hits
    if hits>=max(1,math.ceil(len(groups)*.35)): return "Parcialmente correcta",hits
    return "Incorrecta",hits

def formative_development(stage,key,question,solution,groups,error_note):
    st.markdown(
        f'<div class="question-box"><div class="question-label">PREGUNTA DE DESARROLLO</div>'
        f'<div class="question-text">{question}</div></div>',unsafe_allow_html=True)
    answer=st.text_area("Escribe y justifica tu respuesta",key=f"ans_{key}",
                        placeholder="Explica el fenómeno y propone una solución cuando corresponda…")
    if st.button("Comprobar respuesta",key=f"submit_{key}",type="primary"):
        if len(answer.strip())<20:
            st.warning("La respuesta es demasiado breve. Explica el fenómeno antes de comprobar.")
        else:
            level,hits=_keyword_level(answer,groups)
            if level=="Correcta":
                feedback="Reconoces los conceptos esenciales y los relacionas correctamente."
                st.success(f"Respuesta correcta. {feedback}")
            elif level=="Parcialmente correcta":
                feedback=f"Tu respuesta va bien, pero está incompleta. {error_note}"
                st.warning(f"Respuesta parcialmente correcta. {feedback}")
            else:
                feedback=f"Hay una confusión conceptual. {error_note}"
                st.error(f"Respuesta incorrecta. {feedback}")
            st.session_state[f"checked_{key}"]=(level,feedback)
            _save_formative(stage,key,question,answer,level,feedback)
    if st.session_state.get(f"checked_{key}"):
        with st.expander("Ver solución desarrollada"):
            st.markdown(solution)

def formative_numeric(stage,key,question,inputs,checker,solution):
    st.markdown(
        f'<div class="question-box"><div class="question-label">EJERCICIO NUMÉRICO</div>'
        f'<div class="question-text">{question}</div></div>',unsafe_allow_html=True)
    values={}
    cols=st.columns(min(len(inputs),3))
    for i,(name,label,default,step) in enumerate(inputs):
        values[name]=cols[i%len(cols)].number_input(label,value=default,step=step,key=f"{key}_{name}")
    if st.button("Comprobar cálculo",key=f"submit_{key}",type="primary"):
        ok,feedback=checker(values)
        level="Correcta" if ok else "Incorrecta"
        (st.success if ok else st.error)(("Correcto. " if ok else "Revisa el procedimiento. ")+feedback)
        st.session_state[f"checked_{key}"]=(level,feedback)
        _save_formative(stage,key,question,json.dumps(values,ensure_ascii=False),level,feedback)
    if st.session_state.get(f"checked_{key}"):
        with st.expander("Ver desarrollo paso a paso"):
            st.markdown(solution)

def teacher_group_review(stage,solutions):
    if st.session_state.get("role")!="Docente":
        return
    st.markdown('<div class="teacher-only"><b>👥 Revisión grupal de respuestas</b>'
                '<span>Seleccione una respuesta y revele la pauta solamente cuando decida discutirla con el curso.</span></div>',
                unsafe_allow_html=True)
    with _activity_db() as con:
        rows=con.execute(
            "SELECT id,created_at,student,question_key,question,answer,auto_level,feedback,teacher_level,"
            "auto_score,max_score,teacher_score,teacher_note "
            "FROM formative_responses WHERE stage=? ORDER BY question_key,created_at",(stage,)).fetchall()
    if not rows:
        st.info("Todavía no hay respuestas guardadas de alumnos para esta etapa.")
        return
    labels=[f"{r[3]} · {r[2]} · {r[1].replace('T',' ')}" for r in rows]
    selected=st.selectbox("Respuesta para revisar",range(len(rows)),format_func=lambda i:labels[i],key=f"review_{stage}")
    rid,_,student,qkey,question,answer,auto_level,feedback,teacher_level,auto_score,max_score,teacher_score,teacher_note=rows[selected]
    anonymous=st.toggle("Ocultar nombre al proyectar",value=True,key=f"anon_{stage}")
    st.markdown(f"**Pregunta:** {question}")
    st.markdown(f"**Respuesta de {'Alumno/a' if anonymous else student}:**")
    st.info(answer)
    st.caption(f"Evaluación automática inicial: {auto_level} · {auto_score:g}/{max_score:g} puntos. {feedback or ''}")
    if st.toggle("Mostrar solución esperada",key=f"reveal_{stage}"):
        st.success(solutions.get(qkey,"Revise la pauta técnica asociada a esta pregunta."))
    levels=["Sin revisar","Correcta","Parcialmente correcta","Incorrecta"]
    current=levels.index(teacher_level) if teacher_level in levels else 0
    mark=st.selectbox("Evaluación docente",levels,index=current,key=f"mark_{stage}_{rid}")
    manual=st.number_input(
        "Puntaje docente",min_value=0.0,max_value=float(max_score),value=float(teacher_score if teacher_score is not None else auto_score),
        step=0.5,key=f"teacher_score_{stage}_{rid}",
        help="Este puntaje reemplaza la corrección automática en el contador del alumno.",
    )
    note=st.text_area("Observación para el alumno",value=teacher_note or "",key=f"teacher_note_{stage}_{rid}")
    if st.button("Guardar evaluación docente",key=f"save_mark_{stage}_{rid}"):
        with _activity_db() as con:
            con.execute(
                "UPDATE formative_responses SET teacher_level=?,teacher_score=?,teacher_note=? WHERE id=?",
                (mark,manual,note,rid),
            )
        st.success("Evaluación docente y puntaje guardados.")
    with _activity_db() as con:
        summary=pd.read_sql_query(
            """SELECT student AS Alumno,
            ROUND(SUM(COALESCE(teacher_score,auto_score)),1) AS Puntaje,
            ROUND(SUM(max_score),1) AS Respondido_sobre,
            COUNT(*) AS Actividades
            FROM formative_responses WHERE stage=? GROUP BY student ORDER BY Puntaje DESC""",
            con,params=(stage,),
        )
    with st.expander("Panel de resultados de la etapa"):
        st.dataframe(summary,hide_index=True,use_container_width=True)
        st.download_button(
            "Descargar resultados CSV",summary.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"resultados_etapa_{stage}.csv",mime="text/csv",key=f"download_scores_{stage}",
        )

def line_chart(x, series, title, ytitle):
    fig=go.Figure()
    for name,y in series: fig.add_trace(go.Scatter(x=x,y=y,name=name,mode="lines+markers"))
    fig.update_layout(title=title,xaxis_title="Frecuencia (Hz)",yaxis_title=ytitle,height=390,
                      template="plotly_white",margin=dict(l=20,r=20,t=55,b=20))
    fig.update_xaxes(type="log",tickvals=x)
    st.plotly_chart(fig,use_container_width=True)

def stage0():
    header("ETAPA 0 · BIENVENIDA","Laboratorio del curso Aislamiento a Ruido Aéreo",
           "Una experiencia visual para comprender el fenómeno, experimentar con variables y decidir con criterio técnico y económico.")
    full_matter(0)
    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Duración total de la clase: 4 horas</strong>'
        f'<br><span>{sum(STAGE_MINUTES.values())} min de aprendizaje y aplicación + {BREAK_MINUTES} min de pausa</span></div>'
        f'<div><strong>{TOTAL_CLASS_MINUTES} min</strong></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',unsafe_allow_html=True)
    html='<div class="route-grid">'
    for i,((_,title),(short,desc)) in enumerate(zip(STAGES[1:],ROUTE_SUMMARIES),1):
        html+=f'<div class="route-card"><span class="step">{i}</span><div><b>{title}</b><p>{desc}</p><span class="route-time">⏱️ {STAGE_MINUTES[i]} min</span></div></div>'
        if i==BREAK_AFTER_STAGE:
            html+=f'<div class="break-card"><span class="step">☕</span><div><b>Pausa pedagógica</b><p>Descanso antes del bloque de fundamentos físicos.</p><span class="route-time">⏱️ {BREAK_MINUTES} min</span></div></div>'
    st.markdown(html+'</div>',unsafe_allow_html=True)
    st.markdown('<div class="good" style="margin-top:1rem"><b>Así aprenderás:</b> concepto visual → explicación técnica → ejemplo → interacción → interpretación → ejercicio → retroalimentación.</div>',unsafe_allow_html=True)

def stage1():
    header("ETAPA 1 · MATERIA + LABORATORIO","Control del ruido: fuente, trayectoria y receptor",
           "Antes de elegir un material hay que localizar dónde nace el ruido, cómo se propaga y a quién afecta.")
    full_matter(1)
    lesson("Modelo de control","Fuente: genera la energía. Trayectoria: medio y vías de propagación. Receptor: persona, actividad o recinto afectado. Una solución robusta puede combinar los tres.")
    st.markdown('<div class="section-band"><span>🎛️</span><h3>Laboratorio visual: interviene la escena</h3></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    source=c1.selectbox("🏭 En la fuente",["Sin intervención","Encerrar la fuente","Soportes antivibratorios","Equipo de menor emisión"])
    path=c2.selectbox("〰️ En la trayectoria",["Sin intervención","Barrera acústica"])
    receiver=c3.selectbox("👤 En el receptor",["Sin intervención","Protección auditiva","Cabina acústica","Mejorar fachada"])
    distance=st.select_slider(
        "📏 Separación física entre la fuente y el receptor",
        options=["Distancia inicial","Distancia aumentada"],
        help="La distancia no es una barrera ni una intervención en la trayectoria: es una condición geométrica del problema.",
    )
    gains={"Sin intervención":0,"Encerrar la fuente":10,"Soportes antivibratorios":5,"Equipo de menor emisión":12,
           "Barrera acústica":12,
           "Protección auditiva":10,"Cabina acústica":15,"Mejorar fachada":11}
    distance_gain=5 if distance=="Distancia aumentada" else 0
    total=gains[source]+gains[path]+gains[receiver]+distance_gain
    enclosure='<div class="machine-box"></div>' if source=="Encerrar la fuente" else ""
    mounts='<div class="mounts">▰ ▰</div>' if source=="Soportes antivibratorios" else ""
    barrier='<div class="barrier"></div>' if path=="Barrera acústica" else ""
    cabin='<div class="receiver-cabin"></div>' if receiver=="Cabina acústica" else ""
    facade='<div class="receiver-facade"></div>' if receiver=="Mejorar fachada" else ""
    phones='<div class="headphones">🎧</div>' if receiver=="Protección auditiva" else ""
    wave_count=max(1,6-round(total/7))
    waves=")"*wave_count
    distance_class=" distance-on" if distance=="Distancia aumentada" else ""
    distance_label="Fuente y receptor más separados" if distance=="Distancia aumentada" else "Distancia inicial"
    st.markdown(
        f'<div class="scene-pro{distance_class}"><div class="scene-caption">Nivel visual estimado: {85-total} dB</div>'
        f'{enclosure}{mounts}<div class="machine">⚙️</div><div class="waves">))) {waves}</div>{barrier}'
        f'{cabin}{facade}{phones}<div class="person">🧑</div><div class="distance-label">↔ {distance_label}</div></div>',
        unsafe_allow_html=True,
    )
    a,b,c=st.columns(3);a.metric("Nivel inicial","85 dB");b.metric("Reducción estimada",f"{total} dB");c.metric("Nivel resultante",f"{85-total} dB")
    st.markdown('<div class="warn">Las reducciones se suman aquí con fines didácticos. En un proyecto real deben evaluarse por bandas, vías dominantes y condiciones de montaje.</div>',unsafe_allow_html=True)
    check("e1","Una máquina afecta una oficina contigua. ¿Dónde actúa el muro separador?",["Fuente","Trayectoria","Receptor"],"Trayectoria","El muro se interpone en el camino de propagación.")

def stage2():
    header("ETAPA 2 · LABORATORIO DE DOS RECINTOS","Aislamiento no es absorción",
           "Cambia el panel separador y acondiciona el recinto receptor para observar qué magnitud modifica cada decisión.")
    full_matter(2)
    lesson("Aislamiento acústico","Reduce la energía que atraviesa un elemento entre recintos. Se mejora con masa, estanqueidad, desacoplamiento y control de vías indirectas.")
    lesson("Absorción acústica","Reduce reflexiones dentro del mismo recinto. Se expresa mediante α entre 0 y 1 y modifica reverberación e inteligibilidad.")
    st.markdown('<div class="section-band"><span>🧪</span><h3>Ejemplo didáctico: recinto emisor → panel → recinto receptor</h3></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    panel=c1.selectbox(
        "🧱 Panel separador",
        ["Panel liviano simple","Muro de albañilería","Tabique doble desacoplado"],
        help="Este control modifica la transmisión entre los dos recintos.",
    )
    material=c2.selectbox(
        "🟦 Material absorbente en el receptor",
        ["Sin tratamiento","Panel poroso α = 0,40","Lana mineral revestida α = 0,75","Panel de alto desempeño α = 0,90"],
        help="Este material controla las reflexiones dentro del recinto receptor.",
    )
    area=c3.slider("📐 Superficie absorbente instalada (m²)",0,60,0,5)

    panel_data={
        "Panel liviano simple":(30,"light"),
        "Muro de albañilería":(45,"masonry"),
        "Tabique doble desacoplado":(55,"double"),
    }
    alpha_data={
        "Sin tratamiento":0.0,
        "Panel poroso α = 0,40":0.40,
        "Lana mineral revestida α = 0,75":0.75,
        "Panel de alto desempeño α = 0,90":0.90,
    }
    R,panel_class=panel_data[panel]
    alpha=alpha_data[material]
    V=120.0
    A0=18.0
    A=A0+alpha*area
    T0=.161*V/A0
    T=.161*V/A
    source_level=85.0
    # Relación didáctica: el campo reverberante del receptor disminuye al
    # aumentar A, aunque la propiedad aislante R del panel permanece igual.
    room_correction=10*math.log10(A/A0) if A>A0 else 0.0
    receiver_level=source_level-R-room_correction
    absorber_count=0 if area==0 or alpha==0 else min(4,max(1,math.ceil(area/15)))
    absorber_html="".join(
        f'<div class="absorber {"ceiling" if i==3 else f"a{i+1}"}"></div>'
        for i in range(absorber_count)
    )
    echo_count=max(0,3-round((A-A0)/18))
    echoes="".join(f'<div class="echo-wave e{i+1}">↝ ↝</div>' for i in range(echo_count))
    wave_strength=max(1,min(5,round((60-R)/7)))
    transmitted=")"*wave_strength
    st.markdown(
        f'<div class="two-room-lab">'
        f'<div class="lab-room"><div class="room-name">RECINTO EMISOR · 85 dB</div>'
        f'<div class="speaker-visual">🔊</div><div class="incident-wave">))) )))</div></div>'
        f'<div class="lab-panel {panel_class}">{panel}<br>R = {R} dB</div>'
        f'<div class="lab-room receiver"><div class="room-name">RECINTO RECEPTOR</div>'
        f'{absorber_html}{echoes}<div class="transmitted-wave">{transmitted}</div>'
        f'<div class="listener-visual">🧑‍💻</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="concept-grid">'
        f'<div class="concept-result">🧱<b>{R:.0f} dB</b><span>Aislamiento R del panel<br><strong>No cambia por agregar absorbentes</strong></span></div>'
        f'<div class="concept-result">🟦<b>{A:.1f} m² sabin</b><span>Absorción equivalente del receptor<br>Inicial: {A0:.1f} m² sabin</span></div>'
        f'<div class="concept-result">⏱️<b>{T:.2f} s</b><span>T₆₀ del recinto receptor<br>Inicial: {T0:.2f} s</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    a,b,c=st.columns(3)
    a.metric("Nivel estimado en el receptor",f"{receiver_level:.1f} dB")
    b.metric("Cambio de T₆₀",f"{T-T0:+.2f} s")
    c.metric("Cambio del aislamiento R","0 dB" if material!="Sin tratamiento" else "Sin tratamiento")
    st.markdown(
        '<div class="good"><b>Interpretación:</b> cambiar el panel separador modifica el aislamiento entre recintos. '
        'Agregar material absorbente en el receptor aumenta su absorción equivalente, reduce las reflexiones y disminuye '
        'el T₆₀. El nivel medido en el receptor puede bajar por la menor reverberación, pero el valor R propio del panel no aumenta.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-band"><span>📐</span><h3>Laboratorio visual: absorción equivalente y ecuación de Sabine</h3></div>',unsafe_allow_html=True)
    formula_card("Absorción equivalente y ecuación de Sabine",
                 r"A=\sum_i S_i\alpha_i \qquad T_{60}=0{,}161\,\frac{V}{A}",
                 "<b>S</b>: superficie (m²)<br><b>α</b>: coeficiente de absorción<br><b>V</b>: volumen (m³)<br><b>A</b>: absorción equivalente (m² sabin)",
                 "Para estimar el tiempo de reverberación en un recinto de campo aproximadamente difuso.")
    c1,c2,c3=st.columns(3)
    sabine_v=c1.number_input("Volumen (m³)",50,1000,220,key="e2_sabine_v")
    sabine_base=c2.number_input("Absorción inicial (m² sabin)",5.,200.,28.,key="e2_sabine_base")
    sabine_area=c3.number_input("Área nueva (m²)",0.,300.,55.,key="e2_sabine_area")
    sabine_alpha=st.select_slider(
        "α del material en 500 Hz",
        options=[0.05,.10,.20,.35,.50,.65,.80,.95],
        value=.80,
        key="e2_sabine_alpha",
    )
    sabine_a=sabine_base+sabine_area*sabine_alpha
    sabine_t=.161*sabine_v/sabine_a
    sabine_t0=.161*sabine_v/sabine_base
    a,b,c=st.columns(3)
    a.metric("A nueva",f"{sabine_a:.1f} m² sabin")
    b.metric("T₆₀ inicial",f"{sabine_t0:.2f} s")
    c.metric("T₆₀ final",f"{sabine_t:.2f} s",delta=f"{sabine_t-sabine_t0:+.2f} s")
    if sabine_t<=.8:
        st.success("Condición didáctica favorable para habla: decaimiento rápido y mejor claridad.")
    elif sabine_t<=1.2:
        st.warning("Condición intermedia. Puede requerir más absorción según volumen y uso.")
    else:
        st.error("Reverberación alta para una actividad centrada en la palabra.")
    check(
        "e2_sabine_check",
        "Si el volumen se mantiene y se duplica A, ¿qué ocurre con T₆₀?",
        ["Se duplica","Se reduce aproximadamente a la mitad","No cambia"],
        "Se reduce aproximadamente a la mitad",
        "Sabine muestra una relación inversa entre T₆₀ y A.",
    )
    check(
        "e2_lab_1",
        "Si mantienes el mismo panel y agregas material absorbente en el recinto receptor, ¿qué cambia principalmente?",
        ["Aumenta el aislamiento R del panel","Aumenta la absorción y disminuye el T₆₀","Aumenta la transmisión por el panel"],
        "Aumenta la absorción y disminuye el T₆₀",
        "El absorbente actúa sobre las reflexiones del recinto receptor. No modifica por sí solo la propiedad aislante del panel.",
    )
    check(
        "e2_lab_2",
        "¿Qué intervención permite reducir directamente la energía que atraviesa desde el recinto emisor?",
        ["Cambiar por un panel separador de mayor aislamiento","Agregar paneles absorbentes al receptor","Reducir únicamente el T₆₀ del receptor"],
        "Cambiar por un panel separador de mayor aislamiento",
        "La transmisión entre recintos se controla mejorando la separación: masa, estanqueidad, desacoplamiento y vías laterales.",
    )

def stage3():
    header("ETAPA 3 · PREGUNTAS DE APLICACIÓN","Aislamiento, absorción y acondicionamiento acústico",
           "Responde las cinco situaciones, comprueba tu razonamiento y revisa la aclaración correspondiente.")
    st.markdown('<div class="section-band"><span>✍️</span><h3>Aplicación conceptual · responde y comprueba</h3></div>',unsafe_allow_html=True)
    questions=[
      ("s3q1","En una sala de reuniones se instalan paneles acústicos de espuma en todas las paredes. ¿Este tratamiento mejora el aislamiento acústico entre salas contiguas? Justifica tu respuesta.",
       "No de forma significativa. La espuma es principalmente absorbente: reduce reflexiones y reverberación dentro de la sala, pero su baja masa no impide eficazmente la transmisión. Para aislar se debe mejorar el cerramiento mediante masa, estanqueidad, desacoplamiento y control de fugas y flancos.",
       [["no","no mejora"],["absor","reverber"],["masa","estanque","desacopl","cerramiento"]],"Diferencia el control de reflexiones interiores del control de transmisión entre recintos."),
      ("s3q2","Se requiere reducir el eco en una oficina sin afectar la transmisión de sonido hacia otros recintos. ¿Qué tipo de tratamiento acústico se debe aplicar y por qué?",
       "Se debe aplicar acondicionamiento absorbente interior —paneles, cielo acústico o bafles— para aumentar la absorción equivalente y reducir el T₆₀. El objetivo es controlar reflexiones dentro de la oficina, no modificar el aislamiento del cerramiento.",
       [["absor","acondicion"],["eco","reflex","reverber"],["t60","tiempo de reverberación"]],"La intervención buscada actúa dentro del mismo recinto y no sobre el sonido que atraviesa la separación."),
      ("s3q3","Una persona sigue escuchando a sus vecinos a pesar de instalar paneles acústicos de espuma en su muro. ¿Cuál es el error común en la solución adoptada?",
       "El error es confundir absorción con aislamiento. La espuma puede reducir reflexiones en la habitación, pero no aporta suficiente masa ni desacoplamiento. Deben revisarse muro, puertas, ventanas, juntas, enchufes y transmisiones laterales.",
       [["confund","absorción","absorcion"],["aislamiento","transmisión","transmision"],["masa","desacopl","sell","fuga","flanco"]],"Explica por qué un material absorbente no se transforma automáticamente en un buen aislante."),
      ("s3q4","Un gimnasio necesita reducir el ruido percibido en oficinas contiguas. ¿Se deben usar materiales absorbentes o aislantes? Propón una solución adecuada.",
       "Se requieren principalmente soluciones aislantes y de control vibratorio: piso resiliente o flotante, soportes antivibratorios, cerramientos dobles desacoplados, mayor masa y sellado. Los absorbentes pueden complementar reduciendo la reverberación del gimnasio, pero no sustituyen el aislamiento.",
       [["aisl","transmis"],["vibr","piso flotante","soporte"],["doble","masa","sell","desacopl"]],"Distingue el ruido aéreo de los impactos y vibraciones que pueden viajar por la estructura."),
      ("s3q5","Se diseñan dos salas de clases. Una usa paneles absorbentes en el techo y la otra usa muros dobles entre salas. ¿Cuál solución afecta más la inteligibilidad del habla dentro de la sala y cuál mejora el aislamiento entre ellas?",
       "Los paneles absorbentes del techo reducen el T₆₀ y mejoran principalmente la inteligibilidad dentro del aula. Los muros dobles desacoplados reducen la transmisión y mejoran principalmente el aislamiento entre las salas.",
       [["panel","techo","absorb"],["intelig","reverber"],["muro doble","aislamiento","transmis"]],"Asocia cada solución con el lugar donde aparece su beneficio: dentro de la sala o al otro lado de la separación."),
    ]
    solutions={}
    for key,q,solution,groups,note in questions:
        formative_development(3,key,q,solution,groups,note); solutions[key]=solution
    score_counter(3)
    teacher_group_review(3,solutions)

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

def stage4():
    header("ETAPA 4 · MATERIA + MODELO","Aislamiento acústico y costo-beneficio",
           "La mejor solución no es la de mayor número ni la más barata: es la que cumple la meta con un costo justificable.")
    full_matter(4)
    lesson("Orden correcto de decisión","1) definir meta y espectro; 2) descartar lo que no cumple; 3) comparar costo del ciclo, vida útil, riesgo, ROI y recuperación; 4) revisar margen de seguridad.")
    formula_card("Flujo anual neto",
                 r"F_{\mathrm{neto}}=B_a-C_a",
                 "<b>F<sub>neto</sub></b>: flujo anual neto ($/año)<br>"
                 "<b>B<sub>a</sub></b>: beneficios económicos anuales o costos evitados ($/año)<br>"
                 "<b>C<sub>a</sub></b>: costos recurrentes anuales de operación, inspección y mantención ($/año)",
                 "Para determinar cuánto dinero aporta realmente la solución durante cada año, antes de calcular su período de recuperación.")
    st.markdown(
        '<div class="worked-example"><h3>¿Cómo se interpreta el flujo anual neto?</h3>'
        '<div class="worked-step"><strong>1 · Beneficios anuales.</strong> Se suman los ingresos atribuibles a la solución y los costos que permite evitar: '
        'multas, paralizaciones, reclamos, pérdida de productividad, arriendos temporales o reparaciones repetidas.</div>'
        '<div class="worked-step"><strong>2 · Costos anuales.</strong> Se descuentan únicamente los gastos que se repiten cada año: '
        'mantención, inspecciones, reposición de sellos, energía adicional u operación. La inversión inicial se analiza por separado.</div>'
        '<div class="worked-step"><strong>3 · Cálculo.</strong> Si la solución evita $700.000 al año y exige $100.000 de mantención, '
        'el flujo anual neto es $700.000 − $100.000 = <b>$600.000/año</b>.</div>'
        '<div class="worked-result"><b>Lectura del resultado:</b> un flujo positivo aporta recursos para recuperar la inversión; '
        'un flujo igual a cero no la recupera; y uno negativo significa que los costos anuales superan los beneficios anuales. '
        'El payback se calcula dividiendo la inversión inicial por este flujo positivo.</div></div>',
        unsafe_allow_html=True,
    )
    formula_card("Retorno de la inversión y período de recuperación",
                 r"ROI=\frac{B-C}{C}\,100 \qquad Payback=\frac{I_0}{B_a-M_a}",
                 "<b>B</b>: beneficio acumulado ($)<br><b>C</b>: costo total ($)<br><b>I₀</b>: inversión inicial ($)<br><b>Bₐ−Mₐ</b>: beneficio anual neto ($/año)",
                 "Después de comprobar que la alternativa cumple la meta acústica. La rentabilidad nunca reemplaza la suficiencia técnica.")
    st.markdown(
        '<div class="worked-example"><h3>Ejemplo resuelto · ¿Qué significan ROI y payback?</h3>'
        '<div class="worked-step"><strong>1 · Verificación técnica.</strong> Un encapsulamiento cuesta $2.000.000 y cumple la meta acústica. '
        'Recién ahora corresponde analizar su economía.</div>'
        '<div class="worked-step"><strong>2 · Flujo anual neto.</strong> Evita costos por $700.000 al año y requiere $100.000 de mantención. '
        'Beneficio anual neto = $700.000 − $100.000 = <b>$600.000/año</b>.</div>'
        '<div class="worked-step"><strong>3 · Payback.</strong> $2.000.000 ÷ $600.000/año = <b>3,33 años</b>. '
        'Significa que al cabo de aproximadamente 3 años y 4 meses se recupera la inversión inicial.</div>'
        '<div class="worked-step"><strong>4 · ROI a 5 años.</strong> Beneficio acumulado = $700.000 × 5 = $3.500.000. '
        'Costo total = $2.000.000 + ($100.000 × 5) = $2.500.000. '
        'ROI = ($3.500.000 − $2.500.000) ÷ $2.500.000 × 100 = <b>40 %</b>.</div>'
        '<div class="worked-result">Interpretación: al terminar los 5 años, el proyecto recuperó todos sus costos y generó un beneficio neto equivalente al 40 % del costo total. '
        'El ROI no indica cuándo se recuperó el dinero; ese dato lo entrega el payback.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Ejemplos para interpretar los indicadores")
    st.caption("Selecciona una respuesta en cada situación. Los datos son fijos para concentrar la actividad en la interpretación.")
    check(
        "e4_flow",
        "Una solución evita costos por $900.000 al año y requiere $150.000 anuales de mantención. ¿Cuál es su flujo anual neto?",
        ["$750.000/año","$900.000/año","$1.050.000/año","$150.000/año"],
        "$750.000/año",
        "Fneto = Ba − Ca = $900.000 − $150.000 = $750.000 por año.",
    )
    check(
        "e4_payback",
        "Una medida cuesta $2.400.000 y genera un flujo anual neto de $600.000. ¿Cuál es su payback?",
        ["2 años","4 años","6 años","40 %"],
        "4 años",
        "Payback = I₀/Fneto = $2.400.000/$600.000 por año = 4 años.",
    )
    check(
        "e4_roi",
        "En cinco años, una solución acumula beneficios por $4.500.000 y costos totales por $3.000.000. ¿Cuál es su ROI?",
        ["33,3 %","50 %","66,7 %","150 %"],
        "50 %",
        "ROI = (B−C)/C×100 = ($4.500.000−$3.000.000)/$3.000.000×100 = 50 %.",
    )
    check(
        "e4_decision",
        "La alternativa A tiene ROI de 70 %, pero alcanza 36 dB. La alternativa B tiene ROI de 35 % y alcanza la meta de 40 dB. ¿Cuál puede recomendarse?",
        ["Alternativa A, porque tiene mayor ROI","Alternativa B, porque primero cumple la meta","Promediar dB y ROI","Ninguna, porque el ROI debe superar 50 %"],
        "Alternativa B, porque primero cumple la meta",
        "La suficiencia acústica es el filtro inicial. La rentabilidad solo permite comparar alternativas técnicamente suficientes.",
    )

def stage5():
    header("ETAPA 5 · APLICACIÓN CONCEPTUAL","Decisión técnico-económica",
           "Compara alternativas, filtra por suficiencia acústica y encuentra el mejor compromiso.")
    full_matter(5)
    st.markdown(
        '<div class="question-box"><div class="question-label">CASO DE DECISIÓN</div>'
        '<div class="question-text">¿Cuál de las tres soluciones recomendarías para cumplir el objetivo acústico '
        'con el menor costo del ciclo? Ajusta la meta, revisa los datos de cada alternativa y justifica por qué '
        'tu elección es técnicamente suficiente antes de compararla económicamente.</div></div>',
        unsafe_allow_html=True,
    )
    st.caption("Instrucción: la meta y todos los datos son fijos. Analiza la tabla, descarta las soluciones que no cumplen y presenta tu recomendación sin modificar valores.")
    target=38
    st.info("Objetivo acústico mínimo del caso: **38 dB**")
    fixed=[
        ["Solución A",32,1200000,2640000,7200000,172.7,1.7],
        ["Solución B",40,1900000,4540000,13800000,204.0,2.0],
        ["Solución C",47,3200000,7100000,18750000,164.1,3.2],
    ]
    df=pd.DataFrame(fixed,columns=["Solución","Aislamiento","Inversión","Costo ciclo","Beneficio acumulado","ROI","Payback"])
    df["Cumple"]=df["Aislamiento"]>=target
    st.dataframe(df.style.format({"Inversión":"${:,.0f}","Costo ciclo":"${:,.0f}","Beneficio acumulado":"${:,.0f}","ROI":"{:.1f}%","Payback":"{:.1f} años"}),use_container_width=True,hide_index=True)
    feasible=df[df.Cumple]
    if feasible.empty: st.error("Ninguna alternativa cumple. No corresponde recomendar por precio o ROI.")
    else:
        best=feasible.loc[feasible["Costo ciclo"].idxmin()]
        st.success(f'Entre las alternativas suficientes, {best["Solución"]} tiene el menor costo del ciclo. La decisión final debe revisar además bandas críticas, montaje y riesgo.')
    recommendation=st.radio(
        "Selecciona la solución que recomendarías",
        ["Solución A","Solución B","Solución C"],
        index=None,
        key="s5_table_recommendation",
        horizontal=True,
    )
    justification=st.text_area(
        "Justifica tu decisión utilizando cumplimiento acústico y costo del ciclo",
        key="s5_table_justification",
        placeholder="Ejemplo: descarto… porque no cumple; entre las que cumplen selecciono… porque…",
    )
    if st.button("Comprobar decisión",key="b_s5_table_decision"):
        if recommendation is None:
            st.warning("Selecciona una solución antes de comprobar.")
        elif feasible.empty:
            st.error("Ninguna solución cumple la meta seleccionada. La decisión correcta es rediseñar las alternativas antes de recomendar una.")
        elif recommendation!=best["Solución"]:
            st.error(f'La recomendación no es la óptima con estos datos. Primero descarta las alternativas que no cumplen y, entre las suficientes, compara el costo del ciclo. La respuesta esperada es {best["Solución"]}.')
        elif len(justification.strip())<20:
            st.warning(f'{best["Solución"]} es la alternativa esperada, pero falta desarrollar la justificación técnica y económica.')
        else:
            st.success(f'Correcto. {best["Solución"]} cumple el objetivo y presenta el menor costo del ciclo entre las alternativas suficientes.')
    check("e5","Una alternativa tiene excelente ROI, pero no alcanza la meta acústica. ¿Qué corresponde?",["Elegirla por su ROI","Descartarla o rediseñarla antes de comparar economía","Promediar ROI y dB"],"Descartarla o rediseñarla antes de comparar economía","La suficiencia técnica precede a la optimización económica.")
    st.markdown('<div class="section-band"><span>🧮</span><h3>Aplicación técnico-económica · responde y comprueba</h3></div>',unsafe_allow_html=True)
    q1="Un ingeniero propone aumentar el aislamiento de una oficina de 40 dB a 50 dB. ¿Qué elementos debería considerar para decidir si esto es una buena inversión?"
    s1="Debe comprobar el nivel actual y la meta, privacidad y uso, espectro de la fuente, cumplimiento, beneficio real de 10 dB, costo del ciclo, factibilidad, puertas, ventanas, juntas y flancos, vida útil, riesgo y rendimiento decreciente. «Más dB» no basta si la mejora no es necesaria o no puede lograrse en obra."
    formative_development(5,"s5q1",q1,s1,[["meta","objetivo","norma"],["costo","inversión","inversion"],["puerta","ventana","fuga","flanco"],["beneficio","privacidad","confort"],["factib","vida útil","vida util","riesgo"]],"La decisión debe integrar suficiencia acústica, vías dominantes, costo completo y beneficio útil.")
    q2="Un sistema cuesta $1.200.000 CLP y reduce 30 dB. Otro cuesta $2.400.000 CLP y reduce 38 dB. Calcula el costo por dB de ambos e indica cuál ofrece mayor eficiencia."
    s2="Sistema 1: $1.200.000/30 = **$40.000 por dB**. Sistema 2: $2.400.000/38 = **$63.158 por dB** aproximadamente. El sistema 1 es más eficiente por este indicador, siempre que alcance la meta acústica."
    formative_numeric(5,"s5q2",q2,[("a","Sistema 1 · CLP/dB",0.0,1000.0),("b","Sistema 2 · CLP/dB",0.0,1000.0)],
        lambda v:(abs(v["a"]-40000)<=500 and abs(v["b"]-63157.9)<=600,"Los valores esperados son $40.000/dB y aproximadamente $63.158/dB; el menor costo por dB corresponde al sistema 1."),s2)
    q3="Opción A: inversión $500.000, beneficio $700.000. Opción B: inversión $1.000.000, beneficio $950.000. Calcula el ROI de ambas e identifica la mejor."
    s3="ROI A = ($700.000−$500.000)/$500.000×100 = **40 %**. ROI B = ($950.000−$1.000.000)/$1.000.000×100 = **−5 %**. La opción A tiene el mejor retorno."
    formative_numeric(5,"s5q3",q3,[("a","ROI A (%)",0.0,1.0),("b","ROI B (%)",0.0,1.0)],
        lambda v:(abs(v["a"]-40)<=0.2 and abs(v["b"]+5)<=0.2,"Se esperaba ROI A = 40 % y ROI B = −5 %. La alternativa A ofrece el mejor retorno."),s3)
    score_counter(5)
    teacher_group_review(5,{"s5q1":s1,"s5q2":s2,"s5q3":s3})

def mass_r(m,f): return 20*np.log10(np.maximum(m*f,1))-47

def stage6():
    header("ETAPA 6 · MATERIA + SIMULADORES","Fundamentos físicos del aislamiento acústico",
           "Masa, frecuencia, transmisión, coincidencia, sistemas dobles, estanqueidad y elementos débiles.")
    full_matter(6)
    tabs=st.tabs(["Transmisión y R","Ley de masa","Coincidencia","Sistemas dobles","Elementos compuestos"])
    with tabs[0]:
        formula_card("Coeficiente de transmisión y reducción sonora",
                     r"\tau=\frac{W_t}{W_i} \qquad R=10\log_{10}\left(\frac{1}{\tau}\right)",
                     "<b>Wₜ</b>: potencia transmitida (W)<br><b>Wᵢ</b>: potencia incidente (W)<br><b>τ</b>: fracción transmitida<br><b>R</b>: reducción sonora (dB)",
                     "Para relacionar físicamente la energía que atraviesa una separación con su aislamiento por banda.")
        formula_card("Despeje directo del coeficiente de transmisión",
                     r"\tau=10^{-R/10}",
                     "<b>R</b>: reducción sonora (dB)<br><b>τ</b>: fracción adimensional entre 0 y 1",
                     "Para conocer qué fracción de la energía atraviesa un elemento cuando se dispone de R.")
        R=st.slider("R (dB)",10,70,40,key="r6"); t=10**(-R/10)
        st.metric("Fracción de energía transmitida",f"{t:.8f} ({t*100:.6f} %)")
        st.markdown(
            f'<div class="worked-example"><h3>¿De dónde sale el porcentaje?</h3>'
            f'<div class="worked-step"><strong>1.</strong> La ecuación entrega una fracción decimal: '
            f'τ = 10<sup>−{R}/10</sup> = {t:.8f}.</div>'
            f'<div class="worked-step"><strong>2.</strong> Para expresarla como porcentaje se multiplica por 100: '
            f'{t:.8f} × 100 = <b>{t*100:.6f} %</b>.</div>'
            f'<div class="worked-result">Este porcentaje corresponde a energía transmitida, no a porcentaje de superficie.</div></div>',
            unsafe_allow_html=True,
        )
        st.info("Ejemplo: R = 40 dB → τ = 10⁻⁴ = 0,0001. Solo se transmite 0,01 % de la energía incidente.")
        check("e6_tau_practical","Si R = 30 dB, ¿qué porcentaje de energía se transmite?",
              ["0,001 %","0,01 %","0,1 %","3 %"],"0,1 %",
              "τ = 10⁻³ = 0,001; al multiplicar por 100 se obtiene 0,1 %.")
    with tabs[1]:
        formula_card("Ley de masa ideal para una hoja simple",
                     r"R\approx20\log_{10}(m'f)-47",
                     "<b>m′</b>: masa superficial (kg/m²)<br><b>f</b>: frecuencia (Hz)<br><b>R</b>: reducción sonora (dB)",
                     "Aproximación de campo difuso en la región controlada por masa, lejos de resonancias, coincidencia, fugas y flancos.")
        m=st.slider("Masa superficial m′ (kg/m²)",5,150,25)
        curve=mass_r(m,FREQS); curve2=mass_r(2*m,FREQS)
        line_chart(FREQS,[("m′",curve),("2·m′",curve2)],"Ley de masa ideal","R (dB)")
        st.info("Duplicar masa o frecuencia aumenta aproximadamente 6 dB en la región ideal de ley de masa.")
    with tabs[2]:
        formula_card("Frecuencia crítica de una placa",
                     r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}\qquad D=\frac{Eh^3}{12(1-\nu^2)}",
                     "<b>c</b>: velocidad del sonido (m/s)<br><b>m′</b>: masa superficial (kg/m²)<br><b>D</b>: rigidez flexional (N·m)<br><b>E</b>: módulo de Young (Pa)<br><b>h</b>: espesor (m)<br><b>ν</b>: coeficiente de Poisson",
                     "Para estimar la banda donde la coincidencia puede producir una caída del aislamiento de una placa homogénea.")
        fc=st.slider("Frecuencia crítica estimada (Hz)",100,3150,800)
        ideal=mass_r(25,FREQS); dip=ideal-12*np.exp(-.5*(np.log(FREQS/fc)/.24)**2)
        line_chart(FREQS,[("Ley de masa ideal",ideal),("Con coincidencia",dip)],"Efecto didáctico de coincidencia","R (dB)")
        st.warning("Cerca de fᶜ el panel radia con mayor eficiencia y puede aparecer una caída de aislamiento.")
    with tabs[3]:
        gap=st.slider("Cámara (mm)",20,300,80); absorb=st.checkbox("Absorbente en cámara",True)
        gain=8+min(gap/30,8)+(5 if absorb else 0)
        st.metric("Mejora didáctica sobre hoja simple",f"{gain:.1f} dB")
        st.caption("El desempeño real depende de masas, rigidez de uniones, frecuencia masa–aire–masa y puentes estructurales.")
    with tabs[4]:
        formula_card("Aislamiento de elementos compuestos",
                     r"\tau_{\mathrm{total}}=\frac{\sum_i S_i\tau_i}{\sum_i S_i}\qquad R_{\mathrm{total}}=-10\log_{10}(\tau_{\mathrm{total}})",
                     "<b>Sᵢ</b>: área del elemento i (m²)<br><b>τᵢ=10^{-Rᵢ/10}</b>: coeficiente de transmisión de cada elemento",
                     "Para combinar un muro con puertas, ventanas u otros componentes. Los aislamientos en dB no se promedian.")
        st.markdown("#### Aplicación práctica · muro con puerta")
        st.write("Datos fijos: muro de **4,0 m × 3,0 m** (12 m²), puerta de **1,0 m × 2,0 m** (2 m²), "
                 "R del paño de muro = **55 dB** y R de la puerta = **25 dB**.")
        total_area=12.0
        weak_area=2.0
        share=weak_area/total_area
        wall_area=total_area-weak_area
        wall=55
        door=25
        tau=(wall_area*10**(-wall/10)+weak_area*10**(-door/10))/total_area
        comp=-10*np.log10(tau)
        st.markdown(
            '<div class="worked-example"><h3>Cálculo del porcentaje de área débil</h3>'
            '<div class="worked-step"><strong>1 · Área total del cerramiento.</strong> 4,0 × 3,0 = <b>12 m²</b>.</div>'
            '<div class="worked-step"><strong>2 · Área de la puerta.</strong> 1,0 × 2,0 = <b>2 m²</b>.</div>'
            '<div class="worked-step"><strong>3 · Porcentaje débil.</strong> '
            '(Sdébil/Stotal) × 100 = (2/12) × 100 = <b>16,7 %</b>.</div>'
            '<div class="worked-result">En la ecuación se usa la fracción 2/12 = 0,1667. '
            'El área útil del muro es 12−2 = 10 m²; la puerta no se suma nuevamente al total.</div></div>',
            unsafe_allow_html=True,
        )
        st.metric("R compuesto",f"{comp:.1f} dB")
        st.info("Los dB no se promedian: se combinan coeficientes de transmisión ponderados por superficie.")
        check("e6_area_practical","¿Qué porcentaje del cerramiento corresponde a la puerta?",
              ["12,0 %","16,7 %","20,0 %","2,0 %"],"16,7 %",
              "El porcentaje se obtiene desde las áreas geométricas: (2 m²/12 m²)×100 = 16,7 %.")
        check("e6_comp_practical",f"Al combinar energéticamente ambos elementos, el resultado es aproximadamente {comp:.1f} dB. ¿Por qué queda mucho más cerca de la puerta que del muro?",
              ["Porque se promediaron 55 y 25 dB","Porque la puerta tiene un τ mucho mayor y domina la energía transmitida","Porque la puerta ocupa más superficie que el muro"],
              "Porque la puerta tiene un τ mucho mayor y domina la energía transmitida",
              "Aunque solo ocupa 16,7 % del área, la puerta transmite mucha más energía por metro cuadrado. Por eso los coeficientes τ se ponderan por superficie.")
    check(
        "e6",
        "Si se duplica la masa superficial de un panel dentro de la región ideal de la ley de masa, ¿qué mejora aproximada se espera?",
        ["3 dB","6 dB","10 dB","El aislamiento no cambia"],
        "6 dB",
        "La ley de masa ideal predice aproximadamente 6 dB de aumento de R al duplicar la masa superficial, para una misma frecuencia.",
    )

def stage7():
    header("ETAPA 7 · APLICACIÓN PRÁCTICA","Diseño de aislamiento acústico",
           "Aplica las ecuaciones de la etapa anterior siguiendo una ruta de cálculo clara y verificable.")
    full_matter(7)
    st.markdown(
        '<div class="question-box"><div class="question-label">CASO GUIADO · MURO CON PUERTA</div>'
        '<div class="question-text">Una sala emisora tiene 82 dB. La separación mide 15 m² e incorpora una puerta de 2 m². '
        'El muro tiene R = 50 dB y la puerta R = 30 dB. Calcula el área débil, el aislamiento compuesto y el nivel estimado en el receptor. '
        'Luego decide si cumple la meta de 45 dB.</div></div>',
        unsafe_allow_html=True,
    )
    st.caption("Todos los datos son fijos. Resuelve cada paso y comprueba antes de continuar.")
    source=82.0
    target=45.0
    total_area=15.0
    weak_area=2.0
    wall_area=total_area-weak_area
    r_wall=50.0
    r_weak=30.0
    weak_pct=100*weak_area/total_area
    tau_wall=10**(-r_wall/10)
    tau_weak=10**(-r_weak/10)
    tau_total=(wall_area*tau_wall+weak_area*tau_weak)/total_area
    r_total=-10*math.log10(tau_total)
    receiver=source-r_total
    case_df=pd.DataFrame([
        ["Nivel emisor",f"{source:.0f} dB"],
        ["Área total",f"{total_area:.0f} m²"],
        ["Área de puerta",f"{weak_area:.0f} m²"],
        ["Área efectiva de muro",f"{wall_area:.0f} m²"],
        ["R muro",f"{r_wall:.0f} dB"],
        ["R puerta",f"{r_weak:.0f} dB"],
        ["Meta en receptor",f"≤ {target:.0f} dB"],
    ],columns=["Dato","Valor"])
    st.dataframe(case_df,hide_index=True,use_container_width=True)
    st.markdown(
        '<div class="worked-example"><h3>Origen de las áreas y porcentajes</h3>'
        '<div class="worked-step">El área total de 15 m² corresponde a toda la separación, incluida la puerta.</div>'
        '<div class="worked-step">Área efectiva del muro = 15−2 = <b>13 m²</b>.</div>'
        '<div class="worked-step">Porcentaje de puerta = (2/15)×100 = <b>13,3 %</b>. '
        'En la ecuación se usa 2/15 = 0,1333.</div></div>',
        unsafe_allow_html=True,
    )
    check("e7_guided_area","¿Qué porcentaje del área total ocupa la puerta?",
          ["7,5 %","13,3 %","15,0 %","20,0 %"],"13,3 %",
          "Se obtiene de los datos geométricos del caso: (2 m²/15 m²)×100 = 13,3 %.")
    check("e7_guided_tau","¿Qué coeficientes de transmisión corresponden al muro y a la puerta?",
          ["τmuro=10⁻⁵ y τpuerta=10⁻³","τmuro=50 y τpuerta=30","τmuro=0,50 y τpuerta=0,30"],
          "τmuro=10⁻⁵ y τpuerta=10⁻³",
          "Se aplica τ=10^(−R/10): para 50 dB resulta 10⁻⁵ y para 30 dB resulta 10⁻³.")
    st.latex(rf"\tau_{{total}}=\frac{{13(10^{{-5}})+2(10^{{-3}})}}{{15}}={tau_total:.6f}")
    st.latex(rf"R_{{total}}=-10\log_{{10}}(\tau_{{total}})={r_total:.1f}\ \mathrm{{dB}}")
    check("e7_guided_result",f"Con Rtotal ≈ {r_total:.1f} dB, ¿cuál es el nivel receptor estimado y cumple la meta?",
          [f"{receiver:.1f} dB; sí cumple",f"{receiver:.1f} dB; no cumple","32,0 dB; sí cumple","52,0 dB; no cumple"],
          f"{receiver:.1f} dB; sí cumple",
          f"Lreceptor = 82−{r_total:.1f} = {receiver:.1f} dB. Como es menor o igual que 45 dB, el caso cumple.")
    st.markdown(
        '<div class="good"><b>Lectura profesional:</b> el procedimiento siempre sigue la misma ruta: '
        'áreas → porcentajes → τ de cada elemento → τ ponderado → R compuesto → comparación con la meta.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-band"><span>🧪</span><h3>Aplicación conceptual III · 11 ejercicios</h3></div>',unsafe_allow_html=True)
    solutions={}
    q="En un ensayo simplificado, el nivel medio en el recinto emisor es 85 dB y en el receptor es 45 dB. Sin aplicar correcciones de recinto, calcula R."
    s="Aplicación simplificada: **R = L₁ − L₂ = 85 − 45 = 40 dB**. En un ensayo normalizado real se incorporan las correcciones y condiciones definidas por el método."
    formative_numeric(7,"s7q1",q,[("r","R (dB)",0.0,1.0)],lambda v:(abs(v["r"]-40)<.1,"R debe ser 40 dB: resta nivel receptor al nivel emisor."),s);solutions["s7q1"]=s
    q="Para un elemento con R = 40 dB, calcula el coeficiente de transmisión τ."
    s="**τ = 10^(−R/10) = 10⁻⁴ = 0,0001**, equivalente a 0,01 % de la energía incidente."
    formative_numeric(7,"s7q2",q,[("tau","τ",0.0,0.0001)],lambda v:(abs(v["tau"]-0.0001)<=0.00001,"τ debe ser 0,0001."),s);solutions["s7q2"]=s
    q="Aplica la ley de masa ideal para m′ = 30 kg/m² y f = 500 Hz. Calcula R."
    expected=20*math.log10(30*500)-47
    s=f"**R ≈ 20 log₁₀(30×500) − 47 = {expected:.1f} dB**. Es una aproximación válida solo en la región controlada por masa."
    formative_numeric(7,"s7q3",q,[("r","R (dB)",0.0,0.1)],lambda v:(abs(v["r"]-expected)<=0.3,f"El resultado esperado es aproximadamente {expected:.1f} dB."),s);solutions["s7q3"]=s
    q="Una placa tiene E = 2,5 GPa, h = 12 mm, ν = 0,30, m′ = 9,6 kg/m² y c = 343 m/s. Calcula primero D y luego fᶜ."
    s="Con unidades SI: **D = Eh³/[12(1−ν²)] = 395,6 N·m**. Luego, **fᶜ = c²/(2π)√(m′/D) ≈ 2.917 Hz**."
    formative_numeric(7,"s7q4",q,[("d","D (N·m)",0.0,1.0),("fc","fᶜ (Hz)",0.0,10.0)],
        lambda v:(abs(v["d"]-395.6)<=3 and abs(v["fc"]-2917)<=25,"Se esperaba D ≈ 395,6 N·m y fᶜ ≈ 2.917 Hz. Verifica convertir 12 mm a 0,012 m."),s);solutions["s7q4"]=s
    q="Un recinto posee 60 m² de superficie con α = 0,10 y agrega 25 m² de material con α = 0,80. Calcula la absorción equivalente total."
    s="**A = 60×0,10 + 25×0,80 = 6 + 20 = 26 m² sabin**."
    formative_numeric(7,"s7q5",q,[("a","A total (m² sabin)",0.0,1.0)],lambda v:(abs(v["a"]-26)<.1,"La absorción equivalente total es 26 m² sabin."),s);solutions["s7q5"]=s
    q="Compara dos ventanas: A tiene Rw = 40 dB y B tiene Rw = 35 dB. ¿Cuál transmite menos energía y cuántas veces difieren aproximadamente sus coeficientes τ?"
    s="La ventana A transmite menos. Una diferencia de 5 dB corresponde a una razón de transmisión de **10^(5/10) ≈ 3,16**: B transmite aproximadamente 3,16 veces más energía que A."
    formative_development(7,"s7q6",q,s,[["a","40"],["menos","menor"],["3,16","3.16","tres"]],"No compares los dB como una razón lineal: convierte la diferencia mediante 10^(ΔR/10).");solutions["s7q6"]=s
    q="¿Qué ocurre idealmente con R cuando se duplica la masa superficial de una hoja simple?"
    s="En la región ideal controlada por masa, **R aumenta aproximadamente 6 dB**. No es una regla universal cerca de resonancias, coincidencia, fugas o flancos."
    formative_development(7,"s7q7",q,s,[["6","seis"],["masa"],["ideal","coincid","resonan","aproxim"]],"Indica tanto la mejora aproximada como las condiciones que limitan la ley de masa.");solutions["s7q7"]=s
    q="¿Qué función cumple la lana mineral dentro de un tabique de doble hoja?"
    s="Absorbe y amortigua la energía dentro de la cámara, reduce la severidad de resonancias y mejora el sistema. **No aporta aislamiento por sí sola ni sustituye el desacoplamiento**, la masa o el sellado."
    formative_development(7,"s7q8",q,s,[["absor","amort"],["cámara","camara","resonan"],["no","desacopl","masa"]],"Evita atribuirle a la lana mineral toda la capacidad aislante del tabique.");solutions["s7q8"]=s
    q="Un muro de alto aislamiento incorpora una ventana pequeña de bajo R. ¿Cómo puede afectar esa ventana al aislamiento global?"
    s="Puede dominar el resultado global porque su τ es mucho mayor que el del muro. Se deben combinar los coeficientes de transmisión ponderados por área; **no se promedian los dB**."
    formative_development(7,"s7q9",q,s,[["domina","reduce","debil"],["coeficiente","tau","transmis"],["área","area"],["no","promedi"]],"Explica por qué una superficie pequeña puede transportar una fracción grande de la energía.");solutions["s7q9"]=s
    q="El muro separador fue mejorado, pero el ruido sigue llegando por la unión con el cielo y el piso. ¿Qué fenómeno ocurre y cómo se aborda?"
    s="Existe **transmisión indirecta o por flancos**. Deben diagnosticarse los encuentros y vías estructurales, controlar continuidades rígidas, sellar pasos y diseñar el conjunto constructivo, no solo el paño separador."
    formative_development(7,"s7q10",q,s,[["flanco","indirect"],["cielo","piso","encuentro"],["vía","via","estructura","sell"]],"Nombra la trayectoria real y propone una intervención sobre ese encuentro.");solutions["s7q10"]=s
    q="Un muro de 12 m² tiene R = 55 dB e incorpora una puerta de 2 m² con R = 25 dB. Calcula el R compuesto."
    tau_total=(12*10**(-55/10)+2*10**(-25/10))/14
    r_total=-10*math.log10(tau_total)
    s=f"τtotal = [12·10^(−55/10)+2·10^(−25/10)]/14. Por tanto, **Rtotal ≈ {r_total:.1f} dB**. La puerta reduce drásticamente el desempeño del conjunto."
    formative_numeric(7,"s7q11",q,[("r","R compuesto (dB)",0.0,0.1)],
        lambda v:(abs(v["r"]-r_total)<=0.3,f"El resultado esperado es aproximadamente {r_total:.1f} dB; combina τ ponderados por superficie."),s);solutions["s7q11"]=s
    score_counter(7)
    teacher_group_review(7,solutions)

REF=np.array([33,36,39,42,45,48,51,52,53,54,55,56,56,56,56,56])
def rw_from_curve(curve):
    best=None
    for shift in range(-30,31):
        ref=REF+shift; dev=np.maximum(ref-curve,0)
        if dev.sum()<=32: best=(int(ref[7]),ref,dev)
    return best

def stage8():
    header("ETAPA 8 · MATERIA + INTERPRETACIÓN","Índices de aislamiento acústico",
           "Los números únicos permiten comparar, pero deben corresponder al método, lugar y espectro del problema.")
    full_matter(8)
    data=[
      ("R(f)","Reducción por banda","Laboratorio/curva"),
      ("Rw","Reducción ponderada","Laboratorio ISO"),
      ("R′w","Reducción aparente","Terreno, incluye vías laterales"),
      ("DₙT,w","Diferencia estandarizada","Entre recintos, corregida por T"),
      ("D₂m,nT,w","Diferencia de fachada","Exterior a 2 m"),
      ("STC / ASTC","Clasificación ASTM","Laboratorio / terreno"),
      ("OITC","Exterior–interior","Transporte y bajas frecuencias"),
      ("CAC","Paso por cielo/plenum","Cielos suspendidos"),
    ]
    st.dataframe(pd.DataFrame(data,columns=["Indicador","Representa","Contexto"]),hide_index=True,use_container_width=True)
    formula_card("Índice ponderado y términos de adaptación",
                 r"R_w(C;C_{tr})=52(-2;-7)\,\mathrm{dB}\Rightarrow R_w+C=50\,\mathrm{dB},\;R_w+C_{tr}=45\,\mathrm{dB}",
                 "<b>Rw</b>: valor ponderado ISO<br><b>C</b>: adaptación para espectros medios-altos<br><b>Ctr</b>: adaptación para tránsito y contenido grave",
                 "Para adaptar el índice global al espectro de la fuente. C y Ctr se suman algebraicamente; no son aislamientos independientes.")
    source=st.selectbox("Fuente a evaluar",["Voz / actividades domésticas","Tránsito, buses o bajos","Fachada bajo criterio ASTM","Fuente tonal industrial"])
    recommendation={"Voz / actividades domésticas":"Revisar Rw y Rw+C.","Tránsito, buses o bajos":"Priorizar Rw+Cₜᵣ y la curva grave.",
    "Fachada bajo criterio ASTM":"Revisar OITC además de STC.","Fuente tonal industrial":"La curva completa en la banda tonal es indispensable."}[source]
    st.info(recommendation)
    check("e8","Un tabique tiene Rw=55 dB en laboratorio y R′w=47 dB en obra. ¿El laboratorio estaba necesariamente equivocado?",["Sí","No; montaje y vías laterales pueden explicar la diferencia"],"No; montaje y vías laterales pueden explicar la diferencia","R′w incorpora el comportamiento aparente de la construcción instalada.")

def stage9():
    header("ETAPA 9 · APLICACIÓN PRÁCTICA","Interpretación de índices acústicos",
           "Relaciona cada índice con su definición, contexto de medición y uso correcto.")
    full_matter(9)
    st.markdown("### Actividad · Relaciona los términos pareados")
    st.markdown(
        "En la columna izquierda aparecen los índices acústicos. En la derecha están las definiciones "
        "numeradas y mezcladas. Selecciona junto a cada índice el número que le corresponde."
    )
    paired_terms = {
        "R": "Índice por banda de frecuencia que expresa la reducción sonora de un elemento en laboratorio.",
        "R_w": "Índice único ponderado ISO obtenido al ajustar una curva de referencia a resultados de laboratorio.",
        "R′_w": "Índice único aparente medido en obra, que incorpora montaje, encuentros y transmisiones laterales.",
        "D_nT,w": "Diferencia de niveles entre recintos, normalizada por el tiempo de reverberación y ponderada.",
        "D_2m,nT,w": "Diferencia de niveles de fachada medida con el nivel exterior a 2 m, normalizada y ponderada.",
        "C": "Término de adaptación espectral asociado principalmente a ruido rosa y fuentes de contenido medio-alto.",
        "Cₜᵣ": "Término de adaptación espectral apropiado para tránsito y fuentes con contenido importante en bajas frecuencias.",
        "STC": "Clasificación ASTM de número único usada principalmente para particiones interiores.",
        "OITC": "Clasificación ASTM orientada al aislamiento frente a ruido exterior, especialmente transporte.",
        "CAC": "Clasificación del aislamiento entre recintos que comparten un cielo suspendido y plenum.",
    }
    definitions = list(paired_terms.values())
    mixed_order=[7,2,5,0,8,3,9,1,6,4]
    numbered_definitions={number:definitions[source_index] for number,source_index in enumerate(mixed_order,1)}
    correct_numbers={
        term:next(number for number,definition in numbered_definitions.items() if definition==correct_definition)
        for term,correct_definition in paired_terms.items()
    }
    placeholder = "—"
    selections = {}
    left,right=st.columns([.85,2.15],gap="large")
    with left:
        st.markdown("#### Índices o descriptores")
        for idx,term in enumerate(paired_terms):
            row_label,row_value=st.columns([1.2,.8])
            row_label.markdown(f"**{term}**")
            selections[term]=row_value.selectbox(
                f"Número para {term}",[placeholder]+list(range(1,11)),
                key=f"e9_pair_number_{idx}",label_visibility="collapsed",
            )
    with right:
        st.markdown("#### Definiciones numeradas")
        for number,definition in numbered_definitions.items():
            st.markdown(
                f'<div class="card" style="margin:.28rem 0;padding:.72rem .9rem">'
                f'<b style="color:#0871bd">{number}.</b> {definition}</div>',
                unsafe_allow_html=True,
            )
    if st.button("Comprobar términos pareados",key="e9_check_pairs",type="primary"):
        unanswered=[term for term,value in selections.items() if value==placeholder]
        if unanswered:
            st.warning(f"Completa todas las relaciones. Faltan: {', '.join(unanswered)}.")
        else:
            correct_count=sum(selections[term]==correct_numbers[term] for term in paired_terms)
            pair_score=correct_count*2
            level="Correcta" if correct_count==len(paired_terms) else "Parcialmente correcta" if correct_count>=4 else "Incorrecta"
            _save_formative(
                9,"e9_pairs","Relaciona cada índice acústico con su definición.",
                json.dumps(selections,ensure_ascii=False),level,
                f"{correct_count} de {len(paired_terms)} relaciones correctas.",
                score=pair_score,max_score=20,
            )
            if correct_count==len(paired_terms):
                st.success("¡Correcto! Relacionaste adecuadamente los 10 términos acústicos.")
            else:
                st.warning(f"Obtuviste {correct_count} de {len(paired_terms)} relaciones correctas.")
                for term,correct_definition in paired_terms.items():
                    if selections[term]!=correct_numbers[term]:
                        st.error(
                            f"{term}: la relación seleccionada no corresponde. "
                            f"El número correcto es {correct_numbers[term]}: {correct_definition}",
                            icon="↔️",
                        )
            repeated={number for number in range(1,11) if list(selections.values()).count(number)>1}
            if repeated:
                st.info(f"Revisa los números repetidos ({', '.join(map(str,sorted(repeated)))}): cada definición se utiliza una sola vez.")
    score_counter(9)
    if st.session_state.get("role")=="Docente":
        with st.expander("👩‍🏫 Pauta docente · Términos pareados"):
            st.markdown(
                "Proyecte primero las relaciones sin revelar la pauta. Pida que el curso justifique "
                "especialmente las diferencias entre laboratorio, obra, recintos y fachada."
            )
            if st.checkbox("Mostrar solución de términos pareados",key="e9_reveal_pairs"):
                st.dataframe(
                    pd.DataFrame(
                        [{"Término":term,"N.º correcto":correct_numbers[term],"Definición correcta":definition}
                         for term,definition in paired_terms.items()]
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
                st.info(
                    "Tip técnico: la prima en R′w identifica desempeño aparente en obra; "
                    "el subíndice 2m identifica fachada; nT indica normalización por reverberación. "
                    "C y Cₜᵣ no son índices independientes: se suman algebraicamente a Rw."
                )
        teacher_group_review(9,{"e9_pairs":"Cada uno de los 10 términos debe asociarse una sola vez con la definición mostrada en la pauta docente."})

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

def stage10():
    header("ETAPA 10 · EVALUACIÓN FINAL","Evaluación práctica final · Aislamiento a Ruido Aéreo",
           "30 preguntas: 29 teórico-aplicadas y un caso integrador con costo-beneficio.")
    full_matter(10)
    if "exam_answers" not in st.session_state: st.session_state.exam_answers={}
    tab1,tab2=st.tabs(["Preguntas 1 a 29","Pregunta 30 · Caso práctico"])
    with tab1:
        qn=st.selectbox("Pregunta",range(29),format_func=lambda i:f"Pregunta {i+1}")
        q,opts,correct=QUESTIONS[qn]
        st.markdown(f'<div class="question-box"><div class="question-label">PREGUNTA {qn+1} DE 29</div><div class="question-text">{q}</div></div>',unsafe_allow_html=True)
        ans=st.radio("Selecciona una alternativa",opts,index=None,key=f"q{qn}",label_visibility="collapsed")
        if st.button("Guardar respuesta",key=f"save{qn}"):
            if ans is None: st.warning("Selecciona una alternativa.")
            else: st.session_state.exam_answers[qn]=opts.index(ans);st.success("Respuesta guardada.")
        st.progress(len(st.session_state.exam_answers)/29)
    with tab2:
        st.markdown('<div class="question-box"><div class="question-label">PREGUNTA 30 · CASO PROFESIONAL INTEGRADOR</div><div class="question-text">¿Qué solución recomendarías para proteger un dormitorio contiguo a una sala de máquinas?</div><p>La fuente domina en 125, 250 y 500 Hz. Calcula, compara y justifica tu decisión técnico-económica.</p></div>',unsafe_allow_html=True)
        df=pd.DataFrame({
          "Indicador":["Rw","Cₜᵣ","Rw+Cₜᵣ","R en 125 Hz","R en 250 Hz","R en 500 Hz","Costo instalado","Vida útil"],
          "Solución A":["52 dB","−9 dB","43 dB","27 dB","34 dB","47 dB","$1.800.000","20 años"],
          "Solución B":["49 dB","−4 dB","45 dB","34 dB","39 dB","45 dB","$2.100.000","25 años"]})
        st.dataframe(df,hide_index=True,use_container_width=True)
        c1,c2=st.columns(2);V=c1.number_input("V (m³)",1.,500.,50.);A=c2.number_input("A (m² sabin)",1.,200.,20.)
        calc=st.number_input("Calcula T₆₀ (s)",0.,10.,0.,.01)
        diff=st.number_input("Diferencia de costo ($)",0,5000000,0,step=50000)
        pct=st.number_input("Incremento porcentual de B respecto de A (%)",0.,200.,0.,.1)
        bands=st.multiselect("Bandas críticas",[125,250,500,1000])
        choice=st.radio("Recomendación",["Solución A","Solución B"],index=None)
        justification=st.text_area("Justificación técnico-económica")
        if st.button("Finalizar y corregir evaluación",type="primary"):
            theory=sum(st.session_state.exam_answers.get(i)==QUESTIONS[i][2] for i in range(29))
            practical=0
            practical+=3 if abs(calc-.4025)<=.03 else 0
            practical+=2 if set(bands)=={125,250,500} else 0
            practical+=3 if choice=="Solución B" else 0
            practical+=2 if abs(diff-300000)<=10000 else 0
            practical+=2 if abs(pct-16.7)<=.5 else 0
            words=justification.lower()
            practical+=4 if all(k in words for k in ["costo","125"]) else 2 if justification.strip() else 0
            practical+=4 if any(k in words for k in ["vida útil","cumple","objetivo","grave","250"]) else 0
            total=theory/29*80+practical
            st.session_state.exam_result=(theory,practical,total)
            level="Correcta" if total>=60 else "Incorrecta"
            _save_formative(
                10,"final_exam","Evaluación final del Curso 1",
                json.dumps(
                    {"respuestas_teoricas":st.session_state.exam_answers,
                     "aciertos_teoricos":theory,"puntaje_caso":practical},
                    ensure_ascii=False,
                ),
                level,
                f"Teoría: {theory}/29 aciertos. Caso práctico: {practical}/20 puntos.",
                score=total,max_score=100,
            )
    if "exam_result" in st.session_state:
        theory,practical,total=st.session_state.exam_result
        st.markdown(f'<div class="good"><b>Resultado: {total:.1f}/100</b><br>Teoría: {theory}/29 aciertos, ponderados a 80 puntos. Caso práctico: {practical}/20 puntos.<br>{"APROBADO" if total>=60 else "REQUIERE REFORZAMIENTO"}</div>',unsafe_allow_html=True)
        st.info("Respuesta esperada: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; bandas 125, 250 y 500 Hz; Solución B por mejor respuesta grave, mejor Rw+Cₜᵣ y mayor vida útil. Si ambas cumplieran holgadamente la meta, A podría ser suficiente.")
    score_counter(10)
    teacher_group_review(
        10,
        {"final_exam":"La evaluación suma 80 puntos teóricos y 20 puntos del caso integrador. "
         "La aprobación interna se alcanza con 60/100; el docente puede revisar y ajustar el puntaje con fundamento."},
    )

def login():
    institutional_header()
    header("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN","Laboratorio · Aislamiento a Ruido Aéreo","Ingresa como alumno o docente para acceder a la plataforma.")
    role=st.radio("Perfil",["Alumno","Docente"],horizontal=True)
    name=st.text_input("Nombre completo")
    if role=="Alumno":
        rut=st.text_input("RUT o identificación");email=st.text_input("Correo")
        valid=name.strip() and rut.strip() and "@" in email
    else:
        password=st.text_input("Clave docente",type="password")
        try:
            teacher_password=str(st.secrets["teacher"]["password"])
        except (KeyError, FileNotFoundError):
            teacher_password="docente123"
        valid=name.strip() and password==teacher_password
    if st.button("Ingresar",type="primary",use_container_width=True):
        if valid: st.session_state.update(access=True,role=role,name=name);st.rerun()
        else: st.error("Completa correctamente los datos de acceso.")

if not st.session_state.get("access"):
    login();st.stop()

with st.sidebar:
    uc=ROOT/"assets/logos/logo_uc.png";decon=ROOT/"assets/logos/logo_decon_uc.png"
    if uc.exists(): st.image(str(uc),width=75)
    if decon.exists(): st.image(str(decon),width=130)
    st.markdown("## ◉ LABORATORIO")
    st.caption("AISLAMIENTO A RUIDO AÉREO")
    st.caption("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN")
    st.markdown(f"**{st.session_state.name}**  \n{st.session_state.role}")
    score_counter(compact=True)
    labels=[f"{n} · {t} · {STAGE_MINUTES[i]} min" for i,(n,t) in enumerate(STAGES)]
    selected=st.radio("Ruta de aprendizaje",labels,label_visibility="collapsed")
    if st.button("Cerrar sesión",use_container_width=True):
        st.session_state.clear();st.rerun()
    st.caption("Docente: Marco Araos Barría")

idx=labels.index(selected)
[stage0,stage1,stage2,stage3,stage4,stage5,stage6,stage7,stage8,stage9,stage10][idx]()
