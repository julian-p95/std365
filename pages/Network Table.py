# Importer les bibliothèques nécessaires
import random
import pandas as pd
from pyvis.network import Network
import streamlit as st

# Titre pour la première page
st.title("Graphe centré Table")

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des fichiers Excel
erp_relations = pd.read_excel("/mnt/data/erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("/mnt/data/D365FO.xlsx", sheet_name='D365 Table')

# Gérer les NaN
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()

# Dictionnaire de couleurs
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique() if module}

# Liste de toutes les tables
all_tables = sorted(d365_tables['Table name'].unique())
central_table = st.selectbox('Table centrale:', all_tables)

# Trouver les tables connectées
connected_tables = set(erp_relations.loc[erp_relations['Table Parent'] == central_table, 'Table Enfant'].tolist())
connected_tables |= set(erp_relations.loc[erp_relations['Table Enfant'] == central_table, 'Table Parent'].tolist())
connected_tables.add(central_table)

# Trouver les modules d'application connectés
connected_app_modules = d365_tables[d365_tables['Table name'].isin(connected_tables)]['App module'].unique().tolist()

# Compter les tables pour chaque module
app_module_counter = {}
for table in connected_tables:
    filtered_df = d365_tables[d365_tables['Table name'] == table]
    if not filtered_df.empty:
        app_module = filtered_df['App module'].iloc[0]
        app_module_counter[app_module] = app_module_counter.get(app_module, 0) + 1

# Sélectionner les 3 premiers modules par défaut
top_3_modules = sorted(app_module_counter, key=app_module_counter.get, reverse=True)[:3]
selected_app_modules = st.multiselect('Sélectionnez les modules d’application à afficher:', connected_app_modules, default=top_3_modules)

# Créer la légende pour les modules d'application
legend_data = {module: app_module_colors[module] for module in selected_app_modules}
st.write("### Légende")
legend_html = "<div style='display: flex; flex-direction: row; flex-wrap: wrap;'>"
for module, color in legend_data.items():
    legend_html += f"<div style='margin: 5px;'><span style='background-color: {color}; width: 20px; height: 20px; display: inline-block; margin-right: 5px;'></span>{module}</div>"
legend_html += "</div>"
st.markdown(legend_html, unsafe_allow_html=True)

# Création du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds
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

# Afficher plusieurs tableaux résumés, un par module d'application
st.write("### Tableaux résumés")
for module in selected_app_modules:
    module_tables = [table for table in connected_tables if d365_tables[d365_tables['Table name'] == table]['App module'].iloc[0] == module]
    if module_tables:
        st.write(f"#### {module}")
        module_df = pd.DataFrame({
            "Table connectée": module_tables,
            "Relation": [erp_relations[(erp_relations['Table Parent'] == central_table) & (erp_relations['Table Enfant'] == table)]['Lien 1'].iloc[0] for table in module_tables]
        })
        st.write(module_df)
