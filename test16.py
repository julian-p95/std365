import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter
import random

# Générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Chargement des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:

    # Lecture des données
    erp_relations_df = pd.read_excel(uploaded_file_erp)
    d365_table_df = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list_df = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Comptage des relations
    total_counter = Counter(erp_relations_df['Table Parent']) + Counter(erp_relations_df['Table Enfant'])

    # Conversion en DataFrame
    table_counts = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    table_counts.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure avec d365_table_df
    table_counts = table_counts.merge(d365_table_df[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

    # Suppression des NaN
    table_counts.dropna(subset=['App module'], inplace=True)

    # Liste des modules
    app_modules = table_counts['App module'].unique().tolist()

    # Sélection du module
    app_module = st.selectbox('App Module:', app_modules)

    # Filtrage des tables du module sélectionné
    filtered_tables = table_counts[table_counts['App module'] == app_module]

    # Nombre de tables à afficher
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=min(10, len(filtered_tables)))

    # Tables avec le plus de relations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations
    filtered_relations = erp_relations_df[
        erp_relations_df['Table Parent'].isin(top_tables) | 
        erp_relations_df['Table Enfant'].isin(top_tables)
    ]

    # Création du graphe
    G = nx.Graph()
    for _, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'])

    # Création du graphe PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)

    # Couleurs par module
    color_map = {module: random_color() for module in app_modules}
    for node in G.nodes():
        node_info = table_counts.loc[table_counts['Table'] == node, 'App module']
        if not node_info.empty:
            net.get_node(node)['color'] = color_map.get(node_info.iloc[0], "#000000")

    # Affichage du graphe
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

    # Légende des couleurs
    st.write("Légende des couleurs:")
    for module, color in color_map.items():
        st.write(f"{module} : {color}")

    # Tableau des tables
    table_to_show = filtered_tables.nlargest(num_tables, 'Total Associations')[['Table', 'Total Associations', 'App module']]
    st.table(table_to_show.sort_values('Total Associations', ascending=False))
