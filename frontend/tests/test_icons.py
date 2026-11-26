import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtSvg import QSvgRenderer

from gui.components.icons import ICONS_DIR, tinted_pixmap
from gui.components.sidebar import ICON_MAP, NavButton, Sidebar
from gui.styles.theme import PALETTES


def luminance(hex_color):
    rgb = [
        int(hex_color[index:index + 2], 16) / 255.0
        for index in (1, 3, 5)
    ]
    linear = [
        value / 12.92 if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in rgb
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first, second):
    lighter = max(luminance(first), luminance(second))
    darker = min(luminance(first), luminance(second))
    return (lighter + 0.05) / (darker + 0.05)


class IconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_icon_assets_are_valid_and_nonblank(self):
        names = set(ICON_MAP.values()) | {"logout"}
        for name in names:
            path = ICONS_DIR / f"{name}.svg"
            with self.subTest(icon=name):
                self.assertTrue(path.is_file())
                renderer = QSvgRenderer(str(path))
                self.assertTrue(renderer.isValid())

                pixmap = tinted_pixmap(name, "#FFFFFF", 20)
                image = pixmap.toImage()
                nontransparent = sum(
                    1
                    for y in range(image.height())
                    for x in range(image.width())
                    if image.pixelColor(x, y).alpha() > 0
                )
                self.assertGreaterEqual(nontransparent, 30)

    def test_theme_icon_contrast(self):
        pairs = (
            ("sidebar_text", "sidebar_bg"),
            ("sidebar_hover_text", "sidebar_hover_bg"),
            ("sidebar_active_text", "sidebar_active_bg"),
            ("tint_text", "tint_bg"),
        )
        for theme_name, palette in PALETTES.items():
            for foreground, background in pairs:
                with self.subTest(theme=theme_name, pair=(foreground, background)):
                    ratio = contrast_ratio(
                        palette[foreground],
                        palette[background],
                    )
                    self.assertGreaterEqual(ratio, 3.0)

    def test_sidebar_has_nav_and_logout_buttons(self):
        sidebar = Sidebar()
        nav_buttons = sidebar.findChildren(NavButton)
        self.assertEqual(len(nav_buttons), 9)
        self.assertEqual(len(sidebar.buttons), 8)
        sidebar.deleteLater()
