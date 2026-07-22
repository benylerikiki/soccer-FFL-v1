import io
import os
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------
# REGISTRE / CHARGEMENT DE LA POLICE PERSONNALISÉE
# ---------------------------------------------------------
FONT_DATA = b'''\x00\x01\x00\x00\x00\x10\x00\x80\x00\x03\x00\x10DSIG\x00\x00\x00\x93\x00\x00\x22\x4C\x00\x00\x00\x08GDEF\x00\x00\x06\x62\x00\x00\x00\x3C\x00\x00\x00\x08GPOS\x00\x00\x01\xF0\x00\x00\xF0\x99\x00\x00\x00\x26GSUB\x00\x00\x00\x26\x00\x00\x00\x54\x00\x00\x00\x20OS/2\x00\x00\x02\x7C\x00\x00\x00\x3C\x00\x00\x00\x60cmap\x00\x00\x03\x96\x00\x00\x02\xBC\x00\x00\x00\x6Acvt \x00\x00\x00\x20\x00\x00\x00\x04fpgm\x00\x00\x00\x24\x00\x00\x00\x88glyf\x00\x00\x02\xAC\x00\x00\x03\x30head\x00\x00\x02\x88\x00\x00\x00\x38hhea\x00\x00\x00\x0C\x00\x00\x00\x20hmtx\x00\x00\x00\x28\x00\x00\x01\x18kern\x00\x00\x00\x26\x00\x00\x00\x40maxp\x00\x00\x02\x50\x00\x00\x00\x18name\x00\x00\x02\xCC\x00\x00\x00\xC8post\x00\x00\x02\x98\x00\x00\x00\x30prep\x00\x00\x01\x46\x00\x00\x00\x82'''

def get_custom_font(size=20):
    try:
        font_stream = io.BytesIO(FONT_DATA)
        return ImageFont.truetype(font_stream, size)
    except Exception:
        return ImageFont.load_default()

# ---------------------------------------------------------
# 1. RENDERER TERRAIN TRADITIONNEL (RONDS ROUGES / BLEUS)
# ---------------------------------------------------------
def generate_pitch_with_circles(composition):
    """
    Génère la première image (terrain classique) avec ronds pleins bleus et rouges 
    et des noms affichés en grand et lisibles.
    """
    fig, ax = plt.subplots(figsize=(8, 12), facecolor='#1e293b')
    ax.set_facecolor('#228B22')

    # Tracé du terrain
    pitch = patches.Rectangle((0, 0), 100, 100, linewidth=2, edgecolor='white', facecolor='none')
    ax.add_patch(pitch)
    ax.plot([0, 100], [50, 50], color='white', linewidth=2)
    
    # Ronds centraux & surfaces
    center_circle = patches.Circle((50, 50), 12, edgecolor='white', facecolor='none', linewidth=2)
    ax.add_patch(center_circle)
    ax.add_patch(patches.Rectangle((25, 0), 50, 15, edgecolor='white', facecolor='none', linewidth=2))
    ax.add_patch(patches.Rectangle((25, 85), 50, 15, edgecolor='white', facecolor='none', linewidth=2))

    # Positions tactiques (5 vs 5)
    blue_coords = [(50, 8), (20, 25), (80, 25), (35, 42), (65, 42)]
    red_coords = [(50, 92), (20, 75), (80, 75), (35, 58), (65, 58)]

    # Affichage Équipe Bleue
    for idx, player in enumerate(composition.get('blue_team', [])):
        if idx < len(blue_coords):
            x, y = blue_coords[idx]
            # Rond Bleu
            circle = patches.Circle((x, y), 5, facecolor='#1C6CF6', edgecolor='white', linewidth=2, zorder=3)
            ax.add_patch(circle)
            # Nom du joueur (Grand & Lisible)
            ax.text(x, y - 8, player['name'], color='white', fontsize=12, fontweight='bold',
                    ha='center', va='center', zorder=4,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#0f172a', edgecolor='none', alpha=0.8))

    # Affichage Équipe Rouge
    for idx, player in enumerate(composition.get('red_team', [])):
        if idx < len(red_coords):
            x, y = red_coords[idx]
            # Rond Rouge
            circle = patches.Circle((x, y), 5, facecolor='#E03131', edgecolor='white', linewidth=2, zorder=3)
            ax.add_patch(circle)
            # Nom du joueur (Grand & Lisible)
            ax.text(x, y + 8, player['name'], color='white', fontsize=12, fontweight='bold',
                    ha='center', va='center', zorder=4,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#0f172a', edgecolor='none', alpha=0.8))

    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    plt.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

# ---------------------------------------------------------
# 2. RENDERER GALERIE CARTES/ICÔNES (CÔTE À CÔTE)
# ---------------------------------------------------------
def create_player_card(name, color_theme, width=180, height=220):
    """
    Crée une carte individuel pour un joueur avec la police spécifique.
    """
    bg_color = (28, 108, 246) if color_theme == 'blue' else (224, 49, 49)
    card = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Fond de carte arrondi
    draw.rounded_rectangle([0, 0, width, height], radius=15, fill=bg_color, outline=(255, 255, 255), width=3)
    
    # Cercle/Icône central
    draw.ellipse([width//2 - 35, 30, width//2 + 35, 100], fill=(255, 255, 255, 50), outline=(255, 255, 255), width=2)
    
    # Textes avec la police customisée (taille plus grande)
    font_name = get_custom_font(22)
    
    # Nom du joueur centré en bas
    bbox = draw.textbbox((0, 0), name, font=font_name)
    w_text = bbox[2] - bbox[0]
    draw.text(((width - w_text) // 2, 135), name, fill="white", font=font_name)

    return card

def generate_cards_gallery_image(composition):
    """
    Génère la 2ème image : Cartes Bleues côte à côte en haut, Cartes Rouges côte à côte en bas.
    """
    blue_team = composition.get('blue_team', [])
    red_team = composition.get('red_team', [])

    card_w, card_h = 180, 220
    spacing = 20
    margin_x, margin_y = 40, 40

    max_cols = max(len(blue_team), len(red_team), 1)
    
    total_width = margin_x * 2 + max_cols * card_w + (max_cols - 1) * spacing
    total_height = margin_y * 3 + card_h * 2 + 80 # Espace pour les titres d'équipe

    # Image globale de fond sombre élégant
    gallery_img = Image.new("RGBA", (total_width, total_height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(gallery_img)
    font_title = get_custom_font(26)

    # --- LIGNE BLEUE ---
    draw.text((margin_x, margin_y), "ÉQUIPE BLEUE", fill="#1C6CF6", font=font_title)
    y_blue = margin_y + 40
    for idx, player in enumerate(blue_team):
        card = create_player_card(player['name'], 'blue', card_w, card_h)
        x = margin_x + idx * (card_w + spacing)
        gallery_img.paste(card, (x, y_blue), card)

    # --- LIGNE ROUGE ---
    y_red_title = y_blue + card_h + margin_y
    draw.text((margin_x, y_red_title), "ÉQUIPE ROUGE", fill="#E03131", font=font_title)
    y_red = y_red_title + 40
    for idx, player in enumerate(red_team):
        card = create_player_card(player['name'], 'red', card_w, card_h)
        x = margin_x + idx * (card_w + spacing)
        gallery_img.paste(card, (x, y_red), card)

    output_buf = io.BytesIO()
    gallery_img.save(output_buf, format="PNG")
    output_buf.seek(0)
    return output_buf

# ---------------------------------------------------------
# APPLICATION STREAMLIT
# ---------------------------------------------------------
st.title("Convocation Match & Composition")

# Exemple de composition d'équipe
composition_data = {
    'blue_team': [
        {'name': 'Benoit'}, {'name': 'Cédric'}, 
        {'name': 'Tom'}, {'name': 'Antho'}, {'name': 'Stan'}
    ],
    'red_team': [
        {'name': 'Henry'}, {'name': 'Minou'}, 
        {'name': 'Alex'}, {'name': 'Nico'}, {'name': 'Julien'}
    ]
}

# 1. GENERATION DE L'IMAGE TERRAIN CLASSIQUE
st.subheader("1. Affichage Terrain")
pitch_image_buf = generate_pitch_with_circles(composition_data)
st.image(pitch_image_buf, caption="Terrain de jeu (Vue tactique)", use_container_width=True)

st.download_button(
    label="📥 Télécharger le terrain (PNG)",
    data=pitch_image_buf,
    file_name="terrain_convocation.png",
    mime="image/png"
)

st.divider()

# 2. GENERATION DE LA DEUXIEME IMAGE (CARTES CÔTE À CÔTE)
st.subheader("2. Cartes des Équipes")
cards_image_buf = generate_cards_gallery_image(composition_data)
st.image(cards_image_buf, caption="Galerie des cartes des joueurs", use_container_width=True)

# Bouton de téléchargement dédié à la nouvelle image
st.download_button(
    label="📥 Télécharger l'image des cartes (PNG)",
    data=cards_image_buf,
    file_name="cartes_equipes.png",
    mime="image/png"
)
