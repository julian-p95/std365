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

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()
field_list['TABLE_NAME'] = field_list['TABLE_NAME'].astype(str).str.upper()

# Suppression des valeurs NaN dans 'App module' et tri
d365_tables['App module'].fillna('Inconnu', inplace=True)
app_modules = sorted(d365_tables['App module'].unique().tolist())

# Dictionnaire de couleurs
app_module_colors = {module: random_color() for module in app_modules}

# Comptage des occurrences
total_counter = Counter(erp_relations['Table Parent']) + Counter(erp_relations['Table Enfant'])

# Conversion en DataFrame
df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

# Jointure pour récupérer les modules d'application
df_total_counter = df_total_counter.merge(d365_tables[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

# Module de recherche et sélection du module d'application
search_term_module = st.text_input('Rechercher un module:')
app_module = st.selectbox('Module d\'Application:', [module for module in app_modules if search_term_module.lower() in module.lower()])

# Filtrage des tables pour le module sélectionné
filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]

# Slider pour le nombre de tables
num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)

# Tables avec le plus grand nombre de relations
top_tables = sorted(filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist())

# Filtrage des relations pour inclure seulement ces tables
filtered_relations = erp_relations[erp_relations['Table Parent'].isin(top_tables) & erp_relations['Table Enfant'].isin(top_tables)]

# Création du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds et des arêtes
graphed_tables = set()
for _, row in filtered_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation_str = row['Lien 1']
    
    if parent not in graphed_tables:
        color = app_module_colors.get(app_module, random_color())
        net.add_node(parent, title="", color=color)
        graphed_tables.add(parent)
    
    if child not in graphed_tables:
        color = app_module_colors.get(app_module, random_color())
        net.add_node(child, title="", color=color)
        graphed_tables.add(child)
    
    net.add_edge(parent, child, title=relation_str)

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)

# Module de recherche et tableau pour afficher les champs
search_term_table = st.text_input('Rechercher une table:')
table_choice = st.selectbox('Choisissez une table pour afficher ses champs:', [table for table in sorted(list(graphed_tables)) if search_term_table.lower() in table.lower()])
table_fields = field_list[field_list['TABLE_NAME'] == table_choice]
st.table(table_fields[['COLUMN_NAME', 'DATA_TYPE']])
