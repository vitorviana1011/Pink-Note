from typing import Dict, Any, List, Optional, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget, 
                             QPushButton, QLabel, QDialog, QLineEdit, QTextEdit,
                             QTimeEdit, QDateEdit, QFormLayout, QDialogButtonBox,
                             QMessageBox, QMenu, QAction, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QDateTime
from PyQt5.QtGui import QColor, QTextCharFormat
import datetime

from presentation.components.base_component import BaseComponent
from shared.utils import DateUtils

class EventDialog(QDialog):
    """Diálogo para criar e editar eventos."""
    
    def __init__(self, parent=None, event=None):
        """Inicializa o diálogo.
        
        Args:
            parent: O widget pai
            event: Os dados do evento (opcional, para edição)
        """
        super().__init__(parent)
        
        self.event = event
        self.init_ui()
    
    def init_ui(self):
        """Inicializa os componentes da interface."""
        # Define propriedades do diálogo
        self.setWindowTitle("Evento" if self.event else "Novo Evento")
        self.setMinimumWidth(400)
        
        # Cria layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Entrada de título
        self.title_input = QLineEdit(self)
        if self.event:
            self.title_input.setText(self.event.get('title', ''))
        form_layout.addRow("Título:", self.title_input)
        
        # Entrada de data
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        if self.event and 'date' in self.event:
            event_date = DateUtils.parse_date(self.event['date'])
            self.date_input.setDate(QDate(event_date.year, event_date.month, event_date.day))
        else:
            self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Data:", self.date_input)
        
        # Entrada de hora
        self.time_input = QTimeEdit(self)
        if self.event and 'time' in self.event:
            event_time = DateUtils.parse_time(self.event['time'])
            self.time_input.setTime(QTime(event_time.hour, event_time.minute))
        else:
            self.time_input.setTime(QTime.currentTime())
        form_layout.addRow("Hora:", self.time_input)
        
        # Entrada de descrição
        self.description_input = QTextEdit(self)
        if self.event:
            self.description_input.setText(self.event.get('description', ''))
        form_layout.addRow("Descrição:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_event_data(self) -> Dict[str, Any]:
        """Obtém os dados do evento a partir das entradas do diálogo.
        
        Returns:
            Um dicionário com os dados do evento
        """
        # Obtém valores das entradas
        title = self.title_input.text().strip()
        date = self.date_input.date().toString(Qt.ISODate)
        time = self.time_input.time().toString("hh:mm")
        description = self.description_input.toPlainText().strip()
        
        # Cria dados do evento
        event_data = {
            'title': title,
            'date': date,
            'time': time,
            'description': description
        }
        
        # Adiciona ID se estiver editando
        if self.event and 'id' in self.event:
            event_data['id'] = self.event['id']
        
        return event_data

class CalendarComponent(BaseComponent):
    """Componente para exibir e gerenciar um calendário com eventos."""
    
    # Define sinais
    date_selected = pyqtSignal(QDate)  # Emitido quando uma data é selecionada
    event_created = pyqtSignal(int)    # Emitido quando um evento é criado (event_id)
    event_updated = pyqtSignal(int)    # Emitido quando um evento é atualizado (event_id)
    event_deleted = pyqtSignal(int)    # Emitido quando um evento é deletado (event_id)
    
    def __init__(self, parent=None, controllers=None):
        """Inicializa o componente.
        
        Args:
            parent: O widget pai
            controllers: Um dicionário de controladores
        """
        super().__init__(parent, controllers)
        
        # Data atual
        self.current_date = QDate.currentDate()
        
        # Dados dos eventos
        self.events_by_date = {}
    
    def _init_ui(self):
        """Inicializa os componentes da interface."""
        # Cria layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Cabeçalho do calendário
        header_layout = QHBoxLayout()
        
        # Navegação entre meses
        self.prev_month_btn = QPushButton("<", self)
        self.prev_month_btn.setFixedWidth(30)
        header_layout.addWidget(self.prev_month_btn)
        
        self.month_label = QLabel(self)
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.month_label)
        
        self.next_month_btn = QPushButton(">", self)
        self.next_month_btn.setFixedWidth(30)
        header_layout.addWidget(self.next_month_btn)
        
        main_layout.addLayout(header_layout)
        
        # Widget do calendário
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        self.calendar.setFixedHeight(300)  # Altura fixa para o calendário
        main_layout.addWidget(self.calendar)
        
        # Seção de eventos
        events_layout = QVBoxLayout()
        
        # Cabeçalho dos eventos
        events_header = QHBoxLayout()
        self.events_label = QLabel("Eventos", self)
        self.events_label.setStyleSheet("font-weight: bold;")
        events_header.addWidget(self.events_label)
        
        # Botão para adicionar evento
        self.add_event_btn = QPushButton("Adicionar Evento", self)
        events_header.addWidget(self.add_event_btn)
        events_header.addStretch()
        events_layout.addLayout(events_header)
        
        # Scroll area para eventos do dia
        self.day_events_scroll = QScrollArea(self)
        self.day_events_scroll.setObjectName("dayEventsScrollArea")
        self.day_events_scroll.setWidgetResizable(True)
        self.day_events_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.day_events_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget para conter os eventos
        self.events_container = QWidget()
        self.events_container.setObjectName("dayEventsWidget")
        self.events_container.setLayout(QVBoxLayout())
        self.events_container.layout().setObjectName("dayEventsLayout")
        self.events_container.layout().setContentsMargins(0, 0, 0, 0)
        self.events_container.layout().setSpacing(5)
        self.events_container.layout().addStretch()  # Adiciona espaço em branco no final
        
        # Adiciona o widget de eventos ao scroll area
        self.day_events_scroll.setWidget(self.events_container)
        events_layout.addWidget(self.day_events_scroll)
        
        main_layout.addLayout(events_layout)
        
        # Atualiza a interface com a data atual
        self._update_month_label()
    
    def _connect_signals(self):
        """Conecta sinais e slots."""
        # Conecta sinais do calendário
        self.calendar.clicked.connect(self._on_date_clicked)
        self.calendar.currentPageChanged.connect(self._on_month_changed)
        
        # Conecta botões de navegação
        self.prev_month_btn.clicked.connect(self._on_prev_month)
        self.next_month_btn.clicked.connect(self._on_next_month)
        
        # Conecta botão de adicionar evento
        self.add_event_btn.clicked.connect(self._add_event)
    
    def refresh(self):
        """Atualiza a exibição do calendário."""
        # Carrega eventos do mês atual
        self._load_events_for_month()
        
        # Atualiza a exibição do calendário
        self._update_calendar_display()
        
        # Atualiza eventos para a data selecionada
        self._update_events_display()
    
    def _update_month_label(self):
        """Atualiza o rótulo do mês com o mês e ano atuais."""
        month_year = self.calendar.monthShown(), self.calendar.yearShown()
        month_name = QDate(month_year[1], month_year[0], 1).toString("MMMM yyyy")
        self.month_label.setText(month_name)
        self.month_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #333;")
    
    def _on_date_clicked(self, date: QDate):
        """Manipula o evento de clique na data.
        
        Args:
            date: A data clicada
        """
        self.current_date = date
        self._update_events_display()
        self.date_selected.emit(date)
    
    def _on_month_changed(self, year: int, month: int):
        """Manipula o evento de mudança de mês.
        
        Args:
            year: O novo ano
            month: O novo mês
        """
        self._update_month_label()
        self._load_events_for_month()
        self._update_calendar_display()
    
    def _on_prev_month(self):
        """Navega para o mês anterior."""
        self.calendar.showPreviousMonth()
    
    def _on_next_month(self):
        """Navega para o próximo mês."""
        self.calendar.showNextMonth()
    
    def _load_events_for_month(self):
        """Carrega eventos para o mês atual."""
        event_controller = self.controllers.get('event_controller')
        if not event_controller:
            return
        
        # Obtém o mês e ano atuais
        month = self.calendar.monthShown()
        year = self.calendar.yearShown()
        
        # Obtém eventos para o mês
        events = event_controller.get_events_for_month(year, month)
        
        # Agrupa eventos por data
        self.events_by_date = {}
        for event in events:
            date_str = event.get('date')
            if date_str:
                # Normaliza a string da data removendo a parte da hora, se presente
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                
                if date_str not in self.events_by_date:
                    self.events_by_date[date_str] = []
                self.events_by_date[date_str].append(event)
    
    def _update_calendar_display(self):
        """Atualiza a exibição do calendário com indicadores de eventos."""
        # Obtém datas com eventos
        event_controller = self.controllers.get('event_controller')
        if not event_controller:
            return
        
        # Obtém o mês e ano atuais
        month = self.calendar.monthShown()
        year = self.calendar.yearShown()
        
        # Obtém datas com eventos
        dates_with_events = event_controller.get_dates_with_events(year, month)
        
        # Limpa todos os formatos de data
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Define formato para datas com eventos
        event_format = QTextCharFormat()
        event_format.setBackground(QColor(200, 230, 255))
        event_format.setForeground(QColor(0, 0, 150))
        event_format.setFontWeight(700)  # Fonte em negrito
        
        for date_str in dates_with_events:
            date = QDate.fromString(date_str, Qt.ISODate)
            self.calendar.setDateTextFormat(date, event_format)
    
    def _update_events_display(self):
        """Atualiza a exibição dos eventos para a data selecionada."""
        # Limpa o contêiner de eventos
        self._clear_events_container()
        
        # Obtém a string da data atual
        date_str = self.current_date.toString(Qt.ISODate)
        
        # Obtém eventos para a data
        events = self.events_by_date.get(date_str, [])
        
        if not events:
            # Exibe mensagem de ausência de eventos
            label = QLabel("📅 Sem eventos para esta data", self.events_container)
            label.setStyleSheet("color: gray; font-style: italic; padding: 10px; text-align: center;")
            label.setAlignment(Qt.AlignCenter)
            self.events_container.layout().insertWidget(0, label)
        else:
            # Adiciona widgets de eventos
            for event in events:
                self._add_event_widget(event)
        
        # Adiciona um espaço em branco no final para permitir scroll adequado
        self.events_container.layout().addStretch()
    
    def _clear_events_container(self):
        """Limpa o contêiner de eventos."""
        # Remove todos os widgets do layout
        layout = self.events_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.spacerItem():
                # Remove itens de espaçamento também
                layout.removeItem(item)
    
    def _add_event_widget(self, event: Dict[str, Any]):
        """Adiciona um widget de evento ao contêiner de eventos.
        
        Args:
            event: Os dados do evento
        """
        # Cria widget de evento
        event_widget = QWidget(self.events_container)
        event_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        event_widget.customContextMenuRequested.connect(
            lambda pos, e=event: self._show_event_context_menu(pos, e)
        )
        
        # Define estilo
        event_widget.setStyleSheet(
            "background-color: #f0f8ff; border-radius: 5px; padding: 5px; border: 1px solid #d0e0f0; margin-bottom: 5px;"
        )
        
        # Cria layout
        layout = QVBoxLayout(event_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Adiciona título
        title = event.get('title', '')
        if title:
            title_label = QLabel(title, event_widget)
            title_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(title_label)
        else:
            title_label = QLabel("(Sem título)", event_widget)
            title_label.setStyleSheet("font-weight: bold; color: gray;")
            layout.addWidget(title_label)
        
        # Adiciona hora
        if 'formatted_date' in event:
            formatted_date = event.get('formatted_date', '')
            # Extrai a parte da hora da data formatada (supondo que o formato seja dd/mm/yyyy HH:MM:SS)
            if ' ' in formatted_date:
                time_part = formatted_date.split(' ')[1]
                # Mostra apenas horas e minutos
                if ':' in time_part:
                    time_display = ':'.join(time_part.split(':')[:2])
                    time_label = QLabel(f"⏰ {time_display}", event_widget)
                    time_label.setStyleSheet("color: #666;")
                    layout.addWidget(time_label)
        elif 'time' in event:
            time_label = QLabel(f"⏰ {event.get('time', '')}", event_widget)
            time_label.setStyleSheet("color: #666;")
            layout.addWidget(time_label)
        
        # Adiciona descrição (truncada)
        description = event.get('description', '')
        if description:
            # Trunca a descrição se for muito longa
            max_length = 50
            if len(description) > max_length:
                description = description[:max_length] + '...'
            
            description_label = QLabel(f"📝 {description}", event_widget)
            description_label.setStyleSheet("color: #333; font-size: 9pt;")
            description_label.setWordWrap(True)
            layout.addWidget(description_label)
        
        # Adiciona ao contêiner (inserir no início do layout, antes do stretch)
        layout_count = self.events_container.layout().count()
        if layout_count > 0:
            # Insere antes do último item (que deve ser o stretch)
            self.events_container.layout().insertWidget(layout_count - 1, event_widget)
        else:
            # Se o layout estiver vazio, apenas adiciona
            self.events_container.layout().addWidget(event_widget)
    
    def _show_event_context_menu(self, position, event: Dict[str, Any]):
        """Mostra o menu de contexto para o evento.
        
        Args:
            position: A posição onde mostrar o menu
            event: Os dados do evento
        """
        # Cria menu de contexto
        menu = QMenu(self)
        
        # Adiciona ações
        edit_action = QAction("Editar", self)
        edit_action.triggered.connect(lambda: self._edit_event(event))
        menu.addAction(edit_action)
        
        delete_action = QAction("Deletar", self)
        delete_action.triggered.connect(lambda: self._delete_event(event))
        menu.addAction(delete_action)
        
        # Mostra o menu
        sender = self.sender()
        menu.exec_(sender.mapToGlobal(position))
    
    def _add_event(self):
        """Adiciona um novo evento."""
        # Cria diálogo
        dialog = EventDialog(self)
        
        # Define a data para a data atual selecionada
        dialog.date_input.setDate(self.current_date)
        
        # Mostra diálogo
        if dialog.exec_() == QDialog.Accepted:
            # Obtém dados do evento
            event_data = dialog.get_event_data()
            
            # Valida título
            if not event_data.get('title'):
                QMessageBox.warning(self, "Título Ausente", "Por favor, insira um título para o evento.")
                return
            
            # Cria evento
            event_controller = self.controllers.get('event_controller')
            if event_controller:
                # Analisa a string da data para um objeto de data
                date_str = event_data.get('date')
                time_str = event_data.get('time')
                event_date = None
                
                if date_str:
                    from shared.utils import DateUtils
                    event_date = DateUtils.parse_date(date_str)
                
                # Se a análise da data falhar, usa a data atual
                if event_date is None:
                    from shared.utils import DateUtils
                    event_date = DateUtils.get_current_date()
                
                # Combina a data com a hora, se disponível
                event_datetime = event_date
                if time_str:
                    from shared.utils import DateUtils
                    time_obj = DateUtils.parse_time(time_str)
                    if time_obj and event_date:
                        from datetime import datetime
                        event_datetime = datetime.combine(event_date, time_obj)
                
                event = event_controller.create_event(
                    title=event_data.get('title'),
                    description=event_data.get('description') or '',
                    event_date=event_datetime
                )
                
                if event:
                    # Atualiza o calendário
                    self.refresh()
                    
                    # Emite sinal
                    self.event_created.emit(event['id'])
    
    def _edit_event(self, event: Dict[str, Any]):
        """Edita um evento existente.
        
        Args:
            event: Os dados do evento
        """
        # Cria diálogo
        dialog = EventDialog(self, event)
        
        # Mostra diálogo
        if dialog.exec_() == QDialog.Accepted:
            # Obtém dados do evento
            event_data = dialog.get_event_data()
            
            # Valida título
            if not event_data.get('title'):
                QMessageBox.warning(self, "Título Ausente", "Por favor, insira um título para o evento.")
                return
            
            # Atualiza evento
            event_controller = self.controllers.get('event_controller')
            if event_controller:
                # Analisa a string da data para um objeto de data
                date_str = event_data.get('date')
                time_str = event_data.get('time')
                event_date = None
                
                if date_str:
                    from shared.utils import DateUtils
                    event_date = DateUtils.parse_date(date_str)
                
                # Se a análise da data falhar, usa a data atual
                if event_date is None:
                    from shared.utils import DateUtils
                    event_date = DateUtils.get_current_date()
                
                # Combina a data com a hora, se disponível
                event_datetime = event_date
                if time_str:
                    from shared.utils import DateUtils
                    time_obj = DateUtils.parse_time(time_str)
                    if time_obj and event_date:
                        from datetime import datetime
                        event_datetime = datetime.combine(event_date, time_obj)
                
                updated = event_controller.update_event(
                    event_id=event['id'],
                    title=event_data.get('title'),
                    event_date=event_datetime,
                    description=event_data.get('description') or ''
                )
                
                # Obtém os dados do evento atualizado se a atualização foi bem-sucedida
                updated_event = event_controller.get_event_by_id(event['id']) if updated else None
                
                if updated_event:
                    # Atualiza o calendário
                    self.refresh()
                    
                    # Emite sinal
                    self.event_updated.emit(updated_event['id'])
    
    def _delete_event(self, event: Dict[str, Any]):
        """Deleta um evento.
        
        Args:
            event: Os dados do evento
        """
        # Confirma a exclusão
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza de que deseja excluir este evento? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event_controller = self.controllers.get('event_controller')
            if event_controller:
                event_id = event['id']
                if event_controller.delete_event(event_id):
                    # Atualiza o calendário
                    self.refresh()
                    
                    # Emite sinal
                    self.event_deleted.emit(event_id)