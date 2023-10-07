import streamlit as st
import pandas as pd
from pyvis.network import Network
from collections import Counter
import random

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Upload des fichiers Excel
uploaded_file_erp = st.file_uploader("Télécharger erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Télécharger D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Télécharger Table and Field List.xlsx", type=['xlsx'])

if uploaded_file_erp is not None and uploaded_file_d365fo is not None and uploaded_file_field_list is not None:
    erp_all_table_relations = pd.read_excel(uploaded_file_erp, sheet_name='Sheet1')
    d365fo = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Comptage des occurrences
    total_counter = Counter(erp_all_table_relations['Table Parent']) + Counter(erp_all_table_relations['Table Enfant'])
    df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure pour récupérer les modules d'application
    df_total_counter = df_total_counter.merge(d365fo[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')
    app_modules = d365fo['App module'].unique().tolist()

    # Sélection du module d'application
    app_module = st.selectbox('Module d\'Application:', app_modules)
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations
    filtered_relations = erp_all_table_relations[
        (erp_all_table_relations['Table Parent'].isin(top_tables)) |
        (erp_all_table_relations['Table Enfant'].isin(top_tables))
    ]

    # Initialisation du graphe
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

    # Ajout des nœuds et des arêtes
    for table in top_tables:
        color = random_color()
        columns_info = field_list[field_list['TABLE_NAME'] == table]
        title_str = "<br>".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
        net.add_node(table, title=title_str, color=color)

    for _, row in filtered_relations.iterrows():
        if row['Table Parent'] in top_tables and row['Table Enfant'] in top_tables:
            net.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])

    # Affichage du graphe
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)
