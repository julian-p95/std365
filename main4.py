# table_details.py

import pandas as pd
import streamlit as st

# Titre de la page
st.title("Détails des Tables d'un App module")

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())

# Filtrer les relations pour l'App module sélectionné (en tant que parent uniquement)
filtered_relations = erp_relations[erp_relations['App Module Parent'] == selected_app_module]

# Tableau résumant les relations entre App modules, trié par 'Total Relations'
relation_summary = filtered_relations.groupby(['App Module Parent', 'App Module Enfant']).size().reset_index(name='Total Relations')
relation_summary = relation_summary.sort_values(by='Total Relations', ascending=False)
st.table(relation_summary)

# Filtrer et trier les tables pour l'App module sélectionné
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]
filtered_tables = filtered_tables[['Table name', 'Table label', 'Table group', 'Tabletype']]
total_relations_per_table = filtered_relations['Table Parent'].value_counts()
filtered_tables['Total Relations'] = filtered_tables['Table name'].map(total_relations_per_table).fillna(0)
filtered_tables = filtered_tables.sort_values(by='Total Relations', ascending=False)

# Affichage d'un sélecteur pour choisir une table du App module
selected_table = st.selectbox('Sélectionnez une table:', filtered_tables['Table name'].unique().tolist())

# Affichage du tableau des tables
st.table(filtered_tables)
