from __future__ import annotations

from datetime import date, datetime, timedelta

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtGui import QCloseEvent, QGuiApplication, QScreen

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


from radiator.sources.google_calendar_source import GoogleCalendarSource
from radiator.sources.google_task_source import GoogleTaskSource
from radiator.sources.google_email_source import GoogleEmailSource

from radiator.sections.calendar_section import CalendarSection
from radiator.sections.task_section import TaskSection
from radiator.sections.email_section import EmailSection


class RadiatorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Info Radiator")

        self._allow_close = False
        self._target_screen: QScreen | None = None

        # Frameless removes the title bar and resize handles.
        #
        # Tool keeps the Radiator out of the normal taskbar while still allowing
        # it to exist as an ordinary top-level window.
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)

        self.setMinimumSize(1, 1)

        self._build_ui()
        self._apply_styles()
        self._start_clock()

    def _build_ui(self) -> None:

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

        email_source = GoogleEmailSource()
        self.email_section = EmailSection(source=email_source)

        self.content_layout.addWidget(self.calendar_section)
        self.content_layout.addWidget(self.task_section)
        self.content_layout.addWidget(self.email_section, 1)

        self.setCentralWidget(content)

        self.calendar_section.start_auto_refresh(immediate=True)
        self.task_section.start_auto_refresh(immediate=True)
        self.email_section.start_auto_refresh(immediate=True)

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
        self.email_section.refresh()

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
              font-size: 21px;
              font-weight: 700;
          }

          QLabel#clock {
              color: #9ba3aa;
              font-size: 14px;
          }

          QPushButton#refreshButton {
              background: transparent;
              border: none;
              color: #d7dce0;
              font-size: 25px;
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
              font-size: 14px;
              font-weight: 700;
              letter-spacing: 1px;
          }

          QLabel#sectionStatus {
              color: #798189;
              font-size: 12px;
              font-weight: 600;
          }

          QLabel#calendarDayHeading {
              color: #8fa5b2;
              font-size: 13px;
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
              font-size: 16px;
              font-weight: 600;
          }

          QLabel#cardTitle[completed="true"] {
              color: #788087;
              text-decoration: line-through;
          }

          QLabel#secondaryText {
              color: #a3abb2;
              font-size: 14px;
          }

          QLabel#emailSender {
              color: #c8d0d6;
              font-size: 14px;
              font-weight: 700;
          }

          QLabel#timestamp {
              color: #798189;
              font-size: 12px;
          }

          QPushButton#iconButton {
              background: transparent;
              border: none;
              color: #bbc3c9;
              font-size: 20px;
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
              font-size: 15px;
              font-weight: 600;
          }

          QCheckBox {
              spacing: 2px;
          }

          QCheckBox::indicator {
              width: 20px;
              height: 20px;
          }

          QScrollBar:vertical {
              background: transparent;
              width: 8px;
              margin: 2px;
          }

          QScrollBar::handle:vertical {
              background: #4a5157;
              border-radius: 4px;
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
              font-size: 21px;
              font-weight: 600;
              padding: 0px 5px;
          }

          QPushButton#sectionActionButton:hover {
              background: #343a40;
              border-radius: 4px;
          }

          QLabel#subtaskMarker {
              color: #69747c;
              font-size: 16px;
          }
          """
        )

    def _find_radiator_screen(self) -> QScreen:
        """
        Locate the narrow portrait display intended for the Info Radiator.

        Preferred match:
            - portrait orientation
            - approximately 480 × 1920 pixels

        Fallback:
            - narrowest non-primary display
            - primary display if no other display exists
        """
        screens = QGuiApplication.screens()

        if not screens:
            primary = QGuiApplication.primaryScreen()
            if primary is None:
                raise RuntimeError("Qt could not find any displays.")
            return primary

        def screen_score(screen: QScreen) -> tuple[int, int, int]:
            geometry = screen.geometry()
            width = geometry.width()
            height = geometry.height()

            portrait_penalty = 0 if height > width else 1

            # The physical display is 480 × 1920, but desktop scaling or
            # rotation can produce slightly different logical dimensions.
            target_difference = abs(width - 480) + abs(height - 1920)

            primary_penalty = 1 if screen is QGuiApplication.primaryScreen() else 0

            return (
                portrait_penalty,
                target_difference,
                primary_penalty,
            )

        selected = min(screens, key=screen_score)

        geometry = selected.geometry()
        print(
            "Info Radiator display:",
            selected.name(),
            f"{geometry.width()}x{geometry.height()}",
            f"at {geometry.x()},{geometry.y()}",
        )

        return selected

    def move_to_radiator_screen(self) -> None:
        """
        Move and resize the window to cover the target monitor.
        """
        screen = self._find_radiator_screen()
        geometry = screen.geometry()

        self._target_screen = screen
        self.setScreen(screen)
        self.setGeometry(geometry)

    def show_radiator(self) -> None:
        """
        Place the Radiator on its display and show it.
        """
        self.move_to_radiator_screen()
        self.show()

        # Some Linux window managers adjust a newly shown Tool window.
        # Apply the geometry again after it has become visible.
        QTimer.singleShot(100, self.move_to_radiator_screen)

        self.raise_()
        self.activateWindow()

    def allow_close(self) -> None:
        """
        Allow the real application Quit command to close the window.
        """
        self._allow_close = True

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Closing the window normally hides it to the system tray.

        The tray menu's Quit command calls allow_close() first.
        """
        if self._allow_close:
            event.accept()
            return

        event.ignore()
        self.hide()

    def keyPressEvent(self, event) -> None:
        """
        Escape hides the Radiator without terminating it.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return

        super().keyPressEvent(event)
