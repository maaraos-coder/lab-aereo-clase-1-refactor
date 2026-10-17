"""Revisión docente de entregas individuales del Curso 4 · Laboratorio 2."""
from copy import deepcopy
import base64
import io
import json
import math
import zipfile

from labs.curso4_laboratorio_2_stage10 import (
    RUBRIC, TEACHER_GUIDE, _grade, _render_integrated_report, _report_typography,
)

CLASS_ID = "clase-08-construccion-lab-2"
CATALOG = {
    "Etapa 9 · Cuestionario oficial": {
        "class_id":CLASS_ID,"question_key":"c4l2_final_quiz","stage":9,
        "maximum":30,"with_grade":True,"reviewer":"c4l2_stage9",
    },
    "Etapa 10 · Informe técnico integral y anexos": {
        "class_id":CLASS_ID,"question_key":"c4l2_integrated_project","stage":10,
        "maximum":70,"with_grade":False,"reviewer":"c4l2_stage10","integrated":True,
    },
}


def payload_of(row):
    value=(row or {}).get("answer") or {}
    if isinstance(value,str):
        try: value=json.loads(value)
        except (TypeError,ValueError): return {}
    return deepcopy(value) if isinstance(value,dict) else {}


def score(value,maximum):
    try: value=float(value)
    except (TypeError,ValueError): return None
    return value if math.isfinite(value) and 0<=value<=maximum else None


def quiz_points(payload,quiz_row=None):
    if quiz_row:
        return score(quiz_row.get("teacher_score") if quiz_row.get("teacher_score") is not None else quiz_row.get("auto_score"),30)
    return score((payload.get("stage_9") or {}).get("score"),30)


def final_result(row,quiz_row=None):
    practical=score(row.get("teacher_score"),70)
    quiz=quiz_points(payload_of(row),quiz_row)
    total=None if practical is None or quiz is None else practical+quiz
    return {"practical":practical,"quiz":quiz,"total":total,"grade":None if total is None else _grade(total)}


def review_note(row):
    note=row.get("teacher_note") or ""
    try: parsed=json.loads(note) if isinstance(note,str) else note
    except (TypeError,ValueError): parsed=None
    return parsed if isinstance(parsed,dict) else {"feedback":str(note),"rubric_scores":{}}


def persist_review(client,row,updates):
    result=client.table("responses").update(updates).eq("id",row["id"]).eq("class_id",CLASS_ID).eq("stage",row["stage"]).eq("question_key",row["question_key"]).eq("user_key",row["user_key"]).select("id").execute()
    if not getattr(result,"data",None):
        raise RuntimeError("No se confirmó la actualización de esta entrega.")


def report_bundle(payload):
    """Expediente recibido, incluyendo imágenes, sin datos de otros alumnos."""
    output=io.BytesIO()
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("informe_entregado.json",json.dumps(payload,ensure_ascii=False,indent=2))
        for group_index,(group,items) in enumerate((payload.get("maps") or {}).items(),1):
            for index,item in enumerate(items or [],1):
                try: raw=base64.b64decode(str(item.get("data") or ""),validate=True)
                except (TypeError,ValueError): continue
                if not raw: continue
                mime=item.get("mime") or "image/webp"
                extension={"image/webp":"webp","image/png":"png","image/jpeg":"jpg"}.get(mime,"bin")
                archive.writestr(f"imagenes/grupo_{group_index}/mapa_{index}.{extension}",raw)
    return output.getvalue()


def render_review(st,pd,client,rows,config,now,compact=False):
    if st.session_state.get("role")!="Docente": return
    rows=[row for row in rows if row.get("class_id")==CLASS_ID
          and row.get("question_key")==config["question_key"] and row.get("stage")==config["stage"]]
    if not rows:
        st.caption("Todavía no hay entregas del Curso 4 · Laboratorio 2 para esta evaluación.")
        return
    selected=st.selectbox("Alumno",range(len(rows)),format_func=lambda i:
        (rows[i].get("users") or {}).get("display_name") or (rows[i].get("users") or {}).get("email") or rows[i].get("user_key","Alumno"),
        key=f"teacher_c4l2_student_{config['stage']}_{compact}")
    row=rows[selected]
    payload=payload_of(row)
    prefix=f"teacher_c4l2_{config['stage']}_{row['id']}_{compact}"
    user=row.get("users") or {}
    st.markdown("#### Entrega de "+str(user.get("display_name") or row.get("user_key") or "Alumno"))
    st.caption("Entrega recibida: "+str(row.get("submitted_at") or row.get("updated_at") or "—"))
    note=review_note(row)
    if config["stage"]==9:
        from labs.curso4_laboratorio_2_stage9 import QUESTIONS
        answers=payload.get("answers") or {}
        st.metric("Resultado automático",f"{float(row.get('auto_score') or 0):g}/30")
        for index,question in enumerate(QUESTIONS):
            with st.expander(f"{index+1}. {question[1]}",expanded=index==0):
                st.write("Respuesta del alumno: "+str(answers.get(str(index)) or "Sin respuesta"))
                st.write("Respuesta esperada: "+str(question[2][question[3]]))
        feedback=st.text_area("Observación docente",value=note.get("feedback", ""),key=prefix+"_feedback")
        if st.button("Guardar revisión del cuestionario",key=prefix+"_save"):
            try:
                persist_review(client,row,{"teacher_score":float(row.get("auto_score") or 0),"teacher_note":feedback,
                    "status":"reviewed","teacher_level":"Revisada","updated_at":now()})
            except Exception:
                st.error("No se pudo guardar la revisión. Vuelve a intentarlo.")
            else: st.success("Revisión del cuestionario guardada.")
        return
    quiz_row=None
    try:
        quiz_rows=client.table("responses").select("auto_score,teacher_score").eq("class_id",CLASS_ID).eq("stage",9).eq("question_key","c4l2_final_quiz").eq("user_key",row["user_key"]).limit(1).execute().data or []
        quiz_row=quiz_rows[0] if quiz_rows else None
    except Exception:
        st.warning("No se pudo actualizar el puntaje del cuestionario. Se muestra el incluido en el informe entregado, si existe.")
    result=final_result(row,quiz_row)
    a,b,c=st.columns(3)
    a.metric("Cuestionario",f"{result['quiz']:g}/30" if result['quiz'] is not None else "Pendiente")
    b.metric("Informe práctico",f"{result['practical']:g}/70" if result['practical'] is not None else "Pendiente de revisión")
    c.metric("Nota final",f"{result['grade']:.1f}" if result['grade'] is not None else "Pendiente")
    st.caption("La nota final suma cuestionario (30) e informe práctico (70). No se calcula una nota independiente sobre 70 puntos.")
    _report_typography(st)
    _render_integrated_report(st,pd,payload,quiz_score=result['quiz'],reference_mode=False)
    st.download_button("Descargar informe entregado y anexos (.zip)",report_bundle(payload),
        file_name="informe_y_anexos.zip",mime="application/zip",key=prefix+"_bundle")
    with st.expander("Detalle completo de los datos entregados",expanded=False):
        st.json(payload)
    st.markdown("### Revisión docente del informe · 70 puntos")
    awarded={}
    previous=note.get("rubric_scores") or {}
    for stage,criterion,maximum in RUBRIC:
        st.caption(" · ".join(f"{title}: {points} ptos" for title,points in TEACHER_GUIDE[stage]))
        awarded[str(stage)]=st.number_input(f"Etapa {stage} · {criterion} / {maximum}",min_value=0.,max_value=float(maximum),
            value=score(previous.get(str(stage)),maximum) or 0.,step=.5,key=prefix+f"_rubric_{stage}")
    practical=sum(awarded.values())
    st.metric("Puntaje práctico propuesto",f"{practical:g}/70")
    if result['quiz'] is not None:
        st.metric("Nota final propuesta",f"{_grade(practical+result['quiz']):.1f}")
    feedback=st.text_area("Retroalimentación para el alumno",value=note.get("feedback", ""),key=prefix+"_feedback")
    if st.button("Guardar revisión y publicar resultado",type="primary",key=prefix+"_save"):
        # La respuesta original y las imágenes permanecen como fueron entregadas.
        try:
            persist_review(client,row,{"teacher_score":practical,
                "teacher_note":json.dumps({"feedback":feedback,"rubric_scores":awarded},ensure_ascii=False),
                "teacher_level":"Revisada","status":"reviewed","updated_at":now()})
        except Exception:
            st.error("No se pudo guardar la revisión. Se conserva la entrega original.")
        else: st.success("Revisión publicada. El alumno podrá ver su puntaje práctico y retroalimentación en la Etapa 10.")
