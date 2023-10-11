# Importer les bibliothèques nécessaires
import random
import pandas as pd
from pyvis.network import Network
import streamlit as st

# Titre pour la première page
st.title("Graphe centré sur une table")

# Générer une couleur aléatoire
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

# Widgets pour sélectionner les modules d'application
connected_app_modules = d365_tables[d365_tables['Table name'].isin(connected_tables)]['App module'].unique().tolist()
selected_app_modules = st.multiselect('Sélectionnez les modules d’application à afficher:', connected_app_modules, default=connected_app_modules)

# Création du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Légende pour les modules d'application
st.write("### Légende")
legend = {module: app_module_colors[module] for module in selected_app_modules}
st.write(pd.DataFrame(list(legend.items()), columns=["Module d'application", "Couleur"]))

# Ajout des nœuds
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
        
        if app_module in app_module_counter:
            app_module_counter[app_module] += 1
        else:
            app_module_counter[app_module] = 1

# Tableau résumé
st.write("### Tableau résumé")
st.write(pd.DataFrame(list(app_module_counter.items()), columns=["Module d'application", "Nombre de relations"]))

# Ajout des arêtes
existing_nodes = set(net.get_nodes())
for _, row in erp_relations.iterrows():
    try:
        parent = row['Table Parent']
        child = row['Table Enfant']
        relation = row['Lien 1']
        if parent in existing_nodes and child in existing_nodes:
            net.add_edge(parent, child, title=relation)
    except Exception as e:
        st.write(f"Erreur lors de l'ajout de l'arête de {parent} à {child}: {e}")

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)
