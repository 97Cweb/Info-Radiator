from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import Enum, auto
from typing import Any

from PySide6.QtCore import (
    QObject,
    QRunnable,
    QThreadPool,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtWidgets import QLabel, QWidget

from radiator.widgets.section import SectionWidget


class RefreshWorkerSignals(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()


class RefreshState(Enum):
    LOADING = auto()
    READY = auto()
    ERROR = auto()


class RefreshWorker(QRunnable):
    def __init__(self, loader: Callable[[], Any]) -> None:
        super().__init__()

        self.loader = loader
        self.signals = RefreshWorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self.loader()
        except Exception as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.succeeded.emit(result)
        finally:
            self.signals.finished.emit()


class DataSection(SectionWidget):
    """
    Base class for sections that periodically load data.

    Subclasses implement:
        fetch()
        update(data)
    """

    def __init__(
        self,
        title: str,
        refresh_interval_ms: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)

        self.refresh_interval_ms = refresh_interval_ms
        self._refresh_in_progress = False
        self._has_loaded_once = False

        self._thread_pool = QThreadPool.globalInstance()

        # Controls actual API/data refreshes.
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(refresh_interval_ms)
        self._refresh_timer.timeout.connect(self.refresh)

        # Only updates the displayed age. It does not fetch data.
        self._age_timer = QTimer(self)
        self._age_timer.setInterval(10_000)
        self._age_timer.timeout.connect(self._update_refresh_age)
        self._age_timer.start()

        self.last_refresh: datetime | None = None
        self.refresh_state: RefreshState = RefreshState.LOADING

    def start_auto_refresh(self, immediate: bool = True) -> None:
        self._refresh_timer.start()

        if immediate:
            self.refresh()

    def stop_auto_refresh(self) -> None:
        self._refresh_timer.stop()
        self._age_timer.stop()

    def refresh(self) -> None:
        if self._refresh_in_progress:
            return

        self._refresh_in_progress = True
        self.setProperty("refreshing", True)
        self.refresh_state = RefreshState.LOADING
        self.set_status("Refreshing")

        if not self._has_loaded_once:
            self.show_message("Loading…")

        worker = RefreshWorker(self.fetch)

        worker.signals.succeeded.connect(self._refresh_succeeded)
        worker.signals.failed.connect(self._refresh_failed)
        worker.signals.finished.connect(self._refresh_finished)

        self._thread_pool.start(worker)

    def fetch(self) -> Any:
        """
        Fetch data in a worker thread.

        This method must not directly modify Qt widgets.
        """

        raise NotImplementedError

    def update(self, data: Any) -> None:
        """
        Render loaded data.

        This method runs on the Qt GUI thread.
        """

        raise NotImplementedError

    def show_message(self, message: str) -> None:
        self.clear_items()

        label = QLabel(message)
        label.setObjectName("secondaryText")
        label.setWordWrap(True)

        self.add_item(label)

    @Slot(object)
    def _refresh_succeeded(self, data: Any) -> None:
        self._has_loaded_once = True

        self.refresh_state = RefreshState.READY
        self.last_refresh = datetime.now()

        self.update(data)
        self._update_refresh_age()
        self.set_status("Now")

    @Slot(str)
    def _refresh_failed(self, message: str) -> None:

        self.refresh_state = RefreshState.ERROR
        self.set_status("Error")
        print(f"{self.__class__.__name__}: {message}")

        # Keep previously displayed data after the first successful refresh.
        if not self._has_loaded_once:
            self.show_message("Could not refresh data")

    @Slot()
    def _refresh_finished(self) -> None:
        self._refresh_in_progress = False
        self.setProperty("refreshing", False)

    @Slot()
    def _update_refresh_age(self) -> None:
        if self.refresh_state is RefreshState.LOADING:
            self.set_status("Refreshing...")
            return

        if self.refresh_state is RefreshState.ERROR:
            self.set_status("Error")
            return

        if self.last_refresh is None:
            self.set_status("")
            return

        elasped_seconds = int((datetime.now() - self.last_refresh).total_seconds())
        if elasped_seconds < 60:
            self.set_status("Now")
            return

        elapsed_minutes = elasped_seconds // 60

        if elapsed_minutes < 60:
            self.set_status(f"{elapsed_minutes}m ago")
            return

        elapsed_hours = elapsed_minutes // 60

        if elapsed_hours < 24:
            self.set_status(f"{elapsed_hours}h ago")
            return

        elapsed_days = elapsed_hours // 24
        self.set_status(f"{elapsed_days}d ago")
