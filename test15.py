import streamlit as st
import pandas as pd 
import networkx as nx
from pyvis.network import Network

# Chargement des fichiers Excel
uploaded_erp = st.file_uploader("Fichier ERP")  
uploaded_d365 = st.file_uploader("Fichier D365FO")

if uploaded_erp and uploaded_d365:

    # Lecture des données  
    erp = pd.read_excel(uploaded_erp)
    d365 = pd.read_excel(uploaded_d365)

    # Comptage des relations
    counts = erp['Table Parent'].value_counts() + erp['Table Enfant'].value_counts()
    counts = counts.reset_index()
    counts.columns = ['Table', 'Relations']

    # Jointure avec infos D365FO
    counts = counts.merge(d365[['Table name','Module']], left_on='Table', right_on='Table name')

    # Sélection du module 
    module = st.selectbox('Module', counts['Module'].unique())
    tables = counts[counts['Module']==module]

    # Limitation du nombre de tables
    num_tables = st.slider('Nombre de tables', 1, len(tables), 10) 
    top_tables = tables.nlargest(num_tables, 'Relations')['Table']

    # Filtrage des relations
    relations = erp[erp['Table Parent'].isin(top_tables) | 
                   erp['Table Enfant'].isin(top_tables)]

    # Création du graphe
    G = nx.Graph()
    for _,row in relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'])

    # Affichage avec PyVis
    net = Network()
    net.from_nx(G)
    net.show('graph.html')

    st.components.v1.html(open('graph.html').read())