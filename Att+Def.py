import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# Configuration de la page Streamlit
st.set_page_config(page_title="Soccer FFL Kompo", page_icon="⚽", layout="wide")

# 📳 FORCE LE MODE GRILLE (3 COLONNES INDÉFORMABLES SUR MOBILE)
st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 8px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) > div[data-testid="stColumn"] {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            flex: none !important;
        }
        div[data-testid="stCheckbox"] label {
            font-size: 13px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- CONFIGURATION DES CORRESPONDANCES DE NOTES ---
OPTIONS_ATT = {
    1: "1 - Pas bon en attaque",
    2: "2 - Moyennement bon",
    3: "3 - Plutôt bon",
    4: "4 - Très bon"
}

OPTIONS_DEF = {
    1: "1 - Pas bon en défense",
    2: "2 - Moyennement bon",
    3: "3 - Plutôt bon",
    4: "4 - Très bon"
}

OPTIONS_COL = {
    1: "1 - Pas bon en collectif",
    2: "2 - Moyennement bon",
    3: "3 - Plutôt bon",
    4: "4 - Très bon"
}

# --- FICHIERS DE STOCKAGE ---
DATA_FILE = 'database_joueurs_v2.xlsx'       

# --- FONCTION DE CHARGEMENT ---
def load_data():
    if os.path.exists(DATA_FILE):
        try: 
            return pd.read_excel(DATA_FILE)
        except Exception: 
            pass
    # Base par défaut avec le nouveau système (Attaque, Défense, Collectif)
    return pd.DataFrame({
        "Nom du Joueur": ["Antho", "Cyril V", "Apou", "Benoit", "Nico P", "Mouyss", "Cédric", "Nico M", "David", "Cyril L"],
        "Attaque": [4, 2, 3, 4, 2, 3, 1, 3, 2, 1],
        "Défense": [2, 4, 2, 1, 4, 1, 4, 2, 3, 3],
        "Collectif": [3, 4, 3, 2, 3, 2, 3, 2, 2, 2]
    })

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

if 'players_df' not in st.session_state:
    st.session_state.players_df = load_data()


# --- DESSIN DU TERRAIN AVEC LES NOUVELLES INFOS ---
def draw_combined_field(t1, t2):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    fig.patch.set_facecolor('#226343')
    ax.set_facecolor('#226343')
    
    # Lignes du terrain
    ax.plot([0, 100, 100, 0, 0], [0, 0, 60, 60, 0], color='white', linewidth=2.0)
    ax.plot([50, 50], [0, 60], color='white', linewidth=2.0)
    center_circle = patches.Circle((50, 30), 9, edgecolor='white', facecolor='none', linewidth=1.5)
    ax.add_patch(center_circle)
    ax.scatter(50, 30, color='white', s=15, zorder=2)
    
    # Surfaces
    ax.add_patch(patches.Rectangle((0, 15), 12, 30, edgecolor='white', facecolor='none', linewidth=1.5))
    ax.scatter(9, 30, color='white', s=15, zorder=2)
    ax.add_patch(patches.Rectangle((88, 15), 12, 30, edgecolor='white', facecolor='none', linewidth=1.5))
    ax.scatter(91, 30, color='white', s=15, zorder=2)
    
    # Placement Équipe 1 (Triée par Défense décroissante pour mettre les "défenseurs" derrière)
    pos1 = [(7, 30), (22, 14), (22, 46), (40, 18), (40, 42)]
    players1 = t1.sort_values(by="Défense", ascending=False).reset_index(drop=True)
    for i, row in players1.iterrows():
        if i >= len(pos1): break
        x, y = pos1[i]
        ax.scatter(x, y, color="#1C6CF6", s=220, edgecolors='white', linewidths=1.5, zorder=3)
        ax.text(x, y - 4.2, row['Nom du Joueur'], color='white', fontsize=11, weight='bold', ha='center', va='center', zorder=4)
        
    # Placement Équipe 2
    pos2 = [(93, 30), (78, 14), (78, 46), (60, 18), (60, 42)]
    players2 = t2.sort_values(by="Défense", ascending=False).reset_index(drop=True)
    for i, row in players2.iterrows():
        if i >= len(pos2): break
        x, y = pos2[i]
        ax.scatter(x, y, color="#E03131", s=220, edgecolors='white', linewidths=1.5, zorder=3)
        ax.text(x, y - 4.2, row['Nom du Joueur'], color='white', fontsize=11, weight='bold', ha='center', va='center', zorder=4)
    
    ax.text(25, 64, f"EQUIPE 1\n(A:{t1['Attaque'].sum()} D:{t1['Défense'].sum()} C:{t1['Collectif'].sum()})", color='#1C6CF6', fontsize=12, weight='bold', ha='center', va='center')
    ax.text(75, 64, f"EQUIPE 2\n(A:{t2['Attaque'].sum()} D:{t2['Défense'].sum()} C:{t2['Collectif'].sum()})", color='#E03131', fontsize=12, weight='bold', ha='center', va='center')
    
    ax.set_xlim(-4, 104)
    ax.set_ylim(-6, 68)
    ax.axis('off')
    plt.tight_layout()
    return fig


# --- POP-UP DES COMPOSITIONS ---
@st.dialog("Compositions du Match ⚽", width="large")
def show_teams_popup(t1, t2):
    st.write("Match équilibré généré avec succès ! 📸")
    
    fig_combined = draw_combined_field(t1, t2)
    st.pyplot(fig_combined, use_container_width=True)
    
    buf = io.BytesIO()
    fig_combined.savefig(buf, format="png", bbox_inches='tight', dpi=250, facecolor='#226343')
    buf.seek(0)
    
    st.download_button(
        label="📸 Télécharger l'image (PNG)",
        data=buf,
        file_name="Compositions_FFL.png",
        mime="image/png",
        type="primary" 
    )
    
    st.write("---")
    
    text_whatsapp = "⚽ *COMPOSITIONS DU MATCH EQUILIBRÉ* ⚽\n\n"
    text_whatsapp += f"🔵 *ÉQUIPE 1* (Att: {t1['Attaque'].sum()} | Def: {t1['Défense'].sum()} | Coll: {t1['Collectif'].sum()}) :\n"
    for _, row in t1.iterrows():
        text_whatsapp += f"• {row['Nom du Joueur']} (A:{row['Attaque']} D:{row['Défense']} C:{row['Collectif']})\n"
        
    text_whatsapp += f"\n🔴 *ÉQUIPE 2* (Att: {t2['Attaque'].sum()} | Def: {t2['Défense'].sum()} | Coll: {t2['Collectif'].sum()}) :\n"
    for _, row in t2.iterrows():
        text_whatsapp += f"• {row['Nom du Joueur']} (A:{row['Attaque']} D:{row['Défense']} C:{row['Collectif']})\n"
        
    st.markdown("**📋 Texte à copier pour WhatsApp :**")
    st.code(text_whatsapp, language="text")
        
    if st.button("Fermer"):
        st.rerun()


# --- INTERFACE PRINCIPALE ---
st.header("⚽ Soccer FFL Kompo")

tab1, tab2 = st.tabs(["⚖️ Équilibrage du Jour", "🏃 Gestion de la Base"])

with tab1:
    st.subheader("Sélection des présents")
    
    df_sorted = st.session_state.players_df.sort_values(by="Nom du Joueur").reset_index(drop=True)
    counter_placeholder = st.empty()
    selected_names = []
    
    # Grille de 3 colonnes forcée sur mobile
    for i in range(0, len(df_sorted), 3):
        cols = st.columns(3)
        
        # Col 1
        row1 = df_sorted.iloc[i]
        name1 = row1["Nom du Joueur"]
        with cols[0]:
            if st.checkbox(name1, key=f"select_{name1}"): selected_names.append(name1)
                
        # Col 2
        if i + 1 < len(df_sorted):
            row2 = df_sorted.iloc[i + 1]
            name2 = row2["Nom du Joueur"]
            with cols[1]:
                if st.checkbox(name2, key=f"select_{name2}"): selected_names.append(name2)
                    
        # Col 3
        if i + 2 < len(df_sorted):
            row3 = df_sorted.iloc[i + 2]
            name3 = row3["Nom du Joueur"]
            with cols[2]:
                if st.checkbox(name3, key=f"select_{name3}"): selected_names.append(name3)
                
    selected_players = st.session_state.players_df[st.session_state.players_df["Nom du Joueur"].isin(selected_names)]
    nb_selected = len(selected_players)
    
    # Affichage dynamique du compteur tout en haut
    if nb_selected == 10:
        counter_placeholder.success("✅ 10 joueurs sélectionnés ! Prêts à générer.")
    elif nb_selected > 10:
        counter_placeholder.error(f"⚠️ Trop de joueurs sélectionnés ({nb_selected}/10). Veuillez en décocher {nb_selected - 10} !")
    else:
        counter_placeholder.info(f"🏃 Joueurs sélectionnés : {nb_selected} / 10")
        
    st.write("---")
    
    if nb_selected == 10:
        if st.button("⚡ Générer l'Équilibrage Parfait", type="primary"):
            # ALGORITHME D'ÉQUILIBRAGE PAR COMBINATOIRE (Recherche de la meilleure combinaison sur les 3 critères)
            import itertools
            players_list = selected_players.to_dict(orient='records')
            best_diff = float('inf')
            best_team1, best_team2 = None, None
            
            # On teste toutes les combinaisons possibles de 5 joueurs parmi les 10
            for combo in itertools.combinations(players_list, 5):
                t1 = list(combo)
                t2 = [p for p in players_list if p not in t1]
                
                df_t1 = pd.DataFrame(t1)
                df_t2 = pd.DataFrame(t2)
                
                # Calcul des écarts sur les 3 critères fondamentaux
                diff_att = abs(df_t1['Attaque'].sum() - df_t2['Attaque'].sum())
                diff_def = abs(df_t1['Défense'].sum() - df_t2['Défense'].sum())
                diff_col = abs(df_t1['Collectif'].sum() - df_t2['Collectif'].sum())
                
                # Score global de déséquilibre (on cherche à minimiser ce total)
                total_diff = diff_att + diff_def + diff_col
                
                if total_diff < best_diff:
                    best_diff = total_diff
                    best_team1 = df_t1
                    best_team2 = df_t2
            
            st.session_state.last_team1 = best_team1
            st.session_state.last_team2 = best_team2
            
            show_teams_popup(best_team1, best_team2)

    if 'last_team1' in st.session_state and 'last_team2' in st.session_state:
        st.write("---")
        st.markdown("### 📊 Dernières équipes générées")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🔵 Équipe 1**")
            st.dataframe(st.session_state.last_team1[["Nom du Joueur", "Attaque", "Défense", "Collectif"]], hide_index=True)
        with c2:
            st.markdown("**🔴 Équipe 2**")
            st.dataframe(st.session_state.last_team2[["Nom du Joueur", "Attaque", "Défense", "Collectif"]], hide_index=True)


with tab2:
    st.header("Gestion de la base des joueurs")
    
    # AJOUT MANUEL AVEC LISTES DÉROULANTES EXPLICITES
    with st.expander("➕ Ajouter manuellement un nouveau joueur"):
        with st.form("form_add"):
            name = st.text_input("Nom / Pseudo du joueur")
            
            # Listes déroulantes basées sur les dictionnaires d'options textuelles
            att_label = st.selectbox("Niveau en Attaque", options=list(OPTIONS_ATT.keys()), format_func=lambda x: OPTIONS_ATT[x], index=1)
            def_label = st.selectbox("Niveau en Défense", options=list(OPTIONS_DEF.keys()), format_func=lambda x: OPTIONS_DEF[x], index=1)
            col_label = st.selectbox("Niveau en Collectif", options=list(OPTIONS_COL.keys()), format_func=lambda x: OPTIONS_COL[x], index=2)
            
            if st.form_submit_button("Ajouter le joueur"):
                if name.strip() and name.strip() not in st.session_state.players_df["Nom du Joueur"].values:
                    new_player = pd.DataFrame({
                        "Nom du Joueur": [name.strip()], 
                        "Attaque": [att_label], 
                        "Défense": [def_label], 
                        "Collectif": [col_label]
                    })
                    st.session_state.players_df = pd.concat([st.session_state.players_df, new_player], ignore_index=True)
                    save_data(st.session_state.players_df)
                    st.success(f"✅ {name.strip()} ajouté !")
                    st.rerun()
                else:
                    st.error("Nom vide ou déjà existant dans la base.")
                    
    st.write("---")
    st.subheader("📝 Modification et édition de l'effectif")
    
    # Édition interactive du tableau avec listes déroulantes intégrées directement dans les cellules
    edited_players = st.data_editor(
        st.session_state.players_df, 
        column_config={
            "Attaque": st.column_config.SelectboxColumn("Attaque", options=list(OPTIONS_ATT.keys()), required=True),
            "Défense": st.column_config.SelectboxColumn("Défense", options=list(OPTIONS_DEF.keys()), required=True),
            "Collectif": st.column_config.SelectboxColumn("Collectif", options=list(OPTIONS_COL.keys()), required=True),
        }, 
        hide_index=True, 
        use_container_width=True
    )
    
    if st.button("💾 Enregistrer les modifications", type="primary"):
        st.session_state.players_df = edited_players
        save_data(edited_players)
        st.success("✅ Base de données mise à jour avec succès !")
        st.rerun()
