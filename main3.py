import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture du fichier Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Correction du nom de la colonne
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)

# Graphique avec App modules sélectionnés
filtered_tables = d365_tables[~d365_tables['App module'].isin(['SystemAdministration', 'General', 'Non spécifié'])]
app_module_counts = filtered_tables['App module'].value_counts()
fig1, ax1 = plt.subplots()
app_module_counts.plot(kind='bar', ax=ax1)
plt.title('Répartition des App modules (filtrés)')
plt.xlabel('App module')
plt.ylabel('Nombre de tables')
st.pyplot(fig1)

# Graphique avec tous les App modules
all_app_module_counts = d365_tables['App module'].value_counts()
fig2, ax2 = plt.subplots()
all_app_module_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
plt.title('Répartition de tous les App modules')
st.pyplot(fig2)
