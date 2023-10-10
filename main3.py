import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture des fichiers Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')

# Gestion des valeurs NaN
d365_tables.fillna("Non spécifié", inplace=True)

# Filtre pour éliminer le module "General"
filtered_d365 = d365_tables[d365_tables['App module'] != 'General']

# Graphique à barres horizontales pour App module
fig, ax = plt.subplots()
filtered_d365['App module'].value_counts().plot(kind='barh', ax=ax)
plt.title('Répartition des App modules')
plt.xlabel('Nombre de tables')
plt.ylabel('App module')
st.pyplot(fig)

# Camembert pour App module
app_module_counts = d365_tables['App module'].value_counts().reset_index()
app_module_counts.columns = ['App module', 'Count']
app_module_counts['Category'] = app_module_counts['App module'].apply(lambda x: x if x in ['General', 'Non spécifié', 'SystemAdministration'] else 'Other')
category_counts = app_module_counts.groupby('Category')['Count'].sum()

fig, ax = plt.subplots()
category_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
plt.title('Répartition des App modules')
st.pyplot(fig)
