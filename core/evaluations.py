"""Evaluaciones, respuestas formativas y cálculo de puntajes.

La aplicación inyecta en tiempo de ejecución las dependencias compartidas para
conservar el estado, las consultas y las firmas públicas originales.
"""

from core.activities import activity_metadata

_PROTECTED = {
    '_FUNCTIONS',
    '_PROTECTED',
    '__effective_score_impl',
    '__finish_stage9_impl',
    '__grade_from_percent_impl',
    '__keyword_level_impl',
    '__question_points_impl',
    '__result_summary_impl',
    '__save_formative_impl',
    '__score_from_level_impl',
    '__scores_for_class_impl',
    '__stage9_answer_payload_impl',
    '__stage9_submission_impl',
    '__student_scores_impl',
    '_bind_runtime',
    '_formative_development_impl',
    '_formative_numeric_impl',
    '__saved_formative_response_impl',
    '__render_saved_activity_state_impl',
    '_score_counter_impl',
    'run_evaluation',
}

def _bind_runtime(runtime):
    module_globals=globals()
    for name,value in runtime.items():
        if name not in _PROTECTED:
            module_globals[name]=value

def __question_points_impl(stage,key):
    return float(LAB_POINT_SCHEMAS.get(ACTIVE_LAB,{}).get(stage,{}).get(key,0))


def __score_from_level_impl(level,max_score):
    return max_score if level=="Correcta" else max_score*.5 if level=="Parcialmente correcta" else 0.0


def __save_formative_impl(stage,key,question,answer,level,feedback,score=None,max_score=None,correct_answer=""):
    """Persist every activity through one common engine.

    Returns ``True`` only when the response was stored. Existing callers remain
    compatible because the public signature is unchanged.
    """
    if st.session_state.get("projection_mode"):
        return False
    student=st.session_state.get("name","Alumno")
    user_key=st.session_state.get("user_key") or _make_user_key("Alumno",student)
    max_score=_question_points(stage,key) if max_score is None else float(max_score)
    score=_score_from_level(level,max_score) if score is None else float(score)
    metadata=activity_metadata(CLASS_ID,stage,key)

    try:
        answer_json=json.loads(str(answer))
    except (json.JSONDecodeError,TypeError):
        answer_json={"value":str(answer)}
    if not isinstance(answer_json,dict):
        answer_json={"value":answer_json}
    answer_json.setdefault("_activity",metadata)

    client=_supabase()
    if client is not None:
        question_id=f"{CLASS_ID}-{key}-v1"
        client.table("questions").upsert({
            "id":question_id,"class_id":CLASS_ID,"stage":stage,
            "question_key":key,"question_text":question,
            "correct_answer":correct_answer or feedback,"max_score":max_score,
            "content_version":1,"active":True,"updated_at":_now(),
        },on_conflict="id").execute()
        client.table("responses").upsert({
            "course_id":COURSE_ID,"class_id":CLASS_ID,"user_key":user_key,
            "stage":stage,"question_key":key,"question_text":question,
            "correct_answer":correct_answer or feedback,"answer":answer_json,
            "auto_level":level,"feedback":feedback,"auto_score":score,
            "max_score":max_score,"status":"submitted",
            "updated_at":_now(),"submitted_at":_now(),
        },on_conflict="class_id,user_key,question_key").execute()
        return True

    with _activity_db() as con:
        con.execute(
        """INSERT INTO formative_responses
        (created_at,student,stage,question_key,question,answer,auto_level,feedback,auto_score,max_score)
        VALUES(?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(student,stage,question_key) DO UPDATE SET
        created_at=excluded.created_at,question=excluded.question,
        answer=excluded.answer,auto_level=excluded.auto_level,feedback=excluded.feedback,
        auto_score=excluded.auto_score,max_score=excluded.max_score""",
        (dt.datetime.now().isoformat(timespec="seconds"),student,stage,key,question,
         json.dumps(answer_json,ensure_ascii=False),level,feedback,score,max_score),
        )
    return True


def __saved_formative_response_impl(stage, key):
    """Recover the last persisted response for one formative activity."""
    user_key=st.session_state.get("user_key")
    if not user_key:
        return None
    client=_supabase()
    if client is not None:
        rows=_remote_rows("responses",class_id=CLASS_ID,user_key=user_key) or []
        row=next((r for r in rows if int(r.get("stage") or -1)==int(stage)
                  and str(r.get("question_key") or "")==str(key)),None)
        if row:
            answer=row.get("answer") or {}
            if isinstance(answer,str):
                try: answer=json.loads(answer)
                except Exception: answer={"value":answer}
            row=dict(row); row["answer"]=answer
        return row
    student=st.session_state.get("name","Alumno")
    with _activity_db() as con:
        row=con.execute(
            """SELECT answer,auto_level,feedback,auto_score,max_score,created_at
               FROM formative_responses
               WHERE student=? AND stage=? AND question_key=?""",
            (student,int(stage),str(key)),
        ).fetchone()
    if not row:
        return None
    answer=row[0]
    try: answer=json.loads(answer)
    except Exception: answer={"value":answer}
    return {"answer":answer,"auto_level":row[1],"feedback":row[2],
            "auto_score":row[3],"max_score":row[4],"updated_at":row[5]}


def __render_saved_activity_state_impl(saved, *, numeric=False):
    if not saved:
        return
    level=str(saved.get("auto_level") or "Guardada")
    score=float(saved.get("teacher_score") if saved.get("teacher_score") is not None else saved.get("auto_score") or 0)
    maximum=float(saved.get("max_score") or 0)
    icon="✅" if level=="Correcta" else "🟡" if level=="Parcialmente correcta" else "🔴"
    title=f"{icon} Actividad guardada · {level}"
    st.markdown(f"**{title}**")
    answer=saved.get("answer") or {}
    if numeric and isinstance(answer,dict):
        values={k:v for k,v in answer.items() if k!="_activity"}
        if values:
            st.caption("Última respuesta guardada: " + " · ".join(f"{k} = {v}" for k,v in values.items()))
    if maximum:
        st.caption(f"Puntaje formativo: {score:g} de {maximum:g} puntos")
    if saved.get("feedback"):
        st.caption(str(saved.get("feedback")))

def __student_scores_impl(student=None):
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


def __scores_for_class_impl(class_id, user_key=None):
    """Return effective scores for one laboratory without changing the active view."""
    client=_supabase()
    if client is None:
        return _student_scores()
    user_key=user_key or st.session_state.get("user_key")
    rows=_remote_rows("responses",class_id=class_id,user_key=user_key) if user_key else []
    return [(r["stage"],r["question_key"],float(r.get("auto_score") or 0),
             float(r.get("max_score") or 0),
             None if r.get("teacher_score") is None else float(r["teacher_score"])) for r in rows]


def __effective_score_impl(row):
    return (row[4] if row[4] is not None else row[2]) or 0


def __grade_from_percent_impl(percent):
    """Chilean 1.0–7.0 scale with 60% requirement for grade 4.0."""
    percent=max(0.0,min(100.0,float(percent)))
    if percent < 60:
        return 1.0 + 3.0*(percent/60.0)
    return 4.0 + 3.0*((percent-60.0)/40.0)


def __result_summary_impl():
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


def _score_counter_impl(stage=None,compact=False):
    if st.session_state.get("projection_mode"):
        return
    all_rows=_student_scores()
    if stage is not None:
        schema=LAB_POINT_SCHEMAS.get(ACTIVE_LAB,{}).get(stage,{})
        allowed=set(schema)
        rows=[row for row in all_rows if row[0]==stage and row[1] in allowed]
        maximum=sum(schema.values())
        title=f"Puntaje de la Etapa {stage}"
        expected=len(allowed)
    else:
        activity_stages=LAB_ACTIVITY_STAGES[ACTIVE_LAB]
        allowed_by_stage={s:set(LAB_POINT_SCHEMAS[ACTIVE_LAB][s]) for s in activity_stages}
        rows=[row for row in all_rows if row[0] in allowed_by_stage and row[1] in allowed_by_stage[row[0]]]
        maximum=sum(sum(LAB_POINT_SCHEMAS[ACTIVE_LAB][s].values()) for s in activity_stages)
        title=f"Actividades formativas · Lab. {ACTIVE_LAB}"
        expected=sum(len(keys) for keys in allowed_by_stage.values())
    # Supabase upsert keeps one row per key; dict also protects local/legacy duplicates.
    rows_by_key={(row[0],row[1]):row for row in rows}
    earned=sum((row[4] if row[4] is not None else row[2]) or 0 for row in rows_by_key.values())
    completed=len(rows_by_key)

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


def __keyword_level_impl(answer,groups):
    text=re.sub(r"\s+"," ",answer.lower())
    hits=sum(any(term.lower() in text for term in group) for group in groups)
    if hits>=max(2,math.ceil(len(groups)*.70)): return "Correcta",hits
    if hits>=max(1,math.ceil(len(groups)*.35)): return "Parcialmente correcta",hits
    return "Incorrecta",hits


def _formative_development_impl(stage,key,question,solution,groups,error_note):
    st.markdown(
        f'<div class="question-box"><div class="question-label">PREGUNTA DE DESARROLLO</div>'
        f'<div class="question-text">{question}</div></div>',unsafe_allow_html=True)
    answer=st.text_area("Escribe y justifica tu respuesta",key=f"ans_{key}",
                        placeholder="Explica el fenómeno y propone una solución cuando corresponda…")
    if st.button("Comprobar y guardar",key=f"submit_{key}",type="primary"):
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
            saved=_save_formative(stage,key,question,answer,level,feedback,correct_answer=solution)
            if saved:
                st.caption("✅ Actividad guardada en tu progreso formativo.")
    if st.session_state.get(f"checked_{key}"):
        with st.expander("Ver solución desarrollada"):
            st.markdown(solution)


def _formative_numeric_impl(stage,key,question,inputs,checker,solution):
    st.markdown(
        f'<div class="question-box"><div class="question-label">EJERCICIO NUMÉRICO</div>'
        f'<div class="question-text">{question}</div></div>',unsafe_allow_html=True)

    saved=__saved_formative_response_impl(stage,key)
    saved_answer=(saved or {}).get("answer") or {}
    if not isinstance(saved_answer,dict):
        saved_answer={}

    # Restore the persisted values only before Streamlit creates the widgets.
    for name,_,default,_ in inputs:
        widget_key=f"{key}_{name}"
        if widget_key not in st.session_state and name in saved_answer:
            try: st.session_state[widget_key]=float(saved_answer[name])
            except (TypeError,ValueError): st.session_state[widget_key]=default

    values={}
    cols=st.columns(min(len(inputs),3))
    for i,(name,label,default,step) in enumerate(inputs):
        values[name]=cols[i%len(cols)].number_input(label,value=default,step=step,key=f"{key}_{name}")

    __render_saved_activity_state_impl(saved,numeric=True)

    button_label="Actualizar respuesta" if saved else "Comprobar y guardar"
    if st.button(button_label,key=f"submit_{key}",type="primary"):
        ok,feedback=checker(values)
        level="Correcta" if ok else "Incorrecta"
        saved_ok=_save_formative(
            stage,key,question,json.dumps(values,ensure_ascii=False),level,feedback,
            correct_answer=solution,
        )
        if not saved_ok:
            st.error("No fue posible guardar el cálculo. Intenta nuevamente.")
        else:
            st.session_state[f"checked_{key}"]=(level,feedback)
            st.rerun()

    if saved or st.session_state.get(f"checked_{key}"):
        with st.expander("Ver desarrollo paso a paso"):
            st.markdown(solution)


def __stage9_submission_impl():
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


def __stage9_answer_payload_impl(row):
    """Decode the single definitive Stage 9 response saved in Supabase."""
    payload=row.get("answer") or {}
    if isinstance(payload,str):
        try:
            payload=json.loads(payload)
        except json.JSONDecodeError:
            payload={}
    return payload if isinstance(payload,dict) else {}


def __finish_stage9_impl(reason="submitted"):
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


_FUNCTIONS = {
    '_question_points': __question_points_impl,
    '_score_from_level': __score_from_level_impl,
    '_save_formative': __save_formative_impl,
    '_student_scores': __student_scores_impl,
    '_scores_for_class': __scores_for_class_impl,
    '_effective_score': __effective_score_impl,
    '_grade_from_percent': __grade_from_percent_impl,
    '_result_summary': __result_summary_impl,
    'score_counter': _score_counter_impl,
    '_keyword_level': __keyword_level_impl,
    'formative_development': _formative_development_impl,
    'formative_numeric': _formative_numeric_impl,
    '_saved_formative_response': __saved_formative_response_impl,
    '_render_saved_activity_state': __render_saved_activity_state_impl,
    '_stage9_submission': __stage9_submission_impl,
    '_stage9_answer_payload': __stage9_answer_payload_impl,
    '_finish_stage9': __finish_stage9_impl,
}

def run_evaluation(name,runtime,*args,**kwargs):
    _bind_runtime(runtime)
    return _FUNCTIONS[name](*args,**kwargs)
