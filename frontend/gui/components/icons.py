import logging
from functools import lru_cache
from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer


ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"
LOGGER = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _tinted_pixmap_cached(name: str, color: str, size: int, ratio: float) -> QPixmap:
    path = ICONS_DIR / f"{name}.svg"
    renderer = QSvgRenderer(str(path))
    if not path.is_file() or not renderer.isValid():
        LOGGER.warning("Icon file missing or invalid: %s", path.name)
        pixmap = QPixmap(int(size * ratio), int(size * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap

    pixmap = QPixmap(int(size * ratio), int(size * ratio))
    pixmap.setDevicePixelRatio(ratio)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return pixmap


def tinted_pixmap(name: str, color: str, size: int = 20) -> QPixmap:
    screen = QGuiApplication.primaryScreen()
    ratio = float(screen.devicePixelRatio()) if screen is not None else 1.0
    return _tinted_pixmap_cached(name, color, size, ratio)
