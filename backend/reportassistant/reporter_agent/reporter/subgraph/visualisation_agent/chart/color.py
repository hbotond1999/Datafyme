import random
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ColorPalette:
    colorIndex: int = 0
    opacity: float = 0.4  # 1.0
    colors = [
        "#fd7f6f",
        "#7eb0d5",
        "#b2e061",
        "#bd7ebe",
        "#ffb55a",
        "#ffee65",
        "#beb9db",
        "#fdcce5",
        "#8bd3c7",
        "#115f9a",
        "#1984c5",
        "#22a7f0",
        "#48b5c4",
        "#76c68f",
        "#a6d75b",
        "#c9e52f",
        "#d0ee11",
        "#d0f400",
        "#ffb400",
        "#d2980d",
        "#a57c1b",
        "#786028",
        "#363445",
        "#48446e",
        "#5e569b",
        "#776bcd",
        "#9080ff"
    ]

    def next_color(self):
        if self.colorIndex < len(self.colors):
            color = self.colors[self.colorIndex]
            self.colorIndex += 1
        else:
            # Generate a random hex color
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        return color

    def get_colors(self, number: int) -> Tuple[list, list]:
        colors_without_opacity = []
        colors_with_opacity = []
        for i in range(number):
            color = self.next_color()
            colors_without_opacity.append(color)
            colors_with_opacity.append(self._apply_opacity(color))
        return colors_without_opacity, colors_with_opacity

    def _apply_opacity(self, hex_color: str) -> str:
        """Converts a hex color to RGBA format with the current opacity."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {self.opacity})"
