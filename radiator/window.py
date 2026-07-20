from __future__ import annotations

from datetime import date, datetime, timedelta

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from radiator.sample_data import sample_emails

from radiator.sources.google_calendar_source import GoogleCalendarSource
from radiator.sources.google_task_source import GoogleTaskSource

from radiator.sections.calendar_section import CalendarSection
from radiator.sections.task_section import TaskSection

from radiator.widgets.email_card import EmailCard
from radiator.widgets.section import SectionWidget


class RadiatorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Info Radiator")

        # Good development size for the long 480×1920 display.
        # The operating system can rotate the monitor vertically.
        self.resize(480, 960)
        self.setMinimumWidth(340)

        self._build_ui()
        self._apply_styles()
        self._start_clock()

    def _build_ui(self) -> None:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("content")

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(8, 8, 8, 12)
        self.content_layout.setSpacing(8)

        self._build_header()

        calendar_source = GoogleCalendarSource()
        self.calendar_section = CalendarSection(source=calendar_source)

        task_source = GoogleTaskSource()
        self.task_section = TaskSection(task_source)

        self.email_section = SectionWidget("EMAIL")

        self.content_layout.addWidget(self.calendar_section)
        self.content_layout.addWidget(self.task_section)
        self.content_layout.addWidget(self.email_section)
        self.content_layout.addStretch(1)

        scroll_area.setWidget(content)
        self.setCentralWidget(scroll_area)

        self.calendar_section.start_auto_refresh(immediate=True)
        self.task_section.start_auto_refresh(immediate=True)

    def _build_header(self) -> None:
        header = QFrame()
        header.setObjectName("header")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 8, 6, 8)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        title = QLabel("INFO RADIATOR")
        title.setObjectName("appTitle")
        title_layout.addWidget(title)

        self.clock_label = QLabel()
        self.clock_label.setObjectName("clock")
        title_layout.addWidget(self.clock_label)

        layout.addLayout(title_layout)
        layout.addStretch(1)

        refresh_button = QPushButton("↻")
        refresh_button.setObjectName("refreshButton")
        refresh_button.setToolTip("Refresh")
        refresh_button.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_button)

        self.content_layout.addWidget(header)

    def _start_clock(self) -> None:
        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(1_000)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start()

        self._update_clock()

    def _update_clock(self) -> None:
        now = datetime.now()
        self.clock_label.setText(now.strftime("%A, %B %-d  •  %-I:%M %p"))

    def refresh_data(self) -> None:
        self.calendar_section.refresh()
        self.task_section.refresh()
        self._load_email()

    def _calendar_day_heading(self, event_date: date) -> str:
        today = date.today()
        difference = (event_date - today).days

        if difference == 0:
            return "TODAY"

        if difference == 1:
            return "TOMORROW"

        if 2 <= difference <= 6:
            return f"THIS {event_date.strftime('%A').upper()}"

        if 7 <= difference <= 13:
            return f"NEXT {event_date.strftime('%A').upper()}"

        return event_date.strftime("%A, %B %-d").upper()

    def _load_email(self) -> None:
        self.email_section.clear_items()

        for item in sample_emails():
            self.email_section.add_item(EmailCard(item))

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #151719;
            }

            QWidget#content {
                background: #151719;
            }

            QFrame#header {
                background: #202428;
                border: 1px solid #30363b;
                border-radius: 8px;
            }

            QLabel#appTitle {
                color: #f1f3f4;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#clock {
                color: #9ba3aa;
                font-size: 11px;
            }

            QPushButton#refreshButton {
                background: transparent;
                border: none;
                color: #d7dce0;
                font-size: 22px;
                padding: 4px 8px;
            }

            QPushButton#refreshButton:hover {
                background: #343a40;
                border-radius: 6px;
            }

            QFrame#section {
                background: #1b1e21;
                border: 1px solid #2b3035;
                border-radius: 8px;
            }

            QLabel#sectionTitle {
                color: #8e979f;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }

            QLabel#sectionStatus {
                color: #798189;
                font-size: 10px;
                font-weight: 600;
            }

            QLabel#calendarDayHeading {
                color: #8fa5b2;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
                padding-top: 7px;
                padding-bottom: 2px;
                border-bottom: 1px solid #343a40;
            }

            QFrame#card {
                background: #25292d;
                border: 1px solid #343a40;
                border-radius: 6px;
            }

            QFrame#card:hover {
                background: #2b3035;
                border-color: #4d565e;
            }

            QFrame#unreadCard {
                background: #29333a;
                border: 1px solid #496675;
                border-radius: 6px;
            }

            QFrame#unreadCard:hover {
                background: #303d45;
            }

            QLabel#cardTitle {
                color: #eef0f2;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#cardTitle[completed="true"] {
                color: #788087;
                text-decoration: line-through;
            }

            QLabel#secondaryText {
                color: #a3abb2;
                font-size: 11px;
            }

            QLabel#emailSender {
                color: #c8d0d6;
                font-size: 11px;
                font-weight: 700;
            }

            QLabel#timestamp {
                color: #798189;
                font-size: 10px;
            }

            QPushButton#iconButton {
                background: transparent;
                border: none;
                color: #bbc3c9;
                font-size: 17px;
                padding: 4px;
            }

            QPushButton#iconButton:hover {
                background: #3a4147;
                border-radius: 4px;
            }

            QFrame#taskCard {
                background-color: #20252a;
                border-radius: 6px;
            }

            QFrame#taskCard:hover {
                background-color: #292f35;
            }

            QLabel#taskTitle {
                font-size: 12px;
                font-weight: 600;
            }

            QCheckBox {
                spacing: 0px;
            }

            QCheckBox::indicator {
                width: 17px;
                height: 17px;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #4a5157;
                border-radius: 3px;
                min-height: 30px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QPushButton#sectionActionButton {
                background: transparent;
                border: none;
                color: #bbc3c9;
                font-size: 18px;
                font-weight: 600;
                padding: 0px 5px;
            }

            QPushButton#sectionActionButton:hover {
                background: #343a40;
                border-radius: 4px;
            }

            QLabel#subtaskMarker {
                color: #69747c;
                font-size: 13px;
            }
        """
        )
