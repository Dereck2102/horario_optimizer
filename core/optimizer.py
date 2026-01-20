from ortools.sat.python import cp_model
import pandas as pd
from typing import Dict, List, Tuple
from datetime import time

class HorarioOptimizer:
    """
    Motor de optimización de horarios usando Google OR-Tools CP-SAT Solver.
    
    Utiliza Constraint Programming para encontrar asignaciones óptimas de:
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
            'time_limit_seconds': 120,
            'default_room_capacity': 25,
            'require_lab_for_practices': True
        }
        # Lunes a Viernes: 07:00-20:00 (13 bloques de 60 min)
        self.timeslots_lv = list(range(13))
        # Sábado: 07:00-13:00 (6 bloques de 60 min)
        self.timeslots_sab = list(range(6))
        self.block_duration = 60
        self.variables = {}
        self.solution = None

    def optimize(self, clases: pd.DataFrame, aulas: pd.DataFrame, docentes: pd.DataFrame) -> Dict:
        """
        Ejecuta la optimización del horario.
        
        Args:
            clases: DataFrame con columnas [id, paralelo, materia, nivel, inscritos, duracion_bloques, tipo_espacio]
            aulas: DataFrame con columnas [id, nombre, tipo, capacidad, edificio]
            docentes: DataFrame con columnas [id, nombre, materias_puede_dictar]
            
        Returns:
            Dict con status, schedule (DataFrame), metrics y solver_stats
        """
        self._create_variables(clases, aulas, docentes)
        self._add_hard_constraints(clases, aulas, docentes)
        self._add_soft_constraints(clases, aulas, docentes)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.config['time_limit_seconds']
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

    def _create_variables(self, clases, aulas, docentes):
        """Crea las variables de decisión del modelo CP-SAT."""
        num_timeslots = len(self.timeslots_lv) * 5 + len(self.timeslots_sab)

        for idx, clase in clases.iterrows():
            cid = clase['id']
            dur = clase['duracion_bloques']
            self.variables[cid] = {
                'start': self.model.NewIntVar(0, num_timeslots - dur, f'start_{cid}'),
                'room': self.model.NewIntVar(0, len(aulas) - 1, f'room_{cid}'),
                'teacher': self.model.NewIntVar(0, len(docentes) - 1, f'teacher_{cid}'),
                'duration': dur
            }
            end_var = self.model.NewIntVar(0, num_timeslots, f'end_{cid}')
            self.model.Add(end_var == self.variables[cid]['start'] + dur)
            self.variables[cid]['end'] = end_var
            self.variables[cid]['interval'] = self.model.NewIntervalVar(
                self.variables[cid]['start'], dur, end_var, f'interval_{cid}'
            )

    def _add_hard_constraints(self, clases, aulas, docentes):
        """Añade restricciones duras que DEBEN cumplirse."""
        # No-overlap de aulas: misma aula no puede tener 2 clases simultáneas
        for idx_aula in range(len(aulas)):
            intervals = []
            for idx_clase, clase in clases.iterrows():
                is_in = self.model.NewBoolVar(f'c{clase["id"]}_r{idx_aula}')
                self.model.Add(self.variables[clase['id']]['room'] == idx_aula).OnlyEnforceIf(is_in)
                self.model.Add(self.variables[clase['id']]['room'] != idx_aula).OnlyEnforceIf(is_in.Not())
                intervals.append(self.model.NewOptionalIntervalVar(
                    self.variables[clase['id']]['start'], self.variables[clase['id']]['duration'],
                    self.variables[clase['id']]['end'], is_in, f'opt_c{clase["id"]}_r{idx_aula}'
                ))
            self.model.AddNoOverlap(intervals)

        # No-overlap de docentes: mismo docente no puede dar 2 clases simultáneas
        for idx_doc in range(len(docentes)):
            intervals = []
            for idx_clase, clase in clases.iterrows():
                is_t = self.model.NewBoolVar(f'c{clase["id"]}_t{idx_doc}')
                self.model.Add(self.variables[clase['id']]['teacher'] == idx_doc).OnlyEnforceIf(is_t)
                self.model.Add(self.variables[clase['id']]['teacher'] != idx_doc).OnlyEnforceIf(is_t.Not())
                intervals.append(self.model.NewOptionalIntervalVar(
                    self.variables[clase['id']]['start'], self.variables[clase['id']]['duration'],
                    self.variables[clase['id']]['end'], is_t, f'opt_c{clase["id"]}_t{idx_doc}'
                ))
            self.model.AddNoOverlap(intervals)

        # Restricción de capacidad: inscritos <= capacidad_aula
        for idx_c, clase in clases.iterrows():
            for idx_a, aula in aulas.iterrows():
                if aula['capacidad'] < clase['inscritos']:
                    self.model.Add(self.variables[clase['id']]['room'] != idx_a)

        # Restricción de tipo de espacio: materias de Lab requieren espacios tipo Lab
        if self.config['require_lab_for_practices']:
            for idx_c, clase in clases.iterrows():
                if clase.get('tipo_espacio') == 'Lab':
                    allowed = [i for i, a in aulas.iterrows() if a['tipo'] == 'Lab']
                    if allowed:
                        self.model.AddAllowedAssignments([self.variables[clase['id']]['room']], [(r,) for r in allowed])

        # Restricción de elegibilidad docente
        for idx_c, clase in clases.iterrows():
            eligible = [i for i, d in docentes.iterrows() if clase['materia'] in d['materias_puede_dictar']]
            if eligible:
                self.model.AddAllowedAssignments([self.variables[clase['id']]['teacher']], [(t,) for t in eligible])

    def _add_soft_constraints(self, clases, aulas, docentes):
        """Añade restricciones blandas a optimizar."""
        obj_terms = []
        w = self.config['weights']

        # Minimizar desperdicio de capacidad
        for idx_c, clase in clases.iterrows():
            waste = self.model.NewIntVar(0, 100, f'waste_{clase["id"]}')
            for idx_a, aula in aulas.iterrows():
                is_in = self.model.NewBoolVar(f'waste_c{clase["id"]}_a{idx_a}')
                self.model.Add(self.variables[clase['id']]['room'] == idx_a).OnlyEnforceIf(is_in)
                desperdicio = max(0, aula['capacidad'] - clase['inscritos'])
                self.model.Add(waste == desperdicio).OnlyEnforceIf(is_in)
            obj_terms.append(w['capacity_waste'] * waste)

        if obj_terms:
            self.model.Minimize(sum(obj_terms))

    def _extract_solution(self, solver, clases, aulas, docentes) -> pd.DataFrame:
        """Extrae la solución del solver y la convierte a DataFrame."""
        results = []
        for idx, clase in clases.iterrows():
            cid = clase['id']
            start = solver.Value(self.variables[cid]['start'])
            room_idx = solver.Value(self.variables[cid]['room'])
            teacher_idx = solver.Value(self.variables[cid]['teacher'])
            dia, hora_ini = self._slot_to_datetime(start)
            hora_fin = self._add_blocks(hora_ini, clase['duracion_bloques'])

            results.append({
                'clase_id': cid, 'materia': clase['materia'], 'paralelo': clase['paralelo'],
                'nivel': clase['nivel'], 'dia': dia, 'hora_inicio': hora_ini, 'hora_fin': hora_fin,
                'aula': aulas.iloc[room_idx]['nombre'], 'tipo_aula': aulas.iloc[room_idx]['tipo'],
                'edificio': aulas.iloc[room_idx]['edificio'], 'docente': docentes.iloc[teacher_idx]['nombre'],
                'inscritos': clase['inscritos'], 'capacidad_aula': aulas.iloc[room_idx]['capacidad']
            })
        return pd.DataFrame(results)

    def _slot_to_datetime(self, slot: int) -> Tuple[str, time]:
        """Convierte un timeslot numérico a (día, hora)."""
        slots_lv = len(self.timeslots_lv)
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

        if slot < slots_lv * 5:
            dia = dias[slot // slots_lv]
            hora = time(7 + (slot % slots_lv), 0)
        else:
            dia = 'Sábado'
            hora = time(7 + (slot - slots_lv * 5), 0)
        return dia, hora

    def _add_blocks(self, t: time, blocks: int) -> time:
        """Suma bloques de tiempo a una hora."""
        mins = t.hour * 60 + t.minute + (blocks * 60)
        return time(mins // 60, mins % 60)

    def _calculate_metrics(self, sol: pd.DataFrame) -> Dict:
        """Calcula métricas de calidad del horario generado."""
        return {
            'total_clases': len(sol),
            'aulas_utilizadas': sol['aula'].nunique(),
            'docentes_asignados': sol['docente'].nunique(),
            'promedio_ocupacion': (sol['inscritos'] / sol['capacidad_aula']).mean() * 100
        }

    def _get_status_message(self, status: int) -> str:
        """Convierte el status del solver a mensaje legible."""
        msgs = {
            cp_model.MODEL_INVALID: "Modelo inválido",
            cp_model.INFEASIBLE: "No hay solución factible",
            cp_model.UNKNOWN: "Timeout"
        }
        return msgs.get(status, f"Status: {status}")
