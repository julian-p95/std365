import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network

# Étape 1: Chargement des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_table_field = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

# Étape 2: Traitement des données
if uploaded_file_erp is not None and uploaded_file_d365fo is not None and uploaded_file_table_field is not None:
    st.write("Fichiers chargés, début du traitement...")
    
    erp_all_table_relations = pd.read_excel(uploaded_file_erp)
    d365fo = pd.read_excel(uploaded_file_d365fo)
    table_field = pd.read_excel(uploaded_file_table_field, sheet_name="Field List")

    # Création du graphe avec NetworkX
    st.write("Création du graphe...")
    G = nx.Graph()
    
    for _, row in erp_all_table_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])
    
    # Création du graphe avec PyVis
    st.write("Rendu du graphe avec PyVis...")
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Ajout des nœuds avec métadonnées
    for node in G.nodes():
        node_info = d365fo.loc[d365fo['Table name'] == node, 'App module']
        fields = table_field.loc[table_field['TABLE_NAME'] == node]
        
        if not node_info.empty and not fields.empty:
            title = f"Table: {node}<br>App Module: {node_info.iloc[0]}<br>Fields: {', '.join(fields['COLUMN_NAME'])}"
            net.add_node(node, title=title)
    
    # Ajout des arêtes
    for edge in G.edges(data=True):
        parent, child, data = edge
        net.add_edge(parent, child, title=data.get('title', ''))
    
    # Sauvegarde et affichage
    st.write("Sauvegarde et affichage du graphe...")
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

    st.write("Terminé.")
