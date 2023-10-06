import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network

# Chargement des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_table_field = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_table_field:
    erp_all_table_relations = pd.read_excel(uploaded_file_erp)
    d365fo = pd.read_excel(uploaded_file_d365fo)
    table_field = pd.read_excel(uploaded_file_table_field, sheet_name="Field List")

    # Création du graphe avec NetworkX
    G = nx.Graph()
    for _, row in erp_all_table_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])

    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

    # Ajout des nœuds d'abord
    for node in G.nodes():
        net.add_node(node)

    # Ajout des métadonnées aux nœuds
    for node in net.nodes:
        node_id = node['id']
        node_info = d365fo.loc[d365fo['Table name'] == node_id, 'App module']
        fields = table_field.loc[table_field['TABLE_NAME'] == node_id, 'COLUMN_NAME']
        
        if not node_info.empty and not fields.empty:
            title = f"Table: {node_id}<br>App Module: {node_info.iloc[0]}<br>Fields: {', '.join(fields)}"
            node['title'] = title

    # Ajout des arêtes
    for parent, child, data in G.edges(data=True):
        net.add_edge(parent, child, title=data.get('title', ''))

    # Sauvegarde et affichage
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)
