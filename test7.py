import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter

# Chargement des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_table_field = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

if uploaded_file_erp is not None and uploaded_file_d365fo is not None and uploaded_file_table_field is not None:
    erp_all_table_relations = pd.read_excel(uploaded_file_erp)
    d365fo = pd.read_excel(uploaded_file_d365fo)
    table_field = pd.read_excel(uploaded_file_table_field)

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

    # Création du graphe avec NetworkX
    G = nx.Graph()
    for idx, row in erp_all_table_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])

    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

    # Ajout des nœuds avec métadonnées
    for node in G.nodes():
        node_info = df_total_counter.loc[df_total_counter['Table'] == node, 'App module']
        if not node_info.empty:
            node_module = node_info.iloc[0]
            
            # Récupération des champs et des types pour cette table
            fields = table_field[table_field['TABLE_NAME'] == node]
            fields_desc = ", ".join([f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})" for _, row in fields.iterrows()])
            
            # Ajout des métadonnées au nœud
            title = f"Table: {node}<br>App Module: {node_module}<br>Fields: {fields_desc}"
            net.add_node(node, title=title)
    
    # Ajout des arêtes
    for edge in G.edges(data=True):
        parent, child, data = edge
        net.add_edge(parent, child, title=data['title'])
    
    # Sauvegarder en tant que fichier HTML et lire
    net.save_graph("temp.html")
    HtmlFile = open("temp.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()

    # Affichage du graphique dans Streamlit avec 'components.html'
    components.html(source_code, height=800)
