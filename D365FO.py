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
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)

# Suppression des app modules non nécessaires pour le tableau
filtered_d365_tables = d365_tables[~d365_tables['App module'].isin(['Non spécifié', 'General', 'SystemAdministration'])]

# Calcul du nombre total de tables
total_tables = len(filtered_d365_tables)

# Calcul du nombre de tables par App module
app_module_counts = filtered_d365_tables['App module'].value_counts().reset_index()
app_module_counts.columns = ['App module', 'Nombre de tables']

# Calcul du ratio
app_module_counts['Ratio'] = app_module_counts['Nombre de tables'] / total_tables

# Affichage du tableau
st.table(app_module_counts)



# Graphique à barres horizontales pour Table Groups
fig, ax = plt.subplots(figsize=(10, 12))
table_group_counts = d365_tables['Table group'].value_counts()
table_group_counts.plot(kind='barh', ax=ax)
ax.set_title('Répartition des Table Groups')
ax.set_xlabel('Nombre de tables')
ax.set_ylabel('Table Group')
st.pyplot(fig)
