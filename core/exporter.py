import pandas as pd
from typing import Dict
import io

class HorarioExporter:
    """
    Exportador de horarios a diferentes formatos.
    
    Soporta:
    - Excel (.xlsx) con múltiples pestañas
    - CSV para importación a otros sistemas
    """
    
    def export_to_excel(self, horario: pd.DataFrame, filename: str = None) -> bytes:
        """
        Exporta el horario a Excel con múltiples pestañas.
        
        Genera pestañas:
        - Horario Completo: Toda la información
        - Por paralelo: Una pestaña por cada paralelo
        - Por docente: Una pestaña por cada docente
        
        Args:
            horario: DataFrame con el horario
            filename: No usado, se retorna bytes
            
        Returns:
            Contenido del archivo Excel como bytes
        """
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            horario.to_excel(writer, sheet_name='Horario Completo', index=False)

            for paralelo in horario['paralelo'].unique():
                paralelo_sched = horario[horario['paralelo'] == paralelo]
                paralelo_sched.to_excel(writer, sheet_name=f'{paralelo}'[:31], index=False)

            for docente in horario['docente'].unique():
                doc_sched = horario[horario['docente'] == docente]
                doc_sched.to_excel(writer, sheet_name=f'{docente}'[:31], index=False)

        output.seek(0)
        return output.getvalue()

    def export_to_csv(self, horario: pd.DataFrame) -> bytes:
        """
        Exporta el horario a CSV.
        
        Args:
            horario: DataFrame con el horario
            
        Returns:
            Contenido del archivo CSV como bytes
        """
        return horario.to_csv(index=False).encode('utf-8')
