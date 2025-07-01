from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTabWidget, QPushButton, QToolBar, 
                             QAction, QStatusBar, QMessageBox, QMenu, QDialog,
                             QLabel, QLineEdit, QFormLayout, QDialogButtonBox,
                             QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence
import os
import sys

from presentation.components import (
    NoteListComponent, FolderTreeComponent, NoteEditorComponent,
    CalendarComponent, SearchComponent
)
from shared.di import Container
from shared.config import Config
from shared.utils.logger import Logger
from shared.constants import APP_NAME, APP_VERSION

class SettingsDialog(QDialog):
    """Diálogo de configurações da aplicação."""
    
    def __init__(self, parent=None, config=None):
        """Inicializa o diálogo.
        
        Args:
            parent: O widget pai
            config: A configuração da aplicação
        """
        super().__init__(parent)
        
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """Inicializa os componentes da interface."""
        # Define propriedades do diálogo
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(400)
        
        # Cria layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Entrada do caminho do banco de dados
        self.db_path_input = QLineEdit(self)
        self.db_path_input.setText(self.config.get('database_path'))
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_input)
        db_path_btn = QPushButton("Procurar", self)
        db_path_btn.clicked.connect(self._browse_db_path)
        db_path_layout.addWidget(db_path_btn)
        form_layout.addRow("Caminho do Banco de Dados:", db_path_layout)
        
        # Entrada do caminho de armazenamento
        self.storage_path_input = QLineEdit(self)
        self.storage_path_input.setText(self.config.get('storage_path'))
        storage_path_layout = QHBoxLayout()
        storage_path_layout.addWidget(self.storage_path_input)
        storage_path_btn = QPushButton("Procurar", self)
        storage_path_btn.clicked.connect(self._browse_storage_path)
        storage_path_layout.addWidget(storage_path_btn)
        form_layout.addRow("Caminho de Armazenamento:", storage_path_layout)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _browse_db_path(self):
        """Selecionar caminho do banco de dados."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Selecionar arquivo do banco de dados",
            self.db_path_input.text(),
            "Banco de Dados SQLite (*.db);;Todos os Arquivos (*.*)"
        )
        
        if path:
            self.db_path_input.setText(path)
    
    def _browse_storage_path(self):
        """Selecionar caminho de armazenamento."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Selecionar diretório de armazenamento",
            self.storage_path_input.text()
        )
        
        if path:
            self.storage_path_input.setText(path)
    
    def get_settings(self) -> Dict[str, Any]:
        """Obtém as configurações dos campos do diálogo.
        
        Returns:
            Um dicionário com as configurações
        """
        return {
            'database_path': self.db_path_input.text(),
            'storage_path': self.storage_path_input.text()
        }

class MainWindow(QMainWindow):
    """Janela principal da aplicação."""
    
    def __init__(self):
        """Inicializa a janela principal."""
        super().__init__()
        
        # Inicializa o logger
        self.logger = Logger.get_instance()
        self.logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        
        # Carrega a configuração
        self.config = Config()
        self.config.load()
        
        # Inicializa o container de dependências
        self.container = Container(self.config.get_all())
        
        # Inicializa os controladores
        self.controllers = {
            'note_controller': self.container.get_note_controller(),
            'folder_controller': self.container.get_folder_controller(),
            'event_controller': self.container.get_event_controller(),
            'attachment_controller': self.container.get_attachment_controller()
        }
        
        # Inicializa a UI
        self.init_ui()
        
        # Conecta os sinais
        self.connect_signals()
        
        # Atualiza os componentes
        self.refresh_all()
    
    def init_ui(self):
        """Inicializa os componentes da interface."""
        # Define propriedades da janela
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1000, 600)
        
        # Cria widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Cria layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Cria splitter principal
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Cria painel esquerdo (pastas e notas)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Cria árvore de pastas
        self.folder_tree = FolderTreeComponent(controllers=self.controllers)
        left_layout.addWidget(self.folder_tree)
        
        # Cria lista de notas
        self.note_list = NoteListComponent(controllers=self.controllers)
        left_layout.addWidget(self.note_list)
        
        # Adiciona painel esquerdo ao splitter
        self.main_splitter.addWidget(left_panel)
        
        # Cria painel direito (abas)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Cria widget de abas
        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)
        
        # Cria aba de edição de notas
        self.note_editor = NoteEditorComponent(controllers=self.controllers)
        self.tabs.addTab(self.note_editor, "Nota")
        
        # Cria aba de calendário
        self.calendar = CalendarComponent(controllers=self.controllers)
        self.tabs.addTab(self.calendar, "Calendário")
        
        # Cria aba de busca
        self.search = SearchComponent(controllers=self.controllers)
        self.tabs.addTab(self.search, "Busca")
        
        # Adiciona painel direito ao splitter
        self.main_splitter.addWidget(right_panel)
        
        # Define tamanhos dos painéis no splitter
        self.main_splitter.setSizes([300, 700])
        
        # Cria barra de ferramentas
        self.create_toolbar()
        
        # Cria barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")
    
    def create_toolbar(self):
        """Cria a barra de ferramentas da aplicação."""
        # Cria barra de ferramentas
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Ação de nova nota
        new_note_action = QAction("Nova Nota", self)
        new_note_action.setShortcut(QKeySequence.New)
        new_note_action.triggered.connect(self.new_note)
        toolbar.addAction(new_note_action)
        
        # Ação de nova pasta
        new_folder_action = QAction("Nova Pasta", self)
        new_folder_action.triggered.connect(self.new_folder)
        toolbar.addAction(new_folder_action)
        
        toolbar.addSeparator()
        
        # Ação de novo evento
        new_event_action = QAction("Novo Evento", self)
        new_event_action.triggered.connect(self.new_event)
        toolbar.addAction(new_event_action)
        
        toolbar.addSeparator()
        
        # Ação de configurações
        settings_action = QAction("Configurações", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
        # Ação de sobre
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def connect_signals(self):
        """Conecta os sinais dos componentes."""
        # Conecta sinais da árvore de pastas
        self.folder_tree.folder_selected.connect(self.on_folder_selected)
        
        # Conecta sinais da lista de notas
        self.note_list.note_selected.connect(self.on_note_selected)
        
        # Conecta sinais do editor de notas
        self.note_editor.note_saved.connect(self.on_note_saved)
        self.note_editor.note_deleted.connect(self.on_note_deleted)
        
        # Conecta sinais de busca
        self.search.note_selected.connect(self.on_search_note_selected)
    
    def refresh_all(self):
        """Atualiza todos os componentes."""
        self.folder_tree.refresh()
        self.calendar.refresh()
    
    def on_folder_selected(self, folder_id):
        """Manipula a seleção de pastas.
        
        Args:
            folder_id: O ID da pasta selecionada
        """
        # Atualiza lista de notas
        self.note_list.set_folder(folder_id)
        
        # Atualiza editor de notas
        self.note_editor.set_folder(folder_id)
        
        # Atualiza status
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller:
            folder = folder_controller.get_folder_by_id(folder_id)
            if folder:
                self.status_bar.showMessage(f"Pasta: {folder['name']}")
    
    def on_note_selected(self, note_id):
        """Manipula a seleção de notas.
        
        Args:
            note_id: O ID da nota selecionada
        """
        # Altera para aba de edição de notas
        self.tabs.setCurrentWidget(self.note_editor)
        
        # Carrega nota no editor
        self.note_editor.load_note(note_id)
        
        # Atualiza status
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            note = note_controller.get_note_by_id(note_id)
            if note:
                self.status_bar.showMessage(f"Nota: {note['title']}")
    
    def on_search_note_selected(self, note_id):
        """Manipula a seleção de notas nos resultados da busca.
        
        Args:
            note_id: O ID da nota selecionada
        """
        # Obtém a nota
        note_controller = self.controllers.get('note_controller')
        if not note_controller:
            return
        
        note = note_controller.get_note_by_id(note_id)
        if not note:
            return
        
        # Seleciona a pasta
        folder_id = note.get('folder_id')
        if folder_id:
            self.folder_tree.select_folder(folder_id)
        
        # Seleciona a nota
        self.note_list.select_note(note_id)
    
    def on_note_saved(self, note_id):
        """Manipula o salvamento de notas.
        
        Args:
            note_id: O ID da nota salva
        """
        # Atualiza lista de notas
        self.note_list.refresh()
        
        # Atualiza status
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            note = note_controller.get_note_by_id(note_id)
            if note:
                self.status_bar.showMessage(f"Nota salva: {note['title']}")
    
    def on_note_deleted(self, note_id):
        """Manipula a exclusão de notas.
        
        Args:
            note_id: O ID da nota excluída
        """
        # Atualiza lista de notas
        self.note_list.refresh()
        
        # Atualiza status
        self.status_bar.showMessage("Nota excluída")
    
    def new_note(self):
        """Cria uma nova nota."""
        # Verifica se uma pasta está selecionada
        if self.folder_tree.current_folder_id is None:
            QMessageBox.warning(
                self,
                "Nenhuma Pasta Selecionada",
                "Por favor, selecione uma pasta antes de criar uma nova nota."
            )
            return
        
        # Altera para aba de edição de notas
        self.tabs.setCurrentWidget(self.note_editor)
        
        # Cria nova nota no editor
        self.note_editor.new_note()
    
    def new_folder(self):
        """Cria uma nova pasta."""
        # Obtém ID da pasta pai
        parent_id = self.folder_tree.current_folder_id
        
        # Obtém nome da pasta
        name, ok = QInputDialog.getText(self, "Nova Pasta", "Nome da pasta:")
        if ok and name:
            folder_controller = self.controllers.get('folder_controller')
            if folder_controller:
                folder = folder_controller.create_folder(name, parent_id)
                if folder:
                    # Atualiza árvore de pastas
                    self.folder_tree.refresh()
                    
                    # Atualiza status
                    self.status_bar.showMessage(f"Pasta criada: {name}")
    
    def new_event(self):
        """Cria um novo evento."""
        # Altera para aba de calendário
        self.tabs.setCurrentWidget(self.calendar)
        
        # Aciona adição de evento
        self.calendar._add_event()
    
    def show_settings(self):
        """Exibe o diálogo de configurações."""
        dialog = SettingsDialog(self, self.config)
        if dialog.exec_() == QDialog.Accepted:
            # Obtém configurações
            settings = dialog.get_settings()
            
            # Atualiza configuração
            for key, value in settings.items():
                self.config.set(key, value)
            
            # Salva configuração
            self.config.save()
            
            # Exibe mensagem de reinício
            QMessageBox.information(
                self,
                "Configurações Atualizadas",
                "As configurações foram atualizadas. Algumas mudanças podem exigir um reinício para terem efeito."
            )
    
    def show_about(self):
        """Exibe o diálogo sobre."""
        QMessageBox.about(
            self,
            f"Sobre {APP_NAME}",
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            "<p>Uma aplicação de anotação com gerenciamento de calendário e eventos.</p>"
            "<p>Desenvolvido para o projeto da disciplina de Engenharia de Software.</p>"
        )
    
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela.
        
        Args:
            event: O evento de fechamento
        """
        # Registra saída da aplicação
        self.logger.info(f"Exiting {APP_NAME} v{APP_VERSION}")
        
        # Aceita o evento
        event.accept()