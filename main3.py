import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture des fichiers Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables['App module'].fillna("Non spécifié", inplace=True)
d365_tables['Table group'].fillna("Non spécifié", inplace=True)
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)

# Suppression des app modules non nécessaires
d365_tables = d365_tables[~d365_tables['App module'].isin(['Non spécifié', 'General', 'SystemAdministration'])]

# Graphique à barres horizontales pour App modules
fig1, ax1 = plt.subplots(figsize=(10, 12))
app_module_counts = d365_tables['App module'].value_counts()
app_module_counts.plot(kind='barh', ax=ax1, height=0.8)
plt.title('Répartition des App modules')
plt.xlabel('Nombre de tables')
plt.ylabel('App module')
ax1.invert_yaxis()  # Inversion de l'axe y pour un affichage plus agréable
st.pyplot(fig1)

# Comptage des préfixes des tables
d365_tables['Prefix'] = d365_tables['Table label'].str.split(' ').str[0].str.upper()
prefix_counts = d365_tables['Prefix'].value_counts().reset_index()
prefix_counts.columns = ['Prefix', 'Occurrence']
st.table(prefix_counts)

# Graphique à barres horizontales pour Table Groups
fig2, ax2 = plt.subplots(figsize=(10, 12))
table_group_counts = d365_tables['Table group'].value_counts()
table_group_counts.plot(kind='barh', ax=ax2, height=0.8)
plt.title('Répartition des Table Groups')
plt.xlabel('Nombre de tables')
plt.ylabel('Table Group')
ax2.invert_yaxis()  # Inversion de l'axe y pour un affichage plus agréable
st.pyplot(fig2)
