import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter

# Upload des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])  # Upload ERP
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])  # Upload D365FO

if uploaded_file_erp is not None and uploaded_file_d365fo is not None:
    erp_all_table_relations = pd.read_excel(uploaded_file_erp)
    d365fo = pd.read_excel(uploaded_file_d365fo)

    # Comptage des occurrences
    parent_counter = Counter(erp_all_table_relations['Table Parent'])
    child_counter = Counter(erp_all_table_relations['Table Enfant'])
    total_counter = parent_counter + child_counter

    # Conversion en DataFrame
    df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure avec le DataFrame d365fo
    df_total_counter = df_total_counter.merge(d365fo[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

    # Suppression des NaN
    df_total_counter = df_total_counter.dropna(subset=['App module'])

    # Liste des modules d'application uniques
    app_modules = df_total_counter['App module'].unique().tolist()

    # Widgets pour la sélection
    app_module = st.selectbox('App Module:', app_modules)
    
    # Filtrage des tables pour le module d'application sélectionné
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

    # Mise à jour du slider en fonction du nombre de tables disponibles
    max_tables = len(filtered_tables)
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=max_tables, value=min(10, max_tables))  # Slider

    # Trouver les 'num_tables' tables avec le plus d'associations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table']

    # Filtrage des relations de table pour inclure seulement ces tables
    filtered_relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) | 
        erp_all_table_relations['Table Enfant'].isin(top_tables)
    ]
    
    # Sélection d'une table pour le focus
    focus_table = st.selectbox('Focus sur une table:', ['Toutes les tables'] + top_tables.tolist())  # Focus sur une table

    if focus_table != 'Toutes les tables':
        filtered_relations = filtered_relations[
            (filtered_relations['Table Parent'] == focus_table) | 
            (filtered_relations['Table Enfant'] == focus_table)
        ]
    
    # [Section graphique ici]
    
    # Afficher la légende des couleurs
    st.write("Légende des couleurs:")
    st.write(f"Module d'application sélectionné : Rouge")
    st.write(f"Autres : Vert")
    
    # [Section tableau ici]

