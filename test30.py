# Importation des bibliothèques
import pandas as pd
import random
from collections import Counter
# import de pyvis et streamlit à faire dans votre environnement

# Génération d'une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des fichiers Excel
erp_relations = pd.read_excel("/mnt/data/erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("/mnt/data/D365FO.xlsx", sheet_name='D365 Table')

# Conversion en majuscules pour assurer la correspondance
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()

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
graphed_tables = set()
for table in top_tables:
    color = app_module_colors.get(app_module, random_color())
    net.add_node(table, color=color)
    graphed_tables.add(table)

# Ajout des arêtes
for _, row in filtered_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    
    if include_other_modules:
        # Ajoute des nœuds s'ils n'existent pas déjà
        if parent not in graphed_tables:
            net.add_node(parent, color=random_color())
            graphed_tables.add(parent)
        if child not in graphed_tables:
            net.add_node(child, color=random_color())
            graphed_tables.add(child)

    # Vérifie que les nœuds existent avant d'ajouter une arête
    if parent in graphed_tables and child in graphed_tables:
        net.add_edge(parent, child, title=relation)

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)
