# Importation des bibliothèques
import pandas as pd
import random
from pyvis.network import Network
from collections import Counter
import streamlit as st

# Génération d'une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')
field_list = pd.read_excel("Table and Field List.xlsx", sheet_name='Field List')

# Conversion en majuscules pour assurer la correspondance
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()
field_list['TABLE_NAME'] = field_list['TABLE_NAME'].astype(str).str.upper()

# Dictionnaire de couleurs pour chaque module d'application
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique()}

# Comptage des occurrences
total_counter = Counter(erp_relations['Table Parent']) + Counter(erp_relations['Table Enfant'])

# Conversion en DataFrame
df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

# Jointure pour récupérer les modules d'application
df_total_counter = df_total_counter.merge(d365_tables[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

# Sélection du module d'application
app_modules = d365_tables['App module'].unique().tolist()
app_module = st.selectbox('Module d\'Application:', app_modules)

# Filtrage des tables pour le module sélectionné
filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

# Slider pour le nombre de tables
num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)

# Tables avec le plus grand nombre de relations
top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

# Option pour inclure les tables d'autres modules
include_other_modules = st.checkbox('Inclure les tables d\'autres modules connectées')

# Filtrage des relations
if include_other_modules:
    filtered_relations = erp_relations[
        (erp_relations['Table Parent'].isin(top_tables)) | 
        (erp_relations['Table Enfant'].isin(top_tables))
    ]
else:
    filtered_relations = erp_relations[
        (erp_relations['Table Parent'].isin(top_tables)) & 
        (erp_relations['Table Enfant'].isin(top_tables))
    ]

# Création du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds
for table in top_tables:
    color = app_module_colors.get(app_module, random_color())
    columns_info = field_list[field_list['TABLE_NAME'] == table]
    title_str = "Table: " + table + "\nApp Module: " + app_module + "\nChamps:\n" + "\n".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
    net.add_node(table, title=title_str, color=color)

# Ajout des arêtes
for _, row in filtered_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    net.add_edge(parent, child, title=relation)

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)
