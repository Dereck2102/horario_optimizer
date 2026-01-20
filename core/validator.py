import pandas as pd
from typing import Dict

class HorarioValidator:
    """
    Validador de horarios generados.
    
    Detecta conflictos y problemas en los horarios:
    - Conflictos de aulas (misma aula, mismo día, superposición horaria)
    - Conflictos de docentes (mismo docente, mismo día, superposición)
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_horario(self, horario: pd.DataFrame) -> Dict:
        """
        Valida un horario buscando conflictos.
        
        Args:
            horario: DataFrame con el horario a validar
            
        Returns:
            Dict con 'valid' (bool), 'errors' (list), 'warnings' (list)
        """
        self.errors = []
        self.warnings = []

        self._check_room_conflicts(horario)
        self._check_teacher_conflicts(horario)

        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def _check_room_conflicts(self, horario: pd.DataFrame):
        """Detecta conflictos de aulas (misma aula, mismo horario)."""
        for aula in horario['aula'].unique():
            aula_sched = horario[horario['aula'] == aula]
            for dia in aula_sched['dia'].unique():
                dia_sched = aula_sched[aula_sched['dia'] == dia]
                for i, r1 in dia_sched.iterrows():
                    for j, r2 in dia_sched.iterrows():
                        if i >= j:
                            continue
                        if self._times_overlap(r1['hora_inicio'], r1['hora_fin'], 
                                              r2['hora_inicio'], r2['hora_fin']):
                            self.errors.append(f"Conflicto aula {aula} - {dia}")

    def _check_teacher_conflicts(self, horario: pd.DataFrame):
        """Detecta conflictos de docentes (mismo docente, mismo horario)."""
        for doc in horario['docente'].unique():
            doc_sched = horario[horario['docente'] == doc]
            for dia in doc_sched['dia'].unique():
                dia_sched = doc_sched[doc_sched['dia'] == dia]
                for i, r1 in dia_sched.iterrows():
                    for j, r2 in dia_sched.iterrows():
                        if i >= j:
                            continue
                        if self._times_overlap(r1['hora_inicio'], r1['hora_fin'], 
                                              r2['hora_inicio'], r2['hora_fin']):
                            self.errors.append(f"Conflicto docente {doc} - {dia}")

    def _times_overlap(self, s1, e1, s2, e2) -> bool:
        """Verifica si dos rangos de tiempo se superponen."""
        return not (e1 <= s2 or e2 <= s1)
