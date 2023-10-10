import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables['App module'].fillna("Non spécifié", inplace=True)

# Calcul du nombre total de tables
total_tables = len(d365_tables)

# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', ['ALL'] + d365_tables['App module'].unique().tolist())
if selected_app_module != 'ALL':
    d365_tables = d365_tables[d365_tables['App module'] == selected_app_module]

# Graphique à barres horizontales pour Table group
table_group_counts = d365_tables['Table group'].value_counts()
fig1, ax1 = plt.subplots()
table_group_counts.plot(kind='barh', ax=ax1)
plt.title('Répartition des groupes de tables')
plt.xlabel('Nombre de tables')
plt.ylabel('Groupes de tables')
st.pyplot(fig1)

# Graphique en camembert pour Table type
table_type_counts = d365_tables['Tabletype'].value_counts()
fig2, ax2 = plt.subplots()
table_type_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
plt.title('Répartition des types de tables')
st.pyplot(fig2)

# Tableau des App modules
app_module_summary = d365_tables.groupby(['App module', 'Tabletype']).size().unstack().fillna(0)
app_module_summary['Total'] = app_module_summary.sum(axis=1)
app_module_summary_percentage = (app_module_summary.div(app_module_summary['Total'], axis=0) * 100).drop(columns=['Total'])
app_module_summary_percentage = app_module_summary_percentage.reset_index()
app_module_summary_percentage['Total Tables'] = app_module_summary['Total']
st.table(app_module_summary_percentage)
