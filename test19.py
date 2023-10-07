import streamlit as st
import pandas as pd
from pyvis.network import Network
from collections import Counter
import random

# Générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Upload des fichiers
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

# Vérifier les uploads
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

    # Tous les nœuds potentiels
    all_nodes = set(filtered_relations['Table Parent']).union(set(filtered_relations['Table Enfant']))

    # Création du graphe
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

    # Couleurs
    color_map = {}
    for app_module in app_modules:
        color_map[app_module] = random_color()

    # Ajout des nœuds
    for node in all_nodes:
        fields = ', '.join(field_list_df[field_list_df['TABLE_NAME'] == node]['COLUMN_NAME'].astype(str).tolist())
        net.add_node(node, title=f"<h4>{node}</h4><p>Champs: {fields}</p>")

    # Ajout des arêtes
    for _, row in filtered_relations.iterrows():
        parent, child = row['Table Parent'], row['Table Enfant']
        relation_info = row['Lien 1']
        net.add_edge(parent, child, title=relation_info)

    # Couleurs
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

    # Légende
    st.write("Légende des couleurs:")
    for app_module, color in color_map.items():
        st.write(f"{app_module} : {color}")

    # Tableau
    st.table(filtered_tables[['Table', 'Total Associations']].sort_values('Total Associations', ascending=False))
