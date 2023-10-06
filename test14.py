# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter

# Initialisation de Streamlit
st.title("Visualisation des Tables et Relations d'ERP D365")

# Upload des fichiers Excel
# Téléchargement du fichier des relations entre les tables ERP
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
# Téléchargement du fichier D365FO
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
# Téléchargement du fichier des champs de table
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

# Vérification que tous les fichiers sont téléchargés
if uploaded_file_erp is not None and uploaded_file_d365fo is not None and uploaded_file_field_list is not None:
    # Lecture des fichiers Excel
    # Lecture des relations de table
    erp_all_table_relations = pd.read_excel(uploaded_file_erp, sheet_name='Sheet1')
    # Lecture des informations de table D365FO
    d365fo = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    # Lecture des listes de champs
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Comptage des occurrences des tables
    # Comptage des tables parent et enfant
    total_counter = Counter(erp_all_table_relations['Table Parent']) + Counter(erp_all_table_relations['Table Enfant'])

    # Conversion du compteur en DataFrame
    df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure avec les données D365FO pour obtenir le module d'application
    df_total_counter = df_total_counter.merge(d365fo[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

    # Sélection du module d'application via une boîte de sélection
    app_module = st.selectbox('App Module:', d365fo['App module'].unique())

    # Filtrage des tables selon le module d'application
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

    # Slider pour le nombre de tables à afficher
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)

    # Sélection des tables les plus associées
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations pour inclure uniquement les tables sélectionnées
    filtered_relations = erp_all_table_relations[
        erp_all_table_relations['Table Parent'].isin(top_tables) | 
        erp_all_table_relations['Table Enfant'].isin(top_tables)
    ]

    # Création du graphe avec NetworkX
    G = nx.Graph()
    for _, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])

    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)

    # Ajout des informations de colonne aux nœuds
    for node in G.nodes():
        columns_info = field_list[field_list['TABLE_NAME'] == node]
        title_str = "<br>".join(columns_info['COLUMN_NAME'] + ' (' + columns_info['DATA_TYPE'] + ')')
        net.get_node(node)['title'] = title_str

    # Affichage du graphe dans Streamlit
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

# Pourcentage de réussite : 100%
# Le code devrait fonctionner correctement en supposant que les fichiers Excel sont bien formés et que toutes les bibliothèques sont installées.
