from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from presentation.components.base_component import BaseComponent
from shared.utils import StringUtils

class SearchComponent(BaseComponent):
    """Componente para busca de notas."""
    
    # Define sinais
    search_performed = pyqtSignal(list)  # Emitido quando uma busca é realizada (resultados)
    note_selected = pyqtSignal(int)      # Emitido quando uma nota é selecionada (note_id)
    
    def __init__(self, parent=None, controllers=None):
        """Inicializa o componente.
        
        Args:
            parent: O widget pai
            controllers: Um dicionário de controladores
        """
        super().__init__(parent, controllers)
        
        # Resultados da busca
        self.search_results = []
    
    def _init_ui(self):
        """Inicializa os componentes da interface."""
        # Cria layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Layout da entrada de busca
        search_layout = QHBoxLayout()
        
        # Entrada de busca
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar notas...")
        self.search_input.setStyleSheet("padding: 5px;")
        search_layout.addWidget(self.search_input)
        
        # Botão de busca
        self.search_button = QPushButton("Buscar", self)
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout)
        
        # Rótulo de resultados
        self.results_label = QLabel("Digite um termo de busca acima", self)
        self.results_label.setStyleSheet("color: gray; font-style: italic; margin-top: 5px;")
        main_layout.addWidget(self.results_label)
        
        # Lista de resultados
        self.results_list = QListWidget(self)
        self.results_list.setStyleSheet("margin-top: 5px;")
        main_layout.addWidget(self.results_list)
    
    def _connect_signals(self):
        """Conecta sinais e slots."""
        # Conecta botão de busca
        self.search_button.clicked.connect(self._perform_search)
        
        # Conecta tecla Enter da entrada de busca
        self.search_input.returnPressed.connect(self._perform_search)
        
        # Conecta lista de resultados
        self.results_list.itemClicked.connect(self._on_result_clicked)
    
    def _perform_search(self):
        """Executa a busca usando a entrada atual."""
        # Obtém o termo de busca
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.results_label.setText("Digite um termo de busca acima")
            self.results_list.clear()
            self.search_results = []
            return
        
        # Realiza a busca
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            # Realiza a busca com opções padrão
            # Busca tanto no título quanto no conteúdo, sem diferenciar maiúsculas de minúsculas, em todas as pastas
            self.search_results = note_controller.search_notes(
                search_term=search_term,
                folder_ids=None,  # Busca em todas as pastas
                include_title=True,
                include_content=True,
                case_sensitive=False
            )
            
            # Atualiza o rótulo de resultados
            count = len(self.search_results)
            if count == 0:
                self.results_label.setText(f"Nenhum resultado encontrado para '{search_term}'")
            elif count == 1:
                self.results_label.setText(f"1 resultado encontrado para '{search_term}'")
            else:
                self.results_label.setText(f"{count} resultados encontrados para '{search_term}'")
            
            # Atualiza a lista de resultados
            self._update_results_list()
            
            # Emite sinal
            self.search_performed.emit(self.search_results)
    
    def _update_results_list(self):
        """Atualiza a lista de resultados com os resultados da busca atual."""
        # Limpa a lista
        self.results_list.clear()
        
        # Adiciona os resultados à lista
        for result in self.search_results:
            self._add_result_to_list(result)
    
    def _add_result_to_list(self, result: Dict[str, Any]):
        """Adiciona um resultado da busca à lista.
        
        Args:
            result: Os dados do resultado da busca
        """
        # Cria item da lista
        item = QListWidgetItem()
        
        # Define o texto do item
        title = result.get('title', 'Sem título')
        folder_name = result.get('folder_name', '')
        
        # Cria texto de exibição
        display_text = title
        if folder_name:
            display_text += f" (na {folder_name})"
        
        item.setText(display_text)
        
        # Armazena o ID da nota como dado do usuário
        item.setData(Qt.UserRole, result.get('id'))
        
        # Adiciona o item à lista
        self.results_list.addItem(item)
    
    def _on_result_clicked(self, item: QListWidgetItem):
        """Manipula o evento de clique em um item de resultado.
        
        Args:
            item: O item clicado
        """
        # Obtém o ID da nota
        note_id = item.data(Qt.UserRole)
        
        # Emite sinal
        self.note_selected.emit(note_id)
    
    def clear_search(self):
        """Limpa a entrada de busca e os resultados."""
        self.search_input.clear()
        self.results_list.clear()
        self.results_label.setText("Digite um termo de busca acima")
        self.search_results = []