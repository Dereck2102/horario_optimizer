import pandas as pd
import tabula
from typing import Dict, List
import re

class DataLoader:
    """
    Clase para cargar y generar datos para el optimizador de horarios.
    
    Soporta:
    - Lectura de PDFs del SIIU
    - Lectura de archivos Excel de oferta/demanda
    - Generación de catálogos por defecto para pruebas
    """
    
    def __init__(self):
        self.supported_formats = ['pdf', 'xlsx', 'csv']

    def load_horario_siiu_pdf(self, file_path: str) -> pd.DataFrame:
        """
        Lee un archivo PDF de horario del SIIU.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            DataFrame con las clases extraídas
        """
        try:
            tables = tabula.read_pdf(file_path, pages='all', multiple_tables=True)
            all_classes = []

            for table in tables:
                if table.empty:
                    continue
                classes = self._parse_horario_table(table)
                all_classes.extend(classes)

            return pd.DataFrame(all_classes)
        except Exception as e:
            raise ValueError(f"Error leyendo PDF: {e}")

    def _parse_horario_table(self, table: pd.DataFrame) -> List[Dict]:
        """Parsea una tabla de horario del SIIU."""
        classes = []
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

        for col_idx, dia in enumerate(dias):
            if dia not in table.columns:
                continue

            for hora_idx, cell_value in enumerate(table[dia]):
                if pd.isna(cell_value) or str(cell_value).strip() == '':
                    continue

                cell_str = str(cell_value).strip()
                lines = cell_str.split('\n')

                if len(lines) >= 2:
                    materia = lines[0].strip()
                    aula = lines[1].strip()

                    classes.append({
                        'materia': materia,
                        'dia': dia,
                        'hora_inicio': f"{7 + hora_idx}:00",
                        'aula': aula
                    })

        return classes

    def load_oferta_demanda_excel(self, file_path: str) -> pd.DataFrame:
        """
        Lee un archivo Excel de oferta/demanda del SIIU.
        
        Args:
            file_path: Ruta al archivo Excel
            
        Returns:
            DataFrame con columnas estándar incluyendo duracion_bloques y tipo_espacio inferidos
        """
        try:
            df = pd.read_excel(file_path)
            required_cols = ['Paralelo', 'Asignatura', 'Cupo registrado', 'Estudiantes registrados']

            if not all(col in df.columns for col in required_cols):
                df = pd.read_excel(file_path, skiprows=5)

            df = df.dropna(subset=['Paralelo', 'Asignatura'])
            df['id'] = range(len(df))

            df_clean = df[[col for col in df.columns if col in 
                          ['id', 'Paralelo', 'Asignatura', 'Nivel', 'Carrera', 
                           'Cupo registrado', 'Estudiantes registrados']]].copy()

            df_clean.columns = ['id', 'paralelo', 'materia', 'nivel', 'carrera', 
                               'cupo', 'inscritos'] if len(df_clean.columns) == 7 else df_clean.columns

            df_clean['duracion_bloques'] = df_clean['materia'].apply(self._infer_duration)
            df_clean['tipo_espacio'] = df_clean['materia'].apply(self._infer_space_type)

            return df_clean
        except Exception as e:
            raise ValueError(f"Error leyendo Excel: {e}")

    def _infer_duration(self, materia: str) -> int:
        """Infiere la duración en bloques según el nombre de la materia."""
        materia_lower = materia.lower()
        if any(word in materia_lower for word in ['programacion', 'lab', 'laboratorio']):
            return 2
        return 1

    def _infer_space_type(self, materia: str) -> str:
        """Infiere el tipo de espacio requerido según el nombre de la materia."""
        materia_lower = materia.lower()
        if any(word in materia_lower for word in ['programacion', 'lab', 'practica', 'estructura']):
            return 'Lab'
        return 'Aula'

    def load_disponibilidad_docente(self, file_path: str) -> pd.DataFrame:
        """Lee un archivo Excel de disponibilidad docente."""
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            raise ValueError(f"Error leyendo disponibilidad: {e}")

    def load_catalogo_aulas(self, file_path: str) -> pd.DataFrame:
        """Lee un archivo Excel con el catálogo de aulas."""
        try:
            df = pd.read_excel(file_path)
            df['id'] = range(len(df))

            if 'capacidad' not in df.columns:
                df['capacidad'] = 25
            if 'tipo' not in df.columns:
                df['tipo'] = df['nombre'].apply(lambda x: 'Lab' if 'LAB' in x.upper() else 'Aula')
            if 'edificio' not in df.columns:
                df['edificio'] = 'Principal'

            return df
        except Exception as e:
            raise ValueError(f"Error leyendo catálogo aulas: {e}")

    def create_default_aulas(self, count: int = 50) -> pd.DataFrame:
        """
        Genera un catálogo de aulas por defecto para pruebas.
        
        Args:
            count: Número de espacios a generar (12 serán labs, el resto aulas)
            
        Returns:
            DataFrame con columnas [id, nombre, tipo, capacidad, edificio]
        """
        aulas = []
        for i in range(1, count + 1):
            tipo = 'Lab' if i <= 12 else 'Aula'
            nombre = f'LAB{i}' if tipo == 'Lab' else f'A{i}-{(i-13)//10 + 1}'
            aulas.append({
                'id': i - 1,
                'nombre': nombre,
                'tipo': tipo,
                'capacidad': 25,
                'edificio': f'Edificio {(i-1)//15 + 1}'
            })
        return pd.DataFrame(aulas)

    def create_default_docentes(self, materias: List[str], count: int = 30) -> pd.DataFrame:
        """
        Genera un catálogo de docentes por defecto para pruebas.
        
        Args:
            materias: Lista de materias del semestre
            count: Número de docentes a generar
            
        Returns:
            DataFrame con columnas [id, nombre, materias_puede_dictar]
        """
        docentes = []
        for i in range(count):
            materias_asignadas = [materias[j] for j in range(len(materias)) if (i + j) % 3 == 0]
            docentes.append({
                'id': i,
                'nombre': f'Docente_{i+1}',
                'materias_puede_dictar': materias_asignadas
            })
        return pd.DataFrame(docentes)
