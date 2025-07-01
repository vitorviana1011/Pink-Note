import os
import sqlite3
from datetime import datetime

class DatabaseInitializer:
    """Classe responsável por inicializar o banco de dados SQLite."""
    
    def __init__(self, db_path):
        """Inicializa com o caminho do arquivo do banco de dados."""
        self.db_path = db_path
        self.connection = None
    
    def initialize_database(self):
        """Cria o banco de dados e as tabelas se não existirem."""
        # Garante que o diretório exista
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Conecta ao banco de dados (cria se não existir)
        self.connection = sqlite3.connect(self.db_path)
        
        # Habilita chaves estrangeiras
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Cria tabelas
        self._create_tables()
        
        # Inicializa com dados padrão se necessário
        self._initialize_default_data()
        
        return self.connection
    
    def _create_tables(self):
        """Cria todas as tabelas necessárias."""
        cursor = self.connection.cursor()
        
        # Cria tabela de pastas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            path TEXT NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        )
        """)
        
        # Cria tabela de notas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL,
            modified_at TEXT NOT NULL,
            folder_id INTEGER NOT NULL,
            FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
        )
        """)
        
        # Cria tabela de anexos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """)
        
        # Cria tabela de eventos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
        """)
        
        self.connection.commit()
    
    def _initialize_default_data(self):
        """Inicializa o banco de dados com dados padrão se estiver vazio."""
        cursor = self.connection.cursor()
        
        # Verifica se a tabela de pastas está vazia
        cursor.execute("SELECT COUNT(*) FROM folders")
        folder_count = cursor.fetchone()[0]
        
        if folder_count == 0:
            # Cria a pasta padrão 'Geral'
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO folders (name, parent_id, path) VALUES (?, ?, ?)",
                ("Geral", None, "/Geral")
            )
            
            # Cria uma nota de boas-vindas na pasta Geral
            cursor.execute(
                "INSERT INTO notes (title, content, created_at, modified_at, folder_id) VALUES (?, ?, ?, ?, ?)",
                (
                    "Bem-vindo ao NotePad",
                    "Bem-vindo ao seu novo aplicativo de notas! Este é um exemplo de nota.",
                    now,
                    now,
                    1  # ID da pasta Geral
                )
            )
            
            self.connection.commit()