# Importer les bibliothèques nécessaires
import random
import pandas as pd
from pyvis.network import Network
from collections import Counter
import streamlit as st

# Titre pour la première page
st.title("Graphe centré sur une table")

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gérer les valeurs NaN
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()

# Dictionnaire de couleurs pour chaque module d'application
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique() if module}

# Barre de recherche pour les tables
search_term_table = st.text_input("Rechercher une table")
all_tables = sorted([x for x in d365_tables['Table name'].unique() if x and (search_term_table.lower() in x.lower())])
central_table = st.selectbox('Table centrale:', all_tables)

# Trouver toutes les tables connectées à la table centrale
connected_tables = set(erp_relations.loc[erp_relations['Table Parent'] == central_table, 'Table Enfant'].tolist())
connected_tables.add(central_table)

# Création du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds avec leurs attributs
for table in connected_tables:
    table_info = d365_tables[d365_tables['Table name'] == table].iloc[0]
    title_str = "\n".join([f"{col}: {table_info[col]}" for col in table_info.index if pd.notna(table_info[col])])
    color = app_module_colors.get(table_info['App module'], random_color())
    net.add_node(table, title=title_str, color=color)

# Ajout des arêtes avec leurs attributs
for _, row in erp_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    if parent in connected_tables and child in connected_tables:
        net.add_edge(parent, child, title=relation)

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)
