from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, 
                             QPushButton, QLabel, QFileDialog, QListWidget, QListWidgetItem,
                             QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
import os
import datetime

from presentation.components.base_component import BaseComponent
from shared.constants import SUPPORTED_ATTACHMENT_EXTENSIONS

class NoteEditorComponent(BaseComponent):
    """Componente para edição de notas e gerenciamento de anexos."""
    
    # Define sinais
    note_saved = pyqtSignal(int)  # Emitido quando uma nota é salva (note_id)
    note_deleted = pyqtSignal(int)  # Emitido quando uma nota é excluída (note_id)
    
    def __init__(self, parent=None, controllers=None):
        """Inicializa o componente.
        
        Args:
            parent: O widget pai
            controllers: Um dicionário de controladores
        """
        super().__init__(parent, controllers)
        
        # Dados da nota atual
        self.current_note = None
        self.current_folder_id = None
        self.is_new_note = False
        self.attachments = []
    
    def _init_ui(self):
        """Inicializa os componentes da interface."""
        # Cria o layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Campo de título
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Título da Nota")
        self.title_input.setStyleSheet("font-size: 16px; padding: 5px;")
        main_layout.addWidget(self.title_input)
        
        # Editor de conteúdo
        self.content_editor = QTextEdit(self)
        self.content_editor.setPlaceholderText("Escreva sua nota aqui...")
        self.content_editor.setStyleSheet("font-size: 14px; padding: 5px;")
        main_layout.addWidget(self.content_editor)
        
        # Seção de anexos
        attachment_layout = QVBoxLayout()
        
        # Cabeçalho de anexos
        attachment_header = QHBoxLayout()
        attachment_label = QLabel("Anexos", self)
        attachment_label.setStyleSheet("font-weight: bold;")
        attachment_header.addWidget(attachment_label)
        
        # Botão de adicionar anexo
        self.add_attachment_btn = QPushButton("Adicionar Arquivo", self)
        attachment_header.addWidget(self.add_attachment_btn)
        attachment_header.addStretch()
        attachment_layout.addLayout(attachment_header)
        
        # Lista de anexos
        self.attachments_list = QListWidget(self)
        self.attachments_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.attachments_list.setMaximumHeight(100)
        attachment_layout.addWidget(self.attachments_list)
        
        main_layout.addLayout(attachment_layout)
        
        # Layout dos botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Botão salvar
        self.save_btn = QPushButton("Salvar", self)
        self.save_btn.setStyleSheet("padding: 5px 15px;")
        buttons_layout.addWidget(self.save_btn)
        
        # Botão excluir
        self.delete_btn = QPushButton("Excluir", self)
        self.delete_btn.setStyleSheet("padding: 5px 15px;")
        buttons_layout.addWidget(self.delete_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Rótulo de status
        self.status_label = QLabel(self)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # Estado inicial
        self.clear_editor()
    
    def _connect_signals(self):
        """Conecta sinais e slots."""
        self.save_btn.clicked.connect(self._save_note)
        self.delete_btn.clicked.connect(self._delete_note)
        self.add_attachment_btn.clicked.connect(self._add_attachment)
        self.attachments_list.itemDoubleClicked.connect(self._open_attachment)
        self.attachments_list.customContextMenuRequested.connect(self._show_attachment_context_menu)
        self.title_input.textChanged.connect(self._update_status)
        self.content_editor.textChanged.connect(self._update_status)
    
    def set_folder(self, folder_id: int):
        """Define o ID da pasta atual.
        
        Args:
            folder_id: O ID da pasta
        """
        self.current_folder_id = folder_id
    
    def load_note(self, note_id: int):
        """Carrega uma nota no editor.
        
        Args:
            note_id: O ID da nota
        """
        note_controller = self.controllers.get('note_controller')
        if not note_controller:
            return
        
        # Obtém a nota
        note = note_controller.get_note_by_id(note_id)
        if not note:
            return
        
        # Define a nota atual
        self.current_note = note
        self.is_new_note = False
        
        # Atualiza UI
        self.title_input.setText(note.get('title', ''))
        self.content_editor.setText(note.get('content', ''))
        self.delete_btn.setEnabled(True)
        
        # Carrega anexos
        self._load_attachments(note_id)
        
        # Atualiza status
        self._update_status()
    
    def new_note(self):
        """Cria uma nova nota no editor."""
        # Limpa o editor
        self.clear_editor()
        
        # Define como nova nota
        self.is_new_note = True
        self.current_note = None
        
        # Habilita edição
        self.title_input.setEnabled(True)
        self.content_editor.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.delete_btn.setEnabled(False)
        
        # Foca no campo de título
        self.title_input.setFocus()
        
        # Atualiza status
        self._update_status()
    
    def clear_editor(self):
        """Limpa o editor."""
        # Limpa campos
        self.title_input.clear()
        self.content_editor.clear()
        self.attachments_list.clear()
        
        # Desabilita edição
        self.title_input.setEnabled(False)
        self.content_editor.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.add_attachment_btn.setEnabled(False)
        
        # Limpa nota atual
        self.current_note = None
        self.is_new_note = False
        self.attachments = []
        
        # Atualiza status
        self.status_label.setText("Nenhuma nota selecionada")
    
    def _save_note(self):
        """Salva a nota atual."""
        # Obtém dados da nota
        title = self.title_input.text().strip()
        content = self.content_editor.toPlainText()
        
        # Valida título
        if not title:
            QMessageBox.warning(self, "Título Ausente", "Por favor, insira um título para a nota.")
            self.title_input.setFocus()
            return
        
        note_controller = self.controllers.get('note_controller')
        if not note_controller:
            return
        
        # Salva nota
        if self.is_new_note:
            # Cria nova nota
            if self.current_folder_id is None:
                QMessageBox.warning(self, "Nenhuma Pasta Selecionada", "Por favor, selecione uma pasta para a nota.")
                return
            
            note = note_controller.create_note(
                title=title,
                content=content,
                folder_id=self.current_folder_id
            )
            
            if note:
                self.current_note = note
                self.is_new_note = False
                self.delete_btn.setEnabled(True)
                self.add_attachment_btn.setEnabled(True)
                # Emite sinal
                self.note_saved.emit(note['id'])
        else:
            # Atualiza nota existente
            if not self.current_note or not isinstance(self.current_note, dict) or 'id' not in self.current_note:
                # Se a nota atual for inválida, cria uma nova nota
                if self.current_folder_id is None:
                    QMessageBox.warning(self, "Nenhuma Pasta Selecionada", "Por favor, selecione uma pasta para a nota.")
                    return
                
                note = note_controller.create_note(
                    title=title,
                    content=content,
                    folder_id=self.current_folder_id
                )
                
                if note:
                    self.current_note = note
                    self.is_new_note = False
                    self.delete_btn.setEnabled(True)
                    self.add_attachment_btn.setEnabled(True)
                    self.note_saved.emit(note['id'])
            else:
                # Atualiza a nota existente
                note = note_controller.update_note(
                    note_id=self.current_note['id'],
                    title=title,
                    content=content
                )
                
                if note:
                    self.current_note = note
                    self.note_saved.emit(note['id'])
        
        # Atualiza status
        self._update_status(saved=True)
    
    def _delete_note(self):
        """Exclui a nota atual."""
        if not self.current_note or not isinstance(self.current_note, dict) or 'id' not in self.current_note:
            return
        
        # Confirma exclusão
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza de que deseja excluir esta nota? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            note_controller = self.controllers.get('note_controller')
            if note_controller:
                note_id = self.current_note['id']
                if note_controller.delete_note(note_id):
                    # Limpa o editor
                    self.clear_editor()
                    # Emite sinal
                    self.note_deleted.emit(note_id)
    
    def _load_attachments(self, note_id: int):
        """Carrega anexos para uma nota.
        
        Args:
            note_id: O ID da nota
        """
        attachment_controller = self.controllers.get('attachment_controller')
        if not attachment_controller:
            return
        
        # Limpa a lista
        self.attachments_list.clear()
        
        # Obtém anexos
        self.attachments = attachment_controller.get_attachments_for_note(note_id)
        
        # Adiciona à lista
        for attachment in self.attachments:
            item = QListWidgetItem(attachment.get('file_name', 'Unnamed Attachment'))
            item.setData(Qt.UserRole, attachment['id'])
            self.attachments_list.addItem(item)
        
        # Habilita botão de adicionar anexo
        self.add_attachment_btn.setEnabled(True)
    
    def _add_attachment(self):
        """Adiciona um anexo à nota atual."""
        if not self.current_note or not isinstance(self.current_note, dict) or 'id' not in self.current_note:
            return
        
        # Cria filtro para o diálogo de arquivos
        filter_str = "Todos os Arquivos (*.*);;"
        ext_list = " ".join(f"*.{ext.lstrip('.')}" for ext in SUPPORTED_ATTACHMENT_EXTENSIONS)
        filter_str += f"Arquivos Suportados ({ext_list});;"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Anexo",
            "",
            filter_str
        )
        
        if file_path and os.path.exists(file_path):
            attachment_controller = self.controllers.get('attachment_controller')
            if attachment_controller:
                attachment = attachment_controller.add_attachment(
                    note_id=self.current_note['id'],
                    file_path=file_path
                )
                
                if attachment:
                    item = QListWidgetItem(attachment.get('file_name', 'Unnamed Attachment'))
                    item.setData(Qt.UserRole, attachment['id'])
                    self.attachments_list.addItem(item)
                    self.attachments.append(attachment)
    
    def _open_attachment(self, item: QListWidgetItem):
        """Abre um anexo.
        
        Args:
            item: O item da lista que representa o anexo
        """
        attachment_id = item.data(Qt.UserRole)
        attachment_controller = self.controllers.get('attachment_controller')
        if attachment_controller:
            attachment_controller.open_attachment(attachment_id)
    
    def _show_attachment_context_menu(self, position):
        """Mostra o menu de contexto para o anexo na posição dada.
        
        Args:
            position: A posição onde mostrar o menu
        """
        item = self.attachments_list.itemAt(position)
        if not item:
            return
        
        attachment_id = item.data(Qt.UserRole)
        menu = QMenu(self)
        open_action = QAction("Abrir", self)
        open_action.triggered.connect(lambda: self._open_attachment(item))
        menu.addAction(open_action)
        delete_action = QAction("Excluir", self)
        delete_action.triggered.connect(lambda: self._delete_attachment(attachment_id))
        menu.addAction(delete_action)
        menu.exec_(self.attachments_list.mapToGlobal(position))
    
    def _delete_attachment(self, attachment_id: int):
        """Exclui um anexo.
        
        Args:
            attachment_id: O ID do anexo
        """
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza de que deseja excluir este anexo? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            attachment_controller = self.controllers.get('attachment_controller')
            if attachment_controller and attachment_controller.delete_attachment(attachment_id):
                for i in range(self.attachments_list.count()):
                    item = self.attachments_list.item(i)
                    if item.data(Qt.UserRole) == attachment_id:
                        self.attachments_list.takeItem(i)
                        break
                self.attachments = [a for a in self.attachments if a['id'] != attachment_id]
    
    def _update_status(self, saved=False):
        """Atualiza o rótulo de status.
        
        Args:
            saved: Se a nota foi salva recentemente
        """
        if self.current_note:
            if saved:
                self.status_label.setText(f"Salvo em {datetime.datetime.now().strftime('%H:%M:%S')}")
            else:
                self.status_label.setText("Editando nota")
        elif self.is_new_note:
            self.status_label.setText("Criando nova nota")
        else:
            self.status_label.setText("Nenhuma nota selecionada")