# Importer les bibliothèques nécessaires
import random
import pandas as pd
from pyvis.network import Network
import streamlit as st

# Titre pour la première page
st.title("Graphe centré sur une table")

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gérer les NaN
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()

# Dictionnaire de couleurs
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique() if module}

# Barre de recherche pour les tables
search_term_table = st.text_input("Rechercher une table")
all_tables = sorted([x for x in d365_tables['Table name'].unique() if x and (search_term_table.lower() in x.lower())])
central_table = st.selectbox('Table centrale:', all_tables)

# Trouver les tables connectées
connected_tables = set(erp_relations.loc[erp_relations['Table Parent'] == central_table, 'Table Enfant'].tolist())
connected_tables |= set(erp_relations.loc[erp_relations['Table Enfant'] == central_table, 'Table Parent'].tolist())
connected_tables.add(central_table)

# Trouver les modules d'application connectés et créer un widget multiselect
connected_app_modules = d365_tables[d365_tables['Table name'].isin(connected_tables)]['App module'].unique().tolist()
selected_app_modules = st.multiselect('Sélectionnez les modules d’application à afficher:', connected_app_modules, default=connected_app_modules)

# Créer la légende pour les modules d'application
legend_data = {module: app_module_colors[module] for module in selected_app_modules}
st.write("### Légende")
legend_html = "<div style='display: flex; flex-direction: row;'>"
for module, color in legend_data.items():
    legend_html += f"<div style='margin: 5px;'><span style='background-color: {color}; width: 20px; height: 20px; display: inline-block; margin-right: 5px;'></span>{module}</div>"
legend_html += "</div>"
st.markdown(legend_html, unsafe_allow_html=True)

# Le reste du code pour la création du graphe et l'affichage du tableau résumé reste le même
