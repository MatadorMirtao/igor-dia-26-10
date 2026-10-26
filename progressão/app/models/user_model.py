import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'escoteiros.db')

# --- GERENCIADOR DE CONEXÃO COM CONTEXT MANAGER ---
class GerenciadorDB:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()


# --- CLASSE DE ENTIDADE (ACTIVE RECORD) ---
class User:
    def __init__(self, username, password_hash=None, id=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    # 1. Configuração do Banco
    @classmethod
    def criar_tabela(cls):
        """Método da classe responsável por criar a tabela no banco."""
        with GerenciadorDB() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')

    # 2. Comportamento do Objeto
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def salvar(self):
        """Método do objeto: insere no banco se for novo, atualiza se já existir."""
        with GerenciadorDB() as cursor:
            if self.id is None:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (self.username, self.password_hash)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE users SET username = ?, password_hash = ? WHERE id = ?",
                    (self.username, self.password_hash, self.id)
                )

    # 3. Consultas (Buscas no Banco)
    @classmethod
    def buscar_por_username(cls, username):
        with GerenciadorDB() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return cls(id=row['id'], username=row['username'], password_hash=row['password_hash'])
            return None

    @classmethod
    def listar_todos(cls):
        """Método da classe: Busca todos os registros e os transforma em objetos."""
        with GerenciadorDB() as cursor:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            # Retorna uma lista contendo instâncias da classe User
            return [cls(id=row['id'], username=row['username'], password_hash=row['password_hash']) for row in rows]