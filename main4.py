import pandas as pd
import streamlit as st

# Lecture des fichiers Excel
erp_relations = pd.read_excel("/path/to/erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("/path/to/D365FO.xlsx", sheet_name='D365 Table')

# Compte le nombre total de relations par table
table_relation_counts = erp_relations['Table Parent'].value_counts().reset_index()
table_relation_counts.columns = ['Table name', 'Total Relations']

# Fusion des données pour ajouter le nombre total de relations
d365_tables = pd.merge(d365_tables, table_relation_counts, on='Table name', how='left')
d365_tables['Total Relations'].fillna(0, inplace=True)

# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())

# Filtre les tables par App module
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]
filtered_tables = filtered_tables.sort_values(by='Total Relations', ascending=False)

# Sélection de la table
table_choice = st.selectbox('Choisissez une table pour afficher ses détails:', filtered_tables['Table name'].tolist())
table_details = filtered_tables[filtered_tables['Table name'] == table_choice]
st.table(table_details[['Table name', 'Table label', 'Table group', 'Tabletype', 'Total Relations']])
