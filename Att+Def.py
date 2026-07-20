import streamlit as st
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="Foot 5 - Gestion & Équilibrage", page_icon="⚽", layout="wide")

# Fichier Excel source / sauvegarde
EXCEL_FILE = 'Gestion_Equipes_Foot5_V3.xlsx'

# --- CHARGEMENT DES DONNÉES ---
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            # Charger la liste des joueurs (on saute les lignes d'entête décoratives)
            df = pd.read_excel(EXCEL_FILE, sheet_name='Liste des Joueurs', skiprows=3)
            # Nettoyage des colonnes nommées anonymement
            df = df.dropna(subset=["Nom du Joueur"])
            df = df[["Nom du Joueur", "Attaque (1-10)", "Défense (1-10)", "Note Globale"]]
            return df
        except Exception:
            pass
    
    # Base de données par défaut si le fichier n'est pas trouvé ou corrompu
    return pd.DataFrame({
        "Nom du Joueur": ["Benoit", "Mouyss", "Cédric", "Antho", "David", "Nico P", "Nico M", "Cyril L", "Cyril V", "Apou"],
        "Attaque (1-10)": [9, 8, 4, 6, 7, 3, 9, 6, 5, 6],
        "Défense (1-10)": [7, 4, 9, 6, 5, 7, 6, 5, 8, 4],
        "Note Globale": [8.0, 6.0, 6.5, 6.0, 6.0, 5.0, 7.5, 5.5, 6.5, 5.0]
    })

# Initialisation de la session de rechargement
if 'players_df' not in st.session_state:
    st.session_state.players_df = load_data()

# --- TITRE DE L'APPLICATION ---
st.title("⚽ Gestion & Équilibrage Avancé - Foot 5")
st.write("Gérez vos joueurs et générez des équipes équilibrées instantanément.")

# --- NAVIGATION VIA NAVIGATION BAR / TABS ---
tab1, tab2 = st.tabs(["⚖️ Équilibrage des Équipes", "🏃 Base des Joueurs"])

# ==========================================
# TAB 1 : ÉQUILIBRAGE DES ÉQUIPES
# ==========================================
with tab1:
    st.header("Sélection des 10 joueurs présents")
    
    df_pool = st.session_state.players_df.copy()
    
    # Case à cocher pour la présence
    df_pool.insert(0, "Présent", False)
    
    # Utilisation du data_editor de Streamlit pour cocher rapidement
    edited_df = st.data_editor(
        df_pool,
        column_config={
            "Présent": st.column_config.CheckboxColumn(help="Cochez les 10 joueurs du jour"),
            "Note Globale": st.column_config.NumberColumn(format="%.1f")
        },
        disabled=["Nom du Joueur", "Attaque (1-10)", "Défense (1-10)", "Note Globale"],
        hide_index=True,
        use_container_width=True
    )
    
    # Filtrer les joueurs cochés
    selected_players = edited_df[edited_df["Présent"] == True]
    st.info(f"Joueurs sélectionnés : **{len(selected_players)} / 10**")
    
    if len(selected_players) == 10:
        if st.button("⚡ Calculer les Équipes Équilibrées", type="primary"):
            
            # Recalcul du score de tri tactique de l'Excel : Global + Attaque - Défense
            # Ajout d'un micro-ajustement pour éviter les ex-æquo parfaits lors du tri
            selected_players = selected_players.copy()
            selected_players["Score Comp"] = (
                selected_players["Note Globale"] + 
                selected_players["Attaque (1-10)"] - 
                selected_players["Défense (1-10)"]
            )
            
            # Trier par Score Comp décroissant (comme le Rang dans l'Excel)
            sorted_players = selected_players.sort_values(by="Score Comp", ascending=False).reset_index(drop=True)
            
            # Distribution selon l'algorithme "Snake Draft" de votre Excel :
            # Équipe 1 : Rangs 1, 4, 5, 8, 9 (indices 0, 3, 4, 7, 8)
            # Équipe 2 : Rangs 2, 3, 6, 7, 10 (indices 1, 2, 5, 6, 9)
            indices_t1 = [0, 3, 4, 7, 8]
            indices_t2 = [1, 2, 5, 6, 9]
            
            team1 = sorted_players.iloc[indices_t1].copy()
            team2 = sorted_players.iloc[indices_t2].copy()
            
            # Affichage des résultats en deux colonnes
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔵 ÉQUIPE 1")
                st.dataframe(team1[["Nom du Joueur", "Attaque (1-10)", "Défense (1-10)", "Note Globale"]], hide_index=True, use_container_width=True)
                
                # Statistiques Équipe 1
                t1_att = team1["Attaque (1-10)"].sum()
                t1_def = team1["Défense (1-10)"].sum()
                t1_avg = team1["Note Globale"].mean()
                
                metrics_c1, metrics_c2, metrics_c3 = st.columns(3)
                metrics_c1.metric("Totaux Attaque", int(t1_att))
                metrics_c2.metric("Totaux Défense", int(t1_def))
                metrics_c3.metric("Niveau Moyen", f"{t1_avg:.1f}")
                
            with col2:
                st.subheader("🔴 ÉQUIPE 2")
                st.dataframe(team2[["Nom du Joueur", "Attaque (1-10)", "Défense (1-10)", "Note Globale"]], hide_index=True, use_container_width=True)
                
                # Statistiques Équipe 2
                t2_att = team1["Attaque (1-10)"].sum() # Note: Simulation de votre Excel
                t2_att_real = team2["Attaque (1-10)"].sum()
                t2_def_real = team2["Défense (1-10)"].sum()
                t2_avg_real = team2["Note Globale"].mean()
                
                metrics_d1, metrics_d2, metrics_d3 = st.columns(3)
                metrics_d1.metric("Totaux Attaque", int(t2_att_real))
                metrics_d2.metric("Totaux Défense", int(t2_def_real))
                metrics_d3.metric("Niveau Moyen", f"{t2_avg_real:.1f}")
                
            # Indicateur d'équité globale
            diff_niveau = abs(t1_avg - t2_avg_real)
            if diff_niveau <= 0.5:
                st.success(f"⚖️ Match très équilibré ! Écart moyen de niveau : {diff_niveau:.2f}")
            else:
                st.warning(f"⚠️ Écart de niveau notable : {diff_niveau:.2f}")
    else:
        st.write("💡 *Veuillez cocher exactement 10 joueurs pour activer l'équilibrage.*")

# ==========================================
# TAB 2 : GESTION DE LA BASE DES JOUEURS
# ==========================================
with tab2:
    st.header("Base de données des joueurs")
    
    # Formulaire d'ajout d'un joueur
    with st.expander("➕ Ajouter un nouveau joueur"):
        with st.form("add_player_form", clear_on_submit=True):
            new_name = st.text_input("Nom du joueur")
            new_att = st.slider("Note d'Attaque (1-10)", 1, 10, 5)
            new_def = st.slider("Note de Défense (1-10)", 1, 10, 5)
            
            submit_button = st.form_submit_button("Enregistrer le joueur")
            
            if submit_button:
                if new_name.strip() == "":
                    st.error("Le nom du joueur ne peut pas être vide.")
                elif new_name in st.session_state.players_df["Nom du Joueur"].values:
                    st.error("Ce joueur existe déjà.")
                else:
                    new_global = (new_att + new_def) / 2
                    new_row = pd.DataFrame({
                        "Nom du Joueur": [new_name.strip()],
                        "Attaque (1-10)": [new_att],
                        "Défense (1-10)": [new_def],
                        "Note Globale": [new_global]
                    })
                    st.session_state.players_df = pd.concat([st.session_state.players_df, new_row], ignore_index=True)
                    st.success(f"Joueur {new_name} ajouté avec succès !")
                    st.rerun()

    # Visualisation et suppression de l'effectif actuel
    st.subheader("Effectif enregistré")
    
    # Permettre l'édition directe des notes existantes
    edited_players = st.data_editor(
        st.session_state.players_df,
        column_config={
            "Note Globale": st.column_config.NumberColumn(format="%.1f", disabled=True)
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Recalculer les notes globales automatiquement si l'utilisateur modifie l'attaque ou la défense dans le tableau
    edited_players["Note Globale"] = (edited_players["Attaque (1-10)"] + edited_players["Défense (1-10)"]) / 2
    st.session_state.players_df = edited_players

    # Supprimer un joueur
    player_to_delete = st.selectbox("Sélectionnez un joueur à supprimer", ["-- Choisir --"] + list(st.session_state.players_df["Nom du Joueur"]))
    if player_to_delete != "-- Choisir --":
        if st.button("🗑️ Supprimer définitivement", type="secondary"):
            st.session_state.players_df = st.session_state.players_df[st.session_state.players_df["Nom du Joueur"] != player_to_delete]
            st.success(f"Joueur {player_to_delete} supprimé.")
            st.rerun()
