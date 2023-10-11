import pandas as pd
import random
from pyvis.network import Network
from collections import Counter
import streamlit as st

# Titre de la page
st.title("Graphe centré sur une table")

# Générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des données Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].str.upper()
d365_tables['Table name'] = d365_tables['Table name'].str.upper()

# Créer un dictionnaire de couleurs
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique()}

# Recherche de table
search_term_table = st.text_input("Rechercher une table")
all_tables = sorted([x for x in d365_tables['Table name'].unique() if x and search_term_table.lower() in x.lower()])
central_table = st.selectbox('Table centrale:', all_tables)

# Trouver les tables connectées
connected_tables = set(erp_relations[erp_relations['Table Parent'] == central_table]['Table Enfant'].tolist())
connected_tables.add(central_table)

# Initialiser le graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajouter des nœuds
for table in connected_tables:
    table_info = d365_tables[d365_tables['Table name'] == table]
    if not table_info.empty:
        table_info = table_info.iloc[0]
        title_str = "\n".join([f"{col}: {table_info[col]}" for col in table_info.index if pd.notna(table_info[col])])
        color = app_module_colors.get(table_info['App module'], random_color())
        net.add_node(table, title=title_str, color=color)

# ... (le code précédent reste inchangé)

# Ajouter des arêtes
existing_nodes = set(net.get_nodes())
for _, row in erp_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    
    if parent in existing_nodes and child in existing_nodes:
        net.add_edge(parent, child, title=relation)
    else:
        st.write(f"Erreur: Parent {parent} ou enfant {child} non trouvé dans le graphe.")

# ... (le reste du code reste inchangé)

# Afficher le graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)
