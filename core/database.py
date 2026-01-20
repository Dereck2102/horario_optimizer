"""
Modulo de Base de Datos SQLite
Maneja todas las operaciones de persistencia
"""

import sqlite3
import json
import os
from typing import Dict, List, Optional
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'horarios.db')


@contextmanager
def get_connection():
    """Context manager para conexiones a la BD."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Inicializa las tablas de la base de datos."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de horarios publicados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS horarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                periodo TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        ''')
        
        # Tabla de clases
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paralelo TEXT NOT NULL,
                materia TEXT NOT NULL,
                nivel TEXT,
                inscritos INTEGER,
                duracion_bloques INTEGER DEFAULT 2,
                tipo_espacio TEXT DEFAULT 'Aula',
                periodo TEXT
            )
        ''')
        
        # Tabla de aulas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                tipo TEXT DEFAULT 'Aula',
                capacidad INTEGER,
                edificio TEXT
            )
        ''')
        
        # Tabla de docentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS docentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                materias TEXT,
                email TEXT
            )
        ''')
        
        # Tabla de disponibilidad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disponibilidad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                dia TEXT NOT NULL,
                hora_inicio INTEGER NOT NULL,
                hora_fin INTEGER NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        
        conn.commit()
        
        # Crear usuario admin por defecto si no existe
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                ('admin', 'admin123', 'Administrador', 'Admin')
            )
            cursor.execute(
                'INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                ('profesor1', 'prof123', 'Dr. Juan Perez', 'Profesional')
            )
            cursor.execute(
                'INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                ('estudiante1', 'est123', 'Maria Garcia', 'Estudiante')
            )
            conn.commit()


# =============================================================================
# USUARIOS
# =============================================================================

def get_user(username: str) -> Optional[Dict]:
    """Obtiene un usuario por username."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Autentica un usuario."""
    user = get_user(username)
    if user and user['password'] == password and user['active']:
        return user
    return None


def get_all_users() -> List[Dict]:
    """Obtiene todos los usuarios."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY username')
        return [dict(row) for row in cursor.fetchall()]


def create_user(username: str, password: str, name: str, role: str) -> bool:
    """Crea un nuevo usuario."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                (username, password, name, role)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def update_user_password(username: str, new_password: str) -> bool:
    """Actualiza la contrasena de un usuario."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
        conn.commit()
        return cursor.rowcount > 0


def toggle_user_active(username: str) -> bool:
    """Activa/desactiva un usuario."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET active = NOT active WHERE username = ?', (username,))
        conn.commit()
        return cursor.rowcount > 0


def delete_user(username: str) -> bool:
    """Elimina un usuario."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ? AND username != ?', (username, 'admin'))
        conn.commit()
        return cursor.rowcount > 0


# =============================================================================
# HORARIOS
# =============================================================================

def save_horario(periodo: str, data: List[Dict], created_by: str = None) -> bool:
    """Guarda un horario publicado."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO horarios (periodo, data, created_by) VALUES (?, ?, ?)',
                (periodo, json.dumps(data), created_by)
            )
            conn.commit()
            return True
    except:
        return False


def get_horario(periodo: str) -> Optional[List[Dict]]:
    """Obtiene un horario por periodo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM horarios WHERE periodo = ?', (periodo,))
        row = cursor.fetchone()
        if row:
            return json.loads(row['data'])
    return None


def get_all_horarios() -> Dict[str, List[Dict]]:
    """Obtiene todos los horarios."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT periodo, data FROM horarios ORDER BY created_at DESC')
        return {row['periodo']: json.loads(row['data']) for row in cursor.fetchall()}


def delete_horario(periodo: str) -> bool:
    """Elimina un horario."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM horarios WHERE periodo = ?', (periodo,))
        conn.commit()
        return cursor.rowcount > 0


# =============================================================================
# DISPONIBILIDAD
# =============================================================================

def save_disponibilidad(username: str, bloques: List[Dict]) -> bool:
    """Guarda la disponibilidad de un usuario."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM disponibilidad WHERE username = ?', (username,))
            for bloque in bloques:
                cursor.execute(
                    'INSERT INTO disponibilidad (username, dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)',
                    (username, bloque['dia'], bloque['hora_inicio'], bloque['hora_fin'])
                )
            conn.commit()
            return True
    except:
        return False


def get_disponibilidad(username: str) -> List[Dict]:
    """Obtiene la disponibilidad de un usuario."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT dia, hora_inicio, hora_fin FROM disponibilidad WHERE username = ?', (username,))
        return [dict(row) for row in cursor.fetchall()]


# =============================================================================
# ESTADISTICAS
# =============================================================================

def get_stats() -> Dict:
    """Obtiene estadisticas generales."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM users')
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'Profesional'")
        total_profs = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'Estudiante'")
        total_students = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM horarios')
        total_horarios = cursor.fetchone()['total']
        
        return {
            'users': total_users,
            'professors': total_profs,
            'students': total_students,
            'horarios': total_horarios
        }


# Inicializar DB al importar
init_db()
