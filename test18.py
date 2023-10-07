import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter
import random

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Upload des fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

# Vérifier que tous les fichiers sont chargés
if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:
    erp_relations_df = pd.read_excel(uploaded_file_erp)
    d365_table_df = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list_df = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Comptage des relations
    total_counter = Counter(erp_relations_df['Table Parent']) + Counter(erp_relations_df['Table Enfant'])

    # Conversion en DataFrame
    table_counts = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    table_counts.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure pour récupérer le module
    table_counts = table_counts.merge(d365_table_df[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

    # Suppression des valeurs manquantes
    table_counts.dropna(subset=['App module'], inplace=True)

    # Liste des modules
    app_modules = table_counts['App module'].unique().tolist()

    # Sélection du module
    app_module = st.selectbox('App Module:', app_modules)

    # Filtrage des tables
    filtered_tables = table_counts[table_counts['App module'] == app_module]

    # Nombre de tables à afficher
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=min(10, len(filtered_tables)))

    # Tables les plus liées
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations
    filtered_relations = erp_relations_df[
        erp_relations_df['Table Parent'].isin(top_tables) | 
        erp_relations_df['Table Enfant'].isin(top_tables)
    ]

    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Assignation des couleurs
    color_map = {}
    for app_module in app_modules:
        color_map[app_module] = random_color()

    # Ajout des nœuds et des arêtes
    for _, row in filtered_relations.iterrows():
        parent, child = row['Table Parent'], row['Table Enfant']
        relation_info = row['Lien 1']
        
        # Récupération des champs de chaque table parent et enfant
        parent_fields = ', '.join(field_list_df[field_list_df['TABLE_NAME'] == parent]['COLUMN_NAME'].tolist())
        child_fields = ', '.join(field_list_df[field_list_df['TABLE_NAME'] == child]['COLUMN_NAME'].tolist())
        
        # Ajout des nœuds avec les champs comme titre
        net.add_node(parent, title=f"<h4>{parent}</h4><p>Champs: {parent_fields}</p>")
        net.add_node(child, title=f"<h4>{child}</h4><p>Champs: {child_fields}</p>")
        
        # Ajout des arêtes avec les informations de relation comme titre
        net.add_edge(parent, child, title=relation_info)

    # Configuration des couleurs
    for node in net.nodes:
        node_info = table_counts.loc[table_counts['Table'] == node['id'], 'App module']
        if not node_info.empty:
            node_module = node_info.iloc[0]
            node['color'] = color_map.get(node_module, "#000000")

    # Sauvegarde et affichage
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

    # Afficher la légende
    st.write("Légende des couleurs:")
    for app_module, color in color_map.items():
        st.write(f"{app_module} : {color}")

    # Afficher le tableau
    st.table(filtered_tables[['Table', 'Total Associations']].sort_values('Total Associations', ascending=False))
