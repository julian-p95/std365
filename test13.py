import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Chargement des fichiers Excel
# Charger le fichier des relations entre les tables
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])  
# Charger le fichier D365FO
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
# Charger le fichier des champs de table
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

# Vérifier si tous les fichiers sont chargés
if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:
    erp_all_table_relations = pd.read_excel(uploaded_file_erp)
    d365fo = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')


    # Compter les occurrences de chaque table
    table_counts = erp_all_table_relations['Table Parent'].append(
                   erp_all_table_relations['Table Enfant']).value_counts().reset_index()
    table_counts.columns = ['Table', 'Count']

    # Joindre avec les informations de d365fo
    table_counts = table_counts.merge(d365fo[['Table name', 'App module']], 
                                      left_on='Table', right_on='Table name', how='left')


    # Sélection du module d'application
    app_module = st.selectbox('App Module:', table_counts['App module'].dropna().unique())

    # Filtrer les tables par le module d'application
    filtered_tables = table_counts[table_counts['App module'] == app_module]

    # Slider pour limiter le nombre de tables
    num_tables = st.slider('Number of tables:', min_value=1, max_value=len(filtered_tables), value=10)

    # Sélectionner les tables à afficher
    top_tables = filtered_tables.nlargest(num_tables, 'Count')['Table']


    # Filtrer les relations pour inclure seulement les tables sélectionnées
    relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) |
        erp_all_table_relations['Table Enfant'].isin(top_tables)]

    # Créer le graphe
    G = nx.from_pandas_edgelist(relations, 'Table Parent', 'Table Enfant')

    # Dessiner le graphe
    pos = nx.spring_layout(G, seed=42)  # pour la reproductibilité
    nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='grey')

    # Ajouter les étiquettes des champs de table
    labels = {}
    for node in G.nodes():
        labels[node] = '\n'.join(
            field_list[field_list['TABLE_NAME'] == node]['COLUMN_NAME'].astype(str).tolist())
    nx.draw_networkx_labels(G, pos, labels, verticalalignment='bottom')

    st.pyplot()
