import os
import shutil
import uuid
from datetime import datetime
from typing import Optional, Tuple

class FileStorage:
    """Classe responsável por gerenciar operações de armazenamento de arquivos."""

    def __init__(self, base_storage_path):
        """Inicializa com o caminho base do diretório de armazenamento."""
        self.base_storage_path = base_storage_path

        # Garante que o diretório de armazenamento exista
        os.makedirs(self.base_storage_path, exist_ok=True)

    def save_file(self, source_path: str, note_id: int) -> Tuple[str, str, str]:
        """Salva um arquivo no diretório de armazenamento e retorna seu caminho, nome e tipo.

        Args:
            source_path: Caminho do arquivo de origem
            note_id: ID da nota à qual este arquivo está anexado

        Returns:
            Tupla contendo (file_path, file_name, file_type)
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Arquivo de origem não encontrado: {source_path}")

        # Cria um diretório para os anexos da nota se não existir
        note_dir = os.path.join(self.base_storage_path, f"note_{note_id}")
        os.makedirs(note_dir, exist_ok=True)

        # Obtém nome e extensão do arquivo
        file_name = os.path.basename(source_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        # Gera um nome de arquivo único para evitar colisões
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}{file_ext}"

        # Caminho de destino
        dest_path = os.path.join(note_dir, unique_filename)

        # Copia o arquivo
        shutil.copy2(source_path, dest_path)

        # Determina o tipo do arquivo
        file_type = self._get_file_type(file_ext)

        return dest_path, file_name, file_type

    def delete_file(self, file_path: str) -> bool:
        """Exclui um arquivo do diretório de armazenamento.

        Args:
            file_path: Caminho do arquivo a ser excluído

        Returns:
            True se o arquivo foi excluído, False caso contrário
        """
        if not os.path.exists(file_path):
            return False

        try:
            os.remove(file_path)

            # Verifica se o diretório está vazio e remove se estiver
            dir_path = os.path.dirname(file_path)
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)

            return True
        except OSError:
            return False

    def _get_file_type(self, extension: str) -> str:
        """Determina o tipo do arquivo com base em sua extensão.

        Args:
            extension: Extensão do arquivo incluindo o ponto (ex: '.pdf')

        Returns:
            Uma string representando o tipo do arquivo
        """
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
        document_extensions = [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"]
        spreadsheet_extensions = [".xls", ".xlsx", ".csv", ".ods"]
        presentation_extensions = [".ppt", ".pptx", ".odp"]

        if extension in image_extensions:
            return "image"
        elif extension in document_extensions:
            return "document"
        elif extension in spreadsheet_extensions:
            return "spreadsheet"
        elif extension in presentation_extensions:
            return "presentation"
        else:
            return "other"