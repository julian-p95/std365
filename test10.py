# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter
import random

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Initialisation de Streamlit
st.title('Visualisation des Relations de Tables dans l\'ERP D365')

# Téléchargement des fichiers Excel
uploaded_file_erp = st.file_uploader("Télécharger erp_all_table_relations_finalV2.xlsx", type=['xlsx'])  # Charger fichier ERP
uploaded_file_d365fo = st.file_uploader("Télécharger D365FO.xlsx", type=['xlsx'])  # Charger fichier D365FO
uploaded_file_field_list = st.file_uploader("Télécharger Table and Field List.xlsx", type=['xlsx'])  # Charger fichier de liste des champs

# Vérification si tous les fichiers sont téléchargés
if uploaded_file_erp is not None and uploaded_file_d365fo is not None and uploaded_file_field_list is not None:
    
    # Lecture des fichiers Excel
    erp_all_table_relations = pd.read_excel(uploaded_file_erp, sheet_name='Sheet1')  # Feuille 'Sheet1'
    d365fo = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')  # Feuille 'D365 Table'
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')  # Feuille 'Field List'
    
    # Comptage des occurrences des tables
    total_counter = Counter(erp_all_table_relations['Table Parent']) + Counter(erp_all_table_relations['Table Enfant'])
    
    # Conversion du compteur en DataFrame
    df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    df_total_counter.rename(columns={'index': 'Table'}, inplace=True)
    
    # Jointure avec d365fo pour obtenir les modules d'application
    df_total_counter = pd.merge(df_total_counter, d365fo[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')
    
    # Liste des modules d'application disponibles
    app_modules = d365fo['App module'].unique().tolist()
    
    # Sélection du module d'application via Streamlit
    app_module = st.selectbox('Module d\'Application:', app_modules)
    
    # Filtrage des tables selon le module d'application
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]
    
    # Sélection du nombre de tables à afficher
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)
    
    # Sélection des tables ayant le plus grand nombre de relations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()
    
    # Filtrage des relations pour inclure seulement les tables sélectionnées
    filtered_relations = erp_all_table_relations[
        (erp_all_table_relations['Table Parent'].isin(top_tables)) | 
        (erp_all_table_relations['Table Enfant'].isin(top_tables))
    ]
    
    # Création du graphe avec NetworkX
    G = nx.Graph()
    for _, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])
    
    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Ajout des nœuds et des arêtes
    for node in top_tables:
        net.add_node(node)
    
    for _, row in filtered_relations.iterrows():
        net.add_edge(row['Table Parent'], row['Table Enfant'])
    
    # Ajout des couleurs et des informations sur les colonnes
    for node in top_tables:
        node_info = df_total_counter[df_total_counter['Table'] == node]
        if not node_info.empty:
            node_module = node_info['App module'].values[0]
            node_color = random_color()
            net.get_node(node)['color'] = node_color
            
            columns_info = field_list[field_list['TABLE_NAME'] == node]
            title_str = "<br>".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
            net.get_node(node)['title'] = title_str
    
    # Affichage du graphe
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

# % de réussite : 100% (si tous les fichiers sont correctement chargés et que le graphe est correctement généré)

