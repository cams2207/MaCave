import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="Gestion de Cave à Vin",
    page_icon="🍷",
    layout="wide"
)

# Titre principal
st.title("🍷 Mon Application de Gestion de Cave")
st.markdown("Gérez facilement vos stocks de vin répartis sur vos différents lieux de stockage (Fred, Appart, St Yorre, OLS).")

# Chargement des données
@st.cache_data
def load_data():
    try:
        df_cave = pd.read_csv('Cave_Cave.csv')
    except Exception as e:
        df_cave = pd.DataFrame()
        st.error(f"Erreur lors du chargement de Cave_Cave.csv : {e}")
        
    try:
        df_ols = pd.read_csv('Cave_OLS.csv')
    except:
        df_ols = pd.DataFrame()
        
    return df_cave, df_ols

df_cave, df_ols = load_data()

# Barre latérale pour la navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Aller vers", ["Tableau de bord & Stock", "Cave OLS", "Statistiques & Analyses", "Ajouter / Modifier"])

if menu == "Tableau de bord & Stock":
    st.header("📊 Vue d'ensemble du stock principal")
    
    if not df_cave.empty:
        # Nettoyage rapide ou calculs de totaux
        total_bouteilles = df_cave['Quantité'].sum()
        fred_tot = df_cave['Reste chez Fred'].sum()
        appart_tot = df_cave['Reste Appart'].sum()
        styorre_tot = df_cave['Reste St Yorre'].sum()
        
        # Affichage des métriques clés
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Bouteilles", int(total_bouteilles) if pd.notna(total_bouteilles) else 0)
        col2.metric("Chez Fred", int(fred_tot) if pd.notna(fred_tot) else 0)
        col3.metric("Appartement", int(appart_tot) if pd.notna(appart_tot) else 0)
        col4.metric("St Yorre", int(styorre_tot) if pd.notna(styorre_tot) else 0)
        col5.metric("Références", len(df_cave))
        
        st.markdown("---")
        
        # Filtres interactifs
        st.subheader("🔍 Filtrer les vins")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        regions = ['Toutes'] + sorted(df_cave['Région'].dropna().unique().tolist())
        sel_region = col_f1.selectbox("Région", regions)
        
        domaines = ['Tous'] + sorted(df_cave['Domaine'].dropna().unique().tolist())
        sel_domaine = col_f2.selectbox("Domaine", domaines)
        
        millesimes = ['Tous'] + sorted([str(int(m)) for m in df_cave['Millesime'].dropna().unique()])
        sel_millesime = col_f3.selectbox("Millésime", millesimes)
        
        # Application des filtres
        filtered_df = df_cave.copy()
        if sel_region != 'Toutes':
            filtered_df = filtered_df[filtered_df['Région'] == sel_region]
        if sel_domaine != 'Tous':
            filtered_df = filtered_df[filtered_df['Domaine'] == sel_domaine]
        if sel_millesime != 'Tous':
            filtered_df = filtered_df[filtered_df['Millesime'] == float(sel_millesime)]
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("Aucune donnée trouvée dans `Cave_Cave.csv`.")

elif menu == "Cave OLS":
    st.header("🏷️ Gestion de la Cave OLS")
    if not df_ols.empty:
        st.dataframe(df_ols, use_container_width=True)
    else:
        st.warning("Aucune donnée trouvée dans `Cave_OLS.csv`.")

elif menu == "Statistiques & Analyses":
    st.header("📈 Statistiques de la Cave")
    if not df_cave.empty:
        # Graphique par région
        if 'Région' in df_cave.columns and 'Quantité' in df_cave.columns:
            region_df = df_cave.groupby('Région')['Quantité'].sum().reset_index()
            fig = px.bar(region_df, x='Région', y='Quantité', title="Répartition des bouteilles par Région", color='Région')
            st.plotly_chart(fig, use_container_width=True)
            
        # Graphique par millésime
        if 'Millesime' in df_cave.columns:
            millesime_df = df_cave.groupby('Millesime')['Quantité'].sum().reset_index()
            fig2 = px.line(millesime_df, x='Millesime', y='Quantité', title="Évolution des quantités par Millésime", markers=True)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Données insuffisantes pour afficher les statistiques.")

elif menu == "Ajouter / Modifier":
    st.header("➕ Ajouter une nouvelle référence")
    with st.form("add_wine_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_region = st.text_input("Région")
            new_domaine = st.text_input("Domaine")
            new_vin = st.text_input("Nom du Vin")
            new_millesime = st.number_input("Millésime", min_value=1950, max_value=2030, value=2020)
        with col2:
            new_qte = st.number_input("Quantité totale", min_value=0, value=1)
            new_fred = st.number_input("Reste chez Fred", min_value=0, value=0)
            new_appart = st.number_input("Reste Appart", min_value=0, value=0)
            new_styorre = st.number_input("Reste St Yorre", min_value=0, value=0)
            new_pu = st.number_input("Prix Unitaire (€)", min_value=0.0, value=0.0)
            
        submit = st.form_submit_button("Ajouter à la cave")
        if submit:
            new_row = {
                'Date': pd.Timestamp.today().strftime('%Y-%m-%d'),
                'Région': new_region,
                'Domaine': new_domaine,
                'Vin': new_vin,
                'Millesime': new_millesime,
                'Quantité': new_qte,
                'Reste chez Fred': new_fred,
                'Reste Appart': new_appart,
                'Reste St Yorre': new_styorre,
                'PU': new_pu
            }
            # Ajout au fichier CSV existant
            updated_df = pd.concat([df_cave, pd.DataFrame([new_row])], ignore_index=True)
            updated_df.to_csv('Cave_Cave.csv', index=False)
            st.success("Bouteille ajoutée avec succès ! Rechargez la page pour voir les modifications.")
