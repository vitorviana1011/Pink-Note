import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QFile, QTextStream

from presentation.main_window import MainWindow
from shared.utils.logger import Logger
from shared.constants import APP_NAME, APP_VERSION

# Configurações para suporte a DPI alto
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def exception_hook(exc_type, exc_value, exc_traceback):
    """Hook de exceção personalizado para registrar exceções não tratadas.
    
    Args:
        exc_type: Tipo da exceção
        exc_value: Valor da exceção
        exc_traceback: Traceback da exceção
    """
    # Registra a exceção
    logger = Logger.get_instance()
    logger.error(f"Exceção não tratada: {exc_value}\n{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}")
    
    # Formata o traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    # Exibe mensagem de erro
    QMessageBox.critical(
        None,
        "Erro na Aplicação",
        f"Ocorreu um erro inesperado:\n\n{exc_value}\n\n"
        f"Por favor, reporte este erro com as seguintes informações:\n\n{tb_text}"
    )
    
    # Chama o hook de exceção original
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def main():
    """Ponto de entrada principal da aplicação."""
    # Define o hook de exceção
    sys.excepthook = exception_hook
    
    # Cria a aplicação
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Carrega o stylesheet da aplicação
    style_file = QFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'style.qss'))
    if style_file.exists():
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
        style_file.close()
    
    # Cria a janela principal
    window = MainWindow()
    window.show()
    
    # Executa a aplicação
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())