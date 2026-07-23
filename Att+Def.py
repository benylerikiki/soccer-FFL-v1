import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import io
import itertools
import re
import base64

# Fichiers requis
DATA_FILE = 'database_joueurs_v2.xlsx'       
BLUE_CARD_PATH = 'card_blue.png'
RED_CARD_PATH = 'card_red.png'
FONT_PATH = 'FootballAttack.otf'
LOGO_PATH = 'icon_ffl.png'
VIDEO_PATH = 'FFL_Intro.mp4'

# --- 1. CHARGEMENT DE L'IMAGE POUR STREAMLIT ---
app_icon = "⚽"
if os.path.exists(LOGO_PATH):
    try:
        app_icon = Image.open(LOGO_PATH)  # Streamlit accepte directement les objets PIL Image
    except Exception:
        app_icon = "⚽"

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Soccer FFL Kompo", 
    page_icon=app_icon, 
    layout="wide"
)

# --- 2. INJECTION JAVASCRIPT / CSS POUR FORCER L'ICÔNE MOBILES ET WEBS ---
ICON_PATH = LOGO_PATH if os.path.exists(LOGO_PATH) else None

if ICON_PATH:
    with open(ICON_PATH, "rb") as f:
        icon_bytes = f.read()
    icon_b64 = base64.b64encode(icon_bytes).decode('utf-8')
    
    # On force dynamiquement l'emplacement du favicon dans le VRAI <head> via JavaScript
    pwa_javascript_fix = f"""
        <script>
            var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
            link.type = 'image/png';
            link.rel = 'shortcut icon';
            link.href = 'data:image/png;base64,{icon_b64}';
            document.getElementsByTagName('head')[0].appendChild(link);

            var appleLink = document.createElement('link');
            appleLink.rel = 'apple-touch-icon';
            appleLink.sizes = '180x180';
            appleLink.href = 'data:image/png;base64,{icon_b64}';
            document.getElementsByTagName('head')[0].appendChild(appleLink);
        </script>
    """
    st.markdown(pwa_javascript_fix, unsafe_allow_html=True)
