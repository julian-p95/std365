import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter

# Upload des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])

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
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=50, value=10)

    # Filtrage des tables pour le module d'application sélectionné
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

    # Trouver les 'num_tables' tables avec le plus d'associations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table']

    # Filtrage des relations de table pour inclure seulement ces tables
    filtered_relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) | 
        erp_all_table_relations['Table Enfant'].isin(top_tables)
    ]

    # Afficher le tableau des tables
    st.table(filtered_tables[['Table', 'Total Associations']].sort_values('Total Associations', ascending=False))

    # Sélection d'une table pour le focus
    focus_table = st.selectbox('Focus sur une table:', ['Toutes les tables'] + top_tables.tolist())
    
    if focus_table != 'Toutes les tables':
        filtered_relations = filtered_relations[
            (filtered_relations['Table Parent'] == focus_table) | 
            (filtered_relations['Table Enfant'] == focus_table)
        ]

    # Création du graphe avec NetworkX
    G = nx.Graph()
    for idx, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])

    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)

        # Définition des couleurs des nœuds en fonction du module d'application
    for node in G.nodes():
        node_info = df_total_counter.loc[df_total_counter['Table'] == node, 'App module']
        if not node_info.empty:
            node_module = node_info.iloc[0]
            color = "#FF0000" if node_module == app_module else "#00FF00"
            net.get_node(node)['color'] = color


    # Ajouter des informations au survol pour chaque arête
    for edge in G.edges():
        parent, child = edge
        relations = filtered_relations.loc[
            (filtered_relations['Table Parent'] == parent) & 
            (filtered_relations['Table Enfant'] == child), 
            'Lien 1'
        ].tolist()
        edge_data = net.get_edges()
        edge_index = next((index for (index, d) in enumerate(edge_data) if d["from"] == parent and d["to"] == child), None)
        if edge_index is not None:
            net.get_edges()[edge_index]['title'] = '<br>'.join(relations)

       # Sauvegarder en tant que fichier HTML et lire
    net.save_graph("temp.html")
    HtmlFile = open("temp.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()

    # Affichage du graphique dans Streamlit
    components.html(source_code, height=800)

