from __future__ import annotations
import sys

from PySide6.QtWidgets import QApplication
from radiator.window import RadiatorWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Info Radiator")

    window = RadiatorWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
