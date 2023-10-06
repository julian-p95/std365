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
    
    # Création d'un dictionnaire de couleurs pour chaque App Module
    color_map = {}
    unique_app_modules = df_total_counter['App module'].unique()
    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']  # Exemple de couleurs
    for i, app_module in enumerate(unique_app_modules):
        color_map[app_module] = colors[i % len(colors)]

    # Liste des modules d'application uniques
    app_modules = df_total_counter['App module'].unique().tolist()

    # Widgets pour la sélection
    app_module = st.selectbox('App Module:', app_modules)
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=50, value=10)
    
    # Filtrage des tables pour le module d'application sélectionné
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

    # Sélection des 'num_tables' tables avec le plus d'associations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table']

    # Filtrage des relations de table pour inclure seulement ces tables
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
    
    # Ajout des métadonnées aux nœuds
    for node in G.nodes():
        node_info = df_total_counter.loc[df_total_counter['Table'] == node, 'App module']
        if not node_info.empty:
            node_module = node_info.iloc[0]
            color = color_map.get(node_module, '#000000')  # Noir par défaut

            # Récupération des champs et des types pour cette table
            fields = table_field[table_field['TABLE_NAME'] == node]
            fields_desc = ", ".join([f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})" for _, row in fields.iterrows()])
        
            # Ajout des métadonnées au nœud
            title = f"Table: {node}<br>App Module: {node_module}<br>Fields: {fields_desc}"
            net.add_node(node, title=title, color=color)

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
            
    # Placeholder pour le graphique
    graph_placeholder = st.empty()
    
    # Sauvegarder en tant que fichier HTML et lire
    net.save_graph("temp.html")
    HtmlFile = open("temp.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()

    # Affichage du graphique dans Streamlit
    graph_placeholder.html(source_code, height=800)

    # Génération de la légende des couleurs
    legend_markdown = "### Légende\n"
    for app_module, color in color_map.items():
        legend_markdown += f"- **{app_module}**: ![color](https://via.placeholder.com/15/{color[1:]}?text=+) \n"
    st.markdown(legend_markdown)

    # Afficher le tableau des tables
    table_placeholder = st.empty()
    table_placeholder.table(filtered_tables[['Table', 'Total Associations']].sort_values('Total Associations', ascending=False))
