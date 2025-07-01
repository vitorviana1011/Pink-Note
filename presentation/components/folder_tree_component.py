from typing import List, Dict, Any, Optional, Callable
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

from presentation.components.base_component import BaseComponent

class FolderTreeComponent(BaseComponent):
    """Componente para exibir e gerenciar uma árvore de pastas."""
    
    # Define sinais
    folder_selected = pyqtSignal(int)  # Emitido quando uma pasta é selecionada (folder_id)
    folder_created = pyqtSignal(int)   # Emitido quando uma pasta é criada (folder_id)
    folder_renamed = pyqtSignal(int)   # Emitido quando uma pasta é renomeada (folder_id)
    folder_deleted = pyqtSignal(int)   # Emitido quando uma pasta é excluída (folder_id)
    folder_moved = pyqtSignal(int, int)  # Emitido quando uma pasta é movida (folder_id, target_folder_id)
    
    def __init__(self, parent=None, controllers=None):
        """Inicializa o componente.
        
        Args:
            parent: O widget pai
            controllers: Um dicionário de controladores
        """
        super().__init__(parent, controllers)
        
        # ID da pasta atual
        self.current_folder_id = None
        
        # Mapa de itens de pasta (folder_id -> QTreeWidgetItem)
        self.folder_items = {}
    
    def _init_ui(self):
        """Inicializa os componentes da interface."""
        # Cria o widget de árvore
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Configura o layout
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)
    
    def _connect_signals(self):
        """Conecta sinais e slots."""
        # Conecta sinais do widget de árvore
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def refresh(self):
        """Atualiza a árvore de pastas."""
        # Limpa a árvore
        self.tree_widget.clear()
        self.folder_items = {}
        
        # Obtém a hierarquia de pastas
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller:
            hierarchy = folder_controller.get_folder_hierarchy()
            
            # Monta a árvore
            for folder in hierarchy:
                self._add_folder_to_tree(folder)
            
            # Expande todos os itens
            self.tree_widget.expandAll()
            
            # Seleciona a pasta atual se definida
            if self.current_folder_id is not None:
                self.select_folder(self.current_folder_id)
    
    def _add_folder_to_tree(self, folder: Dict[str, Any], parent_item: Optional[QTreeWidgetItem] = None):
        """Adiciona uma pasta ao widget de árvore.
        
        Args:
            folder: Os dados da pasta
            parent_item: O item pai na árvore (opcional)
        """
        # Cria item de árvore
        item = QTreeWidgetItem()
        item.setText(0, folder['name'])
        item.setData(0, Qt.UserRole, folder['id'])  # Armazena o ID da pasta como dado do usuário
        
        # Adiciona a contagem de notas ao texto se disponível
        if 'note_count' in folder:
            item.setText(0, f"{folder['name']} ({folder['note_count']})")  
        
        # Adiciona o item à árvore
        if parent_item:
            parent_item.addChild(item)
        else:
            self.tree_widget.addTopLevelItem(item)
        
        # Armazena o item no mapa
        self.folder_items[folder['id']] = item
        
        # Adiciona filhos recursivamente
        if 'children' in folder:
            for child in folder['children']:
                self._add_folder_to_tree(child, item)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Manipula o evento de clique em um item.
        
        Args:
            item: O item clicado
            column: A coluna clicada
        """
        folder_id = item.data(0, Qt.UserRole)
        self.current_folder_id = folder_id
        self.folder_selected.emit(folder_id)
    
    def _show_context_menu(self, position):
        """Mostra o menu de contexto para o item da árvore na posição dada.
        
        Args:
            position: A posição onde mostrar o menu
        """
        # Obtém o item na posição
        item = self.tree_widget.itemAt(position)
        if not item:
            return
        
        # Obtém o ID da pasta
        folder_id = item.data(0, Qt.UserRole)
        
        # Cria menu de contexto
        menu = QMenu(self)
        
        # Adiciona ações
        new_folder_action = QAction("Nova Pasta", self)
        new_folder_action.triggered.connect(lambda: self._create_folder(folder_id))
        menu.addAction(new_folder_action)
        
        rename_action = QAction("Renomear", self)
        rename_action.triggered.connect(lambda: self._rename_folder(folder_id))
        menu.addAction(rename_action)
        
        # Adiciona submenu de mover para pasta
        move_menu = menu.addMenu("Mover para")
        self._populate_move_menu(move_menu, folder_id)
        
        # Adiciona ação de excluir (apenas se não for a pasta raiz)
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller:
            folder = folder_controller.get_folder_by_id(folder_id)
            if folder and not folder.get('is_root', False):
                delete_action = QAction("Excluir", self)
                delete_action.triggered.connect(lambda: self._delete_folder(folder_id))
                menu.addAction(delete_action)
        
        # Mostra o menu
        menu.exec_(self.tree_widget.mapToGlobal(position))
    
    def _populate_move_menu(self, menu: QMenu, folder_id: int):
        """Preenche o submenu de mover para pasta.
        
        Args:
            menu: O menu a ser preenchido
            folder_id: O ID da pasta
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return
        
        # Obtém todas as pastas
        folders = folder_controller.get_all_folders()
        
        # Adiciona ações de pasta
        for folder in folders:
            # Pula a pasta atual e seus descendentes
            if folder['id'] == folder_id or self._is_descendant(folder['id'], folder_id):
                continue
            
            action = QAction(folder['name'], self)
            action.triggered.connect(lambda checked=False, fid=folder['id']: self._move_folder(folder_id, fid))
            menu.addAction(action)
        
        # Adiciona ação de mover para raiz
        action = QAction("Raiz", self)
        action.triggered.connect(lambda: self._move_folder(folder_id, None))
        menu.addAction(action)
    
    def _is_descendant(self, folder_id: int, potential_ancestor_id: int) -> bool:
        """Verifica se uma pasta é descendente de outra pasta.
        
        Args:
            folder_id: O ID da pasta a verificar
            potential_ancestor_id: O ID da possível pasta ancestral
            
        Returns:
            True se folder_id é descendente de potential_ancestor_id, False caso contrário
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return False
        
        folder = folder_controller.get_folder_by_id(folder_id)
        if not folder:
            return False
        
        # Se o pai desta pasta é o ancestral potencial, é descendente
        if folder.get('parent_id') == potential_ancestor_id:
            return True
        
        # Se esta pasta não tem pai, não é descendente
        if folder.get('parent_id') is None:
            return False
        
        # Verifica recursivamente se o pai é descendente
        return self._is_descendant(folder.get('parent_id'), potential_ancestor_id)
    
    def _create_folder(self, parent_id: int):
        """Cria uma nova pasta.
        
        Args:
            parent_id: O ID da pasta pai
        """
        # Obtém nome da pasta do usuário
        name, ok = QInputDialog.getText(self, "Nova Pasta", "Nome da pasta:")
        if ok and name:
            folder_controller = self.controllers.get('folder_controller')
            if folder_controller:
                new_folder = folder_controller.create_folder(name, parent_id)
                if new_folder:
                    # Atualiza a árvore
                    self.refresh()
                    
                    # Emite sinal
                    self.folder_created.emit(new_folder['id'])
    
    def _rename_folder(self, folder_id: int):
        """Renomeia uma pasta.
        
        Args:
            folder_id: O ID da pasta
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return
        
        # Obtém o nome atual da pasta
        folder = folder_controller.get_folder_by_id(folder_id)
        if not folder:
            return
        
        # Obtém novo nome do usuário
        name, ok = QInputDialog.getText(
            self, "Renomear Pasta", "Novo nome da pasta:", text=folder['name']
        )
        
        if ok and name and name != folder['name']:
            if folder_controller.rename_folder(folder_id, name):
                # Atualiza o texto do item
                item = self.folder_items.get(folder_id)
                if item:
                    item.setText(0, name)
                
                # Emite sinal
                self.folder_renamed.emit(folder_id)
    
    def _delete_folder(self, folder_id: int):
        """Exclui uma pasta.
        
        Args:
            folder_id: O ID da pasta
        """
        # Confirma exclusão
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir esta pasta? Todas as notas serão movidas para a pasta Geral.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            folder_controller = self.controllers.get('folder_controller')
            if folder_controller and folder_controller.delete_folder(folder_id):
                # Atualiza a árvore
                self.refresh()
                
                # Emite sinal
                self.folder_deleted.emit(folder_id)
    
    def _move_folder(self, folder_id: int, target_folder_id: Optional[int]):
        """Move uma pasta para outro pai.
        
        Args:
            folder_id: O ID da pasta
            target_folder_id: O ID da pasta de destino, ou None para mover para a raiz
        """
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller and folder_controller.move_folder(folder_id, target_folder_id):
            # Atualiza a árvore
            self.refresh()
            
            # Emite sinal
            self.folder_moved.emit(folder_id, target_folder_id or 0)  # Usa 0 para raiz
    
    def select_folder(self, folder_id: int):
        """Seleciona uma pasta na árvore.
        
        Args:
            folder_id: O ID da pasta
        """
        item = self.folder_items.get(folder_id)
        if item:
            self.tree_widget.setCurrentItem(item)
            self.current_folder_id = folder_id