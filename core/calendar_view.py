"""
Modulo para visualizacion de horarios en formato calendario.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional

# Colores para diferentes materias
COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8B500', '#00CED1', '#FF69B4', '#32CD32', '#FFD700'
]


def create_calendar_view(horario: pd.DataFrame, filter_by: Optional[str] = None, 
                         filter_value: Optional[str] = None) -> go.Figure:
    """
    Crea una visualizacion tipo calendario del horario.
    
    Args:
        horario: DataFrame con el horario generado
        filter_by: Campo para filtrar ('paralelo', 'docente', 'aula')
        filter_value: Valor del filtro
        
    Returns:
        Figura de Plotly con el calendario
    """
    # Validar columnas requeridas
    required_cols = ['dia', 'hora_inicio', 'hora_fin', 'materia']
    missing = [c for c in required_cols if c not in horario.columns]
    
    if missing:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Faltan columnas: {', '.join(missing)}", 
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False, font_size=16
        )
        fig.update_layout(height=400)
        return fig
    
    df = horario.copy()
    
    # Aplicar filtro si existe
    if filter_by and filter_value and filter_by in df.columns:
        df = df[df[filter_by] == filter_value]
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay clases para mostrar", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font_size=20)
        fig.update_layout(height=400)
        return fig
    
    # Mapeo de dias a numeros (sin tildes para compatibilidad)
    dias_map = {
        'Lunes': 0, 'Martes': 1, 'Miercoles': 2, 'Miércoles': 2,
        'Jueves': 3, 'Viernes': 4, 'Sabado': 5, 'Sábado': 5
    }
    
    # Crear mapeo de colores por materia
    materias = df['materia'].unique()
    color_map = {m: COLORS[i % len(COLORS)] for i, m in enumerate(materias)}
    
    # Crear figura
    fig = go.Figure()
    
    for _, row in df.iterrows():
        dia_num = dias_map.get(row['dia'], 0)
        
        # Extraer hora de inicio y fin con manejo de errores
        if isinstance(row['hora_inicio'], str):
            hora_ini = int(row['hora_inicio'].split(':')[0])
        else:
            hora_ini = row['hora_inicio'].hour
            
        if isinstance(row['hora_fin'], str):
            hora_fin = int(row['hora_fin'].split(':')[0])
        else:
            hora_fin = row['hora_fin'].hour
        
        # Crear rectángulo para la clase
        fig.add_shape(
            type="rect",
            x0=dia_num - 0.4,
            x1=dia_num + 0.4,
            y0=hora_ini,
            y1=hora_fin,
            fillcolor=color_map[row['materia']],
            opacity=0.7,
            line=dict(color="white", width=2)
        )
        
        # Agregar texto
        texto = f"{row['materia'][:15]}<br>{row['paralelo']}<br>{row['aula']}"
        fig.add_annotation(
            x=dia_num,
            y=(hora_ini + hora_fin) / 2,
            text=texto,
            showarrow=False,
            font=dict(size=9, color="black"),
            align="center"
        )
    
    # Configurar ejes
    fig.update_layout(
        title="📅 Horario Semanal",
        xaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5],
            ticktext=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            range=[-0.5, 5.5],
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(7, 21)),
            ticktext=[f'{h}:00' for h in range(7, 21)],
            range=[20.5, 6.5],  # Invertido para que 7am esté arriba
            showgrid=True,
            gridcolor='lightgray'
        ),
        height=600,
        showlegend=False,
        plot_bgcolor='white'
    )
    
    return fig


def create_heatmap_ocupacion(horario: pd.DataFrame) -> go.Figure:
    """
    Crea un mapa de calor mostrando la ocupación por día/hora.
    
    Args:
        horario: DataFrame con el horario
        
    Returns:
        Figura de Plotly con el heatmap
    """
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    horas = list(range(7, 21))
    
    # Crear matriz de ocupación
    ocupacion = [[0 for _ in horas] for _ in dias]
    
    for _, row in horario.iterrows():
        dia_idx = dias.index(row['dia']) if row['dia'] in dias else -1
        if dia_idx < 0:
            continue
            
        if isinstance(row['hora_inicio'], str):
            hora_ini = int(row['hora_inicio'].split(':')[0])
        else:
            hora_ini = row['hora_inicio'].hour
            
        if isinstance(row['hora_fin'], str):
            hora_fin = int(row['hora_fin'].split(':')[0])
        else:
            hora_fin = row['hora_fin'].hour
        
        for h in range(hora_ini, hora_fin):
            if 7 <= h < 21:
                ocupacion[dia_idx][h - 7] += 1
    
    fig = go.Figure(data=go.Heatmap(
        z=ocupacion,
        x=[f'{h}:00' for h in horas],
        y=dias,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title='Clases')
    ))
    
    fig.update_layout(
        title="📊 Mapa de Ocupación",
        xaxis_title="Hora",
        yaxis_title="Día",
        height=400
    )
    
    return fig


def get_schedule_stats(horario: pd.DataFrame) -> dict:
    """
    Calcula estadísticas del horario.
    
    Args:
        horario: DataFrame con el horario
        
    Returns:
        Diccionario con estadísticas
    """
    stats = {
        'total_clases': len(horario),
        'total_horas': 0,
        'aulas_utilizadas': horario['aula'].nunique(),
        'docentes_asignados': horario['docente'].nunique(),
        'clases_por_dia': {},
        'carga_por_docente': {},
        'ocupacion_promedio': 0
    }
    
    # Calcular horas totales
    for _, row in horario.iterrows():
        if isinstance(row['hora_inicio'], str):
            h_ini = int(row['hora_inicio'].split(':')[0])
        else:
            h_ini = row['hora_inicio'].hour
        if isinstance(row['hora_fin'], str):
            h_fin = int(row['hora_fin'].split(':')[0])
        else:
            h_fin = row['hora_fin'].hour
        stats['total_horas'] += (h_fin - h_ini)
    
    # Clases por día
    stats['clases_por_dia'] = horario.groupby('dia').size().to_dict()
    
    # Carga por docente
    stats['carga_por_docente'] = horario.groupby('docente').size().to_dict()
    
    # Ocupación promedio
    if 'inscritos' in horario.columns and 'capacidad_aula' in horario.columns:
        stats['ocupacion_promedio'] = (horario['inscritos'] / horario['capacidad_aula']).mean() * 100
    
    return stats
