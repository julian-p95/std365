import random
import pandas as pd
from pyvis.network import Network
import streamlit as st

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

# Titre pour la page
st.title("Détails App module et Graphe centré Table")

# Partie 1 : Graphe centré Table
search_term_table = st.text_input("Rechercher une table")
all_tables = sorted([x for x in d365_tables['Table name'].unique() if x and (search_term_table.lower() in x.lower())])
central_table = st.selectbox('Table centrale:', all_tables)

# Trouver les tables et modules connectés
connected_tables = set(erp_relations.loc[erp_relations['Table Parent'] == central_table, 'Table Enfant'].tolist())
connected_tables |= set(erp_relations.loc[erp_relations['Table Enfant'] == central_table, 'Table Parent'].tolist())
connected_tables.add(central_table)
connected_app_modules = d365_tables[d365_tables['Table name'].isin(connected_tables)]['App module'].unique().tolist()
selected_app_modules = st.multiselect('Sélectionnez les modules d’application à afficher:', connected_app_modules, default=connected_app_modules)

# Création du graphe et tableau résumé
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
app_module_counter = {}
for table in connected_tables:
    filtered_df = d365_tables[d365_tables['Table name'] == table]
    if not filtered_df.empty:
        table_info = filtered_df.iloc[0]
        app_module = table_info['App module']
        if app_module not in selected_app_modules:
            continue
        title_str = "\n".join([f"{col}: {table_info[col]}" for col in table_info.index if pd.notna(table_info[col])])
        color = app_module_colors.get(app_module, random_color())
        net.add_node(table, title=title_str, color=color)
        app_module_counter[app_module] = app_module_counter.get(app_module, 0) + 1

# Ajout des arêtes
existing_nodes = set(net.get_nodes())
for _, row in erp_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    if parent in existing_nodes and child in existing_nodes:
        net.add_edge(parent, child, title=relation)

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)

# Afficher le tableau résumé
st.write("### Tableau résumé pour Graphe centré Table")
summary_df = pd.DataFrame(list(app_module_counter.items()), columns=["Module d'application", "Nombre de relations"])
summary_df = summary_df.sort_values(by="Nombre de relations", ascending=False)
st.write(summary_df)

# Partie 2 : Détails App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())
filtered_relations = erp_relations[(erp_relations['App Module Parent'] == selected_app_module)]

# Compte le nombre total de relations par App module Enfant
relation_summary = filtered_relations.groupby(['App Module Parent', 'App Module Enfant']).size().reset_index(name='Total Relations')
relation_summary = relation_summary.sort_values(by='Total Relations', ascending=False)
st.table(relation_summary)

# Filtre les tables par App module
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]
total_relations_count = filtered_relations['Table Parent'].value_counts().reset_index()
total_relations_count.columns = ['Table name', 'Total Relations']
filtered_tables = pd.merge(filtered_tables, total_relations_count, on='Table name', how='left')
filtered_tables = filtered_tables.sort_values(by='Total Relations', ascending=False).head(20)
st.table(filtered_tables[['Table name', 'Table label', 'Table group', 'Tabletype', 'Total Relations']])
