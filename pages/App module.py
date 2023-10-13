import pandas as pd
import streamlit as st

# Lecture des fichiers Excel
# Charger les données
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Titre pour la page
st.title("Détails App module")

# Sélection de l'App module
# Choix de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())

# Filtre les relations par App module
# Filtrer par App module sélectionné
filtered_relations = erp_relations[(erp_relations['App Module Parent'] == selected_app_module)]

# Compte le nombre total de relations par App module Enfant
# Résumé des relations
relation_summary = filtered_relations.groupby(['App Module Parent', 'App Module Enfant']).size().reset_index(name='Total Relations')
relation_summary = relation_summary.sort_values(by='Total Relations', ascending=False)
st.table(relation_summary)

# Filtre les tables par App module
# Filtrer les tables
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]

# Jointure avec le nombre total de relations
# Jointure pour compter les relations
total_relations_count = filtered_relations['Table Parent'].value_counts().reset_index()
total_relations_count.columns = ['Table name', 'Total Relations']
filtered_tables = pd.merge(filtered_tables, total_relations_count, on='Table name', how='left')

# Trie les tables par le nombre total de relations et affiche les 20 premières
# Trier et afficher
filtered_tables = filtered_tables.sort_values(by='Total Relations', ascending=False).head(20)
st.table(filtered_tables[['Table name', 'Table label', 'Table group', 'Tabletype', 'Total Relations']])

# Obtenir toutes les relations où l'App Module sélectionné est impliqué
# Récupérer toutes les relations
all_relations_with_selected_app_module = erp_relations[
    (erp_relations['App Module Parent'] == selected_app_module) | 
    (erp_relations['App Module Enfant'] == selected_app_module)
]

# Compter le nombre total de relations avec d'autres App Modules
# Comptage des relations
total_relations_with_other_app_modules = all_relations_with_selected_app_module.groupby(
    ['App Module Parent', 'App Module Enfant']
).size().reset_index(name='Total Relations')

# Créer un dictionnaire pour compter les relations pour chaque App Module
# Créer un compteur
app_module_relations_counter = {}

for _, row in total_relations_with_other_app_modules.iterrows():
    parent_module = row['App Module Parent']
    child_module = row['App Module Enfant']
    total_relations = row['Total Relations']
    
    if parent_module == selected_app_module:
        app_module_relations_counter[child_module] = app_module_relations_counter.get(child_module, 0) + total_relations
    else:
        app_module_relations_counter[parent_module] = app_module_relations_counter.get(parent_module, 0) + total_relations

# Créer le tableau résumé
# Création du tableau
summary_df = pd.DataFrame(list(app_module_relations_counter.items()), columns=["App Module", "Total Relations"])
summary_df = summary_df.sort_values(by="Total Relations", ascending=False)

# Afficher le tableau résumé
# Affichage du tableau
st.write("### Tableau résumé des relations avec d'autres App Modules")
st.table(summary_df)
