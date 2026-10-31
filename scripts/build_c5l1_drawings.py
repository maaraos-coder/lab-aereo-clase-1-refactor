"""Reproducible academic architectural sheets (PDF + raster PNG previews)."""
from pathlib import Path
import math
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'curso5_lab1'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
pdfmetrics.registerFont(TTFont('DV', FONT))
pdfmetrics.registerFont(TTFont('DVB', FONT.replace('.ttf', '-Bold.ttf')))
INK, GRAY, BLUE, RED = '#263442', '#677582', '#126b99', '#b54732'
C = None

def line(x1,y1,x2,y2,color=INK,w=.18,dash=None):
    C.setStrokeColor(color); C.setLineWidth(w); C.setDash(dash or [])
    C.line(x1,y1,x2,y2); C.setDash([])

def rect(x,y,w,h,fill=None,stroke=INK,lw=.2):
    C.setLineWidth(lw); C.setStrokeColor(stroke)
    if fill: C.setFillColor(fill)
    C.rect(x,y,w,h,stroke=1,fill=bool(fill))

def text(x,y,s,h=2.5,color=INK,bold=False,align='left'):
    C.setFillColor(color); C.setFont('DVB' if bold else 'DV',h)
    getattr(C,{'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,str(s))

def poly(points,fill=None,stroke=INK,w=.2):
    p=C.beginPath();p.moveTo(*points[0])
    for point in points[1:]:p.lineTo(*point)
    p.close();C.setStrokeColor(stroke);C.setLineWidth(w)
    if fill:C.setFillColor(fill)
    C.drawPath(p,stroke=1,fill=bool(fill))

def hatch(x,y,w,h,color='#b0b7bd',spacing=2):
    C.saveState();p=C.beginPath();p.rect(x,y,w,h);C.clipPath(p,stroke=0,fill=0)
    for k in range(-int(h/spacing)-1,int(w/spacing)+2):
        xx=x+k*spacing;line(xx,y,xx+h,y+h,color,.12)
    C.restoreState()

def dimh(x1,x2,y,label,base=None):
    if base is not None:
        line(x1,base,x1,y+2,GRAY,.12);line(x2,base,x2,y+2,GRAY,.12)
    line(x1,y,x2,y,GRAY,.14)
    for x in (x1,x2):line(x-1,y-1,x+1,y+1,GRAY,.22)
    text((x1+x2)/2,y+1.5,label,2.25,align='center')

def dimv(y1,y2,x,label,base=None):
    if base is not None:
        line(base,y1,x+2,y1,GRAY,.12);line(base,y2,x+2,y2,GRAY,.12)
    line(x,y1,x,y2,GRAY,.14)
    for y in (y1,y2):line(x-1,y-1,x+1,y+1,GRAY,.22)
    C.saveState();C.translate(x-1.5,(y1+y2)/2);C.rotate(90)
    text(0,0,label,2.25,align='center');C.restoreState()

def arrow(x1,y1,x2,y2,label=None):
    line(x1,y1,x2,y2,RED,.65)
    ang=math.atan2(y2-y1,x2-x1)
    poly([(x2,y2),(x2-3*math.cos(ang-.42),y2-3*math.sin(ang-.42)),(x2-3*math.cos(ang+.42),y2-3*math.sin(ang+.42))],RED,RED)
    if label:text((x1+x2)/2+2,(y1+y2)/2+3,label,2.7,RED,True)

def note(y,title,lines):
    text(321,y,title,2.9,BLUE,True)
    yy=y-6
    for s in lines:
        text(321,yy,s,2.35);yy-=4.7
    return yy-8

def frame(code,title,subtitle,scale):
    C.saveState();C.scale(mm,mm)
    rect(10,10,400,277,None,INK,.35)
    text(18,277,'LOS ALERCES',5.7,INK,True)
    text(18,270,'EXPEDIENTE ACÚSTICO RESIDENCIAL / CURSO 5 · LABORATORIO 1',2.9,GRAY)
    text(402,277,code,5.7,BLUE,True,'right');text(402,270,'A-302 / CASO ACADÉMICO',2.6,GRAY,align='right')
    line(10,264,410,264,INK,.3);line(313,39,313,264,GRAY,.18)
    line(10,39,410,39,INK,.3);line(285,10,285,39,INK,.25)
    text(18,29,title,4.1,INK,True);text(18,21,subtitle,2.5,GRAY)
    text(18,14,'PROYECTO FICTICIO · NO APTO PARA CONSTRUCCIÓN · Las cotas prevalecen sobre la imagen.',2.2,RED)
    text(292,29,'ESCALA '+scale,2.8,INK,True);text(292,21,'UNIDADES m / DETALLES mm',2.4)
    text(292,14,'REVISIÓN · ACCESO Y PUERTAS · 30 OCT 2026',2.25,GRAY)

def end():C.restoreState();C.showPage()

def door(x,y,r=16,rotation=0):
    C.saveState();C.translate(x,y);C.rotate(rotation)
    line(0,0,r,0,'#ffffff',1.6);line(0,0,0,r,INK,.24)
    C.setLineWidth(.15);C.setStrokeColor(GRAY);C.arc(-r,-r,r,r,startAng=0,extent=90)
    C.restoreState()

def plan():
    frame('AC-01','PLANTA DE ESTUDIO · NIVEL 3','Acceso, distribución y puertas de A-302. Norte hacia arriba.','1:50 · impresión A3')
    k=20; ox=105; oy=244
    def P(x,y):return ox+x*k,oy-y*k
    def wall(a,b,width=1.4):line(*P(*a),*P(*b),INK,width)
    def opening(a,b,leaf=False,turn=1):
        # Clear the complete wall thickness, then draw leaf and swing in plan.
        line(*P(*a),*P(*b),'white',4.2)
        if leaf:
            dx,dy=b[0]-a[0],b[1]-a[1]
            vx,vy=-dy*turn,dx*turn
            line(*P(*a),*P(a[0]+vx,a[1]+vy),INK,.28)
            angle=math.atan2(dy,dx)
            pts=[P(a[0]+math.hypot(dx,dy)*math.cos(angle+turn*t*math.pi/48),a[1]+math.hypot(dx,dy)*math.sin(angle+turn*t*math.pi/48)) for t in range(25)]
            for q,r in zip(pts,pts[1:]):line(*q,*r,GRAY,.14)
    # Reference coordinates are clear-room dimensions, not external gross area.
    living=[(0,0),(6.12,0),(6.12,2.4),(3.4,2.4),(3.4,4.08),(0,4.08)]
    outline=[(0,0),(9.8,0),(9.8,5.125),(7.15,5.125),(7.15,6.95),(3.4,6.95),(3.4,6.785882),(0,6.785882)]
    poly([P(*q) for q in outline],'#fbf7ee',GRAY,.2)
    poly([P(*q) for q in living],'#eaf3f6',BLUE,.25)
    rect(*P(6.12,3.125),3.68*k,3.125*k,'#f7f7f3',GRAY,.15)
    rect(*P(0,6.785882),3.4*k,9.2/3.4*k,'#eef0fa',GRAY,.15)
    rect(*P(3.4,6.947647),2.72*k,7.8/2.72*k,'#edf5e9',GRAY,.15)
    rect(*P(7.15,5.125),2.05*k,2*k,'#eef4f6',GRAY,.15)
    rect(18,oy-4.08*k,83.4,4.08*k,'#f4f4f2',GRAY)
    text(59,222,'A-301',4,GRAY,True,'center');text(59,215,'Estar adyacente',2.7,GRAY,align='center')
    for q,r in zip(outline,outline[1:]+outline[:1]):wall(q,r,3)
    wall((0,0),(0,4.08),3.6)
    for q,r in [((6.12,0),(6.12,6.95)),((6.12,3.125),(9.8,3.125)),((0,4.08),(6.12,4.08)),((3.4,4.08),(3.4,6.95)),((7.15,3.125),(7.15,5.125))]:wall(q,r)
    # L-shaped living room opens into the north end of the distributor.
    # Its southern kitchen connection is also open; areas remain analytical zones.
    opening((6.12,3.15),(6.12,4.05))
    opening((4.6,4.08),(5.8,4.08))
    opening((6.12,5.5),(6.12,6.4))
    opening((2.3,4.08),(3.1,4.08),True,1)
    opening((6.23,3.125),(7.03,3.125),True,-1)
    opening((7.15,4.05),(7.15,4.85),True,-1)
    opening((7.08,6.95),(6.18,6.95),True,1)
    # North windows retain the acoustic dimensions of FA-01.
    for x,w,code,y in [(1.2,3.2,'V-01',0),(7.1,1.6,'V-02',0)]:
        opening((x,y),(x+w,y))
        xx,yy=P(x,y)
        for dy in (-.6,0,.6):line(xx,yy+dy,xx+w*k,yy+dy,BLUE,.22)
        text(xx+w*k/2,yy-5 if y==0 else yy+3,code,2.3,BLUE,True,'center')
    # Shaft borders both bathroom and principal bedroom, on the east side.
    xx,yy=P(9.2,3.725);rect(xx,yy,.6*k,.6*k,'#f9e7de',RED,.35);hatch(xx,yy,12,12,'#cd9e86')
    text(xx+6,yy+4.7,'S-1',2.4,RED,True,'center')
    # Furniture stays clear of the door sweeps and the 1.03 m distributor.
    rect(*P(.45,1.45),1.8*k,.65*k,None,GRAY,.2)
    rect(*P(2.9,1.7),1.3*k,.75*k,None,GRAY,.2)
    for x,y in [(7.2,.4),(.45,4.6)]:
        rect(*P(x,y+1.8),1.4*k,1.8*k,None,GRAY,.18);rect(*P(x+.1,y+.4),1.2*k,.3*k,None,GRAY,.12)
    rect(*P(3.55,6.7),.6*k,2.25*k,'#e4e7e6',GRAY,.15)
    rect(*P(8.35,4),.8*k,.8*k,None,GRAY,.18)
    rect(*P(8.45,4.7),.55*k,.55*k,None,GRAY,.18)
    for label,x,y,size in [('ESTAR-COMEDOR',2.7,2.35,3),('20,40 m² / V 51,0 m³',2.7,2.67,2.2),('DORM. PRINCIPAL',8.1,2.45,2.6),('11,50 m² / V 28,8 m³',8.1,2.75,2.1),('DORMITORIO 2',1.65,6.3,2.6),('9,20 m²',1.65,6.58,2.2),('COCINA',4.9,5.35,2.8),('7,80 m²',4.9,5.65,2.3),('BAÑO',8.1,4.5,2.7),('4,10 m²',8.1,4.8,2.2)]:text(*P(x,y),label,size,align='center')
    # Short straight distributor connects entrance to all private rooms.
    x,y=P(6.63,5.1);C.saveState();C.translate(x,y);C.rotate(90);text(0,0,'DISTRIBUIDOR 1,03 m',2.1,BLUE,True,'center');C.restoreState()
    rect(ox-3.6,oy-9.1*k,202.6,1.8*k,'#f1f1ed',GRAY,.18)
    text(ox+95,oy-8.35*k,'PASILLO COMÚN · 1,80 m',2.8,GRAY,align='center')
    arrow(*P(6.63,8),*P(6.63,6.7))
    text(*P(7.35,7.35),'ACCESO A-302',2.8,BLUE,True)
    text(*P(7.35,7.65),'P-01 · 0,90 m',2.3,GRAY)
    arrow(88,195,122,195,'AI-01')
    text(82,158,'M-01',2.8,RED,True);text(70,153,'HA 180 mm',2.3,GRAY)
    dimh(ox,ox+6.12*k,256,'6,12',oy);dimh(ox+6.12*k,ox+9.8*k,256,'3,68',oy)
    dimv(oy-4.08*k,oy,ox-9,'4,08',ox)
    dimh(ox+1.2*k,ox+4.4*k,250,'3,20',oy)
    dimh(*[P(x,0)[0] for x in (6.12,7.15)],130,'1,03')
    arrow(27,239,27,253);text(27,256,'N',3.4,INK,True,'center')
    line(17,205,304,205,BLUE,.22,[3,2]);text(19,208,'A',3,BLUE,True);text(300,208,'A',3,BLUE,True)
    y=note(253,'ACCESO Y CIRCULACIÓN',['P-01: acceso útil 0,90 m.','Distribuidor útil: 1,03 m.','Dormitorios y baño:','puertas útiles de 0,80 m.','Cocina y estar: vanos','abiertos desde distribuidor.','Las hojas abren a recintos.'])
    y=note(y,'GEOMETRÍA ACÚSTICA',['Estar en L: 20,40 m².','Altura libre: 2,50 m.','M-01: 4,08 × 2,50','= 10,20 m².','Fachada estar: 15,30 m².','V-01: 3,20 × 1,50','= 4,80 m².'])
    y=note(y,'INSTALACIONES',['Baño desplazado al este.','S-1 junto al baño y al','dormitorio principal.','La cocina abre al','distribuidor; no comparte','tabique directo con baño.'])
    note(y,'LECTURA DEL EJERCICIO',['A-301 al oeste.','A-402 sobre A-302.','Fachada norte arriba.','Pasillo común: muro opaco.','Cotas de recintos útiles;','no deducir superficie bruta.'])
    end()

def section():
    frame('AC-02','CORTE A-A · RELACIONES ENTRE VIVIENDAS','Cinco niveles; A-301 / A-302 y A-402. Escala vertical y horizontal común.','1:75 · impresión A3')
    k=1000/75;bx=53;by=65;leftw=5*k;rightw=6.12*k;total=leftw+rightw
    rect(bx-5,by-8,total+10,8,'#d7dbdc');hatch(bx-5,by-8,total+10,8)
    for floor in range(5):
        z=by+floor*2.72*k
        if floor==2:rect(bx+leftw,z,total-leftw,2.5*k,'#eaf3f6',BLUE,.25)
        rect(bx,z-.16*k,total,.16*k,'#7e898f');hatch(bx,z-.16*k,total,.16*k,'#b3bbc0',1.8)
        rect(bx,z,total,.06*k,'#d2bea1',GRAY,.1)
        for xx in (bx,bx+leftw,bx+total):rect(xx-.09*k,z,.18*k,2.72*k,'#414c53')
        n=floor+1
        text(bx+leftw/2,z+1.2*k,f'A-{n}01',3,GRAY,align='center')
        text(bx+leftw+rightw/2,z+1.25*k,f'A-{n}02',3.8,BLUE if floor==2 else INK,True,'center')
        text(bx+leftw+rightw/2,z+.8*k,'RECEPTOR' if floor==2 else ('EMISOR DE IMPACTO' if floor==3 else 'Vivienda'),2.4,GRAY,align='center')
        line(bx-10,z+.06*k,bx+total+15,z+.06*k,GRAY,.12,[2,2])
        text(bx+total+18,z+.06*k-1,f'+{floor*2.72:.2f} m',2.6)
    roof=by+5*2.72*k;rect(bx,roof-.16*k,total,.16*k,'#7e898f')
    dimv(by+2*2.72*k+.06*k,by+3*2.72*k-.16*k,bx-16,'2,50 libre',bx)
    dimv(by,by+2.72*k,bx-28,'2,72 nivel / nivel',bx)
    x=bx+leftw+rightw*.72
    arrow(x,by+3*2.72*k+1.8*k,x,by+2*2.72*k+1.7*k,'IM-01')
    arrow(bx+leftw-20,by+2*2.72*k+1.4*k,bx+leftw+18,by+2*2.72*k+1.4*k,'AI-01')
    text(bx+leftw+4,by+3*2.72*k-4,'L-01 · HA 160 mm + piso 60 mm',2.5,RED,True)
    line(22,by-8,295,by-8,INK,.3)
    y=note(253,'ALTURAS Y NIVELES',['Altura libre: 2,50 m.','Losa estructural: 160 mm.','Paquete superior: 60 mm.','Altura entre niveles: 2,72 m.','Nivel 1: +0,00 m.'])
    y=note(y,'IM-01 · IMPACTO',['A-402: fuente en estar.','A-302: receptor en estar.','Área L-01 útil: 20,40 m².','V receptor: 51,0 m³.','No sumar la sobrelosa a la','masa de la losa desnuda.'])
    y=note(y,'AI-01 · AÉREO',['M-01 entre A-301 / A-302.','Hormigón armado: 180 mm.','Superficie útil: 10,20 m².','Revisar flancos en losas,','fachada y encuentros.'])
    note(y,'ALCANCE',['La sección muestra los','recintos de cálculo.','Fundación y cubierta solo','contextualizan el edificio.','No son detalles de proyecto','estructural ejecutivo.'])
    end()

def elevation():
    frame('AC-03','FACHADA NORTE · ELEVACIÓN Y PAÑO DE CÁLCULO','V-01: estar / V-02: dormitorio. El límite azul identifica el caso FA-01.','1:100 · impresión A3')
    k=10;bx=48;by=72;bw=19.6*k
    for level in range(5):
        yy=by+level*2.72*k
        rect(bx,yy,bw,2.72*k,'#f6f6f3',GRAY,.2)
        line(bx,yy+.06*k,bx+bw,yy+.06*k,GRAY,.15)
        for half in (0,1):
            xx=bx+half*9.8*k
            for wx,ww in [(1.2,3.2),(7.1,1.6)]:
                rect(xx+wx*k,yy+.9*k,ww*k,1.5*k,'#dfedf1',INK,.3)
                line(xx+(wx+ww/2)*k,yy+.9*k,xx+(wx+ww/2)*k,yy+2.4*k,GRAY,.15)
                line(xx+wx*k,yy+.9*k,xx+(wx+ww)*k,yy+2.4*k,GRAY,.12)
        text(bx-5,yy+1.2*k,f'N{level+1}',2.8,align='right')
    line(bx,by+13.6*k,bx+bw,by+13.6*k,INK,.6)
    line(bx,by,bx+bw,by,INK,.5)
    xx=bx+9.8*k;yy=by+2*2.72*k+.06*k
    rect(xx,yy,6.12*k,2.5*k,None,BLUE,.65)
    text(xx+3.06*k,yy+2.5*k+5,'FA-01 · ESTAR A-302',3,BLUE,True,'center')
    text(xx+2.8*k,yy+1.5*k,'V-01',2.6,BLUE,True,'center')
    text(xx+7.9*k,yy+1.5*k,'V-02',2.4,align='center')
    dimh(xx,xx+6.12*k,by-12,'6,12 · paño del estar',by)
    dimh(bx,bx+bw,by-23,'19,60 · dos viviendas en fachada',by)
    dimv(yy,yy+2.5*k,bx+bw+12,'2,50',bx+bw)
    arrow(xx+30,by+13.6*k+24,xx+30,yy+30,'NORTE / EXTERIOR')
    y=note(253,'FA-01 · ESTAR A-302',['Fachada bruta: 15,30 m².','Ventana V-01: 4,80 m².','Opaco F-01: 10,50 m².','Volumen receptor: 51,0 m³.','V-01: DVH 6 / 12 / 4 mm.'])
    y=note(y,'V-02 · DORMITORIO',['Ventana: 1,60 × 1,50 m.','Área: 2,40 m².','Volumen receptor: 28,8 m³.','Se evalúa como otro caso;','no sumar al estar FA-01.'])
    y=note(y,'DATOS DE DISEÑO',['F-01: HA 150 mm + cámara','50 mm + yeso 15 mm.','Modelar marco y sellos según','los antecedentes disponibles.','El DVH por sí solo no','caracteriza toda la ventana.'])
    note(y,'EXPOSICIÓN EXTERIOR',['Lden no se obtiene del plano.','Usar un dato de referencia','o una hipótesis declarada.','65 dB se utiliza solo en el','ejemplo resuelto de etapa 3.'])
    end()

def details():
    frame('AC-04','DETALLES CONSTRUCTIVOS ACÚSTICOS','Soluciones de partida para el diseño; comprobar montaje, continuidad y ficha de producto.','1:5 · detalles acotados')
    # Four spacious detail panels, with keys beneath each drawing.
    for x,y in [(18,155),(166,155),(18,48),(166,48)]:rect(x,y,140,99,None,'#c2c8cd',.15)
    text(23,246,'D1 · M-01 / MEDIANERO',3.2,BLUE,True)
    rect(64,184,36,48,'#9aa2a7');hatch(64,184,36,48)
    dimh(64,100,237,'180 mm',232)
    arrow(33,210,59,210);text(25,219,'A-301',2.5);text(108,219,'A-302',2.5)
    for yy in (184,232):line(63,yy,101,yy,RED,.6)
    text(23,175,'Hormigón armado continuo entre losas.',2.45)
    text(23,169,'Sellado perimetral. Sin trasdosado en la base.',2.35)
    text(23,163,'La mejora se diseña y registra como variante.',2.35)
    text(171,246,'D2 · L-01 / PISO FLOTANTE',3.2,BLUE,True)
    y=187
    for h,fill,name in [(32,'#9aa2a7','HA 160'),(2,'#65aaa3','Resiliente 10'),(8,'#d0b797','Sobrelosa 40'),(2,'#ab835c','Terminación 10')]:
        rect(181,y,75,h,fill,INK,.15);text(262,y+h/2-1,name+' mm',2.35);y+=h
    rect(178,187,2,44,'#65aaa3');rect(174,187,3,44,'#56616b')
    text(171,175,'Banda perimetral continua: evita puente rígido.',2.35)
    text(171,169,'s′ y ΔL(f): requieren ficha o hipótesis declarada.',2.35)
    text(171,163,'No combinar dos mejoras para el mismo sistema.',2.35)
    text(23,139,'D3 · F-01 / TRASDOSADO',3.2,BLUE,True)
    rect(42,76,30,48,'#9aa2a7');hatch(42,76,30,48)
    rect(72,76,10,48,'#ede0a7');hatch(72,76,10,48,'#b69c4c',1.4)
    rect(82,76,3,48,'#dce1e6')
    line(79,80,79,120,INK,.35)
    dimh(42,72,129,'150',124);dimh(72,85,129,'50 + 15',124)
    text(92,117,'EXTERIOR',2.4,GRAY);text(92,111,'a la izquierda',2.25,GRAY)
    text(23,68,'HA 150 + cámara 50 + placa de yeso 15 mm.',2.35)
    text(23,62,'Absorbente y perfilería dentro de la cámara.',2.35)
    text(23,56,'Montaje desacoplado: justificar fijaciones.',2.35)
    text(171,139,'D4 · S-01 / CIERRE DE SHAFT',3.2,BLUE,True)
    for x in (190,192.5,209,211.5):rect(x,78,2.5,46,'#dce1e6',INK,.15)
    rect(195,78,14,46,'#ede0a7');hatch(195,78,14,46,'#b69c4c',1.5)
    C.setStrokeColor(INK);C.setLineWidth(.6);C.circle(242,101,9,stroke=1,fill=0)
    line(214,101,231,101,RED,.5);rect(228,98,3,6,'#65aaa3',GRAY,.15)
    dimh(190,214,129,'120 mm',124)
    text(262,106,'Tubería',2.35);text(262,100,'Abrazadera',2.35);text(262,94,'resiliente',2.35)
    text(171,68,'2 × RF 12,5 / cámara 70 / 2 × RF 12,5.',2.35)
    text(171,62,'120 mm es el conjunto, no cada placa.',2.35)
    text(171,56,'Transferencia estructural: dato no definido.',2.35)
    y=note(253,'MATERIALIDADES BASE',['M-01: HA 180 mm.','L-01: HA 160 mm.','F-01: 150 / 50 / 15 mm.','V-01 y V-02: DVH 6/12/4.','T-01: yeso 12,5 / cámara','65 / yeso 12,5 = 90 mm.'])
    y=note(y,'HIPÓTESIS ACADÉMICAS',['El paquete de piso suma','60 mm sobre losa.','El cierre S-01 se define','en esta revisión a 120 mm.','Los espesores no acreditan','prestaciones de catálogo.'])
    note(y,'VERIFICAR EN SONARA',['Propiedades de cada placa.','Densidad de hormigón.','Rigidez dinámica del piso.','Datos espectrales del DVH.','Puentes y juntas perimetrales.','Fuerza/velocidad sanitaria','y transferencia instalada.'])
    end()

def main():
    global C
    OUT.mkdir(parents=True,exist_ok=True)
    pdf=OUT/'los_alerces_planos_acusticos.pdf'
    C=canvas.Canvas(str(pdf),pagesize=(420*mm,297*mm))
    C.setTitle('Los Alerces · Planos académicos de diseño acústico')
    C.setAuthor('Laboratorio 1 · Curso 5')
    for draw in (plan,section,elevation,details):draw()
    C.save()
    stem=OUT/'_lamina'
    subprocess.run(['pdftoppm','-r','150','-png',str(pdf),str(stem)],check=True)
    from PIL import Image
    for n,name in enumerate(('planta_tipo','corte_aa','fachada_norte','detalles_constructivos'),1):
        src=OUT/f'_lamina-{n}.png'
        with Image.open(src) as im:im.save(OUT/f'{name}.png',optimize=True)
        src.unlink()
    print(pdf)

if __name__=='__main__':main()

