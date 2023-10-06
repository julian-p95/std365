import streamlit as st
import pandas as pd
import networkx as nx

# Chargement des données
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])  
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:
    erp_all_table_relations = pd.read_excel(uploaded_file_erp)
    d365fo = pd.read_excel(uploaded_file_d365fo)
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Comptage des occurrences de tables
    table_counts = erp_all_table_relations['Table Parent'].value_counts() + erp_all_table_relations['Table Enfant'].value_counts()
    table_counts = table_counts.reset_index()
    table_counts.columns = ['Table', 'Count']
    
    # Jointure avec d365fo
    table_counts = table_counts.merge(d365fo[['Table name','App module']], left_on='Table', right_on='Table name')

    # Sélection du module 
    app_module = st.selectbox('App Module:', table_counts['App module'].unique())

    # Filtrage des tables du module sélectionné
    filtered_tables = table_counts[table_counts['App module'] == app_module]

    # Slider pour limiter le nombre de tables
    num_tables = st.slider('Number of tables:', min_value=1, max_value=len(filtered_tables), value=10)

    # Tables à afficher
    top_tables = filtered_tables.nlargest(num_tables, 'Count')['Table'].tolist()

    # Filtrage des relations
    relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) | 
        erp_all_table_relations['Table Enfant'].isin(top_tables)
    ]

    # Création du graphe
    G = nx.from_pandas_edgelist(relations, 'Table Parent', 'Table Enfant')

    # Affichage du graphe
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='grey')

    # Affichage des données cuando survol d'un noeud
    for n in G.nodes():
        table_fields = field_list[field_list['TABLE_NAME'] == n]
        label = f"{n}:\n" + "\n".join(table_fields['COLUMN_NAME'])
        nx.draw_networkx_labels(G, pos, {n:label})

    st.pyplot()