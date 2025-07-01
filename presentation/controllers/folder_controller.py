from typing import List, Optional, Dict, Any, Tuple

from domain.entities.folder import Folder
from application.interfaces.folder_service import FolderService
from shared.utils.logger import Logger

class FolderController:
    """Controlador para operações relacionadas a pastas na camada de apresentação."""
    
    def __init__(self, folder_service: FolderService):
        """Inicializa o controlador com os serviços necessários.
        
        Args:
            folder_service: O serviço de pastas
        """
        self.folder_service = folder_service
        self.logger = Logger.get_instance()
    
    def get_all_folders(self) -> List[Dict[str, Any]]:
        """Obtém todas as pastas.
        
        Returns:
            Uma lista de dicionários representando as pastas
        """
        try:
            folders = self.folder_service.get_all_folders()
            return [self._folder_to_dict(folder) for folder in folders]
        except Exception as e:
            self.logger.error(f"Erro ao obter todas as pastas: {str(e)}")
            return []
    
    def get_folder_by_id(self, folder_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma pasta pelo seu ID.
        
        Args:
            folder_id: O ID da pasta
            
        Returns:
            Um dicionário representando a pasta, ou None se não encontrada
        """
        try:
            folder = self.folder_service.get_folder_by_id(folder_id)
            if folder:
                return self._folder_to_dict(folder)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter a pasta {folder_id}: {str(e)}")
            return None
    
    def get_folder_hierarchy(self) -> List[Dict[str, Any]]:
        """Obtém a hierarquia de pastas.
        
        Returns:
            Uma lista de dicionários representando a hierarquia de pastas
        """
        try:
            hierarchy = self.folder_service.get_folder_hierarchy()
            return self._process_hierarchy(hierarchy)
        except Exception as e:
            self.logger.error(f"Erro ao obter a hierarquia de pastas: {str(e)}")
            return []
    
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Cria uma nova pasta.
        
        Args:
            name: O nome da pasta
            parent_id: O ID da pasta pai (opcional)
            
        Returns:
            Um dicionário representando a pasta criada, ou None se falhar
        """
        try:
            # Valida a pasta pai se fornecida
            if parent_id is not None:
                parent = self.folder_service.get_folder_by_id(parent_id)
                if not parent:
                    self.logger.error(f"Não é possível criar pasta: Pasta pai {parent_id} não encontrada")
                    return None
            
            # Cria a pasta
            folder_id = self.folder_service.create_folder(name, parent_id)
            if folder_id:
                return self.get_folder_by_id(folder_id)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao criar pasta: {str(e)}")
            return None
    
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Renomeia uma pasta.
        
        Args:
            folder_id: O ID da pasta
            new_name: O novo nome da pasta
            
        Returns:
            True se renomeou com sucesso, False caso contrário
        """
        try:
            return self.folder_service.rename_folder(folder_id, new_name)
        except Exception as e:
            self.logger.error(f"Erro ao renomear pasta {folder_id}: {str(e)}")
            return False
    
    def delete_folder(self, folder_id: int) -> bool:
        """Exclui uma pasta.
        
        Args:
            folder_id: O ID da pasta
            
        Returns:
            True se excluiu com sucesso, False caso contrário
        """
        try:
            return self.folder_service.delete_folder(folder_id)
        except Exception as e:
            self.logger.error(f"Erro ao excluir pasta {folder_id}: {str(e)}")
            return False
    
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move uma pasta para outra pasta pai.
        
        Args:
            folder_id: O ID da pasta
            new_parent_id: O novo ID da pasta pai, ou None para mover para a raiz
            
        Returns:
            True se moveu com sucesso, False caso contrário
        """
        try:
            # Valida a nova pasta pai se fornecida
            if new_parent_id is not None:
                parent = self.folder_service.get_folder_by_id(new_parent_id)
                if not parent:
                    self.logger.error(f"Não é possível mover pasta: Pasta pai {new_parent_id} não encontrada")
                    return False
                
                # Verifica se new_parent_id é descendente de folder_id (evita ciclo)
                if self._is_descendant(new_parent_id, folder_id):
                    self.logger.error(f"Não é possível mover pasta: Criaria um ciclo na hierarquia de pastas")
                    return False
            
            return self.folder_service.move_folder(folder_id, new_parent_id)
        except Exception as e:
            self.logger.error(f"Erro ao mover pasta {folder_id} para pai {new_parent_id}: {str(e)}")
            return False
    
    def get_folder_note_count(self, folder_id: int) -> int:
        """Obtém o número de notas em uma pasta.
        
        Args:
            folder_id: O ID da pasta
            
        Returns:
            O número de notas na pasta
        """
        try:
            return self.folder_service.get_folder_note_count(folder_id)
        except Exception as e:
            self.logger.error(f"Erro ao obter quantidade de notas da pasta {folder_id}: {str(e)}")
            return 0
    
    def _folder_to_dict(self, folder: Folder) -> Dict[str, Any]:
        """Converte uma entidade Folder para um dicionário.
        
        Args:
            folder: A entidade Folder
            
        Returns:
            Um dicionário representando a pasta
        """
        return {
            'id': folder.id,
            'name': folder.name,
            'parent_id': folder.parent_id,
            'path': folder.path,
            'is_root': folder.is_root
        }
    
    def _process_hierarchy(self, hierarchy: List[Tuple[Folder, int]]) -> List[Dict[str, Any]]:
        """Processa a hierarquia de pastas para adicionar informações adicionais.
        
        Args:
            hierarchy: A hierarquia de pastas do serviço como uma lista de tuplas (folder, profundidade)
            
        Returns:
            A hierarquia de pastas processada
        """
        result = []
        
        for folder, depth in hierarchy:
            folder_dict = self._folder_to_dict(folder)
            folder_dict['depth'] = depth
            folder_dict['note_count'] = self.get_folder_note_count(folder_dict['id'])
            
            # Filhos são processados separadamente no componente de árvore
            
            result.append(folder_dict)
        
        return result
    
    def _is_descendant(self, folder_id: int, potential_ancestor_id: int) -> bool:
        """Verifica se uma pasta é descendente de outra pasta.
        
        Args:
            folder_id: O ID da pasta a verificar
            potential_ancestor_id: O ID da possível pasta ancestral
            
        Returns:
            True se folder_id é descendente de potential_ancestor_id, False caso contrário
        """
        folder = self.folder_service.get_folder_by_id(folder_id)
        if not folder:
            return False
        
        # Se o pai desta pasta é o ancestral potencial, é descendente
        if folder.parent_id == potential_ancestor_id:
            return True
        
        # Se esta pasta não tem pai, não é descendente
        if folder.parent_id is None:
            return False
        
        # Verifica recursivamente se o pai é descendente
        return self._is_descendant(folder.parent_id, potential_ancestor_id)