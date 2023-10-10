import pandas as pd
import streamlit as st

# Lecture des fichiers Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')

# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())

# Filtre les relations par App module
filtered_relations = erp_relations[erp_relations['App Module Parent'] == selected_app_module]
relation_counts = filtered_relations['Table Parent'].value_counts().reset_index()
relation_counts.columns = ['Table name', 'Total Relations']

# Tableau récapitulatif des relations par App module
relation_summary = filtered_relations.groupby(['App Module Parent', 'App Module Enfant']).size().reset_index(name='Total Relations')
relation_summary = relation_summary.sort_values(by='Total Relations', ascending=False)
st.table(relation_summary)

# Filtre les tables par App module et ajoute le nombre total de relations
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]
filtered_tables = pd.merge(filtered_tables, relation_counts, on='Table name', how='left')
filtered_tables['Total Relations'].fillna(0, inplace=True)
filtered_tables = filtered_tables.sort_values(by='Total Relations', ascending=False)

# Affiche les tables triées par le nombre total de relations
table_details = filtered_tables[['Table name', 'Table label', 'Table group', 'Tabletype', 'Total Relations']]
st.table(table_details)
