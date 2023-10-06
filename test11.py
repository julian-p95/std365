import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import random

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Uploader pour les fichiers Excel
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

# Vérifier si tous les fichiers sont uploadés
if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:
    
    # Lecture des données Excel
    erp_all_table_relations = pd.read_excel(uploaded_file_erp, sheet_name='Sheet1')
    d365fo = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')
    
    # Compter les relations entre les tables
    table_counts = erp_all_table_relations['Table Parent'].value_counts() + erp_all_table_relations['Table Enfant'].value_counts()
    table_counts = table_counts.reset_index()
    table_counts.columns = ['Table', 'Count']
    
    # Joindre les données avec d365fo pour avoir le module de l'application
    table_counts = table_counts.merge(d365fo[['Table name', 'App module']], left_on='Table', right_on='Table name')
    
    # Sélection du module de l'application via Streamlit
    app_module = st.selectbox('App Module:', table_counts['App module'].unique())
    
    # Filtrer les tables par module d'application
    filtered_tables = table_counts[table_counts['App module'] == app_module]
    
    # Slider pour limiter le nombre de tables à afficher
    num_tables = st.slider('Number of tables:', min_value=1, max_value=len(filtered_tables), value=10)
    
    # Sélection des tables les plus importantes
    top_tables = filtered_tables.nlargest(num_tables, 'Count')['Table'].tolist()
    
    # Filtrer les relations pour les tables sélectionnées
    filtered_relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) |
        erp_all_table_relations['Table Enfant'].isin(top_tables)
    ]
    
    # Initialisation du graphe
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Ajout des nœuds et des arêtes
    for _, row in filtered_relations.iterrows():
        net.add_node(row['Table Parent'])
        net.add_node(row['Table Enfant'])
        net.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])
    
    # Ajouter des informations sur le nœud et la couleur
    for node in top_tables:
        node_info = field_list[field_list['TABLE_NAME'] == node]
        title_str = "<br>".join(node_info['COLUMN_NAME'].astype(str) + ' (' + node_info['DATA_TYPE'].astype(str) + ')')
        net.get_node(node)['title'] = title_str
        net.get_node(node)['color'] = random_color()
    
    # Affichage du graphe
    net.show("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()

    st.components.v1.html(source_code, height=800)
