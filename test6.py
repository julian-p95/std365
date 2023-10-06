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
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=max_tables, value=min(10, max_tables))

    # Trouver les 'num_tables' tables avec le plus d'associations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table']

    # Filtrage des relations de table pour inclure seulement ces tables
    filtered_relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) | 
        erp_all_table_relations['Table Enfant'].isin(top_tables)
    ]
    
    # Création du graphe avec NetworkX
    G = nx.Graph()
    for _, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'])
    
    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)

    # Assignation des couleurs par module d'application
    color_map = {}
    for app_module in app_modules:
        color_map[app_module] = random_color()

    for node in G.nodes():
        node_info = df_total_counter.loc[df_total_counter['Table'] == node, 'App module']
        if not node_info.empty:
            node_module = node_info.iloc[0]
            net.get_node(node)['color'] = color_map.get(node_module, "#000000")
    
    # Affichage du graphique dans Streamlit
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

    # Afficher la légende des couleurs
    st.write("Légende des couleurs:")
    for app_module, color in color_map.items():
        st.write(f"{app_module} : {color}")
    
    # Afficher le tableau des tables
    st.table(filtered_tables[['Table', 'Total Associations']].sort_values('Total Associations', ascending=False))
