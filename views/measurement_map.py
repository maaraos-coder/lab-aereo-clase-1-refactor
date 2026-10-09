"""Mapa vial compartido por la entrega del alumno y su revisión docente."""
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st


def render_road_map(complete, intersection_lat, intersection_lon, interval=5, key="road_map"):
    interval = interval if interval in (3, 5) else 5
    valid_levels=[float(r["Leq [dB(A)]"]) for r in complete]
    center_ok=(
        isinstance(intersection_lat,(int,float)) and isinstance(intersection_lon,(int,float))
        and -90<=float(intersection_lat)<=90 and -180<=float(intersection_lon)<=180
        and not (abs(float(intersection_lat))<1e-9 and abs(float(intersection_lon))<1e-9)
    )
    geo_complete=[
        r for r in complete
        if isinstance(r.get("Latitud"),(int,float)) and isinstance(r.get("Longitud"),(int,float))
        and -90<=float(r.get("Latitud"))<=90 and -180<=float(r.get("Longitud"))<=180
        and not (abs(float(r.get("Latitud")))<1e-9 and abs(float(r.get("Longitud")))<1e-9)
    ]

    def _c3l2_fit_axis(rows,lat0,lon0):
        """Proyecta GPS reales sobre un eje recto anclado al centro del cruce."""
        if len(rows)<2:
            return []
        lat0r=math.radians(lat0)
        sx=111320.0*max(0.20,math.cos(lat0r))
        sy=110540.0
        pts=[]
        for r in rows:
            x=(float(r["Longitud"])-lon0)*sx
            y=(float(r["Latitud"])-lat0)*sy
            pts.append([x,y])
        arr=np.asarray(pts,dtype=float)
        cov=arr.T@arr
        vals,vecs=np.linalg.eigh(cov)
        direction=vecs[:,int(np.argmax(vals))]
        # Mantener orientación estable para que el orden espacial no cambie entre reruns.
        if abs(direction[0])>=abs(direction[1]):
            if direction[0]<0: direction=-direction
        elif direction[1]<0:
            direction=-direction
        out=[]
        for r,p in zip(rows,arr):
            t=float(np.dot(p,direction))
            q=direction*t
            lat=lat0+q[1]/sy
            lon=lon0+q[0]/sx
            rr=dict(r)
            rr["_map_lat"]=float(lat)
            rr["_map_lon"]=float(lon)
            rr["_axis_t"]=t
            out.append(rr)
        return out

    if valid_levels and center_ok:
        principal_geo=[r for r in geo_complete if r.get("Vía")=="Vía principal"]
        secondary_geo=[r for r in geo_complete if r.get("Vía")=="Vía secundaria"]
        snapped_principal=_c3l2_fit_axis(principal_geo,float(intersection_lat),float(intersection_lon))
        snapped_secondary=_c3l2_fit_axis(secondary_geo,float(intersection_lat),float(intersection_lon))
        snapped=snapped_principal+snapped_secondary

        if len(snapped_principal)>=2 and len(snapped_secondary)>=2:
            lo=math.floor(min(valid_levels)/interval)*interval
            hi=math.ceil(max(valid_levels)/interval)*interval
            palette=["#C0FFC0","#00CC00","#005000","#FFFF00","#FFC74A","#FF6600","#FF3333","#990033","#AD9AD6","#0000FF","#000066","#000000"]

            def _road_color(level):
                idx=int(math.floor((float(level)-lo)/interval))
                return palette[max(0,min(len(palette)-1,idx))]

            fig=go.Figure()

            # Dibujar cada vía según la posición geográfica ajustada al eje vial.
            for route_rows,route_name in [(snapped_principal,"Vía principal"),(snapped_secondary,"Vía secundaria")]:
                ordered=sorted(route_rows,key=lambda r:r["_axis_t"])
                for i,r in enumerate(ordered):
                    lv=r.get("Leq [dB(A)]")
                    if not isinstance(lv,(int,float)):
                        continue
                    if i==0:
                        a_lat=float(intersection_lat); a_lon=float(intersection_lon)
                    else:
                        a_lat=ordered[i-1]["_map_lat"]; a_lon=ordered[i-1]["_map_lon"]
                    fig.add_trace(go.Scattermap(
                        lat=[a_lat,r["_map_lat"]],lon=[a_lon,r["_map_lon"]],
                        mode="lines",
                        line=dict(width=10,color=_road_color(lv)),
                        hoverinfo="skip",showlegend=False,
                    ))

            # Puntos representados sobre el eje de la calzada.
            for route_rows in (snapped_principal,snapped_secondary):
                if not route_rows:
                    continue
                fig.add_trace(go.Scattermap(
                    lat=[r["_map_lat"] for r in route_rows],
                    lon=[r["_map_lon"] for r in route_rows],
                    mode="markers+text",
                    text=[r["Punto"] for r in route_rows],
                    textposition="top center",
                    marker=dict(
                        size=14,
                        color=[_road_color(r["Leq [dB(A)]"]) for r in route_rows],
                    ),
                    customdata=[[
                        r["Punto"],r["Vía"],float(r["Leq [dB(A)]"]),float(r["Lmax [dB(A)]"]),
                        float(r["Latitud"]),float(r["Longitud"])
                    ] for r in route_rows],
                    hovertemplate=(
                        "<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                        "Leq: %{customdata[2]:.1f} dB(A)<br>"
                        "Lmax: %{customdata[3]:.1f} dB(A)<br>"
                        "GPS medido: %{customdata[4]:.6f}, %{customdata[5]:.6f}<br>"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                ))

            fig.add_trace(go.Scattermap(
                lat=[float(intersection_lat)],lon=[float(intersection_lon)],
                mode="markers+text",text=["Intersección"],textposition="bottom right",
                marker=dict(size=15,color="#111827"),
                hovertemplate="Centro de la intersección<extra></extra>",
                showlegend=False,
            ))

            # Escala de colores vertical tipo mapa de ruido.
            n_bins=max(1,int(math.ceil((hi-lo)/interval))+1)
            legend_rows=[]
            for bi in range(min(n_bins,len(palette))):
                a=lo+bi*interval; b=a+interval
                legend_rows.append((a,b,palette[bi]))

            lat_values=[r["_map_lat"] for r in snapped]+[float(intersection_lat)]
            lon_values=[r["_map_lon"] for r in snapped]+[float(intersection_lon)]
            lat_span=max(lat_values)-min(lat_values)
            lon_span=max(lon_values)-min(lon_values)
            span=max(lat_span,lon_span,0.0005)
            zoom=max(13.0,min(18.5,16.8-math.log10(span/0.003+1.0)))

            fig.update_layout(
                height=620,
                map=dict(
                    style="open-street-map",
                    center=dict(lat=float(intersection_lat),lon=float(intersection_lon)),
                    zoom=zoom,
                ),
                margin=dict(l=0,r=0,t=0,b=0),
                showlegend=False,
            )
            st.plotly_chart(fig,use_container_width=True,key=key)

            legend_html='<div style="display:flex;gap:14px;align-items:stretch;margin:.35rem 0 1rem">'
            legend_html+='<div style="font-size:.78rem;font-weight:800;color:#334155;writing-mode:vertical-rl;transform:rotate(180deg);text-align:center">Leq dB(A)</div>'
            legend_html+='<div style="display:flex;flex-direction:column-reverse;gap:2px">'
            for a,b,color in legend_rows:
                legend_html+=f'<div style="display:flex;align-items:center;gap:7px;font-size:.78rem"><span style="width:26px;height:18px;background:{color};border:1px solid rgba(0,0,0,.15)"></span><span>{a:g}–&lt;{b:g}</span></div>'
            legend_html+='</div></div>'
            st.markdown(legend_html,unsafe_allow_html=True)
            st.caption(
                "Mapa sobre cartografía OpenStreetMap. Las coordenadas GPS originales se mantienen en el registro; "
                "para la representación vial se proyectan al eje estimado de cada calle, anclado al centro de la intersección. "
                "Este ajuste es cartográfico y no modifica el lugar real donde se efectuó la medición."
            )
        else:
            st.info("Para construir el mapa real se requieren al menos 2 puntos con coordenadas válidas en cada vía, además de Leq/Lmax.")
    elif valid_levels and not center_ok:
        st.info("Ingresa la latitud y longitud del centro de la intersección para dibujar el mapa sobre la ubicación real.")
    else:
        st.info("Completa Leq, Lmax y las coordenadas GPS de los puntos para comenzar a construir automáticamente el mapa vial georreferenciado.")

    return valid_levels, center_ok
