# pages/page2.py

import pandas as pd
import streamlit as st

# Titre pour la deuxième page
st.title("Informations sur les Tables")

# Lecture des fichiers Excel pour cette page
field_list = pd.read_excel("Table and Field List.xlsx", sheet_name='Field List')
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Conversion des noms de tables en majuscules
field_list['TABLE_NAME'] = field_list['TABLE_NAME'].astype(str).str.upper()
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()



# Tableau pour la sélection de la table et l'affichage des champs
table_choice = st.selectbox('Choisissez une table pour afficher ses champs:', field_list['TABLE_NAME'].unique())
table_fields = field_list[field_list['TABLE_NAME'] == table_choice]
st.table(table_fields[['COLUMN_NAME', 'DATA_TYPE']])

# Trouver toutes les relations de la table sélectionnée
all_relations = erp_relations[
    (erp_relations['Table Parent'] == table_choice) | 
    (erp_relations['Table Enfant'] == table_choice)
]

# Obtenir les modules d'application pour chaque table liée
all_relations_with_app_module = pd.merge(
    all_relations, d365_tables[['Table name', 'App module']], 
    left_on='Table Enfant', right_on='Table name', how='left'
)

# Compter le nombre de relations par App Module
relation_summary_by_app_module = all_relations_with_app_module.groupby('App module').size().reset_index(name='Total Relations')
relation_summary_by_app_module = relation_summary_by_app_module.sort_values(by='Total Relations', ascending=False)

# Afficher le tableau résumé
st.write("### Tableau résumé des relations par App Module")
st.table(relation_summary_by_app_module)
