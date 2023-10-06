import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter
import random

# Générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Upload des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

if uploaded_file_erp is not None and uploaded_file_d365fo is not None and uploaded_file_field_list is not None:
    erp_all_table_relations = pd.read_excel(uploaded_file_erp)
    d365fo = pd.read_excel(uploaded_file_d365fo)
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Comptage des occurrences
    total_counter = Counter(erp_all_table_relations['Table Parent']) + Counter(erp_all_table_relations['Table Enfant'])

    # Conversion en DataFrame
    df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure avec d365fo pour les modules d'application
    df_total_counter = df_total_counter.merge(d365fo[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

    # Liste des modules d'application
    app_modules = d365fo['App module'].unique().tolist()

    # Sélection du module d'application
    app_module = st.selectbox('App Module:', app_modules)

    # Filtrage des tables pour le module d'application sélectionné
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

    # Slider pour le nombre de tables
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)

    # Sélection des 'num_tables' tables avec le plus grand nombre de relations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations pour inclure ces tables
    filtered_relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) |
        erp_all_table_relations['Table Enfant'].isin(top_tables)
    ]

    # Création du graphe avec NetworkX
    G = nx.Graph()
    for idx, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])

    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)

    # Assignation des couleurs et des infos de colonnes
    color_map = {}
    for node in G.nodes():
        node_info = df_total_counter[df_total_counter['Table'] == node]
        if not node_info.empty:
            node_module = node_info['App module'].values[0]
            node_color = color_map.get(node_module, random_color())
            color_map[node_module] = node_color
            net.get_node(node)['color'] = node_color

            columns_info = field_list[field_list['TABLE_NAME'] == node]
            title_str = "<br>".join(columns_info['COLUMN_NAME'] + ' (' + columns_info['DATA_TYPE'] + ')')
            net.get_node(node)['title'] = title_str

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
            net.get_edges()[edge_index]['title'] = "<br>".join(relations)

    # Affichage du graphe dans Streamlit
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)
