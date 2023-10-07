# Importation des bibliothèques
import pandas as pd
import random
from pyvis.network import Network
from collections import Counter
import streamlit as st

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')
field_list = pd.read_excel("Table and Field List.xlsx", sheet_name='Field List')

# Convertir les noms de table en majuscules pour assurer la correspondance
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()
field_list['TABLE_NAME'] = field_list['TABLE_NAME'].astype(str).str.upper()

# Générer un dictionnaire de couleurs pour chaque App module
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique()}

# Comptage des occurrences
total_counter = Counter(erp_relations['Table Parent']) + Counter(erp_relations['Table Enfant'])

# Conversion en DataFrame
df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

# Jointure pour récupérer les modules d'application
df_total_counter = df_total_counter.merge(d365_tables[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

# Slider pour limiter le nombre de tables chargées par module
max_tables_per_module = st.slider('Max de tables par module:', min_value=1, max_value=100, value=20)

# Filtrer les top tables par App Module
grouped = df_total_counter.groupby('App module')
filtered_top_tables = pd.concat([group.nlargest(max_tables_per_module, 'Total Associations') for _, group in grouped])

# Liste des modules d'application
app_modules = d365_tables['App module'].unique().tolist()

# Sélection du module d'application
app_module = st.selectbox('Module d\'Application:', app_modules)

# Filtrage des tables pour le module d'application sélectionné
filtered_tables = filtered_top_tables[filtered_top_tables['App module'] == app_module]

# Slider pour le nombre de tables
num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)

# Sélection des 'num_tables' tables avec le plus grand nombre de relations
top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

# Filtrage des relations pour inclure seulement ces tables
filtered_relations = erp_relations[
    (erp_relations['Table Parent'].isin(top_tables)) | 
    (erp_relations['Table Enfant'].isin(top_tables))
]

# Création du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds avec leurs attributs
graphed_tables = set()
for table in top_tables:
    color = app_module_colors.get(app_module, random_color())
    columns_info = field_list[field_list['TABLE_NAME'] == table]
    title_str = "Table: " + table + "\nApp Module: " + app_module + "\nChamps:\n" + "\n".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
    net.add_node(table, title=title_str, color=color)
    graphed_tables.add(table)

# ... (code précédent inchangé)

# Ajout des arêtes avec leurs attributs
for _, row in filtered_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    
    if parent in top_tables or child in top_tables:
        # Ajout des nœuds manquants
        for node in [parent, child]:
            if node not in graphed_tables:
                node_app_module = df_total_counter[df_total_counter['Table'] == node]['App module'].iloc[0]
                color = app_module_colors.get(node_app_module, random_color())
                columns_info = field_list[field_list['TABLE_NAME'] == node]
                title_str = "Table: " + node + "\nApp Module: " + str(node_app_module) + "\nChamps:\n" + "\n".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
                net.add_node(node, title=title_str, color=color)
                graphed_tables.add(node)

        # Ajout de l'arête
        net.add_edge(parent, child, title=relation)

# ... (code suivant inchangé)


# Tableau d'informations sur les tables graphées
graphed_table_info = d365_tables[d365_tables['Table name'].isin(graphed_tables)]
graphed_table_info = graphed_table_info[['Table name', 'Table label', 'App module', 'Table group', 'Table type']]

# Vérifier si les colonnes existent avant de fusionner
if 'TABLE_NAME' in field_list.columns and 'TABLE_TYPE' in field_list.columns:
    graphed_table_info = graphed_table_info.merge(field_list[['TABLE_NAME', 'TABLE_TYPE']], left_on='Table name', right_on='TABLE_NAME', how='left')
else:
    st.error('Les colonnes TABLE_NAME et/ou TABLE_TYPE sont manquantes dans le DataFrame field_list.')

graphed_table_info['Total Associations'] = graphed_table_info['Table name'].map(total_counter)
st.table(graphed_table_info)

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)
