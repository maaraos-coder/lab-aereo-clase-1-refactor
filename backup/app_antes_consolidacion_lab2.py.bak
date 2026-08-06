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
from student_results import release_controls, results_view

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
try:
    from supabase import create_client
except ImportError:
    create_client = None
try:
    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    import matplotlib.pyplot as plt
except ImportError:
    ezdxf = Frontend = RenderContext = MatplotlibBackend = plt = None

st.set_page_config(page_title="Laboratorio | Aislamiento a Ruido Aéreo", page_icon="🔊", layout="wide")
ROOT = Path(__file__).parent
FREQS = np.array([100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150])
ACTIVITY_DB = ROOT / "formative_responses.sqlite3"
COURSE_ID = "diplomado-acustica-edificacion"
SANTIAGO_TZ = ZoneInfo("America/Santiago")
ACADEMIC_COURSES = [
    {
        "title": "Aislamiento acústico al ruido aéreo",
        "labs": [
            {"number": 1, "opens_at": "2026-07-25T00:00:00-04:00", "implemented": True},
            {"number": 2, "opens_at": "2026-07-31T00:00:00-04:00", "implemented": True},
        ],
    },
    {
        "title": "Control de ruido de impacto y ruido de instalaciones",
        "labs": [
            {"number": 1, "opens_at": "2026-08-22T00:00:00-04:00", "implemented": False},
            {"number": 2, "opens_at": "2026-08-29T00:00:00-04:00", "implemented": False},
        ],
    },
    {
        "title": "Control de ruido ambiental",
        "labs": [
            {"number": 1, "opens_at": "2026-09-12T00:00:00-03:00", "implemented": False},
            {"number": 2, "opens_at": "2026-09-26T00:00:00-03:00", "implemented": False},
        ],
    },
    {
        "title": "Factores del ruido en el proceso de construcción",
        "labs": [
            {"number": 1, "opens_at": "2026-10-10T00:00:00-03:00", "implemented": False},
            {"number": 2, "opens_at": "2026-10-17T00:00:00-03:00", "implemented": False},
        ],
    },
    {
        "title": "Certificaciones acústicas en la edificación residencial",
        "labs": [
            {"number": 1, "opens_at": "2026-11-07T00:00:00-03:00", "implemented": False},
            {"number": 2, "opens_at": "2026-11-14T00:00:00-03:00", "implemented": False},
        ],
    },
]
LABORATORIES = {
    1: {
        "id": "clase-01-aislamiento-ruido-aereo",
        "title": "Laboratorio 1",
        "description": "",
        "stages": list(range(11)),
    },
    2: {
        "id": "clase-02-aislamiento-ruido-aereo-minvu",
        "title": "Laboratorio 2",
        "description": "",
        "stages": list(range(11)),
    },
}
if st.query_params.get("lab") in ("1","2"):
    st.session_state["active_lab"]=int(st.query_params["lab"])
ACTIVE_LAB = int(st.session_state.get("active_lab", 1))
CLASS_ID = LABORATORIES[ACTIVE_LAB]["id"]
CLASS_NUMBER = ACTIVE_LAB
APPLICATION_POINTS = {
    3: {"s3q1": 2, "s3q2": 2, "s3q3": 2, "s3q4": 2, "s3q5": 2},
    5: {"s5q1": 4, "s5q2": 3, "s5q3": 3},
    7: {"minvu_guided": 20, "s7q1": 2, "s7q2": 2, "s7q3": 2, "s7q4": 2, "s7q5": 2, "s7q6": 2, "s7q7": 2, "s7q8": 2, "s7q9": 1, "s7q10": 1, "s7q11": 2},
    9: {"e9_pairs": 20},
    10: {"final_exam": 100},
}
APPLICATION_TOTAL = sum(sum(stage.values()) for stage in APPLICATION_POINTS.values())
LAB_POINT_SCHEMAS = {
    1: {stage: APPLICATION_POINTS[stage] for stage in [3, 5, 7, 9, 10]},
    2: {
        6: {"direccion_guiada": 10},
        7: {"compare_solutions": 10},
        8: {"compound_door": 10},
        9: {"final_comprehension": 40},
        10: {"final_integrated_design": 60},
    },
}
LAB_ACTIVITY_STAGES = {1: [3, 5, 7, 9], 2: [6, 7, 8]}
FINAL_EXAM_STAGE = 10

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
[data-testid="stSidebar"] [data-baseweb="select"]>div,
[data-testid="stSidebar"] [data-baseweb="input"]>div,
[data-testid="stSidebar"] [data-baseweb="textarea"]>div,
[data-testid="stSidebar"] [data-testid="stNumberInput"]>div>div{
 background:#f8fbff!important;border:1px solid #8db4d4!important;color:#102a43!important;
 box-shadow:0 1px 2px rgba(0,24,54,.12)!important
}
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="input"] *,
[data-testid="stSidebar"] [data-baseweb="textarea"] *,
[data-testid="stSidebar"] [data-testid="stNumberInput"] *{
 color:#102a43!important;-webkit-text-fill-color:#102a43!important
}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] textarea{
 background:#f8fbff!important;color:#102a43!important;-webkit-text-fill-color:#102a43!important;
 caret-color:#102a43!important
}
[data-testid="stSidebar"] input::placeholder,[data-testid="stSidebar"] textarea::placeholder{
 color:#607d98!important;-webkit-text-fill-color:#607d98!important;opacity:1!important
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] button{
 background:#dcecf8!important;border-color:#8db4d4!important
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] button svg,
[data-testid="stSidebar"] [data-baseweb="select"] svg{fill:#173f5f!important;color:#173f5f!important}
[data-testid="stSidebar"] button[kind="secondary"]{
 background:#0b669c!important;border:1px solid #5ed8f0!important;color:#fff!important
}
[data-testid="stSidebar"] button[kind="secondary"] *{color:#fff!important;-webkit-text-fill-color:#fff!important}
[data-testid="stSidebar"] [data-testid="stLinkButton"] a,
[data-testid="stSidebar"] .stButton>button,
[data-testid="stSidebar"] [data-testid="stExpander"] summary{
background:#0b4f83!important;border:1px solid #59d4ef!important;color:#fff!important;box-shadow:none!important}
[data-testid="stSidebar"] [data-testid="stLinkButton"] a *,
[data-testid="stSidebar"] .stButton>button *,
[data-testid="stSidebar"] [data-testid="stExpander"] summary *{color:#fff!important}
[data-testid="stSidebar"] [data-testid="stLinkButton"] a:hover,
[data-testid="stSidebar"] .stButton>button:hover,
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover{
background:#0878bd!important;border-color:#8ee9ff!important}
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
.separator{background:#25374a;display:flex;align-items:center;justify-content:center;color:white;font-size:.72rem;writing-mode:vertical-rl;font-weight:800}
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
.mini-source,.mini-receiver,.mini-separator,.mini-wave,.mini-floorwave{position:absolute}.mini-source{left:8%;bottom:17%;font-size:3.3rem}
.mini-receiver{right:8%;bottom:17%;font-size:3.2rem}.mini-wave{left:30%;top:39%;color:#0877c5;font-size:1.7rem;font-weight:900}
.mini-separator{left:48%;bottom:10%;height:70%;width:18px;background:#344b60;border-radius:4px}.mini-floorwave{left:25%;right:23%;bottom:8%;border-bottom:5px dashed #ef8b2c}
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

def header(kicker,title,desc,show_overview=True,duration_minutes=None):
    match=re.search(r"ETAPA\s+(\d+)",kicker)
    stage_number=int(match.group(1)) if match else None
    minutes = duration_minutes if duration_minutes is not None else STAGE_MINUTES.get(stage_number)
    duration=(f'<div class="time-badge">⏱️ Tiempo de aplicación: {minutes} minutos</div>'
              if minutes is not None else "")
    st.markdown(f'<div class="hero"><span class="tag">{kicker}</span><h1>{title}</h1><p>{desc}</p>{duration}</div>',unsafe_allow_html=True)
    if match and show_overview:
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
    con.execute(
        """CREATE TABLE IF NOT EXISTS projection_state(
        id INTEGER PRIMARY KEY CHECK(id=1), stage INTEGER, question TEXT,
        answer TEXT, solution TEXT, show_answer INTEGER DEFAULT 0,
        show_solution INTEGER DEFAULT 0, updated_at TEXT)"""
    )
    con.execute(
        """INSERT OR IGNORE INTO projection_state
        (id,stage,question,answer,solution,show_answer,show_solution,updated_at)
        VALUES(1,NULL,'','','',0,0,'')"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS user_progress(
        user_key TEXT PRIMARY KEY, role TEXT NOT NULL, display_name TEXT NOT NULL,
        state_json TEXT NOT NULL DEFAULT '{}', updated_at TEXT NOT NULL)"""
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

@st.cache_resource
def _supabase():
    """Server-side Supabase client. The service key never reaches the browser."""
    if create_client is None:
        return None
    try:
        config=st.secrets["supabase"]
        # Supabase accepts both the legacy service_role JWT and the newer
        # server-side secret key. Keep backwards compatibility with existing
        # Streamlit Secrets without ever embedding a credential in the app.
        server_key=(
            config.get("service_role_key")
            or config.get("secret_key")
        )
        if not server_key:
            return None
        return create_client(
            str(config["url"]),
            str(server_key),
        )
    except (KeyError, FileNotFoundError, TypeError, ValueError):
        return None

def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def _parse_opening(value):
    if not value:
        return None
    return dt.datetime.fromisoformat(str(value).replace("Z","+00:00"))

def _opening_label(value):
    opening=_parse_opening(value)
    if opening is None:
        return "Fecha por definir"
    return opening.astimezone(SANTIAGO_TZ).strftime("%d-%m-%Y")

def _is_open(value):
    opening=_parse_opening(value)
    return opening is None or dt.datetime.now(dt.timezone.utc) >= opening.astimezone(dt.timezone.utc)

def _effective_opening(class_number, remote_value=None, fallback_value=None):
    """Use the corrected Lab 2 release date even if Supabase still has the old value."""
    if int(class_number or 0) == 2:
        return ACADEMIC_COURSES[0]["labs"][1]["opens_at"]
    return remote_value or fallback_value

def _remote_rows(table, **filters):
    client=_supabase()
    if client is None:
        return None
    query=client.table(table).select("*")
    for key,value in filters.items():
        query=query.eq(key,value)
    return query.execute().data or []

@st.cache_data(ttl=45, show_spinner=False)
def _course_classes(_client):
    """One shared publication query instead of repeating it throughout each rerun."""
    if _client is None:
        return []
    try:
        return (
            _client.table("classes").select("*")
            .eq("course_id", COURSE_ID).order("class_number").execute().data or []
        )
    except Exception:
        return []

def _clear_course_cache():
    _course_classes.clear()

def _class_row(class_id):
    return next((row for row in _course_classes(_supabase()) if row.get("id") == class_id), {})

def _register_user(user_key, role, name, rut="", email=""):
    client=_supabase()
    if client is None:
        return
    client.table("users").upsert({
        "user_key":user_key,"role":role,"display_name":name,
        "rut":rut or None,"email":email or None,"last_login_at":_now(),
    },on_conflict="user_key").execute()
    client.table("enrollments").upsert({
        "course_id":COURSE_ID,"user_key":user_key,"active":True,
    },on_conflict="course_id,user_key").execute()

def _make_user_key(role, name, identification=""):
    """Stable private identifier: responses do not depend only on the visible name."""
    source=f"{role}|{identification.strip().lower() or name.strip().lower()}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()

def _normalize_name(value):
    """Normalize names for a strict but accent/case-insensitive roster match."""
    value=unicodedata.normalize("NFKD",str(value or ""))
    value="".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(value.casefold().split())

def _normalize_identification(value):
    """Keep only letters and digits so formatted and unformatted RUTs match."""
    return re.sub(r"[^0-9a-z]","",str(value or "").casefold())

def _authorized_student(name, identification):
    client=_supabase()
    if client is None:
        return False,(
            "La conexión permanente no está configurada. Revisa en Streamlit "
            "los Secrets «supabase.url» y «supabase.service_role_key» "
            "(o «supabase.secret_key»)."
        )
    normalized_name=_normalize_name(name)
    normalized_id=_normalize_identification(identification)
    try:
        rows=(client.table("authorized_students").select("*")
              .eq("course_id",COURSE_ID)
              .eq("normalized_identification",normalized_id)
              .eq("active",True).limit(1).execute().data or [])
    except Exception as exc:
        message=str(exc).casefold()
        if "authorized_students" in message and (
            "does not exist" in message or "schema cache" in message
        ):
            return False,(
                "La tabla de acceso todavía no existe en Supabase. Ejecuta una "
                "sola vez el archivo «REPARACION_ACCESO_V29.sql»."
            )
        if "permission" in message or "row-level security" in message or "rls" in message:
            return False,(
                "Supabase rechazó la consulta de acceso. El Secret configurado "
                "debe ser la clave privada «service_role» o «secret», no la "
                "clave pública «anon» o «publishable»."
            )
        return False,(
            "No fue posible consultar la nómina autorizada. Revisa la conexión "
            "a Supabase y ejecuta «REPARACION_ACCESO_V29.sql» una sola vez."
        )
    if not rows:
        return False,"El nombre y el RUT o cédula no coinciden con la nómina autorizada."
    row=rows[0]
    accepted_names={
        _normalize_name(row.get("display_name")),
        _normalize_name(row.get("email")),
    }
    if normalized_name not in accepted_names:
        return False,"El nombre o correo y el RUT o cédula no coinciden con la nómina autorizada."
    return True,row

def _progress_value(value):
    """Return a JSON-safe widget value, or None when it should not be persisted."""
    if isinstance(value,(str,int,float,bool)) or value is None:
        return value
    if isinstance(value,(list,tuple)):
        return [_progress_value(v) for v in value]
    if isinstance(value,dict):
        return {str(k):_progress_value(v) for k,v in value.items()}
    return None

def _is_answer_state(key):
    key=str(key)
    blocked=("access","role","name","user_key","projection_mode","manage_",
             "projection_","review_","anon_","reveal_","teacher_")
    if key.startswith(blocked):
        return False
    return (
        key.startswith(("ans_","checked_","sent_","exam_","q","lab1_","l2s10_","s3","s5","s7","s9","e9_","final_"))
        or key in {"case_V","case_A","case_calc","case_diff","case_pct",
                   "case_bands","case_choice","case_justification"}
    )

def save_user_progress():
    if not st.session_state.get("access") or st.session_state.get("projection_mode"):
        return
    user_key=st.session_state.get("user_key")
    if not user_key:
        return
    state={str(k):_progress_value(v) for k,v in st.session_state.items() if _is_answer_state(k)}
    serialized=json.dumps(state,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    state_hash=hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    hash_key=f"_last_saved_progress_hash_{CLASS_ID}"
    if st.session_state.get(hash_key)==state_hash:
        return
    client=_supabase()
    if client is not None:
        client.table("user_progress").upsert({
            "course_id":COURSE_ID,"class_id":CLASS_ID,"user_key":user_key,
            "role":st.session_state.get("role","Alumno"),
            "display_name":st.session_state.get("name",""),
            "state_json":state,"updated_at":_now(),
        },on_conflict="class_id,user_key").execute()
        st.session_state[hash_key]=state_hash
    else:
        with _activity_db() as con:
            con.execute(
            """INSERT INTO user_progress(user_key,role,display_name,state_json,updated_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(user_key) DO UPDATE SET role=excluded.role,
            display_name=excluded.display_name,state_json=excluded.state_json,
            updated_at=excluded.updated_at""",
            (user_key,st.session_state.get("role","Alumno"),
             st.session_state.get("name",""),serialized,
             dt.datetime.now().isoformat(timespec="seconds")),
            )
        st.session_state[hash_key]=state_hash

def load_user_progress(user_key):
    client=_supabase()
    if client is not None:
        rows=_remote_rows("user_progress",class_id=CLASS_ID,user_key=user_key)
        if not rows: return
        saved=rows[0].get("state_json") or {}
    else:
        with _activity_db() as con:
            row=con.execute("SELECT state_json FROM user_progress WHERE user_key=?",(user_key,)).fetchone()
        if not row: return
        try:
            saved=json.loads(row[0])
        except (TypeError,json.JSONDecodeError):
            return
    try:
        if isinstance(saved,str): saved=json.loads(saved)
    except json.JSONDecodeError:
        return
    for key,value in saved.items():
        if key=="exam_answers" and isinstance(value,dict):
            value={int(k):v for k,v in value.items()}
        if _is_answer_state(key) and key not in st.session_state:
            st.session_state[key]=value
    serialized=json.dumps(
        {str(k):_progress_value(v) for k,v in st.session_state.items() if _is_answer_state(k)},
        ensure_ascii=False,sort_keys=True,separators=(",",":"),
    )
    st.session_state[f"_last_saved_progress_hash_{CLASS_ID}"]=hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

def _set_projection(stage=None,question="",answer="",solution="",show_answer=False,show_solution=False):
    client=_supabase()
    if client is not None:
        client.table("projection_state").upsert({
            "course_id":COURSE_ID,"class_id":CLASS_ID,"stage":stage,
            "question":question,"answer":answer,"solution":solution,
            "show_answer":bool(show_answer),"show_solution":bool(show_solution),
            "updated_at":_now(),
        },on_conflict="course_id,class_id").execute()
    else:
        with _activity_db() as con:
            con.execute(
            """UPDATE projection_state SET stage=?,question=?,answer=?,solution=?,
            show_answer=?,show_solution=?,updated_at=? WHERE id=1""",
            (stage,question,answer,solution,int(show_answer),int(show_solution),
             dt.datetime.now().isoformat(timespec="seconds")),
            )

def projection_view():
    """Complete student-facing class screen intended for a separate Zoom window."""
    client=_supabase()
    if client is not None:
        rows=_remote_rows("projection_state",course_id=COURSE_ID,class_id=CLASS_ID)
        item=rows[0] if rows else {}
        row=(item.get("stage"),item.get("question"),item.get("answer"),item.get("solution"),
             item.get("show_answer"),item.get("show_solution"),item.get("updated_at"))
    else:
        with _activity_db() as con:
            row=con.execute(
                "SELECT stage,question,answer,solution,show_answer,show_solution,updated_at "
                "FROM projection_state WHERE id=1"
            ).fetchone()
    stage=row[0] if row else None
    if stage is None:
        st.markdown(
            '<div class="hero"><div class="tag">VISTA DE PROYECCIÓN · ALUMNOS</div>'
            '<h1>Laboratorio de aislamiento a ruido aéreo</h1>'
            '<p>Pantalla preparada. Seleccione una etapa desde el panel docente.</p></div>',
            unsafe_allow_html=True,
        )
        st.info("El docente todavía no ha seleccionado el contenido de la clase.")
    else:
        st.session_state["projection_mode"]=True
        st.session_state["role"]="Proyección"
        st.session_state["name"]="Pantalla de clase"
        stage_functions=LAB_STAGE_FUNCTIONS[ACTIVE_LAB]
        stage_functions[int(stage)]()
        if row[4] and row[2]:
            st.markdown("#### Respuesta anónima seleccionada por el docente")
            st.info(row[2])
        if row[5] and row[3]:
            st.markdown("#### Solución revelada por el docente")
            st.success(row[3])
    st.caption("Vista para alumnos: sin profundización docente, nombres, puntajes ni controles privados.")
    if st.button("Actualizar pantalla",use_container_width=True):
        st.rerun()

def _question_points(stage,key):
    return float(LAB_POINT_SCHEMAS.get(ACTIVE_LAB,{}).get(stage,{}).get(key,0))

def _score_from_level(level,max_score):
    return max_score if level=="Correcta" else max_score*.5 if level=="Parcialmente correcta" else 0.0

def _save_formative(stage,key,question,answer,level,feedback,score=None,max_score=None,correct_answer=""):
    if st.session_state.get("projection_mode"):
        return
    student=st.session_state.get("name","Alumno")
    user_key=st.session_state.get("user_key") or _make_user_key("Alumno",student)
    max_score=_question_points(stage,key) if max_score is None else float(max_score)
    score=_score_from_level(level,max_score) if score is None else float(score)
    client=_supabase()
    if client is not None:
        question_id=f"{CLASS_ID}-{key}-v1"
        client.table("questions").upsert({
            "id":question_id,"class_id":CLASS_ID,"stage":stage,
            "question_key":key,"question_text":question,
            "correct_answer":correct_answer or feedback,"max_score":max_score,
            "content_version":1,"active":True,"updated_at":_now(),
        },on_conflict="id").execute()
        try:
            answer_json=json.loads(str(answer))
        except (json.JSONDecodeError,TypeError):
            answer_json={"value":str(answer)}
        client.table("responses").upsert({
            "course_id":COURSE_ID,"class_id":CLASS_ID,"user_key":user_key,
            "stage":stage,"question_key":key,"question_text":question,
            "correct_answer":correct_answer or feedback,"answer":answer_json,
            "auto_level":level,"feedback":feedback,"auto_score":score,
            "max_score":max_score,"status":"submitted",
            "updated_at":_now(),"submitted_at":_now(),
        },on_conflict="class_id,user_key,question_key").execute()
    else:
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
    client=_supabase()
    if client is not None:
        if student==st.session_state.get("name"):
            rows=_remote_rows("responses",class_id=CLASS_ID,user_key=st.session_state.get("user_key"))
        else:
            users=_remote_rows("users",display_name=student)
            rows=_remote_rows("responses",class_id=CLASS_ID,user_key=users[0]["user_key"]) if users else []
        return [(r["stage"],r["question_key"],float(r.get("auto_score") or 0),
                 float(r.get("max_score") or 0),
                 None if r.get("teacher_score") is None else float(r["teacher_score"])) for r in rows]
    with _activity_db() as con:
        rows=con.execute(
            """SELECT stage,question_key,auto_score,max_score,teacher_score
            FROM formative_responses WHERE student=?""",(student,)).fetchall()
    return rows

def _scores_for_class(class_id, user_key=None):
    """Return effective scores for one laboratory without changing the active view."""
    client=_supabase()
    if client is None:
        return _student_scores()
    user_key=user_key or st.session_state.get("user_key")
    rows=_remote_rows("responses",class_id=class_id,user_key=user_key) if user_key else []
    return [(r["stage"],r["question_key"],float(r.get("auto_score") or 0),
             float(r.get("max_score") or 0),
             None if r.get("teacher_score") is None else float(r["teacher_score"])) for r in rows]

def _effective_score(row):
    return (row[4] if row[4] is not None else row[2]) or 0

def _grade_from_percent(percent):
    """Chilean 1.0–7.0 scale with 60% requirement for grade 4.0."""
    percent=max(0.0,min(100.0,float(percent)))
    if percent < 60:
        return 1.0 + 3.0*(percent/60.0)
    return 4.0 + 3.0*((percent-60.0)/40.0)

def _result_summary():
    """Build laboratory and course totals for the signed-in student."""
    lab_rows={n:_scores_for_class(info["id"]) for n,info in LABORATORIES.items()}
    summaries={}
    for lab_number,rows in lab_rows.items():
        activity_stages=LAB_ACTIVITY_STAGES[lab_number]
        activity_rows=[r for r in rows if r[0] in activity_stages]
        activity_max=sum(sum(LAB_POINT_SCHEMAS[lab_number][s].values()) for s in activity_stages)
        activity_earned=sum(_effective_score(r) for r in activity_rows)
        answered=len({r[1] for r in activity_rows})
        expected=sum(len(LAB_POINT_SCHEMAS[lab_number][s]) for s in activity_stages)
        summaries[lab_number]={
            "earned":activity_earned,"maximum":activity_max,
            "answered":answered,"expected":expected,
        }
    final_rows=[r for r in lab_rows[2] if r[0]==FINAL_EXAM_STAGE and r[1]=="final_exam"]
    final_done=bool(final_rows)
    final_score=sum(_effective_score(r) for r in final_rows)
    activities_earned=sum(item["earned"] for item in summaries.values())
    activities_max=sum(item["maximum"] for item in summaries.values())
    course_earned=activities_earned+final_score
    course_max=activities_max+100
    percent=100*course_earned/course_max if course_max else 0
    return summaries,{
        "final_done":final_done,"final_score":final_score,
        "earned":course_earned,"maximum":course_max,"percent":percent,
        "grade":_grade_from_percent(percent) if final_done else None,
    }

def score_counter(stage=None,compact=False):
    if st.session_state.get("projection_mode"):
        return
    rows=_student_scores()
    if stage is not None:
        rows=[row for row in rows if row[0]==stage]
        maximum=sum(LAB_POINT_SCHEMAS.get(ACTIVE_LAB,{}).get(stage,{}).values())
        title=f"Puntaje de la Etapa {stage}"
    else:
        activity_stages=LAB_ACTIVITY_STAGES[ACTIVE_LAB]
        rows=[row for row in rows if row[0] in activity_stages]
        maximum=sum(sum(LAB_POINT_SCHEMAS[ACTIVE_LAB][s].values()) for s in activity_stages)
        title=f"Actividades formativas · Lab. {ACTIVE_LAB}"
    earned=sum((row[4] if row[4] is not None else row[2]) or 0 for row in rows)
    completed=len({row[1] for row in rows})
    expected=(len(LAB_POINT_SCHEMAS.get(ACTIVE_LAB,{}).get(stage,{})) if stage is not None else
              sum(len(LAB_POINT_SCHEMAS[ACTIVE_LAB][s]) for s in activity_stages))

    # La evaluación final del Laboratorio 1 se guarda como un único registro
    # definitivo. Antes del envío, la tarjeta lateral debe reflejar el avance
    # que ya está persistido en user_progress, no esperar a que exista ese
    # registro final en responses.
    if ACTIVE_LAB==1 and stage==10 and not rows:
        draft_answers=st.session_state.get("lab1_final_answers",{})
        answered_questions=sum(
            draft_answers.get(str(i)) is not None for i in range(len(LAB1_QUESTIONS))
        )
        correct_questions=sum(
            draft_answers.get(str(i))==options[correct]
            for i,(_,options,correct) in enumerate(LAB1_QUESTIONS)
        )
        theory_live=correct_questions/len(LAB1_QUESTIONS)*80
        practical_live=_lab1_case_score(
            st.session_state.get("case_calc",0),
            st.session_state.get("case_diff",0),
            st.session_state.get("case_pct",0),
            st.session_state.get("case_bands",[]),
            st.session_state.get("case_choice"),
            st.session_state.get("case_justification",""),
        )
        case_started=any([
            float(st.session_state.get("case_calc",0) or 0)>0,
            float(st.session_state.get("case_diff",0) or 0)>0,
            float(st.session_state.get("case_pct",0) or 0)>0,
            bool(st.session_state.get("case_bands",[])),
            bool(st.session_state.get("case_choice")),
            bool(str(st.session_state.get("case_justification","")).strip()),
        ])
        earned=theory_live+practical_live
        completed=answered_questions+int(case_started)
        expected=30
    pct=100*earned/maximum if maximum else 0
    if compact:
        st.markdown(
            f'<div class="score-counter sidebar-score"><div><b>🏆 {title}</b>'
            f'<small>{completed} de {expected} respuestas registradas</small>'
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
            _save_formative(stage,key,question,answer,level,feedback,correct_answer=solution)
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
        _save_formative(stage,key,question,json.dumps(values,ensure_ascii=False),level,feedback,correct_answer=solution)
    if st.session_state.get(f"checked_{key}"):
        with st.expander("Ver desarrollo paso a paso"):
            st.markdown(solution)

def teacher_group_review(stage,solutions):
    if st.session_state.get("role")!="Docente":
        return
    st.markdown('<div class="teacher-only"><b>👥 Revisión grupal de respuestas</b>'
                '<span>Seleccione una respuesta y revele la pauta solamente cuando decida discutirla con el curso.</span></div>',
                unsafe_allow_html=True)
    client=_supabase()
    remote=client is not None
    if remote:
        raw=client.table("responses").select("*,users(display_name)").eq(
            "class_id",CLASS_ID).eq("stage",stage).order("question_key").order("updated_at").execute().data or []
        rows=[(r["id"],r.get("updated_at",""),(r.get("users") or {}).get("display_name","Alumno"),
               r["question_key"],r["question_text"],
               (r.get("answer") or {}).get("value",json.dumps(r.get("answer") or {},ensure_ascii=False)),
               r.get("auto_level"),r.get("feedback"),r.get("teacher_level"),
               float(r.get("auto_score") or 0),float(r.get("max_score") or 0),
               None if r.get("teacher_score") is None else float(r["teacher_score"]),
               r.get("teacher_note")) for r in raw]
    else:
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
    solution=solutions.get(qkey,"Revise la pauta técnica asociada a esta pregunta.")
    if st.toggle("Mostrar solución esperada",key=f"reveal_{stage}"):
        st.success(solution)
    st.markdown("##### Control de la pantalla compartida")
    p1,p2,p3,p4=st.columns(4)
    if p1.button("Mostrar pregunta",key=f"project_q_{stage}_{rid}",use_container_width=True):
        _set_projection(stage,question,answer,solution,False,False)
        st.success("Pregunta enviada a la vista de alumnos.")
    if p2.button("Mostrar respuesta",key=f"project_a_{stage}_{rid}",use_container_width=True):
        _set_projection(stage,question,answer,solution,True,False)
        st.success("Respuesta anonimizada enviada a la vista de alumnos.")
    if p3.button("Revelar solución",key=f"project_s_{stage}_{rid}",use_container_width=True):
        _set_projection(stage,question,answer,solution,True,True)
        st.success("Solución revelada en la vista de alumnos.")
    if p4.button("Limpiar pantalla",key=f"project_clear_{stage}_{rid}",use_container_width=True):
        _set_projection()
        st.success("Pantalla de proyección limpiada.")
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
        if remote:
            client.table("responses").update({
                "teacher_level":mark,"teacher_score":manual,"teacher_note":note,
                "status":"reviewed","updated_at":_now(),
            }).eq("id",rid).execute()
        else:
            with _activity_db() as con:
                con.execute(
                "UPDATE formative_responses SET teacher_level=?,teacher_score=?,teacher_note=? WHERE id=?",
                (mark,manual,note,rid),
                )
        st.success("Evaluación docente y puntaje guardados.")
    if remote:
        summary_rows={}
        for r in raw:
            name=(r.get("users") or {}).get("display_name","Alumno")
            item=summary_rows.setdefault(name,{"Alumno":name,"Puntaje":0.0,"Respondido_sobre":0.0,"Actividades":0})
            item["Puntaje"]+=float(r.get("teacher_score") if r.get("teacher_score") is not None else r.get("auto_score") or 0)
            item["Respondido_sobre"]+=float(r.get("max_score") or 0);item["Actividades"]+=1
        summary=pd.DataFrame(summary_rows.values())
    else:
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

def teacher_student_management():
    """Reset one stage, reset all work, or remove a test student."""
    if st.session_state.get("role")!="Docente":
        return
    client=_supabase()
    remote=client is not None
    if remote:
        response_users=client.table("responses").select("user_key").eq("class_id",CLASS_ID).execute().data or []
        keys=sorted({r["user_key"] for r in response_users})
        users=client.table("users").select("user_key,display_name").in_("user_key",keys).execute().data if keys else []
        student_map={u["display_name"]:u["user_key"] for u in users}
        students=sorted(student_map)
    else:
        with _activity_db() as con:
            students=[r[0] for r in con.execute(
            "SELECT DISTINCT student FROM formative_responses ORDER BY student"
            ).fetchall()]
    if not students:
        st.info("Todavía no hay alumnos con respuestas guardadas.")
        return
    student=st.selectbox("Alumno",students,key="manage_student")
    scope=st.selectbox(
        "Alcance del reinicio",
        ["Curso completo"]+[f"Etapa {n}" for n in sorted(APPLICATION_POINTS)],
        key="manage_scope",
    )
    confirm=st.checkbox(
        f"Confirmo que deseo modificar los registros de {student}",
        key="manage_confirm",
    )
    c1,c2=st.columns(2)
    if c1.button("Reiniciar respuestas",disabled=not confirm,use_container_width=True):
        if remote:
            user_key=student_map[student]
            query=client.table("responses").delete().eq("class_id",CLASS_ID).eq("user_key",user_key)
            if scope!="Curso completo":
                query=query.eq("stage",int(scope.split()[-1]))
            query.execute()
            if scope=="Curso completo":
                client.table("user_progress").delete().eq("class_id",CLASS_ID).eq("user_key",user_key).execute()
        else:
          with _activity_db() as con:
            if scope=="Curso completo":
                con.execute("DELETE FROM formative_responses WHERE student=?",(student,))
                con.execute("DELETE FROM user_progress WHERE display_name=?",(student,))
            else:
                stage_number=int(scope.split()[-1])
                con.execute(
                    "DELETE FROM formative_responses WHERE student=? AND stage=?",
                    (student,stage_number),
                )
                rows=con.execute(
                    "SELECT user_key,state_json FROM user_progress WHERE display_name=?",(student,)
                ).fetchall()
                prefixes={
                    3:("s3","ans_s3","checked_s3"),5:("s5","ans_s5","checked_s5"),
                    7:("s7","ans_s7","checked_s7"),9:("s9","e9_","ans_e9","checked_e9"),
                    10:("q","exam_","case_","final_"),
                }.get(stage_number,(f"s{stage_number}",f"ans_s{stage_number}",f"checked_s{stage_number}"))
                for user_key,state_json in rows:
                    try:
                        state=json.loads(state_json)
                    except (TypeError,json.JSONDecodeError):
                        state={}
                    state={k:v for k,v in state.items() if not k.startswith(prefixes)}
                    con.execute(
                        "UPDATE user_progress SET state_json=?,updated_at=? WHERE user_key=?",
                        (json.dumps(state,ensure_ascii=False),
                         dt.datetime.now().isoformat(timespec="seconds"),user_key),
                    )
        st.success(f"Se reiniciaron las respuestas de {student} en: {scope.lower()}.")
        st.rerun()
    if c2.button("Eliminar alumno de prueba",disabled=not confirm,use_container_width=True):
        if remote:
            user_key=student_map[student]
            client.table("responses").delete().eq("class_id",CLASS_ID).eq("user_key",user_key).execute()
            client.table("user_progress").delete().eq("class_id",CLASS_ID).eq("user_key",user_key).execute()
            client.table("enrollments").delete().eq("course_id",COURSE_ID).eq("user_key",user_key).execute()
            client.table("users").delete().eq("user_key",user_key).execute()
        else:
            with _activity_db() as con:
                con.execute("DELETE FROM formative_responses WHERE student=?",(student,))
                con.execute("DELETE FROM user_progress WHERE display_name=?",(student,))
        st.success(f"Se eliminó el registro de prueba de {student}.")
        st.rerun()

def teacher_publication_management():
    """Let the teacher reveal a laboratory only when it is ready to be taught."""
    if st.session_state.get("role")!="Docente":
        return
    client=_supabase()
    if client is None:
        st.warning("Supabase debe estar conectado para administrar publicaciones.")
        return
    st.markdown("#### Publicación de laboratorios")
    try:
        classes=_course_classes(client)
    except Exception:
        st.error("No fue posible consultar el estado de publicación.")
        return
    for item in classes:
        number=item.get("class_number")
        if number not in LABORATORIES:
            continue
        published=item.get("status")=="published"
        label=f"Laboratorio {number}"
        st.caption(f"{label}: {'publicado para alumnos' if published else 'oculto para alumnos'}")
        action="Ocultar laboratorio" if published else "Publicar laboratorio"
        if st.button(action,key=f"publication_{number}",use_container_width=True):
            new_status="draft" if published else "published"
            client.table("classes").update(
                {"status":new_status,"updated_at":_now()}
            ).eq("id",item["id"]).execute()
            _clear_course_cache()
            st.success(f"{label} quedó {'publicado' if new_status=='published' else 'oculto'}.")
            st.rerun()

def formula_reference():
    """Fallback reference view; the sidebar button opens the complete floating formulary."""
    header("FORMULARIO DEL DIPLOMADO","Compendio de los dos laboratorios disponibles",
           "Incluye únicamente las fórmulas utilizadas actualmente en los Laboratorios 1 y 2 del Curso 1.")
    st.info("Usa el botón «Abrir Formulario del Diplomado» de la barra lateral.")
    tab1,tab2,tab3,tab4=st.tabs([
        "Recintos y absorción","Transmisión y aislamiento",
        "Placas y sistemas dobles","Evaluación económica",
    ])
    with tab1:
        formula_card("Área de absorción equivalente",r"A=\sum_i \alpha_i S_i",
                     "<b>A</b>: absorción equivalente [m² sabin]<br><b>αᵢ</b>: coeficiente de absorción [-]<br><b>Sᵢ</b>: superficie [m²]",
                     "Para sumar la absorción aportada por las superficies de un recinto.")
        formula_card("Tiempo de reverberación de Sabine",r"T_{60}=0.161\,\frac{V}{A}",
                     "<b>T₆₀</b>: tiempo [s]<br><b>V</b>: volumen [m³]<br><b>A</b>: absorción equivalente [m² sabin]",
                     "Para estimar la reverberación cuando el campo es suficientemente difuso.")
    with tab2:
        formula_card("Coeficiente de transmisión",r"\tau=10^{-R/10}",
                     "<b>τ</b>: coeficiente de transmisión [-]<br><b>R</b>: índice de reducción sonora [dB]",
                     "Para transformar un aislamiento en una fracción de energía transmitida.")
        formula_card("Elemento compuesto",r"\tau_{\mathrm{total}}=\frac{\sum_i S_i\tau_i}{\sum_i S_i}\quad;\quad R_{\mathrm{total}}=-10\log_{10}(\tau_{\mathrm{total}})",
                     "<b>Sᵢ</b>: área de cada elemento [m²]<br><b>τᵢ</b>: transmisión de cada elemento [-]<br><b>Rtotal</b>: reducción compuesta [dB]",
                     "Para muros con puertas, ventanas, rendijas u otros elementos de distinto aislamiento.")
        formula_card("Porcentaje de área débil",r"p_{\mathrm{débil}}=\frac{S_{\mathrm{débil}}}{S_{\mathrm{total}}}\,100",
                     "<b>pdébil</b>: porcentaje [%]<br><b>Sdébil</b>: área débil [m²]<br><b>Stotal</b>: área total [m²]",
                     "Para cuantificar qué parte del cerramiento corresponde al elemento de menor aislamiento.")
        formula_card("Diferencia de nivel simplificada",r"\Delta L=L_{\mathrm{emisor}}-L_{\mathrm{receptor}}",
                     "<b>ΔL</b>: diferencia de nivel [dB]<br><b>L</b>: nivel sonoro [dB]",
                     "Relación didáctica. En evaluación normalizada también intervienen geometría y reverberación.")
    with tab3:
        formula_card("Ley de masa (aproximación)",r"R\approx20\log_{10}(m'f)-47",
                     "<b>R</b>: reducción sonora [dB]<br><b>m′</b>: masa superficial [kg/m²]<br><b>f</b>: frecuencia [Hz]",
                     "Para observar la tendencia ideal de una placa simple fuera de resonancias y coincidencia.")
        formula_card("Rigidez flexional",r"D=\frac{Eh^3}{12(1-\nu^2)}",
                     "<b>D</b>: rigidez [N·m]<br><b>E</b>: módulo de Young [Pa]<br><b>h</b>: espesor [m]<br><b>ν</b>: Poisson [-]",
                     "Paso previo al cálculo de la frecuencia crítica de una placa.")
        formula_card("Frecuencia crítica",r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}",
                     "<b>fc</b>: frecuencia crítica [Hz]<br><b>c</b>: velocidad del sonido [m/s]<br><b>m′</b>: masa superficial [kg/m²]<br><b>D</b>: rigidez [N·m]",
                     "Para ubicar la zona de coincidencia donde puede caer el aislamiento.")
        formula_card("Resonancia masa–aire–masa",r"f_0\approx60\sqrt{\frac{1}{d}\left(\frac{1}{m'_1}+\frac{1}{m'_2}\right)}",
                     "<b>f₀</b>: resonancia [Hz]<br><b>d</b>: cámara [m]<br><b>m′₁,m′₂</b>: masas superficiales [kg/m²]",
                     "Estimación para sistemas dobles separados por una cámara de aire.")
    with tab4:
        formula_card("Flujo neto anual",r"F_{\mathrm{neto}}=B_{\mathrm{bruto}}-C_{\mathrm{anual}}",
                     "<b>Fneto</b>: flujo anual disponible [$ /año]<br><b>Bbruto</b>: beneficio bruto [$ /año]<br><b>Canual</b>: costos recurrentes [$ /año]",
                     "Es el dinero anual que efectivamente queda para recuperar la inversión.")
        formula_card("Payback",r"\mathrm{Payback}=\frac{I_0}{F_{\mathrm{neto}}}",
                     "<b>I₀</b>: inversión inicial [$]<br><b>Fneto</b>: flujo neto [$ /año]",
                     "Indica cuántos años tarda en recuperarse la inversión.")
        formula_card("Retorno sobre la inversión",r"ROI=\frac{B_{\mathrm{total}}-I_0}{I_0}\,100",
                     "<b>ROI</b>: rentabilidad [%]<br><b>Btotal</b>: beneficio acumulado [$]<br><b>I₀</b>: inversión inicial [$]",
                     "Indica cuánto se ganó o perdió en relación con lo invertido.")

def formula_popup_button():
    """Open the cumulative Diploma reference without creating a second login session."""
    # El formulario describe el material académico actualmente cargado, no el
    # calendario de publicación. Alumno y docente deben consultar exactamente
    # los mismos dos laboratorios reales del Curso 1.
    visible_labs={(1,1),(1,2)}
    popup=build_formulary_html(visible_labs)
    popup_json=json.dumps(popup,ensure_ascii=False)
    components.html(f"""
    <button id="open-formulas">📐 Abrir Formulario actualizado · Lab. 1 y 2</button>
    <style>body{{margin:0}}button{{width:100%;height:42px;background:#0b4f83;color:white;
    border:1px solid #59d4ef;border-radius:8px;font-weight:700;font-size:13px;cursor:pointer}}
    button:hover{{background:#0878bd;border-color:#8ee9ff}}</style>
    <script>document.getElementById('open-formulas').onclick=()=>{{
      const win=window.open('','formulario_diplomado_app123','popup=yes,width=820,height=880,resizable=yes,scrollbars=yes');
      win.document.open();win.document.write({popup_json});win.document.close();
    }};</script>""",height=48,scrolling=False)
    return
    lab1_formulae=[
        ("Absorción equivalente","A = Σ α<sub>i</sub> · S<sub>i</sub>",[
            ("A","área de absorción acústica equivalente","m² sabin"),
            ("α<sub>i</sub>","coeficiente de absorción de la superficie i","adimensional"),
            ("S<sub>i</sub>","área de la superficie i","m²")]),
        ("Tiempo de reverberación de Sabine","T<sub>60</sub> = 0,161 · V / A",[
            ("T<sub>60</sub>","tiempo para que el nivel sonoro decaiga 60 dB","s"),
            ("V","volumen del recinto","m³"),
            ("A","área de absorción acústica equivalente","m² sabin")]),
        ("Coeficiente de transmisión","τ = 10<sup>−R/10</sup>",[
            ("τ","relación entre potencia sonora transmitida e incidente","adimensional"),
            ("R","índice de reducción sonora del elemento","dB")]),
        ("Elemento compuesto","τ<sub>t</sub> = Σ(S<sub>i</sub>·τ<sub>i</sub>) / ΣS<sub>i</sub><br>R<sub>t</sub> = −10·log<sub>10</sub>(τ<sub>t</sub>)",[
            ("τ<sub>t</sub>","coeficiente de transmisión total del cerramiento","adimensional"),
            ("S<sub>i</sub>","área de cada elemento (muro, puerta o ventana)","m²"),
            ("τ<sub>i</sub>","coeficiente de transmisión de cada elemento","adimensional"),
            ("R<sub>t</sub>","índice de reducción sonora del elemento compuesto","dB")]),
        ("Diferencia de nivel estandarizada","D<sub>nT</sub> = L<sub>1</sub> − L<sub>2</sub> + 10·log<sub>10</sub>(T/T<sub>0</sub>)",[
            ("D<sub>nT</sub>","diferencia de nivel estandarizada entre recintos","dB"),
            ("L<sub>1</sub>","nivel promedio en el recinto emisor","dB"),
            ("L<sub>2</sub>","nivel promedio en el recinto receptor","dB"),
            ("T","tiempo de reverberación medido en el receptor","s"),
            ("T<sub>0</sub>","tiempo de reverberación de referencia; usualmente 0,5 s","s")]),
        ("Ley de masa (aproximación)","R ≈ 20·log<sub>10</sub>(m′·f) − 47",[
            ("R","índice de reducción sonora aproximado","dB"),
            ("m′","masa superficial de la placa","kg/m²"),
            ("f","frecuencia","Hz")]),
        ("Rigidez flexional","D = E·h<sup>3</sup> / [12·(1−ν<sup>2</sup>)]",[
            ("D","rigidez flexional por unidad de ancho","N·m"),
            ("E","módulo de Young del material","Pa"),
            ("h","espesor de la placa","m"),
            ("ν","coeficiente de Poisson","adimensional")]),
        ("Frecuencia crítica","f<sub>c</sub> = c<sup>2</sup>/(2π) · √(m′/D)",[
            ("f<sub>c</sub>","frecuencia crítica o de coincidencia","Hz"),
            ("c","velocidad del sonido en el aire","m/s"),
            ("m′","masa superficial de la placa","kg/m²"),
            ("D","rigidez flexional de la placa","N·m")]),
        ("Resonancia masa–aire–masa","f<sub>0</sub> ≈ 60·√[(1/d)·(1/m′<sub>1</sub>+1/m′<sub>2</sub>)]",[
            ("f<sub>0</sub>","frecuencia de resonancia del sistema doble","Hz"),
            ("d","profundidad de la cámara de aire","m"),
            ("m′<sub>1</sub>, m′<sub>2</sub>","masas superficiales de las dos hojas","kg/m²")]),
        ("Periodo de recuperación","Payback = I<sub>0</sub> / F<sub>neto</sub>",[
            ("I<sub>0</sub>","inversión inicial","$"),
            ("F<sub>neto</sub>","flujo neto anual atribuible a la solución","$/año"),
            ("Payback","tiempo necesario para recuperar la inversión","años")]),
        ("Retorno sobre la inversión","ROI = (B<sub>total</sub> − I<sub>0</sub>) / I<sub>0</sub> · 100",[
            ("B<sub>total</sub>","beneficio económico acumulado en el periodo analizado","$"),
            ("I<sub>0</sub>","inversión inicial","$"),
            ("ROI","retorno sobre la inversión","%")]),
    ]
    lab2_formulae=[
        ("Adaptaciones espectrales ISO","R<sub>w</sub> + C &nbsp;&nbsp;·&nbsp;&nbsp; R<sub>w</sub> + C<sub>tr</sub>",[
            ("R<sub>w</sub>","índice ponderado de reducción sonora del elemento ensayado","dB"),
            ("C","término de adaptación para espectros predominantemente medios y altos","dB"),
            ("C<sub>tr</sub>","término de adaptación para tránsito y espectros con contenido grave","dB")]),
        ("Diferencia de nivel estandarizada","D<sub>nT</sub> = L<sub>1</sub> − L<sub>2</sub> + 10·log<sub>10</sub>(T/T<sub>0</sub>)",[
            ("D<sub>nT</sub>","diferencia de nivel estandarizada entre recintos","dB"),
            ("L<sub>1</sub>","nivel promedio en el recinto emisor","dB"),
            ("L<sub>2</sub>","nivel promedio en el recinto receptor","dB"),
            ("T","tiempo de reverberación medido en el recinto receptor","s"),
            ("T<sub>0</sub>","tiempo de reverberación de referencia; usualmente 0,5 s en viviendas","s")]),
        ("Descriptor adaptado del caso","D<sub>nT,A</sub> = D<sub>nT,w</sub> + C",[
            ("D<sub>nT,A</sub>","diferencia de nivel estandarizada ponderada A para el espectro considerado","dB"),
            ("D<sub>nT,w</sub>","valor único ponderado de la diferencia de nivel estandarizada","dB"),
            ("C","término de adaptación espectral correspondiente","dB")]),
        ("Paso simplificado de elemento a edificio","D<sub>nT,A</sub> ≈ R<sub>comp,A</sub> + 10·log<sub>10</sub>(0,32·V/S) − L<sub>obra</sub>",[
            ("D<sub>nT,A</sub>","diferencia de nivel estandarizada adaptada estimada","dB"),
            ("R<sub>comp,A</sub>","reducción sonora adaptada del elemento compuesto","dB"),
            ("V","volumen del recinto receptor","m³"),
            ("S","área del elemento separador","m²"),
            ("L<sub>obra</sub>","pérdida estimada por montaje, encuentros y ejecución","dB")]),
        ("Aislamiento del cerramiento compuesto","τ<sub>comp</sub> = Σ(S<sub>i</sub>·10<sup>−R<sub>i</sub>/10</sup>)/ΣS<sub>i</sub><br>R<sub>comp</sub> = −10·log<sub>10</sub>(τ<sub>comp</sub>)",[
            ("τ<sub>comp</sub>","coeficiente de transmisión del cerramiento completo","adimensional"),
            ("S<sub>i</sub>","área de cada componente, por ejemplo muro o puerta","m²"),
            ("R<sub>i</sub>","índice de reducción sonora de cada componente","dB"),
            ("R<sub>comp</sub>","índice de reducción sonora del conjunto","dB")]),
    ]

    def build_cards(formulae):
        cards=""
        for name,equation,variables in formulae:
            rows="".join(
                f"<tr><th>{symbol}</th><td>{meaning}</td><td>{unit}</td></tr>"
                for symbol,meaning,unit in variables)
            cards+=(
                f"<article><h3>{name}</h3><div class='eq'>{equation}</div>"
                f"<table><thead><tr><th>Símbolo</th><th>Corresponde a</th><th>Unidad</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></article>")
        return cards

    cards=(
        "<section><div class='lab-title'><b>Laboratorio 1</b>"
        "<span>Fundamentos, recintos, transmisión, placas y evaluación económica</span></div>"
        + build_cards(lab1_formulae) + "</section>"
    )
    show_lab2=st.session_state.get("role")=="Docente" or ACTIVE_LAB==2
    if show_lab2:
        cards+=(
            "<section><div class='lab-title lab2'><b>Laboratorio 2</b>"
            "<span>CES–MINVU, descriptores de edificio, ISO 12354 y casos profesionales</span></div>"
            + build_cards(lab2_formulae) + "</section>"
        )
    popup=f"""<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>
    <style>body{{font-family:Arial,sans-serif;background:#f4f8fc;color:#102b49;margin:0;padding:18px}}
    header{{position:sticky;top:0;background:linear-gradient(135deg,#07172b,#0878bd);color:white;
    border-radius:14px;padding:16px 18px;box-shadow:0 8px 22px #07172b33}}header b{{font-size:20px}}
    .lab-title{{display:flex;flex-direction:column;gap:3px;background:#e8f5fd;border:1px solid #b9def3;
    border-radius:12px;padding:12px 14px;margin:16px 0 10px;color:#084f83}}.lab-title b{{font-size:17px}}
    .lab-title span{{font-size:12px;color:#536b82}}.lab-title.lab2{{background:#eef8f2;border-color:#bfe3cf;color:#08724e}}
    article{{background:white;border:1px solid #d8e6f3;border-left:5px solid #0a75bd;
    border-radius:12px;padding:12px 14px;margin:10px 0}}h3{{font-size:14px;margin:0 0 8px;color:#0a4f86}}
    .eq{{font-size:20px;font-weight:800;line-height:1.55;margin-bottom:10px}}
    table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:6px 7px;border-top:1px solid #e1eaf2;text-align:left;vertical-align:top}}
    thead th{{color:#53657a;font-size:11px;text-transform:uppercase}}tbody th{{color:#083f6b;white-space:nowrap}}
    small{{display:block;margin-top:7px;color:#60718a}}</style>
    </head><body><header><b>📐 {title}</b><br><small style='color:#d9f5ff'>Formulario acumulativo del curso, organizado por laboratorio</small></header>{cards}</body></html>"""
    popup_json=json.dumps(popup,ensure_ascii=False)
    components.html(f"""
    <button id="open-formulas">📐 Abrir fórmulas</button>
    <style>body{{margin:0}}button{{width:100%;height:42px;background:#0b4f83;color:white;
    border:1px solid #59d4ef;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer}}
    button:hover{{background:#0878bd;border-color:#8ee9ff}}</style>
    <script>document.getElementById('open-formulas').onclick=()=>{{
      const win=window.open('','formulario_laboratorio','popup=yes,width=720,height=840,resizable=yes,scrollbars=yes');
      win.document.open();win.document.write({popup_json});win.document.close();
    }};</script>""",height=48,scrolling=False)

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
    if st.button("📏 Abrir visor CAD y medir",key=f"open_cad_{stage}",
                 use_container_width=True,type="secondary"):
        cad_viewer_dialog(stage)

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
    formula_card("Del beneficio anual bruto al flujo neto anual",
                 r"F_{\mathrm{neto,anual}}=B_{\mathrm{bruto,anual}}-C_{\mathrm{recurrente,anual}}",
                 "<b>F<sub>neto</sub></b>: flujo anual neto ($/año)<br>"
                 "<b>B<sub>bruto</sub></b>: ahorro o ganancia total que produce la solución durante un año, antes de descontar gastos ($/año)<br>"
                 "<b>C<sub>recurrente</sub></b>: operación, inspección y mantención que se repiten cada año ($/año)",
                 "Para evitar ambigüedad, la aplicación no usa «beneficio anual neto» como un concepto separado: el dinero que queda después de descontar costos se llama flujo neto anual.")
    st.markdown(
        '<div class="worked-example"><h3>Dos cantidades diferentes</h3>'
        '<div class="worked-step"><strong>1 · Beneficio anual bruto.</strong> Es todo el ahorro o ganancia generado durante un año, antes de descontar gastos. '
        'Se suman los ingresos atribuibles a la solución y los costos que permite evitar: '
        'multas, paralizaciones, reclamos, pérdida de productividad, arriendos temporales o reparaciones repetidas.</div>'
        '<div class="worked-step"><strong>2 · Costos recurrentes anuales.</strong> Son los gastos que se repiten cada año: '
        'mantención, inspecciones, reposición de sellos, energía adicional u operación. La inversión inicial se analiza por separado.</div>'
        '<div class="worked-step"><strong>3 · Flujo neto anual.</strong> Es el dinero que realmente queda disponible cada año. '
        'Si el beneficio bruto es $700.000 y los costos recurrentes son $100.000, entonces '
        '$700.000 − $100.000 = <b>$600.000/año</b>.</div>'
        '<div class="worked-result"><b>Lectura del resultado:</b> un flujo positivo aporta recursos para recuperar la inversión; '
        'un flujo igual a cero no la recupera; y uno negativo significa que los costos anuales superan los beneficios anuales. '
        'El payback se calcula dividiendo la inversión inicial por este flujo positivo.</div></div>',
        unsafe_allow_html=True,
    )
    formula_card("Payback · tiempo para recuperar la inversión",
                 r"Payback=\frac{I_0}{F_{\mathrm{neto,anual}}}",
                 "<b>I₀</b>: inversión inicial ($)<br><b>F<sub>neto,anual</sub></b>: beneficio anual bruto menos costos recurrentes ($/año)",
                 "Responde una pregunta concreta: ¿cuántos años tardaré en recuperar el dinero invertido? Un payback menor significa recuperación más rápida, pero no informa cuánto se gana después.")
    formula_card("ROI · rentabilidad de la inversión",
                 r"ROI=\frac{B_{\mathrm{acumulado}}-C_{\mathrm{total}}}{C_{\mathrm{total}}}\,100",
                 "<b>B acumulado</b>: beneficios obtenidos durante el período analizado ($)<br><b>C total</b>: inversión inicial más todos los costos del mismo período ($)",
                 "Responde: ¿cuánto gané o perdí, en porcentaje, respecto de todo lo que costó la inversión? ROI positivo = ganancia; 0 % = solo se recuperaron los costos; negativo = pérdida.")
    st.markdown(
        '<div class="worked-example"><h3>Ejemplo resuelto · ¿Qué significan ROI y payback?</h3>'
        '<div class="worked-step"><strong>1 · Verificación técnica.</strong> Un encapsulamiento cuesta $2.000.000 y cumple la meta acústica. '
        'Recién ahora corresponde analizar su economía.</div>'
        '<div class="worked-step"><strong>2 · Flujo neto anual.</strong> El beneficio anual bruto es $700.000 y la mantención recurrente es $100.000. '
        'Flujo neto anual = $700.000 − $100.000 = <b>$600.000/año</b>.</div>'
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
        'con el menor costo del ciclo? Revisa la meta fija y los datos de cada alternativa; luego justifica por qué '
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

def compound_r(areas, ratings):
    """Energetic combination of components expressed in decibels."""
    total_area=float(sum(areas))
    tau=sum(float(s)*10**(-float(r)/10) for s,r in zip(areas,ratings))/total_area
    return -10*math.log10(max(tau,1e-30))

def geometry_term(volume, separating_area):
    """Didactic V/S term for T0=0.5 s used in the MINVU exercise."""
    return 10*math.log10(0.32*float(volume)/float(separating_area))

def quirt_window_curve(m1,m2,gap,height,width,alpha,freqs=FREQS):
    """Implementación didáctica del modelo de Quirt para ventanas dobles."""
    rho0=1.21
    c=343.0
    f1=(1/(2*math.pi))*math.sqrt(((m1+m2)*rho0*c**2)/(gap*m1*m2))
    low=mass_r(m1+m2,freqs)
    leaf1=mass_r(m1,freqs)
    leaf2=mass_r(m2,freqs)
    high=(
        leaf1+leaf2+10*math.log10(alpha)+10*math.log10(gap)
        +10*math.log10((height+width)/(height*width))+3
    )
    return np.where(freqs<f1,low,high),f1

def stage6():
    header("ETAPA 6 · MATERIA + SIMULADORES","Fundamentos físicos del aislamiento acústico",
           "Modelos físicos de placas simples, Sharp, resonancia y ventanas dobles mediante Quirt.")
    full_matter(6)
    tabs=st.tabs(["Transmisión y R","Ley de masa","Coincidencia","Sharp · panel doble","Quirt · ventanas","Elementos compuestos"])
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
        st.markdown("#### Panel doble con cavidad absorbente · método de Sharp")
        formula_card(
            "Resonancia masa-aire-masa",
            r"f_0\approx60\sqrt{\frac{1/m_1+1/m_2}{d}}",
            "<b>m₁, m₂</b>: masas superficiales de las hojas (kg/m²)<br>"
            "<b>d</b>: separación entre hojas (m)<br><b>f₀</b>: frecuencia de resonancia (Hz)",
            "Para identificar el valle de baja frecuencia antes de interpretar la mejora del sistema doble.",
        )
        gap=st.slider("Cámara (mm)",20,300,80); absorb=st.checkbox("Absorbente en cámara",True)
        m1=st.slider("Masa hoja 1 (kg/m²)",5,80,20,key="sharp_m1")
        m2=st.slider("Masa hoja 2 (kg/m²)",5,80,20,key="sharp_m2")
        f0=60*math.sqrt((1/m1+1/m2)/(gap/1000))
        gain=8+min(gap/30,8)+(5 if absorb else 0)
        c1,c2=st.columns(2)
        c1.metric("f₀ aproximada",f"{f0:.0f} Hz")
        c2.metric("Mejora didáctica sobre hoja simple",f"{gain:.1f} dB")
        st.caption("Sharp es apropiado para paneles dobles cuya cavidad contiene absorbente. El desempeño depende además de conexiones de línea, separación de montantes, frecuencias críticas y puentes estructurales.")
    with tabs[4]:
        st.markdown("#### Ventana doble · modelo de Quirt de tu tesis")
        st.info(
            "Una ventana doble no se trata como un tabique con lana mineral. Su cavidad no está rellena y "
            "los modos interiores dependen también de la altura y el ancho del marco."
        )
        formula_card(
            "Frecuencia de resonancia f₁ · ecuación 2.28",
            r"f_1=\frac{1}{2\pi}\sqrt{\frac{(\rho_{s1}+\rho_{s2})\rho_0c^2}{d\,\rho_{s1}\rho_{s2}}}",
            "<b>ρs₁, ρs₂</b>: masa superficial de cada vidrio (kg/m²)<br>"
            "<b>ρ₀</b>: densidad del aire (kg/m³)<br><b>c</b>: velocidad del sonido (m/s)<br>"
            "<b>d</b>: cámara entre vidrios (m)",
            "Separa los dos regímenes del modelo de ventana doble.",
        )
        formula_card(
            "Régimen superior de la ventana doble",
            r"TL=TL_{\rho s1}+TL_{\rho s2}+10\log_{10}\alpha+10\log_{10}d+"
            r"10\log_{10}\left(\frac{h+w}{hw}\right)+3",
            "<b>α</b>: absorción a incidencia aleatoria del perímetro<br>"
            "<b>h, w</b>: alto y ancho de la cavidad (m)<br>"
            "<b>TLρs₁, TLρs₂</b>: pérdida de cada vidrio por banda",
            "Sobre f₁, la cavidad se considera un espacio reverberante. Bajo f₁ se usa una placa equivalente con la suma de masas.",
        )
        q1,q2,q3=st.columns(3)
        glass1=q1.number_input("Vidrio 1 (mm)",2.0,12.0,3.0,.5,key="quirt_g1")
        glass2=q2.number_input("Vidrio 2 (mm)",2.0,12.0,3.0,.5,key="quirt_g2")
        q3.number_input("Densidad vidrio (kg/m³)",2000.,2800.,2500.,50.,key="quirt_density",disabled=True)
        q4,q5,q6=st.columns(3)
        gap_mm=q4.number_input("Cámara d (mm)",4.0,100.0,6.0,1.0,key="quirt_gap")
        height=q5.number_input("Alto h (m)",.30,4.00,1.75,.05,key="quirt_h")
        width=q6.number_input("Ancho w (m)",.30,4.00,.62,.05,key="quirt_w")
        alpha=st.slider("Absorción perimetral α",.02,.30,.10,.01,key="quirt_alpha")
        density=2500.0
        qm1=density*glass1/1000
        qm2=density*glass2/1000
        curve,f1=quirt_window_curve(qm1,qm2,gap_mm/1000,height,width,alpha)
        base=mass_r(qm1+qm2,FREQS)
        c1,c2,c3=st.columns(3)
        c1.metric("Masa vidrio 1",f"{qm1:.1f} kg/m²")
        c2.metric("Masa vidrio 2",f"{qm2:.1f} kg/m²")
        c3.metric("Resonancia f₁",f"{f1:.0f} Hz")
        line_chart(
            FREQS,
            [("Ventana doble · Quirt",curve),("Placa equivalente bajo f₁",base)],
            f"Predicción didáctica {glass1:g}({gap_mm:g}){glass2:g}",
            "TL (dB)",
        )
        st.markdown(
            '<div class="good"><b>Lectura del modelo:</b> bajo f₁ las dos hojas se estiman como una placa '
            'con la suma de masas. Sobre f₁ intervienen cada vidrio, la cámara, el perímetro y las dimensiones '
            'del marco. El análisis debe entregar además Rw, C y Ctr mediante ISO 717-1.</div>',
            unsafe_allow_html=True,
        )
        check(
            "e6_quirt",
            "¿Por qué no corresponde aplicar sin cambios el método de Sharp a una ventana doble?",
            [
                "Porque la cavidad de la ventana no lleva absorbente y sus modos dependen también del marco",
                "Porque el vidrio no posee masa superficial",
                "Porque las ventanas solo se evalúan con absorción Sabine",
            ],
            "Porque la cavidad de la ventana no lleva absorbente y sus modos dependen también del marco",
            "Tu tesis adopta Quirt para representar la cavidad sin absorbente y la influencia de h y w.",
        )
    with tabs[5]:
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
        main_partition=55
        door=25
        tau=(wall_area*10**(-main_partition/10)+weak_area*10**(-door/10))/total_area
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
        st.markdown(
            '<div class="good"><b>Comprobación geométrica:</b> la puerta representa '
            '<b>16,7 %</b> del cerramiento, porque (2 m²/12 m²)×100 = 16,7 %. '
            'La fracción que se utiliza en la ecuación es 2/12 = 0,1667.</div>',
            unsafe_allow_html=True,
        )
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

def _legacy_stage7():
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
    st.markdown(
        '<div class="good"><b>Resultado del paso geométrico:</b> la puerta ocupa '
        '<b>13,3 %</b> de la separación, porque (2 m²/15 m²)×100 = 13,3 %. '
        'Este porcentaje proviene de las áreas del caso y no es un dato supuesto.</div>',
        unsafe_allow_html=True,
    )
    formula_card(
        "Combinación energética del muro y la puerta",
        r"\tau_i=10^{-R_i/10}\qquad"
        r"\tau_{\mathrm{total}}=\frac{S_{\mathrm{muro}}\tau_{\mathrm{muro}}+"
        r"S_{\mathrm{puerta}}\tau_{\mathrm{puerta}}}{S_{\mathrm{total}}}"
        r"\qquad R_{\mathrm{total}}=-10\log_{10}(\tau_{\mathrm{total}})",
        "<b>Rᵢ</b>: reducción sonora de cada elemento (dB)<br>"
        "<b>τᵢ</b>: coeficiente de transmisión de cada elemento (adimensional)<br>"
        "<b>S<sub>muro</sub></b>: área efectiva del muro = 13 m²<br>"
        "<b>S<sub>puerta</sub></b>: área de la puerta = 2 m²<br>"
        "<b>S<sub>total</sub></b>: área total de la separación = 15 m²",
        "Para combinar elementos con aislamientos diferentes. Los valores de R en dB "
        "no se promedian; primero deben convertirse a coeficientes τ y ponderarse por área.",
    )
    check("e7_guided_tau","¿Qué coeficientes de transmisión corresponden al muro y a la puerta?",
          ["τmuro=10⁻⁵ y τpuerta=10⁻³","τmuro=50 y τpuerta=30","τmuro=0,50 y τpuerta=0,30"],
          "τmuro=10⁻⁵ y τpuerta=10⁻³",
          "Se aplica τ=10^(−R/10): para 50 dB resulta 10⁻⁵ y para 30 dB resulta 10⁻³.")
    st.latex(rf"\tau_{{total}}=\frac{{13(10^{{-5}})+2(10^{{-3}})}}{{15}}={tau_total:.6f}")
    st.latex(rf"R_{{total}}=-10\log_{{10}}(\tau_{{total}})={r_total:.1f}\ \mathrm{{dB}}")
    formula_card(
        "Diferencia de nivel y estimación del nivel receptor",
        r"\begin{aligned}"
        r"\Delta L &= L_{\mathrm{emisor}}-L_{\mathrm{receptor}}\\"
        r"L_{\mathrm{receptor}} &\approx L_{\mathrm{emisor}}-R_{\mathrm{total}}"
        r"\end{aligned}",
        "<b>ΔL</b>: diferencia entre el nivel emisor y el nivel receptor (dB)<br>"
        "<b>L<sub>emisor</sub></b>: nivel en la sala emisora = 82 dB<br>"
        "<b>L<sub>receptor</sub></b>: nivel estimado en la sala receptora (dB)<br>"
        "<b>R<sub>total</sub></b>: aislamiento compuesto calculado = "
        f"{r_total:.1f} dB",
        "En este ejercicio simplificado se considera que la reducción producida por la "
        "separación es aproximadamente igual a la diferencia de nivel. Por eso se resta "
        "Rtotal al nivel emisor. En una medición normalizada real también deben considerarse "
        "la geometría y las condiciones acústicas del recinto receptor.",
    )
    st.latex(
        rf"L_{{\mathrm{{receptor}}}}\approx 82-{r_total:.1f}"
        rf"={receiver:.1f}\ \mathrm{{dB}}"
    )
    check("e7_guided_result",f"Con Rtotal ≈ {r_total:.1f} dB, ¿cuál es el nivel receptor estimado y cumple la meta?",
          [f"{receiver:.1f} dB; sí cumple",f"{receiver:.1f} dB; no cumple","32,0 dB; sí cumple","52,0 dB; no cumple"],
          f"{receiver:.1f} dB; sí cumple",
          f"En esta estimación simplificada, ΔL ≈ Rtotal y Lreceptor = 82−{r_total:.1f} "
          f"= {receiver:.1f} dB. Como es menor o igual que 45 dB, el caso cumple.")
    st.markdown(
        '<div class="good"><b>Lectura profesional:</b> el procedimiento siempre sigue la misma ruta: '
        'áreas → porcentajes → τ de cada elemento → τ ponderado → R compuesto → '
        'diferencia de nivel estimada → nivel receptor → comparación con la meta.</div>',
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
    st.markdown("#### Ejercicio guiado · Rigidez flexional y frecuencia crítica")
    formula_card(
        "Ecuaciones que debes aplicar",
        r"\begin{aligned}"
        r"D&=\frac{Eh^3}{12(1-\nu^2)}\\[0.65em]"
        r"f_c&=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}"
        r"\end{aligned}",
        "<b>D</b>: rigidez flexional de la placa (N·m)<br>"
        "<b>E</b>: módulo de Young (Pa)<br>"
        "<b>h</b>: espesor de la placa (m)<br>"
        "<b>ν</b>: coeficiente de Poisson (adimensional)<br>"
        "<b>f<sub>c</sub></b>: frecuencia crítica o de coincidencia (Hz)<br>"
        "<b>c</b>: velocidad del sonido en el aire (m/s)<br>"
        "<b>m′</b>: masa superficial de la placa (kg/m²)",
        "Primero calcula D con todas las magnitudes en el Sistema Internacional. "
        "Después utiliza ese resultado en la ecuación de fᶜ.",
    )
    st.markdown(
        '<div class="worked-example"><h3>Preparación de los datos</h3>'
        '<div class="worked-step"><strong>Módulo de Young:</strong> '
        'E = 2,5 GPa = <b>2,5×10⁹ Pa</b>.</div>'
        '<div class="worked-step"><strong>Espesor:</strong> '
        'h = 12 mm = <b>0,012 m</b>.</div>'
        '<div class="worked-step"><strong>Datos que ya están en SI:</strong> '
        'ν = 0,30; m′ = 9,6 kg/m²; c = 343 m/s.</div>'
        '<div class="worked-result">Ruta de cálculo: convertir unidades → calcular D → '
        'calcular fᶜ → interpretar el resultado.</div></div>',
        unsafe_allow_html=True,
    )
    q=("Una placa tiene E = 2,5 GPa, h = 12 mm, ν = 0,30, m′ = 9,6 kg/m² "
       "y c = 343 m/s. Calcula primero la rigidez flexional D y después la frecuencia "
       "crítica fᶜ.")
    s=("Con unidades SI: **D = Eh³/[12(1−ν²)] = 395,6 N·m**. Luego, "
       "**fᶜ = c²/(2π)√(m′/D) ≈ 2.917 Hz**. Cerca de esa frecuencia puede producirse "
       "el fenómeno de coincidencia: la placa radia con mayor eficiencia y aparece una "
       "disminución o valle en su aislamiento.")
    formative_numeric(7,"s7q4",q,[("d","D (N·m)",0.0,1.0),("fc","fᶜ (Hz)",0.0,10.0)],
        lambda v:(abs(v["d"]-395.6)<=3 and abs(v["fc"]-2917)<=25,"Se esperaba D ≈ 395,6 N·m y fᶜ ≈ 2.917 Hz. Verifica convertir 12 mm a 0,012 m."),s);solutions["s7q4"]=s
    check(
        "s7q4_interpretation",
        "¿Qué puede ocurrir con el aislamiento de la placa cerca de su frecuencia crítica fᶜ?",
        [
            "Puede disminuir y formar un valle por el fenómeno de coincidencia",
            "Aumenta siempre 6 dB, sin importar el material",
            "La placa deja de transmitir completamente",
            "Solo cambia el tiempo de reverberación del recinto",
        ],
        "Puede disminuir y formar un valle por el fenómeno de coincidencia",
        "Cerca de fᶜ aumenta la eficiencia de acoplamiento y radiación de la placa, "
        "por lo que el aislamiento puede presentar una caída.",
    )
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

def stage7():
    header(
        "ETAPA 7 · EJERCICIO PROFESIONAL GUIADO",
        "MINVU Magallanes · Sala de Reuniones Dirección",
        "Sigue el proceso completo: requerimiento → geometría → objetivo del elemento → cálculo acústico → DnT,A → decisión de obra.",
    )
    st.image(
        str(ROOT/"assets/course_visuals/minvu_direccion_guided.jpg"),
        caption="Recorte pedagógico del nivel 4. El recinto guiado está marcado en rojo y la longitud compartida es 5,55 m.",
        use_container_width=True,
    )
    st.markdown(
        '<div class="question-box"><div class="question-label">ENCARGO REAL ADAPTADO</div>'
        '<div class="question-text">Diseñar la separación entre Sala de Reuniones Dirección y Oficina Director.</div>'
        '<p>Meta: <b>DnT,A ≥ 35 dB</b>; margen mínimo: <b>5 dB</b>; pérdida de obra: <b>3 dB</b>; '
        'espesor máximo: <b>150 mm</b>. Para actividad interior se utilizará <b>Rw + C</b>.</p></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        pd.DataFrame(
            [
                ["Área Sala de Reuniones Dirección","20,98 m²","Plano nivel 4"],
                ["Área Oficina Director","27,46 m²","Plano nivel 4"],
                ["Longitud del separador","5,55 m","Cota del plano"],
                ["Altura libre","2,70 m","Dato docente"],
                ["Pérdida de obra","3 dB","Supuesto pedagógico"],
                ["Margen mínimo","5 dB","Criterio del encargo"],
            ],
            columns=["Dato","Valor","Origen"],
        ),
        hide_index=True,
        use_container_width=True,
    )

    area_floor=20.98
    height=2.70
    length=5.55
    volume=area_floor*height
    surface=length*height
    kgeo=geometry_term(volume,surface)
    target=35.0
    margin=5.0
    work_loss=3.0
    objective=target+margin+work_loss-kgeo

    st.markdown("### Paso 1 · Identificar el requerimiento")
    descriptor=st.radio(
        "¿Qué descriptor debe verificarse?",
        ["Rw del tabique","DnT,A entre recintos","Tiempo de reverberación"],
        index=None,
        key="minvu_guided_descriptor",
        horizontal=True,
    )
    st.info("La exigencia corresponde al desempeño entre recintos. Rw y Rw+C son entradas del elemento; no son la meta final del edificio.")

    st.markdown("### Paso 2 · Levantar la geometría")
    c1,c2,c3=st.columns(3)
    v_answer=c1.number_input("Volumen receptor V (m³)",0.0,500.0,0.0,.01,key="minvu_guided_v")
    s_answer=c2.number_input("Superficie separadora S (m²)",0.0,200.0,0.0,.01,key="minvu_guided_s")
    k_answer=c3.number_input("Kgeo (dB)",-20.0,20.0,0.0,.01,key="minvu_guided_k")
    with st.expander("Ver fórmula de geometría"):
        formula_card(
            "Geometría del recinto receptor",
            r"V=A_{\mathrm{piso}}h\qquad S=Lh\qquad K_{\mathrm{geo}}=10\log_{10}\left(\frac{0,32V}{S}\right)",
            "<b>V</b>: volumen receptor (m³)<br><b>S</b>: superficie total del separador (m²)<br>"
            "<b>h</b>: altura libre (m)<br><b>L</b>: longitud compartida (m)",
            "Para conectar el aislamiento del elemento con la diferencia estandarizada entre estos recintos.",
        )

    st.markdown("### Paso 3 · Calcular el objetivo del elemento")
    objective_answer=st.number_input(
        "Rw + C objetivo mínimo (dB), incluyendo margen y pérdida de obra",
        0.0,100.0,0.0,.01,key="minvu_guided_objective",
    )
    st.caption("Despeje: (Rw+C)objetivo = meta + margen + pérdida de obra - Kgeo.")

    alternatives=pd.DataFrame(
        [
            ["G-01","Hoja simple reforzada, montante común",40,-2,-7,100,45000],
            ["G-02","Doble placa, cámara con lana, montante alternado",50,-3,-9,140,68000],
            ["TA-01","Solución real: 2 placas/cara y montantes al tresbolillo",60,-4,-11,140,92000],
        ],
        columns=["Código","Descripción","Rw","C","Ctr","Espesor (mm)","Costo ref. ($/m²)"],
    )
    alternatives["Rw+C"]=alternatives["Rw"]+alternatives["C"]
    alternatives["DnT,A estimado"]=alternatives["Rw+C"]+kgeo-work_loss
    alternatives["Margen sobre meta"]=alternatives["DnT,A estimado"]-target

    st.markdown("### Paso 4 · Diseñar y comparar soluciones")
    st.dataframe(
        alternatives[["Código","Descripción","Rw","C","Ctr","Rw+C","Espesor (mm)","Costo ref. ($/m²)"]],
        hide_index=True,
        use_container_width=True,
    )
    st.markdown(
        "En el modelo registra las capas, la cámara, el absorbente y el tipo de conexión. "
        "Revisa la curva R(f), la resonancia masa-aire-masa y las frecuencias críticas antes de aceptar el número único."
    )
    selected=st.radio(
        "¿Qué alternativa es la solución mínima que cumple la meta y el margen?",
        ["G-01","G-02","TA-01"],
        index=None,
        key="minvu_guided_choice",
        horizontal=True,
    )
    dnta_answer=st.number_input(
        "DnT,A estimado de la alternativa elegida (dB)",
        0.0,100.0,0.0,.01,key="minvu_guided_dnta",
    )
    reason=st.text_area(
        "Justificación profesional breve",
        placeholder="Nombra el descriptor, el margen, el espesor, el costo y al menos un riesgo de ejecución.",
        key="minvu_guided_reason",
    )

    st.markdown("### Paso 5 · Elementos débiles y modelo de ventanas")
    st.markdown(
        "Si aparece una ventana doble, el cálculo debe utilizar el modelo de **Quirt**. "
        "Si aparece una puerta u otro componente, el paño se combina energéticamente por superficies."
    )
    quirt_choice=st.radio(
        "¿Qué dato distingue al modelo Quirt de una simple suma de dos vidrios?",
        [
            "Solo el color del vidrio",
            "La cámara sin absorbente, f₁ y las dimensiones h y w del marco",
            "Únicamente el costo de la ventana",
        ],
        index=None,
        key="minvu_guided_quirt",
    )

    if st.button("Comprobar y guardar ejercicio guiado",type="primary",key="minvu_guided_submit"):
        required=[
            descriptor is not None,
            v_answer>0,
            s_answer>0,
            objective_answer>0,
            selected is not None,
            dnta_answer>0,
            bool(reason.strip()),
            quirt_choice is not None,
        ]
        if not all(required):
            st.warning("Completa todos los pasos antes de comprobar el ejercicio.")
        else:
            score=0
            score+=2 if descriptor=="DnT,A entre recintos" else 0
            score+=2 if abs(v_answer-volume)<=.15 else 0
            score+=2 if abs(s_answer-surface)<=.15 else 0
            score+=2 if abs(k_answer-kgeo)<=.12 else 0
            score+=3 if abs(objective_answer-objective)<=.35 else 0
            score+=3 if selected=="G-02" else 0
            score+=2 if abs(dnta_answer-44.8)<=.35 else 0
            words=reason.lower()
            score+=2 if sum(k in words for k in ["margen","espesor","costo","sello","flanco","losa"])>=3 else 1
            score+=2 if quirt_choice=="La cámara sin absorbente, f₁ y las dimensiones h y w del marco" else 0
            level="Correcta" if score>=17 else "Parcialmente correcta" if score>=10 else "Incorrecta"
            _save_formative(
                7,"minvu_guided","Ejercicio profesional guiado MINVU · Sala de Reuniones Dirección",
                json.dumps(
                    {
                        "descriptor":descriptor,"V":v_answer,"S":s_answer,"Kgeo":k_answer,
                        "objetivo":objective_answer,"alternativa":selected,"DnTA":dnta_answer,
                        "justificacion":reason,"quirt":quirt_choice,
                    },
                    ensure_ascii=False,
                ),
                level,
                f"Resultado guiado: {score}/20 puntos.",
                score=score,max_score=20,
                correct_answer="V=56,65 m³; S=14,99 m²; Kgeo=0,83 dB; objetivo Rw+C=42,17 dB; G-02; DnT,A=44,8 dB.",
            )
            if score>=17:
                st.success(f"Ejercicio completado: {score}/20. Aplicaste correctamente el flujo profesional.")
            else:
                st.warning(f"Resultado: {score}/20. Revisa los pasos señalados en la pauta.")

    if st.session_state.get("role")=="Docente":
        with st.expander("🔐 Pauta docente · revelar desarrollo completo"):
            st.latex(rf"V=20,98\times2,70={volume:.2f}\ \mathrm{{m^3}}")
            st.latex(rf"S=5,55\times2,70={surface:.2f}\ \mathrm{{m^2}}")
            st.latex(rf"K_{{geo}}=10\log_{{10}}(0,32V/S)={kgeo:.2f}\ \mathrm{{dB}}")
            st.latex(rf"(R_w+C)_{{objetivo}}=35+5+3-{kgeo:.2f}={objective:.2f}\ \mathrm{{dB}}")
            st.dataframe(
                alternatives[["Código","Rw+C","DnT,A estimado","Margen sobre meta","Costo ref. ($/m²)"]],
                hide_index=True,use_container_width=True,
            )
            st.success("Decisión esperada: G-02. G-01 solo logra 35,8 dB y no alcanza el margen; TA-01 es robusta, pero resulta sobredimensionada para este encargo pedagógico.")
            st.markdown(
                "**Solución real TA-01:** canal 92 mm; montantes de 60 mm al tresbolillo; lana de vidrio de 50 mm; "
                "placas de 10 y 15 mm por cara; juntas traslapadas y banda de estanqueidad perimetral. "
                "Resultado del informe: Rw=60 dB, C=-4 dB, Ctr=-11 dB."
            )
    score_counter(7)
    teacher_group_review(
        7,
        {"minvu_guided":"V=56,65 m³; S=14,99 m²; Kgeo=+0,83 dB; Rw+C objetivo=42,17 dB; G-02; DnT,A=44,8 dB."},
    )

REF=np.array([33,36,39,42,45,48,51,52,53,54,55,56,56,56,56,56])
def rw_from_curve(curve):
    best=None
    for shift in range(-30,31):
        ref=REF+shift; dev=np.maximum(ref-curve,0)
        if dev.sum()<=32: best=(int(ref[7]),ref,dev)
    return best

def stage8():
    header("ETAPA 8 · DEL ELEMENTO AL EDIFICIO","ISO 12354 e índices de aislamiento acústico",
           "Conecta Rw, C y Ctr del elemento con geometría, pérdidas de obra, flancos y el DnT,A exigido en el caso MINVU.")
    full_matter(8)
    st.markdown("### Ruta profesional utilizada en la asesoría")
    st.markdown(
        '<div class="worked-example"><h3>El cálculo del elemento no entrega por sí solo el desempeño terminado del recinto</h3>'
        '<div class="worked-step"><strong>1 · Elemento.</strong> Se predicen R(f), Rw, C y Ctr.</div>'
        '<div class="worked-step"><strong>2 · Obra.</strong> Se consideran montaje, sellos, encuentros y transmisión lateral para estimar R′.</div>'
        '<div class="worked-step"><strong>3 · Recintos.</strong> La geometría V/S y la normalización permiten estimar DnT,w o DnT,A.</div>'
        '<div class="worked-result">Flujo: requerimiento → cálculo del elemento → pérdida de obra/flancos → geometría → cumplimiento.</div></div>',
        unsafe_allow_html=True,
    )
    formula_card(
        "Relación didáctica empleada en el caso MINVU",
        r"D_{nT,A}\approx(R_w+C)+10\log_{10}\left(\frac{0,32V}{S}\right)-L_{\mathrm{obra}}-L_{\mathrm{flancos}}",
        "<b>V</b>: volumen receptor (m³)<br><b>S</b>: superficie total del separador (m²)<br>"
        "<b>Lobra</b>: pérdida pedagógica de ejecución (dB)<br><b>Lflancos</b>: penalización simplificada de vías laterales (dB)",
        "Para comprender el cálculo inverso y comparar alternativas. No sustituye el modelo detallado por bandas de ISO 12354-1.",
    )
    st.warning(
        "Rw, R′w y DnT,A no son intercambiables. La prima identifica el comportamiento aparente en obra; "
        "nT indica normalización por reverberación; A incorpora la adaptación espectral utilizada por el criterio del caso."
    )
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

def _legacy_stage10():
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
        c1,c2=st.columns(2)
        V=c1.number_input("V (m³)",1.,500.,50.,key="case_V")
        A=c2.number_input("A (m² sabin)",1.,200.,20.,key="case_A")
        calc=st.number_input("Calcula T₆₀ (s)",0.,10.,0.,.01,key="case_calc")
        diff=st.number_input("Diferencia de costo ($)",0,5000000,0,step=50000,key="case_diff")
        pct=st.number_input("Incremento porcentual de B respecto de A (%)",0.,200.,0.,.1,key="case_pct")
        bands=st.multiselect("Bandas críticas",[125,250,500,1000],key="case_bands")
        choice=st.radio("Recomendación",["Solución A","Solución B"],index=None,key="case_choice")
        justification=st.text_area("Justificación técnico-económica",key="case_justification")
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
                correct_answer=(
                    "Pauta: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; "
                    "bandas 125, 250 y 500 Hz; Solución B por mejor respuesta grave, "
                    "mejor Rw+Cₜᵣ y mayor vida útil."
                ),
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

def stage10():
    header(
        "ETAPA 10 · EVALUACIÓN PROFESIONAL FINAL",
        "MINVU Magallanes · Sala de Reuniones Licitaciones",
        "Caso individual equivalente al ejercicio guiado. Cambia la geometría e incorpora una puerta que puede dominar el resultado.",
    )
    already_submitted=any(row[1]=="final_exam" for row in _student_scores())
    if already_submitted and st.session_state.get("role")!="Docente":
        st.success("Tu evaluación final ya fue enviada. El intento quedó cerrado y guardado.")
        st.info("El docente puede revisar tu desarrollo, ajustar el puntaje con fundamento o habilitar un nuevo intento desde Gestión de alumnos.")
        score_counter(10)
        return

    st.image(
        str(ROOT/"assets/course_visuals/minvu_licitaciones_exam.jpg"),
        caption="Recorte del nivel 4. La Sala de Reuniones Licitaciones está marcada en rojo y el paño hacia circulación incluye una puerta.",
        use_container_width=True,
    )
    st.markdown(
        '<div class="question-box"><div class="question-label">ENCARGO INDIVIDUAL · 90 MINUTOS</div>'
        '<div class="question-text">Propón la combinación de menor costo que cumpla DnT,A ≥ 35 dB.</div>'
        '<p>Después de una pérdida de obra de 3 dB debe conservar un margen mínimo de 3 dB. '
        'Usa <b>Rw + C</b>, combina tabique y puerta energéticamente y justifica la solución.</p></div>',
        unsafe_allow_html=True,
    )
    st.warning("Intento único. Revisa todos los campos antes de presionar «Enviar evaluación final».")

    floor_area=24.84
    height=2.70
    length=3.72
    door_w=0.90
    door_h=2.10
    volume=floor_area*height
    surface=length*height
    door_area=door_w*door_h
    wall_area=surface-door_area
    kgeo=geometry_term(volume,surface)
    work_loss=3.0
    required_dnta=38.0

    opaque={
        "O-01":{"name":"Tabique básico","rw":44,"c":-2,"thickness":100,"cost":45000},
        "O-02":{"name":"Tabique reforzado desacoplado","rw":52,"c":-3,"thickness":140,"cost":68000},
        "O-03":{"name":"TA-01","rw":60,"c":-4,"thickness":140,"cost":92000},
    }
    doors={
        "P-01":{"name":"Puerta hueca sin sello inferior","rw":22,"c":-1,"cost":280000},
        "P-02":{"name":"Puerta sólida con sellos","rw":32,"c":-1,"cost":690000},
        "P-03":{"name":"Puerta acústica certificada","rw":40,"c":-1,"cost":1650000},
    }
    st.markdown("### Antecedentes del caso")
    st.dataframe(
        pd.DataFrame(
            [
                ["Área de piso receptor","24,84 m²"],["Altura libre","2,70 m"],
                ["Longitud del separador","3,72 m"],["Puerta","0,90 × 2,10 m"],
                ["Meta","DnT,A ≥ 35 dB"],["Margen mínimo","3 dB"],
                ["Pérdida de obra","3 dB"],["Espesor máximo","150 mm"],
            ],
            columns=["Dato","Valor"],
        ),
        hide_index=True,use_container_width=True,
    )
    component_rows=[]
    for code,item in opaque.items():
        component_rows.append([code,item["name"],item["rw"],item["c"],item["rw"]+item["c"],f'{item["thickness"]} mm',f'${item["cost"]:,.0f}/m²'.replace(",","." )])
    for code,item in doors.items():
        component_rows.append([code,item["name"],item["rw"],item["c"],item["rw"]+item["c"],"—",f'${item["cost"]:,.0f}/un'.replace(",","." )])
    st.dataframe(
        pd.DataFrame(component_rows,columns=["Código","Componente","Rw","C","Rw+C","Espesor","Costo"]),
        hide_index=True,use_container_width=True,
    )

    st.markdown("### 1 · Requerimiento y descriptor · 10 puntos")
    descriptor=st.radio(
        "Selecciona la verificación correcta",
        [
            "Comparar directamente Rw con 35 dB",
            "Calcular DnT,A con Rw+C, geometría y pérdida de obra",
            "Promediar Rw del muro y de la puerta",
        ],
        index=None,key="final_descriptor",
    )

    st.markdown("### 2 · Levantamiento geométrico · 15 puntos")
    g1,g2,g3=st.columns(3)
    v_ans=g1.number_input("V (m³)",0.0,500.0,0.0,.01,key="final_v")
    s_ans=g2.number_input("S total (m²)",0.0,200.0,0.0,.01,key="final_s")
    sd_ans=g3.number_input("S puerta (m²)",0.0,20.0,0.0,.01,key="final_sd")
    g4,g5=st.columns(2)
    sw_ans=g4.number_input("S tabique neto (m²)",0.0,200.0,0.0,.01,key="final_sw")
    k_ans=g5.number_input("Kgeo (dB)",-20.0,20.0,0.0,.01,key="final_kgeo")

    st.markdown("### 3 · Configuración del modelo acústico · 15 puntos")
    model_text=st.text_area(
        "Describe cómo configurarías y revisarías O-02 en el modelo acústico",
        placeholder="Capas, cámara, absorbente, montantes/conexión, curva R(f), resonancia y frecuencias críticas.",
        key="final_model",
    )

    st.markdown("### 4 · Aislamiento compuesto y paso a DnT,A · 35 puntos")
    st.latex(r"R_{\mathrm{comp,A}}=-10\log_{10}\left[\frac{S_m10^{-(R_w+C)_m/10}+S_p10^{-(R_w+C)_p/10}}{S}\right]")
    st.latex(r"D_{nT,A}\approx R_{\mathrm{comp,A}}+K_{\mathrm{geo}}-L_{\mathrm{obra}}")
    test_pairs=[("O-01","P-01"),("O-01","P-02"),("O-02","P-02")]
    pair_answers={}
    for idx,(o,p) in enumerate(test_pairs,1):
        st.markdown(f"**Combinación {idx}: {o} + {p}**")
        c1,c2=st.columns(2)
        pair_answers[(o,p)]=(
            c1.number_input("Rcomp,A (dB)",0.0,100.0,0.0,.01,key=f"final_rcomp_{idx}"),
            c2.number_input("DnT,A estimado (dB)",0.0,100.0,0.0,.01,key=f"final_dnta_{idx}"),
        )

    st.markdown("### 5 · Optimización · 10 puntos")
    choice=st.selectbox(
        "Combinación de menor costo que alcanza 38 dB (meta + margen)",
        ["— Selecciona —"]+[f"{o} + {p}" for o in opaque for p in doors],
        key="final_choice",
    )
    cost_ans=st.number_input(
        "Costo instalado de la combinación elegida ($)",
        0,5000000,0,step=1000,key="final_cost",
    )

    st.markdown("### 6 · Constructibilidad y conclusión · 15 puntos")
    construction=st.text_area(
        "Indica cinco medidas de control de obra verificables",
        placeholder="Ej.: continuidad losa a losa, sellos, juntas, cajas, marco y sello inferior de puerta...",
        key="final_construction",
    )
    conclusion=st.text_area(
        "Conclusión profesional · máximo 150 palabras",
        max_chars=1200,
        placeholder="Señala combinación, descriptor, resultado, margen, costo, elemento dominante y riesgo de obra.",
        key="final_conclusion",
    )

    if st.button("Enviar evaluación final",type="primary",key="final_exam_submit"):
        numeric_complete=all([
            v_ans>0,s_ans>0,sd_ans>0,sw_ans>0,
            all(r>0 and d>0 for r,d in pair_answers.values()),
            cost_ans>0,
        ])
        if descriptor is None or not numeric_complete or choice.startswith("—") or not model_text.strip() or not construction.strip() or not conclusion.strip():
            st.warning("La evaluación está incompleta. Revisa requerimiento, geometría, tres combinaciones, costo y respuestas profesionales.")
        else:
            score=0.0
            score+=10 if descriptor=="Calcular DnT,A con Rw+C, geometría y pérdida de obra" else 0
            geometry_checks=[
                abs(v_ans-volume)<=.15,abs(s_ans-surface)<=.10,abs(sd_ans-door_area)<=.05,
                abs(sw_ans-wall_area)<=.10,abs(k_ans-kgeo)<=.10,
            ]
            score+=3*sum(geometry_checks)

            model_words=model_text.lower()
            model_hits=sum(any(term in model_words for term in group) for group in [
                ["placa","capa"],["cámara","camara"],["lana","absorb"],["montante","desacopl","conex"],
                ["curva","r(f)"],["resonan","crítica","critica","coincid"],
            ])
            score+=15 if model_hits>=5 else 10 if model_hits>=3 else 5 if model_hits>=1 else 0

            expected={}
            for o,p in test_pairs:
                ro=opaque[o]["rw"]+opaque[o]["c"]
                rp=doors[p]["rw"]+doors[p]["c"]
                rcomp=compound_r([wall_area,door_area],[ro,rp])
                expected[(o,p)]=(rcomp,rcomp+kgeo-work_loss)
            compound_hits=0
            dnta_hits=0
            for pair,(r_ans,d_ans) in pair_answers.items():
                r_expected,d_expected=expected[pair]
                compound_hits+=abs(r_ans-r_expected)<=.25
                dnta_hits+=abs(d_ans-d_expected)<=.25
            score+=(20/3)*compound_hits
            score+=5*dnta_hits

            optimal_cost=round(wall_area*opaque["O-02"]["cost"]+doors["P-02"]["cost"])
            score+=6 if choice=="O-02 + P-02" else 0
            score+=4 if abs(cost_ans-optimal_cost)<=2000 else 0

            construction_words=construction.lower()
            construction_hits=sum(any(term in construction_words for term in group) for group in [
                ["losa"],["sello","burlete"],["junta","traslap"],["caja","enchufe"],
                ["puerta","marco","inferior"],["ducto","paso"],["encuentro"],["foto","inspección","inspeccion"],
            ])
            score+=10 if construction_hits>=5 else 6 if construction_hits>=3 else 3 if construction_hits>=1 else 0

            conclusion_words=conclusion.lower()
            conclusion_hits=sum(any(term in conclusion_words for term in group) for group in [
                ["o-02"],["p-02"],["dnt","38,3","38.3"],["margen"],["costo"],["puerta","domin"],
            ])
            score+=5 if conclusion_hits>=4 else 3 if conclusion_hits>=2 else 1
            score=min(100.0,score)
            level="Correcta" if score>=60 else "Incorrecta"
            _save_formative(
                10,"final_exam","Evaluación profesional final MINVU · Sala de Reuniones Licitaciones",
                json.dumps(
                    {
                        "descriptor":descriptor,
                        "geometria":{"V":v_ans,"S":s_ans,"Spuerta":sd_ans,"Stabique":sw_ans,"Kgeo":k_ans},
                        "modelo_acustico":model_text,
                        "combinaciones":{f"{o}+{p}":{"Rcomp":r,"DnTA":d} for (o,p),(r,d) in pair_answers.items()},
                        "seleccion":choice,"costo":cost_ans,
                        "constructibilidad":construction,"conclusion":conclusion,
                    },
                    ensure_ascii=False,
                ),
                level,
                f"Puntaje automático inicial: {score:.1f}/100. Pendiente de revisión docente cualitativa.",
                score=score,max_score=100,
                correct_answer="V=67,07; S=10,04; Sp=1,89; Sm=8,15; Kgeo=3,30. Alternativa óptima: O-02+P-02; DnT,A=38,3 dB; costo=$1.244.472.",
            )
            st.session_state.exam_result=score
            st.success(f"Evaluación enviada y cerrada. Puntaje automático inicial: {score:.1f}/100.")
            st.info("La conclusión, la configuración del modelo y las medidas de obra quedan disponibles para revisión del docente.")

    if st.session_state.get("role")=="Docente":
        with st.expander("🔐 Pauta docente · resultados y rúbrica"):
            st.markdown(
                f"**Geometría:** V={volume:.2f} m³; S={surface:.2f} m²; Spuerta={door_area:.2f} m²; "
                f"Stabique={wall_area:.2f} m²; Kgeo={kgeo:.2f} dB."
            )
            rows=[]
            for o,oi in opaque.items():
                for p,pi in doors.items():
                    rcomp=compound_r([wall_area,door_area],[oi["rw"]+oi["c"],pi["rw"]+pi["c"]])
                    dnta=rcomp+kgeo-work_loss
                    cost=wall_area*oi["cost"]+pi["cost"]
                    rows.append([f"{o} + {p}",round(rcomp,1),round(dnta,1),round(cost)])
            st.dataframe(pd.DataFrame(rows,columns=["Combinación","Rcomp,A","DnT,A","Costo ($)"]),hide_index=True,use_container_width=True)
            st.success("Respuesta óptima: O-02 + P-02. DnT,A ≈ 38,3 dB; margen ≈ 3,3 dB; costo ≈ $1.244.472.")
            st.markdown(
                "**Rúbrica:** requerimiento 10; geometría 15; configuración del modelo 15; "
                "aislamiento compuesto 20; paso a DnT,A 15; optimización 10; constructibilidad 10; conclusión 5."
            )
    score_counter(10)
    teacher_group_review(
        10,
        {"final_exam":"V=67,07 m³; S=10,04 m²; Sp=1,89 m²; Sm=8,15 m²; Kgeo=3,30 dB. "
         "O-02+P-02 es la combinación mínima que logra meta+margen: DnT,A≈38,3 dB."},
    )


def lab1_stage0():
    header('ETAPA 0 · BIENVENIDA', 'Laboratorio del curso Aislamiento a Ruido Aéreo', 'Una experiencia visual para comprender el fenómeno, experimentar con variables y decidir con criterio técnico y económico.')
    st.markdown(f'<div class="class-clock"><div><strong>⏱️ Duración total de la clase: 4 horas</strong><br><span>{sum(STAGE_MINUTES.values())} min de aprendizaje y aplicación + {BREAK_MINUTES} min de pausa</span></div><div><strong>{TOTAL_CLASS_MINUTES} min</strong></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>', unsafe_allow_html=True)
    html = '<div class="route-grid">'
    for i, ((_, title), (short, desc)) in enumerate(zip(STAGES[1:], ROUTE_SUMMARIES), 1):
        html += f'<div class="route-card"><span class="step">{i}</span><div><b>{title}</b><p>{desc}</p><span class="route-time">⏱️ {STAGE_MINUTES[i]} min</span></div></div>'
        if i == BREAK_AFTER_STAGE:
            html += f'<div class="break-card"><span class="step">☕</span><div><b>Pausa pedagógica</b><p>Descanso antes del bloque de fundamentos físicos.</p><span class="route-time">⏱️ {BREAK_MINUTES} min</span></div></div>'
    st.markdown(html + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="good" style="margin-top:1rem"><b>Así aprenderás:</b> concepto visual → explicación técnica → ejemplo → interacción → interpretación → ejercicio → retroalimentación.</div>', unsafe_allow_html=True)

def lab1_stage1():
    header('ETAPA 1 · MATERIA + LABORATORIO', 'Control del ruido: fuente, trayectoria y receptor', 'Antes de elegir un material hay que localizar dónde nace el ruido, cómo se propaga y a quién afecta.')
    full_matter(1)
    lesson('Modelo de control', 'Fuente: genera la energía. Trayectoria: medio y vías de propagación. Receptor: persona, actividad o recinto afectado. Una solución robusta puede combinar los tres.')
    st.markdown('<div class="section-band"><span>🎛️</span><h3>Laboratorio visual: interviene la escena</h3></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    source = c1.selectbox('🏭 En la fuente', ['Sin intervención', 'Encerrar la fuente', 'Soportes antivibratorios', 'Equipo de menor emisión'])
    path = c2.selectbox('〰️ En la trayectoria', ['Sin intervención', 'Barrera acústica'])
    receiver = c3.selectbox('👤 En el receptor', ['Sin intervención', 'Protección auditiva', 'Cabina acústica', 'Mejorar fachada'])
    distance = st.select_slider('📏 Separación física entre la fuente y el receptor', options=['Distancia inicial', 'Distancia aumentada'], help='La distancia no es una barrera ni una intervención en la trayectoria: es una condición geométrica del problema.')
    gains = {'Sin intervención': 0, 'Encerrar la fuente': 10, 'Soportes antivibratorios': 5, 'Equipo de menor emisión': 12, 'Barrera acústica': 12, 'Protección auditiva': 10, 'Cabina acústica': 15, 'Mejorar fachada': 11}
    distance_gain = 5 if distance == 'Distancia aumentada' else 0
    total = gains[source] + gains[path] + gains[receiver] + distance_gain
    enclosure = '<div class="machine-box"></div>' if source == 'Encerrar la fuente' else ''
    mounts = '<div class="mounts">▰ ▰</div>' if source == 'Soportes antivibratorios' else ''
    barrier = '<div class="barrier"></div>' if path == 'Barrera acústica' else ''
    cabin = '<div class="receiver-cabin"></div>' if receiver == 'Cabina acústica' else ''
    facade = '<div class="receiver-facade"></div>' if receiver == 'Mejorar fachada' else ''
    phones = '<div class="headphones">🎧</div>' if receiver == 'Protección auditiva' else ''
    wave_count = max(1, 6 - round(total / 7))
    waves = ')' * wave_count
    distance_class = ' distance-on' if distance == 'Distancia aumentada' else ''
    distance_label = 'Fuente y receptor más separados' if distance == 'Distancia aumentada' else 'Distancia inicial'
    st.markdown(f'<div class="scene-pro{distance_class}"><div class="scene-caption">Nivel visual estimado: {85 - total} dB</div>{enclosure}{mounts}<div class="machine">⚙️</div><div class="waves">))) {waves}</div>{barrier}{cabin}{facade}{phones}<div class="person">🧑</div><div class="distance-label">↔ {distance_label}</div></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('Nivel inicial', '85 dB')
    b.metric('Reducción estimada', f'{total} dB')
    c.metric('Nivel resultante', f'{85 - total} dB')
    st.markdown('<div class="warn">Las reducciones se suman aquí con fines didácticos. En un proyecto real deben evaluarse por bandas, vías dominantes y condiciones de montaje.</div>', unsafe_allow_html=True)
    check('e1', 'Una máquina afecta una oficina contigua. ¿Dónde actúa el muro separador?', ['Fuente', 'Trayectoria', 'Receptor'], 'Trayectoria', 'El muro se interpone en el camino de propagación.')

def lab1_stage2():
    header('ETAPA 2 · LABORATORIO DE DOS RECINTOS', 'Aislamiento no es absorción', 'Cambia el panel separador y acondiciona el recinto receptor para observar qué magnitud modifica cada decisión.')
    full_matter(2)
    lesson('Aislamiento acústico', 'Reduce la energía que atraviesa un elemento entre recintos. Se mejora con masa, estanqueidad, desacoplamiento y control de vías indirectas.')
    lesson('Absorción acústica', 'Reduce reflexiones dentro del mismo recinto. Se expresa mediante α entre 0 y 1 y modifica reverberación e inteligibilidad.')
    st.markdown('<div class="section-band"><span>🧪</span><h3>Ejemplo didáctico: recinto emisor → panel → recinto receptor</h3></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    panel = c1.selectbox('🧱 Panel separador', ['Panel liviano simple', 'Muro de albañilería', 'Tabique doble desacoplado'], help='Este control modifica la transmisión entre los dos recintos.')
    material = c2.selectbox('🟦 Material absorbente en el receptor', ['Sin tratamiento', 'Panel poroso α = 0,40', 'Lana mineral revestida α = 0,75', 'Panel de alto desempeño α = 0,90'], help='Este material controla las reflexiones dentro del recinto receptor.')
    area = c3.slider('📐 Superficie absorbente instalada (m²)', 0, 60, 0, 5)
    panel_data = {'Panel liviano simple': (30, 'light'), 'Muro de albañilería': (45, 'masonry'), 'Tabique doble desacoplado': (55, 'double')}
    alpha_data = {'Sin tratamiento': 0.0, 'Panel poroso α = 0,40': 0.4, 'Lana mineral revestida α = 0,75': 0.75, 'Panel de alto desempeño α = 0,90': 0.9}
    R, panel_class = panel_data[panel]
    alpha = alpha_data[material]
    V = 120.0
    A0 = 18.0
    A = A0 + alpha * area
    T0 = 0.161 * V / A0
    T = 0.161 * V / A
    source_level = 85.0
    room_correction = 10 * math.log10(A / A0) if A > A0 else 0.0
    receiver_level = source_level - R - room_correction
    absorber_count = 0 if area == 0 or alpha == 0 else min(4, max(1, math.ceil(area / 15)))
    absorber_html = ''.join((f"""<div class="absorber {('ceiling' if i == 3 else f'a{i + 1}')}"></div>""" for i in range(absorber_count)))
    echo_count = max(0, 3 - round((A - A0) / 18))
    echoes = ''.join((f'<div class="echo-wave e{i + 1}">↝ ↝</div>' for i in range(echo_count)))
    wave_strength = max(1, min(5, round((60 - R) / 7)))
    transmitted = ')' * wave_strength
    st.markdown(f'<div class="two-room-lab"><div class="lab-room"><div class="room-name">RECINTO EMISOR · 85 dB</div><div class="speaker-visual">🔊</div><div class="incident-wave">))) )))</div></div><div class="lab-panel {panel_class}">{panel}<br>R = {R} dB</div><div class="lab-room receiver"><div class="room-name">RECINTO RECEPTOR</div>{absorber_html}{echoes}<div class="transmitted-wave">{transmitted}</div><div class="listener-visual">🧑\u200d💻</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="concept-grid"><div class="concept-result">🧱<b>{R:.0f} dB</b><span>Aislamiento R del panel<br><strong>No cambia por agregar absorbentes</strong></span></div><div class="concept-result">🟦<b>{A:.1f} m² sabin</b><span>Absorción equivalente del receptor<br>Inicial: {A0:.1f} m² sabin</span></div><div class="concept-result">⏱️<b>{T:.2f} s</b><span>T₆₀ del recinto receptor<br>Inicial: {T0:.2f} s</span></div></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('Nivel estimado en el receptor', f'{receiver_level:.1f} dB')
    b.metric('Cambio de T₆₀', f'{T - T0:+.2f} s')
    c.metric('Cambio del aislamiento R', '0 dB' if material != 'Sin tratamiento' else 'Sin tratamiento')
    st.markdown('<div class="good"><b>Interpretación:</b> cambiar el panel separador modifica el aislamiento entre recintos. Agregar material absorbente en el receptor aumenta su absorción equivalente, reduce las reflexiones y disminuye el T₆₀. El nivel medido en el receptor puede bajar por la menor reverberación, pero el valor R propio del panel no aumenta.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-band"><span>📐</span><h3>Laboratorio visual: absorción equivalente y ecuación de Sabine</h3></div>', unsafe_allow_html=True)
    formula_card('Absorción equivalente y ecuación de Sabine', 'A=\\sum_i S_i\\alpha_i \\qquad T_{60}=0{,}161\\,\\frac{V}{A}', '<b>S</b>: superficie (m²)<br><b>α</b>: coeficiente de absorción<br><b>V</b>: volumen (m³)<br><b>A</b>: absorción equivalente (m² sabin)', 'Para estimar el tiempo de reverberación en un recinto de campo aproximadamente difuso.')
    c1, c2, c3 = st.columns(3)
    sabine_v = c1.number_input('Volumen (m³)', 50, 1000, 220, key='e2_sabine_v')
    sabine_base = c2.number_input('Absorción inicial (m² sabin)', 5.0, 200.0, 28.0, key='e2_sabine_base')
    sabine_area = c3.number_input('Área nueva (m²)', 0.0, 300.0, 55.0, key='e2_sabine_area')
    sabine_alpha = st.select_slider('α del material en 500 Hz', options=[0.05, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95], value=0.8, key='e2_sabine_alpha')
    sabine_a = sabine_base + sabine_area * sabine_alpha
    sabine_t = 0.161 * sabine_v / sabine_a
    sabine_t0 = 0.161 * sabine_v / sabine_base
    a, b, c = st.columns(3)
    a.metric('A nueva', f'{sabine_a:.1f} m² sabin')
    b.metric('T₆₀ inicial', f'{sabine_t0:.2f} s')
    c.metric('T₆₀ final', f'{sabine_t:.2f} s', delta=f'{sabine_t - sabine_t0:+.2f} s')
    if sabine_t <= 0.8:
        st.success('Condición didáctica favorable para habla: decaimiento rápido y mejor claridad.')
    elif sabine_t <= 1.2:
        st.warning('Condición intermedia. Puede requerir más absorción según volumen y uso.')
    else:
        st.error('Reverberación alta para una actividad centrada en la palabra.')
    check('e2_sabine_check', 'Si el volumen se mantiene y se duplica A, ¿qué ocurre con T₆₀?', ['Se duplica', 'Se reduce aproximadamente a la mitad', 'No cambia'], 'Se reduce aproximadamente a la mitad', 'Sabine muestra una relación inversa entre T₆₀ y A.')
    check('e2_lab_1', 'Si mantienes el mismo panel y agregas material absorbente en el recinto receptor, ¿qué cambia principalmente?', ['Aumenta el aislamiento R del panel', 'Aumenta la absorción y disminuye el T₆₀', 'Aumenta la transmisión por el panel'], 'Aumenta la absorción y disminuye el T₆₀', 'El absorbente actúa sobre las reflexiones del recinto receptor. No modifica por sí solo la propiedad aislante del panel.')
    check('e2_lab_2', '¿Qué intervención permite reducir directamente la energía que atraviesa desde el recinto emisor?', ['Cambiar por un panel separador de mayor aislamiento', 'Agregar paneles absorbentes al receptor', 'Reducir únicamente el T₆₀ del receptor'], 'Cambiar por un panel separador de mayor aislamiento', 'La transmisión entre recintos se controla mejorando la separación: masa, estanqueidad, desacoplamiento y vías laterales.')

def lab1_stage3():
    header('ETAPA 3 · PREGUNTAS DE APLICACIÓN', 'Aislamiento, absorción y acondicionamiento acústico', 'Responde las cinco situaciones, comprueba tu razonamiento y revisa la aclaración correspondiente.')
    st.markdown('<div class="section-band"><span>✍️</span><h3>Aplicación conceptual · responde y comprueba</h3></div>', unsafe_allow_html=True)
    questions = [('s3q1', 'En una sala de reuniones se instalan paneles acústicos de espuma en todas las paredes. ¿Este tratamiento mejora el aislamiento acústico entre salas contiguas? Justifica tu respuesta.', 'No de forma significativa. La espuma es principalmente absorbente: reduce reflexiones y reverberación dentro de la sala, pero su baja masa no impide eficazmente la transmisión. Para aislar se debe mejorar el cerramiento mediante masa, estanqueidad, desacoplamiento y control de fugas y flancos.', [['no', 'no mejora'], ['absor', 'reverber'], ['masa', 'estanque', 'desacopl', 'cerramiento']], 'Diferencia el control de reflexiones interiores del control de transmisión entre recintos.'), ('s3q2', 'Se requiere reducir el eco en una oficina sin afectar la transmisión de sonido hacia otros recintos. ¿Qué tipo de tratamiento acústico se debe aplicar y por qué?', 'Se debe aplicar acondicionamiento absorbente interior —paneles, cielo acústico o bafles— para aumentar la absorción equivalente y reducir el T₆₀. El objetivo es controlar reflexiones dentro de la oficina, no modificar el aislamiento del cerramiento.', [['absor', 'acondicion'], ['eco', 'reflex', 'reverber'], ['t60', 'tiempo de reverberación']], 'La intervención buscada actúa dentro del mismo recinto y no sobre el sonido que atraviesa la separación.'), ('s3q3', 'Una persona sigue escuchando a sus vecinos a pesar de instalar paneles acústicos de espuma en su muro. ¿Cuál es el error común en la solución adoptada?', 'El error es confundir absorción con aislamiento. La espuma puede reducir reflexiones en la habitación, pero no aporta suficiente masa ni desacoplamiento. Deben revisarse muro, puertas, ventanas, juntas, enchufes y transmisiones laterales.', [['confund', 'absorción', 'absorcion'], ['aislamiento', 'transmisión', 'transmision'], ['masa', 'desacopl', 'sell', 'fuga', 'flanco']], 'Explica por qué un material absorbente no se transforma automáticamente en un buen aislante.'), ('s3q4', 'Un gimnasio necesita reducir el ruido percibido en oficinas contiguas. ¿Se deben usar materiales absorbentes o aislantes? Propón una solución adecuada.', 'Se requieren principalmente soluciones aislantes y de control vibratorio: piso resiliente o flotante, soportes antivibratorios, cerramientos dobles desacoplados, mayor masa y sellado. Los absorbentes pueden complementar reduciendo la reverberación del gimnasio, pero no sustituyen el aislamiento.', [['aisl', 'transmis'], ['vibr', 'piso flotante', 'soporte'], ['doble', 'masa', 'sell', 'desacopl']], 'Distingue el ruido aéreo de los impactos y vibraciones que pueden viajar por la estructura.'), ('s3q5', 'Se diseñan dos salas de clases. Una usa paneles absorbentes en el techo y la otra usa muros dobles entre salas. ¿Cuál solución afecta más la inteligibilidad del habla dentro de la sala y cuál mejora el aislamiento entre ellas?', 'Los paneles absorbentes del techo reducen el T₆₀ y mejoran principalmente la inteligibilidad dentro del aula. Los muros dobles desacoplados reducen la transmisión y mejoran principalmente el aislamiento entre las salas.', [['panel', 'techo', 'absorb'], ['intelig', 'reverber'], ['muro doble', 'aislamiento', 'transmis']], 'Asocia cada solución con el lugar donde aparece su beneficio: dentro de la sala o al otro lado de la separación.')]
    solutions = {}
    for key, q, solution, groups, note in questions:
        formative_development(3, key, q, solution, groups, note)
        solutions[key] = solution
    score_counter(3)
    teacher_group_review(3, solutions)

def lab1_stage4():
    header('ETAPA 4 · MATERIA + MODELO', 'Aislamiento acústico y costo-beneficio', 'La mejor solución no es la de mayor número ni la más barata: es la que cumple la meta con un costo justificable.')
    full_matter(4)
    lesson('Orden correcto de decisión', '1) definir meta y espectro; 2) descartar lo que no cumple; 3) comparar costo del ciclo, vida útil, riesgo, ROI y recuperación; 4) revisar margen de seguridad.')
    formula_card('Del beneficio anual bruto al flujo neto anual', 'F_{\\mathrm{neto,anual}}=B_{\\mathrm{bruto,anual}}-C_{\\mathrm{recurrente,anual}}', '<b>F<sub>neto</sub></b>: flujo anual neto ($/año)<br><b>B<sub>bruto</sub></b>: ahorro o ganancia total que produce la solución durante un año, antes de descontar gastos ($/año)<br><b>C<sub>recurrente</sub></b>: operación, inspección y mantención que se repiten cada año ($/año)', 'Para evitar ambigüedad, la aplicación no usa «beneficio anual neto» como un concepto separado: el dinero que queda después de descontar costos se llama flujo neto anual.')
    st.markdown('<div class="worked-example"><h3>Dos cantidades diferentes</h3><div class="worked-step"><strong>1 · Beneficio anual bruto.</strong> Es todo el ahorro o ganancia generado durante un año, antes de descontar gastos. Se suman los ingresos atribuibles a la solución y los costos que permite evitar: multas, paralizaciones, reclamos, pérdida de productividad, arriendos temporales o reparaciones repetidas.</div><div class="worked-step"><strong>2 · Costos recurrentes anuales.</strong> Son los gastos que se repiten cada año: mantención, inspecciones, reposición de sellos, energía adicional u operación. La inversión inicial se analiza por separado.</div><div class="worked-step"><strong>3 · Flujo neto anual.</strong> Es el dinero que realmente queda disponible cada año. Si el beneficio bruto es $700.000 y los costos recurrentes son $100.000, entonces $700.000 − $100.000 = <b>$600.000/año</b>.</div><div class="worked-result"><b>Lectura del resultado:</b> un flujo positivo aporta recursos para recuperar la inversión; un flujo igual a cero no la recupera; y uno negativo significa que los costos anuales superan los beneficios anuales. El payback se calcula dividiendo la inversión inicial por este flujo positivo.</div></div>', unsafe_allow_html=True)
    formula_card('Payback · tiempo para recuperar la inversión', 'Payback=\\frac{I_0}{F_{\\mathrm{neto,anual}}}', '<b>I₀</b>: inversión inicial ($)<br><b>F<sub>neto,anual</sub></b>: beneficio anual bruto menos costos recurrentes ($/año)', 'Responde una pregunta concreta: ¿cuántos años tardaré en recuperar el dinero invertido? Un payback menor significa recuperación más rápida, pero no informa cuánto se gana después.')
    formula_card('ROI · rentabilidad de la inversión', 'ROI=\\frac{B_{\\mathrm{acumulado}}-C_{\\mathrm{total}}}{C_{\\mathrm{total}}}\\,100', '<b>B acumulado</b>: beneficios obtenidos durante el período analizado ($)<br><b>C total</b>: inversión inicial más todos los costos del mismo período ($)', 'Responde: ¿cuánto gané o perdí, en porcentaje, respecto de todo lo que costó la inversión? ROI positivo = ganancia; 0 % = solo se recuperaron los costos; negativo = pérdida.')
    st.markdown('<div class="worked-example"><h3>Ejemplo resuelto · ¿Qué significan ROI y payback?</h3><div class="worked-step"><strong>1 · Verificación técnica.</strong> Un encapsulamiento cuesta $2.000.000 y cumple la meta acústica. Recién ahora corresponde analizar su economía.</div><div class="worked-step"><strong>2 · Flujo neto anual.</strong> El beneficio anual bruto es $700.000 y la mantención recurrente es $100.000. Flujo neto anual = $700.000 − $100.000 = <b>$600.000/año</b>.</div><div class="worked-step"><strong>3 · Payback.</strong> $2.000.000 ÷ $600.000/año = <b>3,33 años</b>. Significa que al cabo de aproximadamente 3 años y 4 meses se recupera la inversión inicial.</div><div class="worked-step"><strong>4 · ROI a 5 años.</strong> Beneficio acumulado = $700.000 × 5 = $3.500.000. Costo total = $2.000.000 + ($100.000 × 5) = $2.500.000. ROI = ($3.500.000 − $2.500.000) ÷ $2.500.000 × 100 = <b>40 %</b>.</div><div class="worked-result">Interpretación: al terminar los 5 años, el proyecto recuperó todos sus costos y generó un beneficio neto equivalente al 40 % del costo total. El ROI no indica cuándo se recuperó el dinero; ese dato lo entrega el payback.</div></div>', unsafe_allow_html=True)
    st.markdown('### Ejemplos para interpretar los indicadores')
    st.caption('Selecciona una respuesta en cada situación. Los datos son fijos para concentrar la actividad en la interpretación.')
    check('e4_flow', 'Una solución evita costos por $900.000 al año y requiere $150.000 anuales de mantención. ¿Cuál es su flujo anual neto?', ['$750.000/año', '$900.000/año', '$1.050.000/año', '$150.000/año'], '$750.000/año', 'Fneto = Ba − Ca = $900.000 − $150.000 = $750.000 por año.')
    check('e4_payback', 'Una medida cuesta $2.400.000 y genera un flujo anual neto de $600.000. ¿Cuál es su payback?', ['2 años', '4 años', '6 años', '40 %'], '4 años', 'Payback = I₀/Fneto = $2.400.000/$600.000 por año = 4 años.')
    check('e4_roi', 'En cinco años, una solución acumula beneficios por $4.500.000 y costos totales por $3.000.000. ¿Cuál es su ROI?', ['33,3 %', '50 %', '66,7 %', '150 %'], '50 %', 'ROI = (B−C)/C×100 = ($4.500.000−$3.000.000)/$3.000.000×100 = 50 %.')
    check('e4_decision', 'La alternativa A tiene ROI de 70 %, pero alcanza 36 dB. La alternativa B tiene ROI de 35 % y alcanza la meta de 40 dB. ¿Cuál puede recomendarse?', ['Alternativa A, porque tiene mayor ROI', 'Alternativa B, porque primero cumple la meta', 'Promediar dB y ROI', 'Ninguna, porque el ROI debe superar 50 %'], 'Alternativa B, porque primero cumple la meta', 'La suficiencia acústica es el filtro inicial. La rentabilidad solo permite comparar alternativas técnicamente suficientes.')

def lab1_stage5():
    header('ETAPA 5 · APLICACIÓN CONCEPTUAL', 'Decisión técnico-económica', 'Compara alternativas, filtra por suficiencia acústica y encuentra el mejor compromiso.')
    full_matter(5)
    st.markdown('<div class="question-box"><div class="question-label">CASO DE DECISIÓN</div><div class="question-text">¿Cuál de las tres soluciones recomendarías para cumplir el objetivo acústico con el menor costo del ciclo? Revisa la meta fija y los datos de cada alternativa; luego justifica por qué tu elección es técnicamente suficiente antes de compararla económicamente.</div></div>', unsafe_allow_html=True)
    st.caption('Instrucción: la meta y todos los datos son fijos. Analiza la tabla, descarta las soluciones que no cumplen y presenta tu recomendación sin modificar valores.')
    target = 38
    st.info('Objetivo acústico mínimo del caso: **38 dB**')
    fixed = [['Solución A', 32, 1200000, 2640000, 7200000, 172.7, 1.7], ['Solución B', 40, 1900000, 4540000, 13800000, 204.0, 2.0], ['Solución C', 47, 3200000, 7100000, 18750000, 164.1, 3.2]]
    df = pd.DataFrame(fixed, columns=['Solución', 'Aislamiento', 'Inversión', 'Costo ciclo', 'Beneficio acumulado', 'ROI', 'Payback'])
    df['Cumple'] = df['Aislamiento'] >= target
    st.dataframe(df.style.format({'Inversión': '${:,.0f}', 'Costo ciclo': '${:,.0f}', 'Beneficio acumulado': '${:,.0f}', 'ROI': '{:.1f}%', 'Payback': '{:.1f} años'}), use_container_width=True, hide_index=True)
    feasible = df[df.Cumple]
    if feasible.empty:
        st.error('Ninguna alternativa cumple. No corresponde recomendar por precio o ROI.')
    else:
        best = feasible.loc[feasible['Costo ciclo'].idxmin()]
        st.success(f"Entre las alternativas suficientes, {best['Solución']} tiene el menor costo del ciclo. La decisión final debe revisar además bandas críticas, montaje y riesgo.")
    recommendation = st.radio('Selecciona la solución que recomendarías', ['Solución A', 'Solución B', 'Solución C'], index=None, key='s5_table_recommendation', horizontal=True)
    justification = st.text_area('Justifica tu decisión utilizando cumplimiento acústico y costo del ciclo', key='s5_table_justification', placeholder='Ejemplo: descarto… porque no cumple; entre las que cumplen selecciono… porque…')
    if st.button('Comprobar decisión', key='b_s5_table_decision'):
        if recommendation is None:
            st.warning('Selecciona una solución antes de comprobar.')
        elif feasible.empty:
            st.error('Ninguna solución cumple la meta seleccionada. La decisión correcta es rediseñar las alternativas antes de recomendar una.')
        elif recommendation != best['Solución']:
            st.error(f"La recomendación no es la óptima con estos datos. Primero descarta las alternativas que no cumplen y, entre las suficientes, compara el costo del ciclo. La respuesta esperada es {best['Solución']}.")
        elif len(justification.strip()) < 20:
            st.warning(f"{best['Solución']} es la alternativa esperada, pero falta desarrollar la justificación técnica y económica.")
        else:
            st.success(f"Correcto. {best['Solución']} cumple el objetivo y presenta el menor costo del ciclo entre las alternativas suficientes.")
    check('e5', 'Una alternativa tiene excelente ROI, pero no alcanza la meta acústica. ¿Qué corresponde?', ['Elegirla por su ROI', 'Descartarla o rediseñarla antes de comparar economía', 'Promediar ROI y dB'], 'Descartarla o rediseñarla antes de comparar economía', 'La suficiencia técnica precede a la optimización económica.')
    st.markdown('<div class="section-band"><span>🧮</span><h3>Aplicación técnico-económica · responde y comprueba</h3></div>', unsafe_allow_html=True)
    q1 = 'Un ingeniero propone aumentar el aislamiento de una oficina de 40 dB a 50 dB. ¿Qué elementos debería considerar para decidir si esto es una buena inversión?'
    s1 = 'Debe comprobar el nivel actual y la meta, privacidad y uso, espectro de la fuente, cumplimiento, beneficio real de 10 dB, costo del ciclo, factibilidad, puertas, ventanas, juntas y flancos, vida útil, riesgo y rendimiento decreciente. «Más dB» no basta si la mejora no es necesaria o no puede lograrse en obra.'
    formative_development(5, 's5q1', q1, s1, [['meta', 'objetivo', 'norma'], ['costo', 'inversión', 'inversion'], ['puerta', 'ventana', 'fuga', 'flanco'], ['beneficio', 'privacidad', 'confort'], ['factib', 'vida útil', 'vida util', 'riesgo']], 'La decisión debe integrar suficiencia acústica, vías dominantes, costo completo y beneficio útil.')
    q2 = 'Un sistema cuesta $1.200.000 CLP y reduce 30 dB. Otro cuesta $2.400.000 CLP y reduce 38 dB. Calcula el costo por dB de ambos e indica cuál ofrece mayor eficiencia.'
    s2 = 'Sistema 1: $1.200.000/30 = **$40.000 por dB**. Sistema 2: $2.400.000/38 = **$63.158 por dB** aproximadamente. El sistema 1 es más eficiente por este indicador, siempre que alcance la meta acústica.'
    formative_numeric(5, 's5q2', q2, [('a', 'Sistema 1 · CLP/dB', 0.0, 1000.0), ('b', 'Sistema 2 · CLP/dB', 0.0, 1000.0)], lambda v: (abs(v['a'] - 40000) <= 500 and abs(v['b'] - 63157.9) <= 600, 'Los valores esperados son $40.000/dB y aproximadamente $63.158/dB; el menor costo por dB corresponde al sistema 1.'), s2)
    q3 = 'Opción A: inversión $500.000, beneficio $700.000. Opción B: inversión $1.000.000, beneficio $950.000. Calcula el ROI de ambas e identifica la mejor.'
    s3 = 'ROI A = ($700.000−$500.000)/$500.000×100 = **40 %**. ROI B = ($950.000−$1.000.000)/$1.000.000×100 = **−5 %**. La opción A tiene el mejor retorno.'
    formative_numeric(5, 's5q3', q3, [('a', 'ROI A (%)', 0.0, 1.0), ('b', 'ROI B (%)', 0.0, 1.0)], lambda v: (abs(v['a'] - 40) <= 0.2 and abs(v['b'] + 5) <= 0.2, 'Se esperaba ROI A = 40 % y ROI B = −5 %. La alternativa A ofrece el mejor retorno.'), s3)
    score_counter(5)
    teacher_group_review(5, {'s5q1': s1, 's5q2': s2, 's5q3': s3})

def lab1_stage6():
    header('ETAPA 6 · MATERIA + SIMULADORES', 'Fundamentos físicos del aislamiento acústico', 'Masa, frecuencia, transmisión, coincidencia, sistemas dobles, estanqueidad y elementos débiles.')
    full_matter(6)
    tabs = st.tabs(['Transmisión y R', 'Ley de masa', 'Coincidencia', 'Sistemas dobles', 'Elementos compuestos'])
    with tabs[0]:
        formula_card('Coeficiente de transmisión y reducción sonora', '\\tau=\\frac{W_t}{W_i} \\qquad R=10\\log_{10}\\left(\\frac{1}{\\tau}\\right)', '<b>Wₜ</b>: potencia transmitida (W)<br><b>Wᵢ</b>: potencia incidente (W)<br><b>τ</b>: fracción transmitida<br><b>R</b>: reducción sonora (dB)', 'Para relacionar físicamente la energía que atraviesa una separación con su aislamiento por banda.')
        formula_card('Despeje directo del coeficiente de transmisión', '\\tau=10^{-R/10}', '<b>R</b>: reducción sonora (dB)<br><b>τ</b>: fracción adimensional entre 0 y 1', 'Para conocer qué fracción de la energía atraviesa un elemento cuando se dispone de R.')
        R = st.slider('R (dB)', 10, 70, 40, key='r6')
        t = 10 ** (-R / 10)
        st.metric('Fracción de energía transmitida', f'{t:.8f} ({t * 100:.6f} %)')
        st.markdown(f'<div class="worked-example"><h3>¿De dónde sale el porcentaje?</h3><div class="worked-step"><strong>1.</strong> La ecuación entrega una fracción decimal: τ = 10<sup>−{R}/10</sup> = {t:.8f}.</div><div class="worked-step"><strong>2.</strong> Para expresarla como porcentaje se multiplica por 100: {t:.8f} × 100 = <b>{t * 100:.6f} %</b>.</div><div class="worked-result">Este porcentaje corresponde a energía transmitida, no a porcentaje de superficie.</div></div>', unsafe_allow_html=True)
        st.info('Ejemplo: R = 40 dB → τ = 10⁻⁴ = 0,0001. Solo se transmite 0,01 % de la energía incidente.')
        check('e6_tau_practical', 'Si R = 30 dB, ¿qué porcentaje de energía se transmite?', ['0,001 %', '0,01 %', '0,1 %', '3 %'], '0,1 %', 'τ = 10⁻³ = 0,001; al multiplicar por 100 se obtiene 0,1 %.')
    with tabs[1]:
        formula_card('Ley de masa ideal para una hoja simple', "R\\approx20\\log_{10}(m'f)-47", '<b>m′</b>: masa superficial (kg/m²)<br><b>f</b>: frecuencia (Hz)<br><b>R</b>: reducción sonora (dB)', 'Aproximación de campo difuso en la región controlada por masa, lejos de resonancias, coincidencia, fugas y flancos.')
        m = st.slider('Masa superficial m′ (kg/m²)', 5, 150, 25)
        curve = mass_r(m, FREQS)
        curve2 = mass_r(2 * m, FREQS)
        line_chart(FREQS, [('m′', curve), ('2·m′', curve2)], 'Ley de masa ideal', 'R (dB)')
        st.info('Duplicar masa o frecuencia aumenta aproximadamente 6 dB en la región ideal de ley de masa.')
    with tabs[2]:
        formula_card('Frecuencia crítica de una placa', "f_c=\\frac{c^2}{2\\pi}\\sqrt{\\frac{m'}{D}}\\qquad D=\\frac{Eh^3}{12(1-\\nu^2)}", '<b>c</b>: velocidad del sonido (m/s)<br><b>m′</b>: masa superficial (kg/m²)<br><b>D</b>: rigidez flexional (N·m)<br><b>E</b>: módulo de Young (Pa)<br><b>h</b>: espesor (m)<br><b>ν</b>: coeficiente de Poisson', 'Para estimar la banda donde la coincidencia puede producir una caída del aislamiento de una placa homogénea.')
        fc = st.slider('Frecuencia crítica estimada (Hz)', 100, 3150, 800)
        ideal = mass_r(25, FREQS)
        dip = ideal - 12 * np.exp(-0.5 * (np.log(FREQS / fc) / 0.24) ** 2)
        line_chart(FREQS, [('Ley de masa ideal', ideal), ('Con coincidencia', dip)], 'Efecto didáctico de coincidencia', 'R (dB)')
        st.warning('Cerca de fᶜ el panel radia con mayor eficiencia y puede aparecer una caída de aislamiento.')
    with tabs[3]:
        gap = st.slider('Cámara (mm)', 20, 300, 80)
        absorb = st.checkbox('Absorbente en cámara', True)
        gain = 8 + min(gap / 30, 8) + (5 if absorb else 0)
        st.metric('Mejora didáctica sobre hoja simple', f'{gain:.1f} dB')
        st.caption('El desempeño real depende de masas, rigidez de uniones, frecuencia masa–aire–masa y puentes estructurales.')
    with tabs[4]:
        formula_card('Aislamiento de elementos compuestos', '\\tau_{\\mathrm{total}}=\\frac{\\sum_i S_i\\tau_i}{\\sum_i S_i}\\qquad R_{\\mathrm{total}}=-10\\log_{10}(\\tau_{\\mathrm{total}})', '<b>Sᵢ</b>: área del elemento i (m²)<br><b>τᵢ=10^{-Rᵢ/10}</b>: coeficiente de transmisión de cada elemento', 'Para combinar un muro con puertas, ventanas u otros componentes. Los aislamientos en dB no se promedian.')
        st.markdown('#### Aplicación práctica · muro con puerta')
        st.write('Datos fijos: muro de **4,0 m × 3,0 m** (12 m²), puerta de **1,0 m × 2,0 m** (2 m²), R del paño de muro = **55 dB** y R de la puerta = **25 dB**.')
        total_area = 12.0
        weak_area = 2.0
        share = weak_area / total_area
        wall_area = total_area - weak_area
        main_partition = 55
        door = 25
        tau = (wall_area * 10 ** (-main_partition / 10) + weak_area * 10 ** (-door / 10)) / total_area
        comp = -10 * np.log10(tau)
        st.markdown('<div class="worked-example"><h3>Cálculo del porcentaje de área débil</h3><div class="worked-step"><strong>1 · Área total del cerramiento.</strong> 4,0 × 3,0 = <b>12 m²</b>.</div><div class="worked-step"><strong>2 · Área de la puerta.</strong> 1,0 × 2,0 = <b>2 m²</b>.</div><div class="worked-step"><strong>3 · Porcentaje débil.</strong> (Sdébil/Stotal) × 100 = (2/12) × 100 = <b>16,7 %</b>.</div><div class="worked-result">En la ecuación se usa la fracción 2/12 = 0,1667. El área útil del muro es 12−2 = 10 m²; la puerta no se suma nuevamente al total.</div></div>', unsafe_allow_html=True)
        st.metric('R compuesto', f'{comp:.1f} dB')
        st.info('Los dB no se promedian: se combinan coeficientes de transmisión ponderados por superficie.')
        st.markdown('<div class="good"><b>Comprobación geométrica:</b> la puerta representa <b>16,7 %</b> del cerramiento, porque (2 m²/12 m²)×100 = 16,7 %. La fracción que se utiliza en la ecuación es 2/12 = 0,1667.</div>', unsafe_allow_html=True)
        check('e6_comp_practical', f'Al combinar energéticamente ambos elementos, el resultado es aproximadamente {comp:.1f} dB. ¿Por qué queda mucho más cerca de la puerta que del muro?', ['Porque se promediaron 55 y 25 dB', 'Porque la puerta tiene un τ mucho mayor y domina la energía transmitida', 'Porque la puerta ocupa más superficie que el muro'], 'Porque la puerta tiene un τ mucho mayor y domina la energía transmitida', 'Aunque solo ocupa 16,7 % del área, la puerta transmite mucha más energía por metro cuadrado. Por eso los coeficientes τ se ponderan por superficie.')
    check('e6', 'Si se duplica la masa superficial de un panel dentro de la región ideal de la ley de masa, ¿qué mejora aproximada se espera?', ['3 dB', '6 dB', '10 dB', 'El aislamiento no cambia'], '6 dB', 'La ley de masa ideal predice aproximadamente 6 dB de aumento de R al duplicar la masa superficial, para una misma frecuencia.')

def lab1_stage7():
    header('ETAPA 7 · APLICACIÓN PRÁCTICA', 'Diseño de aislamiento acústico', 'Aplica las ecuaciones de la etapa anterior siguiendo una ruta de cálculo clara y verificable.')
    full_matter(7)
    st.markdown('<div class="question-box"><div class="question-label">CASO GUIADO · MURO CON PUERTA</div><div class="question-text">Una sala emisora tiene 82 dB. La separación mide 15 m² e incorpora una puerta de 2 m². El muro tiene R = 50 dB y la puerta R = 30 dB. Calcula el área débil, el aislamiento compuesto y el nivel estimado en el receptor. Luego decide si cumple la meta de 45 dB.</div></div>', unsafe_allow_html=True)
    st.caption('Todos los datos son fijos. Resuelve cada paso y comprueba antes de continuar.')
    source = 82.0
    target = 45.0
    total_area = 15.0
    weak_area = 2.0
    wall_area = total_area - weak_area
    r_wall = 50.0
    r_weak = 30.0
    weak_pct = 100 * weak_area / total_area
    tau_wall = 10 ** (-r_wall / 10)
    tau_weak = 10 ** (-r_weak / 10)
    tau_total = (wall_area * tau_wall + weak_area * tau_weak) / total_area
    r_total = -10 * math.log10(tau_total)
    receiver = source - r_total
    case_df = pd.DataFrame([['Nivel emisor', f'{source:.0f} dB'], ['Área total', f'{total_area:.0f} m²'], ['Área de puerta', f'{weak_area:.0f} m²'], ['Área efectiva de muro', f'{wall_area:.0f} m²'], ['R muro', f'{r_wall:.0f} dB'], ['R puerta', f'{r_weak:.0f} dB'], ['Meta en receptor', f'≤ {target:.0f} dB']], columns=['Dato', 'Valor'])
    st.dataframe(case_df, hide_index=True, use_container_width=True)
    st.markdown('<div class="worked-example"><h3>Origen de las áreas y porcentajes</h3><div class="worked-step">El área total de 15 m² corresponde a toda la separación, incluida la puerta.</div><div class="worked-step">Área efectiva del muro = 15−2 = <b>13 m²</b>.</div><div class="worked-step">Porcentaje de puerta = (2/15)×100 = <b>13,3 %</b>. En la ecuación se usa 2/15 = 0,1333.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="good"><b>Resultado del paso geométrico:</b> la puerta ocupa <b>13,3 %</b> de la separación, porque (2 m²/15 m²)×100 = 13,3 %. Este porcentaje proviene de las áreas del caso y no es un dato supuesto.</div>', unsafe_allow_html=True)
    formula_card('Combinación energética del muro y la puerta', '\\tau_i=10^{-R_i/10}\\qquad\\tau_{\\mathrm{total}}=\\frac{S_{\\mathrm{muro}}\\tau_{\\mathrm{muro}}+S_{\\mathrm{puerta}}\\tau_{\\mathrm{puerta}}}{S_{\\mathrm{total}}}\\qquad R_{\\mathrm{total}}=-10\\log_{10}(\\tau_{\\mathrm{total}})', '<b>Rᵢ</b>: reducción sonora de cada elemento (dB)<br><b>τᵢ</b>: coeficiente de transmisión de cada elemento (adimensional)<br><b>S<sub>muro</sub></b>: área efectiva del muro = 13 m²<br><b>S<sub>puerta</sub></b>: área de la puerta = 2 m²<br><b>S<sub>total</sub></b>: área total de la separación = 15 m²', 'Para combinar elementos con aislamientos diferentes. Los valores de R en dB no se promedian; primero deben convertirse a coeficientes τ y ponderarse por área.')
    check('e7_guided_tau', '¿Qué coeficientes de transmisión corresponden al muro y a la puerta?', ['τmuro=10⁻⁵ y τpuerta=10⁻³', 'τmuro=50 y τpuerta=30', 'τmuro=0,50 y τpuerta=0,30'], 'τmuro=10⁻⁵ y τpuerta=10⁻³', 'Se aplica τ=10^(−R/10): para 50 dB resulta 10⁻⁵ y para 30 dB resulta 10⁻³.')
    st.latex(f'\\tau_{{total}}=\\frac{{13(10^{{-5}})+2(10^{{-3}})}}{{15}}={tau_total:.6f}')
    st.latex(f'R_{{total}}=-10\\log_{{10}}(\\tau_{{total}})={r_total:.1f}\\ \\mathrm{{dB}}')
    formula_card('Diferencia de nivel y estimación del nivel receptor', '\\begin{aligned}\\Delta L &= L_{\\mathrm{emisor}}-L_{\\mathrm{receptor}}\\\\L_{\\mathrm{receptor}} &\\approx L_{\\mathrm{emisor}}-R_{\\mathrm{total}}\\end{aligned}', f'<b>ΔL</b>: diferencia entre el nivel emisor y el nivel receptor (dB)<br><b>L<sub>emisor</sub></b>: nivel en la sala emisora = 82 dB<br><b>L<sub>receptor</sub></b>: nivel estimado en la sala receptora (dB)<br><b>R<sub>total</sub></b>: aislamiento compuesto calculado = {r_total:.1f} dB', 'En este ejercicio simplificado se considera que la reducción producida por la separación es aproximadamente igual a la diferencia de nivel. Por eso se resta Rtotal al nivel emisor. En una medición normalizada real también deben considerarse la geometría y las condiciones acústicas del recinto receptor.')
    st.latex(f'L_{{\\mathrm{{receptor}}}}\\approx 82-{r_total:.1f}={receiver:.1f}\\ \\mathrm{{dB}}')
    check('e7_guided_result', f'Con Rtotal ≈ {r_total:.1f} dB, ¿cuál es el nivel receptor estimado y cumple la meta?', [f'{receiver:.1f} dB; sí cumple', f'{receiver:.1f} dB; no cumple', '32,0 dB; sí cumple', '52,0 dB; no cumple'], f'{receiver:.1f} dB; sí cumple', f'En esta estimación simplificada, ΔL ≈ Rtotal y Lreceptor = 82−{r_total:.1f} = {receiver:.1f} dB. Como es menor o igual que 45 dB, el caso cumple.')
    st.markdown('<div class="good"><b>Lectura profesional:</b> el procedimiento siempre sigue la misma ruta: áreas → porcentajes → τ de cada elemento → τ ponderado → R compuesto → diferencia de nivel estimada → nivel receptor → comparación con la meta.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-band"><span>🧪</span><h3>Aplicación conceptual III · 11 ejercicios</h3></div>', unsafe_allow_html=True)
    solutions = {}
    q = 'En un ensayo simplificado, el nivel medio en el recinto emisor es 85 dB y en el receptor es 45 dB. Sin aplicar correcciones de recinto, calcula R.'
    s = 'Aplicación simplificada: **R = L₁ − L₂ = 85 − 45 = 40 dB**. En un ensayo normalizado real se incorporan las correcciones y condiciones definidas por el método.'
    formative_numeric(7, 's7q1', q, [('r', 'R (dB)', 0.0, 1.0)], lambda v: (abs(v['r'] - 40) < 0.1, 'R debe ser 40 dB: resta nivel receptor al nivel emisor.'), s)
    solutions['s7q1'] = s
    q = 'Para un elemento con R = 40 dB, calcula el coeficiente de transmisión τ.'
    s = '**τ = 10^(−R/10) = 10⁻⁴ = 0,0001**, equivalente a 0,01 % de la energía incidente.'
    formative_numeric(7, 's7q2', q, [('tau', 'τ', 0.0, 0.0001)], lambda v: (abs(v['tau'] - 0.0001) <= 1e-05, 'τ debe ser 0,0001.'), s)
    solutions['s7q2'] = s
    q = 'Aplica la ley de masa ideal para m′ = 30 kg/m² y f = 500 Hz. Calcula R.'
    expected = 20 * math.log10(30 * 500) - 47
    s = f'**R ≈ 20 log₁₀(30×500) − 47 = {expected:.1f} dB**. Es una aproximación válida solo en la región controlada por masa.'
    formative_numeric(7, 's7q3', q, [('r', 'R (dB)', 0.0, 0.1)], lambda v: (abs(v['r'] - expected) <= 0.3, f'El resultado esperado es aproximadamente {expected:.1f} dB.'), s)
    solutions['s7q3'] = s
    st.markdown('#### Ejercicio guiado · Rigidez flexional y frecuencia crítica')
    formula_card('Ecuaciones que debes aplicar', "\\begin{aligned}D&=\\frac{Eh^3}{12(1-\\nu^2)}\\\\[0.65em]f_c&=\\frac{c^2}{2\\pi}\\sqrt{\\frac{m'}{D}}\\end{aligned}", '<b>D</b>: rigidez flexional de la placa (N·m)<br><b>E</b>: módulo de Young (Pa)<br><b>h</b>: espesor de la placa (m)<br><b>ν</b>: coeficiente de Poisson (adimensional)<br><b>f<sub>c</sub></b>: frecuencia crítica o de coincidencia (Hz)<br><b>c</b>: velocidad del sonido en el aire (m/s)<br><b>m′</b>: masa superficial de la placa (kg/m²)', 'Primero calcula D con todas las magnitudes en el Sistema Internacional. Después utiliza ese resultado en la ecuación de fᶜ.')
    st.markdown('<div class="worked-example"><h3>Preparación de los datos</h3><div class="worked-step"><strong>Módulo de Young:</strong> E = 2,5 GPa = <b>2,5×10⁹ Pa</b>.</div><div class="worked-step"><strong>Espesor:</strong> h = 12 mm = <b>0,012 m</b>.</div><div class="worked-step"><strong>Datos que ya están en SI:</strong> ν = 0,30; m′ = 9,6 kg/m²; c = 343 m/s.</div><div class="worked-result">Ruta de cálculo: convertir unidades → calcular D → calcular fᶜ → interpretar el resultado.</div></div>', unsafe_allow_html=True)
    q = 'Una placa tiene E = 2,5 GPa, h = 12 mm, ν = 0,30, m′ = 9,6 kg/m² y c = 343 m/s. Calcula primero la rigidez flexional D y después la frecuencia crítica fᶜ.'
    s = 'Con unidades SI: **D = Eh³/[12(1−ν²)] = 395,6 N·m**. Luego, **fᶜ = c²/(2π)√(m′/D) ≈ 2.917 Hz**. Cerca de esa frecuencia puede producirse el fenómeno de coincidencia: la placa radia con mayor eficiencia y aparece una disminución o valle en su aislamiento.'
    formative_numeric(7, 's7q4', q, [('d', 'D (N·m)', 0.0, 1.0), ('fc', 'fᶜ (Hz)', 0.0, 10.0)], lambda v: (abs(v['d'] - 395.6) <= 3 and abs(v['fc'] - 2917) <= 25, 'Se esperaba D ≈ 395,6 N·m y fᶜ ≈ 2.917 Hz. Verifica convertir 12 mm a 0,012 m.'), s)
    solutions['s7q4'] = s
    check('s7q4_interpretation', '¿Qué puede ocurrir con el aislamiento de la placa cerca de su frecuencia crítica fᶜ?', ['Puede disminuir y formar un valle por el fenómeno de coincidencia', 'Aumenta siempre 6 dB, sin importar el material', 'La placa deja de transmitir completamente', 'Solo cambia el tiempo de reverberación del recinto'], 'Puede disminuir y formar un valle por el fenómeno de coincidencia', 'Cerca de fᶜ aumenta la eficiencia de acoplamiento y radiación de la placa, por lo que el aislamiento puede presentar una caída.')
    q = 'Un recinto posee 60 m² de superficie con α = 0,10 y agrega 25 m² de material con α = 0,80. Calcula la absorción equivalente total.'
    s = '**A = 60×0,10 + 25×0,80 = 6 + 20 = 26 m² sabin**.'
    formative_numeric(7, 's7q5', q, [('a', 'A total (m² sabin)', 0.0, 1.0)], lambda v: (abs(v['a'] - 26) < 0.1, 'La absorción equivalente total es 26 m² sabin.'), s)
    solutions['s7q5'] = s
    q = 'Compara dos ventanas: A tiene Rw = 40 dB y B tiene Rw = 35 dB. ¿Cuál transmite menos energía y cuántas veces difieren aproximadamente sus coeficientes τ?'
    s = 'La ventana A transmite menos. Una diferencia de 5 dB corresponde a una razón de transmisión de **10^(5/10) ≈ 3,16**: B transmite aproximadamente 3,16 veces más energía que A.'
    formative_development(7, 's7q6', q, s, [['a', '40'], ['menos', 'menor'], ['3,16', '3.16', 'tres']], 'No compares los dB como una razón lineal: convierte la diferencia mediante 10^(ΔR/10).')
    solutions['s7q6'] = s
    q = '¿Qué ocurre idealmente con R cuando se duplica la masa superficial de una hoja simple?'
    s = 'En la región ideal controlada por masa, **R aumenta aproximadamente 6 dB**. No es una regla universal cerca de resonancias, coincidencia, fugas o flancos.'
    formative_development(7, 's7q7', q, s, [['6', 'seis'], ['masa'], ['ideal', 'coincid', 'resonan', 'aproxim']], 'Indica tanto la mejora aproximada como las condiciones que limitan la ley de masa.')
    solutions['s7q7'] = s
    q = '¿Qué función cumple la lana mineral dentro de un tabique de doble hoja?'
    s = 'Absorbe y amortigua la energía dentro de la cámara, reduce la severidad de resonancias y mejora el sistema. **No aporta aislamiento por sí sola ni sustituye el desacoplamiento**, la masa o el sellado.'
    formative_development(7, 's7q8', q, s, [['absor', 'amort'], ['cámara', 'camara', 'resonan'], ['no', 'desacopl', 'masa']], 'Evita atribuirle a la lana mineral toda la capacidad aislante del tabique.')
    solutions['s7q8'] = s
    q = 'Un muro de alto aislamiento incorpora una ventana pequeña de bajo R. ¿Cómo puede afectar esa ventana al aislamiento global?'
    s = 'Puede dominar el resultado global porque su τ es mucho mayor que el del muro. Se deben combinar los coeficientes de transmisión ponderados por área; **no se promedian los dB**.'
    formative_development(7, 's7q9', q, s, [['domina', 'reduce', 'debil'], ['coeficiente', 'tau', 'transmis'], ['área', 'area'], ['no', 'promedi']], 'Explica por qué una superficie pequeña puede transportar una fracción grande de la energía.')
    solutions['s7q9'] = s
    q = 'El muro separador fue mejorado, pero el ruido sigue llegando por la unión con el cielo y el piso. ¿Qué fenómeno ocurre y cómo se aborda?'
    s = 'Existe **transmisión indirecta o por flancos**. Deben diagnosticarse los encuentros y vías estructurales, controlar continuidades rígidas, sellar pasos y diseñar el conjunto constructivo, no solo el paño separador.'
    formative_development(7, 's7q10', q, s, [['flanco', 'indirect'], ['cielo', 'piso', 'encuentro'], ['vía', 'via', 'estructura', 'sell']], 'Nombra la trayectoria real y propone una intervención sobre ese encuentro.')
    solutions['s7q10'] = s
    q = 'Un muro de 12 m² tiene R = 55 dB e incorpora una puerta de 2 m² con R = 25 dB. Calcula el R compuesto.'
    tau_total = (12 * 10 ** (-55 / 10) + 2 * 10 ** (-25 / 10)) / 14
    r_total = -10 * math.log10(tau_total)
    s = f'τtotal = [12·10^(−55/10)+2·10^(−25/10)]/14. Por tanto, **Rtotal ≈ {r_total:.1f} dB**. La puerta reduce drásticamente el desempeño del conjunto.'
    formative_numeric(7, 's7q11', q, [('r', 'R compuesto (dB)', 0.0, 0.1)], lambda v: (abs(v['r'] - r_total) <= 0.3, f'El resultado esperado es aproximadamente {r_total:.1f} dB; combina τ ponderados por superficie.'), s)
    solutions['s7q11'] = s
    score_counter(7)
    teacher_group_review(7, solutions)

def lab1_stage8():
    header('ETAPA 8 · MATERIA + INTERPRETACIÓN', 'Índices de aislamiento acústico', 'Los números únicos permiten comparar, pero deben corresponder al método, lugar y espectro del problema.')
    full_matter(8)
    data = [('R(f)', 'Reducción por banda', 'Laboratorio/curva'), ('Rw', 'Reducción ponderada', 'Laboratorio ISO'), ('R′w', 'Reducción aparente', 'Terreno, incluye vías laterales'), ('DₙT,w', 'Diferencia estandarizada', 'Entre recintos, corregida por T'), ('D₂m,nT,w', 'Diferencia de fachada', 'Exterior a 2 m'), ('STC / ASTC', 'Clasificación ASTM', 'Laboratorio / terreno'), ('OITC', 'Exterior–interior', 'Transporte y bajas frecuencias'), ('CAC', 'Paso por cielo/plenum', 'Cielos suspendidos')]
    st.dataframe(pd.DataFrame(data, columns=['Indicador', 'Representa', 'Contexto']), hide_index=True, use_container_width=True)
    formula_card('Índice ponderado y términos de adaptación', 'R_w(C;C_{tr})=52(-2;-7)\\,\\mathrm{dB}\\Rightarrow R_w+C=50\\,\\mathrm{dB},\\;R_w+C_{tr}=45\\,\\mathrm{dB}', '<b>Rw</b>: valor ponderado ISO<br><b>C</b>: adaptación para espectros medios-altos<br><b>Ctr</b>: adaptación para tránsito y contenido grave', 'Para adaptar el índice global al espectro de la fuente. C y Ctr se suman algebraicamente; no son aislamientos independientes.')
    source = st.selectbox('Fuente a evaluar', ['Voz / actividades domésticas', 'Tránsito, buses o bajos', 'Fachada bajo criterio ASTM', 'Fuente tonal industrial'])
    recommendation = {'Voz / actividades domésticas': 'Revisar Rw y Rw+C.', 'Tránsito, buses o bajos': 'Priorizar Rw+Cₜᵣ y la curva grave.', 'Fachada bajo criterio ASTM': 'Revisar OITC además de STC.', 'Fuente tonal industrial': 'La curva completa en la banda tonal es indispensable.'}[source]
    st.info(recommendation)
    check('e8', 'Un tabique tiene Rw=55 dB en laboratorio y R′w=47 dB en obra. ¿El laboratorio estaba necesariamente equivocado?', ['Sí', 'No; montaje y vías laterales pueden explicar la diferencia'], 'No; montaje y vías laterales pueden explicar la diferencia', 'R′w incorpora el comportamiento aparente de la construcción instalada.')

def lab1_stage9():
    header('ETAPA 9 · APLICACIÓN PRÁCTICA', 'Interpretación de índices acústicos', 'Relaciona cada índice con su definición, contexto de medición y uso correcto.')
    full_matter(9)
    st.markdown('### Actividad · Relaciona los términos pareados')
    st.markdown('En la columna izquierda aparecen los índices acústicos. En la derecha están las definiciones numeradas y mezcladas. Selecciona junto a cada índice el número que le corresponde.')
    paired_terms = {'R': 'Índice por banda de frecuencia que expresa la reducción sonora de un elemento en laboratorio.', 'R_w': 'Índice único ponderado ISO obtenido al ajustar una curva de referencia a resultados de laboratorio.', 'R′_w': 'Índice único aparente medido en obra, que incorpora montaje, encuentros y transmisiones laterales.', 'D_nT,w': 'Diferencia de niveles entre recintos, normalizada por el tiempo de reverberación y ponderada.', 'D_2m,nT,w': 'Diferencia de niveles de fachada medida con el nivel exterior a 2 m, normalizada y ponderada.', 'C': 'Término de adaptación espectral asociado principalmente a ruido rosa y fuentes de contenido medio-alto.', 'Cₜᵣ': 'Término de adaptación espectral apropiado para tránsito y fuentes con contenido importante en bajas frecuencias.', 'STC': 'Clasificación ASTM de número único usada principalmente para particiones interiores.', 'OITC': 'Clasificación ASTM orientada al aislamiento frente a ruido exterior, especialmente transporte.', 'CAC': 'Clasificación del aislamiento entre recintos que comparten un cielo suspendido y plenum.'}
    definitions = list(paired_terms.values())
    mixed_order = [7, 2, 5, 0, 8, 3, 9, 1, 6, 4]
    numbered_definitions = {number: definitions[source_index] for number, source_index in enumerate(mixed_order, 1)}
    correct_numbers = {term: next((number for number, definition in numbered_definitions.items() if definition == correct_definition)) for term, correct_definition in paired_terms.items()}
    placeholder = '—'
    selections = {}
    left, right = st.columns([0.85, 2.15], gap='large')
    with left:
        st.markdown('#### Índices o descriptores')
        for idx, term in enumerate(paired_terms):
            row_label, row_value = st.columns([1.2, 0.8])
            row_label.markdown(f'**{term}**')
            selections[term] = row_value.selectbox(f'Número para {term}', [placeholder] + list(range(1, 11)), key=f'e9_pair_number_{idx}', label_visibility='collapsed')
    with right:
        st.markdown('#### Definiciones numeradas')
        for number, definition in numbered_definitions.items():
            st.markdown(f'<div class="card" style="margin:.28rem 0;padding:.72rem .9rem"><b style="color:#0871bd">{number}.</b> {definition}</div>', unsafe_allow_html=True)
    if st.button('Comprobar términos pareados', key='e9_check_pairs', type='primary'):
        unanswered = [term for term, value in selections.items() if value == placeholder]
        if unanswered:
            st.warning(f"Completa todas las relaciones. Faltan: {', '.join(unanswered)}.")
        else:
            correct_count = sum((selections[term] == correct_numbers[term] for term in paired_terms))
            pair_score = correct_count * 2
            level = 'Correcta' if correct_count == len(paired_terms) else 'Parcialmente correcta' if correct_count >= 4 else 'Incorrecta'
            _save_formative(9, 'e9_pairs', 'Relaciona cada índice acústico con su definición.', json.dumps(selections, ensure_ascii=False), level, f'{correct_count} de {len(paired_terms)} relaciones correctas.', score=pair_score, max_score=20)
            if correct_count == len(paired_terms):
                st.success('¡Correcto! Relacionaste adecuadamente los 10 términos acústicos.')
            else:
                st.warning(f'Obtuviste {correct_count} de {len(paired_terms)} relaciones correctas.')
                for term, correct_definition in paired_terms.items():
                    if selections[term] != correct_numbers[term]:
                        st.error(f'{term}: la relación seleccionada no corresponde. El número correcto es {correct_numbers[term]}: {correct_definition}', icon='↔️')
            repeated = {number for number in range(1, 11) if list(selections.values()).count(number) > 1}
            if repeated:
                st.info(f"Revisa los números repetidos ({', '.join(map(str, sorted(repeated)))}): cada definición se utiliza una sola vez.")
    score_counter(9)
    if st.session_state.get('role') == 'Docente':
        with st.expander('👩\u200d🏫 Pauta docente · Términos pareados'):
            st.markdown('Proyecte primero las relaciones sin revelar la pauta. Pida que el curso justifique especialmente las diferencias entre laboratorio, obra, recintos y fachada.')
            if st.checkbox('Mostrar solución de términos pareados', key='e9_reveal_pairs'):
                st.dataframe(pd.DataFrame([{'Término': term, 'N.º correcto': correct_numbers[term], 'Definición correcta': definition} for term, definition in paired_terms.items()]), hide_index=True, use_container_width=True)
                st.info('Tip técnico: la prima en R′w identifica desempeño aparente en obra; el subíndice 2m identifica fachada; nT indica normalización por reverberación. C y Cₜᵣ no son índices independientes: se suman algebraicamente a Rw.')
        teacher_group_review(9, {'e9_pairs': 'Cada uno de los 10 términos debe asociarse una sola vez con la definición mostrada en la pauta docente.'})

LAB1_QUESTIONS = [('La trayectoria incluye principalmente:', ['La partición y sus fugas', 'Solo el oído', 'Solo la fuente'], 0), ('La absorción reduce principalmente:', ['La reverberación interior', 'La masa del muro', 'El ruido emitido'], 0), ('A = Σ(S·α) representa:', ['Absorción equivalente', 'Masa superficial', 'Costo del ciclo'], 0), ('Sabine relaciona:', ['V, A y T₆₀', 'R, STC y OITC', 'Costo, ROI y vida útil'], 0), ('Si A aumenta con V constante, T₆₀:', ['Disminuye', 'Aumenta', 'No cambia'], 0), ('Antes de comparar ROI se debe:', ['Verificar suficiencia acústica', 'Elegir lo más barato', 'Promediar dB'], 0), ('ROI compara:', ['Beneficio neto con costo total', 'R con frecuencia', 'Área con volumen'], 0), ('Payback expresa:', ['Tiempo de recuperación', 'Vida útil acústica', 'Frecuencia crítica'], 0), ('El punto de equilibrio es:', ['Donde el beneficio adicional deja de justificar el costo', 'El mayor R posible', 'El menor precio siempre'], 0), ('Una solución que no cumple la meta:', ['Se descarta o rediseña', 'Gana si tiene buen ROI', 'Se aprueba por vida útil'], 0), ('τ es:', ['Energía transmitida/incidente', 'R promedio', 'Absorción total'], 0), ('R se expresa en:', ['dB', 'sabin', 'segundos'], 0), ('Duplicar masa en ley de masa aporta cerca de:', ['6 dB', '1 dB', '20 dB'], 0), ('La coincidencia puede producir:', ['Una caída de R', 'Aislamiento infinito', 'Mayor absorción Sabine'], 0), ('La lana en una cámara ayuda a:', ['Amortiguar resonancias', 'Crear puentes rígidos', 'Eliminar sellos'], 0), ('Una rendija puede:', ['Dominar la transmisión', 'Mejorar R', 'Aumentar masa'], 0), ('Los R de elementos compuestos se combinan mediante:', ['τ ponderado por área', 'Promedio aritmético', 'Suma directa'], 0), ('Transmisión flanqueante significa:', ['Vía indirecta alrededor del separador', 'Reflexión interior', 'Medición a 2 m'], 0), ('R(f) es:', ['Resultado por banda', 'Un único índice', 'Costo por dB'], 0), ('Rw corresponde principalmente a:', ['Laboratorio ISO', 'Terreno ASTM', 'Absorción'], 0), ('R′w incorpora:', ['Comportamiento aparente en obra', 'Solo el material aislado', 'ROI'], 0), ('DₙT,w corrige mediante:', ['Tiempo de reverberación', 'Costo de montaje', 'Masa'], 0), ('D₂m,nT,w se usa en:', ['Fachadas', 'Cielos plenums', 'ROI'], 0), ('OITC es especialmente útil para:', ['Ruido exterior de transporte', 'Eco interior', 'Impactos exclusivamente'], 0), ('Cₜᵣ se asocia a:', ['Tránsito y contenido grave', 'Solo agudos', 'Reverberación'], 0), ('STC y Rw:', ['No tienen conversión fija universal', 'Siempre difieren en 2', 'Son idénticos'], 0), ('CAC evalúa:', ['Paso por cielos y plenums', 'Fachada a 2 m', 'Tiempo de recuperación'], 0), ('Para una fuente tonal debe priorizarse:', ['Curva por bandas', 'Solo el índice mayor', 'Solo el costo'], 0), ('Rw es:', ['Valor de referencia ajustada en 500 Hz', 'Promedio de R', 'R medido siempre en 500 Hz'], 0)]

def _lab1_final_submission():
    """Return the student's definitive Lab 1 submission, if it exists."""
    client=_supabase()
    user_key=st.session_state.get('user_key')
    if client is None or not user_key:
        return None
    try:
        rows=(client.table('responses').select('*')
              .eq('class_id',CLASS_ID).eq('user_key',user_key)
              .eq('stage',10).eq('question_key','final_exam')
              .limit(1).execute().data or [])
    except Exception:
        return None
    if not rows:
        return None
    row=rows[0]
    payload=_stage9_answer_payload(row)
    return {'row':row,'payload':payload if isinstance(payload,dict) else {}}

def _lab1_case_score(calc,diff,pct,bands,choice,justification):
    practical=0
    practical += 3 if abs(float(calc)-0.4025)<=0.03 else 0
    practical += 2 if set(bands or [])=={125,250,500} else 0
    practical += 3 if choice=='Solución B' else 0
    practical += 2 if abs(float(diff)-300000)<=10000 else 0
    practical += 2 if abs(float(pct)-16.7)<=0.5 else 0
    words=str(justification or '').lower()
    practical += 4 if all(k in words for k in ['costo','125']) else 2 if words.strip() else 0
    practical += 4 if any(k in words for k in ['vida útil','cumple','objetivo','grave','250']) else 0
    return min(20,practical)

def _finish_lab1_final(reason='submitted'):
    answers=dict(st.session_state.get('lab1_final_answers',{}))
    answers={str(i):answers.get(str(i)) for i in range(29)}
    answer_indexes={}
    hits=0
    for i,(_,options,correct) in enumerate(LAB1_QUESTIONS):
        selected=answers[str(i)]
        answer_indexes[str(i)]=options.index(selected) if selected in options else None
        hits += int(selected==options[correct])
    practical=_lab1_case_score(
        st.session_state.get('case_calc',0),st.session_state.get('case_diff',0),
        st.session_state.get('case_pct',0),st.session_state.get('case_bands',[]),
        st.session_state.get('case_choice'),st.session_state.get('case_justification',''),
    )
    theory_score=hits/29*80
    total=theory_score+practical
    payload={
        'respuestas_teoricas':answer_indexes,'respuestas_texto':answers,
        'aciertos_teoricos':hits,'puntaje_teorico':theory_score,
        'puntaje_caso':practical,'reason':reason,'finished_at':_now(),
        'caso_integrador':{
            'volumen':st.session_state.get('case_V',50.0),
            'absorcion':st.session_state.get('case_A',20.0),
            't60':st.session_state.get('case_calc',0),
            'diferencia_costo':st.session_state.get('case_diff',0),
            'incremento_porcentual':st.session_state.get('case_pct',0),
            'bandas_criticas':st.session_state.get('case_bands',[]),
            'recomendacion':st.session_state.get('case_choice'),
            'justificacion':st.session_state.get('case_justification',''),
        },
    }
    _save_formative(
        10,'final_exam','Evaluación final del Curso 1',
        json.dumps(payload,ensure_ascii=False),
        'Correcta' if total>=60 else 'Incorrecta',
        f'Teoría: {hits}/29 aciertos ({theory_score:.1f}/80). Caso práctico: {practical}/20 puntos.',
        score=total,max_score=100,
        correct_answer=('Pauta: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; '
                        'bandas 125, 250 y 500 Hz; Solución B.'),
    )
    st.session_state['lab1_exam_submitted']=True
    st.session_state['exam_result']=(hits,practical,total)
    save_user_progress()

def lab1_stage10():
    header('ETAPA 10 · EVALUACIÓN FINAL', 'Evaluación práctica final · Aislamiento a Ruido Aéreo', '30 preguntas: 29 teórico-aplicadas y un caso integrador con costo-beneficio.')
    full_matter(10)
    if st.session_state.get('role')=='Docente':
        st.info('Vista docente: pauta de consulta. El docente no desarrolla esta evaluación.')
        for i,(question,options,correct) in enumerate(LAB1_QUESTIONS):
            with st.expander(f'Pregunta {i+1} · {question}',expanded=i==0):
                for option_index,option in enumerate(options):
                    st.write(f"{'✅' if option_index==correct else '○'} {chr(65+option_index)}. {option}")
        st.markdown('### Respuestas y rúbrica de alumnos')
        _teacher_lab1_final_results()
        return

    remote=_lab1_final_submission()
    if remote or st.session_state.get('lab1_exam_submitted'):
        payload=(remote or {}).get('payload',{})
        row=(remote or {}).get('row',{})
        answers=payload.get('respuestas_teoricas',{})
        hits=int(payload.get('aciertos_teoricos',0) or 0)
        practical=float(payload.get('puntaje_caso',0) or 0)
        total=float(row.get('auto_score',hits/29*80+practical) or 0)
        st.success(f'Evaluación enviada y guardada · Puntaje: {total:.1f}/100')
        st.caption('El intento está cerrado. Tus respuestas permanecen disponibles al cerrar sesión o volver a ingresar.')
        with st.expander('Revisar respuestas 1 a 29'):
            for i,(question,options,correct) in enumerate(LAB1_QUESTIONS):
                raw=answers.get(str(i),answers.get(i)) if isinstance(answers,dict) else None
                try: selected=int(raw) if raw is not None else None
                except (TypeError,ValueError): selected=None
                chosen=options[selected] if selected is not None and 0<=selected<len(options) else 'Sin respuesta'
                st.markdown(f"**{'✅' if selected==correct else '❌'} {i+1}. {question}**")
                st.write(f'Tu respuesta: {chosen}')
                st.caption(f'Respuesta correcta: {options[correct]}')
        st.info('Pauta del caso: T₆₀≈0,40 s; diferencia $300.000; incremento 16,7%; bandas 125, 250 y 500 Hz; Solución B.')
        return

    tab1, tab2 = st.tabs(['Preguntas 1 a 29', 'Pregunta 30 · Caso práctico'])
    with tab1:
        # Keep every answer in a durable dictionary. Only one radio widget is
        # rendered at a time, and Streamlit removes hidden widget keys when the
        # student changes question; the dictionary must therefore be the source
        # of truth for progress and Supabase persistence.
        if not isinstance(st.session_state.get('lab1_final_answers'),dict):
            # Migrate any answer saved by APP 112-114 under the former q0..q28
            # widget keys, so the student's existing progress is not discarded.
            st.session_state['lab1_final_answers']={
                str(i):st.session_state.get(f'q{i}')
                for i in range(29) if st.session_state.get(f'q{i}') is not None
            }
        draft_answers=st.session_state['lab1_final_answers']
        qn = st.selectbox('Pregunta', range(29), format_func=lambda i: f'Pregunta {i + 1}')
        q, opts, correct = LAB1_QUESTIONS[qn]
        st.markdown(f'<div class="question-box"><div class="question-label">PREGUNTA {qn + 1} DE 29</div><div class="question-text">{q}</div></div>', unsafe_allow_html=True)
        saved_answer=draft_answers.get(str(qn))
        radio_index=opts.index(saved_answer) if saved_answer in opts else None
        ans = st.radio('Selecciona una alternativa', opts, index=radio_index,
                       key=f'_lab1_visible_q{qn}', label_visibility='collapsed')
        if st.button('Guardar respuesta', key=f'save{qn}'):
            if ans is None:
                st.warning('Selecciona una alternativa.')
            else:
                draft_answers[str(qn)]=ans
                st.session_state['lab1_final_answers']=draft_answers
                save_user_progress()
                st.success('Respuesta guardada.')
        answered=sum(draft_answers.get(str(i)) is not None for i in range(29))
        hits=sum(draft_answers.get(str(i))==LAB1_QUESTIONS[i][1][LAB1_QUESTIONS[i][2]] for i in range(29))
        theory_score=hits/29*80
        st.progress(answered/29)
        st.caption(f'{answered} de 29 respuestas registradas · Puntaje teórico acumulado: {theory_score:.1f}/80')
    with tab2:
        st.markdown('<div class="question-box"><div class="question-label">PREGUNTA 30 · CASO PROFESIONAL INTEGRADOR</div><div class="question-text">¿Qué solución recomendarías para proteger un dormitorio contiguo a una sala de máquinas?</div><p>La fuente domina en 125, 250 y 500 Hz. Calcula, compara y justifica tu decisión técnico-económica.</p></div>', unsafe_allow_html=True)
        df = pd.DataFrame({'Indicador': ['Rw', 'Cₜᵣ', 'Rw+Cₜᵣ', 'R en 125 Hz', 'R en 250 Hz', 'R en 500 Hz', 'Costo instalado', 'Vida útil'], 'Solución A': ['52 dB', '−9 dB', '43 dB', '27 dB', '34 dB', '47 dB', '$1.800.000', '20 años'], 'Solución B': ['49 dB', '−4 dB', '45 dB', '34 dB', '39 dB', '45 dB', '$2.100.000', '25 años']})
        st.dataframe(df, hide_index=True, use_container_width=True)
        c1, c2 = st.columns(2)
        V = c1.number_input('V (m³)', 1.0, 500.0, 50.0, key='case_V')
        A = c2.number_input('A (m² sabin)', 1.0, 200.0, 20.0, key='case_A')
        calc = st.number_input('Calcula T₆₀ (s)', 0.0, 10.0, 0.0, 0.01, key='case_calc')
        diff = st.number_input('Diferencia de costo ($)', 0, 5000000, 0, step=50000, key='case_diff')
        pct = st.number_input('Incremento porcentual de B respecto de A (%)', 0.0, 200.0, 0.0, 0.1, key='case_pct')
        bands = st.multiselect('Bandas críticas', [125, 250, 500, 1000], key='case_bands')
        choice = st.radio('Recomendación', ['Solución A', 'Solución B'], index=None, key='case_choice')
        justification = st.text_area('Justificación técnico-económica', key='case_justification')
        practical_live=_lab1_case_score(calc,diff,pct,bands,choice,justification)
        draft_answers=st.session_state.get('lab1_final_answers',{})
        theory_hits=sum(draft_answers.get(str(i))==LAB1_QUESTIONS[i][1][LAB1_QUESTIONS[i][2]] for i in range(29))
        theory_live=theory_hits/29*80
        st.markdown(f'<div class="good"><b>Puntaje acumulado: {theory_live+practical_live:.1f}/100</b><br>Teoría: {theory_live:.1f}/80 · Caso práctico: {practical_live}/20.</div>',unsafe_allow_html=True)
        answered=sum(draft_answers.get(str(i)) is not None for i in range(29))
        if st.button('Enviar evaluación definitiva',type='primary',use_container_width=True,key='lab1_final_submit'):
            if answered<29 or choice is None or not justification.strip():
                st.session_state['lab1_confirm_incomplete']=True
                st.warning('La evaluación tiene respuestas pendientes. Revísalas antes del envío definitivo.')
            else:
                try:
                    _finish_lab1_final('submitted')
                    st.rerun()
                except Exception as exc:
                    st.error(f'No fue posible enviar la evaluación. Tus respuestas continúan guardadas como avance. Detalle: {exc}')
        if st.session_state.get('lab1_confirm_incomplete'):
            if st.button('Confirmar envío con respuestas pendientes',key='lab1_final_submit_incomplete'):
                try:
                    _finish_lab1_final('submitted_incomplete')
                    st.rerun()
                except Exception as exc:
                    st.error(f'No fue posible enviar la evaluación. Tus respuestas continúan guardadas como avance. Detalle: {exc}')

# ---------------------------------------------------------------------------
# Laboratorio 2 · ruta profesional MINVU / CES / ISO 12354
# Esta ruta es independiente del Laboratorio 1. No reutiliza sus etapas.
# ---------------------------------------------------------------------------
LAB2_MINUTES = [15, 20, 25, 35, 35, 25, 35, 20, 20, 10, 60]

def _lab2_heading(stage, title, purpose):
    header(
        f"ETAPA {stage} · LABORATORIO 2",
        title,
        purpose,
        show_overview=False,
        duration_minutes=LAB2_MINUTES[stage],
    )

def lab2_stage0():
    _lab2_heading(0, "Ruta profesional de cuatro horas",
                  "Del requerimiento acústico a una recomendación verificable, construible y defendible.")
    st.markdown(r"""
    ### Resultado de aprendizaje
    Al finalizar podrás transformar un requerimiento CES/MINVU en una solución de separación interior,
    distinguir el descriptor correcto, estimar el desempeño instalado y controlar los puntos débiles.
    """)
    st.dataframe(pd.DataFrame([
        ["00:00–00:15","Apertura, objetivos y antecedentes del encargo"],
        ["00:15–00:35","Requerimientos CES usados en la asesoría MINVU"],
        ["00:35–01:00","Rw, C, Ctr, R′w, DnT,w y DnT,A"],
        ["01:00–01:35","Modelos: placa simple, coincidencia, Sharp y masa–aire–masa"],
        ["01:35–02:10","Cinco problemas numéricos resueltos"],
        ["02:10–02:20","Pausa"],
        ["02:20–02:45","Aplicación didáctica de ISO 12354"],
        ["02:45–03:20","Caso guiado: Sala de Reuniones Dirección"],
        ["03:20–03:40","TA-01 y comparación de tres soluciones"],
        ["03:40–04:00","Puertas, aislamiento compuesto y preparación de evaluación"],
    ], columns=["Minutos","Actividad"]), hide_index=True, use_container_width=True)
    st.info("La evaluación individual de la Sala de Reuniones Licitaciones se abre únicamente cuando el docente la publica.")

def lab2_stage1():
    _lab2_heading(1, "Del requerimiento CES al criterio de diseño",
                  "Separar exigencia, descriptor, recinto, condición de ensayo y margen de proyecto.")
    st.markdown(r"""
    ### Lectura correcta del encargo

    1. Identifica el par de recintos y el elemento separador.
    2. Confirma si el valor corresponde a laboratorio, edificio terminado o diferencia entre recintos.
    3. Conserva el descriptor escrito en el requerimiento: no reemplaces automáticamente \(D_{nT,A}\) por \(R_w\).
    4. Registra el espectro relevante: voz, tránsito, instalaciones u otra fuente.
    5. Define un margen de diseño y las pérdidas previsibles de obra.

    **Regla profesional:** una solución no cumple porque su ficha tenga un \(R_w\) mayor que la meta.
    Debe existir una cadena de cálculo que conecte el elemento ensayado con la condición instalada.
    """)
    st.warning("Los valores del caso MINVU se usan como antecedentes de una asesoría específica. No deben presentarse como exigencias universales para todo edificio.")

def lab2_stage2():
    _lab2_heading(2, "Descriptores sin confusiones",
                  "Elegir el indicador que responde a la pregunta técnica real.")
    st.dataframe(pd.DataFrame([
        ["R(f)","Laboratorio, por banda","Reducción sonora del elemento ensayado"],
        ["Rw","Laboratorio, índice único","Valor ponderado ISO 717-1 del elemento"],
        ["C / Ctr","Adaptación espectral","Corrección según familia de espectro; Ctr penaliza más el contenido grave de tránsito"],
        ["R′w","Edificio terminado","Reducción aparente; incorpora montaje y transmisiones laterales"],
        ["DnT,w","Entre recintos","Diferencia de niveles normalizada al tiempo de reverberación"],
        ["DnT,A","Entre recintos, ponderación A","Valor asociado al espectro normalizado que exige el encargo"],
    ], columns=["Descriptor","Ámbito","Qué representa"]), hide_index=True, use_container_width=True)
    st.latex(r"D_{nT}=L_1-L_2+10\log_{10}\left(\frac{T}{T_0}\right),\qquad T_0=0.5\ \mathrm{s}")
    st.markdown(r"**No existe una conversión universal fija** entre \(R_w\), \(R'_w\) y \(D_{nT,w}\). La geometría, absorción, montaje y flancos cambian el resultado.")

def lab2_stage3():
    _lab2_heading(3, "Modelos de predicción de la tesis",
                  "Reconocer el alcance y las limitaciones de cada modelo antes de calcular.")
    st.dataframe(pd.DataFrame([
        ["Ley de masa","Placa simple, zona controlada por masa",r"R≈20 log10(m·f)−47","No representa resonancia ni coincidencia"],
        ["Coincidencia","Placas delgadas",r"fc depende de masa, rigidez y espesor","Produce una pérdida localizada de aislamiento"],
        ["Sharp","Placas simples reales","Ajuste por regiones alrededor de fc","Útil como modelo semiempírico, no sustituye un ensayo"],
        ["Masa–aire–masa","Sistemas dobles","Dos hojas + cámara + absorbente","La resonancia puede degradar bajas frecuencias"],
    ], columns=["Modelo","Uso","Idea de cálculo","Advertencia"]), hide_index=True, use_container_width=True)
    m=st.slider("Masa superficial de la placa (kg/m²)",5,80,25,key="lab2_model_m")
    f=st.select_slider("Frecuencia (Hz)",options=[100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150],value=500,key="lab2_model_f")
    st.metric("Predicción ideal por ley de masa",f"{float(mass_r(m,f)):.1f} dB")
    st.caption("Es una referencia ideal por banda; no es Rw ni desempeño garantizado en obra.")

def lab2_stage4():
    _lab2_heading(4, "Cinco problemas numéricos resueltos",
                  "Seguir datos, fórmula, sustitución, unidad e interpretación.")
    problems=[
        ("1 · Ley de masa","m=25 kg/m²; f=500 Hz",r"R=20\log_{10}(25·500)-47=34.9\ \mathrm{dB}","Predicción ideal por banda, no Rw."),
        ("2 · Término espectral","Rw=52 dB; C=−3 dB",r"R_w+C=52-3=49\ \mathrm{dB}","La adaptación espectral reduce el valor útil para ese espectro."),
        ("3 · Diferencia normalizada","L1=85 dB; L2=48 dB; T=0.8 s",r"D_{nT}=85-48+10\log_{10}(0.8/0.5)=39.0\ \mathrm{dB}","Normalizar permite comparar recintos con distinta reverberación."),
        ("4 · Elemento compuesto","Muro 8.11 m² a 49 dB; puerta 1.89 m² a 31 dB",r"R_{comp}=-10\log_{10}\frac{8.11·10^{-4.9}+1.89·10^{-3.1}}{10}=38.1\ \mathrm{dB}","La puerta domina pese a ocupar menos área."),
        ("5 · Paso a desempeño estimado","Rcomp,A=38.1 dB; Kgeo=3.2 dB; obra=3 dB",r"D_{nT,A}\approx38.1+3.2-3.0=38.3\ \mathrm{dB}","El margen debe verificarse, no suponerse."),
    ]
    for title,data,development,meaning in problems:
        with st.expander(title, expanded=title.startswith("1")):
            st.write(f"**Datos:** {data}")
            st.latex(development)
            st.write(f"**Interpretación:** {meaning}")
    check("lab2_p4","¿Qué componente suele controlar una separación compuesta?",["El de mayor área","El de menor aislamiento ponderado por su área","El más caro"],"El de menor aislamiento ponderado por su área","La combinación debe hacerse energéticamente; los dB no se promedian.")

def lab2_stage5():
    _lab2_heading(5, "ISO 12354 como puente de diseño",
                  "Pasar del dato del elemento al comportamiento esperado del edificio.")
    st.markdown(r"""
    ### Secuencia didáctica simplificada

    **1. Entrada:** curva o índice del elemento ensayado.  
    **2. Geometría:** área separadora, volumen receptor y absorción/tiempo de reverberación.  
    **3. Caminos:** transmisión directa más contribuciones laterales.  
    **4. Resultado:** aislamiento aparente o diferencia normalizada, según la magnitud requerida.  
    **5. Verificación:** comparar con la meta, margen y condiciones reales de ejecución.

    La aplicación usa una aproximación pedagógica para seguir la cadena de decisiones.
    No debe etiquetarse como cálculo normativo completo cuando no se modelan todas las uniones y vías laterales.
    """)
    st.latex(r"R'=-10\log_{10}\left(\tau_d+\sum \tau_{flanco}\right)")
    st.info("La contribución total se suma en energía. Una vía lateral débil puede limitar el desempeño aunque el tabique directo sea excelente.")

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


def lab2_stage6():
    _lab2_heading(6, "Ejercicio guiado · Sala de Reuniones Dirección",
                  "Resolver el caso junto al docente y documentar cada decisión.")
    st.image(str(ROOT/"assets/course_visuals/stage6_double_wall.webp"),use_container_width=True)
    st.markdown(r"""
    ### Ficha de trabajo

    - Delimita emisor, receptor y separación.
    - Calcula volumen receptor, superficie total, puerta y paño opaco.
    - Selecciona el descriptor exigido.
    - Compara el valor de laboratorio con la estimación instalada.
    - Declara margen, pérdida de obra y controles de constructibilidad.
    """)
    cad_viewer_button(6)
    response=st.text_area("Conclusión guiada del equipo",key="lab2_direccion_conclusion",
                          placeholder="Descriptor, solución, resultado, margen, punto débil y controles de obra.")
    if st.button("Guardar conclusión guiada",key="lab2_save_direccion"):
        if len(response.strip())<40:
            st.warning("Desarrolla una conclusión técnica más completa.")
        else:
            _save_formative(6,"direccion_guiada","Caso guiado · Sala de Reuniones Dirección",
                            response,"Correcta","Conclusión enviada para revisión docente.",score=10,max_score=10)
            st.success("Conclusión guardada.")
    score_counter(6)

def lab2_stage7():
    _lab2_heading(7, "Comparación de tres soluciones",
                  "Contrastar la TA-01 original con alternativas técnicamente viables.")
    st.dataframe(pd.DataFrame([
        ["Solución 1","TA-01 original",60,-4,56,140,92000],
        ["Solución 2","Tabique reforzado desacoplado",52,-3,49,140,68000],
        ["Solución 3","Tabique básico mejorado",47,-2,45,100,45000],
    ],columns=["Alternativa","Sistema","Rw","C","Rw+C","Espesor (mm)","Costo ($/m²)"]),
        hide_index=True,use_container_width=True)
    choice=st.radio("¿Qué solución debe recomendarse?",[
        "Siempre TA-01 porque tiene el Rw más alto",
        "La de menor costo que cumpla con margen después de considerar puerta y obra",
        "Siempre la alternativa más barata",
    ],index=None,key="lab2_solution_choice")
    reason=st.text_area("Justificación",key="lab2_solution_reason")
    if st.button("Enviar comparación",key="lab2_solution_submit"):
        correct=choice=="La de menor costo que cumpla con margen después de considerar puerta y obra"
        score=(6 if correct else 0)+(4 if len(reason.strip())>=50 else 2 if reason.strip() else 0)
        _save_formative(7,"compare_solutions","Comparación TA-01 y alternativas",
                        json.dumps({"seleccion":choice,"justificacion":reason},ensure_ascii=False),
                        "Correcta" if score>=6 else "Parcialmente correcta",
                        "La selección final depende del sistema compuesto, margen y constructibilidad.",score=score,max_score=10)
        st.success(f"Respuesta guardada: {score}/10 puntos.")
    score_counter(7)

def lab2_stage8():
    _lab2_heading(8, "Aislamiento compuesto y efecto de puertas",
                  "Comprobar por qué una abertura pequeña puede controlar el resultado.")
    wall_area=8.11
    door_area=1.89
    rw_wall=st.slider("Rw+C del paño opaco (dB)",35,60,49,key="lab2_wall_rating")
    rw_door=st.slider("Rw+C de la puerta (dB)",15,45,31,key="lab2_door_rating")
    result=compound_r([wall_area,door_area],[rw_wall,rw_door])
    st.metric("Aislamiento compuesto estimado",f"{result:.1f} dB")
    st.caption(f"Paño opaco: {wall_area:.2f} m² · Puerta: {door_area:.2f} m².")
    st.latex(r"R_{comp}=-10\log_{10}\left(\frac{\sum S_i10^{-R_i/10}}{\sum S_i}\right)")
    answer=st.text_area("¿Qué especificación constructiva agregarías a la puerta?",key="lab2_door_control")
    if st.button("Guardar análisis de puerta",key="lab2_door_submit"):
        hits=sum(k in answer.lower() for k in ["sello","marco","inferior","burlete","umbral"])
        score=10 if hits>=3 else 6 if hits>=1 else 2
        _save_formative(8,"compound_door","Aislamiento compuesto y puerta",answer,
                        "Correcta" if score>=6 else "Parcialmente correcta",
                        f"Resultado compuesto calculado: {result:.1f} dB.",score=score,max_score=10)
        st.success(f"Análisis guardado: {score}/10 puntos.")
    score_counter(8)

def lab2_stage9():
    _lab2_heading(9, "Preparación de la evaluación individual",
                  "Practicar el método sin revelar el caso evaluado.")
    st.markdown("""
    ### Lista de comprobación

    - Descriptor y meta correctamente identificados.
    - Geometría y áreas netas calculadas.
    - Conversión energética de muro y puerta.
    - Paso justificado desde laboratorio a estimación instalada.
    - Comparación de alternativas con margen.
    - Controles de obra verificables.
    - Conclusión breve con resultado, costo, riesgo y recomendación.
    """)
    with st.expander("Banco de práctica"):
        st.markdown(r"""
        1. ¿Por qué \(R_w\) no debe compararse directamente con \(D_{nT,A}\)?  
        2. ¿Qué cambia al reemplazar una puerta hueca por una puerta sellada?  
        3. ¿Cuándo usarías \(C\) y cuándo \(C_{tr}\)?  
        4. ¿Qué representa una pérdida de obra?  
        5. ¿Por qué una solución de mayor \(R_w\) puede no ser la recomendación óptima?
        """)
    if st.session_state.get("role")=="Docente":
        with st.expander("🔐 Guion docente y fichas"):
            st.markdown("""
            **Guion de 30 diapositivas:** apertura (1–3), encargo CES/MINVU (4–7),
            descriptores (8–12), modelos de tesis (13–17), problemas resueltos (18–22),
            ISO 12354 (23–25), caso Dirección y alternativas (26–28), evaluación y cierre (29–30).

            **Fichas:** requerimiento; geometría; componentes; comparación; control de obra;
            conclusión profesional. Las soluciones y la evaluación futura permanecen protegidas.
            """)

def lab2_stage10():
    _lab2_heading(10, "Evaluación individual · Sala de Reuniones Licitaciones",
                  "Resolver un caso equivalente con intento único y rúbrica analítica de 100 puntos.")
    cad_viewer_button(10)
    stage10()

# ---------------------------------------------------------------------------
# Laboratorio 2 · Clase de 4 horas con pausa de 30 minutos
# Modelos de predicción del aislamiento a ruido aéreo
# ---------------------------------------------------------------------------
# Laboratorio 2: jornada de 4 horas.
# 210 minutos de trabajo + 30 minutos de pausa después de la Etapa 5.
# Los dos bloques tienen 105 minutos efectivos de trabajo cada uno.
LAB2_MINUTES = [10, 15, 25, 15, 20, 20, 10, 15, 20, 20, 40]
LAB2_BREAK_AFTER_STAGE = 5
LAB2_BREAK_MINUTES = 30
LAB2_ACTIVE_MINUTES = sum(LAB2_MINUTES)
LAB2_TOTAL_MINUTES = LAB2_ACTIVE_MINUTES + LAB2_BREAK_MINUTES
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
    """Mass-controlled limp sheet at one incidence angle."""
    omega = 2*math.pi*frequency
    ratio = omega*mass*max(math.cos(math.radians(theta)), .001)/(2*rho_air*sound_speed)
    return 1.0/(1.0+ratio**2)

def _critical_frequency(rho, h_mm, young_gpa, poisson, sound_speed=343.0):
    h = h_mm/1000
    surface_mass = rho*h
    stiffness = young_gpa*1e9*h**3/(12*(1-poisson**2))
    fc = sound_speed**2/(2*math.pi)*math.sqrt(surface_mass/stiffness)
    return surface_mass, stiffness, fc

def _mass_law_curve(mass):
    return 20*np.log10(np.maximum(mass*LAB2_FREQS, 1))-47

def _simple_real_curve(mass, fc, loss=9):
    base = _mass_law_curve(mass)
    dip = loss*np.exp(-0.5*(np.log2(LAB2_FREQS/fc)/0.30)**2)
    low = 5*np.exp(-0.5*(np.log2(LAB2_FREQS/90)/0.55)**2)
    return base-dip-low

def _sharp_parameters(m1, m2, depth):
    d = max(depth/1000, .01)
    f0 = 60*math.sqrt((1/m1+1/m2)/d)
    fl = max(f0*4, 200)
    return f0, fl

def _sharp_curve(m1, m2, depth, connection="Independiente"):
    f0, fl = _sharp_parameters(m1, m2, depth)
    d = depth/1000
    total = []
    for f in LAB2_FREQS:
        if f < f0:
            value = float(mass_r(m1+m2, f))
        elif f < fl:
            value = float(mass_r(m1, f)+mass_r(m2, f)+20*math.log10(max(f*d, .01))-29)
        else:
            value = float(mass_r(m1, f)+mass_r(m2, f)+6)
        if connection == "Montante compartido":
            value -= 9
        elif connection == "Puente accidental":
            value -= 6
        total.append(value)
    return np.array(total), f0, fl

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

def _lab2_heading(stage, title, purpose):
    header(f"ETAPA {stage} · LABORATORIO 2", title, purpose,
           show_overview=False, duration_minutes=LAB2_MINUTES[stage])

def lab2_stage0():
    header(
        "ETAPA 0 · BIENVENIDA",
        "Laboratorio 2 · Modelos de predicción del aislamiento acústico",
        "Una experiencia visual para reconocer el sistema constructivo, seleccionar el modelo físico y leer correctamente su curva de pérdida de transmisión.",
        show_overview=False,
        duration_minutes=LAB2_MINUTES[0],
    )
    st.markdown(
        f'<div class="class-clock"><div><strong>⏱️ Duración total del laboratorio: 4 horas</strong>'
        f'<br><span>{LAB2_ACTIVE_MINUTES} min de aprendizaje y evaluación + '
        f'{LAB2_BREAK_MINUTES} min de pausa</span>'
        f'</div><div><strong>{LAB2_TOTAL_MINUTES} min</strong></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-band"><span>🗺️</span><h3>Tu ruta de aprendizaje</h3></div>',
        unsafe_allow_html=True,
    )
    route = [
        ("Pérdida de transmisión", "Relaciona la energía incidente y transmitida con τ y TL.", LAB2_MINUTES[1]),
        ("Panel simple", "Reconoce incidencia, rigidez, resonancias, ley de masa y coincidencia.", LAB2_MINUTES[2]),
        ("Comparación de placas", "Compara yeso-cartón, vidrio monolítico y hormigón por bandas.", LAB2_MINUTES[3]),
        ("Panel doble", "Explora masas, cámara de aire, resonancia y conexiones estructurales.", LAB2_MINUTES[4]),
        ("Modelo de Sharp", "Calcula f₀, fₗ y el TL correspondiente en cada tramo.", LAB2_MINUTES[5]),
        ("Ventanas dobles", "Analiza la cámara, las hojas y la pérdida de transmisión del sistema.", LAB2_MINUTES[6]),
        ("Bandas de frecuencia", "Distingue octavas y tercios de octava e interpreta sus curvas.", LAB2_MINUTES[7]),
        ("Rw, C y Ctr", "Obtiene e interpreta el índice ponderado y sus adaptaciones espectrales.", LAB2_MINUTES[8]),
        ("Evaluación de comprensión", "Resuelve 10 preguntas con alternativas en un único intento.", LAB2_MINUTES[9]),
        ("Aplicación integradora", "Desarrolla y justifica la solución del caso técnico final.", LAB2_MINUTES[10]),
    ]
    html = '<div class="route-grid">'
    for i, (title, description, minutes) in enumerate(route, 1):
        html += (
            f'<div class="route-card"><span class="step">{i}</span><div>'
            f'<b>{title}</b><p>{description}</p>'
            f'<span class="route-time">⏱️ {minutes} min</span></div></div>'
        )
    st.markdown(html + "</div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="warn" style="margin-top:1rem"><b>☕ Pausa programada: '
        f'{LAB2_BREAK_MINUTES} minutos</b><br>Se realizará después de la Etapa '
        f'{LAB2_BREAK_AFTER_STAGE}. Primer bloque: 105 min · Pausa: 30 min · '
        f'Segundo bloque: 105 min.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="good" style="margin-top:1rem"><b>Así aprenderás:</b> '
        'concepto visual → fundamento físico → ecuación → simulación → caso real → interpretación de la curva.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="warn" style="margin-top:.8rem"><b>Alcance del modelo:</b> '
        'las predicciones corresponden al elemento idealizado. El resultado construido también '
        'depende del montaje, sellos, encuentros, dimensiones y transmisiones laterales.</div>',
        unsafe_allow_html=True,
    )

def lab2_stage1():
    _lab2_heading(
        1,
        "Pérdida de transmisión: τ, TL y escala decibel",
        "Comprender el decibel como una relación logarítmica y convertir, en ambos sentidos, entre coeficiente de transmisión y pérdida de transmisión.",
    )
    _lab2_image("panel_simple")

    st.markdown("### 1. El decibel no es una cantidad absoluta")
    st.markdown(r"""
    El **decibel (dB)** expresa de forma logarítmica la **relación entre dos cantidades**.
    No es una unidad absoluta como el watt, el metro o el pascal. En relaciones de
    potencia o energía se utiliza:
    """)
    st.latex(r"L=10\log_{10}\left(\frac{W_1}{W_0}\right)")
    st.markdown(r"""
    En acústica las potencias, intensidades y presiones abarcan rangos enormes. La escala
    logarítmica los convierte en valores manejables y permite interpretar órdenes de
    magnitud: una razón energética de 10 equivale a 10 dB; de 100, a 20 dB; y de
    1.000, a 30 dB.
    """)

    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### Nivel de presión sonora")
        st.latex(r"L_p=20\log_{10}\left(\frac{p}{p_0}\right)")
        st.markdown(
            "Compara la presión acústica **p** con la presión de referencia "
            "**p₀ = 20 µPa**. Ejemplo: **85 dB SPL**."
        )
    with c2:
        st.markdown("#### Pérdida de transmisión")
        st.latex(r"TL=10\log_{10}\left(\frac{W_i}{W_t}\right)")
        st.markdown(
            "Compara la potencia incidente **Wᵢ** y la transmitida **Wₜ**. "
            "Un **TL = 30 dB** no es un sonido de 30 dB."
        )
    st.info(
        "Decir solamente «40 dB» está incompleto: siempre debe indicarse la magnitud, "
        "por ejemplo 40 dB SPL, TL = 40 dB o R = 40 dB."
    )

    st.markdown("### 2. Del coeficiente τ a la pérdida de transmisión TL")
    st.markdown("""
    El coeficiente de transmisión **τ** es la fracción adimensional de la potencia
    incidente que atraviesa la separación:
    """)
    st.latex(r"\tau=\frac{W_t}{W_i}\qquad 0\leq\tau\leq1")
    st.markdown("La definición de pérdida de transmisión es:")
    st.latex(r"TL=10\log_{10}\left(\frac{W_i}{W_t}\right)")
    st.markdown("Como **Wᵢ/Wₜ = 1/τ**, la sustitución entrega:")
    st.latex(r"TL=10\log_{10}\left(\frac{1}{\tau}\right)")
    st.latex(r"\boxed{TL=-10\log_{10}(\tau)}")
    st.markdown("Y para realizar la conversión inversa:")
    st.latex(r"\boxed{\tau=10^{-TL/10}}")

    st.markdown("### 3. Explorador técnico τ ↔ TL")
    control_mode=st.radio(
        "Variable que deseas controlar",
        ["TL (dB)","τ (coeficiente de transmisión)"],
        horizontal=True,
        key="lab2_tau_tl_mode",
    )
    if control_mode=="TL (dB)":
        tl=float(st.slider(
            "Pérdida de transmisión TL (dB)",0,60,30,1,key="lab2_tau_tl_db"
        ))
        tau=10**(-tl/10)
    else:
        tau_options=[10**(-i/10) for i in range(60,-1,-1)]
        tau=st.select_slider(
            "Coeficiente de transmisión τ",
            options=tau_options,
            value=1e-3,
            format_func=lambda value: (
                f"{value:.6f}".rstrip("0").rstrip(".")
                if value >= 1e-4 else f"{value:.1e}"
            ),
            key="lab2_tau_value",
        )
        tl=-10*math.log10(tau)
        st.caption(
            f"τ siempre es positivo. Equivalencia logarítmica: "
            f"τ = 10^({math.log10(tau):.1f})"
        )

    transmitted_pct=100*tau
    not_transmitted_pct=100*(1-tau)
    m1,m2,m3=st.columns(3)
    m1.metric("TL",f"{tl:.1f} dB")
    m2.metric("τ",f"{tau:.6g}")
    m3.metric("Energía transmitida",f"{transmitted_pct:.6g} %")

    incident_units=1_000_000.0
    transmitted_units=incident_units*tau
    energy_fig=go.Figure()
    energy_fig.add_trace(go.Bar(
        x=["Potencia incidente Wi","Potencia transmitida Wt"],
        y=[incident_units,transmitted_units],
        marker_color=["#0b69d1","#ef8b2c"],
        text=[f"{incident_units:,.0f} unidades",f"{transmitted_units:,.3g} unidades"],
        textposition="outside",
        hovertemplate="%{x}<br>%{y:,.6g} unidades<extra></extra>",
    ))
    energy_fig.update_layout(
        title="Comparación energética en escala logarítmica",
        yaxis_title="Potencia relativa (unidades)",
        yaxis_type="log",
        yaxis_range=[-1,6.45],
        height=360,
        showlegend=False,
        margin=dict(l=35,r=20,t=65,b=40),
    )
    tau_curve=np.logspace(0,-6,241)
    tl_curve=-10*np.log10(tau_curve)
    relation_fig=go.Figure()
    relation_fig.add_trace(go.Scatter(
        x=tau_curve,y=tl_curve,mode="lines",name="TL = −10 log₁₀(τ)",
        line=dict(width=4,color="#0b69d1"),
    ))
    relation_fig.add_trace(go.Scatter(
        x=[tau],y=[tl],mode="markers+text",name="Selección actual",
        marker=dict(size=13,color="#ef8b2c"),
        text=[f"τ={tau:.3g} · TL={tl:.1f} dB"],
        textposition="top center",
    ))
    relation_fig.update_layout(
        title="Relación logarítmica entre τ y TL",
        xaxis_title="Coeficiente de transmisión τ",
        yaxis_title="Pérdida de transmisión TL (dB)",
        xaxis_type="log",
        xaxis_autorange="reversed",
        yaxis_range=[0,64],
        height=360,
        hovermode="closest",
        margin=dict(l=35,r=20,t=65,b=40),
    )
    relation_fig.update_xaxes(
        tickvals=[1,1e-1,1e-2,1e-3,1e-4,1e-5,1e-6],
        ticktext=["1","0,1","0,01","0,001","10⁻⁴","10⁻⁵","10⁻⁶"],
    )
    graph_left,graph_right=st.columns(2,gap="medium")
    with graph_left:
        st.plotly_chart(
            energy_fig,
            use_container_width=True,
            key="lab2_tau_tl_energy_chart",
        )
    with graph_right:
        st.plotly_chart(
            relation_fig,
            use_container_width=True,
            key="lab2_tau_tl_relation_chart",
        )
    st.markdown(
        f'<div class="lesson"><b>Lectura técnica:</b> de 1.000.000 unidades incidentes, '
        f'atraviesan {transmitted_units:,.3g}. Esto corresponde a τ = {tau:.6g}, '
        f'{transmitted_pct:.6g} % transmitido y TL = {tl:.1f} dB. '
        f'La fracción no transmitida es {not_transmitted_pct:.6g} %; este último valor '
        f'no debe confundirse automáticamente con absorción, porque también incluye energía reflejada.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### 4. ¿Por qué aquí se usa TL y después aparecerá R?")
    st.markdown("""
    En esta etapa usamos **TL** (*Transmission Loss*) porque partimos de la relación física
    entre potencia incidente y transmitida y trabajamos con modelos predictivos. En ensayos
    normalizados de elementos constructivos se usa habitualmente el **índice de reducción
    acústica R**, obtenido a partir de los niveles de las cámaras y de las condiciones
    del ensayo. Ambos describen el aislamiento por bandas y pueden coincidir bajo
    condiciones ideales, pero el símbolo debe corresponder al contexto y al método de
    obtención. Más adelante, la curva **R(f)** permitirá calcular **Rw**.
    """)

    st.markdown("### 5. Preguntas de comprensión")
    check(
        "lab2_s1_q1",
        "Un panel tiene τ = 0,01. ¿Qué porcentaje de la energía incidente lo atraviesa?",
        ["10 %","1 %","0,1 %","0,01 %"],
        "1 %",
        "τ es una fracción: 0,01 × 100 = 1 %.",
    )
    check(
        "lab2_s1_q2",
        "Si τ = 0,001, ¿qué TL se obtiene mediante TL = −10 log₁₀(τ)?",
        ["10 dB","20 dB","30 dB","40 dB"],
        "30 dB",
        "log₁₀(0,001) = −3; por tanto, TL = −10(−3) = 30 dB.",
    )
    check(
        "lab2_s1_q3",
        "¿Cuál afirmación describe correctamente el decibel?",
        [
            "Es una unidad absoluta de potencia sonora",
            "Expresa logarítmicamente una relación entre cantidades",
            "Siempre representa nivel de presión sonora",
            "Es equivalente a un watt",
        ],
        "Expresa logarítmicamente una relación entre cantidades",
        "El dB expresa una razón logarítmica; la magnitud concreta depende de la ecuación y de sus referencias.",
    )
    check(
        "lab2_s1_q4",
        "El panel A tiene TL = 20 dB y el B, TL = 30 dB. ¿Qué comparación es correcta?",
        [
            "B transmite diez veces menos energía que A",
            "B transmite solamente 10 % menos energía que A",
            "A y B transmiten la misma energía",
            "B transmite el doble de energía que A",
        ],
        "B transmite diez veces menos energía que A",
        "Un aumento de 10 dB en TL divide por diez la energía transmitida.",
    )
    check(
        "lab2_s1_q5",
        "¿Por qué se usa TL en esta etapa y R en un ensayo normalizado de una partición?",
        [
            "TL se relaciona aquí con un modelo energético; R corresponde al resultado normalizado del elemento ensayado",
            "TL se usa solo en exteriores y R solo en interiores",
            "TL se mide en watt y R en decibeles",
            "No existe diferencia de contexto entre ambos símbolos",
        ],
        "TL se relaciona aquí con un modelo energético; R corresponde al resultado normalizado del elemento ensayado",
        "TL es habitual en la formulación física y predictiva; R es la denominación normalizada del índice de reducción acústica por bandas.",
    )

def lab2_stage2():
    _lab2_heading(2, "Panel simple: incidencia y cuatro zonas físicas",
                  "Relacionar masa, frecuencia, rigidez, resonancia y coincidencia con la forma de la curva.")
    _lab2_image("panel_simple")
    st.caption(
        "Placa simple sometida a una onda sonora: una parte de la energía se refleja, "
        "otra hace vibrar la placa y una fracción se transmite al recinto receptor."
    )
    st.markdown("""
    Un **panel simple** es una hoja o conjunto de capas unidas rígidamente que vibran como
    una sola masa: vidrio monolítico, placa de yeso, tablero de madera, chapa o muro macizo.
    No existe una segunda hoja independiente ni una cámara que actúe como resorte.
    """)
    st.markdown("### 1. ¿Qué define a una placa simple?")
    st.markdown("""
    Se considera **placa simple** al elemento que, frente a la excitación sonora, se
    desplaza y flexiona esencialmente como una sola hoja. Puede estar constituido por
    un único material o por capas adheridas rígidamente; lo importante es que no existan
    dos hojas independientes separadas por una cámara de aire.

    Su primera propiedad acústica es la **masa superficial**: la masa contenida en cada
    metro cuadrado de placa. Para una placa homogénea se obtiene multiplicando la densidad
    del material por su espesor:
    """)
    st.latex(r"m'=\rho h")
    st.markdown("""
    - **m′**: masa superficial, en kg/m².
    - **ρ**: densidad del material, en kg/m³.
    - **h**: espesor, en m.

    La masa superficial —y no la masa total de toda la placa— es la que interviene en la
    ley de masa. Dos placas del mismo material y espesor tienen la misma m′ aunque sus
    superficies totales sean distintas. Al aumentar m′ crece la oposición inercial al
    movimiento, pero la respuesta real también depende de la rigidez de flexión, las
    dimensiones, los apoyos, el amortiguamiento y la frecuencia.
    """)
    _lab2_image("s2_punto1")
    _lab2_plain_language_cards(
        "La masa superficial indica cuánto pesa un metro cuadrado de placa.",
        "Compara placas del mismo tamaño: la más densa o gruesa tendrá mayor m′.",
        "Usar la masa total de la pared. La ley de masa utiliza kg/m², no kg.",
    )
    st.markdown("### 2. Incidencia normal y oblicua")
    st.markdown("""
    El ángulo **θ se mide respecto de la línea normal a la placa**, no respecto de su
    superficie:

    - **Incidencia normal (θ = 0°):** la onda llega perpendicularmente a la placa.
    - **Incidencia oblicua (0° < θ < 90°):** la onda llega inclinada.
    - **Incidencia rasante (θ próxima a 90°):** la propagación es casi paralela a la placa.

    La incidencia normal y la oblicua describen una sola dirección de llegada. En cambio,
    en un recinto reverberante existe energía que alcanza la placa desde muchas direcciones:
    eso se representa mediante un promedio energético angular.
    """)
    _lab2_image("s2_punto2")
    _lab2_plain_language_cards(
        "El sonido puede llegar de frente o inclinado; el ángulo cambia cómo empuja la placa.",
        "El ángulo se mide desde la línea perpendicular a la placa: 0° es incidencia normal.",
        "Medir θ desde la superficie o creer que 78° representa por sí solo todo el campo.",
    )
    st.markdown("### 3. Coeficiente de transmisión sonora según el ángulo")
    st.latex(r"\tau(\theta)=\left[1+\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)^2\right]^{-1}")
    st.latex(r"TL(\theta)=-10\log_{10}\left[\tau(\theta)\right]")
    st.markdown("""
    El coeficiente **τ(θ)** representa la fracción de potencia sonora incidente que
    atraviesa la placa para una dirección específica. Es un valor adimensional entre
    0 y 1: cuanto menor es τ, menor energía se transmite y mayor es la pérdida de
    transmisión **TL**.

    En esta expresión, **ω = 2πf** es la frecuencia angular, **m′** es la masa
    superficial de la placa, **ρ₀** es la densidad del aire, **c** es la velocidad del
    sonido y **θ** es el ángulo medido desde la normal. El término **cos θ** hace que
    la impedancia efectiva que presenta la placa cambie con la dirección de llegada.
    Por eso una misma placa y una misma frecuencia no entregan un único resultado para
    todas las incidencias.

    El cálculo se realiza primero en escala energética mediante τ(θ). Después se
    convierte a decibeles con **TL(θ) = −10 log₁₀[τ(θ)]**. Por ejemplo, τ = 0,01
    significa que atraviesa el 1 % de la potencia incidente y equivale a TL = 20 dB.
    """)
    _lab2_image("s2_tau_angulo")
    _lab2_plain_language_cards(
        "Cada dirección deja pasar una fracción distinta de energía, representada por τ(θ).",
        "Observa cómo varía la energía transmitida al cambiar únicamente el ángulo.",
        "Interpretar τ como decibeles: τ es una proporción energética y TL es su expresión logarítmica.",
    )
    st.markdown("### 4. Incidencia aleatoria y promedio de campo")
    st.latex(
        r"\overline{\tau}="
        r"\frac{\displaystyle\int_{0}^{\theta_{\mathrm{lim}}}"
        r"\tau(\theta)\sin\theta\cos\theta\,d\theta}"
        r"{\displaystyle\int_{0}^{\theta_{\mathrm{lim}}}"
        r"\sin\theta\cos\theta\,d\theta}"
    )
    st.latex(r"TL_{\mathrm{campo}}=-10\log_{10}\left(\overline{\tau}\right)")
    st.markdown("""
    En un campo sonoro reverberante la placa recibe simultáneamente energía desde muchas
    direcciones. El resultado de campo no corresponde al TL de un ángulo particular:
    se obtiene integrando los coeficientes **τ(θ)** de todas las direcciones consideradas.

    La ponderación **sin θ cos θ** tiene un significado físico. **sin θ** representa la
    cantidad de direcciones disponibles dentro de cada anillo angular, mientras que
    **cos θ** representa la componente de intensidad sonora normal a la superficie.
    El denominador normaliza esa ponderación para que el resultado sea un promedio
    energético y no una suma dependiente del intervalo elegido.

    En este laboratorio se adopta **θ_lim = 78°** como aproximación práctica de campo.
    Se integran todas las incidencias entre 0° y 78°; no se calcula únicamente la
    transmisión a 78°. Una vez obtenido el coeficiente medio **τ̄**, recién entonces
    se transforma a decibeles para obtener **TL_campo**.
    """)
    _lab2_image("s2_punto4")
    _lab2_plain_language_cards(
        "Un recinto real envía sonido hacia la placa desde muchas direcciones a la vez.",
        "El resultado de campo integra desde 0° hasta 78° con ponderación energética.",
        "Promediar directamente los TL o tomar el valor a 78° como si fuera el promedio de campo.",
    )
    st.markdown("""
    - **Incidencia aleatoria o campo difuso ideal:** supone direcciones distribuidas
      estadísticamente hasta 90°.
    - **Incidencia de campo:** aproximación práctica del promedio angular; frecuentemente
      se limita la integración cerca de 78° para representar mejor resultados experimentales.

    No se promedian directamente valores de TL en decibeles. Primero se promedian los
    coeficientes de transmisión τ y después se transforma el resultado a decibeles.
    """)
    st.markdown("### 5. Rigidez de flexión: la placa también se deforma")
    st.markdown("""
    Una placa simple no se desplaza únicamente como una masa rígida: también se curva.
    La resistencia que opone a esa deformación se denomina **rigidez de flexión**:
    """)
    st.latex(r"D=\frac{Eh^3}{12(1-\nu^2)}")
    st.markdown("""
    - **D**: rigidez de flexión por unidad de ancho, en N·m.
    - **E**: módulo de Young, en Pa.
    - **h**: espesor, en m.
    - **ν**: coeficiente de Poisson, adimensional.

    La relación D ∝ h³ muestra que el espesor afecta mucho más a la rigidez que a la masa
    superficial: si se duplica h, m′ se duplica, pero D aumenta idealmente ocho veces.
    Esta rigidez determina los modos propios y, junto con m′, la propagación de las ondas
    de flexión y la frecuencia crítica.
    """)
    st.markdown("#### Ecuación de movimiento de una placa simple sometida a presión sonora")
    st.markdown("""
    Para describir cómo responde la placa cuando el sonido la excita, se plantea su
    equilibrio dinámico: la presión sonora aplicada debe vencer simultáneamente la
    resistencia de la placa a curvarse y la inercia asociada a su masa superficial.
    """)
    st.latex(r"D\nabla^4\xi+m'\frac{\partial^2\xi}{\partial t^2}=\Delta p")
    st.markdown("""
    En esta ecuación de movimiento, **D∇⁴ξ** representa la resistencia a la flexión,
    **m′∂²ξ/∂t²** la inercia de la masa superficial y **Δp** la diferencia de presión
    sonora entre ambas caras que hace vibrar la placa. En la región donde domina la
    inercia puede simplificarse este equilibrio y obtenerse la ley de masa.
    """)
    _lab2_image("s2_punto3")
    _lab2_plain_language_cards(
        "La placa no solo se desplaza: también se curva. D mide cuánto cuesta doblarla.",
        "El espesor aparece elevado al cubo; pequeños cambios de h modifican mucho la rigidez.",
        "Suponer que una placa más pesada siempre tiene proporcionalmente mayor rigidez.",
    )
    st.markdown("### 6. De la impedancia de masa a la ley de masa aproximada")
    st.markdown("""
    En la región donde domina la **inercia**, una hoja ideal puede representarse mediante
    su impedancia mecánica por unidad de superficie. Para una excitación armónica:
    """)
    st.latex(r"z_m=j\omega m'")
    st.markdown("Al sustituirla en la expresión de transmisión de una hoja entre dos medios de aire:")
    st.latex(r"\tau(\theta)=\left[1+\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)^2\right]^{-1}")
    st.markdown("y aplicar la definición desarrollada en la Etapa 1:")
    st.latex(r"TL(\theta)=-10\log_{10}\left[\tau(\theta)\right]")
    st.markdown("""
    Para incidencia normal, **θ = 0°** y, por tanto, **cos θ = 1**. Si el término de masa
    es mucho mayor que 1, se desprecia el 1 de la expresión. Luego se sustituye la
    frecuencia angular por su relación con la frecuencia ordinaria:
    """)
    st.latex(r"\omega=2\pi f")
    st.latex(r"TL_n\approx20\log_{10}(m'f)+20\log_{10}\left(\frac{\pi}{\rho_0c}\right)")
    st.latex(r"TL_n\approx20\log_{10}(m'f)-42\quad\text{dB}")
    st.info("La expresión anterior corresponde a incidencia normal y conduce, para aire "
            "en condiciones habituales, a una constante cercana a −42 dB.")
    st.latex(r"TL_{\mathrm{campo}}\approx20\log_{10}(m'f)-47\quad\mathrm{dB}")
    st.markdown("""
    La forma con **−47 dB** incorpora una corrección aproximada de incidencia de campo.
    No es una constante universal ni una ley física diferente: depende del modelo angular
    adoptado y solo describe la tendencia de la zona controlada por masa, lejos de las
    resonancias, la coincidencia, las fugas y las transmisiones laterales.
    """)
    _lab2_image("s2_ley_masa",
                "Zona controlada por masa: una placa más pesada opone mayor inercia.")
    _lab2_plain_language_cards(
        "Una placa pesada se parece a un carro difícil de empujar: se mueve menos ante el sonido.",
        "En la zona de masa, duplicar m′ o la frecuencia aumenta el TL aproximadamente 6 dB.",
        "Extender la recta de ley de masa a resonancias y coincidencia, donde deja de ser válida.",
    )

    st.markdown("### 7. Frecuencia crítica y coincidencia")
    st.latex(r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{D}}")
    st.markdown("""
    La **frecuencia crítica** es la zona en que la onda sonora puede acoplarse con
    una onda de flexión de la placa. Ese acoplamiento facilita la transmisión y
    puede producir un valle en la curva de aislamiento.

    **En sencillo:** existe una zona donde la placa vibra de una forma especialmente
    favorable para que el sonido pase. Se calcula usando la masa superficial y la
    rigidez explicadas antes; no es un parámetro independiente.
    """)
    st.latex(r"m'=\rho h")
    st.latex(r"D=\frac{Eh^3}{12(1-\nu^2)}")
    st.latex(r"f_c\propto\frac{1}{h}\sqrt{\frac{\rho}{E}}")
    st.caption(
        "η no determina por sí solo fᶜ; influye principalmente en la profundidad "
        "y anchura del valle de coincidencia."
    )
    _lab2_image("s2_frecuencia_critica",
                "Coincidencia entre la onda sonora y la onda de flexión de una placa.")
    _lab2_plain_language_cards(
        "Es una zona donde la onda aérea logra hacer vibrar la placa con especial eficiencia.",
        "La curva real forma un valle respecto de la tendencia ideal de ley de masa.",
        "Confundir la frecuencia crítica con una resonancia propia global de la placa.",
    )

    st.markdown("### 8. Laboratorio interactivo: incidencia y aislamiento")
    st.markdown("""
    Una misma placa puede evaluarse bajo tres condiciones de incidencia. La diferencia
    no está en el material, sino en **cómo llega la energía sonora** y en la forma de
    combinarla:

    - **Incidencia normal:** ondas paralelas que llegan perpendicularmente a la placa.
    - **Campo de laboratorio 0°–78°:** promedio energético de múltiples incidencias
      comprendidas entre 0° y 78°.
    - **Campo difuso ideal 0°–90°:** modelo ideal con energía procedente de todo el
      hemisferio incidente.

    Selecciona una condición para resaltarla y cambia la frecuencia. La aplicación
    recalcula simultáneamente los tres resultados, de modo que puedas comparar el efecto
    del modelo de incidencia sin confundir el promedio de campo con un rayo aislado.
    """)

    lab_mode_options = [
        "Incidencia normal · 0°",
        "Campo de laboratorio · 0° a 78°",
        "Campo difuso ideal · 0° a 90°",
    ]
    control_a, control_b = st.columns([1.55, 1])
    field_mode = control_a.radio(
        "Condición que deseas observar",
        lab_mode_options,
        index=1,
        horizontal=True,
        key="lab2_field_mode",
    )
    angular_frequency = control_b.select_slider(
        "Frecuencia de cálculo (Hz)",
        options=LAB2_FREQS.tolist(),
        value=500,
        key="lab2_field_frequency",
    )

    angular_mass = 10.0

    def _field_average_tau(limit_degrees):
        field_angles = np.linspace(0.0, float(limit_degrees), 900)
        field_angles_rad = np.deg2rad(field_angles)
        field_tau = np.array([
            _mass_sheet_tau(angular_mass, angular_frequency, float(theta))
            for theta in field_angles
        ])
        field_weights = np.sin(field_angles_rad) * np.cos(field_angles_rad)
        if hasattr(np, "trapezoid"):
            numerator = np.trapezoid(field_tau * field_weights, field_angles_rad)
            denominator = np.trapezoid(field_weights, field_angles_rad)
        else:
            numerator = np.trapz(field_tau * field_weights, field_angles_rad)
            denominator = np.trapz(field_weights, field_angles_rad)
        return max(float(numerator / max(denominator, 1e-15)), 1e-15)

    tau_normal = _mass_sheet_tau(angular_mass, angular_frequency, 0)
    tau_field_78 = _field_average_tau(78.0)
    tau_field_90 = _field_average_tau(89.9)
    tl_normal = -10 * math.log10(tau_normal)
    tl_field_78 = -10 * math.log10(tau_field_78)
    tl_field_90 = -10 * math.log10(tau_field_90)

    field_results = {
        "Incidencia normal · 0°": (tau_normal, tl_normal),
        "Campo de laboratorio · 0° a 78°": (tau_field_78, tl_field_78),
        "Campo difuso ideal · 0° a 90°": (tau_field_90, tl_field_90),
    }
    selected_tau, selected_tl = field_results[field_mode]

    # Esquema pedagógico: tres campos visibles y la selección destacada.
    field_colors = {
        "Incidencia normal · 0°": "#1565c0",
        "Campo de laboratorio · 0° a 78°": "#ef6c00",
        "Campo difuso ideal · 0° a 90°": "#7b1fa2",
    }
    field_titles = [
        "Incidencia normal",
        "Campo de laboratorio 0°–78°",
        "Campo difuso ideal 0°–90°",
    ]
    field_keys = lab_mode_options
    fig_fields = go.Figure()
    for panel_index, (panel_title, panel_key) in enumerate(zip(field_titles, field_keys)):
        x0 = panel_index * 4.0
        active = panel_key == field_mode
        color = field_colors[panel_key]
        fig_fields.add_shape(
            type="rect",
            x0=x0 + 0.05,
            x1=x0 + 3.75,
            y0=0.15,
            y1=4.65,
            fillcolor=color if active else "#f8fafc",
            opacity=0.11 if active else 1.0,
            line=dict(color=color if active else "#cbd5e1", width=4 if active else 1.5),
            layer="below",
        )
        panel_x = x0 + 2.55
        fig_fields.add_shape(
            type="rect",
            x0=panel_x,
            x1=panel_x + 0.12,
            y0=0.8,
            y1=3.85,
            fillcolor="#475569",
            line=dict(color="#334155", width=1),
        )
        fig_fields.add_annotation(
            x=x0 + 1.9,
            y=4.3,
            text=f"<b>{panel_title}</b>",
            showarrow=False,
            font=dict(size=14, color="#0f172a"),
        )

        if panel_index == 0:
            ray_origins = [(x0 + 0.45, 1.45), (x0 + 0.45, 2.3), (x0 + 0.45, 3.15)]
        elif panel_index == 1:
            ray_origins = [
                (x0 + 0.45, 0.65), (x0 + 0.45, 1.25), (x0 + 0.45, 2.3),
                (x0 + 0.45, 3.35), (x0 + 0.45, 3.95),
            ]
        else:
            ray_origins = [
                (x0 + 0.35, 0.35), (x0 + 0.35, 0.9), (x0 + 0.35, 1.55),
                (x0 + 0.35, 2.3), (x0 + 0.35, 3.05), (x0 + 0.35, 3.7),
                (x0 + 0.35, 4.25),
            ]
        for origin_x, origin_y in ray_origins:
            fig_fields.add_annotation(
                x=panel_x,
                y=2.3,
                ax=origin_x,
                ay=origin_y,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                text="",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.1,
                arrowwidth=2.8 if active else 1.8,
                arrowcolor=color if active else "#94a3b8",
            )
        fig_fields.add_annotation(
            x=x0 + 1.9,
            y=0.42,
            text="<b>SELECCIONADO</b>" if active else "Seleccionar arriba",
            showarrow=False,
            font=dict(size=11, color=color if active else "#64748b"),
        )

    fig_fields.update_xaxes(range=[0, 11.8], visible=False, fixedrange=True)
    fig_fields.update_yaxes(range=[0, 4.9], visible=False, fixedrange=True)
    fig_fields.update_layout(
        title="Cómo llega la energía sonora a la placa",
        height=430,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(
        fig_fields,
        use_container_width=True,
        key="lab2_three_incidence_fields",
        config={"displayModeBar": False},
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("TL normal", f"{tl_normal:.1f} dB", "Incidencia 0°")
    m2.metric("TL de campo", f"{tl_field_78:.1f} dB", "Promedio 0°–78°")
    m3.metric("TL difuso ideal", f"{tl_field_90:.1f} dB", "Promedio 0°–90°")

    comparison_names = ["Normal 0°", "Campo 0°–78°", "Difuso ideal 0°–90°"]
    comparison_values = [tl_normal, tl_field_78, tl_field_90]
    comparison_colors = [
        field_colors["Incidencia normal · 0°"],
        field_colors["Campo de laboratorio · 0° a 78°"],
        field_colors["Campo difuso ideal · 0° a 90°"],
    ]
    fig_comparison = go.Figure(go.Bar(
        x=comparison_names,
        y=comparison_values,
        marker_color=comparison_colors,
        text=[f"{value:.1f} dB" for value in comparison_values],
        textposition="outside",
        hovertemplate="%{x}<br>TL = %{y:.1f} dB<extra></extra>",
    ))
    fig_comparison.update_layout(
        title=f"Comparación del aislamiento a {angular_frequency} Hz",
        xaxis_title="Condición de incidencia",
        yaxis_title="Pérdida de transmisión, TL (dB)",
        height=360,
        margin=dict(l=35, r=15, t=60, b=45),
        showlegend=False,
    )
    fig_comparison.update_yaxes(
        range=[0, max(comparison_values) * 1.22],
        gridcolor="#e2e8f0",
    )
    st.plotly_chart(
        fig_comparison,
        use_container_width=True,
        key="lab2_field_tl_comparison",
        config={"displayModeBar": False},
    )

    transmitted_percent = 100.0 * selected_tau
    if field_mode == "Incidencia normal · 0°":
        field_explanation = (
            "Las ondas llegan perpendicularmente y todas comparten la misma dirección. "
            "El resultado corresponde a una incidencia única, no a un promedio angular."
        )
    elif field_mode == "Campo de laboratorio · 0° a 78°":
        field_explanation = (
            "El resultado combina energéticamente todas las incidencias entre 0° y 78°. "
            "No corresponde al TL de una onda que llega a 78°."
        )
    else:
        field_explanation = (
            "El modelo ideal incorpora incidencias de prácticamente todo el hemisferio. "
            "Los ángulos rasantes se incluyen con su ponderación energética, no con igual peso."
        )
    st.markdown(
        f'<div class="lesson"><b>Interpretación automática:</b> a '
        f'<b>{angular_frequency} Hz</b>, la condición <b>{field_mode}</b> entrega '
        f'<b>TL = {selected_tl:.1f} dB</b> y transmite aproximadamente '
        f'<b>{transmitted_percent:.3g} %</b> de la energía incidente en este modelo '
        f'ideal de masa. {field_explanation}</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Ver detalle matemático"):
        st.markdown(
            "Para cada dirección se calcula primero el coeficiente de transmisión "
            "de la hoja simple:"
        )
        st.latex(
            r"\tau(\theta)=\left[1+\left("
            r"\frac{\omega m'\cos\theta}{2\rho_0c}"
            r"\right)^2\right]^{-1}"
        )
        st.markdown(
            "Para los campos angulares, los coeficientes se integran con ponderación "
            "energética y solo después se convierten a decibeles:"
        )
        st.latex(
            r"\overline{\tau}="
            r"\frac{\displaystyle\int_{0}^{\theta_{\max}}\tau(\theta)"
            r"\sin\theta\cos\theta\,d\theta}"
            r"{\displaystyle\int_{0}^{\theta_{\max}}"
            r"\sin\theta\cos\theta\,d\theta}"
        )
        st.latex(r"TL=-10\log_{10}\left(\overline{\tau}\right)")
        st.markdown("""
        - **τ(θ):** coeficiente de transmisión para el ángulo θ.
        - **θ:** ángulo de incidencia medido desde la normal.
        - **ω = 2πf:** frecuencia angular.
        - **m′:** masa superficial de la placa.
        - **ρ₀:** densidad del aire.
        - **c:** velocidad del sonido en el aire.
        - **θmáx:** 78° para el campo de laboratorio y aproximadamente 90° para el
          campo difuso ideal.
        - **τ̄:** coeficiente de transmisión promedio.
        - **TL:** pérdida de transmisión, en dB.

        Los valores de TL no se promedian directamente. Primero se promedia la energía
        mediante τ y luego se transforma el resultado a decibeles.
        """)
    st.markdown("### 9. Explorador de las cuatro zonas")
    material=st.selectbox("Material",["Yeso-cartón","Vidrio","Madera contrachapada","Hormigón"],key="lab2_panel_material")
    props={
        # densidad, espesor, E [GPa], nu, eta aproximada
        "Yeso-cartón":(800,12.5,2.5,.30,.030),
        "Vidrio":(2500,6.0,70.0,.23,.010),
        "Madera contrachapada":(600,18.0,8.0,.30,.025),
        "Hormigón":(2400,100.0,30.0,.20,.020),
    }
    rho,default_h,young,poisson,eta=props[material]
    h=st.slider("Espesor (mm)",4.0,200.0,float(default_h),0.5,key="lab2_panel_h")
    selected_zone=st.radio("Zona que deseas analizar",
        ["1 · Rigidez","2 · Resonancias","3 · Ley de masa","4 · Coincidencia"],
        horizontal=True,key="lab2_selected_zone")
    mass,stiffness,calculated_fc=_critical_frequency(rho,h,young,poisson)
    default_loss=max(5,min(16,5-10*math.log10(eta)))
    curve=_simple_real_curve(mass,calculated_fc,default_loss)
    zone_explanations={
        "1 · Rigidez":(
            "A muy baja frecuencia dominan la rigidez, el tamaño, los apoyos y las "
            "fijaciones. Al variar el material o el espesor cambia la rigidez a "
            "flexión D; por eso esta zona no puede predecirse solo con la masa "
            "superficial m′."
        ),
        "2 · Resonancias":(
            "Los modos propios dependen de la relación D/m′, de las dimensiones y "
            "de los bordes. Una placa más rígida desplaza sus modos; una placa mayor "
            "o más pesada tiende a llevarlos hacia frecuencias menores."
        ),
        "3 · Ley de masa":(
            "Entre las resonancias y la coincidencia domina la inercia. En esta "
            "región resulta útil la ley de masa: al duplicar m′ o la frecuencia, "
            "el aislamiento aumenta aproximadamente 6 dB."
        ),
        "4 · Coincidencia":(
            f"Para la selección actual, la frecuencia crítica es aproximadamente "
            f"{calculated_fc:.0f} Hz. En torno a ella, la onda aérea se acopla con "
            "una onda de flexión de la placa y aumenta la energía transmitida."
        ),
    }
    st.markdown("#### Cómo interpretar la zona seleccionada")
    st.markdown(
        f"**{selected_zone}.** {zone_explanations[selected_zone]} "
        "En el gráfico, el fondo coloreado identifica el intervalo donde domina "
        "este mecanismo."
    )
    if selected_zone=="1 · Rigidez":
        st.latex(r"D=\frac{Eh^3}{12(1-\nu^2)}")
    elif selected_zone=="3 · Ley de masa":
        st.latex(r"TL\approx20\log_{10}(m'f)-47")
    elif selected_zone=="4 · Coincidencia":
        st.latex(r"f_c\propto\frac{1}{h}\sqrt{\frac{\rho}{E}}")
    # Rangos didácticos para mostrar dónde domina cada mecanismo. La zona de
    # coincidencia sigue a fᶜ, por lo que cambia al modificar material o espesor.
    zone_highlights={
        "1 · Rigidez":(50,125,"Zona de rigidez","#9ec5fe"),
        "2 · Resonancias":(63,250,"Zona de resonancias","#ffd8a8"),
        "3 · Ley de masa":(
            250,max(315,.80*calculated_fc),"Zona de ley de masa","#b7e4c7"
        ),
        "4 · Coincidencia":(
            .80*calculated_fc,1.25*calculated_fc,
            "Zona de coincidencia","#f3b4c2"
        ),
    }
    _plot_curves([
        ("Respuesta aproximada",curve,"solid"),
        ("Ley de masa ideal",_mass_law_curve(mass),"dash"),
    ],f"{material} · m′ = {mass:.1f} kg/m²",
       [(calculated_fc,"fᶜ")],zone_highlights[selected_zone])
    z1,z2,z3=st.columns(3)
    z1.metric("Masa superficial m′",f"{mass:.1f} kg/m²")
    z2.metric("Rigidez D",f"{stiffness:.1f} N·m")
    z3.metric("Frecuencia crítica fᶜ",f"{calculated_fc:.0f} Hz")
    st.caption("Modelo didáctico: muestra mecanismos y tendencias; no sustituye una curva de ensayo del producto.")
    st.markdown("### 10. Preguntas de comprensión")
    check("lab2_s2_q1",
        "¿De dónde proviene el término aproximado −47 dB de la ley de masa?",
        [
            "De una corrección de incidencia de campo/difusa aplicada a la tendencia controlada por masa",
            "De la frecuencia crítica de cualquier material",
            "De convertir watt directamente en presión sonora",
            "Es una constante universal exacta para todas las placas",
        ],
        "De una corrección de incidencia de campo/difusa aplicada a la tendencia controlada por masa",
        "La aproximación normal conduce a una constante cercana a −42 dB; −47 dB representa una aproximación de campo y no reproduce resonancia ni coincidencia.")
    check("lab2_s2_q2",
        "En el laboratorio angular, ¿qué significa θ = 0°?",
        ["Incidencia normal","Incidencia rasante","Campo difuso","Ausencia de transmisión"],
        "Incidencia normal",
        "El ángulo se mide respecto de la normal a la placa; por ello 0° corresponde a llegada perpendicular.")
    check("lab2_s2_q3",
        "¿Cómo se obtiene correctamente el TL de un campo con múltiples ángulos?",
        [
            "Se promedian energéticamente los τ(θ) y luego se convierten a TL",
            "Se promedian directamente los TL en dB",
            "Se toma solamente el TL a 78°",
            "Se usa siempre el TL a 0°",
        ],
        "Se promedian energéticamente los τ(θ) y luego se convierten a TL",
        "Los decibeles no se promedian aritméticamente para esta operación; primero se combinan coeficientes de transmisión.")
    check("lab2_s2_q4",
        "¿En qué zona es válida la tendencia TL ≈ 20 log₁₀(m′f) − 47?",
        [
            "En la zona controlada por masa, lejos de resonancias y coincidencia",
            "En todas las frecuencias sin excepción",
            "Únicamente en la zona de rigidez",
            "Solo exactamente en la frecuencia crítica",
        ],
        "En la zona controlada por masa, lejos de resonancias y coincidencia",
        "La ley de masa aproximada describe una región, no la curva completa de una placa real.")
    check("lab2_s2_q5",
        "Para una misma placa homogénea, ¿qué tendencia presenta fᶜ al aumentar el espesor?",
        [
            "Disminuye aproximadamente en proporción inversa al espesor",
            "Aumenta en proporción al cubo del espesor",
            "Permanece siempre constante",
            "Se vuelve igual a la primera resonancia modal",
        ],
        "Disminuye aproximadamente en proporción inversa al espesor",
        "Como m′ crece con h y D con h³, fᶜ es aproximadamente proporcional a 1/h para un mismo material.")

def _panel_simple_tau(frequency, angles_rad, surface_mass, stiffness,
                      loss_factor, rho_air=1.18, sound_speed=343.0):
    """Coeficiente de transmisión angular para una placa simple homogénea."""
    omega = 2*np.pi*np.asarray(frequency, dtype=float)
    theta = np.asarray(angles_rad, dtype=float)
    omega_grid = omega[..., np.newaxis]
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    mass_term = (
        omega_grid*surface_mass*cos_theta/(2*rho_air*sound_speed)
    )
    flexural_term = (
        omega_grid**2*stiffness*sin_theta**4/
        (sound_speed**4*surface_mass)
    )
    real_part = 1 + loss_factor*mass_term*flexural_term
    imaginary_part = mass_term*(1-flexural_term)
    return 1/np.maximum(real_part**2+imaginary_part**2, 1e-15)


def _panel_simple_field_tl(frequencies, surface_mass, stiffness,
                           loss_factor):
    """Cálculo de campo para una placa simple entre 0 y 78 grados."""
    angles = np.linspace(0.0, np.deg2rad(78.0), 720)
    tau_angular = _panel_simple_tau(
        frequencies, angles, surface_mass, stiffness, loss_factor
    )
    weights = np.sin(angles)*np.cos(angles)
    integrand = tau_angular*weights
    if hasattr(np, "trapezoid"):
        integral = np.trapezoid(integrand, angles, axis=-1)
    else:
        integral = np.trapz(integrand, angles, axis=-1)
    normalizer = 2.0904
    tau_field = np.maximum(normalizer*integral, 1e-12)
    tl_field = -10*np.log10(tau_field)
    return tau_field, tl_field, angles, tau_angular, normalizer


def lab2_stage3():
    _lab2_heading(
        3,
        "Ejercicio aplicado: TL de una placa simple de yeso-cartón",
        "Construir la predicción continua desde las propiedades del material hasta el TL de campo.",
    )
    st.markdown("""
    ### Situación profesional
    Se proyecta una **placa homogénea simple de yeso-cartón** para separar un recinto
    emisor de uno receptor. Antes de utilizar índices globales o datos por bandas, se
    desea predecir cómo cambia su pérdida por transmisión entre **50 y 5.000 Hz**.

    En este primer ejercicio no se aplicará la ley de masa aproximada ni una corrección
    dibujada para la coincidencia. La curva se obtendrá directamente con la ecuación
    angular de placa simple y su integración de campo.
    """)
    _lab2_image(
        "yeso_carton",
        "Placa simple: una hoja homogénea, sin cámara ni segunda placa independiente.",
    )

    st.markdown("### Ruta del ejercicio")
    st.markdown("""
    1. Ingresar las propiedades del yeso-cartón.
    2. Calcular masa superficial, rigidez de flexión y frecuencia crítica.
    3. Calcular el coeficiente de transmisión de cada ángulo.
    4. Integrar energéticamente todas las incidencias entre 0° y 78°.
    5. Transformar el coeficiente de campo en TL y analizar la curva continua.
    """)
    st.info(
        "**Idea clave:** 78° no es un único rayo. Es el límite superior del campo "
        "angular utilizado para integrar todas las incidencias desde 0° hasta 78°."
    )

    st.markdown("### Paso 1 · Propiedades de la placa")
    st.caption(
        "Los valores iniciales son referencias didácticas para una placa de yeso-cartón. "
        "Puedes modificarlos para observar qué propiedad cambia la predicción."
    )
    p1,p2,p3=st.columns(3)
    rho=p1.number_input(
        "Densidad ρ (kg/m³)", min_value=300.0, max_value=3000.0,
        value=800.0, step=10.0, key="lab2_s3_rho",
        help="Masa contenida en un metro cúbico del material.")
    h_mm=p2.number_input(
        "Espesor h (mm)", min_value=4.0, max_value=50.0,
        value=12.5, step=0.5, key="lab2_s3_h",
        help="El cálculo convierte automáticamente milímetros a metros.")
    young_gpa=p3.number_input(
        "Módulo de Young E (GPa)", min_value=0.1, max_value=100.0,
        value=2.5, step=0.1, key="lab2_s3_e",
        help="Representa la resistencia elástica del material a deformarse.")
    p4,p5,p6=st.columns(3)
    poisson=p4.number_input(
        "Coeficiente de Poisson ν", min_value=0.05, max_value=0.49,
        value=0.30, step=0.01, format="%.2f", key="lab2_s3_nu",
        help="Relaciona la deformación transversal con la longitudinal.")
    eta=p5.number_input(
        "Factor de pérdidas η", min_value=0.001, max_value=0.200,
        value=0.030, step=0.001, format="%.3f", key="lab2_s3_eta",
        help="Representa el amortiguamiento interno de la placa.")
    selected_frequency=p6.number_input(
        "Frecuencia a inspeccionar (Hz)", min_value=50, max_value=5000,
        value=1000, step=50, key="lab2_s3_selected_frequency")

    st.markdown(
        '<div class="lesson"><b>Traducción para no ingenieros:</b> ρ y h determinan '
        "cuánta masa existe en cada metro cuadrado; E, h y ν determinan cuánto se "
        "resiste la placa a curvarse; η indica cuánta vibración interna logra disipar.</div>",
        unsafe_allow_html=True,
    )

    h=h_mm/1000
    surface_mass=rho*h
    stiffness=young_gpa*1e9*h**3/(12*(1-poisson**2))
    critical_frequency=343.0**2/(2*math.pi)*math.sqrt(surface_mass/stiffness)

    st.markdown("### Paso 2 · Magnitudes calculadas")
    st.latex(r"m'=\rho h")
    st.latex(r"B=\frac{Eh^3}{12(1-\nu^2)}")
    st.latex(r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{B}}")
    r1,r2,r3=st.columns(3)
    r1.metric("Masa superficial m′",f"{surface_mass:.2f} kg/m²")
    r2.metric("Rigidez de flexión B",f"{stiffness:.2f} N·m")
    r3.metric("Frecuencia crítica fᶜ",f"{critical_frequency:.0f} Hz")
    if 50 <= critical_frequency <= 5000:
        st.warning(
            f"La frecuencia crítica calculada ({critical_frequency:.0f} Hz) está dentro "
            "del intervalo analizado. Revisa la curva cerca de ese valor: allí puede "
            "aumentar la transmisión por coincidencia."
        )
    else:
        st.success(
            f"La frecuencia crítica calculada ({critical_frequency:.0f} Hz) queda fuera "
            "del intervalo de 50 a 5.000 Hz."
        )

    st.markdown("### Paso 3 · De un ángulo al coeficiente de transmisión")
    st.markdown(r"""
    Para una misma frecuencia, el sonido puede alcanzar la placa desde muchas direcciones.
    La tesis calcula primero un coeficiente \(\tau(\theta,f)\) para cada dirección.
    \(\tau=1\) significa transmisión total y un valor próximo a cero significa que pasa
    una fracción muy pequeña de la energía incidente.
    """)
    st.latex(
        r"\tau(\theta,f)=\left\{\left[1+\eta"
        r"\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)"
        r"\left(\frac{\omega^2B\sin^4\theta}{c^4m'}\right)\right]^2+"
        r"\left[\left(\frac{\omega m'\cos\theta}{2\rho_0c}\right)"
        r"\left(1-\frac{\omega^2B\sin^4\theta}{c^4m'}\right)\right]^2"
        r"\right\}^{-1}"
    )
    st.caption(
        "ω = 2πf; θ se mide respecto de la normal; ρ₀ = 1,21 kg/m³; c = 343 m/s."
    )

    selected_f=float(selected_frequency)
    tau_field_one,tl_field_one,angles,tau_angular,normalizer=(
        _panel_simple_field_tl(
            np.array([selected_f]),surface_mass,stiffness,eta
        )
    )
    tau_selected=tau_angular[0]
    angles_deg=np.degrees(angles)
    angular_fig=go.Figure()
    angular_fig.add_trace(go.Scatter(
        x=angles_deg,y=100*tau_selected,mode="lines",
        line=dict(color="#08a6c9",width=4),
        name=f"{selected_frequency} Hz"))
    angular_fig.add_vline(x=78,line_dash="dash",line_color="#ef8b2c")
    angular_fig.update_layout(
        title=f"Transmisión angular a {selected_frequency} Hz",
        xaxis_title="Ángulo respecto de la normal (°)",
        yaxis_title="Energía transmitida (%)",
        xaxis=dict(range=[0,90]),
        height=390,margin=dict(l=35,r=20,t=60,b=40),
        hovermode="x unified")
    st.plotly_chart(
        angular_fig,use_container_width=True,key="lab2_s3_angular_curve")
    st.markdown(
        '<div class="lesson"><b>Cómo leer este gráfico:</b> cada punto corresponde a '
        "una dirección de llegada distinta, no a una frecuencia distinta. La línea se "
        "detiene en 78° porque esa es la última incidencia incorporada al campo de "
        "laboratorio.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Paso 4 · Construcción del campo hasta 78°")
    st.latex(
        r"\overline{\tau}_{campo}(f)=2{,}0904"
        r"\int_0^{78^\circ}\tau(\theta,f)\cos\theta\sin\theta\,d\theta"
    )
    st.latex(
        r"TL_{campo}(f)=-10\log_{10}\left[\overline{\tau}_{campo}(f)\right]"
    )
    st.markdown(r"""
    El factor \(2{,}0904\) normaliza la ponderación angular limitada a 78°. Primero se
    suman las fracciones de energía transmitida, considerando el peso correspondiente a
    cada dirección. **Solo después** ese promedio se convierte a decibeles. Promediar
    directamente los valores de TL sería incorrecto.
    """)
    f1,f2,f3=st.columns(3)
    f1.metric(
        f"τ̄ de campo a {selected_frequency} Hz",
        f"{float(tau_field_one[0]):.6f}")
    f2.metric(
        "Energía transmitida",
        f"{100*float(tau_field_one[0]):.4f} %")
    f3.metric(
        "TL de campo",
        f"{float(tl_field_one[0]):.1f} dB")

    st.markdown("### Paso 5 · Curva continua de TL en frecuencia lineal")
    frequencies=np.arange(50.0,5000.0+1,10.0)
    tau_field,tl_field,_,_,_= _panel_simple_field_tl(
        frequencies,surface_mass,stiffness,eta)
    selected_index=int(np.argmin(np.abs(frequencies-selected_f)))
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl_field,mode="lines",
        name="TL de campo · 0° a 78°",
        line=dict(color="#0967d2",width=4)))
    if 50 <= critical_frequency <= 5000:
        fig.add_vline(
            x=critical_frequency,line_dash="dash",line_color="#ef8b2c",
            annotation_text="fᶜ",annotation_position="top")
    fig.add_trace(go.Scatter(
        x=[frequencies[selected_index]],y=[tl_field[selected_index]],
        mode="markers",name=f"{int(frequencies[selected_index])} Hz",
        marker=dict(size=12,color="#ef8b2c")))
    fig.update_layout(
        title="Pérdida por transmisión de campo · placa simple de yeso-cartón",
        xaxis_title="Frecuencia (Hz) · escala lineal",
        yaxis_title="TL de campo (dB)",
        xaxis=dict(type="linear",range=[50,5000],dtick=500),
        height=470,hovermode="x unified",
        margin=dict(l=40,r=20,t=65,b=45),
        legend=dict(orientation="h",y=1.12))
    st.plotly_chart(fig,use_container_width=True,key="lab2_s3_tl_linear")
    st.caption(
        "Curva predictiva continua del modelo teórico. No corresponde a un ensayo "
        "normalizado ni incorpora dimensiones finitas, apoyos, juntas, fugas o flancos."
    )

    st.markdown("### Paso 6 · Lectura de resultados")
    sample_frequencies=np.array([125.,250.,500.,1000.,2000.,4000.])
    sample_tau,sample_tl,_,_,_=_panel_simple_field_tl(
        sample_frequencies,surface_mass,stiffness,eta)
    results=pd.DataFrame({
        "Frecuencia (Hz)":sample_frequencies.astype(int),
        "τ̄ campo":sample_tau,
        "Energía transmitida (%)":100*sample_tau,
        "TL campo (dB)":sample_tl,
    })
    st.dataframe(
        results.style.format({
            "τ̄ campo":"{:.6f}",
            "Energía transmitida (%)":"{:.4f}",
            "TL campo (dB)":"{:.1f}",
        }),
        use_container_width=True,hide_index=True)
    min_index=int(np.argmin(tl_field))
    max_transmission_index=int(np.argmax(tau_field))
    a,b,c=st.columns(3)
    a.metric(
        "Menor TL calculado",
        f"{tl_field[min_index]:.1f} dB",
        f"a {frequencies[min_index]:.0f} Hz")
    b.metric(
        "Mayor transmisión",
        f"{100*tau_field[max_transmission_index]:.3f} %",
        f"a {frequencies[max_transmission_index]:.0f} Hz")
    c.metric(
        "TL a 1.000 Hz",
        f"{sample_tl[3]:.1f} dB")

    st.markdown("### Paso 7 · Conclusión del alumno")
    st.markdown(r"""
    Responde utilizando los resultados obtenidos, no solamente una descripción general:

    - ¿La frecuencia crítica está dentro del intervalo analizado?
    - ¿Qué sucede con el TL cerca de \(f_c\)?
    - ¿En qué frecuencia de la tabla se transmite la mayor fracción de energía?
    - ¿Por qué \(TL\) no es constante para una misma placa?
    """)
    conclusion=st.text_area(
        "Redacta tu conclusión técnica",
        key="lab2_s3_conclusion",height=130,
        placeholder=(
            "Ejemplo de estructura: La placa posee m′ = ... kg/m² y fᶜ = ... Hz. "
            "La curva muestra que... La banda más desfavorable es..."))
    if st.button("Comprobar mi análisis",key="lab2_s3_check_conclusion"):
        if len(conclusion.strip()) < 80:
            st.warning(
                "Desarrolla un poco más la respuesta: incluye m′, fᶜ, una frecuencia "
                "desfavorable y la relación entre τ y TL.")
        else:
            st.success(
                "Tu análisis tiene una extensión suficiente. Contrástalo con los valores "
                "calculados y verifica que no confundas 78° con un único ángulo.")

    check(
        "lab2_s3_q1",
        "¿Qué representa el límite de 78° en este ejercicio?",
        [
            "El único ángulo con que se ensaya la placa",
            "El límite superior de la integración de múltiples incidencias",
            "La frecuencia crítica expresada en grados",
            "El ángulo de montaje del tabique",
        ],
        "El límite superior de la integración de múltiples incidencias",
        "El campo incorpora todos los ángulos entre 0° y 78° con ponderación energética.",
    )
    check(
        "lab2_s3_q2",
        "¿Cuál es el orden correcto para obtener el TL de campo?",
        [
            "Promediar los TL angulares y luego calcular τ",
            "Calcular τ angular, integrar τ y convertir el promedio a TL",
            "Calcular solamente τ a 78°",
            "Promediar las frecuencias y aplicar la ley de masa",
        ],
        "Calcular τ angular, integrar τ y convertir el promedio a TL",
        "Los decibeles no se promedian directamente: primero se integra la energía transmitida.",
    )

def lab2_stage4():
    """Explicación técnica de dos placas simples separadas por una cámara de aire."""
    _lab2_heading(
        4,
        "Pérdida de transmisión en paneles dobles",
        "Comprender el sistema masa–aire–masa, sus frecuencias características y las tres regiones del modelo.",
    )
    _lab2_image(
        "panel_doble",
        "Modelo idealizado: dos placas homogéneas simples separadas por una cámara de aire.",
    )
    st.markdown(r"""
    ### Introducción

    Un panel doble está formado por **dos placas separadas por una cámara de
    aire**. A diferencia de una placa simple, su comportamiento no depende
    solamente de la masa y la rigidez de cada hoja: el aire encerrado actúa como
    un resorte y acopla el movimiento de ambas placas.

    El conjunto puede representarse como un sistema **masa–aire–masa**:

    - La placa 1 constituye la primera masa.
    - La cámara de aire aporta la elasticidad.
    - La placa 2 constituye la segunda masa.

    Este mecanismo produce una frecuencia de resonancia \(f_0\) y obliga a
    estudiar la pérdida por transmisión mediante tres regiones. Por eso, agregar
    una segunda placa no genera la misma mejora en todas las frecuencias.
    """)
    st.info(
        "**Continuidad con la Etapa 3:** cada hoja se calcula primero como una placa "
        "simple con integración de campo entre 0° y 78°. Después, ambas curvas se "
        "combinan mediante la ecuación de panel doble."
    )
    st.caption(
        "En esta explicación se utiliza el modelo teórico ideal. Las correcciones "
        "por absorbente, montantes, fijaciones, fugas y transmisiones laterales no "
        "forman parte de esta etapa."
    )

    st.markdown("### 1 · Propiedades de las dos placas")
    st.markdown(r"""
        Cada hoja conserva las propiedades del panel simple estudiado en la
        Etapa 3. Para la placa \(i\):
    """)
    st.latex(r"m'_i=\rho_i h_i")
    st.latex(r"B_i=\frac{E_i h_i^3}{12}")
    st.caption(
        "Para cada hoja i, m′ es la masa superficial en kg/m² y B es la rigidez "
        "a flexión en N·m."
    )
    _lab2_image(
        "s4_propiedades_placas",
        "Cada hoja aporta masa superficial y rigidez a flexión al sistema doble.",
    )
    _lab2_plain_language_cards(
        "Cada placa conserva su propio peso por metro cuadrado y su propia resistencia a doblarse.",
        "El espesor aumenta la masa linealmente, pero la rigidez crece con el cubo del espesor.",
        "Suponer que dos placas separadas por aire se comportan desde el inicio como una sola placa gruesa.",
    )

    st.markdown("### 2 · Resonancia masa–aire–masa")
    st.markdown(r"""
    En \(f_0\), las dos placas y el aire de la cámara interactúan con mayor
    intensidad. Esta resonancia constituye una zona desfavorable porque puede
    reducir el aislamiento del sistema. Su posición depende de las masas
    superficiales y de la profundidad \(d\) de la cámara:
    """)
    st.latex(
        r"f_0=\frac{1}{2\pi}"
        r"\sqrt{\rho_0c^2}"
        r"\sqrt{\frac{m'_1+m'_2}{m'_1m'_2d}}"
    )
    st.markdown(r"""
    Al aumentar la masa de las hojas o la profundidad de la cámara, \(f_0\)
    normalmente se desplaza hacia frecuencias más bajas.

    La segunda frecuencia característica, \(f_1\), marca el cambio hacia la
    región superior del modelo:
    """)
    st.latex(r"f_1=\frac{c}{2\pi d}")
    st.caption(
        "En ambas expresiones, d se ingresa en metros; ρ₀ = 1,18 kg/m³ y c = 343 m/s."
    )
    _lab2_image(
        "s4_resonancia",
        "En la resonancia, las dos masas quedan acopladas por el resorte neumático de la cámara.",
    )
    _lab2_plain_language_cards(
        "Las placas son las masas y el aire encerrado funciona como un resorte que las conecta.",
        "Una cámara más profunda o placas más pesadas desplazan normalmente f₀ hacia frecuencias bajas.",
        "Pensar que agregar una segunda placa siempre mejora el aislamiento: cerca de f₀ puede aparecer una caída.",
    )

    st.markdown("### 3 · Ecuación por regiones")
    st.latex(
        r"TL_D(f)=\begin{cases}"
        r"TL_{eq}(f), & f<f_0\\[4pt]"
        r"TL_1(f)+TL_2(f)+20\log_{10}(fd)-29, & f_0\leq f<f_1\\[4pt]"
        r"TL_1(f)+TL_2(f)+6, & f\geq f_1"
        r"\end{cases}"
    )
    st.markdown(r"""
    **Región 1 · Bajo \(f_0\).** Las placas se comportan de manera acoplada y se
    representan como un panel equivalente. Todavía no se obtiene el beneficio
    completo de la cámara.
    """)
    st.latex(r"m'_{eq}=m'_1+m'_2")
    st.latex(r"B_{eq}=B_1+B_2")
    st.latex(r"\eta_{eq}=\eta_1+\eta_2")
    st.markdown(r"""
    **Región 2 · Entre \(f_0\) y \(f_1\).** Se desarrolla el comportamiento
    masa–aire–masa. La pérdida por transmisión depende de las dos placas y
    aparece explícitamente la profundidad \(d\) de la cámara.

    **Región 3 · Sobre \(f_1\).** El modelo combina la pérdida por transmisión
    de ambas hojas y agrega 6 dB.
    """)
    st.caption(
        "TL₁, TL₂ y TLₑq se obtienen con el mismo cálculo angular y de campo "
        "utilizado para las placas simples en la Etapa 3."
    )
    _lab2_image(
        "s4_regiones",
        "La respuesta del panel doble cambia al atravesar f₀ y f₁.",
    )
    _lab2_plain_language_cards(
        "La curva no se calcula con una sola regla: el modelo cambia según la frecuencia.",
        "Bajo f₀ domina el conjunto acoplado; entre f₀ y f₁ actúa masa–aire–masa; sobre f₁ se combinan ambas hojas.",
        "Aplicar la ecuación de la región central a todo el espectro o interpretar las discontinuidades como un fenómeno real exacto.",
    )

    materials={
        "Yeso-cartón":{"rho":800.0,"E":2.5,"eta":0.030,"h":12.5},
        "Madera":{"rho":600.0,"E":10.0,"eta":0.020,"h":18.0},
        "Hormigón":{"rho":2400.0,"E":30.0,"eta":0.010,"h":100.0},
    }
    st.markdown("### 4 · Explorador técnico del modelo")
    st.markdown(
        "Modifica los parámetros para observar cómo cambian las masas superficiales, "
        "las frecuencias características y la curva. Esta sección ilustra la teoría; "
        "el ejercicio de aplicación aparece al final."
    )
    col_left,col_right=st.columns(2)
    with col_left:
        st.markdown("#### Placa 1")
        material_1=st.selectbox(
            "Material de la placa 1",list(materials),index=0,
            key="lab2_s4_material_1")
        default_1=materials[material_1]
        h1_mm=st.number_input(
            "Espesor de la placa 1 (mm)",4.0,300.0,float(default_1["h"]),0.5,
            key="lab2_s4_h1")
    with col_right:
        st.markdown("#### Placa 2")
        material_2=st.selectbox(
            "Material de la placa 2",list(materials),index=0,
            key="lab2_s4_material_2")
        default_2=materials[material_2]
        h2_mm=st.number_input(
            "Espesor de la placa 2 (mm)",4.0,300.0,float(default_2["h"]),0.5,
            key="lab2_s4_h2")
    depth_mm=st.slider(
        "Profundidad de la cámara d (mm)",20,300,70,5,
        key="lab2_s4_depth")

    h1=h1_mm/1000
    h2=h2_mm/1000
    d=depth_mm/1000
    m1=default_1["rho"]*h1
    m2=default_2["rho"]*h2
    b1=default_1["E"]*1e9*h1**3/12
    b2=default_2["E"]*1e9*h2**3/12
    eta1=default_1["eta"]
    eta2=default_2["eta"]
    rho_air=1.18
    sound_speed=343.0
    f0=(1/(2*math.pi))*math.sqrt(rho_air*sound_speed**2)*math.sqrt(
        (m1+m2)/(m1*m2*d)
    )
    f1=sound_speed/(2*math.pi*d)

    frequencies=np.arange(50.0,5000.0+1,10.0)
    _,tl1,_,_,_=_panel_simple_field_tl(frequencies,m1,b1,eta1)
    _,tl2,_,_,_=_panel_simple_field_tl(frequencies,m2,b2,eta2)
    _,tl_equivalent,_,_,_=_panel_simple_field_tl(
        frequencies,m1+m2,b1+b2,eta1+eta2
    )
    tl_double=np.empty_like(frequencies)
    region_1=frequencies < f0
    region_2=(frequencies >= f0) & (frequencies < f1)
    region_3=frequencies >= f1
    tl_double[region_1]=tl_equivalent[region_1]
    tl_double[region_2]=(
        tl1[region_2]+tl2[region_2]
        +20*np.log10(frequencies[region_2]*d)-29
    )
    tl_double[region_3]=tl1[region_3]+tl2[region_3]+6

    a,b,c,d_metric=st.columns(4)
    a.metric("Masa placa 1",f"{m1:.2f} kg/m²")
    b.metric("Masa placa 2",f"{m2:.2f} kg/m²")
    c.metric("Resonancia f₀",f"{f0:.0f} Hz")
    d_metric.metric("Transición f₁",f"{f1:.0f} Hz")

    st.markdown("#### Curva y tres regiones del modelo")
    st.markdown(
        "La curva azul gruesa representa el **TL del sistema doble**. Las líneas "
        "punteadas muestran el comportamiento de cada placa por separado. Los fondos "
        "de color identifican las tres regiones del modelo y las líneas verticales "
        "marcan las frecuencias características calculadas para la configuración actual."
    )
    fig=go.Figure()
    fig.add_vrect(
        x0=50,x1=min(f0,5000),fillcolor="#dcecff",opacity=.42,
        line_width=0)
    if f0 < 5000:
        fig.add_vrect(
            x0=max(50,f0),x1=min(f1,5000),fillcolor="#fff0cf",opacity=.42,
            line_width=0)
    if f1 < 5000:
        fig.add_vrect(
            x0=max(50,f1),x1=5000,fillcolor="#dcf5e8",opacity=.42,
            line_width=0)
    # El panel doble se dibuja primero para que las curvas de cada placa
    # permanezcan visibles por encima, incluso cuando siguen valores cercanos.
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl_double,mode="lines",name="Panel doble",
        line=dict(color="#173f63",width=5)))
    # Los marcadores alternados permiten reconocer ambas placas cuando son
    # idénticas y sus curvas coinciden exactamente.
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl1,mode="lines",
        name=f"Placa 1: {material_1}",
        line=dict(color="#1976d2",width=2.5,dash="dash")))
    fig.add_trace(go.Scatter(
        x=frequencies,y=tl2,mode="lines",
        name=f"Placa 2: {material_2}",
        line=dict(color="#e07a00",width=2.5,dash="dot")))
    marker_step=max(1,len(frequencies)//16)
    fig.add_trace(go.Scatter(
        x=frequencies[::marker_step],y=tl1[::marker_step],
        mode="markers",showlegend=False,hoverinfo="skip",
        marker=dict(color="#1976d2",size=6,symbol="circle")))
    fig.add_trace(go.Scatter(
        x=frequencies[marker_step//2::marker_step],
        y=tl2[marker_step//2::marker_step],
        mode="markers",showlegend=False,hoverinfo="skip",
        marker=dict(
            color="white",line=dict(color="#e07a00",width=2),
            size=8,symbol="diamond")))
    if 50 <= f0 <= 5000:
        fig.add_vline(x=f0,line_dash="dash",line_color="#d64545",
                      annotation_text="f₀",annotation_position="top right")
    if 50 <= f1 <= 5000:
        fig.add_vline(x=f1,line_dash="dash",line_color="#16845b",
                      annotation_text="f₁",annotation_position="top right")
    fig.update_layout(
        title=dict(
            text="Pérdida por transmisión del sistema de panel doble",
            x=.5,
            xanchor="center",
            font=dict(size=20,color="#173f63"),
        ),
        xaxis_title="Frecuencia (Hz) · escala lineal",
        yaxis_title="TL de campo (dB)",
        xaxis=dict(type="linear",range=[50,5000],dtick=500,showgrid=True),
        yaxis=dict(showgrid=True,gridcolor="rgba(23,63,99,.10)"),
        height=650,hovermode="x unified",
        margin=dict(l=65,r=30,t=90,b=145),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-.20,
            xanchor="center",
            x=.5,
            title_text="",
            bgcolor="rgba(255,255,255,.92)",
            bordercolor="rgba(23,63,99,.18)",
            borderwidth=1,
            font=dict(size=13),
        ))
    st.plotly_chart(fig,use_container_width=True,key="lab2_s4_double_curve")
    st.caption(
        "Las discontinuidades en f₀ y f₁ pertenecen a la formulación idealizada por "
        "tramos. La predicción no incorpora fugas, uniones rígidas ni transmisiones laterales."
    )
    _lab2_plain_language_cards(
        "Mueve los materiales, espesores y la cámara para ver cómo cambia la pared completa, no solo una placa.",
        "Observa primero dónde quedan f₀ y f₁; después compara la línea gruesa del panel doble con las dos líneas punteadas.",
        "Elegir la mejor solución mirando un único valor máximo de TL e ignorar la caída de resonancia y la banda de interés.",
    )

    st.markdown("#### Resultados por frecuencia")
    sample_frequencies=np.array([125.,250.,500.,1000.,2000.,4000.])
    sample_indices=[int(np.argmin(np.abs(frequencies-f))) for f in sample_frequencies]
    table=pd.DataFrame({
        "Frecuencia (Hz)":sample_frequencies.astype(int),
        "TL placa 1 (dB)":tl1[sample_indices],
        "TL placa 2 (dB)":tl2[sample_indices],
        "TL panel doble (dB)":tl_double[sample_indices],
        "Región":[
            "1 · Panel equivalente" if f < f0 else
            "2 · Masa–aire–masa" if f < f1 else
            "3 · Región superior"
            for f in sample_frequencies
        ],
    })
    st.dataframe(
        table.style.format({
            "TL placa 1 (dB)":"{:.1f}",
            "TL placa 2 (dB)":"{:.1f}",
            "TL panel doble (dB)":"{:.1f}",
        }),
        use_container_width=True,hide_index=True)

    st.markdown("### 5 · Ejercicio breve de aplicación")
    st.markdown(r"""
    Una sala de máquinas debe separarse de una oficina mediante dos placas y una
    cámara de aire. Utiliza el explorador con la configuración seleccionada y:

    1. Informa \(m'_1\), \(m'_2\), \(f_0\) y \(f_1\).
    2. Identifica qué región está activa a 125, 500, 1.000 y 4.000 Hz.
    3. Compara el \(TL\) del panel doble con el de cada placa simple.
    4. Modifica solamente la profundidad de la cámara y explica cómo cambian
       \(f_0\), \(f_1\) y el comportamiento entre 500 y 2.000 Hz.
    5. Recomienda una profundidad de cámara y justifica técnicamente tu decisión.
    """)
    analysis=st.text_area(
        "Conclusión técnica",
        key="lab2_s4_analysis",height=150,
        placeholder=(
            "Las masas superficiales son... La resonancia f₀ aparece en... "
            "Entre 500 y 2.000 Hz el sistema... Aumentaría/disminuiría la cámara porque..."
        ))
    if st.button("Comprobar mi análisis",key="lab2_s4_check_analysis"):
        if len(analysis.strip()) < 140:
            st.warning(
                "La conclusión aún es breve. Incluye m′₁, m′₂, f₀, f₁, al menos "
                "dos valores de TL y una decisión sobre la cámara.")
        else:
            st.success(
                "La extensión es suficiente. Verifica que tu decisión se apoye en "
                "los valores calculados y en la región activa del modelo.")

    st.markdown("### 6 · Comprobación conceptual")
    check(
        "lab2_s4_q1",
        "¿Qué representa físicamente el aire contenido en la cámara?",
        ["Un resorte acústico","Una tercera placa rígida","Una fuente sonora","Una fuga"],
        "Un resorte acústico",
        "Las dos placas actúan como masas y el aire encerrado aporta la elasticidad del sistema."
    )
    check(
        "lab2_s4_q2",
        "¿Qué sucede normalmente con f₀ al aumentar la profundidad de la cámara?",
        ["Disminuye","Aumenta","No cambia","Se hace igual a f₁"],
        "Disminuye",
        "Al aumentar d disminuye la rigidez efectiva del resorte de aire y la resonancia se desplaza hacia abajo."
    )
    check(
        "lab2_s4_q3",
        "¿Qué modelo se aplica por debajo de f₀?",
        [
            "Un panel equivalente con masas, rigideces y pérdidas combinadas",
            "La suma de ambas placas más 6 dB",
            "Solo la placa más pesada",
            "La ecuación de la cámara sin considerar las placas",
        ],
        "Un panel equivalente con masas, rigideces y pérdidas combinadas",
        "Bajo f₀ el cálculo utiliza m′eq, Beq y ηeq para representar la respuesta conjunta."
    )
    check(
        "lab2_s4_q4",
        "¿Cuál expresión corresponde a la región entre f₀ y f₁?",
        [
            "TL₁ + TL₂ + 20 log₁₀(fd) − 29",
            "TL₁ + TL₂ + 6",
            "TL de la placa 1 solamente",
            "20 log₁₀(m′₁ + m′₂)",
        ],
        "TL₁ + TL₂ + 20 log₁₀(fd) − 29",
        "En la región intermedia intervienen ambas hojas y aparece explícitamente la profundidad de la cámara."
    )
    check(
        "lab2_s4_q5",
        "¿Por qué esta curva no predice por sí sola el desempeño completo de un tabique construido?",
        [
            "Porque no incorpora montantes, fijaciones, fugas, encuentros ni transmisiones laterales",
            "Porque solo puede calcularse a 78 Hz",
            "Porque las masas superficiales no afectan el aislamiento",
            "Porque un panel doble siempre funciona como una placa simple",
        ],
        "Porque no incorpora montantes, fijaciones, fugas, encuentros ni transmisiones laterales",
        "El ejercicio representa el mecanismo ideal de dos placas y una cámara; la obra agrega caminos estructurales y defectos posibles."
    )

def lab2_stage5():
    _lab2_heading(
        5,
        "Del panel doble ideal al tabique real",
        "Distinguir conexiones lineales metálicas y de madera, y reconocer el principio de una conexión puntual.",
    )

    st.markdown("""
    En la Etapa 4 estudiamos dos hojas y una cámara como un sistema ideal. Un tabique
    construido necesita perfiles, fijaciones y encuentros para sostenerse. Cuando un
    mismo montante une mecánicamente ambas caras aparece un **puente estructural**:
    parte de la vibración evita el camino puramente aéreo de la cámara y se transmite
    por una conexión continua.
    """)
    _lab2_image(
        "s5_tabique_real",
        "Tabique real: placas, cámara absorbente, perfiles y fijaciones forman un solo sistema constructivo.",
    )
    _lab2_plain_language_cards(
        "La cámara no trabaja sola. Los tornillos y montantes pueden funcionar como un camino rígido entre una cara y la otra.",
        "Sigue la energía ámbar que llega a la primera placa y el camino cian que atraviesa los perfiles.",
        "Suponer que agregar lana mineral elimina el puente rígido. El absorbente ayuda a la cámara, pero no desacopla las placas.",
    )

    st.markdown("### 1 · Sistema ideal y sistema conectado")
    st.markdown("""
    En un sistema independiente cada hoja pertenece a una estructura diferente y la
    transmisión está dominada por las dos masas, la cámara y su amortiguamiento. En
    una conexión lineal, un montante o pie derecho continuo acopla ambas caras a lo
    largo de una línea. Esa unión cambia el mecanismo y limita el beneficio del
    desacoplamiento.
    """)
    _lab2_image(
        "s5_ideal_vs_conectado",
        "Comparación conceptual: doble estructura independiente y estructura conectada mediante montantes continuos.",
    )
    _lab2_plain_language_cards(
        "Dos hojas separadas pueden vibrar con mayor independencia. Si las amarramos con el mismo perfil, la vibración encuentra un atajo.",
        "Compara la intensidad de la onda transmitida y la concentración de energía en las uniones.",
        "Comparar ambos sistemas solo por su masa total. La forma en que las hojas están conectadas también controla el resultado.",
    )

    st.markdown("### 2 · Conexión lineal con perfilería metálica")
    st.markdown("""
    En un tabique de yeso-cartón, los tornillos fijan ambas caras a montantes metálicos
    compartidos. Cada montante forma una **línea vertical continua de conexión
    estructural**. La vibración de la primera hoja puede entrar al perfil y volver a
    radiarse desde la segunda hoja a lo largo de esa línea.
    """)
    _lab2_image(
        "s5_conexion_lineal_metal",
        "Conexión lineal metálica: las dos caras quedan vinculadas por montantes continuos de acero galvanizado.",
    )
    _lab2_plain_language_cards(
        "El perfil metálico funciona como un puente largo y continuo entre las dos caras del tabique.",
        "Sigue el recorrido placa → tornillos → montante metálico → tornillos → placa opuesta.",
        "Creer que cada tornillo constituye por sí solo una conexión puntual. Aquí los tornillos descargan sobre un mismo perfil continuo: el conjunto se modela como conexión lineal.",
    )

    st.markdown("### 3 · Conexión lineal con pies derechos de madera")
    st.markdown("""
    El principio es el mismo cuando ambas caras se fijan a un **pie derecho continuo
    de madera**. Cambia el material y su rigidez, pero la geometría de la unión sigue
    siendo lineal: el elemento estructural se prolonga verticalmente y conecta las
    hojas a lo largo de toda su altura.
    """)
    _lab2_image(
        "s5_conexion_lineal_madera",
        "Conexión lineal de madera: ambas caras se fijan a pies derechos continuos compartidos.",
    )
    _lab2_plain_language_cards(
        "Aunque sea madera, el pie derecho también crea un camino estructural continuo entre ambas caras.",
        "Observa que la energía se distribuye a lo largo de cada elemento vertical y no solo en un punto aislado.",
        "Clasificar la unión por el material. Lo que define que sea lineal es la continuidad geométrica del contacto, no que el montante sea metálico o de madera.",
    )

    st.markdown("### 4 · Conexión puntual")
    st.markdown("""
    Una materialización constructiva real del apoyo puntual es el sistema de
    **clips acústicos resilientes**. Cada clip se fija al montante en una posición
    discreta y sostiene un canal metálico horizontal. Las dos placas de esa cara se
    atornillan al canal, no directamente al montante.

    El contacto con la estructura primaria queda concentrado en los clips separados.
    El canal es continuo porque debe sostener las placas, pero su vínculo con los
    montantes ocurre solo en esos puntos resilientes. El resultado depende del tipo,
    rigidez, separación y carga admisible de los clips, además de la configuración
    completa del tabique.
    """)
    _lab2_image(
        "s5_conexion_puntual",
        "Apoyo puntual real: clips resilientes separados fijan canales horizontales que reciben las dos placas de una cara.",
    )
    _lab2_plain_language_cards(
        "Las placas descansan sobre canales; los canales se conectan a los montantes mediante clips separados que reducen el puente rígido directo.",
        "Sigue el montaje real: montante → clip resiliente → canal horizontal → dos placas de yeso-cartón.",
        "Confundir el canal horizontal con una conexión lineal rígida al montante. El canal es continuo, pero se apoya en clips discretos y resilientes.",
    )

    st.markdown("### 5 · Comparación constructiva")
    st.markdown("""
    | Tipo de conexión | Cómo se reconoce | Camino estructural |
    |---|---|---|
    | Lineal metálica | Ambas caras fijadas a un perfil metálico continuo compartido | A lo largo del montante |
    | Lineal de madera | Ambas caras fijadas a un pie derecho continuo compartido | A lo largo del pie derecho |
    | Puntual resiliente | Clips separados fijados a montantes sostienen canales horizontales | Concentrado en cada clip antes de distribuirse por el canal |

    **Idea clave:** metal y madera corresponden a dos materializaciones de una
    conexión lineal rígida. El sistema de clips introduce apoyos puntuales
    resilientes reales; no debe calcularse con la ecuación de conexión lineal sin
    disponer del modelo o de datos de ensayo del sistema específico.
    """)

    st.markdown("### 6 · Cómo se obtiene el TL total del tabique")
    st.markdown("""
    El tabique transmite energía simultáneamente por dos caminos: el campo
    acústico de la cámara y las conexiones rígidas. Por ello, sus pérdidas por
    transmisión no se suman ni se restan directamente en decibeles. Primero se
    calcula cada camino, luego se transforma cada TL en coeficiente de transmisión
    y finalmente se suman las energías transmitidas.
    """)

    st.markdown("#### 6.1 · Camino aéreo: TL base con cámara vacía")
    st.markdown("""
    Es la pérdida por transmisión de las dos hojas separadas por una **cámara de
    aire vacía**, antes de incorporar montantes o material absorbente. Se calcula
    por bandas de frecuencia y cambia según la región en que se encuentre el
    sistema.
    """)
    st.latex(r"""
    TL_{\mathrm{base}}(f)=
    \begin{cases}
    TL_{m'_1+m'_2}(f), & f<f_0 \\[4pt]
    TL_1(f)+TL_2(f)+20\log_{10}(f\,d)-29, & f_0\leq f<f_l \\[4pt]
    TL_1(f)+TL_2(f)+6, & f\geq f_l
    \end{cases}
    """)
    st.latex(
        r"f_0=\frac{1}{2\pi}\sqrt{\rho_0c^2"
        r"\left(\frac{m'_1+m'_2}{m'_1m'_2d}\right)}"
    )
    st.latex(r"f_l=\frac{c}{2\pi d}")
    st.markdown(r"""
- $TL_1(f)$ y $TL_2(f)$: pérdida por transmisión de cada hoja.
- $TL_{m'_1+m'_2}(f)$: pérdida por transmisión de una hoja equivalente con la masa superficial total.
- $d$: profundidad de la cámara, en metros.
- $f_0$: frecuencia de resonancia masa–aire–masa.
- $f_l$: frecuencia límite utilizada para separar las regiones del modelo.
    """)

    st.markdown("#### 6.2 · Camino estructural: TL de la conexión lineal")
    st.markdown("""
    Cuando ambas caras se vinculan mediante montantes continuos, el modelo
    simplificado representa el sistema conectado a partir de una hoja equivalente
    y una corrección asociada a la geometría de las líneas de unión.
    """)
    st.latex(r"TL_{\mathrm{línea}}(f)=TL_{m'_1+m'_2}(f)+\Delta TL_{m'}")
    st.latex(
        r"\Delta TL_{m'}="
        r"10\log_{10}(b\,f_c)+"
        r"20\log_{10}\left(\frac{m'_1}{m'_1+m'_2}\right)-18"
    )
    st.markdown(r"""
- $b$: separación entre líneas de conexión o montantes, en metros.
- $f_c$: frecuencia crítica más alta de las dos hojas, en Hz.
- $m'_1$ y $m'_2$: masas superficiales de las hojas 1 y 2, en $\mathrm{kg/m^2}$.
- $TL_{m'_1+m'_2}(f)$: pérdida por transmisión de una hoja equivalente cuya masa superficial es $m'_1+m'_2$.
- $\Delta TL_{m'}$: corrección, en decibeles, asociada a la conexión lineal.
    """)

    st.markdown("#### 6.3 · TL total con cámara vacía")
    st.markdown("""
    El camino aéreo y el camino estructural actúan **en paralelo**. Para
    combinarlos, cada pérdida por transmisión se convierte primero en su
    coeficiente de transmisión:
    """)
    st.latex(r"\tau_{\mathrm{base}}(f)=10^{-TL_{\mathrm{base}}(f)/10}")
    st.latex(r"\tau_{\mathrm{línea}}(f)=10^{-TL_{\mathrm{línea}}(f)/10}")
    st.latex(
        r"\boxed{TL_{\mathrm{total}}(f)=-10\log_{10}\left["
        r"10^{-TL_{\mathrm{base}}(f)/10}+"
        r"10^{-TL_{\mathrm{línea}}(f)/10}\right]}"
    )
    st.markdown("""
    El resultado queda siempre controlado por el camino que transmite más
    energía, es decir, por el que posee el TL más bajo. Si ambos caminos tienen
    exactamente el mismo TL, su combinación entrega 3 dB menos que cada camino
    por separado.
    """)

    st.markdown("#### 6.4 · Camino aéreo con material absorbente")
    st.markdown("""
    El material poroso incorporado dentro de la cámara disipa energía mediante
    pérdidas viscosas y térmicas, reduce las reflexiones internas y amortigua el
    acoplamiento acústico entre las hojas. Su aporte modifica únicamente el
    camino aéreo de la cámara:
    """)
    st.latex(
        r"TL_{\mathrm{abs}}(f)="
        r"TL_{\mathrm{base}}(f)+\Delta TL_{\mathrm{abs}}(f)"
    )
    st.markdown(r"""
- $\Delta TL_{\mathrm{abs}}(f)$: mejora por banda asociada al amortiguamiento de la cámara.
- El absorbente **no elimina** el camino mecánico formado por montantes y fijaciones.
- Su efecto real depende de la frecuencia, resistividad al flujo, espesor, profundidad de cámara y porcentaje de llenado; no solamente de la densidad nominal.
    """)

    st.markdown("#### 6.5 · TL total con conexión lineal y absorbente")
    st.markdown("""
    El resultado final se obtiene combinando el camino aéreo ya amortiguado con
    el camino estructural, que permanece activo:
    """)
    st.latex(r"\tau_{\mathrm{abs}}(f)=10^{-TL_{\mathrm{abs}}(f)/10}")
    st.latex(r"\tau_{\mathrm{total,abs}}(f)=\tau_{\mathrm{abs}}(f)+\tau_{\mathrm{línea}}(f)")
    st.latex(
        r"\boxed{TL_{\mathrm{total,abs}}(f)=-10\log_{10}\left["
        r"10^{-TL_{\mathrm{abs}}(f)/10}+"
        r"10^{-TL_{\mathrm{línea}}(f)/10}\right]}"
    )
    st.markdown(r"""
    **Lectura física:** el absorbente reduce la energía transmitida por la cámara,
    pero no interrumpe la transmisión por perfiles y fijaciones. Cuando
    $TL_{\mathrm{abs}}$ supera ampliamente a $TL_{\mathrm{línea}}$, el camino
    estructural domina y el resultado final se aproxima a
    $TL_{\mathrm{línea}}$. Por eso la mejora del TL total puede ser menor que
    $\Delta TL_{\mathrm{abs}}$.
    """)

    st.markdown("#### 6.6 · Resultado completo por frecuencia")
    st.markdown(r"""
    En cada banda se deben informar los cinco valores siguientes:

    | Resultado | Significado |
    |---|---|
    | $TL_{\mathrm{base}}(f)$ | Camino aéreo del panel doble con cámara vacía |
    | $TL_{\mathrm{línea}}(f)$ | Camino mecánico asociado a la conexión lineal |
    | $TL_{\mathrm{total}}(f)$ | Resultado de cámara vacía + conexión lineal |
    | $TL_{\mathrm{abs}}(f)$ | Camino aéreo con material absorbente |
    | $TL_{\mathrm{total,abs}}(f)$ | Resultado final de absorbente + conexión lineal |

    **Secuencia correcta:** se calcula el TL de cada camino, se convierte a
    $\tau$, se suman los coeficientes de transmisión y se vuelve a decibeles.
    """)
    st.warning("""
    **Alcance del cálculo:** la descomposición permite comprender por separado la
    cámara, la conexión y el absorbente. Es un modelo pedagógico y no reemplaza
    un ensayo de laboratorio ni incorpora automáticamente fugas, cajas eléctricas,
    encuentros, transmisiones laterales o errores de montaje.
    """)

    st.markdown("### 7 · Laboratorio interactivo: construye el tabique")
    st.info(
        "Modifica las propiedades de las hojas y la cámara. El laboratorio calcula "
        "el comportamiento acústico del tabique y lo compara con una hoja equivalente "
        "de igual masa superficial total."
    )
    _lab2_image(
        "s5_geometria_camara_montantes",
        "Geometría utilizada por el modelo: d es la profundidad libre de la cámara, "
        "medida perpendicularmente entre las caras interiores de las hojas; b es la "
        "separación eje a eje entre dos montantes consecutivos.",
    )
    st.markdown("""
    **Cómo leer las dos dimensiones del render**

    - **d · Profundidad de la cámara:** distancia perpendicular entre las caras
      interiores de las dos hojas. Se ingresa en milímetros y se convierte a metros
      para calcular las frecuencias **f₀** y **fₗ**.

    - **b · Separación de montantes:** distancia horizontal **eje a eje** entre
      dos perfiles consecutivos. No corresponde al ancho libre del paño. Interviene
      en la corrección del camino de transmisión por conexión lineal, **ΔTLₘ′**.
    """)
    support_type=st.radio(
        "Tipo de conexión lineal que deseas representar",
        ["Perfilería metálica", "Pies derechos de madera"],
        horizontal=True,
        key="s5_real_support_type",
    )
    if support_type=="Perfilería metálica":
        st.info(
            "Perfilería metálica liviana · Sus alas y alma delgada son más flexibles "
            "que un pie derecho macizo. Esa resiliencia suele reducir el acoplamiento "
            "mecánico entre las dos hojas y entregar mayor aislamiento que una "
            "estructura de madera equivalente. Un perfil metálico más grueso y rígido "
            "puede perder parte de esa ventaja."
        )
    else:
        st.warning(
            "Pies derechos de madera · Su sección maciza presenta mayor rigidez y "
            "normalmente forma un puente mecánico más eficaz entre ambas hojas. Por "
            "ello, una solución equivalente suele aislar menos que con perfilería "
            "metálica liviana, especialmente cuando las placas están fijadas "
            "directamente a ambos lados del mismo pie derecho."
        )
    st.caption(
        "Alcance del cálculo: la ecuación simplificada disponible representa una "
        "conexión lineal genérica y todavía entrega el mismo valor para metal y "
        "madera. La diferencia real depende de la rigidez y geometría del montante, "
        "su espesor o sección, la separación, las fijaciones y las capas de placa. "
        "Por rigor técnico no se aplica una corrección arbitraria sin datos mecánicos "
        "o resultados de ensayo de la solución constructiva."
    )
    c1,c2,c3,c4=st.columns(4)
    m1=c1.number_input("Masa hoja 1 · m′₁ (kg/m²)",5.0,80.0,10.0,1.0,key="s5_real_m1")
    m2=c2.number_input("Masa hoja 2 · m′₂ (kg/m²)",5.0,80.0,10.0,1.0,key="s5_real_m2")
    depth=c3.number_input("Profundidad de cámara · d (mm)",30,300,70,10,key="s5_real_d")
    spacing=c4.select_slider(
        "Separación de montantes · b (m)",
        options=[0.30,0.40,0.45,0.60,0.80,1.00],
        value=0.60,
        key="s5_real_b",
    )
    # Las hojas se representan como placas homogéneas de yeso-cartón. A partir
    # de la masa superficial seleccionada se obtiene el espesor equivalente,
    # su rigidez de flexión y, finalmente, la frecuencia crítica. De esta forma
    # f_c es un resultado físico del modelo y no un dato libre del alumno.
    leaf_density=800.0
    leaf_young=2.5e9
    leaf_poisson=0.30
    leaf_h1=float(m1)/leaf_density
    leaf_h2=float(m2)/leaf_density
    rigidity1=leaf_young*leaf_h1**3/(12.0*(1.0-leaf_poisson**2))
    rigidity2=leaf_young*leaf_h2**3/(12.0*(1.0-leaf_poisson**2))
    sound_speed=343.0
    fc1_value=(
        sound_speed**2/(2.0*np.pi)
        *np.sqrt(float(m1)/rigidity1)
    )
    fc2_value=(
        sound_speed**2/(2.0*np.pi)
        *np.sqrt(float(m2)/rigidity2)
    )

    c5,c6,c7=st.columns(3)
    c5.metric("Frecuencia crítica calculada · hoja 1",f"{fc1_value:.0f} Hz")
    c6.metric("Frecuencia crítica calculada · hoja 2",f"{fc2_value:.0f} Hz")
    selected_f=c7.selectbox(
        "Banda que deseas inspeccionar (Hz)",
        LAB2_FREQS.tolist(),
        index=9,
        key="s5_real_f",
    )
    st.caption(
        "Las frecuencias críticas no son parámetros seleccionables. Se calculan "
        "automáticamente para hojas homogéneas de yeso-cartón a partir de m′, "
        "ρ = 800 kg/m³, E = 2,5 GPa y ν = 0,30."
    )

    c8,c9,c10=st.columns(3)
    eta1=c8.number_input(
        "Factor de pérdidas hoja 1 · η₁",
        min_value=0.005,max_value=0.200,value=0.030,step=0.005,
        format="%.3f",key="s5_real_eta1",
    )
    eta2=c9.number_input(
        "Factor de pérdidas hoja 2 · η₂",
        min_value=0.005,max_value=0.200,value=0.030,step=0.005,
        format="%.3f",key="s5_real_eta2",
    )
    absorbent_type=c10.selectbox(
        "Absorbente en la cámara",
        ["Sin absorbente","Lana mineral 40 kg/m³","Lana mineral 60 kg/m³","Lana mineral 80 kg/m³"],
        index=2,key="s5_real_absorbent",
    )

    def _angular_transmission_integral(surface_mass,rigidity,loss_factor,frequencies):
        rho_air=1.18
        sound_speed=343.0
        theta=np.linspace(0.0,(4.0/9.0)*np.pi,720)
        sin_theta=np.sin(theta)
        cos_theta=np.cos(theta)
        values=[]
        for frequency in np.asarray(frequencies,dtype=float):
            omega=2.0*np.pi*frequency
            mass_term=(omega*surface_mass*cos_theta)/(2.0*rho_air*sound_speed)
            bending_term=((omega**2)*rigidity*(sin_theta**4))/(surface_mass*sound_speed**4)
            denominator=(1.0+loss_factor*mass_term*bending_term)**2+(mass_term*(1.0-bending_term))**2
            angular_integrand=(1.0/denominator)*cos_theta*sin_theta
            angular_integral=float(np.trapezoid(angular_integrand,theta))
            transmission=max(angular_integral*2.0904,1e-12)
            values.append(10.0*np.log10(1.0/transmission))
        return np.asarray(values,dtype=float)

    rho_air=1.18
    cavity_depth=max(float(depth)*1e-3,1e-4)
    tl_leaf1=_angular_transmission_integral(float(m1),rigidity1,float(eta1),LAB2_FREQS)
    tl_leaf2=_angular_transmission_integral(float(m2),rigidity2,float(eta2),LAB2_FREQS)
    equivalent=_angular_transmission_integral(
        float(m1+m2),rigidity1+rigidity2,float(eta1+eta2),LAB2_FREQS,
    )
    f0=(
        (1.0/(2.0*np.pi))*np.sqrt(rho_air*sound_speed**2)
        *np.sqrt((float(m1)+float(m2))/(float(m1)*float(m2)*cavity_depth))
    )
    fl=sound_speed/(2.0*np.pi*cavity_depth)
    absorbent_gain={
        "Sin absorbente":0.0,
        "Lana mineral 40 kg/m³":1.5,
        "Lana mineral 60 kg/m³":3.0,
        "Lana mineral 80 kg/m³":4.5,
    }[absorbent_type]
    absorbent_gain_curve=np.where(
        LAB2_FREQS < fl,
        absorbent_gain,
        absorbent_gain*0.35,
    )
    base=np.zeros_like(LAB2_FREQS,dtype=float)
    for band_index,frequency in enumerate(LAB2_FREQS):
        if frequency<f0:
            base[band_index]=equivalent[band_index]
        elif frequency<fl:
            base[band_index]=(
                tl_leaf1[band_index]+tl_leaf2[band_index]
                +20.0*np.log10(max(float(frequency)*cavity_depth,1e-12))-29.0
            )
        else:
            base[band_index]=(
                tl_leaf1[band_index]+tl_leaf2[band_index]+6.0
            )

    fc_high=max(fc1_value,fc2_value)
    line_correction=(
        10.0*np.log10(max(float(spacing)*fc_high,1e-12))
        +20.0*np.log10(float(m1)/(float(m1)+float(m2)))
        -18.0
    )
    line_path=equivalent+line_correction
    air_abs=base+absorbent_gain_curve
    tau_base=np.power(10.0,-base/10.0)
    tau_line=np.power(10.0,-line_path/10.0)
    tau_air_abs=np.power(10.0,-air_abs/10.0)
    total_empty=-10.0*np.log10(np.maximum(tau_base+tau_line,1e-12))
    total_abs=-10.0*np.log10(np.maximum(tau_air_abs+tau_line,1e-12))
    total_abs_improvement=total_abs-total_empty
    idx=int(np.where(LAB2_FREQS==selected_f)[0][0])
    has_absorbent=absorbent_type!="Sin absorbente"
    absorbent_card_title=(
        "2 · Cámara absorbente · sin conexión"
        if has_absorbent else
        "2 · Cámara vacía · sin conexión (sin absorbente seleccionado)"
    )
    real_card_title=(
        "🟢 4 · TL REAL · absorbente + conexión"
        if has_absorbent else
        "🟢 4 · TL REAL · cámara vacía + conexión"
    )

    st.markdown("#### Comparación de las cuatro configuraciones")
    st.caption(
        f"Resultados en la banda de {selected_f} Hz · "
        f"f₀ = {f0:.0f} Hz · fₗ = {fl:.0f} Hz"
    )
    a,b,c,d=st.columns(4)
    a.metric(
        f"1 · Cámara vacía · sin conexión · {selected_f} Hz",
        f"{base[idx]:.1f} dB",
        help="TL del camino aéreo ideal: dos hojas separadas por una cámara vacía, sin montantes que unan ambas caras.",
    )
    b.metric(
        f"{absorbent_card_title} · {selected_f} Hz",
        f"{air_abs[idx]:.1f} dB",
        delta=f"{absorbent_gain_curve[idx]:+.1f} dB por absorbente",
        help="TL del camino aéreo después de incorporar el aporte por banda del material absorbente, todavía sin conexión lineal.",
    )
    c.metric(
        f"3 · Cámara vacía · con conexión · {selected_f} Hz",
        f"{total_empty[idx]:.1f} dB",
        delta=f"{total_empty[idx]-base[idx]:+.1f} dB por conexión",
        delta_color="normal",
        help="Resultado de combinar energéticamente el camino aéreo de la cámara vacía con el camino mecánico de la conexión lineal.",
    )
    d.metric(
        f"{real_card_title} · {selected_f} Hz",
        f"{total_abs[idx]:.1f} dB",
        delta=f"{total_abs_improvement[idx]:+.1f} dB de mejora real",
        help="Resultado constructivo final: camino aéreo con absorbente combinado energéticamente con la conexión lineal.",
    )

    st.info(
        f"**Lectura comparativa a {selected_f} Hz:** sin conexión, la cámara vacía "
        f"entrega {base[idx]:.1f} dB y la cámara con {absorbent_type.lower()} "
        f"entrega {air_abs[idx]:.1f} dB. Al incorporar la conexión lineal, la "
        f"cámara vacía queda en {total_empty[idx]:.1f} dB. La configuración "
        f"completa —absorbente más conexión— entrega un **TL real de "
        f"{total_abs[idx]:.1f} dB**, equivalente a una mejora real de "
        f"{total_abs_improvement[idx]:+.1f} dB respecto de la misma conexión "
        f"con cámara vacía."
    )

    with st.expander("Ver resultados numéricos en todas las bandas", expanded=True):
        results_by_band=pd.DataFrame({
            "Frecuencia (Hz)":LAB2_FREQS.astype(int),
            "1 · Cámara vacía, sin conexión (dB)":np.round(base,1),
            "2 · Cámara absorbente, sin conexión (dB)":np.round(air_abs,1),
            "3 · Cámara vacía, con conexión (dB)":np.round(total_empty,1),
            "4 · TL real: absorbente + conexión (dB)":np.round(total_abs,1),
            "TL del camino lineal usado en el cálculo (dB)":np.round(line_path,1),
            "Aporte del absorbente al camino aéreo (dB)":np.round(absorbent_gain_curve,1),
            "Mejora real entre configuraciones 3 y 4 (dB)":np.round(total_abs_improvement,1),
        })
        st.dataframe(
            results_by_band,
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Las configuraciones 3 y 4 incluyen la conexión. Se obtienen sumando "
            "los coeficientes de transmisión del camino aéreo y del camino lineal; "
            "no mediante suma o resta directa de decibeles."
        )

    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=base,mode="lines+markers",
        name="1 · Cámara vacía · sin conexión",
        line=dict(color="#08a9d8",width=4),marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=air_abs,mode="lines+markers",
        name=absorbent_card_title,
        line=dict(color="#65a30d",width=4,dash="dot"),marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=total_empty,mode="lines+markers",
        name="3 · Cámara vacía · con conexión",
        line=dict(color="#9b59b6",width=4),marker=dict(size=6,symbol="triangle-up"),
    ))
    fig.add_trace(go.Scatter(
        x=LAB2_FREQS,y=total_abs,mode="lines+markers",
        name=real_card_title.replace("🟢 ",""),
        line=dict(color="#1b9e77",width=5),marker=dict(size=7,symbol="square"),
    ))
    fig.add_vline(x=selected_f,line_color="#1d3557",line_dash="dot",line_width=2)
    fig.add_annotation(
        x=selected_f,y=max(
            float(base[idx]),float(air_abs[idx]),
            float(total_empty[idx]),float(total_abs[idx]),
        ),
        text=f"{selected_f} Hz",showarrow=True,arrowhead=2,ay=-42,
        font=dict(color="#17324d"),
    )
    fig.update_layout(
        title="Comparación de las cuatro configuraciones del tabique",
        xaxis_title="Frecuencia central (Hz)",yaxis_title="Pérdida por transmisión TL (dB)",
        xaxis_type="log",hovermode="x unified",height=520,
        margin=dict(l=45,r=25,t=75,b=115),
        legend=dict(
            orientation="h",yanchor="top",y=-0.23,xanchor="center",x=.5,
            bgcolor="rgba(255,255,255,.92)",
        ),
    )
    fig.update_xaxes(
        tickvals=[63,125,250,500,1000,2000,4000],
        ticktext=["63","125","250","500","1k","2k","4k"],
        range=[math.log10(50),math.log10(5000)],autorange=False,
    )
    st.plotly_chart(fig,use_container_width=True,key="lab2_s5_real_wall_curve")

    st.markdown("### 8 · Interpretación automática del diseño")
    if spacing <= .40:
        spacing_reading="La modulación es cerrada: existen muchas líneas de conexión por metro de tabique."
    elif spacing <= .60:
        spacing_reading="La modulación es habitual: el efecto de los montantes sigue siendo parte central del sistema."
    else:
        spacing_reading="La modulación es más abierta: hay menos líneas de conexión, pero debe verificarse la estabilidad constructiva."
    symmetry=abs(m1-m2)/(m1+m2)
    if symmetry < .10:
        mass_reading="Las hojas son casi simétricas; sus respuestas críticas pueden concentrarse en zonas similares."
    else:
        mass_reading="Las hojas son asimétricas; esto puede separar parcialmente sus respuestas críticas."
    if st.session_state.get("role")=="Docente":
        with st.container(border=True):
            st.markdown("#### 🔐 Lectura docente · ¿En qué frecuencias actúa mejor el absorbente?")
            st.markdown(
                "Para la configuración seleccionada, las frecuencias que delimitan "
                "las regiones de análisis son:"
            )
            freq_col_1, freq_col_2 = st.columns(2)
            with freq_col_1:
                st.caption("Resonancia masa–aire–masa")
                st.latex(rf"f_0 \approx {f0:.0f}\ \mathrm{{Hz}}")
            with freq_col_2:
                st.caption("Frecuencia límite del modelo")
                st.latex(rf"f_l \approx {fl:.0f}\ \mathrm{{Hz}}")
            st.markdown(
                """
                Estos valores permiten interpretar el aporte del material poroso por regiones:

                1. **Bajo f₀: aporte generalmente limitado.** Las longitudes de onda
                   son grandes y el comportamiento está controlado principalmente por las
                   masas de las hojas y la rigidez del aire encerrado. La lana puede
                   introducir amortiguamiento, pero no reemplaza masa, mayor separación ni
                   desacoplamiento. En esta zona no debe esperarse una ganancia uniforme
                   importante de TL.

                2. **En torno a f₀: aporte especialmente valioso.** El material poroso
                   disipa energía por pérdidas viscosas y térmicas y reduce el factor de
                   calidad de la resonancia masa–aire–masa. Su principal beneficio es
                   hacer menos profundo y menos abrupto el valle de TL. Normalmente
                   amortigua la resonancia más de lo que desplaza su frecuencia central.

                3. **Entre f₀ y fₗ: región de mejor eficacia de banda ancha.**
                   Aquí disminuyen las reflexiones múltiples, las ondas estacionarias y el
                   acoplamiento acústico entre hojas. El efecto aumenta cuando el material
                   ocupa una fracción importante de la cámara sin quedar excesivamente
                   comprimido y posee una resistividad al flujo adecuada.

                4. **Sobre fₗ: el absorbente todavía controla el campo de la cámara,
                   pero la mejora adicional del TL total puede estabilizarse.** En esta
                   región pueden dominar la coincidencia de las placas, los montantes,
                   tornillos, encuentros y otros puentes estructurales. Si el **TL de la
                   conexión lineal** es menor que el TL del camino aéreo, agregar
                   más absorbente producirá poca mejora en el **TL real**.
                """
            )
            st.markdown(
                fr"""
                **Lectura de este diseño:** se seleccionó **{absorbent_type}** y una cámara
                de **{depth:.0f} mm**. {spacing_reading} {mass_reading} La frecuencia
                crítica dominante es **{fc_high:.0f} Hz** y la corrección del modelo
                lineal es **{line_correction:+.1f} dB**. El resultado final se obtiene
                combinando energéticamente el camino aéreo absorbido con el camino por
                {support_type.lower()}; el absorbente no se suma directamente al TL de
                los montantes.

                **Criterio profesional:** no debe elegirse una lana solamente por su
                densidad nominal. El comportamiento depende de la **resistividad al
                flujo**, espesor instalado, porcentaje de llenado, compresión, posición,
                profundidad de la cámara y frecuencia. Este laboratorio representa esas
                tendencias mediante una ganancia pedagógica por bandas; no constituye la
                predicción certificada de un producto ni reemplaza un ensayo.
                """
            )

    with st.expander("Ver procedimiento matemático paso a paso"):
        st.markdown("**1. Masa superficial total**")
        st.latex(
            rf"m'_1+m'_2={m1:.1f}+{m2:.1f}={m1+m2:.1f}\ \mathrm{{kg/m^2}}"
        )

        st.markdown("**2. Rigidez de cada hoja**")
        st.latex(r"B_i=m'_i\left(\frac{c^2}{2\pi f_{c,i}}\right)^2")
        st.latex(
            rf"B_1={rigidity1:.2f}\ \mathrm{{N\,m}},"
            rf"\qquad B_2={rigidity2:.2f}\ \mathrm{{N\,m}}"
        )

        st.markdown(
            "**3. Transmisión angular:** el modelo integra la transmisión de cada "
            "hoja para ángulos de incidencia entre 0° y 80°."
        )

        st.markdown("**4. Frecuencia de resonancia masa–aire–masa**")
        st.latex(rf"f_0={f0:.1f}\ \mathrm{{Hz}}")

        st.markdown("**5. Frecuencia límite de la cámara**")
        st.latex(rf"f_l={fl:.1f}\ \mathrm{{Hz}}")

        st.markdown("**6. Corrección del modelo de conexión lineal**")
        st.latex(
            rf"\Delta TL_{{m'}}="
            rf"10\log_{{10}}({float(spacing):.2f}\cdot {fc_high:.0f})+"
            rf"20\log_{{10}}\left(\frac{{{float(m1):.1f}}}"
            rf"{{{float(m1):.1f}+{float(m2):.1f}}}\right)-18"
            rf"={line_correction:.2f}\ \mathrm{{dB}}"
        )
        st.latex(
            rf"TL_\mathrm{{línea}}({selected_f})="
            rf"TL_{{m'_1+m'_2}}({selected_f})+\Delta TL_{{m'}}="
            rf"{equivalent[idx]:.1f}+({line_correction:.2f})="
            rf"{line_path[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.markdown("**7. TL total con cámara vacía**")
        st.latex(
            rf"TL_\mathrm{{total}}({selected_f})=-10\log_{{10}}\left("
            rf"10^{{-{base[idx]:.1f}/10}}+10^{{-{line_path[idx]:.1f}/10}}\right)"
            rf"={total_empty[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.markdown("**8. Camino aéreo con absorbente**")
        st.latex(
            rf"\Delta TL_\mathrm{{abs}}({selected_f})="
            rf"{absorbent_gain_curve[idx]:.1f}\ \mathrm{{dB}}"
        )
        st.latex(
            rf"TL_\mathrm{{abs}}({selected_f})="
            rf"{base[idx]:.1f}+{absorbent_gain_curve[idx]:.1f}="
            rf"{air_abs[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.markdown("**9. TL total final con absorbente y conexión lineal**")
        st.latex(
            rf"TL_\mathrm{{total,abs}}({selected_f})=-10\log_{{10}}\left("
            rf"10^{{-{air_abs[idx]:.1f}/10}}+10^{{-{line_path[idx]:.1f}/10}}\right)"
            rf"={total_abs[idx]:.1f}\ \mathrm{{dB}}"
        )

        st.caption(
            "Las curvas se calculan mediante tres regiones de comportamiento. "
            "El absorbente modifica el camino aéreo; la conexión lineal permanece como "
            "un camino mecánico paralelo. Los resultados totales se obtienen sumando "
            "coeficientes de transmisión y convirtiendo nuevamente a decibeles."
        )

    st.markdown("### 9 · Comprobación conceptual")
    check(
        "lab2_s5_q1",
        "¿Por qué un montante compartido puede reducir el beneficio de una cámara?",
        [
            "Porque crea un camino estructural entre ambas hojas",
            "Porque elimina la masa de las placas",
            "Porque convierte la lana mineral en una fuente sonora",
            "Porque abre necesariamente una fuga de aire",
        ],
        "Porque crea un camino estructural entre ambas hojas",
        "La vibración puede viajar por placas, tornillos y perfil continuo sin depender solo del campo aéreo de la cámara.",
    )
    check(
        "lab2_s5_q2",
        "¿Qué representa b en el modelo de conexión lineal?",
        [
            "La separación entre líneas de conexión o montantes",
            "El espesor de la lana mineral",
            "La profundidad total de ambas placas",
            "La velocidad del sonido",
        ],
        "La separación entre líneas de conexión o montantes",
        "b describe la modulación de las conexiones continuas y se expresa en metros.",
    )
    check(
        "lab2_s5_q3",
        "¿Agregar absorbente dentro de la cámara elimina por sí solo el puente rígido?",
        ["No","Sí","Solo sobre 500 Hz","Solo si ambas hojas pesan lo mismo"],
        "No",
        "El absorbente amortigua el campo de la cámara, pero no separa mecánicamente las fijaciones y perfiles.",
    )
    check(
        "lab2_s5_q4",
        "¿La curva calculada garantiza el desempeño final del tabique en obra?",
        [
            "No, deben considerarse ensayo, montaje, fugas, encuentros y flancos",
            "Sí, porque incorpora todos los detalles constructivos",
            "Sí, pero únicamente si b=0,60 m",
            "No, porque el aislamiento nunca puede calcularse",
        ],
        "No, deben considerarse ensayo, montaje, fugas, encuentros y flancos",
        "El modelo sirve para comprender tendencias; el desempeño real depende de más caminos de transmisión y de la ejecución.",
    )
    check(
        "lab2_s5_q5",
        "¿Qué diferencia geométrica principal existe entre una conexión lineal y una puntual?",
        [
            "La lineal se prolonga continuamente; la puntual actúa en posiciones discretas",
            "La lineal siempre es metálica y la puntual siempre es de madera",
            "La puntual no transmite vibración",
            "No existe ninguna diferencia",
        ],
        "La lineal se prolonga continuamente; la puntual actúa en posiciones discretas",
        "La clasificación depende de cómo se distribuye el acoplamiento: a lo largo de una línea o en puntos separados.",
    )

def lab2_stage6():
    _lab2_heading(6, "Comparación aplicada y cierre parcial",
                  "Contrastar un panel pesado con un tabique liviano de doble estructura.")
    concrete=_simple_real_curve(240,180,5)
    double,f0,fl=_sharp_curve(20,20,140,"Independiente")
    left,right=st.columns(2)
    with left:
        st.markdown("#### Panel pesado")
        _lab2_image("comparador_hormigon")
        st.caption("Hormigón 100 mm · una hoja · m′≈240 kg/m²")
    with right:
        st.markdown("#### Tabique liviano doble")
        _lab2_image("comparador_tabique")
        st.caption("Dos hojas · cámara 140 mm · bastidores independientes")
    _plot_curves([
        ("Hormigón 100 mm",concrete,"solid"),
        ("Tabique doble liviano",double,"dash"),
    ],"Dos estrategias distintas de aislamiento",[(f0,"f₀ doble"),(fl,"fₗ doble")])
    st.success("""
    **Conclusión:** más masa no garantiza superioridad en todas las bandas. Un sistema
    liviano correctamente desacoplado puede alcanzar una pendiente mayor sobre su
    resonancia; el panel pesado suele ser robusto en bajas frecuencias. La decisión exige
    comparar curvas, espectro, espesor, peso, encuentros, costo y calidad de ejecución.
    """)
    st.markdown("### Puente hacia la segunda mitad")
    st.write("En el siguiente bloque se desarrollarán ventanas dobles, bandas de octava y tercio de octava, y los números únicos Rw, C y Ctr.")

def _lab2_pending(stage, title):
    _lab2_heading(stage,title,"Contenido reservado para la segunda mitad de la Clase 1.")
    st.info("Esta etapa se desarrollará después de validar en aula las primeras dos horas.")

def lab2_stage7():
    _lab2_heading(
        7,
        "Bandas de frecuencia: octavas y tercios de octava",
        "Transformar un espectro continuo en bandas normalizadas y elegir la resolución adecuada para interpretar el aislamiento acústico.",
    )

    st.markdown("""
    ### 1 · De una frecuencia continua a grupos comparables

    El sonido puede contener energía en una cantidad prácticamente continua de
    frecuencias. Mostrar cada frecuencia por separado entrega mucho detalle, pero
    dificulta comparar mediciones, materiales y soluciones constructivas.

    Por eso la acústica agrupa la energía en **bandas de frecuencia**. Cada banda
    reúne todas las frecuencias comprendidas entre un límite inferior y un límite
    superior, y se identifica mediante una **frecuencia central**.
    """)
    _lab2_image(
        "stage7_espectro_a_bandas",
        "El analizador agrupa un espectro continuo en intervalos de frecuencia que pueden compararse de manera ordenada.",
    )

    st.markdown(
        """
        <div class="route-grid">
          <div class="route-card"><span class="step">f</span><div><b>Frecuencia</b>
          <p>Indica cuántas oscilaciones ocurren cada segundo. Se expresa en hertz.</p></div></div>
          <div class="route-card"><span class="step">B</span><div><b>Banda</b>
          <p>Intervalo que reúne varias frecuencias para analizarlas como un conjunto.</p></div></div>
          <div class="route-card"><span class="step">fᶜ</span><div><b>Frecuencia central</b>
          <p>Nombre de la banda; no significa que solo se mida esa frecuencia.</p></div></div>
          <div class="route-card"><span class="step">R</span><div><b>Resolución</b>
          <p>Cuanto más estrecha es la banda, mayor detalle conserva el análisis.</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "**En palabras simples:** una banda funciona como una caja. Dentro de ella se "
        "guarda la energía de un intervalo completo, y la frecuencia central es la "
        "etiqueta que usamos para reconocer esa caja."
    )

    st.markdown("### 2 · La escala no se divide en anchos iguales")
    st.write(
        "En una escala lineal se avanza sumando una cantidad fija, por ejemplo "
        "100, 200, 300 y 400 Hz. En las bandas de octava y de tercio se avanza "
        "multiplicando por una razón constante. Por eso su eje natural es logarítmico."
    )
    formula_card(
        "Relación entre frecuencias centrales consecutivas",
        r"f_{c,k+1}=f_{c,k}\,2^{1/b}",
        "<b>f<sub>c,k</sub></b>: frecuencia central de una banda (Hz)<br>"
        "<b>f<sub>c,k+1</sub></b>: frecuencia central siguiente (Hz)<br>"
        "<b>b</b>: número de bandas por octava; b=1 para octavas y b=3 para tercios",
        "Permite construir una sucesión proporcional. En una octava la frecuencia se "
        "duplica; en un tercio se multiplica aproximadamente por 1,26.",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Una octava", "× 2")
        st.caption("125 → 250 → 500 → 1.000 Hz")
    with c2:
        st.metric("Un tercio de octava", "× 1,26")
        st.caption("100 → 125 → 160 → 200 Hz")
    with c3:
        st.metric("Tres tercios", "× 2")
        st.caption("100 → 125 → 160 → 200 Hz")

    st.markdown("### 3 · Frecuencia central y límites de cada banda")
    formula_card(
        "Límites exactos de una banda fraccionaria",
        r"\begin{aligned}"
        r"f_i&=f_c\,2^{-1/(2b)}\\[0.35em]"
        r"f_s&=f_c\,2^{1/(2b)}\\[0.35em]"
        r"f_c&=\sqrt{f_i f_s}"
        r"\end{aligned}",
        "<b>fᵢ</b>: límite inferior de la banda (Hz)<br>"
        "<b>fₛ</b>: límite superior de la banda (Hz)<br>"
        "<b>f<sub>c</sub></b>: frecuencia central exacta (Hz)<br>"
        "<b>b</b>: 1 para octava y 3 para tercio de octava",
        "Sirve para saber qué frecuencias pertenecen realmente a una banda. La "
        "frecuencia central es la media geométrica de sus límites, no la media aritmética.",
    )

    calc_type = st.radio(
        "Calcula los límites de una banda",
        ["Octava", "Tercio de octava"],
        horizontal=True,
        key="lab2_s7_band_calc_type",
    )
    available_centers = (
        [63, 125, 250, 500, 1000, 2000, 4000]
        if calc_type == "Octava"
        else [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630,
              800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
    )
    nominal_fc = st.select_slider(
        "Frecuencia central nominal",
        available_centers,
        value=1000,
        format_func=lambda x: f"{x:,} Hz".replace(",", "."),
        key="lab2_s7_nominal_center",
    )
    bands_per_octave = 1 if calc_type == "Octava" else 3
    lower_limit = nominal_fc * 2 ** (-1 / (2 * bands_per_octave))
    upper_limit = nominal_fc * 2 ** (1 / (2 * bands_per_octave))
    m1, m2, m3 = st.columns(3)
    m1.metric("Límite inferior fᵢ", f"{lower_limit:.1f} Hz")
    m2.metric("Centro nominal fᶜ", f"{nominal_fc} Hz")
    m3.metric("Límite superior fₛ", f"{upper_limit:.1f} Hz")
    st.caption(
        "Los instrumentos muestran centros nominales redondeados —por ejemplo 125 o "
        "160 Hz— para facilitar la lectura. Los filtros se definen mediante relaciones "
        "exactas alrededor de su frecuencia central."
    )

    st.markdown("### 4 · Octava y tercio de octava")
    _lab2_image(
        "stage7_octava_vs_tercio",
        "Arriba: pocas bandas anchas. Abajo: tres subdivisiones por cada octava, capaces de revelar más detalle espectral.",
    )
    comparison = pd.DataFrame([
        ["Octava", "1", "2", "Vista general del espectro", "Diagnóstico rápido y comunicación global"],
        ["Tercio de octava", "3", "2^(1/3) ≈ 1,26", "Mayor detalle", "Aislamiento, normativa y detección de valles"],
    ], columns=["Análisis", "Bandas por octava", "Razón entre centros",
                "Qué muestra", "Uso típico"])
    st.dataframe(comparison, hide_index=True, use_container_width=True)
    st.info(
        "Una banda de tercio no contiene un tercio de la energía de una octava. "
        "Significa que el intervalo de una octava fue dividido logarítmicamente en "
        "tres bandas consecutivas."
    )

    st.markdown("### 5 · ¿Cómo se obtiene el nivel de una banda?")
    formula_card(
        "Suma energética dentro del intervalo",
        r"L_{\mathrm{banda}}=10\log_{10}\left(\sum_{j\in\mathrm{banda}}10^{L_j/10}\right)",
        "<b>L<sub>banda</sub></b>: nivel total de la banda (dB)<br>"
        "<b>Lⱼ</b>: nivel de cada componente o subintervalo contenido en la banda (dB)",
        "Los decibeles no se promedian aritméticamente. Primero se convierten a energía, "
        "se suman y después se vuelve a decibeles.",
    )
    st.warning(
        "**Error frecuente:** sumar o promediar directamente los valores en dB. "
        "Una banda representa la suma energética de todo lo que contiene."
    )

    st.markdown("### 6 · Laboratorio interactivo · del espectro a las bandas")
    st.write(
        "Construye una fuente con contenido amplio y agrega un tono dominante. Luego "
        "compara cuánto detalle conserva cada representación."
    )
    a, b, c = st.columns(3)
    with a:
        tone_frequency = st.slider(
            "Frecuencia del tono",
            80, 4000, 630, 10,
            key="lab2_s7_tone_frequency",
        )
    with b:
        tone_level = st.slider(
            "Intensidad del tono",
            0, 25, 16, 1,
            key="lab2_s7_tone_level",
        )
    with c:
        view_mode = st.radio(
            "Representación",
            ["Espectro fino", "Octavas", "Tercios", "Comparar"],
            key="lab2_s7_view_mode",
        )

    fine_f = np.geomspace(40, 8000, 720)
    base_level = (
        56
        - 5.5 * np.log2(fine_f / 250)
        + 3.2 * np.sin(np.log(fine_f) * 4.1)
        + 1.4 * np.cos(np.log(fine_f) * 9.3)
    )
    peak_width = 0.028
    tone_shape = tone_level * np.exp(
        -0.5 * (np.log2(fine_f / tone_frequency) / peak_width) ** 2
    )
    fine_levels = base_level + tone_shape

    octave_centers = np.array([63, 125, 250, 500, 1000, 2000, 4000], dtype=float)
    third_centers = np.array(
        [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
         1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000], dtype=float
    )

    def aggregate_bands(centers, subdivisions):
        results = []
        for center in centers:
            lo = center * 2 ** (-1 / (2 * subdivisions))
            hi = center * 2 ** (1 / (2 * subdivisions))
            mask = (fine_f >= lo) & (fine_f < hi)
            if not np.any(mask):
                results.append(np.nan)
                continue
            # Each logarithmic sample represents an equal spectral subinterval.
            results.append(10 * np.log10(np.sum(10 ** (fine_levels[mask] / 10))))
        return np.array(results)

    octave_levels = aggregate_bands(octave_centers, 1)
    third_levels = aggregate_bands(third_centers, 3)
    fig = go.Figure()
    if view_mode in ("Espectro fino", "Comparar"):
        fig.add_trace(go.Scatter(
            x=fine_f, y=fine_levels, name="Espectro fino",
            mode="lines", line=dict(color="#f39c3d", width=2),
        ))
    if view_mode in ("Octavas", "Comparar"):
        fig.add_trace(go.Scatter(
            x=octave_centers, y=octave_levels, name="Bandas de octava",
            mode="lines+markers", line=dict(color="#26a7df", width=4),
            marker=dict(size=9),
        ))
    if view_mode in ("Tercios", "Comparar"):
        fig.add_trace(go.Scatter(
            x=third_centers, y=third_levels, name="Bandas de tercio",
            mode="lines+markers", line=dict(color="#25d6b2", width=3),
            marker=dict(size=7),
        ))
    fig.add_vline(
        x=tone_frequency, line_dash="dot", line_color="#ff8a38",
        annotation_text=f"Tono: {tone_frequency} Hz",
        annotation_position="top",
    )
    fig.update_layout(
        title="Una misma fuente, distintas resoluciones",
        xaxis_title="Frecuencia (Hz)", yaxis_title="Nivel relativo (dB)",
        xaxis_type="log", hovermode="x unified", height=470,
        margin=dict(l=35, r=20, t=65, b=40),
        legend=dict(orientation="h", y=1.13),
    )
    fig.update_xaxes(
        tickvals=[50, 63, 100, 125, 250, 500, 1000, 2000, 4000, 8000],
        ticktext=["50", "63", "100", "125", "250", "500", "1k", "2k", "4k", "8k"],
    )
    st.plotly_chart(fig, use_container_width=True)

    nearest_oct = int(octave_centers[np.argmin(np.abs(np.log(octave_centers / tone_frequency)))])
    nearest_third = int(third_centers[np.argmin(np.abs(np.log(third_centers / tone_frequency)))])
    x1, x2, x3 = st.columns(3)
    x1.metric("Tono configurado", f"{tone_frequency} Hz")
    x2.metric("Banda de octava más próxima", f"{nearest_oct} Hz")
    x3.metric("Banda de tercio más próxima", f"{nearest_third} Hz")
    st.success(
        "**Lectura del laboratorio:** la octava entrega una tendencia compacta; el "
        "tercio de octava localiza mejor la zona del tono o del valle. Ninguna crea "
        "energía nueva: solo cambia la resolución con que se agrupa la misma señal."
    )

    st.markdown("### 7 · Relación con el aislamiento acústico")
    st.write("""
    Las curvas de pérdida de transmisión se presentan por bandas porque un elemento
    no aísla igual en todo el espectro. Los tercios de octava permiten reconocer:

    - resonancias y valles estrechos;
    - la región controlada por masa;
    - la caída de coincidencia;
    - diferencias entre dos soluciones que una octava podría ocultar;
    - bandas críticas de una fuente real.
    """)
    st.markdown(
        '<div class="good"><b>Idea central:</b> una octava resume; un tercio diagnostica. '
        'Para evaluar aislamiento acústico y construir índices ponderados se necesita '
        'conservar suficiente detalle por frecuencia.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("role") == "Docente":
        with st.expander("🔐 Lectura docente · precisión técnica y conducción"):
            st.markdown("""
            - Aclare que **frecuencia lineal** y **bandas** no son magnitudes opuestas:
              una escala lineal representa incrementos aditivos; las bandas fraccionarias
              se ordenan mediante razones constantes y se visualizan mejor en escala logarítmica.
            - La frecuencia central mostrada normalmente es **nominal**. Los filtros
              normalizados emplean centros y límites exactos; no conviene deducir límites
              usando el punto medio aritmético.
            - Tres bandas de tercio consecutivas cubren una octava porque sus razones
              se multiplican tres veces y producen una razón total igual a 2.
            - El nivel de octava puede reconstruirse desde sus tres tercios mediante
              suma energética, no mediante promedio de dB.
            - En aislamiento, mayor resolución permite observar resonancia y coincidencia,
              pero no mejora por sí misma la exactitud física del modelo o de la medición.
            """)
            st.latex(
                r"L_{\mathrm{oct}}=10\log_{10}\left("
                r"10^{L_1/10}+10^{L_2/10}+10^{L_3/10}\right)"
            )

    st.markdown("### 8 · Cinco preguntas de comprensión")
    check(
        "lab2_s7_q1",
        "¿Qué representa la frecuencia central de una banda?",
        [
            "La etiqueta de un intervalo comprendido entre dos límites",
            "La única frecuencia que mide el instrumento",
            "El promedio aritmético obligatorio de todos los tonos",
            "La intensidad máxima del sonido",
        ],
        "La etiqueta de un intervalo comprendido entre dos límites",
        "La banda contiene un intervalo completo; la frecuencia central la identifica.",
    )
    check(
        "lab2_s7_q2",
        "¿Qué ocurre con la frecuencia al avanzar una octava completa?",
        ["Se duplica", "Aumenta siempre 100 Hz", "Se triplica", "Disminuye 3 dB"],
        "Se duplica",
        "Entre centros separados por una octava existe una razón de 2.",
    )
    check(
        "lab2_s7_q3",
        "¿Cuántas bandas de tercio de octava cubren una octava?",
        ["Tres", "Dos", "Diez", "Depende del nivel en dB"],
        "Tres",
        "Cada paso multiplica la frecuencia por 2^(1/3); tres pasos producen una razón total de 2.",
    )
    check(
        "lab2_s7_q4",
        "¿Por qué el tercio de octava ayuda a diagnosticar una caída de aislamiento?",
        [
            "Porque conserva más detalle espectral que una octava",
            "Porque siempre entrega 3 dB más",
            "Porque elimina la frecuencia crítica",
            "Porque convierte el aislamiento en absorción",
        ],
        "Porque conserva más detalle espectral que una octava",
        "Sus bandas más estrechas permiten localizar mejor valles, tonos y cambios de pendiente.",
    )
    check(
        "lab2_s7_q5",
        "¿Cómo deben combinarse varios niveles contenidos dentro de una banda?",
        [
            "Mediante suma energética",
            "Promediando directamente los dB",
            "Eligiendo siempre el valor menor",
            "Sumando las frecuencias centrales",
        ],
        "Mediante suma energética",
        "Los dB son logarítmicos: se convierten a energía, se suman y se vuelve a dB.",
    )

def lab2_stage8():
    _lab2_heading(
        8,
        "Número único de aislamiento a ruido aéreo: Rw, C y Ctr",
        "Convertir una curva de reducción sonora por tercios de octava en un descriptor único, sin perder de vista el espectro de la fuente.",
    )

    st.markdown("""
    ### 1 · ¿Por qué se informa Rw y no solamente R o TL?

    Tanto **R** como **TL** describen la reducción de la transmisión sonora en una
    **frecuencia o banda determinada**. Por ejemplo, informar R = 48 dB a 500 Hz
    solo explica lo que ocurre en esa banda: el mismo elemento puede entregar un
    valor menor en graves, uno mayor en agudos y presentar un valle de coincidencia.

    Por eso, un único R o TL no representa el comportamiento global del elemento y
    tampoco permite comparar soluciones si no se indica exactamente la frecuencia.
    En aislamiento a ruido aéreo se informa **Rw** porque resume, mediante un
    procedimiento normalizado, la curva completa de 16 tercios de octava entre
    100 y 3.150 Hz.

    **Rw no reemplaza la curva R(f): la resume.** La curva se conserva para el
    diagnóstico técnico; Rw se usa para declarar, especificar y comparar el
    desempeño mediante un mismo criterio.
    """)
    why_a, why_b, why_c = st.columns(3)
    with why_a:
        st.markdown(
            '<div class="route-card"><span class="step">R o TL</span><div>'
            '<b>Resultado por banda</b><p>Indica cuánto se reduce el sonido en una '
            'frecuencia concreta.</p></div></div>', unsafe_allow_html=True,
        )
    with why_b:
        st.markdown(
            '<div class="route-card"><span class="step">R(f)</span><div>'
            '<b>Diagnóstico completo</b><p>Permite localizar graves débiles, '
            'resonancias y coincidencia.</p></div></div>', unsafe_allow_html=True,
        )
    with why_c:
        st.markdown(
            '<div class="route-card"><span class="step">Rw</span><div>'
            '<b>Comparación normalizada</b><p>Condensa las 16 bandas con una misma '
            'regla de ponderación.</p></div></div>', unsafe_allow_html=True,
        )
    st.warning(
        "**Lectura correcta:** Rw = 52 dB no significa R = 52 dB en todas las "
        "frecuencias. Significa que la curva completa obtuvo un índice ponderado "
        "de 52 dB mediante el procedimiento normalizado."
    )

    st.markdown("""
    ### 2 · Del resultado por bandas al número único

    La reducción sonora **R** de un elemento constructivo cambia con la frecuencia.
    Una pared puede aislar bien en bandas medias y presentar un valle en bajas
    frecuencias o alrededor de la coincidencia. Por eso el resultado físico completo
    sigue siendo la curva **R(f)**.

    Para comparar soluciones y expresar requisitos de forma compacta, el método
    pondera esa curva mediante una referencia normalizada y obtiene **Rw**. Luego,
    los términos **C** y **Ctr** adaptan el resultado a dos familias de espectros.
    """)
    _lab2_image(
        "stage8_airborne_rw",
        "La curva de referencia se ajusta sobre R(f) y el número único Rw se lee en 500 Hz sobre esa referencia desplazada.",
    )
    st.markdown(
        """
        <div class="route-grid">
          <div class="route-card"><span class="step">R(f)</span><div><b>Curva por bandas</b>
          <p>Muestra cuánto reduce el elemento en cada tercio de octava.</p></div></div>
          <div class="route-card"><span class="step">Rw</span><div><b>Valor ponderado</b>
          <p>Resume la curva mediante el ajuste de una referencia normalizada.</p></div></div>
          <div class="route-card"><span class="step">C</span><div><b>Adaptación espectral 1</b>
          <p>Ajusta Rw a fuentes con mayor importancia relativa en frecuencias medias y altas.</p></div></div>
          <div class="route-card"><span class="step">Ctr</span><div><b>Adaptación espectral 2</b>
          <p>Da más importancia al contenido grave típico del tránsito urbano.</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.success(
        "**En palabras simples:** Rw es el titular; C y Ctr explican cómo cambia ese "
        "titular cuando la fuente tiene otro reparto de energía por frecuencia."
    )

    st.markdown("### 3 · ¿Cuándo corresponde usar Rw?")
    st.write("""
    **Rw describe el aislamiento a ruido aéreo de un elemento ensayado en
    laboratorio**, como un muro, tabique, puerta, ventana, piso o cubierta. La fuente
    sonora se ubica en un recinto emisor y se determina cuánto se reduce la energía
    que atraviesa el elemento hacia el recinto receptor.

    No corresponde usar Rw para describir absorción interior, tiempo de reverberación
    ni ruido de impactos. Tampoco debe confundirse con el desempeño aparente de toda
    una construcción terminada, donde pueden intervenir encuentros, fugas y
    transmisiones laterales.
    """)
    a, b, c = st.columns(3)
    with a:
        st.markdown(
            '<div class="good"><b>✓ Sí corresponde</b><br>Transmisión aérea a través '
            'de un elemento separador ensayado.</div>',
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            '<div class="warn"><b>✗ No es absorción</b><br>No indica cuánto sonido '
            'absorbe una superficie dentro del mismo recinto.</div>',
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            '<div class="warn"><b>✗ No es impacto</b><br>No caracteriza golpes, '
            'pisadas ni excitación directa de la estructura.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### 4 · Curva de referencia y desviaciones desfavorables")
    st.write("""
    La **curva de referencia** es una plantilla normalizada con una forma fija. No
    es la curva medida del tabique ni una exigencia independiente. Se coloca sobre
    el mismo gráfico de R(f) y solo puede desplazarse verticalmente, sin deformarla.

    En cada una de las 16 bandas se comparan dos valores. Si la referencia queda
    **por encima** de R(f), al elemento le falta aislamiento respecto de la plantilla
    y aparece una desviación desfavorable. Si R(f) queda por encima, el resultado es
    favorable, pero ese excedente vale cero: una banda muy buena no puede borrar un
    valle de otra banda.
    """)
    formula_card(
        "Desviación desfavorable en cada banda",
        r"d_i=\max\left(0,\;R_{\mathrm{ref},i}-R_i\right)",
        "<b>dᵢ</b>: desviación desfavorable en la banda i (dB)<br>"
        "<b>R<sub>ref,i</sub></b>: valor de la curva de referencia desplazada (dB)<br>"
        "<b>Rᵢ</b>: reducción sonora medida o calculada en esa banda (dB)",
        "Solo existe desviación cuando la curva real queda bajo la referencia. Si la "
        "curva real está por encima, esa diferencia favorable no compensa los valles.",
    )
    formula_card(
        "Condición de ajuste para 16 tercios de octava",
        r"\sum_{i=1}^{16}d_i\leq 32\ \mathrm{dB}",
        "<b>16 bandas</b>: desde 100 hasta 3.150 Hz<br>"
        "<b>32 dB</b>: suma máxima de desviaciones desfavorables",
        "La referencia se mueve verticalmente en pasos de 1 dB. Se busca la posición "
        "más alta que todavía cumple el límite total de 32 dB.",
    )
    st.info(
        "**Importante:** Rw no es el promedio de R, ni el mayor valor de la curva, ni "
        "simplemente R a 500 Hz. Es el valor de la **curva de referencia ya ajustada** "
        "en la banda de 500 Hz."
    )

    st.markdown("#### Compruébalo moviendo la referencia")
    demo_freq = np.array([100, 125, 160, 200, 250, 315, 400, 500,
                          630, 800, 1000, 1250, 1600, 2000, 2500, 3150])
    demo_r = np.array([27, 31, 35, 39, 43, 47, 50, 52,
                       54, 56, 55, 51, 57, 59, 61, 63], dtype=float)
    demo_ref_shape = np.array([33, 36, 39, 42, 45, 48, 51, 52,
                               53, 54, 55, 56, 56, 56, 56, 56], dtype=float)
    demo_rw = st.slider(
        "Posición de la referencia en 500 Hz (dB)", 42, 58, 50, 1,
        key="lab2_s8_demo_reference",
    )
    demo_ref = demo_ref_shape + (demo_rw - 52)
    demo_dev = np.maximum(0.0, demo_ref - demo_r)
    demo_total = float(np.sum(demo_dev))
    demo_fig = go.Figure()
    demo_fig.add_trace(go.Scatter(x=demo_freq, y=demo_r, mode="lines+markers",
                                  name="R(f)", line=dict(color="#25d6b2", width=4)))
    demo_fig.add_trace(go.Scatter(x=demo_freq, y=demo_ref, mode="lines+markers",
                                  name="Referencia desplazada",
                                  line=dict(color="#ff9f43", width=3, shape="hv")))
    for demo_i in np.where(demo_dev > 0)[0]:
        demo_fig.add_trace(go.Scatter(
            x=[demo_freq[demo_i], demo_freq[demo_i]],
            y=[demo_r[demo_i], demo_ref[demo_i]], mode="lines",
            line=dict(color="#ff4d6d", width=5), showlegend=False,
            hovertemplate=f"{demo_freq[demo_i]} Hz<br>Déficit: {demo_dev[demo_i]:.1f} dB<extra></extra>",
        ))
    demo_fig.update_layout(height=430, xaxis_type="log",
                           xaxis_title="Frecuencia central (Hz)",
                           yaxis_title="Reducción sonora (dB)",
                           hovermode="x unified", margin=dict(l=30, r=20, t=35, b=35))
    demo_fig.update_xaxes(tickvals=demo_freq,
                          ticktext=[str(v) if v < 1000 else f"{v/1000:g}k" for v in demo_freq])
    st.plotly_chart(demo_fig, use_container_width=True)
    demo_a, demo_b, demo_c = st.columns(3)
    demo_a.metric("Bandas desfavorables", int(np.sum(demo_dev > 0)))
    demo_b.metric("Suma de desviaciones", f"{demo_total:.1f} dB")
    demo_c.metric("Condición", "Cumple" if demo_total <= 32 else "No cumple")
    if demo_total <= 32:
        st.success("Esta posición cumple Σdᵢ ≤ 32 dB. Intenta subirla 1 dB: solo será la posición final si la nueva suma deja de cumplir.")
    else:
        st.error("Esta posición supera 32 dB. La referencia debe bajarse hasta recuperar el cumplimiento.")

    st.markdown("### 5 · Procedimiento gráfico para obtener Rw")
    st.markdown("""
    1. Se dispone de los valores de **R** en los 16 tercios de octava entre 100 y
       3.150 Hz.
    2. Se superpone la curva de referencia normalizada.
    3. Se calculan únicamente las diferencias donde la referencia queda sobre R.
    4. Se suman esas desviaciones desfavorables.
    5. Se desplaza la referencia en pasos enteros de 1 dB hasta encontrar la posición
       más alta cuya suma no supera 32 dB.
    6. El valor de esa referencia desplazada a 500 Hz es **Rw**.
    """)
    st.warning(
        "**Error frecuente:** permitir que bandas con aislamiento alto compensen un "
        "valle. El método no lo permite: las diferencias favorables valen cero."
    )

    rw_step = st.select_slider(
        "Recorre el procedimiento",
        options=[1, 2, 3, 4, 5], value=1,
        format_func=lambda n: {
            1: "1 · Curva R(f)", 2: "2 · Superponer referencia",
            3: "3 · Identificar déficits", 4: "4 · Verificar Σdᵢ ≤ 32 dB",
            5: "5 · Leer Rw en 500 Hz",
        }[n], key="lab2_s8_rw_step",
    )
    guided = go.Figure()
    guided.add_trace(go.Scatter(x=demo_freq, y=demo_r, mode="lines+markers",
                                name="R(f)", line=dict(color="#25d6b2", width=4)))
    if rw_step >= 2:
        guided.add_trace(go.Scatter(x=demo_freq, y=demo_ref, mode="lines+markers",
                                    name="Curva de referencia",
                                    line=dict(color="#ff9f43", width=3, shape="hv")))
    if rw_step >= 3:
        for demo_i in np.where(demo_dev > 0)[0]:
            guided.add_trace(go.Scatter(x=[demo_freq[demo_i], demo_freq[demo_i]],
                                        y=[demo_r[demo_i], demo_ref[demo_i]], mode="lines",
                                        line=dict(color="#ff4d6d", width=5), showlegend=False))
    if rw_step == 5:
        guided.add_vline(x=500, line_dash="dot", line_color="#ffffff")
        guided.add_annotation(x=500, y=demo_rw, text=f"Rw = {demo_rw} dB",
                              showarrow=True, arrowhead=2, bgcolor="#10263c")
    guided.update_layout(height=400, xaxis_type="log", xaxis_title="Frecuencia (Hz)",
                         yaxis_title="R (dB)", margin=dict(l=30, r=20, t=30, b=35))
    guided.update_xaxes(tickvals=demo_freq,
                        ticktext=[str(v) if v < 1000 else f"{v/1000:g}k" for v in demo_freq])
    st.plotly_chart(guided, use_container_width=True)
    guided_text = {
        1: "Primero se necesita la curva R(f) completa en las 16 bandas.",
        2: "La plantilla conserva su forma y se desplaza verticalmente en pasos enteros de 1 dB.",
        3: "Las líneas rojas son los únicos déficits que se contabilizan; los excedentes valen cero.",
        4: f"La suma actual es {demo_total:.1f} dB. Debe ser menor o igual que 32 dB.",
        5: f"Una vez hallada la posición más alta admisible, se lee la referencia a 500 Hz: Rw = {demo_rw} dB.",
    }[rw_step]
    st.info(guided_text)

    st.markdown("### 6 · ¿Qué significan C y Ctr?")
    st.write("""
    Dos elementos con el mismo Rw pueden comportarse de manera distinta frente a
    una conversación, música o tránsito. Los términos de adaptación espectral
    incorporan esa diferencia mediante espectros normalizados.

    - **C** se usa para la familia espectral con mayor importancia relativa en
      frecuencias medias y altas, asociada, por ejemplo, a actividades de vivienda,
      conversación, juegos infantiles o tránsito ferroviario rápido.
    - **Ctr** se usa para fuentes con contenido grave importante, como tránsito
      urbano, buses, camiones, música con bajos o ciertas fuentes industriales.
    """)
    formula_card(
        "Nivel resultante del espectro adaptado",
        r"X=-10\log_{10}\left(\sum_i10^{(L_i-R_i)/10}\right)",
        "<b>X</b>: aislamiento global frente al espectro considerado (dB)<br>"
        "<b>Lᵢ</b>: nivel relativo normalizado del espectro en la banda i (dB)<br>"
        "<b>Rᵢ</b>: reducción sonora del elemento en la banda i (dB)",
        "Se resta el aislamiento banda por banda al espectro de la fuente y se suma "
        "energéticamente lo que logra transmitirse.",
    )
    formula_card(
        "Términos de adaptación espectral",
        r"C=X_1-R_w,\qquad C_{tr}=X_2-R_w",
        "<b>X₁</b>: resultado con el espectro de referencia 1<br>"
        "<b>X₂</b>: resultado con el espectro de referencia 2<br>"
        "<b>Rw</b>: índice ponderado (dB)",
        "C y Ctr no son aislamientos independientes: se suman algebraicamente a Rw.",
    )
    st.markdown(
        '<div class="good"><b>Forma correcta de informar:</b> '
        'R<sub>w</sub>(C; C<sub>tr</sub>) = 52 (−2; −7) dB<br>'
        '<span>Para el espectro 1: Rw+C = 50 dB · Para tránsito: Rw+Ctr = 45 dB</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 6.1 · Punto de partida: conservar el Rw ya construido")
    st.write(
        "Para obtener **C** y **Ctr** no se construye otra curva ni se vuelve a "
        "calcular Rw. Se conserva la misma curva R(f) del procedimiento anterior "
        "y la posición final de la curva de referencia. Sobre ese resultado se "
        "aplican, uno después del otro, los dos espectros normalizados."
    )

    frequencies = demo_freq.astype(float)
    spectrum_c = np.array(
        [-29, -26, -23, -21, -19, -17, -15, -13,
         -12, -11, -10, -9, -9, -9, -9, -9],
        dtype=float,
    )
    spectrum_ctr = np.array(
        [-20, -20, -18, -16, -15, -14, -13, -12,
         -11, -9, -8, -9, -10, -11, -13, -15],
        dtype=float,
    )
    r_curve = demo_r.copy()
    best_shift = -60
    for shift in range(-60, 61):
        shifted = demo_ref_shape + shift
        deviations = np.maximum(0.0, shifted - r_curve)
        if float(np.sum(deviations)) <= 32.0 + 1e-9:
            best_shift = shift
    shifted_reference = demo_ref_shape + best_shift
    deviations = np.maximum(0.0, shifted_reference - r_curve)
    rw_value = int(round(52 + best_shift))
    x_c = -10.0 * np.log10(np.sum(10.0 ** ((spectrum_c - r_curve) / 10.0)))
    x_ctr = -10.0 * np.log10(np.sum(10.0 ** ((spectrum_ctr - r_curve) / 10.0)))
    c_value = int(round(x_c - rw_value))
    ctr_value = int(round(x_ctr - rw_value))
    total_deviation = float(np.sum(deviations))
    transmitted_c = spectrum_c - r_curve
    transmitted_ctr = spectrum_ctr - r_curve

    st.markdown(
        f'<div class="good"><b>Resultado que continúa desde el punto anterior:</b> '
        f'R<sub>w</sub> = {rw_value} dB · Σd<sub>i</sub> = {total_deviation:.1f} dB</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 6.2 · Construcción paso a paso de C")
    c_step = st.select_slider(
        "Recorre la construcción de C",
        options=[1, 2, 3, 4], value=1,
        format_func=lambda n: {
            1: "1 · Aplicar espectro 1", 2: "2 · Restar R(f)",
            3: "3 · Sumar la transmisión", 4: "4 · Obtener C",
        }[n], key="lab2_s8_c_step",
    )
    c_fig = go.Figure()
    c_fig.add_trace(go.Bar(x=frequencies, y=spectrum_c, name="Espectro 1",
                           marker_color="#56a8ff"))
    if c_step >= 2:
        c_fig.add_trace(go.Scatter(x=frequencies, y=transmitted_c,
                                   mode="lines+markers", name="Lᵢ − Rᵢ",
                                   line=dict(color="#ff9f43", width=4)))
    c_fig.update_layout(height=390, barmode="overlay", xaxis_type="log",
                        xaxis_title="Frecuencia central (Hz)",
                        yaxis_title="Nivel relativo (dB)",
                        margin=dict(l=30, r=20, t=25, b=35))
    c_fig.update_xaxes(tickvals=frequencies,
                       ticktext=[str(int(v)) if v < 1000 else f"{v/1000:g}k" for v in frequencies])
    st.plotly_chart(c_fig, use_container_width=True)
    c_explanation = {
        1: "El espectro 1 fija cuánta energía relativa aporta cada tercio de octava.",
        2: "Se resta Rᵢ en cada banda. El resultado Lᵢ−Rᵢ representa la energía relativa que logra transmitirse.",
        3: f"Las 16 contribuciones se suman energéticamente, no aritméticamente: X₁ = {x_c:.1f} dB.",
        4: f"Finalmente, C = X₁ − Rw = {x_c:.1f} − {rw_value} = {c_value:+d} dB.",
    }[c_step]
    st.info(c_explanation)
    if c_step >= 3:
        st.latex(rf"X_1=-10\log_{{10}}\left(\sum_i10^{{(L_{{1,i}}-R_i)/10}}\right)={x_c:.1f}\ \mathrm{{dB}}")
    if c_step == 4:
        st.latex(rf"C=X_1-R_w={x_c:.1f}-{rw_value}={c_value:+d}\ \mathrm{{dB}}")
        st.success(f"Para el espectro 1: Rw + C = {rw_value + c_value} dB.")

    st.markdown("#### 6.3 · Construcción paso a paso de Ctr")
    ctr_step = st.select_slider(
        "Recorre la construcción de Ctr",
        options=[1, 2, 3, 4], value=1,
        format_func=lambda n: {
            1: "1 · Aplicar espectro 2", 2: "2 · Restar R(f)",
            3: "3 · Sumar la transmisión", 4: "4 · Obtener Ctr",
        }[n], key="lab2_s8_ctr_step",
    )
    ctr_fig = go.Figure()
    ctr_fig.add_trace(go.Bar(x=frequencies, y=spectrum_ctr, name="Espectro 2",
                             marker_color="#b06cff"))
    if ctr_step >= 2:
        ctr_fig.add_trace(go.Scatter(x=frequencies, y=transmitted_ctr,
                                     mode="lines+markers", name="Lᵢ − Rᵢ",
                                     line=dict(color="#ff4d6d", width=4)))
    ctr_fig.update_layout(height=390, barmode="overlay", xaxis_type="log",
                          xaxis_title="Frecuencia central (Hz)",
                          yaxis_title="Nivel relativo (dB)",
                          margin=dict(l=30, r=20, t=25, b=35))
    ctr_fig.update_xaxes(tickvals=frequencies,
                         ticktext=[str(int(v)) if v < 1000 else f"{v/1000:g}k" for v in frequencies])
    st.plotly_chart(ctr_fig, use_container_width=True)
    ctr_explanation = {
        1: "El espectro 2 asigna mayor importancia relativa a las bajas frecuencias, características del tránsito urbano.",
        2: "Se resta la misma curva Rᵢ. Los valores L₂,ᵢ−Rᵢ muestran qué bandas graves dominan la transmisión.",
        3: f"Se realiza nuevamente una suma energética de las 16 bandas: X₂ = {x_ctr:.1f} dB.",
        4: f"Finalmente, Ctr = X₂ − Rw = {x_ctr:.1f} − {rw_value} = {ctr_value:+d} dB.",
    }[ctr_step]
    st.info(ctr_explanation)
    if ctr_step >= 3:
        st.latex(rf"X_2=-10\log_{{10}}\left(\sum_i10^{{(L_{{2,i}}-R_i)/10}}\right)={x_ctr:.1f}\ \mathrm{{dB}}")
    if ctr_step == 4:
        st.latex(rf"C_{{tr}}=X_2-R_w={x_ctr:.1f}-{rw_value}={ctr_value:+d}\ \mathrm{{dB}}")
        st.success(f"Para el espectro de tránsito: Rw + Ctr = {rw_value + ctr_value} dB.")

    st.markdown("#### 6.4 · Resultado completo")
    st.markdown(
        f'<div class="good"><b>Forma normalizada de informar:</b> '
        f'R<sub>w</sub>(C; C<sub>tr</sub>) = {rw_value} '
        f'({c_value:+d}; {ctr_value:+d}) dB<br>'
        f'<span>Rw+C = {rw_value+c_value} dB · '
        f'Rw+Ctr = {rw_value+ctr_value} dB</span></div>',
        unsafe_allow_html=True,
    )

    table = pd.DataFrame({
        "Frecuencia (Hz)": frequencies.astype(int),
        "R(f) (dB)": r_curve,
        "Espectro 1 (dB)": spectrum_c.astype(int),
        "L1-R (dB)": transmitted_c,
        "Espectro 2 (dB)": spectrum_ctr.astype(int),
        "L2-R (dB)": transmitted_ctr,
    })
    with st.expander("Ver cálculo banda por banda de C y Ctr"):
        st.dataframe(table.round(1), hide_index=True, use_container_width=True)

    st.markdown("### 7 · Cómo interpretar el resultado")
    source_type = st.radio(
        "Selecciona la fuente que quieres evaluar",
        ["Voces y actividades de vivienda", "Tránsito urbano, buses o música con bajos",
         "Fuente tonal o banda dominante"],
        horizontal=True,
        key="lab2_s8_source_type",
    )
    if source_type == "Voces y actividades de vivienda":
        st.info(
            f"Revisa principalmente **Rw+C = {rw_value+c_value} dB**, junto con la "
            "curva R(f) en las bandas donde se concentra la fuente."
        )
    elif source_type == "Tránsito urbano, buses o música con bajos":
        st.info(
            f"Revisa principalmente **Rw+Ctr = {rw_value+ctr_value} dB** y confirma "
            "el desempeño real en bajas frecuencias."
        )
    else:
        st.info(
            "Un número único puede ocultar la banda decisiva. Para una fuente tonal "
            "debe revisarse directamente **R(f)** en la frecuencia dominante."
        )
    st.warning(
        "Un Rw mayor no garantiza por sí solo la mejor solución para cualquier fuente. "
        "Dos elementos con igual Rw pueden tener Ctr y curvas graves muy diferentes."
    )

    if st.session_state.get("role") == "Docente":
        with st.expander("🔐 Lectura docente · precisión técnica y conducción"):
            st.markdown("""
            - Presente primero la curva R(f). El índice único debe aparecer como una
              consecuencia del análisis por bandas, no como sustituto de este.
            - La referencia se desplaza verticalmente sin cambiar su forma. El ajuste
              se realiza en pasos de 1 dB y se conserva la posición más alta que cumple
              la suma máxima de desviaciones desfavorables.
            - Las diferencias favorables no se restan de las desfavorables. Esta regla
              evita que un buen desempeño agudo oculte un valle importante.
            - Rw caracteriza el elemento bajo el método de ensayo correspondiente.
              No debe prometerse el mismo valor para la construcción instalada sin
              considerar sellos, encuentros, flancos y calidad de ejecución.
            - C y Ctr se calculan energéticamente con espectros normalizados. En muchos
              sistemas constructivos Ctr es más negativo porque el aislamiento suele
              ser menor en graves y el espectro de tránsito pondera más esa región.
            - La notación completa conserva los signos: 52 (−2; −7) dB. No escriba
              “C = 2” si el resultado real es −2 dB.
            """)
            st.latex(
                r"R_w(C;C_{tr})=52(-2;-7)\ \mathrm{dB}"
            )
            st.latex(
                r"R_w+C=50\ \mathrm{dB},\qquad R_w+C_{tr}=45\ \mathrm{dB}"
            )

    st.markdown("### 8 · Cinco preguntas de comprensión")
    check(
        "lab2_s8_q1",
        "¿Qué representa Rw?",
        [
            "Un índice único obtenido ajustando una curva de referencia a R(f)",
            "El promedio aritmético de todos los valores R",
            "El aislamiento exacto en todas las frecuencias",
            "El coeficiente de absorción del muro",
        ],
        "Un índice único obtenido ajustando una curva de referencia a R(f)",
        "Rw resume la curva mediante un procedimiento de referencia y desviaciones.",
    )
    check(
        "lab2_s8_q2",
        "¿Cuándo existe una desviación desfavorable?",
        [
            "Cuando la referencia ajustada queda sobre la curva R",
            "Cuando R queda sobre la referencia",
            "Siempre que la frecuencia supera 500 Hz",
            "Solo cuando Ctr es negativo",
        ],
        "Cuando la referencia ajustada queda sobre la curva R",
        "Solo el déficit de R respecto de la referencia aporta a la suma desfavorable.",
    )
    check(
        "lab2_s8_q3",
        "¿Dónde se lee Rw después de ajustar la referencia?",
        [
            "En el valor de la referencia ajustada a 500 Hz",
            "En la banda con mayor R",
            "En el promedio entre 100 y 3150 Hz",
            "En el valor de Ctr",
        ],
        "En el valor de la referencia ajustada a 500 Hz",
        "Ese valor define el índice ponderado una vez cumplido el criterio de ajuste.",
    )
    check(
        "lab2_s8_q4",
        "¿Qué combinación es especialmente pertinente frente a tránsito urbano?",
        ["Rw+Ctr", "Rw+C únicamente", "R a 3150 Hz únicamente", "El promedio de C y Ctr"],
        "Rw+Ctr",
        "Ctr adapta el resultado a un espectro con mayor contenido relativo en bajas frecuencias.",
    )
    check(
        "lab2_s8_q5",
        "¿Puede una fuente tonal evaluarse correctamente usando solo Rw?",
        [
            "No; debe revisarse también R(f) en la banda dominante",
            "Sí; Rw siempre contiene toda la información espectral",
            "Sí, pero solo si Ctr es cero",
            "No; debe usarse absorción Sabine",
        ],
        "No; debe revisarse también R(f) en la banda dominante",
        "El número único puede ocultar un valle localizado justo en la frecuencia de la fuente.",
    )

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

def _stage9_submission():
    """Recover the definitive attempt even if the browser session was closed."""
    user_key=st.session_state.get("user_key")
    if not user_key:
        return None
    rows=_remote_rows("responses",class_id=CLASS_ID,user_key=user_key)
    row=next((item for item in (rows or []) if item.get("question_key")=="final_comprehension"),None)
    if not row:
        return None
    answer=row.get("answer") or {}
    if isinstance(answer,str):
        try: answer=json.loads(answer)
        except json.JSONDecodeError: answer={}
    return {
        "answers":answer.get("answers",{}),
        "score":float(row.get("auto_score") or 0),
        "teacher_score":row.get("teacher_score"),
        "teacher_note":row.get("teacher_note") or "",
    }

def _stage9_answer_payload(row):
    """Decode the single definitive Stage 9 response saved in Supabase."""
    payload=row.get("answer") or {}
    if isinstance(payload,str):
        try:
            payload=json.loads(payload)
        except json.JSONDecodeError:
            payload={}
    return payload if isinstance(payload,dict) else {}

def teacher_stage9_results(compact=False):
    """Teacher-only automatic rubric and editable grading for Stage 9."""
    if st.session_state.get("role")!="Docente":
        return
    client=_supabase()
    if client is None:
        st.warning("Conecta Supabase para consultar las respuestas de los alumnos.")
        return
    try:
        raw=(client.table("responses").select("*,users(display_name,email)")
             .eq("class_id",CLASS_ID).eq("stage",9)
             .eq("question_key","final_comprehension")
             .order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.error(f"No fue posible consultar las respuestas de la Etapa 9: {exc}")
        return
    if not raw:
        st.info("Todavía no hay evaluaciones de la Etapa 9 enviadas por alumnos.")
        return

    def student_name(row):
        user=row.get("users") or {}
        return user.get("display_name") or row.get("user_key","Alumno")

    selected=st.selectbox(
        "Alumno evaluado",range(len(raw)),
        format_func=lambda i:f"{student_name(raw[i])} · {float(raw[i].get('auto_score') or 0):g}/40",
        key=f"stage9_teacher_student_{'compact' if compact else 'full'}",
    )
    row=raw[selected]
    payload=_stage9_answer_payload(row)
    answers=payload.get("answers",{}) if isinstance(payload,dict) else {}
    st.caption(
        f"Respuesta recibida: {str(row.get('updated_at') or '').replace('T',' ')[:19]} · "
        "guardada en Supabase, tabla responses, clave final_comprehension."
    )

    automatic=[]
    for i,item in enumerate(STAGE9_QUESTIONS):
        chosen=answers.get(str(i)) if isinstance(answers,dict) else None
        correct=item["options"][item["correct"]]
        automatic.append(4.0 if chosen==correct else 0.0)

    st.markdown("#### Rúbrica automática editable")
    st.caption("La pauta asigna 4 puntos por respuesta correcta. El docente puede ajustar cada criterio entre 0 y 4 puntos y dejar la justificación correspondiente.")
    awarded=[]
    current_total=row.get("teacher_score")
    saved_rubric=payload.get("rubric_scores",[]) if isinstance(payload,dict) else []
    for i,item in enumerate(STAGE9_QUESTIONS):
        chosen=answers.get(str(i)) if isinstance(answers,dict) else None
        correct=item["options"][item["correct"]]
        with st.expander(
            f"{i+1}. {item['title']} · {'Correcta' if chosen==correct else 'Incorrecta'} · {automatic[i]:g}/4",
            expanded=(not compact and i==0),
        ):
            st.markdown(f"**Pregunta:** {item['question']}")
            st.write(f"**Respuesta del alumno:** {chosen or 'Sin respuesta'}")
            st.success(f"**Respuesta correcta:** {correct}")
            st.info(item["explanation"])
            default=(float(saved_rubric[i]) if i<len(saved_rubric) else automatic[i])
            awarded.append(st.number_input(
                "Puntaje otorgado",0.0,4.0,float(default),0.5,
                key=f"stage9_rubric_{row['id']}_{i}_{'c' if compact else 'f'}",
            ))
    total=float(sum(awarded))
    note=st.text_area(
        "Observación general para el alumno",value=row.get("teacher_note") or "",
        key=f"stage9_note_{row['id']}_{'c' if compact else 'f'}",
    )
    c1,c2=st.columns(2)
    c1.metric("Puntaje automático",f"{sum(automatic):g}/40")
    c2.metric("Puntaje ajustado",f"{total:g}/40")
    if st.button("Guardar rúbrica docente",type="primary",use_container_width=True,
                 key=f"stage9_save_rubric_{row['id']}_{'c' if compact else 'f'}"):
        updated_payload=dict(payload)
        updated_payload["rubric_scores"]=awarded
        client.table("responses").update({
            "answer":updated_payload,
            "teacher_level":"Correcta" if total>=24 else "Incorrecta",
            "teacher_score":total,"teacher_note":note,
            "status":"reviewed","updated_at":_now(),
        }).eq("id",row["id"]).execute()
        st.success("Rúbrica y observación docente guardadas.")

    summary=[]
    for result in raw:
        result_payload=_stage9_answer_payload(result)
        result_answers=result_payload.get("answers",{}) if isinstance(result_payload,dict) else {}
        answered=sum(bool(result_answers.get(str(i))) for i in range(10))
        summary.append({
            "Alumno":student_name(result),"Respondidas":f"{answered}/10",
            "Puntaje automático":float(result.get("auto_score") or 0),
            "Puntaje docente":result.get("teacher_score"),
            "Estado":"Revisada" if result.get("teacher_score") is not None else "Corrección automática",
        })
    frame=pd.DataFrame(summary)
    with st.expander("Resumen y descarga del curso"):
        st.dataframe(frame,hide_index=True,use_container_width=True)
        st.download_button(
            "Descargar resultados CSV",frame.to_csv(index=False).encode("utf-8-sig"),
            "resultados_etapa_9.csv","text/csv",
            key=f"stage9_download_{'c' if compact else 'f'}",
        )

def teacher_stage9_answer_key():
    """Teacher view of the assessment: alternatives and key, never answer controls."""
    st.info("Vista docente: esta pantalla es una pauta de consulta. No inicia el temporizador ni permite desarrollar la evaluación.")
    for i,item in enumerate(STAGE9_QUESTIONS):
        correct=item["options"][item["correct"]]
        with st.expander(f"Pregunta {i+1} · {item['title']}",expanded=i==0):
            st.markdown(f"**{item['question']}**")
            for option_index,option in enumerate(item["options"]):
                prefix="✅" if option_index==item["correct"] else "○"
                st.write(f"{prefix} {chr(65+option_index)}. {option}")
            st.success(f"Respuesta correcta: {correct}")
            st.info(item["explanation"])

def _teacher_lab1_final_results(compact=False):
    """Resultados de la evaluación final (Etapa 10) del Laboratorio 1."""
    client=_supabase()
    if client is None:
        st.warning("Conecta Supabase para consultar las respuestas de los alumnos.")
        return
    try:
        raw=(client.table("responses").select("*,users(display_name,email)")
             .eq("class_id",CLASS_ID).eq("stage",10)
             .eq("question_key","final_exam")
             .order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.error(f"No fue posible consultar la evaluación del Laboratorio 1: {exc}")
        return
    if not raw:
        st.info("Todavía no hay evaluaciones finales enviadas en el Laboratorio 1.")
        return

    def student_name(row):
        user=row.get("users") or {}
        return user.get("display_name") or user.get("email") or row.get("user_key","Alumno")

    selected=st.selectbox(
        "Alumno evaluado",range(len(raw)),
        format_func=lambda i:f"{student_name(raw[i])} · {float(raw[i].get('auto_score') or 0):.1f}/100",
        key=f"teacher_lab1_final_student_{'compact' if compact else 'full'}",
    )
    row=raw[selected]
    payload=_stage9_answer_payload(row)
    answers=payload.get("respuestas_teoricas",{}) if isinstance(payload,dict) else {}
    theory_hits=int(payload.get("aciertos_teoricos",0) or 0) if isinstance(payload,dict) else 0
    case_score=float(payload.get("puntaje_caso",0) or 0) if isinstance(payload,dict) else 0
    auto_score=float(row.get("auto_score") or 0)
    st.caption(f"Envío: {str(row.get('updated_at') or '').replace('T',' ')[:19]} · Laboratorio 1 · Etapa 10")
    c1,c2,c3=st.columns(3)
    c1.metric("Aciertos teóricos",f"{theory_hits}/29")
    c2.metric("Caso integrador",f"{case_score:g}/20")
    c3.metric("Puntaje automático",f"{auto_score:.1f}/100")

    with st.expander("Respuestas 1 a 29",expanded=not compact):
        for i,(question,options,correct_index) in enumerate(LAB1_QUESTIONS):
            chosen_raw=answers.get(str(i),answers.get(i)) if isinstance(answers,dict) else None
            try: chosen_index=int(chosen_raw) if chosen_raw is not None else None
            except (TypeError,ValueError): chosen_index=None
            chosen=options[chosen_index] if chosen_index is not None and 0<=chosen_index<len(options) else "Sin respuesta"
            correct=options[correct_index]
            icon="✅" if chosen_index==correct_index else "❌"
            st.markdown(f"**{icon} {i+1}. {question}**")
            st.write(f"Respuesta del alumno: {chosen}")
            st.caption(f"Respuesta correcta: {correct}")

    with st.expander("Pregunta 30 · Caso profesional integrador"):
        case=payload.get("caso_integrador",{}) if isinstance(payload,dict) else {}
        if case:
            st.write(f"T₆₀ calculado: {case.get('t60','Sin respuesta')}")
            st.write(f"Diferencia de costo: {case.get('diferencia_costo','Sin respuesta')}")
            st.write(f"Incremento porcentual: {case.get('incremento_porcentual','Sin respuesta')}")
            st.write(f"Bandas críticas: {case.get('bandas_criticas',[])}")
            st.write(f"Recomendación: {case.get('recomendacion','Sin respuesta')}")
            st.write(f"Justificación: {case.get('justificacion','Sin respuesta')}")
        else:
            st.info("Este envío pertenece a una versión anterior: conserva el puntaje del caso, pero no el detalle de sus campos.")
        st.success("Pauta: T₆₀≈0,40 s; $300.000; 16,7 %; bandas 125, 250 y 500 Hz; Solución B con justificación técnica y económica.")

    st.markdown("#### Rúbrica automática editable")
    adjusted=st.number_input(
        "Puntaje final otorgado por el docente",0.0,100.0,
        float(row.get("teacher_score") if row.get("teacher_score") is not None else auto_score),0.5,
        key=f"teacher_lab1_final_score_{row['id']}_{'c' if compact else 'f'}",
    )
    note=st.text_area("Observación docente",value=row.get("teacher_note") or "",
                      key=f"teacher_lab1_final_note_{row['id']}_{'c' if compact else 'f'}")
    if st.button("Guardar revisión del Laboratorio 1",type="primary",use_container_width=True,
                 key=f"teacher_lab1_final_save_{row['id']}_{'c' if compact else 'f'}"):
        client.table("responses").update({
            "teacher_level":"Correcta" if adjusted>=60 else "Incorrecta",
            "teacher_score":adjusted,"teacher_note":note,"status":"reviewed","updated_at":_now(),
        }).eq("id",row["id"]).execute()
        st.success("Puntaje y observación docente guardados.")

def teacher_course_results(compact=False):
    """Centro docente general de evaluaciones de todos los laboratorios del Curso 1."""
    if st.session_state.get("role")!="Docente":
        return
    st.markdown("### Centro de resultados · Curso 1")
    st.caption("Consulta separadamente cada evaluación. Las respuestas y puntajes de un laboratorio no sobrescriben los de otro.")
    client=_supabase()
    if client is not None:
        try:
            all_rows=(client.table("responses").select("*,users(display_name,email)")
                      .in_("class_id",["clase-01-aislamiento-ruido-aereo","clase-02-aislamiento-ruido-aereo-minvu"]).in_("question_key",["final_exam","final_comprehension","final_integrated_design"])
                      .execute().data or [])
            consolidated={}
            for row in all_rows:
                user=row.get("users") or {}
                key=row.get("user_key") or user.get("email") or str(row.get("id"))
                item=consolidated.setdefault(key,{
                    "Alumno":user.get("display_name") or user.get("email") or key,
                    "Lab. 1 · Etapa 10":"Pendiente","Lab. 2 · Etapa 9":"Pendiente","Lab. 2 · Etapa 10":"Pendiente",
                    "Total registrado":"Pendiente",
                })
                score=row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score")
                if row.get("question_key")=="final_exam": item["Lab. 1 · Etapa 10"]=f"{float(score or 0):.1f}/100"
                if row.get("question_key")=="final_comprehension": item["Lab. 2 · Etapa 9"]=f"{float(score or 0):.1f}/40"
                if row.get("question_key")=="final_integrated_design": item["Lab. 2 · Etapa 10"]=f"{float(score or 0):.1f}/60"
            for item in consolidated.values():
                values=[]
                for field,maximum in (("Lab. 1 · Etapa 10",100),("Lab. 2 · Etapa 9",40),("Lab. 2 · Etapa 10",60)):
                    if item[field]!="Pendiente": values.append(float(item[field].split("/")[0])/maximum*100)
                item["Total registrado"]=f"{sum(values)/len(values):.1f}%" if values else "Pendiente"
            if consolidated:
                with st.expander("Resumen acumulado de todos los alumnos"):
                    summary_frame=pd.DataFrame(consolidated.values())
                    st.dataframe(summary_frame,hide_index=True,use_container_width=True)
                    st.download_button("Descargar consolidado CSV",summary_frame.to_csv(index=False).encode("utf-8-sig"),
                                       "resultados_curso_1.csv","text/csv",
                                       key=f"course_results_csv_{'compact' if compact else 'full'}")
        except Exception as exc:
            st.warning(f"No fue posible construir el resumen acumulado: {exc}")
    evaluations={
        "Laboratorio 1 · Etapa 10 · Evaluación final":("lab1",100),
        "Laboratorio 2 · Etapa 9 · Comprensión":("lab2",40),
        "Laboratorio 2 · Etapa 10 · Diseño integrador":("integrated",60),
    }
    label=st.selectbox("Laboratorio y evaluación",list(evaluations),
                       key=f"course_results_evaluation_{'compact' if compact else 'full'}")
    kind,_=evaluations[label]
    if kind=="lab1":
        _teacher_lab1_final_results(compact=compact)
    elif kind=="lab2":
        teacher_stage9_results(compact=compact)
    else:
        _teacher_lab2_integrated_results(compact=compact)

def _teacher_lab2_integrated_results(compact=False):
    client=_supabase()
    if client is None:
        st.info("Los resultados estarán disponibles al conectar la aplicación.")
        return
    try:
        rows=(client.table("responses").select("*,users(display_name,email)")
              .eq("class_id","clase-02-aislamiento-ruido-aereo-minvu")
              .eq("question_key","final_integrated_design").execute().data or [])
    except Exception as exc:
        st.warning(f"No fue posible cargar los desarrollos: {exc}"); return
    if not rows:
        st.info("Todavía no hay desarrollos enviados en la Etapa 10 del Laboratorio 2."); return
    labels=[]
    for row in rows:
        user=row.get("users") or {}; labels.append(f"{user.get('display_name') or user.get('email') or row.get('user_key')} · {str(row.get('updated_at') or '')[:16]}")
    idx=st.selectbox("Alumno",range(len(rows)),format_func=lambda i:labels[i],key=f"teacher_l2s10_student_{'c' if compact else 'f'}")
    row=rows[idx]; payload=row.get("answer") or {}
    if isinstance(payload,dict) and "value" in payload:
        try: payload=json.loads(payload["value"])
        except Exception: payload={}
    result=payload.get("calculated_result",{}) if isinstance(payload,dict) else {}
    student=payload.get("student_result",{}) if isinstance(payload,dict) else {}
    st.markdown(f"**Resultado calculado:** Rw(C; Ctr) = {result.get('rw','—')} ({result.get('c','—')}; {result.get('ctr','—')}) dB")
    st.write(f"Respuesta ingresada por el alumno: Rw={student.get('rw','—')} dB · C={student.get('c','—')} dB · Ctr={student.get('ctr','—')} dB")
    for label,key in (("Muro/tabique","wall"),("Ventana","window"),("Puerta","door")):
        data=payload.get(key,{}) if isinstance(payload,dict) else {}; st.write(f"**{label}:** {data.get('description','Sin información')} · Rw {data.get('rw','—')} dB")
    st.write(f"Puntaje de diseño: {payload.get('design_score',0):g}/40 · Comprensión: {payload.get('comprehension_score',0):g}/20")
    current=row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score") or 0
    adjusted=st.number_input("Puntaje docente",0.,60.,float(current),1.,key=f"teacher_l2s10_score_{row.get('id')}_{compact}")
    note=st.text_area("Observación docente",value=row.get("teacher_note") or "",key=f"teacher_l2s10_note_{row.get('id')}_{compact}")
    if st.button("Guardar revisión del diseño integrador",type="primary",key=f"teacher_l2s10_save_{row.get('id')}_{compact}"):
        client.table("responses").update({"teacher_score":adjusted,"teacher_note":note,"teacher_level":"Correcta" if adjusted>=36 else "Parcialmente correcta","status":"reviewed","updated_at":_now()}).eq("id",row["id"]).execute(); st.success("Revisión guardada.")

def _finish_stage9(reason="submitted"):
    answers={str(i):st.session_state.get(f"e9_q{i}") for i in range(10)}
    score=sum(
        4 for i,item in enumerate(STAGE9_QUESTIONS)
        if answers.get(str(i))==item["options"][item["correct"]]
    )
    payload={"answers":answers,"reason":reason,"finished_at":_now()}
    _save_formative(
        9,"final_comprehension","Etapa 9 · Evaluación de comprensión",
        json.dumps(payload,ensure_ascii=False),
        "Correcta" if score>=24 else "Incorrecta",
        f"Resultado automático: {score}/40 puntos.",
        score=score,max_score=40,
        correct_answer="Pauta automática de las 10 preguntas disponible después del cierre.",
    )
    st.session_state["e9_submitted"]=True
    st.session_state["e9_score"]=score
    st.session_state["e9_saved_answers"]=answers
    save_user_progress()

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

def lab2_stage9():
    _lab2_heading(
        9,"Evaluación final · Preguntas de comprensión",
        "Diez preguntas de selección única · 20 minutos · 40 puntos.",
    )
    st.info(
        "Esta evaluación tiene un solo intento. Tus respuestas se guardan automáticamente. "
        "Al enviar o agotarse el tiempo, el intento quedará cerrado y podrás revisar la pauta completa."
    )

    if st.session_state.get("role")=="Docente":
        teacher_stage9_answer_key()
        st.markdown("---")
        st.markdown("### Respuestas de alumnos y rúbrica")
        teacher_stage9_results()
        return

    remote=_stage9_submission()
    submitted=bool(remote or st.session_state.get("e9_submitted"))
    if submitted:
        saved=(remote or {}).get("answers") or st.session_state.get("e9_saved_answers",{})
        score=(remote or {}).get("score",st.session_state.get("e9_score",0))
        st.success(f"Evaluación finalizada · Puntaje: {score:g}/40")
        st.caption("El intento está cerrado. Puedes volver a esta etapa cuando quieras para revisar tus respuestas.")
        for i,item in enumerate(STAGE9_QUESTIONS):
            student_answer=saved.get(str(i)) if isinstance(saved,dict) else None
            correct=item["options"][item["correct"]]
            with st.expander(f"Pregunta {i+1} · {item['title']}",expanded=i==0):
                st.markdown(f"**{item['question']}**")
                st.write(f"Tu respuesta: {student_answer or 'Sin respuesta'}")
                if student_answer==correct:
                    st.success(f"Respuesta correcta: {correct}")
                else:
                    st.error(f"Respuesta correcta: {correct}")
                st.info(item["explanation"])
        return

    if not st.session_state.get("e9_started_at"):
        st.markdown("### Antes de comenzar")
        st.markdown(
            "- Dispondrás de **20 minutos continuos**.\n"
            "- Cada respuesta vale **4 puntos**.\n"
            "- Puedes cambiar tus respuestas mientras el tiempo esté activo.\n"
            "- Al finalizar, no podrás responder nuevamente sin un reinicio docente."
        )
        if st.button("Comenzar evaluación",type="primary",use_container_width=True,key="e9_start_button"):
            now=dt.datetime.now(dt.timezone.utc)
            st.session_state["e9_started_at"]=now.isoformat()
            st.session_state["e9_deadline"]=(now+dt.timedelta(minutes=20)).isoformat()
            save_user_progress()
            st.rerun()
        return

    deadline=st.session_state.get("e9_deadline")
    if not deadline:
        started=dt.datetime.fromisoformat(st.session_state["e9_started_at"].replace("Z","+00:00"))
        deadline=(started+dt.timedelta(minutes=20)).isoformat()
        st.session_state["e9_deadline"]=deadline
    _stage9_clock(deadline)

    for i,item in enumerate(STAGE9_QUESTIONS):
        st.markdown(
            f'<div class="question-box"><div class="question-label">PREGUNTA {i+1} DE 10 · 4 PUNTOS</div>'
            f'<div class="question-text">{item["question"]}</div></div>',
            unsafe_allow_html=True,
        )
        st.radio(
            "Selecciona una alternativa",item["options"],index=None,
            key=f"e9_q{i}",label_visibility="collapsed",
        )

    answered=sum(st.session_state.get(f"e9_q{i}") is not None for i in range(10))
    st.progress(answered/10)
    st.caption(f"{answered} de 10 respuestas registradas y guardadas.")
    if st.button("Enviar evaluación definitiva",type="primary",use_container_width=True,key="e9_submit_button"):
        if answered<10:
            st.warning(f"Aún faltan {10-answered} preguntas. Puedes enviarla, pero quedarán sin puntaje.")
            st.session_state["e9_confirm_incomplete"]=True
        else:
            _finish_stage9("submitted")
            st.rerun()
    if st.session_state.get("e9_confirm_incomplete") and answered<10:
        if st.button("Confirmar envío con respuestas pendientes",key="e9_submit_incomplete"):
            _finish_stage9("submitted_incomplete")
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
    """Pauta docente de la Etapa 10, sin controles destinados al alumno."""
    st.info(
        "Vista docente: esta pantalla muestra la pauta y los resultados correctos. "
        "No permite seleccionar sistemas, ingresar valores, contestar preguntas ni enviar el ejercicio."
    )
    st.markdown("### Pauta del cálculo integrador")
    st.latex(r"\tau_{T,f}=\frac{19{,}71\,10^{-R_{m,f}/10}+2{,}40\,10^{-R_{v,f}/10}+1{,}89\,10^{-R_{p,f}/10}}{24{,}00}")
    st.latex(r"R_{T,f}=-10\log_{10}(\tau_{T,f})")
    st.success(
        "Resultado correcto del procedimiento: combinar las curvas por transmisión y superficie "
        "en cada tercio de octava; con la curva combinada construir Rw y calcular C y Ctr. "
        "El diseño cumple cuando Rw ≥ 40 dB. El valor numérico depende de la solución seleccionada por cada alumno."
    )
    _lab2_s10_teacher_solved_examples()
    st.markdown("### Pauta · Preguntas de comprensión")
    for i,(question,options,correct) in enumerate(LAB2_S10_QUESTIONS):
        with st.expander(f"Pregunta {i+1}",expanded=i==0):
            st.markdown(f"**{question}**")
            for option_index,option in enumerate(options):
                prefix="✅" if option_index==correct else "○"
                st.write(f"{prefix} {chr(65+option_index)}. {option}")
            st.success(f"Respuesta correcta: {options[correct]}")
            st.info(LAB2_S10_EXPLANATIONS[i])

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
    """Ejemplos numéricos resueltos, visibles únicamente en la pauta docente."""
    examples=[]

    wall_a=_lab2_s10_single("Ladrillo cerámico",120)
    window_a,*_=_glass_panel_tl(6,.010,LAB2_S10_FREQS)
    door_a=_lab2_s10_door_curve(32)
    examples.append({
        "title":"Ejemplo 1 · Solución que no cumple",
        "purpose":"Permite explicar por qué un muro razonable no compensa una ventana simple y una puerta de prestación limitada.",
        "wall":"Ladrillo cerámico de 120 mm",
        "window":"Vidrio simple de 6 mm",
        "door":"P3 · Madera maciza de 45 mm, con sellos",
        "curves":[wall_a,np.asarray(window_a,dtype=float),door_a],
    })

    wall_b=_lab2_s10_double(
        "Yeso-cartón alta densidad",15,2,
        "Yeso-cartón alta densidad",15,2,
        100,"Lana mineral 40 kg/m³",
    )
    window_b,*_=_double_window_model(6,10,.020,1.2,2.0,.10,.010,.010,LAB2_S10_FREQS)
    door_b=_lab2_s10_door_curve(48)
    examples.append({
        "title":"Ejemplo 2 · Solución que cumple",
        "purpose":"Ejemplo de pauta con tabique desacoplado, vidrios asimétricos y una puerta reforzada.",
        "wall":"2× yeso-cartón alta densidad 15 mm / cámara 100 mm con lana mineral 40 kg/m³ / 2× yeso-cartón alta densidad 15 mm",
        "window":"Ventana doble 6/20/10 mm",
        "door":"P6 · Puerta acústica reforzada",
        "curves":[wall_b,np.asarray(window_b,dtype=float),door_b],
    })

    st.markdown("### Ejemplos resueltos del cálculo integrador")
    st.caption(
        "Estas son pautas de referencia, no las únicas soluciones posibles. Todos los valores "
        "se obtienen con las mismas funciones de cálculo utilizadas por el alumno."
    )
    for example_index,example in enumerate(examples):
        wall_curve,window_curve,door_curve=example["curves"]
        combined=-10*np.log10((
            19.71*10**(-wall_curve/10)
            +2.40*10**(-window_curve/10)
            +1.89*10**(-door_curve/10)
        )/24.0)
        wr,wc,wctr=_lab2_s10_indices(wall_curve)
        vr,vc,vctr=_lab2_s10_indices(window_curve)
        dr,dc,dctr=_lab2_s10_indices(door_curve)
        rw,c,ctr=_lab2_s10_indices(combined)
        weakest=min([(wr,"muro/tabique"),(vr,"ventana"),(dr,"puerta")])[1]
        with st.expander(example["title"],expanded=example_index==0):
            st.write(example["purpose"])
            st.markdown(
                f"**Muro/tabique:** {example['wall']}  \n"
                f"**Ventana:** {example['window']}  \n"
                f"**Puerta:** {example['door']}"
            )
            summary=pd.DataFrame([
                ["Muro/tabique",19.71,example["wall"],f"{wr} ({wc:+d}; {wctr:+d})"],
                ["Ventana",2.40,example["window"],f"{vr} ({vc:+d}; {vctr:+d})"],
                ["Puerta",1.89,example["door"],f"{dr} ({dc:+d}; {dctr:+d})"],
            ],columns=["Elemento","Superficie (m²)","Solución","Rw (C; Ctr) dB"])
            st.dataframe(summary,hide_index=True,use_container_width=True)
            a,b,c1,c2=st.columns(4)
            a.metric("Rw combinado",f"{rw} dB")
            b.metric("C",f"{c:+d} dB")
            c1.metric("Ctr",f"{ctr:+d} dB")
            c2.metric("Rw + C",f"{rw+c} dB")
            (st.success if rw>=40 else st.error)(
                f"{'Cumple' if rw>=40 else 'No cumple'}: Rw = {rw} dB "
                f"{'≥' if rw>=40 else '<'} 40 dB. Elemento de menor Rw: {weakest}."
            )
            _lab2_s10_plot(
                f"{example['title']} · curvas por tercios de octava",
                [("Muro/tabique",wall_curve),("Ventana",window_curve),
                 ("Puerta",door_curve),("Paramento combinado",combined)],
            )
            st.markdown("**Desarrollo espectral correcto**")
            st.dataframe(pd.DataFrame({
                "Frecuencia (Hz)":LAB2_S10_FREQS.astype(int),
                "Muro/tabique Rm (dB)":np.round(wall_curve,1),
                "Ventana Rv (dB)":np.round(window_curve,1),
                "Puerta Rp (dB)":np.round(door_curve,1),
                "R combinado (dB)":np.round(combined,1),
            }),hide_index=True,use_container_width=True)
            st.info(
                f"Resultado de pauta: Rw(C; Ctr) = {rw} ({c:+d}; {ctr:+d}) dB; "
                f"Rw+C = {rw+c} dB y Rw+Ctr = {rw+ctr} dB."
            )

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

def lab2_stage10():
    _lab2_heading(10,"Diseño integrador · paramento sala–pasillo","Diseña muro, ventana y puerta; calcula Rw, C y Ctr; y verifica el requisito Rw ≥ 40 dB.")
    st.info("Duración: 40 minutos · 60 puntos. Las curvas se calculan con las mismas herramientas físicas utilizadas en las etapas anteriores.")
    st.markdown("### Encargo profesional")
    st.markdown("Una sala de clases de **8,00 × 6,00 × 3,00 m** recibe ruido desde el pasillo. El paramento separador mide **8,00 × 3,00 m** y debe alcanzar **Rw ≥ 40 dB**. Debes diseñar y seleccionar sus tres componentes.")
    geo=pd.DataFrame([["Muro o tabique",19.71,"82,13 %"],["Ventana 2,00 × 1,20 m",2.40,"10,00 %"],["Puerta 0,90 × 2,10 m",1.89,"7,87 %"],["Total",24.00,"100 %"]],columns=["Elemento","Superficie (m²)","Proporción"])
    st.dataframe(geo,hide_index=True,use_container_width=True)
    if st.session_state.get("role")=="Docente":
        teacher_lab2_stage10_answer_key()
        st.markdown("---")
        st.markdown("### Resultados enviados por los alumnos")
        _teacher_lab2_integrated_results()
        return

    st.markdown("## 1 · Diseña el muro o tabique")
    wall_type=st.radio("Sistema opaco",["Muro o placa simple","Tabique de placa doble"],horizontal=True,key="l2s10_wall_type")
    if wall_type=="Muro o placa simple":
        c1,c2=st.columns(2); mat=c1.selectbox("Material",list(LAB2_S10_MATERIALS),key="l2s10_sm"); th=c2.selectbox("Espesor (mm)",LAB2_S10_MATERIALS[mat]["th"],key="l2s10_st")
        wall_curve=_lab2_s10_single(mat,th); wall_desc=f"{mat} · {th:g} mm"
    else:
        a,b=st.columns(2)
        with a:
            m1=st.selectbox("Material hoja 1",list(LAB2_S10_LEAVES),key="l2s10_m1"); t1=st.selectbox("Espesor hoja 1 (mm)",LAB2_S10_LEAVES[m1]["th"],key="l2s10_t1"); n1=st.selectbox("Placas hoja 1",[1,2],key="l2s10_n1")
        with b:
            m2=st.selectbox("Material hoja 2",list(LAB2_S10_LEAVES),key="l2s10_m2"); t2=st.selectbox("Espesor hoja 2 (mm)",LAB2_S10_LEAVES[m2]["th"],key="l2s10_t2"); n2=st.selectbox("Placas hoja 2",[1,2],key="l2s10_n2")
        c,d=st.columns(2); gap=c.selectbox("Cámara (mm)",[40,60,80,100,120,150],key="l2s10_gap"); absorb=d.selectbox("Absorbente",["Sin absorbente","Lana de vidrio 15 kg/m³","Lana de vidrio 32 kg/m³","Lana mineral 40 kg/m³","Lana mineral 60 kg/m³"],key="l2s10_abs")
        wall_curve=_lab2_s10_double(m1,t1,n1,m2,t2,n2,gap,absorb); wall_desc=f"{n1}×{m1} {t1:g} / {gap} mm / {n2}×{m2} {t2:g} · {absorb}"
    wr,wc,wt=_lab2_s10_indices(wall_curve); st.success(f"Resultado diseñado: Rw(C; Ctr) = {wr} ({wc:+d}; {wt:+d}) dB")
    _lab2_s10_plot("Curva del elemento opaco",[("Muro/tabique",wall_curve)])
    if st.button("Incorporar muro al paramento",type="primary",key="l2s10_pick_wall"):
        st.session_state["l2s10_wall"]={"description":wall_desc,"curve":wall_curve.tolist(),"rw":wr,"c":wc,"ctr":wt}; save_user_progress(); st.success("Muro incorporado y guardado.")

    st.markdown("## 2 · Diseña la ventana")
    window_type=st.radio("Tipo de ventana",["Vidrio simple","Ventana doble"],horizontal=True,key="l2s10_window_type")
    if window_type=="Vidrio simple":
        g=st.selectbox("Espesor del vidrio (mm)",[4,5,6,8,10,12],key="l2s10_g"); window_curve,_m,_b,_fc=_glass_panel_tl(g,.010,LAB2_S10_FREQS); window_desc=f"Vidrio simple {g} mm"
    else:
        x,y,z=st.columns(3); g1=x.selectbox("Vidrio 1 (mm)",[4,5,6,8,10,12],key="l2s10_g1"); wg=y.selectbox("Cámara (mm)",[6,10,12,16,20,30,50,80],key="l2s10_wgap"); g2=z.selectbox("Vidrio 2 (mm)",[4,5,6,8,10,12],index=2,key="l2s10_g2")
        window_curve,*_=_double_window_model(g1,g2,wg/1000,1.2,2.0,.10,.010,.010,LAB2_S10_FREQS); window_desc=f"Ventana doble {g1}/{wg}/{g2} mm"
    vr,vc,vt=_lab2_s10_indices(window_curve); st.success(f"Resultado diseñado: Rw(C; Ctr) = {vr} ({vc:+d}; {vt:+d}) dB")
    _lab2_s10_plot("Curva de la ventana",[("Ventana",window_curve)])
    if st.button("Incorporar ventana al paramento",type="primary",key="l2s10_pick_window"):
        st.session_state["l2s10_window"]={"description":window_desc,"curve":np.asarray(window_curve).tolist(),"rw":vr,"c":vc,"ctr":vt}; save_user_progress(); st.success("Ventana incorporada y guardada.")

    st.markdown("## 3 · Selecciona la puerta")
    door=st.selectbox("Solución de puerta",list(LAB2_S10_DOORS),key="l2s10_door_type"); door_curve=_lab2_s10_door_curve(LAB2_S10_DOORS[door]); dr,dc,dtc=_lab2_s10_indices(door_curve)
    st.caption("La curva incluye de forma referencial el efecto de la hoja, sellos y encuentros; no se calcula solo por ley de masa.")
    st.success(f"Resultado referencial: Rw(C; Ctr) = {dr} ({dc:+d}; {dtc:+d}) dB")
    if st.button("Incorporar puerta al paramento",type="primary",key="l2s10_pick_door"):
        st.session_state["l2s10_door"]={"description":door,"curve":door_curve.tolist(),"rw":dr,"c":dc,"ctr":dtc}; save_user_progress(); st.success("Puerta incorporada y guardada.")

    st.markdown("## 4 · Paramento sala de clases–pasillo")
    wall=st.session_state.get("l2s10_wall"); window=st.session_state.get("l2s10_window"); door_saved=st.session_state.get("l2s10_door")
    if not all([wall,window,door_saved]):
        st.warning("Incorpora primero el muro, la ventana y la puerta. Cada botón conserva la curva completa para el cálculo compuesto."); return
    st.markdown(f"""<div style='border-radius:20px;padding:1.2rem;background:linear-gradient(135deg,#eaf5ff,#f8fbff);border:2px solid #88bce8'><b>PASILLO → SALA DE CLASES</b><br><br>🧱 <b>Muro · 19,71 m²:</b> {wall['description']} · Rw {wall['rw']} dB<br>🪟 <b>Ventana · 2,40 m²:</b> {window['description']} · Rw {window['rw']} dB<br>🚪 <b>Puerta · 1,89 m²:</b> {door_saved['description']} · Rw {door_saved['rw']} dB</div>""",unsafe_allow_html=True)
    combined=-10*np.log10((19.71*10**(-np.array(wall["curve"])/10)+2.40*10**(-np.array(window["curve"])/10)+1.89*10**(-np.array(door_saved["curve"])/10))/24.0)
    cr,cc,cct=_lab2_s10_indices(combined); _lab2_s10_plot("Aislamiento por tercios de octava",[("Muro",wall["curve"]),("Ventana",window["curve"]),("Puerta",door_saved["curve"]),("Paramento combinado",combined)])
    with st.expander("Ver tabla espectral del cálculo compuesto"):
        st.dataframe(pd.DataFrame({"Frecuencia (Hz)":LAB2_S10_FREQS.astype(int),"Muro (dB)":np.round(wall["curve"],1),"Ventana (dB)":np.round(window["curve"],1),"Puerta (dB)":np.round(door_saved["curve"],1),"Combinado (dB)":np.round(combined,1)}),hide_index=True,use_container_width=True)
    st.markdown("## 5 · Calcula, ingresa e interpreta tu resultado")
    st.markdown("#### Ecuación del aislamiento compuesto")
    st.latex(r"\tau_{T,f}=\frac{S_m10^{-R_{m,f}/10}+S_v10^{-R_{v,f}/10}+S_p10^{-R_{p,f}/10}}{S_m+S_v+S_p}")
    st.latex(r"R_{T,f}=-10\log_{10}(\tau_{T,f})")
    st.caption("Para este ejercicio: Sm = 19,71 m²; Sv = 2,40 m²; Sp = 1,89 m²; ST = 24,00 m². La combinación se realiza en cada banda, no promediando decibeles ni valores Rw.")
    _lab2_s10_index_workbench(combined)
    st.markdown("### Ingresa tus resultados")
    submitted=bool(st.session_state.get("l2s10_submitted"))
    q1,q2,q3=st.columns(3); ans_rw=q1.number_input("Rw combinado (dB)",0,100,0,key="l2s10_ans_rw",disabled=submitted); ans_c=q2.number_input("C (dB)",-30,10,0,key="l2s10_ans_c",disabled=submitted); ans_ctr=q3.number_input("Ctr (dB)",-30,10,0,key="l2s10_ans_ctr",disabled=submitted)
    st.caption("Puedes corregir y verificar nuevamente cuantas veces necesites. El intento se bloquea únicamente al enviar el desarrollo definitivo.")
    current_signature=(int(ans_rw),int(ans_c),int(ans_ctr))
    if st.button("Verificar resultado",key="l2s10_verify",disabled=submitted):
        st.session_state["l2s10_verified_signature"]=current_signature; st.session_state["l2s10_verified"]=True; save_user_progress()
    verified_signature=tuple(st.session_state.get("l2s10_verified_signature",()))
    verified=verified_signature==current_signature and bool(st.session_state.get("l2s10_verified"))
    if st.session_state.get("l2s10_verified") and not verified:
        st.warning("Modificaste uno o más resultados después de verificar. Presiona nuevamente “Verificar resultado”.")
    if verified:
        numeric=sum([abs(ans_rw-cr)<=1,abs(ans_c-cc)<=1,abs(ans_ctr-cct)<=1]); design_score=20+numeric*(20/3)
        st.success(f"Resultado calculado: Rw(C; Ctr) = {cr} ({cc:+d}; {cct:+d}) dB · Rw+C = {cr+cc} dB")
        (st.success if cr>=40 else st.error)(f"{'Cumple' if cr>=40 else 'No cumple'} el requisito Rw ≥ 40 dB.")
        weakest=min([(wall['rw'],'muro'),(window['rw'],'ventana'),(door_saved['rw'],'puerta')])[1]; st.info(f"Elemento débil de la selección: **{weakest}**. La influencia final depende simultáneamente de su transmisión y superficie.")
    else: design_score=0

    st.markdown("## 6 · Preguntas de comprensión")
    correct_count=0
    answers={}
    for i,(question,options,correct) in enumerate(LAB2_S10_QUESTIONS):
        value=st.radio(f"{i+1}. {question}",options,index=None,key=f"l2s10_q{i}"); answers[str(i)]=value
        if value==options[correct]: correct_count+=1
    comprehension_score=correct_count*4; total=round(design_score+comprehension_score,1)
    st.metric("Puntaje acumulado",f"{total:g}/60")
    if st.button("Enviar desarrollo definitivo",type="primary",use_container_width=True,key="l2s10_submit",disabled=submitted):
        if not verified or any(v is None for v in answers.values()): st.warning("Verifica los resultados actualmente ingresados y responde las cinco preguntas antes de enviar.")
        else:
            payload={"geometry":{"room":"8.00×6.00×3.00 m","wall":19.71,"window":2.40,"door":1.89,"total":24.00},"wall":wall,"window":window,"door":door_saved,"combined_curve":combined.tolist(),"student_result":{"rw":ans_rw,"c":ans_c,"ctr":ans_ctr},"calculated_result":{"rw":cr,"c":cc,"ctr":cct},"answers":answers,"design_score":design_score,"comprehension_score":comprehension_score}
            _save_formative(10,"final_integrated_design","Diseño integrador del paramento sala–pasillo",json.dumps(payload,ensure_ascii=False),"Correcta" if total>=36 else "Parcialmente correcta",f"Resultado automático: {total:g}/60 puntos.",score=total,max_score=60,correct_answer=f"Resultado dependiente del diseño; cálculo verificado banda por banda. Selección enviada: Rw(C;Ctr)={cr}({cc:+d};{cct:+d}) dB.")
            st.session_state["l2s10_submitted"]=True; save_user_progress(); st.success(f"Desarrollo enviado y guardado · {total:g}/60 puntos.")

def lab2_stage3():
    """Ejercicio comparativo de tres placas simples homogéneas."""
    _lab2_heading(
        3,
        "Ejercicio aplicado: comparación de tres placas simples",
        "Predecir el TL de campo de yeso-cartón, madera y hormigón, y justificar una decisión de diseño.",
    )
    st.markdown("""
    ### Encargo profesional

    Debes seleccionar una **placa homogénea simple** para separar un recinto ruidoso
    de una sala de trabajo. Estudiarás tres alternativas —yeso-cartón, madera y
    hormigón— entre **50 y 5.000 Hz**.

    El propósito no es limitarse a decir que el hormigón aísla más. Debes explicar
    cómo la densidad, el espesor, la rigidez y el amortiguamiento modifican la masa
    superficial, la frecuencia crítica y la curva completa de aislamiento.
    """)
    st.success("""
    **En palabras simples:** probaremos tres “paredes de una sola pieza”. La aplicación
    enviará sonido contra cada una desde muchas direcciones y calculará cuánto logra
    atravesarla. Una curva más alta significa que pasa menos sonido.
    """)
    _lab2_image(
        "panel_simple",
        "Modelo utilizado: una placa homogénea simple, sin cámara, montantes ni una segunda hoja.",
    )
    st.info(
        "**Método común para las tres alternativas:** primero se calcula "
        "τ(θ,f), después se integran energéticamente todas las incidencias entre "
        "0° y 78° y, finalmente, el resultado se transforma en TL de campo."
    )

    st.markdown("### Las tres placas que se compararán")
    image_col_1,image_col_2,image_col_3=st.columns(3)
    with image_col_1:
        st.markdown("#### Yeso-cartón")
        _lab2_image(
            "yeso_carton",
            "Una placa simple de yeso-cartón, sin perfiles, cámara ni segunda hoja.",
        )
        st.markdown(
            "**En palabras simples:** es una hoja liviana. Se mueve con mayor "
            "facilidad cuando recibe sonido y, por eso, normalmente deja pasar más "
            "energía que una placa pesada."
        )
    with image_col_2:
        st.markdown("#### Madera")
        _lab2_image(
            "madera",
            "Un panel simple y macizo de madera, sin entramado ni revestimientos.",
        )
        st.markdown(
            "**En palabras simples:** combina un peso moderado con una rigidez "
            "mayor que la del yeso-cartón. Su respuesta cambia con la frecuencia "
            "y con la facilidad con que el panel puede flexionarse."
        )
    with image_col_3:
        st.markdown("#### Hormigón")
        _lab2_image(
            "hormigon",
            "Un muro simple y macizo de hormigón, sin cámaras ni capas adicionales.",
        )
        st.markdown(
            "**En palabras simples:** concentra mucha masa en cada metro cuadrado. "
            "Cuesta más hacerlo vibrar, por lo que generalmente transmite menos "
            "sonido que las alternativas livianas."
        )
    st.caption(
        "Las imágenes representan una sola hoja homogénea de cada material. "
        "No corresponden a tabiques dobles ni a sistemas con cámara de aire."
    )

    st.markdown("### 1 · Modelo físico utilizado")
    st.markdown("#### Masa superficial")
    st.latex(r"m'=\rho h")
    st.caption("Masa por unidad de superficie de la placa, expresada en kg/m².")
    st.info(
        "**Explicación para no ingenieros:** indica cuánto pesa un metro cuadrado "
        "de la placa. No importa cuánto pesa el muro completo, sino cuánto material "
        "hay en cada m². En general, una placa con mayor masa superficial es más "
        "difícil de mover y puede aislar mejor."
    )

    st.markdown("#### Rigidez a flexión")
    st.latex(r"B=\frac{E h^3}{12}")
    st.caption("Rigidez a flexión por unidad de ancho, expresada en N·m.")
    st.info(
        "**Explicación para no ingenieros:** representa qué tan difícil es doblar "
        "la placa. Una lámina flexible vibra con facilidad; una muy rígida se opone "
        "a curvarse. El espesor influye mucho porque aparece elevado al cubo."
    )

    st.markdown("#### Frecuencia crítica")
    st.latex(r"f_c=\frac{c^2}{2\pi}\sqrt{\frac{m'}{B}}")
    st.caption("Frecuencia a partir de la cual puede producirse el fenómeno de coincidencia.")
    st.info(
        "**Explicación para no ingenieros:** es una frecuencia especialmente "
        "desfavorable. Cerca de ella, el sonido del aire logra hacer vibrar la placa "
        "de manera muy eficiente y el aislamiento puede presentar una caída, aunque "
        "la placa sea pesada."
    )

    st.markdown("#### Coeficiente de transmisión para cada frecuencia y ángulo")
    st.write(
        "Para evitar una expresión excesivamente larga, se definen primero dos "
        "términos auxiliares. Esta forma es algebraicamente equivalente a la "
        "ecuación completa utilizada en el cálculo."
    )
    st.latex(
        r"A(\theta,f)=\frac{\omega m'\cos\theta}{2\rho_0c}"
    )
    st.latex(
        r"C(\theta,f)=\frac{\omega^2 B\sin^4\theta}{c^4m'}"
    )
    st.latex(
        r"\tau(\theta,f)="
        r"\frac{1}{\left[1+\eta A(\theta,f)C(\theta,f)\right]^2"
        r"+\left[A(\theta,f)\left(1-C(\theta,f)\right)\right]^2}"
    )
    st.info(
        "**Explicación para no ingenieros:** τ es la fracción de energía sonora que "
        "consigue atravesar la placa. Si τ es grande, pasa más sonido; si τ es "
        "pequeño, la placa aísla mejor. Se calcula para distintas frecuencias y "
        "ángulos porque el sonido no siempre llega de frente."
    )
    st.markdown("#### Coeficiente de transmisión de campo")
    st.latex(
        r"\overline{\tau}_{campo}(f)=2{,}0904"
        r"\int_0^{78^\circ}\tau(\theta,f)\cos\theta\sin\theta\,d\theta"
    )
    st.info(
        "**Explicación para no ingenieros:** en un recinto real el sonido llega "
        "desde muchas direcciones. Esta integración reúne todas esas incidencias "
        "entre 0° y 78° en un único valor energético representativo del campo sonoro."
    )
    st.markdown("#### Pérdida por transmisión de campo")
    st.latex(
        r"TL_{campo}(f)=10\log_{10}\left(\frac{1}"
        r"{\overline{\tau}_{campo}(f)}\right)"
        r"=-10\log_{10}\left[\overline{\tau}_{campo}(f)\right]"
    )
    st.info(
        "**Explicación para no ingenieros:** TL expresa el aislamiento en decibeles. "
        "Un TL mayor significa que atraviesa menos energía sonora. Por ejemplo, una "
        "subida de la curva indica una mejora; un valle señala una frecuencia donde "
        "la placa está aislando menos."
    )
    st.caption(
        "ω = 2πf; ρ₀ = 1,18 kg/m³; c = 343 m/s. "
        "78° es el límite superior de integración, no un único rayo."
    )
    st.markdown("#### Variables y unidades")
    st.dataframe(
        pd.DataFrame([
            ["ρ", "Densidad del material", "kg/m³"],
            ["h", "Espesor de la placa", "m"],
            ["m′", "Masa superficial", "kg/m²"],
            ["E", "Módulo de Young", "Pa"],
            ["B", "Rigidez a flexión", "N·m"],
            ["η", "Factor de pérdidas", "Adimensional"],
            ["f", "Frecuencia", "Hz"],
            ["ω = 2πf", "Frecuencia angular", "rad/s"],
            ["θ", "Ángulo respecto de la normal", "grados o radianes"],
        ], columns=["Símbolo", "Significado", "Unidad"]),
        use_container_width=True,
        hide_index=True,
    )

    presets={
        "Yeso-cartón":{
            "rho":800.0,"h":12.5,"e":2.5,"eta":0.030,
            "color":"#1677d2",
            "note":"Placa liviana de referencia.",
        },
        "Madera":{
            "rho":600.0,"h":18.0,"e":10.0,"eta":0.020,
            "color":"#d58b16",
            "note":"Modelo isotrópico simplificado; la madera real depende de la dirección de las fibras.",
        },
        "Hormigón":{
            "rho":2400.0,"h":100.0,"e":30.0,"eta":0.010,
            "color":"#d64545",
            "note":"Elemento pesado homogéneo de referencia.",
        },
    }
    frequencies=np.arange(50.0,5000.0+1,10.0)
    sample_frequencies=np.array([125.,250.,500.,1000.,2000.,4000.])
    material_results={}

    st.markdown("### 2 · Analiza cada material")
    st.markdown("""
    Recorre las tres pestañas. Puedes modificar los valores de referencia. Para
    comparar correctamente, la aplicación aplicará el mismo intervalo de frecuencia,
    campo angular y ecuaciones a todas las alternativas.
    """)
    st.markdown("""
    **Guía rápida de los controles**

    - **Densidad:** qué tan concentrada está la materia; no es el peso total.
    - **Espesor:** distancia entre las dos caras de esta única placa.
    - **Módulo de Young:** resistencia del material a deformarse.
    - **Factor de pérdidas:** capacidad del material para amortiguar su vibración.
    """)
    tabs=st.tabs(list(presets.keys()))
    for tab,(material,preset) in zip(tabs,presets.items()):
        slug={"Yeso-cartón":"yeso","Madera":"madera","Hormigón":"hormigon"}[material]
        with tab:
            st.markdown(f"#### Caso · {material}")
            st.caption(preset["note"])
            _lab2_image(
                {"Yeso-cartón":"yeso_carton","Madera":"madera",
                 "Hormigón":"hormigon"}[material],
                {
                    "Yeso-cartón":(
                        "Placa simple homogénea de yeso-cartón: una sola hoja, sin "
                        "montantes, cámara ni segunda placa."
                    ),
                    "Madera":(
                        "Panel simple homogéneo de madera: una sola hoja maciza, sin "
                        "entramado, cámara ni revestimientos adicionales."
                    ),
                    "Hormigón":(
                        "Muro simple homogéneo de hormigón: una sola hoja maciza."
                    ),
                }[material],
            )
            st.info(
                "La imagen y el cálculo representan el mismo modelo idealizado: "
                "**una única placa simple, homogénea e infinita**. No se incorporan "
                "montantes, uniones, cavidades, segundas hojas ni transmisiones laterales."
            )
            st.markdown({
                "Yeso-cartón":(
                    "**Cómo interpretar este caso:** al ser una placa liviana y "
                    "delgada, tendrá una masa superficial baja. Observa dónde aparece "
                    "su frecuencia crítica y si la curva presenta allí una pérdida "
                    "de aislamiento."
                ),
                "Madera":(
                    "**Cómo interpretar este caso:** el mayor espesor aumenta tanto "
                    "la masa como, con mucha más fuerza, la rigidez. Comprueba si eso "
                    "hace que su curva y su frecuencia crítica sean distintas de las "
                    "del yeso-cartón."
                ),
                "Hormigón":(
                    "**Cómo interpretar este caso:** su elevada densidad y espesor "
                    "producen una masa superficial muy grande. Compara cuánto aumenta "
                    "el TL y recuerda que aquí se modela solo el material, no sus "
                    "encuentros ni posibles fugas en obra."
                ),
            }[material])
            c1,c2,c3=st.columns(3)
            rho=c1.number_input(
                "Densidad ρ (kg/m³)",300.0,3000.0,preset["rho"],10.0,
                key=f"lab2_s3_{slug}_rho")
            h_mm=c2.number_input(
                "Espesor h (mm)",4.0,300.0,preset["h"],0.5,
                key=f"lab2_s3_{slug}_h")
            young_gpa=c3.number_input(
                "Módulo de Young E (GPa)",0.1,100.0,preset["e"],0.1,
                key=f"lab2_s3_{slug}_e")
            eta=st.number_input(
                "Factor de pérdidas η",0.001,0.200,preset["eta"],0.001,
                format="%.3f",key=f"lab2_s3_{slug}_eta")

            h=h_mm/1000
            surface_mass=rho*h
            stiffness=young_gpa*1e9*h**3/12
            critical_frequency=343.0**2/(2*math.pi)*math.sqrt(surface_mass/stiffness)
            tau_field,tl_field,_,_,_=_panel_simple_field_tl(
                frequencies,surface_mass,stiffness,eta)
            sample_tau,sample_tl,_,_,_=_panel_simple_field_tl(
                sample_frequencies,surface_mass,stiffness,eta)
            material_results[material]={
                "m":surface_mass,"B":stiffness,"fc":critical_frequency,
                "tau":tau_field,"tl":tl_field,"sample_tau":sample_tau,
                "sample_tl":sample_tl,"color":preset["color"],
            }

            m1,m2,m3=st.columns(3)
            m1.metric("Masa superficial m′",f"{surface_mass:.2f} kg/m²")
            m2.metric("Rigidez B",f"{stiffness:,.1f} N·m")
            m3.metric("Frecuencia crítica fᶜ",f"{critical_frequency:,.0f} Hz")
            st.caption(
                "Estos resultados indican cuánto pesa la placa por metro cuadrado, "
                "cuánto se resiste a curvarse y dónde puede aparecer la coincidencia."
            )
            if 50 <= critical_frequency <= 5000:
                st.warning(
                    f"fᶜ = {critical_frequency:,.0f} Hz está dentro del intervalo. "
                    "Busca su efecto en la curva."
                )
            else:
                st.success(
                    f"fᶜ = {critical_frequency:,.0f} Hz queda fuera del intervalo mostrado."
                )

            fig_material=go.Figure()
            fig_material.add_trace(go.Scatter(
                x=frequencies,y=tl_field,mode="lines",name=material,
                line=dict(color=preset["color"],width=4)))
            if 50 <= critical_frequency <= 5000:
                fig_material.add_vline(
                    x=critical_frequency,line_dash="dash",
                    line_color=preset["color"],annotation_text="fᶜ",
                    annotation_position="top")
            fig_material.update_layout(
                title=f"TL de campo · {material}",
                xaxis_title="Frecuencia (Hz) · escala lineal",
                yaxis_title="TL de campo (dB)",
                xaxis=dict(type="linear",range=[50,5000],dtick=500),
                height=420,hovermode="x unified",
                margin=dict(l=40,r=20,t=60,b=45),
                showlegend=False)
            st.plotly_chart(
                fig_material,use_container_width=True,
                key=f"lab2_s3_{slug}_curve")
            st.info(
                "**Cómo leer la curva:** de izquierda a derecha se pasa de sonidos "
                "graves a agudos; cuanto más alta está la línea, mayor es el "
                "aislamiento. Observa qué ocurre cerca de la línea vertical fᶜ."
            )
            st.dataframe(
                pd.DataFrame({
                    "Frecuencia (Hz)":sample_frequencies.astype(int),
                    "τ̄ campo":sample_tau,
                    "Energía transmitida (%)":100*sample_tau,
                    "TL campo (dB)":sample_tl,
                }).style.format({
                    "τ̄ campo":"{:.6f}",
                    "Energía transmitida (%)":"{:.4f}",
                    "TL campo (dB)":"{:.1f}",
                }),
                use_container_width=True,hide_index=True)
            st.caption(
                "La tabla presenta el mismo fenómeno de dos formas: menor energía "
                "transmitida equivale a un TL mayor."
            )

    st.markdown("### 3 · Comparación conjunta")
    st.markdown(
        "Aquí se superponen las tres alternativas. En cada frecuencia, la curva que "
        "queda más arriba entrega el mayor aislamiento según este modelo."
    )
    visible=st.multiselect(
        "Curvas visibles",
        list(presets.keys()),
        default=list(presets.keys()),
        key="lab2_s3_visible_materials",
    )
    comparison=go.Figure()
    for material in visible:
        result=material_results[material]
        comparison.add_trace(go.Scatter(
            x=frequencies,y=result["tl"],mode="lines",name=material,
            line=dict(color=result["color"],width=3)))
        if 50 <= result["fc"] <= 5000:
            comparison.add_vline(
                x=result["fc"],line_dash="dot",line_color=result["color"],
                annotation_text=f"fᶜ {material}",annotation_position="top")
    comparison.update_layout(
        title="Comparación de TL de campo · mismas ecuaciones y campo hasta 78°",
        xaxis_title="Frecuencia (Hz) · escala lineal",
        yaxis_title="TL de campo (dB)",
        xaxis=dict(type="linear",range=[50,5000],dtick=500),
        height=500,hovermode="x unified",
        margin=dict(l=40,r=20,t=75,b=45),
        legend=dict(orientation="h",y=1.16))
    st.plotly_chart(
        comparison,use_container_width=True,key="lab2_s3_comparison")
    st.info(
        "**No compares solo el espesor.** También importan la densidad, la masa "
        "superficial y la rigidez. Por eso el orden de las curvas puede cambiar "
        "según la frecuencia."
    )

    comparison_rows=[]
    for material,result in material_results.items():
        row={
            "Material":material,
            "m′ (kg/m²)":result["m"],
            "B (N·m)":result["B"],
            "fᶜ (Hz)":result["fc"],
        }
        for i,freq in enumerate(sample_frequencies):
            row[f"TL {int(freq)} Hz"]=result["sample_tl"][i]
        comparison_rows.append(row)
    st.dataframe(
        pd.DataFrame(comparison_rows).style.format({
            "m′ (kg/m²)":"{:.2f}","B (N·m)":"{:,.1f}","fᶜ (Hz)":"{:,.0f}",
            **{f"TL {int(f)} Hz":"{:.1f}" for f in sample_frequencies},
        }),
        use_container_width=True,hide_index=True)
    st.caption(
        "Para justificar tu decisión, compara una misma columna de frecuencia entre "
        "los tres materiales y cita sus valores."
    )
    st.caption(
        "Predicción teórica de placas infinitas y homogéneas. No equivale a un ensayo "
        "normalizado y no incorpora juntas, apoyos, dimensiones finitas, fugas ni flancos."
    )

    st.markdown("### 4 · Decisión de diseño")
    st.markdown("""
    **Restricción del proyecto:** se busca el mayor aislamiento entre **500 y
    2.000 Hz**, pero primero debes comparar el desempeño técnico de las tres
    alternativas. Después, considera que el proyecto exige una solución liviana y
    descarta el hormigón.

    Tu respuesta debe:

    1. Identificar la mayor masa superficial.
    2. Comparar el TL en 500, 1.000 y 2.000 Hz.
    3. Ubicar la frecuencia crítica de cada placa.
    4. Explicar cualquier caída cercana a la coincidencia.
    5. Elegir entre yeso-cartón y madera bajo la restricción de bajo peso.
    """)
    decision=st.text_area(
        "Conclusión técnica y alternativa seleccionada",
        key="lab2_s3_design_decision",height=160,
        placeholder=(
            "La alternativa con mayor m′ es... Entre 500 y 2.000 Hz se observa... "
            "Las frecuencias críticas son... Al excluir el hormigón, seleccionaría... porque..."
        ))
    if st.button("Comprobar desarrollo",key="lab2_s3_check_decision"):
        if len(decision.strip()) < 140:
            st.warning(
                "La justificación aún es breve. Incluye valores de m′, fᶜ y TL en al "
                "menos dos frecuencias, y explica la selección liviana.")
        else:
            st.success(
                "La extensión es suficiente. Verifica que tu elección se apoye en los "
                "resultados calculados y no solamente en el nombre o espesor del material.")

    st.markdown("### 5 · Comprobación conceptual")
    check(
        "lab2_s3_compare_q1",
        "¿Por qué se integran los coeficientes τ antes de calcular el TL de campo?",
        [
            "Porque primero debe combinarse la energía transmitida y después convertirse a decibeles",
            "Porque los valores de TL no dependen del ángulo",
            "Porque 78° representa una única incidencia real",
            "Porque así se elimina la frecuencia crítica",
        ],
        "Porque primero debe combinarse la energía transmitida y después convertirse a decibeles",
        "El promedio se realiza en magnitudes energéticas; los TL angulares no se promedian directamente.",
    )
    check(
        "lab2_s3_compare_q2",
        "¿Qué afirmación interpreta correctamente la comparación?",
        [
            "El desempeño depende de masa superficial, rigidez, amortiguamiento y frecuencia",
            "La placa más gruesa siempre posee la frecuencia crítica más alta",
            "Todos los materiales de igual espesor producen la misma curva",
            "La coincidencia se añade dibujando una corrección artificial",
        ],
        "El desempeño depende de masa superficial, rigidez, amortiguamiento y frecuencia",
        "La curva surge del mismo modelo físico para las tres placas; no basta comparar solamente espesores.",
    )
    check(
        "lab2_s3_compare_q3",
        "Si aumenta el espesor de una placa manteniendo su densidad, ¿qué ocurre directamente con su masa superficial?",
        [
            "Aumenta, porque m′ = ρh",
            "Disminuye, porque la placa se vuelve más rígida",
            "Permanece constante, porque solo depende del material",
            "Se hace igual a la densidad del aire",
        ],
        "Aumenta, porque m′ = ρh",
        "La masa superficial es proporcional tanto a la densidad como al espesor de la placa.",
    )
    check(
        "lab2_s3_compare_q4",
        "¿Qué representa una disminución del TL alrededor de la frecuencia crítica?",
        [
            "Una mayor transmisión asociada al fenómeno de coincidencia",
            "La desaparición completa de la vibración de la placa",
            "Un aumento automático de la masa superficial",
            "Un error producido por usar frecuencia lineal",
        ],
        "Una mayor transmisión asociada al fenómeno de coincidencia",
        "Cerca de la frecuencia crítica se favorece el acoplamiento entre el campo sonoro y las ondas de flexión de la placa.",
    )
    check(
        "lab2_s3_compare_q5",
        "¿Por qué la imagen del sistema constructivo real no debe interpretarse como una predicción completa del tabique?",
        [
            "Porque el ejercicio modela una placa homogénea e infinita y no incorpora juntas, apoyos ni flancos",
            "Porque las imágenes no tienen dimensiones escritas",
            "Porque el hormigón no puede analizarse mediante masa superficial",
            "Porque el modelo solo funciona para incidencia normal",
        ],
        "Porque el ejercicio modela una placa homogénea e infinita y no incorpora juntas, apoyos ni flancos",
        "El modelo permite estudiar el material aislado, pero no reemplaza la evaluación del elemento instalado en obra.",
    )

def lab2_stage6():
    """Etapa 6 completa: pérdida de transmisión en ventanas dobles (Quirt, 1983)."""
    _lab2_heading(
        6,
        "Pérdida de transmisión sonora en ventanas dobles",
        "Comprender cómo las masas de los vidrios, la cámara y sus dimensiones "
        "modifican el TL por bandas.",
    )

    hero = ROOT / "assets/lab2/etapa6_ventana_doble_quirt_profesional.png"
    if hero.exists():
        st.image(str(hero), use_container_width=True)
    st.caption(
        "Dos vidrios separados por una cámara de aire: la primera hoja vibra, "
        "excita el campo de la cavidad y este pone en movimiento la segunda hoja."
    )

    st.markdown("### 1 · ¿Qué es una ventana doble desde el punto de vista acústico?")
    st.markdown("""
    Una ventana doble es un sistema **masa–aire–masa**. Cada vidrio funciona como una
    masa y el aire encerrado entre ambos actúa como un resorte. El sonido no atraviesa
    simplemente dos obstáculos independientes: las hojas quedan acopladas por la cámara.

    Por eso su respuesta presenta dos regiones:

    - **Bajo la frecuencia f₁:** las dos hojas se mueven fuertemente acopladas y el
      conjunto se aproxima a una placa cuya masa superficial es la suma de ambos vidrios.
    - **Sobre f₁:** las hojas responden de manera más independiente y la cavidad puede
      tratarse aproximadamente como un espacio reverberante. Intervienen el TL de cada
      vidrio, la separación, el perímetro y las dimensiones de la ventana.

    **En palabras simples:** antes de f₁, los dos vidrios tienden a “viajar juntos”.
    Después de f₁, la cámara ayuda a separarlos acústicamente y el aislamiento puede
    crecer con mayor rapidez.
    """)

    st.markdown("### 2 · Frecuencia que separa ambos comportamientos")
    formula_card(
        "Frecuencia f₁ de la ventana doble · Quirt (1983)",
        r"f_1=\frac{1}{2\pi}\sqrt{\frac{(\rho_{s1}+\rho_{s2})\rho_0c^2}"
        r"{d\,\rho_{s1}\rho_{s2}}}",
        "<b>ρs₁, ρs₂</b>: masas superficiales de los vidrios (kg/m²)<br>"
        "<b>ρ₀</b>: densidad del aire (kg/m³)<br>"
        "<b>c</b>: velocidad del sonido (m/s)<br>"
        "<b>d</b>: separación libre entre vidrios (m)<br>"
        "<b>f₁</b>: frecuencia límite del modelo (Hz)",
        "Para saber en qué banda deja de utilizarse la placa equivalente y comienza "
        "el régimen superior de la cavidad.",
    )
    st.info(
        "Aumentar la profundidad d reduce f₁. Esto desplaza la zona desfavorable hacia "
        "frecuencias más bajas. Aumentar la masa de los vidrios también tiende a reducirla."
    )

    st.markdown("### 3 · Pérdida de transmisión bajo f₁")
    st.latex(r"f<f_1")
    st.latex(r"TL(f)\approx TL_{\rho_{s1}+\rho_{s2}}(f)")
    st.markdown("""
    En esta región se estima el TL como el de una placa infinita cuya masa superficial
    equivale a la suma:
    """)
    st.latex(r"\rho_{s,\mathrm{eq}}=\rho_{s1}+\rho_{s2}")
    st.markdown(
        "**Lectura sencilla:** la cámara todavía no entrega toda la ventaja esperada; "
        "ambas hojas se comportan aproximadamente como una masa equivalente."
    )

    st.markdown("### 4 · Pérdida de transmisión sobre f₁")
    st.latex(r"f\geq f_1")
    formula_card(
        "Régimen superior de la ventana doble",
        r"TL=TL_{\rho_{s1}}+TL_{\rho_{s2}}+10\log_{10}(\alpha)"
        r"+10\log_{10}(d)+10\log_{10}\left(\frac{h+w}{hw}\right)+3",
        "<b>TLρs₁, TLρs₂</b>: TL individual de cada vidrio por banda<br>"
        "<b>α</b>: absorción a incidencia aleatoria del perímetro interior<br>"
        "<b>d</b>: profundidad de la cámara (m)<br>"
        "<b>h, w</b>: alto y ancho interiores de la cavidad (m)",
        "Para estimar el TL cuando la cavidad se considera un espacio reverberante.",
    )
    st.markdown("""
    La ecuación no significa que cualquier aumento de cámara entregue siempre la misma
    mejora. El resultado depende simultáneamente de las masas, la frecuencia, el tamaño
    de la cavidad y las pérdidas en el perímetro.

    **α no representa un absorbente que rellena la cámara.** Corresponde a la absorción
    efectiva del perímetro y de las superficies interiores. En una ventana estándar la
    cavidad permanece libre; por eso no debe aplicarse sin cambios el modelo de un tabique
    relleno con lana mineral.
    """)

    st.markdown("### 5 · Lo que el modelo ideal todavía no incluye")
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        "**Marco y sellos**\n\nUna pequeña fuga puede dominar la transmisión y reducir "
        "fuertemente el aislamiento medido."
    )
    c2.markdown(
        "**Coincidencia del vidrio**\n\nCada hoja puede presentar un valle propio. "
        "Vidrios iguales tienden a superponer sus debilidades."
    )
    c3.markdown(
        "**Transmisiones laterales**\n\nEncuentros, cajones de persiana y la fachada "
        "pueden limitar el resultado instalado."
    )
    st.warning(
        "Una cámara pequeña con dos vidrios iguales puede ser excelente térmicamente, "
        "pero no necesariamente es la solución acústica óptima. La asimetría desplaza "
        "las coincidencias y una cámara mayor reduce el acoplamiento masa–aire–masa."
    )

    st.markdown("## Laboratorio interactivo · construye y analiza una ventana doble")
    st.caption(
        "Modifica una variable a la vez y observa f₁, la región activa y la curva de TL."
    )
    dimensions_render = ROOT / "assets/lab2/ventana_doble_parametros_d_h_w.png"
    if dimensions_render.exists():
        st.image(str(dimensions_render), use_container_width=True)
        st.caption(
            "Geometría utilizada en el laboratorio: d es la separación entre placas; "
            "h y w corresponden a la altura y al ancho de la cavidad."
        )
    a, b, c = st.columns(3)
    g1 = a.slider("Espesor vidrio 1 (mm)", 3.0, 12.0, 4.0, 0.5, key="l2s6_g1")
    g2 = b.slider("Espesor vidrio 2 (mm)", 3.0, 12.0, 6.0, 0.5, key="l2s6_g2")
    gap_mm = c.slider("Separación entre placas d (mm)", 6, 200, 40, 2, key="l2s6_gap")
    d1, d2, d3 = st.columns(3)
    height = d1.slider("Altura de la cavidad h (m)", 0.5, 3.0, 1.5, 0.1, key="l2s6_h")
    width = d2.slider("Ancho de la cavidad w (m)", 0.5, 3.0, 1.2, 0.1, key="l2s6_w")
    alpha = d3.slider("Absorción perimetral α", 0.02, 0.30, 0.10, 0.01, key="l2s6_alpha")

    p1, p2 = st.columns(2)
    eta1 = p1.slider(
        "Factor de pérdidas del vidrio 1 η₁",
        0.001, 0.100, 0.010, 0.001,
        format="%.3f", key="l2s6_eta1",
    )
    eta2 = p2.slider(
        "Factor de pérdidas del vidrio 2 η₂",
        0.001, 0.100, 0.010, 0.001,
        format="%.3f", key="l2s6_eta2",
    )

    gap = gap_mm / 1000.0
    window_tl, tl1, tl2, equivalent, f1, masses, fcs, geometry = (
        _double_window_model(
            g1, g2, gap, height, width, alpha, eta1, eta2, FREQS
        )
    )
    m1, m2 = masses

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Masa vidrio 1", f"{m1:.1f} kg/m²")
    e2.metric("Masa vidrio 2", f"{m2:.1f} kg/m²")
    e3.metric("Frecuencias críticas", f"{fcs[0]:.0f} / {fcs[1]:.0f} Hz")
    e4.metric("Frecuencia f₁", f"{f1:.0f} Hz")

    selected_f = st.select_slider(
        "Frecuencia que deseas inspeccionar (Hz)",
        options=[int(v) for v in FREQS],
        value=500,
        key="l2s6_selected_f",
    )
    idx = int(np.argmin(np.abs(FREQS - selected_f)))
    regime = "Bajo f₁ · placa equivalente" if selected_f < f1 else "Sobre f₁ · cavidad reverberante"
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Régimen activo", regime)
    r2.metric("TL vidrio 1 · modelo físico", f"{tl1[idx]:.1f} dB")
    r3.metric("TL vidrio 2 · modelo físico", f"{tl2[idx]:.1f} dB")
    r4.metric("TL ventana doble", f"{window_tl[idx]:.1f} dB")
    st.caption(
        f"Configuración {g1:g}–{gap_mm}–{g2:g} mm. "
        f"A {selected_f} Hz se aplica: {regime}."
    )

    _plot_curves(
        [
            ("Ventana doble · modelo completo", window_tl, "solid"),
            ("Masa equivalente bajo f₁", equivalent, "dash"),
            ("Vidrio 1 · modelo físico", tl1, "dot"),
            ("Vidrio 2 · modelo físico", tl2, "dot"),
        ],
        "Pérdida de transmisión sonora por bandas",
        [(f1, "f₁"), (fcs[0], "fᶜ₁"), (fcs[1], "fᶜ₂")],
    )

    table = pd.DataFrame({
        "Frecuencia (Hz)": FREQS.astype(int),
        "Régimen": np.where(FREQS < f1, "Bajo f₁", "Sobre f₁"),
        "TL vidrio 1 (dB)": np.round(tl1, 1),
        "TL vidrio 2 (dB)": np.round(tl2, 1),
        "TL placa equivalente (dB)": np.round(equivalent, 1),
        "TL ventana doble (dB)": np.round(window_tl, 1),
    })
    st.dataframe(table, use_container_width=True, hide_index=True)

    with st.expander("Ver cálculo matemático en la frecuencia seleccionada"):
        st.markdown("**1 · Masas superficiales de los vidrios**")
        st.latex(
            rf"\rho_{{s1}}=2500\cdot {g1/1000:.4f}={m1:.2f}\ \mathrm{{kg/m^2}}"
        )
        st.latex(
            rf"\rho_{{s2}}=2500\cdot {g2/1000:.4f}={m2:.2f}\ \mathrm{{kg/m^2}}"
        )
        st.markdown("**2 · Frecuencia de cambio de régimen**")
        st.latex(rf"f_1={f1:.1f}\ \mathrm{{Hz}}")
        st.markdown("**3 · Cada vidrio se calcula primero con el modelo físico de placa simple**")
        st.latex(r"TL_{\mathrm{vidrio}}(f)=-10\log_{10}\overline{\tau}(f)")
        st.latex(
            rf"TL_{{1,\mathrm{{vidrio}}}}({selected_f})"
            rf"={tl1[idx]:.2f}\ \mathrm{{dB}},\quad "
            rf"f_{{c1}}={fcs[0]:.0f}\ \mathrm{{Hz}}"
        )
        st.latex(
            rf"TL_{{2,\mathrm{{vidrio}}}}({selected_f})"
            rf"={tl2[idx]:.2f}\ \mathrm{{dB}},\quad "
            rf"f_{{c2}}={fcs[1]:.0f}\ \mathrm{{Hz}}"
        )
        if selected_f < f1:
            st.markdown("**4 · La frecuencia seleccionada está bajo f₁**")
            st.latex(
                rf"TL({selected_f})=TL_{{\rho_{{s1}}+\rho_{{s2}}}}"
                rf"={equivalent[idx]:.1f}\ \mathrm{{dB}}"
            )
        else:
            st.markdown("**4 · La frecuencia seleccionada está sobre f₁**")
            st.latex(
                rf"TL({selected_f})={tl1[idx]:.1f}+{tl2[idx]:.1f}"
                rf"+10\log_{{10}}({alpha:.2f})+10\log_{{10}}({gap:.3f})"
                rf"+10\log_{{10}}\left(\frac{{{height:.1f}+{width:.1f}}}"
                rf"{{{height:.1f}\cdot {width:.1f}}}\right)+3"
            )
            st.latex(rf"TL({selected_f})={window_tl[idx]:.1f}\ \mathrm{{dB}}")
        st.caption(
            "Los TL de los vidrios incluyen masa, rigidez, amortiguamiento, incidencia "
            "angular y coincidencia mediante el modelo físico de placa simple. Quirt representa después "
            "la cavidad ideal; no incorpora fugas, marco, herrajes ni transmisión lateral."
        )

    if st.session_state.get("role") == "Docente":
        with st.expander("🔐 Lectura docente · interpretación y límites"):
            st.markdown("""
            - **Alrededor de f₁** debe enfatizarse el acoplamiento masa–aire–masa y la
              transición entre las dos expresiones; no interpretar un salto del modelo
              como una discontinuidad exacta de una ventana real.
            - **En bajas frecuencias** domina el acoplamiento y el ruido de tránsito
              pesado puede revelar la principal debilidad del sistema.
            - **En medias y altas frecuencias** crece el beneficio de separar las hojas,
              pero pueden aparecer coincidencias de los vidrios.
            - **Vidrios asimétricos** no garantizan por sí solos más TL en cada banda,
              pero evitan que ambas coincidencias se superpongan exactamente.
            - **El resultado instalado** estará limitado por marco, sellos, encuentros,
              cajones, ventilaciones y transmisiones laterales. La curva ideal no debe
              presentarse como un valor certificado de obra.
            """)

    st.markdown("### Cinco preguntas de comprensión")
    check(
        "lab2_s6_q1",
        "¿Qué representa físicamente el aire encerrado entre los dos vidrios?",
        ["Un resorte acústico que acopla ambas masas", "Una tercera placa sólida",
         "Una fuga permanente", "Un absorbente poroso"],
        "Un resorte acústico que acopla ambas masas",
        "El sistema se interpreta como masa–aire–masa: vidrio, resorte de aire y vidrio.",
    )
    check(
        "lab2_s6_q2",
        "¿Cómo se estima el TL bajo f₁ en este modelo?",
        ["Como una placa equivalente con la suma de masas", "Sumando directamente 20 dB",
         "Usando solo el vidrio más delgado", "Ignorando ambos vidrios"],
        "Como una placa equivalente con la suma de masas",
        "Bajo f₁ ambas hojas se consideran fuertemente acopladas.",
    )
    check(
        "lab2_s6_q3",
        "¿Qué suele ocurrir con f₁ al aumentar la profundidad d de la cámara?",
        ["Disminuye", "Aumenta", "Permanece siempre fija", "Se transforma en Rw"],
        "Disminuye",
        "En la ecuación, d está en el denominador dentro de la raíz.",
    )
    check(
        "lab2_s6_q4",
        "¿Por qué dos vidrios distintos pueden ser preferibles acústicamente?",
        ["Porque separan sus debilidades de coincidencia", "Porque eliminan el marco",
         "Porque llenan la cámara con absorbente", "Porque hacen innecesarios los sellos"],
        "Porque separan sus debilidades de coincidencia",
        "La asimetría ayuda a que los valles propios de ambas hojas no coincidan exactamente.",
    )
    check(
        "lab2_s6_q5",
        "¿La curva ideal calculada garantiza el mismo TL en la ventana instalada?",
        ["No; marco, sellos, fugas y flancos pueden dominar", "Sí, siempre",
         "Sí, si ambos vidrios son iguales", "Solo depende del color del marco"],
        "No; marco, sellos, fugas y flancos pueden dominar",
        "El desempeño real debe verificarse mediante datos de ensayo y una ejecución estanca.",
    )


LAB1_STAGE_TITLES = [
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
    ("Etapa 10","Evaluación final del Laboratorio 1"),
]
LAB2_STAGE_TITLES = [
    ("Etapa 0","Ruta completa del Laboratorio 2"),
    ("Etapa 1","Pérdida de transmisión: energía, τ y TL"),
    ("Etapa 2","Panel simple: incidencia y cuatro zonas"),
    ("Etapa 3","Comparación aplicada de placas simples"),
    ("Etapa 4","Pérdida de transmisión en paneles dobles"),
    ("Etapa 5","Modelo de Sharp: TL por tramos"),
    ("Etapa 6","Pérdida de transmisión en ventanas dobles"),
    ("Etapa 7","Bandas de frecuencia: octavas y tercios"),
    ("Etapa 8","Número único Rw, C y Ctr"),
    ("Etapa 9","Evaluación final · Preguntas de comprensión"),
    ("Etapa 10","Aplicación integradora · segunda mitad"),
]
LAB_STAGE_TITLES = {1: LAB1_STAGE_TITLES, 2: LAB2_STAGE_TITLES}
LAB_STAGE_FUNCTIONS = {
    1: [lab1_stage0,lab1_stage1,lab1_stage2,lab1_stage3,lab1_stage4,lab1_stage5,
        lab1_stage6,lab1_stage7,lab1_stage8,lab1_stage9,lab1_stage10],
    2: [lab2_stage0,lab2_stage1,lab2_stage2,lab2_stage3,lab2_stage4,lab2_stage5,
        lab2_stage6,lab2_stage7,lab2_stage8,lab2_stage9,lab2_stage10],
}

def _results_catalog():
    """Describe the ten laboratories for results and teacher release controls."""
    first_course=[]
    for lab_number in (1,2):
        minutes=STAGE_MINUTES if lab_number==1 else dict(enumerate(LAB2_MINUTES))
        stages=[]
        for stage,(prefix,title) in enumerate(LAB_STAGE_TITLES[lab_number]):
            stages.append({
                "title":title,
                "objective":f"{prefix} del Laboratorio {lab_number}.",
                "content_markdown":"",
                "activity_markdown":"",
                "teacher_solution":"",
                "minutes":int(minutes.get(stage,20)),
            })
        first_course.append({
            "id":LABORATORIES[lab_number]["id"],
            "course":"Aislamiento a ruido aéreo",
            "lab":lab_number,
            "stages":stages,
        })
    later=[]
    for lab in FUTURE_LABS.values():
        stages=[]
        for stage,(title,objective,concept,activity) in enumerate(lab["stages"]):
            stages.append({
                "title":title,"objective":objective,
                "content_markdown":concept,"activity_markdown":activity,
                "teacher_solution":"",
                "minutes":20 if stage not in (9,10) else 35,
            })
        later.append({
            "id":lab["id"],"course":lab["course"],"lab":lab["number"],"stages":stages,
        })
    return first_course+later

def _student_result_payload(value):
    """Decode the different answer formats used by both laboratories."""
    payload=value
    for _ in range(3):
        if isinstance(payload,str):
            try:
                payload=json.loads(payload)
            except (json.JSONDecodeError,TypeError):
                return payload
        elif isinstance(payload,dict) and set(payload)=={"value"}:
            payload=payload.get("value")
        else:
            break
    return payload

def _result_date(value):
    if not value:
        return "Fecha no registrada"
    try:
        parsed=dt.datetime.fromisoformat(str(value).replace("Z","+00:00"))
        return parsed.astimezone(SANTIAGO_TZ).strftime("%d-%m-%Y · %H:%M h")
    except (TypeError,ValueError):
        return str(value).replace("T"," ")[:16]

def _friendly_result_label(key):
    labels={
        "t60":"Tiempo de reverberación","volumen":"Volumen",
        "absorcion":"Absorción equivalente","diferencia_costo":"Diferencia de costo",
        "incremento_porcentual":"Incremento porcentual","bandas_criticas":"Bandas críticas",
        "recomendacion":"Recomendación","justificacion":"Justificación",
        "rw":"Rw","c":"C","ctr":"Ctr","description":"Descripción",
        "design_score":"Puntaje de diseño","comprehension_score":"Puntaje de comprensión",
        "wall":"Muro o tabique","window":"Ventana","door":"Puerta",
    }
    return labels.get(str(key),str(key).replace("_"," ").strip().capitalize())

def _clean_result_rows(payload,prefix=""):
    """Create readable rows while excluding persistence-only fields."""
    hidden={"reason","finished_at","rubric_scores","verification_signature","curve","tl","frequencies"}
    rows=[]
    if not isinstance(payload,dict):
        return [(prefix or "Respuesta",payload)]
    for key,value in payload.items():
        if key in hidden or key in {"answers","respuestas_teoricas","caso_integrador","calculated_result","student_result"}:
            continue
        label=f"{prefix} · {_friendly_result_label(key)}" if prefix else _friendly_result_label(key)
        if isinstance(value,dict):
            rows.extend(_clean_result_rows(value,label))
        elif isinstance(value,list):
            rows.append((label,", ".join(map(str,value)) if value else "Sin selección"))
        elif value not in (None,""):
            rows.append((label,value))
    return rows

def _render_final_exam_result(payload):
    theory=float(payload.get("puntaje_teorico",0) or 0)
    case=float(payload.get("puntaje_caso",0) or 0)
    hits=int(payload.get("aciertos_teoricos",0) or 0)
    c1,c2,c3=st.columns(3)
    c1.metric("Aciertos teóricos",f"{hits}/29")
    c2.metric("Puntaje teórico",f"{theory:g}/80")
    c3.metric("Caso integrador",f"{case:g}/20")
    case_data=payload.get("caso_integrador",{})
    if isinstance(case_data,dict) and case_data:
        st.markdown("**Caso profesional integrador**")
        table=pd.DataFrame(
            [{"Parámetro":_friendly_result_label(k),"Respuesta":", ".join(map(str,v)) if isinstance(v,list) else v}
             for k,v in case_data.items() if v not in (None,"")]
        )
        if not table.empty:
            st.dataframe(table,hide_index=True,use_container_width=True)

def _render_comprehension_result(payload):
    answers=payload.get("answers",{}) if isinstance(payload,dict) else {}
    if not isinstance(answers,dict):
        return
    correct=0
    for i,item in enumerate(STAGE9_QUESTIONS):
        chosen=answers.get(str(i),"Sin respuesta")
        expected=item["options"][item["correct"]]
        is_correct=chosen==expected
        correct+=int(is_correct)
        with st.expander(f"{'✅' if is_correct else '❌'} Pregunta {i+1} · {item['title']}"):
            st.write(f"**Tu respuesta:** {chosen}")
            st.caption("La pauta y explicación se muestran cuando corresponda según la liberación docente.")
    st.caption(f"Respuestas correctas: {correct} de {len(STAGE9_QUESTIONS)}")

def _render_integrated_result(payload):
    calculated=payload.get("calculated_result",{}) if isinstance(payload,dict) else {}
    student=payload.get("student_result",{}) if isinstance(payload,dict) else {}
    c1,c2,c3=st.columns(3)
    c1.metric("Rw calculado",f"{calculated.get('rw','—')} dB")
    c2.metric("C",f"{calculated.get('c','—')} dB")
    c3.metric("Ctr",f"{calculated.get('ctr','—')} dB")
    components=[]
    for key,label in (("wall","Muro o tabique"),("window","Ventana"),("door","Puerta")):
        data=payload.get(key,{})
        if isinstance(data,dict):
            components.append({"Elemento":label,"Solución":data.get("description","Sin información"),"Rw":data.get("rw","—")})
    if components:
        st.dataframe(pd.DataFrame(components),hide_index=True,use_container_width=True)
    if student:
        st.caption(f"Resultado ingresado por el alumno: Rw {student.get('rw','—')} dB · C {student.get('c','—')} dB · Ctr {student.get('ctr','—')} dB")

def results_view(client,catalog,user_key):
    """Student-facing academic results center; never exposes raw JSON."""
    header("MIS RESULTADOS","Tu avance académico","Revisa tus actividades, evaluaciones y observaciones docentes.")
    if client is None:
        st.info("Los resultados estarán disponibles cuando la aplicación recupere la conexión permanente.")
        return
    try:
        rows=(client.table("responses").select("*").eq("user_key",user_key)
              .in_("class_id",[LABORATORIES[1]["id"],LABORATORIES[2]["id"]])
              .order("updated_at",desc=True).execute().data or [])
    except Exception as exc:
        st.warning(f"No fue posible cargar tus resultados en este momento: {exc}")
        return
    if not rows:
        st.info("Todavía no tienes actividades enviadas. Tus resultados aparecerán aquí después del primer envío.")
        return

    earned=sum(float(r.get("teacher_score") if r.get("teacher_score") is not None else r.get("auto_score") or 0) for r in rows)
    maximum=sum(float(r.get("max_score") or 0) for r in rows)
    percent=(100*earned/maximum) if maximum else 0
    reviewed=sum(r.get("teacher_score") is not None or r.get("status")=="reviewed" for r in rows)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Puntaje registrado",f"{earned:g} de {maximum:g}")
    c2.metric("Porcentaje",f"{percent:.1f} %")
    c3.metric("Actividades enviadas",f"{len(rows)}")
    c4.metric("Revisadas por docente",f"{reviewed} de {len(rows)}")
    st.progress(min(1.0,max(0.0,percent/100)))

    for lab_number,lab in LABORATORIES.items():
        lab_rows=[r for r in rows if r.get("class_id")==lab["id"]]
        st.markdown(f"### Laboratorio {lab_number}")
        if not lab_rows:
            st.caption("Aún no hay actividades enviadas en este laboratorio.")
            continue
        lab_earned=sum(float(r.get("teacher_score") if r.get("teacher_score") is not None else r.get("auto_score") or 0) for r in lab_rows)
        lab_max=sum(float(r.get("max_score") or 0) for r in lab_rows)
        st.caption(f"{len(lab_rows)} actividades registradas · {lab_earned:g} de {lab_max:g} puntos obtenidos")
        for row in lab_rows:
            score=float(row.get("teacher_score") if row.get("teacher_score") is not None else row.get("auto_score") or 0)
            max_score=float(row.get("max_score") or 0)
            reviewed_now=row.get("teacher_score") is not None or row.get("status")=="reviewed"
            title=row.get("question_text") or f"Etapa {row.get('stage','—')}"
            with st.expander(f"{'✅' if score>=.6*max_score else '🟡'} {title} · {score:g}/{max_score:g} puntos"):
                a,b,c=st.columns(3)
                a.metric("Puntaje",f"{score:g}/{max_score:g}")
                b.metric("Estado","Revisado" if reviewed_now else "Enviado")
                c.metric("Fecha",_result_date(row.get("submitted_at") or row.get("updated_at")))
                payload=_student_result_payload(row.get("answer"))
                key=row.get("question_key")
                if key=="final_exam" and isinstance(payload,dict):
                    _render_final_exam_result(payload)
                elif key=="final_comprehension" and isinstance(payload,dict):
                    _render_comprehension_result(payload)
                elif key=="final_integrated_design" and isinstance(payload,dict):
                    _render_integrated_result(payload)
                else:
                    clean=_clean_result_rows(payload)
                    if clean:
                        st.markdown("**Tu respuesta**")
                        st.dataframe(pd.DataFrame(clean,columns=["Parámetro","Respuesta"]),hide_index=True,use_container_width=True)
                    else:
                        st.caption("La respuesta fue registrada correctamente.")
                note=row.get("teacher_note")
                if note:
                    st.info(f"**Retroalimentación docente:** {note}")
                elif not reviewed_now:
                    st.caption("Pendiente de revisión docente.")

def course_dashboard():
    header("MIS CLASES","Diplomado en Acústica en la Edificación",
           "Selecciona un curso y abre el laboratorio habilitado en la fecha programada.")
    client=_supabase()
    if client is None:
        st.warning("Supabase todavía no está configurado. La aplicación está usando almacenamiento local de prueba.")
        classes=[
            {"id":"clase-01-aislamiento-ruido-aereo","class_number":1,
             "title":"Laboratorio 1",
             "description":"","status":"published","due_at":None},
            {"id":"clase-02-aislamiento-ruido-aereo-minvu","class_number":2,
             "title":"Laboratorio 2",
             "description":"","status":"draft","due_at":None},
        ]
    else:
        classes=_course_classes(client)
    class_by_number={item.get("class_number"):item for item in classes}
    summaries,course_result=_result_summary()
    first_course=ACADEMIC_COURSES[0]
    st.markdown(f"### {first_course['title']}")
    for lab in first_course["labs"]:
        number=lab["number"]
        item=class_by_number.get(number,{})
        opening=_effective_opening(number,item.get("opens_at"),lab["opens_at"])
        released=item.get("status") in ("published","archived")
        if st.session_state.get("role")=="Alumno" and not released:
            continue
        available=released and _is_open(opening)
        if st.session_state.get("role")=="Docente":
            available=True
        summary=summaries[number]
        progress_status=("Pendiente" if summary["answered"]==0 else
                         "Completado" if summary["answered"]>=summary["expected"] else "En progreso")
        if st.session_state.get("role")=="Docente":
            availability=("Publicado para alumnos" if released else
                          "Borrador · oculto para alumnos")
        else:
            availability="Disponible" if available else f"Habilitación: {_opening_label(opening)}"
        st.markdown(
            f'<div class="lesson"><div class="overview-title">LABORATORIO {number}</div>'
            f'<span class="muted">{availability}</span><hr>'
            f'<b>{summary["earned"]:g}/{summary["maximum"]:g} puntos</b><br>'
            f'<span class="muted">Estado: {progress_status} · '
            f'{summary["answered"]} de {summary["expected"]} actividades realizadas</span></div>',
            unsafe_allow_html=True)
        if available and st.button(
            "Continuar laboratorio" if number==ACTIVE_LAB else "Abrir laboratorio",
            key=f"open_lab_{number}",type="primary" if number==ACTIVE_LAB else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_lab=number
            st.session_state["_open_lab_requested"]=True
            st.rerun()

    lab2_released=class_by_number.get(2,{}).get("status") in ("published","archived")
    st.markdown("#### Resultado del curso")
    if st.session_state.get("role")=="Alumno" and not lab2_released:
        st.info("El curso continúa en desarrollo. Tu avance del laboratorio publicado se conserva.")
    elif not course_result["final_done"]:
        st.warning(
            f'**Evaluación final: Pendiente.** Puntaje acumulado actual: '
            f'{course_result["earned"]:g}/{course_result["maximum"]:g} puntos. '
            'La nota final se calculará cuando envíes la evaluación final del Laboratorio 2.'
        )
    else:
        state="Aprobado" if course_result["grade"]>=4.0 else "Reprobado"
        st.success(
            f'**{state}.** Puntaje final: {course_result["earned"]:g}/'
            f'{course_result["maximum"]:g} puntos ({course_result["percent"]:.1f}%). '
            f'Nota final: **{course_result["grade"]:.1f}**.'
        )

    st.markdown("---")
    for course in COURSE_LABS:
        visible_labs=[]
        for lab in course["labs"]:
            row=next((r for r in classes if r.get("id")==lab["id"]),{})
            published=row.get("status") in ("published","archived")
            if st.session_state.get("role")=="Docente" or (published and _is_open(row.get("opens_at") or lab["opens_at"])):
                visible_labs.append((lab,row,published))
        if not visible_labs:
            continue
        st.markdown(f"### {course['course']}")
        columns=st.columns(2)
        for column,(lab,row,published) in zip(columns,visible_labs):
            with column:
                state=("Publicado para alumnos" if published else "Borrador · oculto para alumnos")
                st.markdown(
                    f'<div class="lesson"><div class="overview-title">LABORATORIO {lab["number"]}</div>'
                    f'<span class="muted">Programado: {_opening_label(row.get("opens_at") or lab["opens_at"])}</span><hr>'
                    f'<b>{state}</b><br><span class="muted">{lab["focus"]}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Abrir laboratorio",key=f'open_{lab["id"]}',use_container_width=True):
                    st.session_state["future_lab_id"]=lab["id"]
                    st.rerun()

def _future_saved(class_id):
    """Return the saved state for the selected student and future class."""
    cache_key=f"future_saved_{class_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    client=_supabase()
    if client is None:
        return {}
    try:
        rows=(client.table("user_progress").select("state_json")
              .eq("class_id",class_id).eq("user_key",st.session_state.user_key)
              .limit(1).execute().data or [])
        state=rows[0].get("state_json",{}) if rows else {}
        state=json.loads(state) if isinstance(state,str) else state
        st.session_state[cache_key]=state
        return state
    except Exception:
        return {}

def _save_future_state(class_id,state):
    client=_supabase()
    st.session_state[f"future_saved_{class_id}"]=state
    if client is None:
        return
    client.table("user_progress").upsert({
        "course_id":COURSE_ID,"class_id":class_id,
        "user_key":st.session_state.user_key,
        "role":st.session_state.get("role","Alumno"),
        "display_name":st.session_state.get("name",""),
        "state_json":state,"updated_at":_now(),
    },on_conflict="class_id,user_key").execute()

def future_lab_view(lab):
    """Data-driven renderer for the eight laboratories developed from the source material."""
    class_id=lab["id"]
    saved=_future_saved(class_id)
    with st.sidebar:
        uc=ROOT/"assets/logos/logo_uc.png"; decon=ROOT/"assets/logos/logo_decon_uc.png"
        if uc.exists(): st.image(str(uc),width=75)
        if decon.exists(): st.image(str(decon),width=130)
        st.markdown("## ◉ LABORATORIO")
        st.markdown(
            f'<div style="background:#0b4f83;border:1px solid #59d4ef;border-radius:12px;'
            f'padding:.75rem .85rem;margin:.35rem 0 .8rem"><b>LABORATORIO {lab["number"]}</b><br>'
            f'<span style="font-size:.78rem;color:#d9f5ff">{lab["course_short"]}</span></div>',
            unsafe_allow_html=True)
        st.caption("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN")
        st.markdown(f"**{st.session_state.name}**  \n{st.session_state.role}")
        answered=sum(1 for i in range(11) if saved.get(f"done_{i}"))
        st.progress(answered/11)
        st.caption(f"Avance: {answered}/11 etapas · {answered*10}/110 puntos formativos")
        formula_popup_button()
        if st.session_state.get("role") == "Alumno" and st.button("📊 Mis resultados", use_container_width=True):
            st.session_state.pop("future_lab_id", None)
            st.session_state["main_view"] = "📊 Mis resultados"
            st.rerun()
        selected=st.radio(
            "Ruta de aprendizaje",
            list(range(11)),
            format_func=lambda i:f"Etapa {i} · {lab['stages'][i][0]}",
            key=f"future_stage_{class_id}",
        )
        if st.button("← Volver a Mis clases",use_container_width=True):
            st.session_state.pop("future_lab_id",None); st.rerun()
        if st.session_state.get("role")=="Docente":
            client=_supabase()
            if client is not None:
                row=_class_row(class_id)
                published=row.get("status")=="published"
                st.caption("Publicado para alumnos" if published else "Borrador · oculto para alumnos")
                if st.button("Ocultar laboratorio" if published else "Publicar laboratorio",
                             key=f"future_publish_{class_id}",use_container_width=True):
                    client.table("classes").update({
                        "status":"draft" if published else "published","updated_at":_now()
                    }).eq("id",class_id).execute()
                    _clear_course_cache()
                    st.rerun()
        if st.button("Cerrar sesión",use_container_width=True):
            st.session_state.clear(); st.rerun()

    title,objective,concept,activity=lab["stages"][selected]
    stage_minutes=20 if selected not in (9,10) else 35
    header(f"ETAPA {selected} · LABORATORIO {lab['number']}",title,objective)
    st.caption(f"{lab['course']} · Fuente base: {lab['source']} · 4 horas totales")
    left,right=st.columns([1.25,.75])
    with left:
        st.markdown("### Desarrollo técnico")
        st.markdown(concept)
        if selected in (2,3,4,5,8):
            st.markdown("#### Regla de trabajo")
            if "ambiental" in lab["id"]:
                st.latex(r"L_{eq}=10\log_{10}\left(\frac{1}{T}\sum_i t_i\,10^{L_i/10}\right)")
            elif "construccion" in lab["id"]:
                st.latex(r"L_p(r_2)=L_p(r_1)-20\log_{10}(r_2/r_1)")
            elif "impacto" in lab["id"]:
                st.latex(r"L'_{nT}=L_i-10\log_{10}(T/T_0)")
            else:
                st.latex(r"D_{nT}=L_1-L_2+10\log_{10}(T/T_0)")
        st.info("Criterio profesional: registra dato, método, unidad, supuesto e interpretación. Un resultado sin trazabilidad no es verificable.")
    with right:
        st.markdown("### Mapa de decisión")
        st.markdown(f"""
        1. **Fenómeno:** {title}  
        2. **Magnitud:** elegir el indicador correcto.  
        3. **Método:** separar cálculo, medición y estimación.  
        4. **Decisión:** comparar con el criterio aplicable.  
        5. **Verificación:** definir cómo comprobar la medida.
        """)
        st.metric("Tiempo de etapa",f"{stage_minutes} min")

    st.markdown("### Actividad interactiva")
    st.write(activity)
    answer=st.text_area(
        "Desarrollo del alumno",
        value=saved.get(f"answer_{selected}",""),
        height=150,key=f"future_answer_{class_id}_{selected}",
        placeholder="Describe datos, procedimiento, resultado e interpretación.",
    )
    c1,c2,c3=st.columns(3)
    magnitude=c1.selectbox("Magnitud principal",["Seleccionar","Nivel por bandas","Índice único","Tiempo / duración","Vibración","Clase / cumplimiento"],key=f"mag_{class_id}_{selected}")
    method=c2.selectbox("Tipo de evidencia",["Seleccionar","Cálculo","Medición","Modelación","Inspección","Combinación"],key=f"method_{class_id}_{selected}")
    confidence=c3.slider("Confianza en la respuesta",1,5,3,key=f"conf_{class_id}_{selected}")
    if st.button("Guardar y completar etapa",type="primary",key=f"complete_{class_id}_{selected}"):
        if len(answer.strip())<40 or magnitude=="Seleccionar" or method=="Seleccionar":
            st.warning("Completa un desarrollo de al menos 40 caracteres y selecciona magnitud y evidencia.")
        else:
            saved.update({
                f"answer_{selected}":answer,f"magnitude_{selected}":magnitude,
                f"method_{selected}":method,f"confidence_{selected}":confidence,
                f"done_{selected}":True,f"updated_{selected}":_now(),
            })
            _save_future_state(class_id,saved)
            st.success("Etapa guardada. El avance pertenece únicamente a este laboratorio.")
            st.rerun()

    if st.session_state.get("role")=="Docente":
        with st.expander("🔐 Orientación docente y respuesta esperada"):
            if editable.get("teacher_solution"):
                st.markdown(editable["teacher_solution"])
            st.markdown(f"""
            **Evidencia mínima:** identificación correcta del fenómeno; selección coherente
            de magnitud y método; procedimiento trazable; resultado con unidad; decisión
            vinculada al criterio; medida verificable.

            **Retroalimentación sugerida:** revisar si la respuesta distingue propiedad de
            elemento, desempeño en terreno, exposición y percepción. Penalizar promedios
            aritméticos de decibeles, símbolos intercambiados y conclusiones normativas sin fuente.
            """)

def calculation_notebook():
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
    institutional_header()
    header("DIPLOMADO EN ACÚSTICA EN LA EDIFICACIÓN","Curso · Aislamiento a Ruido Aéreo","Laboratorios interactivos 1 y 2")
    role=st.radio("Perfil",["Alumno","Docente"],horizontal=True)
    name=st.text_input("Nombre completo")
    if role=="Alumno":
        rut=st.text_input("RUT o cédula de identificación")
        valid=bool(name.strip() and rut.strip())
        identification=_normalize_identification(rut)
    else:
        password=st.text_input("Clave docente",type="password")
        try:
            teacher_password=str(st.secrets["teacher"]["password"])
        except (KeyError, FileNotFoundError):
            teacher_password="docente123"
        valid=name.strip() and password==teacher_password
        identification="docente"
    if st.button("Ingresar",type="primary",use_container_width=True):
        if role=="Alumno" and valid:
            authorized,detail=_authorized_student(name,rut)
            if not authorized:
                st.error(detail)
                return
            roster_name=detail.get("display_name") or name.strip()
            roster_email=detail.get("email") or ""
            user_key=_make_user_key(role,name,identification)
            st.session_state.update(access=True,role=role,name=roster_name,user_key=user_key)
            _register_user(user_key,role,roster_name,rut,roster_email)
            load_user_progress(user_key)
            st.rerun()
        elif role=="Docente" and valid:
            user_key=_make_user_key(role,name,identification)
            st.session_state.update(access=True,role=role,name=name,user_key=user_key)
            _register_user(user_key,role,name)
            load_user_progress(user_key)
            st.rerun()
        else:
            st.error("Completa correctamente los datos de acceso.")

if st.query_params.get("projection")=="1":
    projection_view()
    st.stop()

st.session_state.pop("projection_mode",None)

if not st.session_state.get("access"):
    login();st.stop()

if st.query_params.get("formulas")=="1":
    formula_reference()
    st.stop()

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
    view_options=[
        "🏠 Mis clases",
        "📊 Mis resultados",
        f"📚 Laboratorio {ACTIVE_LAB} y actividades",
    ]
    if st.session_state.get("main_view") not in view_options:
        st.session_state["main_view"]="🏠 Mis clases"
    view=st.radio(
        "Vista",
        view_options,
        key="main_view",
        help="Selecciona Mis clases o la ruta del laboratorio.",
    )
    # El alumno ve la escala de la etapa abierta (por ejemplo, 100 puntos en
    # la evaluación final), no una suma de escalas diferentes. El docente
    # consulta puntajes exclusivamente en el Centro de resultados.
    if st.session_state.role=="Alumno":
        sidebar_stage=None
        if view==view_options[2]:
            saved_stage=st.session_state.get(f"selected_stage_lab_{ACTIVE_LAB}","")
            for stage_number,(stage_prefix,stage_title) in enumerate(LAB_STAGE_TITLES[ACTIVE_LAB]):
                if str(saved_stage).startswith(f"{stage_prefix} · {stage_title}"):
                    sidebar_stage=stage_number
                    break
        score_counter(stage=sidebar_stage,compact=True)
    formula_popup_button()
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
        with st.expander("📊 Centro de resultados · Curso 1"):
            teacher_course_results(compact=True)
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
elif view=="📊 Mis resultados":
    results_view(_supabase(), _results_catalog(), st.session_state.get("user_key", ""))
elif view==view_options[2]:
    lab_stages=LABORATORIES[ACTIVE_LAB]["stages"]
    if selected not in labels:
        selected=labels[lab_stages[0]]
    idx=labels.index(selected)
    st.caption(f"Curso: Aislamiento a ruido aéreo · Laboratorio {ACTIVE_LAB} de 2")
    LAB_STAGE_FUNCTIONS[ACTIVE_LAB][idx]()

# Autosave after every interaction. Closing the browser or changing tabs does not erase work.
save_user_progress()
