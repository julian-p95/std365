# main.py

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page d'accueil
st.title("Accueil")

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN pour le module d'application
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules pour le DataFrame de relations
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()

# Calcul du nombre total de tables
total_tables = len(d365_tables)

# Calcul du nombre de tables par "Table group"
table_group_counts = d365_tables['Table group'].value_counts()
table_group_ratios = (table_group_counts / total_tables) * 100

# Visualisation de la répartition des "Table group"
fig1, ax1 = plt.subplots()
table_group_ratios.plot(kind='bar', ax=ax1)
plt.title('Répartition des Table group (Barres)')
plt.xlabel('Table group')
plt.ylabel('% du total des tables')
st.pyplot(fig1)

# Camembert filtré par "App module"
selected_app_module = st.selectbox('Sélectionnez un App module pour le camembert:', d365_tables['App module'].unique())
filtered_d365 = d365_tables[d365_tables['App module'] == selected_app_module]
filtered_table_group_counts = filtered_d365['Table group'].value_counts()
filtered_table_group_ratios = (filtered_table_group_counts / len(filtered_d365)) * 100

fig2, ax2 = plt.subplots()
filtered_table_group_ratios.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
plt.title(f'Répartition des Table group pour {selected_app_module} (Camembert)')
st.pyplot(fig2)

# Tableau récapitulatif des App modules
table_types = d365_tables.groupby(['App module', 'Tabletype']).size().unstack().fillna(0)
table_types['Total'] = table_types.sum(axis=1)
table_types_percentage = (table_types.div(table_types['Total'], axis=0) * 100).drop(columns=['Total'])
st.table(table_types_percentage.reset_index())
