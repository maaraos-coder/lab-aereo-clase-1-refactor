"""Estilos globales de la aplicación."""

GLOBAL_CSS = r'''
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
'''

def apply_global_styles(st):
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
