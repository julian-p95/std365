import pandas as pd
import streamlit as st

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Titre pour la page
st.title("Détails App module")


# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())

# Filtre les relations par App module
filtered_relations = erp_relations[(erp_relations['App Module Parent'] == selected_app_module)]

# Compte le nombre total de relations par App module Enfant
relation_summary = filtered_relations.groupby(['App Module Parent', 'App Module Enfant']).size().reset_index(name='Total Relations')
relation_summary = relation_summary.sort_values(by='Total Relations', ascending=False)
st.table(relation_summary)

# Filtre les tables par App module
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]

# Jointure avec le nombre total de relations
total_relations_count = filtered_relations['Table Parent'].value_counts().reset_index()
total_relations_count.columns = ['Table name', 'Total Relations']
filtered_tables = pd.merge(filtered_tables, total_relations_count, on='Table name', how='left')

# Trie les tables par le nombre total de relations et affiche les 50 premières
filtered_tables = filtered_tables.sort_values(by='Total Relations', ascending=False).head(20)
st.table(filtered_tables[['Table name', 'Table label', 'Table group', 'Tabletype', 'Total Relations']])