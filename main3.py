# main.py

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from collections import Counter

# Titre de la page d'accueil
st.title("Accueil")

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN pour le module d'application
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()

# Calcul du nombre total de tables
total_tables = len(d365_tables)

# Calcul du nombre de tables par "Table Group"
table_group_counts = d365_tables['TableGroup'].value_counts()
table_group_ratios = (table_group_counts / total_tables) * 100

# Visualisation de la répartition des "Table Group"
fig1, ax1 = plt.subplots()
table_group_ratios.plot(kind='bar', ax=ax1)
plt.title('Répartition des Table Group (Barres)')
plt.xlabel('Table Group')
plt.ylabel('% du total des tables')
st.pyplot(fig1)

# Camembert filtré par "App module"
selected_app_module = st.selectbox('Sélectionnez un App module pour le camembert:', d365_tables['App module'].unique())
filtered_d365 = d365_tables[d365_tables['App module'] == selected_app_module]
filtered_table_group_counts = filtered_d365['TableGroup'].value_counts()
filtered_table_group_ratios = (filtered_table_group_counts / len(filtered_d365)) * 100

fig2, ax2 = plt.subplots()
filtered_table_group_ratios.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
plt.title(f'Répartition des Table Group pour {selected_app_module} (Camembert)')
st.pyplot(fig2)

# Tableau récapitulatif des App modules
table_types = d365_tables.groupby(['App module', 'TableType']).size().unstack().fillna(0)
table_types['Total'] = table_types.sum(axis=1)
table_types_percentage = (table_types.div(table_types['Total'], axis=0) * 100).drop(columns=['Total'])
st.table(table_types_percentage.reset_index())

# Détails pour chaque module d'application
app_module_counts = d365_tables['App module'].value_counts().sort_values(ascending=False)
for app_module in app_module_counts.index:
    st.subheader(f"App Module: {app_module}")

    # Tables du module d'application
    filtered_tables = d365_tables[d365_tables['App module'] == app_module]
    filtered_tables['Total Associations'] = filtered_tables['Table name'].map(total_counter)

    # 10 tables avec le plus grand nombre de relations
    top_tables = filtered_tables.nlargest(10, 'Total Associations')
    st.table(top_tables[['Table name', 'Total Associations', 'TableGroup', 'TableType', 'TableLabel']])
