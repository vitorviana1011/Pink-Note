import os
import sqlite3
from typing import Dict, Any

from application.interfaces.note_service import NoteService
from application.interfaces.folder_service import FolderService
from application.interfaces.event_service import EventService
from application.interfaces.attachment_service import AttachmentService

from application.use_cases.note_service_impl import NoteServiceImpl
from application.use_cases.folder_service_impl import FolderServiceImpl
from application.use_cases.event_service_impl import EventServiceImpl
from application.use_cases.attachment_service_impl import AttachmentServiceImpl

from domain.repositories.note_repository import NoteRepository
from domain.repositories.folder_repository import FolderRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.attachment_repository import AttachmentRepository

from infrastructure.database.note_repository_impl import NoteRepositoryImpl
from infrastructure.database.folder_repository_impl import FolderRepositoryImpl
from infrastructure.database.event_repository_impl import EventRepositoryImpl
from infrastructure.database.attachment_repository_impl import AttachmentRepositoryImpl
from infrastructure.database.db_init import DatabaseInitializer
from infrastructure.storage.file_storage import FileStorage

class Container:
    """Container de Injeção de Dependências da aplicação.
    
    Esta classe gerencia a criação e o ciclo de vida de todas as dependências da aplicação,
    seguindo o padrão de Injeção de Dependências para promover baixo acoplamento.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o container com a configuração da aplicação.
        
        Args:
            config: Um dicionário contendo a configuração da aplicação
        """
        self.config = config
        self._instances = {}
    
    def get_db_connection(self) -> sqlite3.Connection:
        """Obtém ou cria a conexão com o banco de dados."""
        if 'db_connection' not in self._instances:
            db_path = self.config.get('db_path', 'notepad.db')
            initializer = DatabaseInitializer(db_path)
            self._instances['db_connection'] = initializer.initialize_database()
        
        return self._instances['db_connection']
    
    def get_file_storage(self) -> FileStorage:
        """Obtém ou cria o serviço de armazenamento de arquivos."""
        if 'file_storage' not in self._instances:
            storage_path = self.config.get('storage_path', 'attachments')
            self._instances['file_storage'] = FileStorage(storage_path)
        
        return self._instances['file_storage']
    
    def get_note_repository(self) -> NoteRepository:
        """Obtém ou cria o repositório de notas."""
        if 'note_repository' not in self._instances:
            self._instances['note_repository'] = NoteRepositoryImpl(self.get_db_connection())
        
        return self._instances['note_repository']
    
    def get_folder_repository(self) -> FolderRepository:
        """Obtém ou cria o repositório de pastas."""
        if 'folder_repository' not in self._instances:
            self._instances['folder_repository'] = FolderRepositoryImpl(self.get_db_connection())
        
        return self._instances['folder_repository']
    
    def get_event_repository(self) -> EventRepository:
        """Obtém ou cria o repositório de eventos."""
        if 'event_repository' not in self._instances:
            self._instances['event_repository'] = EventRepositoryImpl(self.get_db_connection())
        
        return self._instances['event_repository']
    
    def get_attachment_repository(self) -> AttachmentRepository:
        """Obtém ou cria o repositório de anexos."""
        if 'attachment_repository' not in self._instances:
            self._instances['attachment_repository'] = AttachmentRepositoryImpl(self.get_db_connection())
        
        return self._instances['attachment_repository']
    
    def get_note_service(self) -> NoteService:
        """Obtém ou cria o serviço de notas."""
        if 'note_service' not in self._instances:
            self._instances['note_service'] = NoteServiceImpl(self.get_note_repository())
        
        return self._instances['note_service']
    
    def get_folder_service(self) -> FolderService:
        """Obtém ou cria o serviço de pastas."""
        if 'folder_service' not in self._instances:
            self._instances['folder_service'] = FolderServiceImpl(self.get_folder_repository())
        
        return self._instances['folder_service']
    
    def get_event_service(self) -> EventService:
        """Obtém ou cria o serviço de eventos."""
        if 'event_service' not in self._instances:
            self._instances['event_service'] = EventServiceImpl(self.get_event_repository())
        
        return self._instances['event_service']
    
    def get_attachment_service(self) -> AttachmentService:
        """Obtém ou cria o serviço de anexos."""
        if 'attachment_service' not in self._instances:
            self._instances['attachment_service'] = AttachmentServiceImpl(
                self.get_attachment_repository()
            )
        
        return self._instances['attachment_service']
    
    def get_note_controller(self):
        """Obtém ou cria o controlador de notas."""
        if 'note_controller' not in self._instances:
            from presentation.controllers.note_controller import NoteController
            self._instances['note_controller'] = NoteController(
                self.get_note_service(),
                self.get_folder_service()
            )
        
        return self._instances['note_controller']
    
    def get_folder_controller(self):
        """Obtém ou cria o controlador de pastas."""
        if 'folder_controller' not in self._instances:
            from presentation.controllers.folder_controller import FolderController
            self._instances['folder_controller'] = FolderController(
                self.get_folder_service()
            )
        
        return self._instances['folder_controller']
    
    def get_event_controller(self):
        """Obtém ou cria o controlador de eventos."""
        if 'event_controller' not in self._instances:
            from presentation.controllers.event_controller import EventController
            self._instances['event_controller'] = EventController(
                self.get_event_service()
            )
        
        return self._instances['event_controller']
    
    def get_attachment_controller(self):
        """Obtém ou cria o controlador de anexos."""
        if 'attachment_controller' not in self._instances:
            from presentation.controllers.attachment_controller import AttachmentController
            self._instances['attachment_controller'] = AttachmentController(
                self.get_attachment_service(),
                self.get_note_service()
            )
        
        return self._instances['attachment_controller']