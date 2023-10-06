import pandas as pd
import random
# from pyvis.network import Network  # Décommentez cette ligne dans votre environnement

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Chargement des fichiers Excel
try:
    erp_all_table_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
    d365fo = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')
    field_list = pd.read_excel("Table and Field List.xlsx", sheet_name='Field List')
    # Vérification des colonnes
    assert all(col in erp_all_table_relations.columns for col in ['Table Parent', 'Table Enfant', 'Lien 1'])
    assert all(col in d365fo.columns for col in ['Table name', 'App module'])
    assert all(col in field_list.columns for col in ['TABLE_NAME', 'COLUMN_NAME', 'DATA_TYPE'])
except Exception as e:
    print(f"Erreur lors du chargement des fichiers ou des colonnes manquantes: {e}")
    exit()

# Comptage des relations entre tables
table_counts = (erp_all_table_relations['Table Parent'].append(erp_all_table_relations['Table Enfant'])).value_counts().reset_index()
table_counts.columns = ['Table', 'Count']

# Jointure avec les informations de D365FO
table_counts = table_counts.merge(d365fo[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

# Sélection du module d'application (à remplacer par un choix utilisateur dans Streamlit)
app_module = 'ModuleName'  # À remplacer

# Filtrage des tables par module d'application
filtered_tables = table_counts[table_counts['App module'] == app_module]

# Tables à afficher (limite fixée à 10 pour cet exemple)
top_tables = filtered_tables.nlargest(10, 'Count')['Table'].tolist()

# Filtrage des relations
filtered_relations = erp_all_table_relations[
    erp_all_table_relations['Table Parent'].isin(top_tables) |
    erp_all_table_relations['Table Enfant'].isin(top_tables)
]

# Création du graphe avec PyVis
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds et des arêtes
for _, row in filtered_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    
    # Ajout des nœuds s'ils n'existent pas encore
    if parent not in net.nodes:
        parent_info = field_list[field_list['TABLE_NAME'] == parent]
        parent_title = "<br>".join(parent_info['COLUMN_NAME'].astype(str) + ' (' + parent_info['DATA_TYPE'].astype(str) + ')')
        net.add_node(parent, title=parent_title, color=random_color())
    if child not in net.nodes:
        child_info = field_list[field_list['TABLE_NAME'] == child]
        child_title = "<br>".join(child_info['COLUMN_NAME'].astype(str) + ' (' + child_info['DATA_TYPE'].astype(str) + ')')
        net.add_node(child, title=child_title, color=random_color())
        
    # Ajout de l'arête
    net.add_edge(parent, child, title=relation)

# Affichage du graphe (à remplacer par le code Streamlit approprié)
# net.show("temp.html")
