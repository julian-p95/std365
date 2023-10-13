# Importer les bibliothèques nécessaires
import random
import pandas as pd

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

# Liste de toutes les tables
all_tables = sorted(d365_tables['Table name'].unique())
central_table = "YOUR_CENTRAL_TABLE"  # À remplacer par la sélection de l'utilisateur

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
selected_app_modules = top_3_modules  # À remplacer par la sélection de l'utilisateur

# Le reste du code reste le même
# ...
# Note : L'exécution du code complet nécessite des bibliothèques non disponibles dans cet environnement.
# Veuillez copier ce code et l'exécuter dans votre propre environnement pour voir les résultats.
