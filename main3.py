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
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)  # Correction ici

# Graphique à barres horizontales pour App modules
app_module_counts = d365_tables['App module'].value_counts()
app_module_counts = app_module_counts.drop(['Non spécifié', 'SystemAdministration', 'General'])
fig1, ax1 = plt.subplots(figsize=(10, 12))  # Ajustement de la taille du graphique
app_module_counts.plot(kind='barh', ax=ax1, height=0.8)  # Ajustement de l'épaisseur des barres

ax1.set_title('Répartition des App modules')
ax1.set_xlabel('Nombre de tables')
ax1.set_ylabel('App modules')
plt.yticks(fontsize=8)
st.pyplot(fig1)

# Graphique à barres horizontales pour Table Group
table_group_counts = d365_tables['Table group'].value_counts()
fig2, ax2 = plt.subplots()
table_group_counts.plot(kind='barh', ax=ax2)
ax2.set_title('Répartition des Table Group')
ax2.set_xlabel('Nombre de tables')
ax2.set_ylabel('Table Group')
plt.yticks(fontsize=8)
st.pyplot(fig2)
