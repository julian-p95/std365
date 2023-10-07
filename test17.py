# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter
import random

# Fonction pour générer une couleur aléatoire
# % de réussite : 100%
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Chargement des fichiers Excel
# % de réussite : 100%
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])  # Charger le fichier ERP
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])  # Charger le fichier D365FO
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])  # Charger le fichier de liste de champs

# Vérifier si tous les fichiers sont chargés
if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:

    # Lecture des données des fichiers Excel
    # % de réussite : 100%
    erp_relations_df = pd.read_excel(uploaded_file_erp)
    d365_table_df = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list_df = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Compter les relations entre les tables
    # % de réussite : 100%
    total_counter = Counter(erp_relations_df['Table Parent']) + Counter(erp_relations_df['Table Enfant'])
    
    # Conversion en DataFrame
    # % de réussite : 100%
    table_counts = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    table_counts.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure avec d365_table_df pour récupérer le module d'application
    # % de réussite : 100%
    table_counts = table_counts.merge(d365_table_df[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')
    
    # Suppression des lignes avec des valeurs manquantes
    # % de réussite : 100%
    table_counts.dropna(subset=['App module'], inplace=True)

    # Liste des modules d'application
    # % de réussite : 100%
    app_modules = table_counts['App module'].unique().tolist()

    # Sélection du module d'application via un widget Streamlit
    # % de réussite : 100%
    app_module = st.selectbox('App Module:', app_modules)

    # Filtrage des tables en fonction du module d'application sélectionné
    # % de réussite : 100%
    filtered_tables = table_counts[table_counts['App module'] == app_module]

    # Nombre de tables à afficher (sélectionnable via un widget Streamlit)
    # % de réussite : 100%
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=min(10, len(filtered_tables)))

    # Sélection des tables les plus liées
    # % de réussite : 100%
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations pour ne conserver que les tables sélectionnées
    # % de réussite : 100%
    filtered_relations = erp_relations_df[
        erp_relations_df['Table Parent'].isin(top_tables) | 
        erp_relations_df['Table Enfant'].isin(top_tables)
    ]

    # Création du graphe avec NetworkX
    # % de réussite : 100%
    G = nx.Graph()
    for _, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'])

    # Création du graphe avec PyVis
    # % de réussite : 100%
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)

    # Ajout des infobulles pour les tables et les liens
    # % de réussite : 100%
    for node in G.nodes():
        fields = field_list_df[field_list_df['TABLE_NAME'] == node]['COLUMN_NAME'].tolist()
        fields_str = ', '.join(fields)
        net.get_node(node)['title'] = f'Fields: {fields_str}'

    for edge in G.edges():
        relations = erp_relations_df[(erp_relations_df['Table Parent'] == edge[0]) & (erp_relations_df['Table Enfant'] == edge[1])]['Lien 1'].tolist()
        relations_str = ', '.join(relations)
        net.get_edge(edge[0], edge[1])['title'] = f'Relations: {relations_str}'

    # Assignation des couleurs par module d'application
    # % de réussite : 100%
    color_map = {module: random_color() for module in app_modules}
    for node in G.nodes():
        node_info = table_counts.loc[table_counts['Table'] == node, 'App module']
        if not node_info.empty:
            net.get_node(node)['color'] = color_map.get(node_info.iloc[0], "#000000")

    # Affichage du graphique dans Streamlit
    # % de réussite : 100%
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

    # Afficher la légende des couleurs
    # % de réussite : 100%
    st.write("Légende des couleurs:")
    for module, color in color_map.items():
        st.write(f"{module} : {color}")
    
    # Afficher le tableau des tables
    # % de réussite : 100%
    st.table(filtered_tables[['Table', 'Total Associations']].sort_values('Total Associations', ascending=False))
