import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import itertools
import re

# Configuration de la page Streamlit
st.set_page_config(page_title="Soccer FFL Kompo", page_icon="⚽", layout="wide")

# 📳 FORCE LE MODE GRILLE
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

TEXT_OPTIONS = ["1 - Pas bon", "2 - Moyennement bon", "3 - Assez bon", "4 - Très bon"]

def text_to_score(text_value):
    text_str = str(text_value)
    if text_str.startswith("1"): return 1
    if text_str.startswith("2"): return 2
    if text_str.startswith("3"): return 3
    if text_str.startswith("4"): return 4
    return 2

DATA_FILE = 'database_joueurs_v2.xlsx'       

def load_data():
    if os.path.exists(DATA_FILE):
        try: 
            df = pd.read_excel(DATA_FILE)
            for col in ["Attaque", "Défense", "Collectif"]:
                df[col] = df[col].apply(lambda x: x if str(x) in TEXT_OPTIONS else TEXT_OPTIONS[1])
            return df
        except Exception: 
            pass
            
    return pd.DataFrame({
        "Nom du Joueur": ["Antho", "Cyril V", "Apou", "Benoit", "Nico P", "Mouyss", "Cédric", "Nico M", "David", "Cyril L"],
        "Attaque": ["4 - Très bon", "2 - Moyennement bon", "3 - Assez bon", "4 - Très bon", "2 - Moyennement bon", "3 - Assez bon", "1 - Pas bon", "3 - Assez bon", "2 - Moyennement bon", "1 - Pas bon"],
        "Défense": ["2 - Moyennement bon", "4 - Très bon", "2 - Moyennement bon", "1 - Pas bon", "4 - Très bon", "1 - Pas bon", "4 - Très bon", "2 - Moyennement bon", "3 - Assez bon", "3 - Assez bon"],
        "Collectif": ["3 - Assez bon", "4 - Très bon", "3 - Assez bon", "2 - Moyennement bon", "3 - Assez bon", "2 - Moyennement bon", "3 - Assez bon", "2 - Moyennement bon", "2 - Moyennement bon", "2 - Moyennement bon"]
    })

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

if 'players_df' not in st.session_state:
    st.session_state.players_df = load_data()

# Initialisation du set de stockage des joueurs cochés via convocation
if 'auto_selected' not in st.session_state:
    st.session_state.auto_selected = set()

# Synchronisation forcée avec l'état des checkbox individuelles
for name in st.session_state.auto_selected:
    st.session_state[f"select_{name}"] = True

# --- DESSIN DU TERRAIN ---
def draw_combined_field(t1, t2):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    fig.patch.set_facecolor('#226343')
    ax.set_facecolor('#226343')
    
    ax.plot([0, 100, 100, 0, 0], [0, 0, 60, 60, 0], color='white', linewidth=2.0)
    ax.plot([50, 50], [0, 60], color='white', linewidth=2.0)
    center_circle = patches.Circle((50, 30), 9, edgecolor='white', facecolor='none', linewidth=1.5)
    ax.add_patch(center_circle)
    ax.scatter(50, 30, color='white', s=15, zorder=2)
    
    ax.add_patch(patches.Rectangle((0, 15), 12, 30, edgecolor='white', facecolor='none', linewidth=1.5))
    ax.scatter(9, 30, color='white', s=15, zorder=2)
    ax.add_patch(patches.Rectangle((88, 15), 12, 30, edgecolor='white', facecolor='none', linewidth=1.5))
    ax.scatter(91, 30, color='white', s=15, zorder=2)
    
    # Équipe 1
    pos1 = [(7, 30), (22, 14), (22, 46), (40, 18), (40, 42)]
    players1 = t1.copy()
    players1['Def_Num'] = players1['Défense'].apply(text_to_score)
    players1 = players1.sort_values(by="Def_Num", ascending=False).reset_index(drop=True)
    for i, row in players1.iterrows():
        if i >= len(pos1): break
        x, y = pos1[i]
        ax.scatter(x, y, color="#1C6CF6", s=220, edgecolors='white', linewidths=1.5, zorder=3)
        ax.text(x, y - 4.2, row['Nom du Joueur'], color='white', fontsize=11, weight='bold', ha='center', va='center', zorder=4)
        
    # Équipe 2
    pos2 = [(93, 30), (78, 14), (78, 46), (60, 18), (60, 42)]
    players2 = t2.copy()
    players2['Def_Num'] = players2['Défense'].apply(text_to_score)
    players2 = players2.sort_values(by="Def_Num", ascending=False).reset_index(drop=True)
    for i, row in players2.iterrows():
        if i >= len(pos2): break
        x, y = pos2[i]
        ax.scatter(x, y, color="#E03131", s=220, edgecolors='white', linewidths=1.5, zorder=3)
        ax.text(x, y - 4.2, row['Nom du Joueur'], color='white', fontsize=11, weight='bold', ha='center', va='center', zorder=4)
    
    t1_att = t1['Attaque'].apply(text_to_score).sum()
    t1_def = t1['Défense'].apply(text_to_score).sum()
    t1_col = t1['Collectif'].apply(text_to_score).sum()
    
    t2_att = t2['Attaque'].apply(text_to_score).sum()
    t2_def = t2['Défense'].apply(text_to_score).sum()
    t2_col = t2['Collectif'].apply(text_to_score).sum()
    
    ax.text(25, 64, f"EQUIPE 1\n(A:{t1_att} D:{t1_def} C:{t1_col})", color='#1C6CF6', fontsize=12, weight='bold', ha='center', va='center')
    ax.text(75, 64, f"EQUIPE 2\n(A:{t2_att} D:{t2_def} C:{t2_col})", color='#E03131', fontsize=12, weight='bold', ha='center', va='center')
    
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
    
    st.download_button(label="📸 Télécharger l'image (PNG)", data=buf, file_name="Compositions_FFL.png", mime="image/png", type="primary")
    st.write("---")
    
    text_whatsapp = "⚽ *COMPOSITIONS DU MATCH* ⚽\n\n"
    text_whatsapp += "🔵 *ÉQUIPE 1* :\n"
    for _, row in t1.iterrows():
        text_whatsapp += f"• {row['Nom du Joueur']}\n"
        
    text_whatsapp += "\n🔴 *ÉQUIPE 2* :\n"
    for _, row in t2.iterrows():
        text_whatsapp += f"• {row['Nom du Joueur']}\n"
        
    st.markdown("**📋 Texte à copier pour WhatsApp (Noms uniquement) :**")
    st.code(text_whatsapp, language="text")
    if st.button("Fermer"): st.rerun()


# --- INTERFACE PRINCIPALE ---
st.header("⚽ Soccer FFL Kompo")

tab1, tab2 = st.tabs(["⚖️ Équilibrage du Jour", "🏃 Gestion de la Base"])

with tab1:
    # --- MODULE D'ANALYSE AUTOMATIQUE DE CONVOCATION ---
    with st.expander("📋 Analyser une convocation WhatsApp (Optionnel)", expanded=False):
        convoc_text = st.text_area("Colle le texte brut de ta convocation ici :", height=150, placeholder="Présents : nicoP (1) , dimeh(2)...")
        
        if st.button("🔍 Extraire et Valider les Joueurs"):
            if convoc_text.strip():
                match = re.search(r"Présents\s*:\s*(.*)", convoc_text, re.IGNORECASE)
                if match:
                    raw_presents = match.group(1).split("\n")[0]
                    cleaned_line = re.sub(r"\(\s*\d+\s*\)", "", raw_presents)
                    extracted_names = [n.strip() for n in re.split(r"[, ]+", cleaned_line) if n.strip()]
                    
                    db_names = st.session_state.players_df["Nom du Joueur"].values
                    db_names_lower = {name.lower(): name for name in db_names}
                    
                    found_players = set()
                    unknown_names = []
                    
                    for name in extracted_names:
                        if name.lower() in db_names_lower:
                            found_players.add(db_names_lower[name.lower()])
                        else:
                            unknown_names.append(name)
                    
                    st.session_state.auto_selected = found_players
                    
                    # On force l'activation dans le session_state des checkbox
                    for p_name in found_players:
                        st.session_state[f"select_{p_name}"] = True
                    
                    if unknown_names:
                        st.warning(f"⚠️ {len(unknown_names)} joueur(s) inconnu(s) détecté(s) !")
                        st.session_state.unknown_names = unknown_names
                    else:
                        st.success(f"✅ {len(found_players)} joueurs importés et cochés avec succès !")
                        st.rerun()
                else:
                    st.error("Le mot 'Présents :' n'a pas été trouvé dans le texte.")
            else:
                st.error("Le texte est vide.")

    # Formulaire dynamique si des joueurs inconnus ont été détectés
    if 'unknown_names' in st.session_state and st.session_state.unknown_names:
        st.info("💡 Résolution des joueurs inconnus :")
        db_names = sorted(list(st.session_state.players_df["Nom du Joueur"].values))
        
        current_unknown = st.session_state.unknown_names[0]
        st.markdown(f"Le nom **{current_unknown}** n'est pas reconnu.")
        
        choice = st.radio(f"Que faire pour '{current_unknown}' ?", ["Il correspond à un joueur existant sous un autre nom", "Créer un nouveau joueur dans la base"], key=f"choice_{current_unknown}")
        
        if choice == "Il correspond à un joueur existant sous un autre nom":
            linked_name = st.selectbox("Sélectionner le vrai profil existant :", options=db_names)
            if st.button(f"Associer {current_unknown} à {linked_name}"):
                st.session_state.auto_selected.add(linked_name)
                st.session_state[f"select_{linked_name}"] = True # Force la coche
                st.session_state.unknown_names.pop(0)
                st.rerun()
        else:
            with st.form(f"form_quick_add_{current_unknown}"):
                new_clean_name = st.text_input("Nom définitif pour la base", value=current_unknown)
                att_l = st.selectbox("Attaque", options=TEXT_OPTIONS, index=1)
                def_l = st.selectbox("Défense", options=TEXT_OPTIONS, index=1)
                col_l = st.selectbox("Collectif", options=TEXT_OPTIONS, index=2)
                
                if st.form_submit_button("💾 Enregistrer et Cocher"):
                    if new_clean_name.strip():
                        new_clean = new_clean_name.strip()
                        new_p = pd.DataFrame({
                            "Nom du Joueur": [new_clean], 
                            "Attaque": [att_l], "Défense": [def_l], "Collectif": [col_l]
                        })
                        st.session_state.players_df = pd.concat([st.session_state.players_df, new_p], ignore_index=True)
                        save_data(st.session_state.players_df)
                        
                        st.session_state.auto_selected.add(new_clean)
                        st.session_state[f"select_{new_clean}"] = True # Force la coche
                        st.session_state.unknown_names.pop(0)
                        st.rerun()

    st.write("---")
    st.subheader("Sélection des présents")
    
    df_sorted = st.session_state.players_df.sort_values(by="Nom du Joueur").reset_index(drop=True)
    counter_placeholder = st.empty()
    selected_names = []
    
    # Affichage de la grille de cases à cocher
    for i in range(0, len(df_sorted), 3):
        cols = st.columns(3)
        
        row1 = df_sorted.iloc[i]
        name1 = row1["Nom du Joueur"]
        # Vérification si le joueur doit être coché par défaut
        val1 = st.session_state.get(f"select_{name1}", name1 in st.session_state.auto_selected)
        with cols[0]:
            if st.checkbox(name1, key=f"select_{name1}", value=val1): 
                selected_names.append(name1)
                st.session_state.auto_selected.add(name1)
            else:
                st.session_state.auto_selected.discard(name1)
                
        if i + 1 < len(df_sorted):
            row2 = df_sorted.iloc[i + 1]
            name2 = row2["Nom du Joueur"]
            val2 = st.session_state.get(f"select_{name2}", name2 in st.session_state.auto_selected)
            with cols[1]:
                if st.checkbox(name2, key=f"select_{name2}", value=val2): 
                    selected_names.append(name2)
                    st.session_state.auto_selected.add(name2)
                else:
                    st.session_state.auto_selected.discard(name2)
                    
        if i + 2 < len(df_sorted):
            row3 = df_sorted.iloc[i + 2]
            name3 = row3["Nom du Joueur"]
            val3 = st.session_state.get(f"select_{name3}", name3 in st.session_state.auto_selected)
            with cols[2]:
                if st.checkbox(name3, key=f"select_{name3}", value=val3): 
                    selected_names.append(name3)
                    st.session_state.auto_selected.add(name3)
                else:
                    st.session_state.auto_selected.discard(name3)
                
    selected_players = st.session_state.players_df[st.session_state.players_df["Nom du Joueur"].isin(selected_names)]
    nb_selected = len(selected_players)
    
    if nb_selected == 10:
        counter_placeholder.success("✅ 10 joueurs sélectionnés ! Prêts à configurer les options.")
    elif nb_selected > 10:
        counter_placeholder.error(f"⚠️ Trop de joueurs sélectionnés ({nb_selected}/10). Veuillez en décocher {nb_selected - 10} !")
    else:
        counter_placeholder.info(f"🏃 Joueurs sélectionnés : {nb_selected} / 10")
        
    st.write("---")
    
    if nb_selected == 10:
        st.markdown("### ⛔ Restriction d'affinité (Optionnel)")
        j1 = st.selectbox("Sélectionner un joueur...", options=["Aucune restriction"] + sorted(selected_names), index=0)
        remaining_options = [n for n in selected_names if n != j1] if j1 != "Aucune restriction" else []
        j2 = st.selectbox("... à ne surtout pas faire jouer avec :", options=["Aucun"] + sorted(remaining_options), index=0) if j1 != "Aucune restriction" else "Aucun"
        st.write("")
        
        if st.button("⚡ Générer l'Équilibrage Parfait", type="primary"):
            players_list = selected_players.to_dict(orient='records')
            best_diff = float('inf')
            best_team1, best_team2 = None, None
            valid_combo_found = False
            
            for combo in itertools.combinations(players_list, 5):
                t1 = list(combo)
                t2 = [p for p in players_list if p not in t1]
                
                names_t1 = [p['Nom du Joueur'] for p in t1]
                names_t2 = [p['Nom du Joueur'] for p in t2]
                
                if j1 != "Aucune restriction" and j2 != "Aucun":
                    if (j1 in names_t1 and j2 in names_t1) or (j1 in names_t2 and j2 in names_t2):
                        continue
                
                valid_combo_found = True
                df_t1 = pd.DataFrame(t1)
                df_t2 = pd.DataFrame(t2)
                
                t1_att_sum = df_t1['Attaque'].apply(text_to_score).sum()
                t1_def_sum = df_t1['Défense'].apply(text_to_score).sum()
                t1_col_sum = df_t1['Collectif'].apply(text_to_score).sum()
                
                t2_att_sum = df_t2['Attaque'].apply(text_to_score).sum()
                t2_def_sum = df_t2['Défense'].apply(text_to_score).sum()
                t2_col_sum = df_t2['Collectif'].apply(text_to_score).sum()
                
                diff_att = abs(t1_att_sum - t2_att_sum)
                diff_def = abs(t1_def_sum - t2_def_sum)
                diff_col = abs(t1_col_sum - t2_col_sum)
                
                total_diff = diff_att + diff_def + diff_col
                
                if total_diff < best_diff:
                    best_diff = total_diff
                    best_team1 = df_t1
                    best_team2 = df_t2
            
            if not valid_combo_found:
                st.error("Impossible de générer les équipes avec cette contrainte.")
            else:
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
    with st.expander("➕ Ajouter manuellement un nouveau joueur"):
        with st.form("form_add"):
            name = st.text_input("Nom / Pseudo du joueur")
            att_label = st.selectbox("Niveau en Attaque", options=TEXT_OPTIONS, index=1)
            def_label = st.selectbox("Niveau en Défense", options=TEXT_OPTIONS, index=1)
            col_label = st.selectbox("Niveau en Collectif", options=TEXT_OPTIONS, index=2)
            
            if st.form_submit_button("Ajouter le joueur"):
                if name.strip() and name.strip() not in st.session_state.players_df["Nom du Joueur"].values:
                    new_player = pd.DataFrame({
                        "Nom du Joueur": [name.strip()], "Attaque": [att_label], "Défense": [def_label], "Collectif": [col_label]
                    })
                    st.session_state.players_df = pd.concat([st.session_state.players_df, new_player], ignore_index=True)
                    save_data(st.session_state.players_df)
                    st.success(f"✅ {name.strip()} ajouté dans la base Excel !")
                    st.rerun()
                else:
                    st.error("Le nom est vide ou existe déjà.")
                    
    st.write("---")
    st.subheader("📝 Modification et édition de l'effectif")
    
    edited_players = st.data_editor(
        st.session_state.players_df, 
        column_config={
            "Attaque": st.column_config.SelectboxColumn("Attaque", options=TEXT_OPTIONS, required=True),
            "Défense": st.column_config.SelectboxColumn("Défense", options=TEXT_OPTIONS, required=True),
            "Collectif": st.column_config.SelectboxColumn("Collectif", options=TEXT_OPTIONS, required=True),
        }, 
        hide_index=True, 
        use_container_width=True
    )
    
    if st.button("💾 Enregistrer les modifications", type="primary"):
        st.session_state.players_df = edited_players
        save_data(edited_players)
        st.success("✅ Fichier Excel sauvegardé avec succès !")
        st.rerun()
    
