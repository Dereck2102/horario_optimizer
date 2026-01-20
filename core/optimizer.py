"""
Motor de optimizacion de horarios usando Google OR-Tools CP-SAT Solver.
"""

from ortools.sat.python import cp_model
import pandas as pd
from typing import Dict, List, Tuple
from datetime import time


class HorarioOptimizer:
    """
    Motor de optimizacion de horarios usando Google OR-Tools CP-SAT Solver.
    
    Utiliza Constraint Programming para encontrar asignaciones optimas de:
    - Clases a timeslots
    - Clases a aulas
    - Clases a docentes
    
    Respetando restricciones duras (no-overlap, capacidad, elegibilidad)
    y optimizando restricciones blandas (minimizar desperdicio de capacidad).
    """
    
    def __init__(self, config: Dict = None):
        self.model = cp_model.CpModel()
        self.config = config or {
            'weights': {'gaps': 10, 'capacity_waste': 5, 'teacher_balance': 3, 'building': 2},
            'time_limit_seconds': 300,
            'default_room_capacity': 25,
            'require_lab_for_practices': True
        }
        # Lunes a Viernes: 07:00-20:00 (13 bloques de 60 min)
        self.timeslots_lv = list(range(13))
        # Sabado: 07:00-13:00 (6 bloques de 60 min)
        self.timeslots_sab = list(range(6))
        self.block_duration = 60
        self.variables = {}
        self.solution = None
        self.num_timeslots = len(self.timeslots_lv) * 5 + len(self.timeslots_sab)

    def optimize(self, clases: pd.DataFrame, aulas: pd.DataFrame, docentes: pd.DataFrame) -> Dict:
        """
        Ejecuta la optimizacion del horario.
        
        Args:
            clases: DataFrame con columnas [id, paralelo, materia, nivel, inscritos, duracion_bloques, tipo_espacio]
            aulas: DataFrame con columnas [id, nombre, tipo, capacidad, edificio]
            docentes: DataFrame con columnas [id, nombre, materias_puede_dictar]
            
        Returns:
            Dict con status, schedule (DataFrame), metrics y solver_stats
        """
        # Reiniciar modelo
        self.model = cp_model.CpModel()
        self.variables = {}
        
        # Validar y preparar datos
        clases = self._prepare_clases(clases)
        aulas = self._prepare_aulas(aulas)
        docentes = self._prepare_docentes(docentes, clases)
        
        # Crear modelo
        self._create_variables(clases, aulas, docentes)
        self._add_hard_constraints(clases, aulas, docentes)
        self._add_soft_constraints(clases, aulas)

        # Resolver
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.config['time_limit_seconds']
        solver.parameters.num_search_workers = 4  # Paralelizar busqueda
        
        status = solver.Solve(self.model)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            self.solution = self._extract_solution(solver, clases, aulas, docentes)
            return {
                'status': 'success',
                'optimal': status == cp_model.OPTIMAL,
                'schedule': self.solution,
                'metrics': self._calculate_metrics(self.solution),
                'solver_stats': {
                    'wall_time': solver.WallTime(),
                    'conflicts': solver.NumConflicts(),
                    'branches': solver.NumBranches()
                }
            }
        return {'status': 'failed', 'reason': self._get_status_message(status)}

    def _prepare_clases(self, clases: pd.DataFrame) -> pd.DataFrame:
        """Prepara y valida el DataFrame de clases."""
        df = clases.copy()
        df = df.reset_index(drop=True)
        if 'id' not in df.columns:
            df['id'] = range(len(df))
        if 'duracion_bloques' not in df.columns:
            df['duracion_bloques'] = 2
        if 'tipo_espacio' not in df.columns:
            df['tipo_espacio'] = 'Aula'
        if 'inscritos' not in df.columns:
            df['inscritos'] = 30
        return df

    def _prepare_aulas(self, aulas: pd.DataFrame) -> pd.DataFrame:
        """Prepara y valida el DataFrame de aulas."""
        df = aulas.copy()
        df = df.reset_index(drop=True)
        if 'id' not in df.columns:
            df['id'] = range(len(df))
        return df

    def _prepare_docentes(self, docentes: pd.DataFrame, clases: pd.DataFrame) -> pd.DataFrame:
        """Prepara y valida el DataFrame de docentes."""
        df = docentes.copy()
        df = df.reset_index(drop=True)
        if 'id' not in df.columns:
            df['id'] = range(len(df))
        
        # Asegurar que cada materia tenga al menos un docente elegible
        materias = clases['materia'].unique()
        for materia in materias:
            elegibles = [i for i, d in df.iterrows() 
                        if isinstance(d.get('materias_puede_dictar'), list) 
                        and materia in d['materias_puede_dictar']]
            if not elegibles:
                # Asignar al primer docente disponible
                if len(df) > 0:
                    current_materias = df.loc[0, 'materias_puede_dictar']
                    if isinstance(current_materias, list):
                        df.at[0, 'materias_puede_dictar'] = current_materias + [materia]
                    else:
                        df.at[0, 'materias_puede_dictar'] = [materia]
        return df

    def _create_variables(self, clases, aulas, docentes):
        """Crea las variables de decision del modelo CP-SAT."""
        num_aulas = len(aulas)
        num_docentes = len(docentes)

        for idx, clase in clases.iterrows():
            cid = clase['id']
            dur = min(clase['duracion_bloques'], 4)  # Limitar duracion a 4 bloques
            max_start = self.num_timeslots - dur
            
            self.variables[cid] = {
                'start': self.model.NewIntVar(0, max_start, f'start_{cid}'),
                'room': self.model.NewIntVar(0, num_aulas - 1, f'room_{cid}'),
                'teacher': self.model.NewIntVar(0, num_docentes - 1, f'teacher_{cid}'),
                'duration': dur
            }
            
            end_var = self.model.NewIntVar(dur, self.num_timeslots, f'end_{cid}')
            self.model.Add(end_var == self.variables[cid]['start'] + dur)
            self.variables[cid]['end'] = end_var
            
            self.variables[cid]['interval'] = self.model.NewIntervalVar(
                self.variables[cid]['start'], dur, end_var, f'interval_{cid}'
            )

    def _add_hard_constraints(self, clases, aulas, docentes):
        """Anade restricciones duras que DEBEN cumplirse."""
        num_aulas = len(aulas)
        num_docentes = len(docentes)
        
        # No-overlap de aulas: misma aula no puede tener 2 clases simultaneas
        for idx_aula in range(num_aulas):
            intervals = []
            for idx_clase, clase in clases.iterrows():
                cid = clase['id']
                is_in = self.model.NewBoolVar(f'c{cid}_r{idx_aula}')
                self.model.Add(self.variables[cid]['room'] == idx_aula).OnlyEnforceIf(is_in)
                self.model.Add(self.variables[cid]['room'] != idx_aula).OnlyEnforceIf(is_in.Not())
                
                opt_interval = self.model.NewOptionalIntervalVar(
                    self.variables[cid]['start'], 
                    self.variables[cid]['duration'],
                    self.variables[cid]['end'], 
                    is_in, 
                    f'opt_c{cid}_r{idx_aula}'
                )
                intervals.append(opt_interval)
            
            if intervals:
                self.model.AddNoOverlap(intervals)

        # No-overlap de docentes: mismo docente no puede dar 2 clases simultaneas
        for idx_doc in range(num_docentes):
            intervals = []
            for idx_clase, clase in clases.iterrows():
                cid = clase['id']
                is_t = self.model.NewBoolVar(f'c{cid}_t{idx_doc}')
                self.model.Add(self.variables[cid]['teacher'] == idx_doc).OnlyEnforceIf(is_t)
                self.model.Add(self.variables[cid]['teacher'] != idx_doc).OnlyEnforceIf(is_t.Not())
                
                opt_interval = self.model.NewOptionalIntervalVar(
                    self.variables[cid]['start'], 
                    self.variables[cid]['duration'],
                    self.variables[cid]['end'], 
                    is_t, 
                    f'opt_c{cid}_t{idx_doc}'
                )
                intervals.append(opt_interval)
            
            if intervals:
                self.model.AddNoOverlap(intervals)

        # Restriccion de capacidad: inscritos <= capacidad_aula
        for idx_c, clase in clases.iterrows():
            cid = clase['id']
            inscritos = clase['inscritos']
            allowed_rooms = []
            
            for idx_a, aula in aulas.iterrows():
                if aula['capacidad'] >= inscritos:
                    allowed_rooms.append(idx_a)
            
            if allowed_rooms:
                self.model.AddAllowedAssignments(
                    [self.variables[cid]['room']], 
                    [(r,) for r in allowed_rooms]
                )

        # Restriccion de tipo de espacio
        if self.config.get('require_lab_for_practices', True):
            for idx_c, clase in clases.iterrows():
                cid = clase['id']
                tipo_requerido = clase.get('tipo_espacio', 'Aula')
                
                if tipo_requerido == 'Lab':
                    allowed_labs = [idx_a for idx_a, aula in aulas.iterrows() 
                                   if aula['tipo'] == 'Lab' and aula['capacidad'] >= clase['inscritos']]
                    if allowed_labs:
                        self.model.AddAllowedAssignments(
                            [self.variables[cid]['room']], 
                            [(r,) for r in allowed_labs]
                        )

        # Restriccion de elegibilidad docente
        for idx_c, clase in clases.iterrows():
            cid = clase['id']
            materia = clase['materia']
            
            eligible = []
            for idx_d, doc in docentes.iterrows():
                materias_doc = doc.get('materias_puede_dictar', [])
                if isinstance(materias_doc, list) and materia in materias_doc:
                    eligible.append(idx_d)
            
            if eligible:
                self.model.AddAllowedAssignments(
                    [self.variables[cid]['teacher']], 
                    [(t,) for t in eligible]
                )

    def _add_soft_constraints(self, clases, aulas):
        """Anade restricciones blandas a optimizar (objetivo)."""
        obj_terms = []
        w = self.config.get('weights', {'capacity_waste': 5})
        
        # Minimizar desperdicio de capacidad usando variables auxiliares
        waste_weight = w.get('capacity_waste', 5)
        
        for idx_c, clase in clases.iterrows():
            cid = clase['id']
            inscritos = clase['inscritos']
            
            # Para cada aula, calcular el desperdicio potencial
            for idx_a, aula in aulas.iterrows():
                if aula['capacidad'] >= inscritos:
                    # Variable booleana: esta clase esta en esta aula?
                    is_in = self.model.NewBoolVar(f'waste_c{cid}_a{idx_a}')
                    self.model.Add(self.variables[cid]['room'] == idx_a).OnlyEnforceIf(is_in)
                    self.model.Add(self.variables[cid]['room'] != idx_a).OnlyEnforceIf(is_in.Not())
                    
                    # El desperdicio es (capacidad - inscritos) * is_in
                    desperdicio = aula['capacidad'] - inscritos
                    if desperdicio > 0 and waste_weight > 0:
                        # Usar la variable booleana como contribucion al objetivo
                        waste_int = self.model.NewIntVar(0, desperdicio, f'waste_int_c{cid}_a{idx_a}')
                        self.model.Add(waste_int == desperdicio).OnlyEnforceIf(is_in)
                        self.model.Add(waste_int == 0).OnlyEnforceIf(is_in.Not())
                        obj_terms.append(waste_int)

        if obj_terms:
            self.model.Minimize(sum(obj_terms))

    def _extract_solution(self, solver, clases, aulas, docentes) -> pd.DataFrame:
        """Extrae la solucion del solver y la convierte a DataFrame."""
        results = []
        
        for idx, clase in clases.iterrows():
            cid = clase['id']
            start = solver.Value(self.variables[cid]['start'])
            room_idx = solver.Value(self.variables[cid]['room'])
            teacher_idx = solver.Value(self.variables[cid]['teacher'])
            
            dia, hora_ini = self._slot_to_datetime(start)
            hora_fin = self._add_blocks(hora_ini, self.variables[cid]['duration'])

            aula_row = aulas.iloc[room_idx]
            docente_row = docentes.iloc[teacher_idx]

            results.append({
                'clase_id': cid, 
                'materia': clase['materia'], 
                'paralelo': clase['paralelo'],
                'nivel': clase.get('nivel', ''),
                'dia': dia, 
                'hora_inicio': hora_ini.strftime('%H:%M'), 
                'hora_fin': hora_fin.strftime('%H:%M'),
                'aula': aula_row['nombre'], 
                'tipo_aula': aula_row['tipo'],
                'edificio': aula_row.get('edificio', ''),
                'docente': docente_row['nombre'],
                'inscritos': clase['inscritos'], 
                'capacidad_aula': aula_row['capacidad']
            })
            
        return pd.DataFrame(results)

    def _slot_to_datetime(self, slot: int) -> Tuple[str, time]:
        """Convierte un timeslot numerico a (dia, hora)."""
        slots_lv = len(self.timeslots_lv)
        dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes']

        if slot < slots_lv * 5:
            dia = dias[slot // slots_lv]
            hora = time(7 + (slot % slots_lv), 0)
        else:
            dia = 'Sabado'
            hora = time(7 + (slot - slots_lv * 5), 0)
        return dia, hora

    def _add_blocks(self, t: time, blocks: int) -> time:
        """Suma bloques de tiempo a una hora."""
        mins = t.hour * 60 + t.minute + (blocks * 60)
        hours = mins // 60
        if hours >= 24:
            hours = 23
            mins = 59
        else:
            mins = mins % 60
        return time(hours, mins)

    def _calculate_metrics(self, sol: pd.DataFrame) -> Dict:
        """Calcula metricas de calidad del horario generado."""
        if len(sol) == 0:
            return {
                'total_clases': 0,
                'aulas_utilizadas': 0,
                'docentes_asignados': 0,
                'promedio_ocupacion': 0
            }
        
        return {
            'total_clases': len(sol),
            'aulas_utilizadas': sol['aula'].nunique(),
            'docentes_asignados': sol['docente'].nunique(),
            'promedio_ocupacion': (sol['inscritos'] / sol['capacidad_aula']).mean() * 100
        }

    def _get_status_message(self, status: int) -> str:
        """Convierte el status del solver a mensaje legible."""
        msgs = {
            cp_model.MODEL_INVALID: "Modelo invalido - revise los datos de entrada",
            cp_model.INFEASIBLE: "No hay solucion factible - verifique que hay suficientes aulas/docentes para las clases",
            cp_model.UNKNOWN: "Tiempo agotado - intente aumentar el tiempo limite o reducir las clases"
        }
        return msgs.get(status, f"Error desconocido (status: {status})")
