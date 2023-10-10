import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture du fichier Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables['App module'].fillna("Non spécifié", inplace=True)
d365_tables['Table group'].fillna("Non spécifié", inplace=True)
d365_tables['Table\xa0type'].fillna("Non spécifié", inplace=True)

# Filtrage des App modules
filtered_tables = d365_tables[~d365_tables['App module'].isin(['SystemAdministration', 'General', 'Non spécifié'])]

# Répartition par App module
app_module_counts = filtered_tables['App module'].value_counts()

# Graphique horizontal des App modules
fig1, ax1 = plt.subplots()
app_module_counts.plot(kind='barh', ax=ax1, linewidth=2)
plt.title('Répartition des App modules')
plt.xlabel('Nombre de tables')
plt.ylabel('App module')
ax1.bar_label(ax1.containers[0])
st.pyplot(fig1)

# Répartition par Table group
table_group_counts = d365_tables['Table group'].value_counts()

# Graphique horizontal des Table groups
fig2, ax2 = plt.subplots()
table_group_counts.plot(kind='barh', ax=ax2, linewidth=2)
plt.title('Répartition des groupes de tables')
plt.xlabel('Nombre de tables')
plt.ylabel('Table group')
ax2.bar_label(ax2.containers[0])
st.pyplot(fig2)
