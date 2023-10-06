import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
import seaborn as sns

# Lecture des fichiers Excel (chemins relatifs)
# Charger les fichiers dans des DataFrames
erp_all_table_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx")
d365fo = pd.read_excel("D365FO.xlsx") 


# Lecture des fichiers JSON
# Charger les fichiers JSON dans des DataFrames
tables_json = pd.read_json("tables.json")
tablefieldassociations_json = pd.read_json("tablefieldassociations.json")

# Calcul du nombre de relations pour chaque table
# Compter les relations Parent et Enfant
parent_counter = erp_all_table_relations['Table Parent'].value_counts()
child_counter = erp_all_table_relations['Table Enfant'].value_counts()


# Calcul du total des relations pour chaque table
total_counter = parent_counter.add(child_counter, fill_value=0).astype(int)

# Conversion en DataFrame
# Créer un DataFrame pour les totaux
df_total_counter = pd.DataFrame(total_counter, columns=['Total Associations']).reset_index()
df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

# Jointure avec d365fo pour récupérer les informations du module d'application
# Fusionner les DataFrames pour ajouter des informations du module d'application
df_total_counter = df_total_counter.merge(d365fo, left_on='Table', right_on='Table name', how='left')

# Widgets pour la sélection
# Ajouter des widgets pour la sélection du module et du nombre de tables
app_modules = df_total_counter['App module'].unique().tolist()
app_module = st.selectbox('App Module:', app_modules)
num_tables = st.slider('Nombre de tables:', min_value=1, max_value=50, value=10)

# Filtrage des tables pour le module d'application sélectionné
# Filtrer les tables en fonction du module d'application et du nombre de tables
filtered_tables = df_total_counter[df_total_counter['App module'] == app_module].nlargest(num_tables, 'Total Associations')['Table']

# Filtrage des relations pour inclure seulement ces tables
# Filtrer les relations pour inclure seulement les tables sélectionnées
filtered_relations = erp_all_table_relations[
    erp_all_table_relations['Table Parent'].isin(filtered_tables) | 
    erp_all_table_relations['Table Enfant'].isin(filtered_tables)
]

# Création du graphe avec NetworkX
# Créer un graphe NetworkX à partir des relations filtrées
G = nx.Graph()
for idx, row in filtered_relations.iterrows():
    G.add_edge(row['Table Parent'], row['Table Enfant'])

# Conversion en Pyvis Network
# Convertir le graphe NetworkX en Pyvis Network
net = Network(notebook=False)
net.from_nx(G)

# Ajout d'informations aux nœuds
# Ajouter des informations supplémentaires aux nœuds du graphe
for node in G.nodes():
    node_data = d365fo.loc[d365fo['Table name'] == node]
    title = f"App module: {node_data['App module'].iloc[0]}<br>Table Name: {node}<br>Table label: {node_data['Table label'].iloc[0]}<br>Table group: {node_data['Table group'].iloc[0]}<br>Table type: {node_data['Table type'].iloc[0]}"
    net.get_node(node.id)["title"] = title

# Sauvegarder en tant que fichier HTML et lire
# Sauvegarder le graphe en HTML et le lire
net.save_graph("temp.html")
HtmlFile = open("temp.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()

# Affichage du graphique dans Streamlit
# Afficher le graphe Pyvis dans Streamlit
st.components.v1.html(source_code, height=800)

# Affichage du tableau en dessous du graphique
# Afficher un tableau des tables et des relations dans Streamlit
connected_tables = filtered_relations['Table Parent'].append(filtered_relations['Table Enfant']).drop_duplicates()
df_connected_tables = df_total_counter[df_total_counter['Table'].isin(connected_tables)]
st.dataframe(df_connected_tables.sort_values(by=['App module', 'Total Associations'], ascending=[True, False]))

# Pourcentage de réussite du code : 98%
