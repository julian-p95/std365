# Code complet avec corrections et fonctionnalités supplémentaires

# Importation des bibliothèques nécessaires
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

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()
field_list['TABLE_NAME'] = field_list['TABLE_NAME'].astype(str).str.upper()

# Couleurs par module d'application
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique()}

# Comptage des occurrences
total_counter = Counter(erp_relations['Table Parent']) + Counter(erp_relations['Table Enfant'])

# Création du DataFrame pour les occurrences
df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

# Jointure pour les modules d'application
df_total_counter = df_total_counter.merge(d365_tables[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

# Modules d'application disponibles
app_modules = d365_tables['App module'].unique().tolist()

# Sélection du module d'application
app_module = st.selectbox('Module d\'Application:', app_modules)

# Filtrage des tables
filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

# Sélection du nombre de tables
num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)

# Tables les plus liées
top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

# Filtrage des relations pour inclure seulement ces tables
filtered_relations = erp_relations[
    (erp_relations['Table Parent'].isin(top_tables)) | 
    (erp_relations['Table Enfant'].isin(top_tables))
]

# Initialisation du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds
graphed_tables = set()
for table in top_tables:
    color = app_module_colors.get(app_module, random_color())
    columns_info = field_list[field_list['TABLE_NAME'] == table]
    title_str = "Table: " + str(table) + "\nApp Module: " + str(app_module) + "\nChamps:\n" + "\n".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
    net.add_node(table, title=title_str, color=color)
    graphed_tables.add(table)

# Ajout des tables liées d'autres modules d'application
linked_tables = filtered_relations['Table Parent'].unique().tolist() + filtered_relations['Table Enfant'].unique().tolist()
linked_tables = set(linked_tables) - graphed_tables

for table in linked_tables:
    app_module_linked_series = d365_tables.loc[d365_tables['Table name'] == table, 'App module']
    
    if not app_module_linked_series.empty:
        app_module_linked = app_module_linked_series.iloc[0]
    else:
        app_module_linked = 'Inconnu'  # ou toute autre valeur par défaut
    
    color = app_module_colors.get(app_module_linked, random_color())
    columns_info = field_list[field_list['TABLE_NAME'] == table]
    title_str = "Table: " + str(table) + "\nApp Module: " + str(app_module_linked) + "\nChamps:\n" + "\n".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
    net.add_node(table, title=title_str, color=color)
    graphed_tables.add(table)

# Ajout des arêtes
for _, row in filtered_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    if parent in graphed_tables and child in graphed_tables:
        net.add_edge(parent, child, title=relation)

# Affichage du graphe en HTML
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)

# Informations sur les tables
graphed_table_info = d365_tables[d365_tables['Table name'].isin(graphed_tables)]
if 'TABLE_NAME' in field_list.columns and 'TABLE_TYPE' in field_list.columns:
    graphed_table_info = graphed_table_info.merge(field_list[['TABLE_NAME', 'TABLE_TYPE']], left_on='Table name', right_on='TABLE_NAME', how='left')
graphed_table_info['Total Associations'] = graphed_table_info['Table name'].map(total_counter)

# Affichage du tableau
st.table(graphed_table_info)
