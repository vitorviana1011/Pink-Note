from typing import List, Dict, Any, Optional, Callable
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

from presentation.components.base_component import BaseComponent
from shared.utils.string_utils import StringUtils

class NoteListComponent(BaseComponent):
    """Componente para exibir e gerenciar uma lista de notas."""
    
    # Define sinais
    note_selected = pyqtSignal(int)  # Emitido quando uma nota é selecionada (note_id)
    note_deleted = pyqtSignal(int)   # Emitido quando uma nota é excluída (note_id)
    note_moved = pyqtSignal(int, int)  # Emitido quando uma nota é movida (note_id, target_folder_id)
    
    def __init__(self, parent=None, controllers=None):
        """Inicializa o componente.
        
        Args:
            parent: O widget pai
            controllers: Um dicionário de controladores
        """
        super().__init__(parent, controllers)
        
        # ID da pasta atual
        self.current_folder_id = None
        
        # Dados das notas
        self.notes = []
    
    def _init_ui(self):
        """Inicializa os componentes da interface."""
        # Cria o widget de lista
        self.list_widget = QListWidget(self)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Configura o layout
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
    
    def _connect_signals(self):
        """Conecta sinais e slots."""
        # Conecta sinais do widget de lista
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def set_folder(self, folder_id: int):
        """Define a pasta atual e carrega suas notas.
        
        Args:
            folder_id: O ID da pasta
        """
        self.current_folder_id = folder_id
        self.refresh()
    
    def refresh(self):
        """Atualiza a lista de notas."""
        if self.current_folder_id is None:
            return
        
        # Limpa a lista
        self.list_widget.clear()
        
        # Obtém notas para a pasta atual
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            self.notes = note_controller.get_notes_by_folder(self.current_folder_id)
            
            # Adiciona notas à lista
            for note in self.notes:
                self._add_note_to_list(note)
    
    def _add_note_to_list(self, note: Dict[str, Any]):
        """Adiciona uma nota ao widget de lista.
        
        Args:
            note: Os dados da nota
        """
        # Cria item de lista
        item = QListWidgetItem(note['title'])
        item.setData(Qt.UserRole, note['id'])  # Armazena o ID da nota como dado do usuário
        
        # Adiciona um tooltip com uma prévia do conteúdo
        if note['content']:
            preview = StringUtils.truncate(note['content'], 100)
            item.setToolTip(preview)
        
        # Adiciona item à lista
        self.list_widget.addItem(item)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Manipula o evento de clique em um item.
        
        Args:
            item: O item clicado
        """
        note_id = item.data(Qt.UserRole)
        self.note_selected.emit(note_id)
    
    def _show_context_menu(self, position):
        """Mostra o menu de contexto para o item da lista na posição dada.
        
        Args:
            position: A posição onde mostrar o menu
        """
        # Obtém o item na posição
        item = self.list_widget.itemAt(position)
        if not item:
            return
        
        # Obtém o ID da nota
        note_id = item.data(Qt.UserRole)
        
        # Cria menu de contexto
        menu = QMenu(self)
        
        # Adiciona ações
        delete_action = QAction("Excluir", self)
        delete_action.triggered.connect(lambda: self._delete_note(note_id))
        menu.addAction(delete_action)
        
        # Adiciona submenu de mover para pasta
        move_menu = menu.addMenu("Mover para")
        self._populate_move_menu(move_menu, note_id)
        
        # Mostra o menu
        menu.exec_(self.list_widget.mapToGlobal(position))
    
    def _populate_move_menu(self, menu: QMenu, note_id: int):
        """Preenche o submenu de mover para pasta.
        
        Args:
            menu: O menu a ser preenchido
            note_id: O ID da nota
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return
        
        # Obtém todas as pastas
        folders = folder_controller.get_all_folders()
        
        # Adiciona ações de pasta
        for folder in folders:
            # Pula a pasta atual
            if folder['id'] == self.current_folder_id:
                continue
            
            action = QAction(folder['name'], self)
            action.triggered.connect(lambda checked=False, fid=folder['id']: self._move_note(note_id, fid))
            menu.addAction(action)
    
    def _delete_note(self, note_id: int):
        """Exclui uma nota.
        
        Args:
            note_id: O ID da nota
        """
        # Confirma exclusão
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir esta nota?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            note_controller = self.controllers.get('note_controller')
            if note_controller and note_controller.delete_note(note_id):
                # Remove a nota da lista
                for i in range(self.list_widget.count()):
                    item = self.list_widget.item(i)
                    if item.data(Qt.UserRole) == note_id:
                        self.list_widget.takeItem(i)
                        break
                
                # Emite sinal
                self.note_deleted.emit(note_id)
    
    def _move_note(self, note_id: int, target_folder_id: int):
        """Move uma nota para outra pasta.
        
        Args:
            note_id: O ID da nota
            target_folder_id: O ID da pasta de destino
        """
        note_controller = self.controllers.get('note_controller')
        if note_controller and note_controller.move_note(note_id, target_folder_id):
            # Remove a nota da lista
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.UserRole) == note_id:
                    self.list_widget.takeItem(i)
                    break
            
            # Emite sinal
            self.note_moved.emit(note_id, target_folder_id)
    
    def select_note(self, note_id: int):
        """Seleciona uma nota na lista.
        
        Args:
            note_id: O ID da nota
        """
        # Procura o item com o ID da nota fornecido
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == note_id:
                self.list_widget.setCurrentItem(item)
                break