import pandas as pd
import streamlit as st

# Lecture des fichiers Excel
erp_relations = pd.read_excel("/path/to/erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("/path/to/D365FO.xlsx", sheet_name='D365 Table')

# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())

# Tableau des relations par App module
filtered_relations = erp_relations[erp_relations['App Module Parent'] == selected_app_module]
relation_summary = filtered_relations.groupby('App Module Enfant').size().reset_index(name='Total Relations').sort_values(by='Total Relations', ascending=False)
st.table(relation_summary)

# Tableau des tables par App module
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]
top_tables = filtered_tables.nlargest(20, 'Total Relations')
st.table(top_tables[['Table name', 'Table label', 'Table group', 'Table type', 'Total Relations']])
