import winreg

def is_dark_mode():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        # AppsUseLightTheme: 0 = Dark, 1 = Light
        # SystemUsesLightTheme: 0 = Dark, 1 = Light
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except:
        return False

# Palettes
PALETTE_LIGHT = {
    "PRIMARY": "#6750A4",
    "ON_PRIMARY": "#FFFFFF",
    "PRIMARY_CONTAINER": "#EADDFF",
    "ON_PRIMARY_CONTAINER": "#21005D",
    "SECONDARY_CONTAINER": "#E8DEF8",
    "ON_SECONDARY_CONTAINER": "#1D192B",
    "SURFACE": "#FEF7FF",
    "ON_SURFACE": "#1D1B20",
    "SURFACE_VARIANT": "#E7E0EC",
    "ON_SURFACE_VARIANT": "#49454F",
    "OUTLINE": "#79747E",
    "INPUT_BG": "#FEF7FF",
}

PALETTE_DARK = {
    "PRIMARY": "#D0BCFF",
    "ON_PRIMARY": "#381E72",
    "PRIMARY_CONTAINER": "#4F378B",
    "ON_PRIMARY_CONTAINER": "#EADDFF",
    "SECONDARY_CONTAINER": "#4A4458",
    "ON_SECONDARY_CONTAINER": "#E8DEF8",
    "SURFACE": "#141218", # Dark background
    "ON_SURFACE": "#E6E1E5", # Light text
    "SURFACE_VARIANT": "#49454F",
    "ON_SURFACE_VARIANT": "#CAC4D0",
    "OUTLINE": "#938F99",
    "INPUT_BG": "#141218",
}

def get_current_palette():
    return PALETTE_DARK if is_dark_mode() else PALETTE_LIGHT

FONT_FAMILY = "Segoe UI"

def get_stylesheet():
    p = get_current_palette()
    
    return f"""
    QMainWindow {{
        background-color: {p['SURFACE']};
        font-family: "{FONT_FAMILY}";
    }}
    
    /* Specifically target central widget to ensure background coverage */
    QWidget#CentralWidget {{
        background-color: {p['SURFACE']};
    }}

    /* Global Label Styling */
    QLabel {{
        color: {p['ON_SURFACE']};
        font-size: 14px;
        background-color: transparent; /* Verify labels don't have bg */
    }}

    /* Titles */
    QLabel#HeaderTitle {{
        font-size: 24px;
        font-weight: bold;
        color: {p['ON_SURFACE']};
        margin-bottom: 10px;
    }}
    QLabel#DurationLabel {{
        color: {p['ON_SURFACE_VARIANT']};
        font-size: 12px;
    }}

    /* Text Inputs */
    QLineEdit {{
        border: 1px solid {p['OUTLINE']};
        border-radius: 4px;
        padding: 10px;
        font-size: 16px;
        background-color: {p['INPUT_BG']};
        color: {p['ON_SURFACE']};
        selection-background-color: {p['PRIMARY_CONTAINER']};
        selection-color: {p['ON_PRIMARY_CONTAINER']};
    }}
    QLineEdit:focus {{
        border: 2px solid {p['PRIMARY']};
        padding: 9px;
    }}

    /* ComboBox */
    QComboBox {{
        border: 1px solid {p['OUTLINE']};
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 100px;
        background-color: {p['INPUT_BG']};
        color: {p['ON_SURFACE']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p['INPUT_BG']};
        color: {p['ON_SURFACE']};
        selection-background-color: {p['SECONDARY_CONTAINER']};
        selection-color: {p['ON_SECONDARY_CONTAINER']};
        border: 1px solid {p['OUTLINE']};
    }}

    /* Buttons (Filled) */
    QPushButton#PrimaryButton {{
        background-color: {p['PRIMARY']};
        color: {p['ON_PRIMARY']};
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 14px;
        font-weight: 500;
        border: none;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {p['PRIMARY_CONTAINER']};
        color: {p['ON_PRIMARY_CONTAINER']};
    }}
    QPushButton#PrimaryButton:disabled {{
        background-color: {p['OUTLINE']};
        color: {p['SURFACE']};
    }}

    /* Buttons (Tonal/Secondary) */
    QPushButton#SecondaryButton {{
        background-color: {p['SECONDARY_CONTAINER']};
        color: {p['ON_SECONDARY_CONTAINER']};
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 14px;
        border: none;
    }}
    
    /* Cards */
    QFrame#SurfaceCard {{
        background-color: {p['SURFACE']};
        border: 1px solid {p['SURFACE_VARIANT']};
        border-radius: 12px;
    }}

    /* Progress Bar */
    QProgressBar {{
        border: none;
        background-color: {p['SURFACE_VARIANT']};
        border-radius: 4px;
        height: 8px;
        text-align: center;
        color: {p['ON_SURFACE']}; /* Text inside bar */
    }}
    QProgressBar::chunk {{
        background-color: {p['PRIMARY']};
        border-radius: 4px;
    }}
    """
