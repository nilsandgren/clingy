"""Color theme definitions for sticky notes."""


# Each theme defines colors for the note background, title bar, text, and accent.
THEMES = {
    "yellow": {
        "background": "#FDFD96",
        "title_bar":  "#F0F070",
        "text_color": "#333333",
        "accent":     "#E0D86E",
    },
    "pink": {
        "background": "#FFB6C1",
        "title_bar":  "#FF9CAD",
        "text_color": "#333333",
        "accent":     "#FF8095",
    },
    "blue": {
        "background": "#AEC6CF",
        "title_bar":  "#8FB3BF",
        "text_color": "#1A1A2E",
        "accent":     "#7BA3B0",
    },
    "green": {
        "background": "#B5EAD7",
        "title_bar":  "#95D4BC",
        "text_color": "#2D4A3E",
        "accent":     "#7EC8A7",
    },
    "purple": {
        "background": "#D4A5D8",
        "title_bar":  "#C48FC8",
        "text_color": "#2E1A30",
        "accent":     "#B67ABB",
    },
    "gray": {
        "background": "#D3D3D3",
        "title_bar":  "#BEBEBE",
        "text_color": "#333333",
        "accent":     "#A9A9A9",
    },
}

# Ordered list of theme names for the color picker.
THEME_NAMES = list(THEMES.keys())

DEFAULT_THEME = "yellow"


def get_theme(name: str) -> dict:
    """Return the theme dict for the given name, falling back to yellow."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])
