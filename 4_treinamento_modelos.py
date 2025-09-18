# ==============================================================================
# SCRIPT DE ANÁLISE E TREINAMENTO DE MODELOS - MYNEXTRIDE
# ==============================================================================

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

print("--- Iniciando Script de Análise e Treinamento ---")

# --- Carregando os Dados ---
print("\n[FASE 1] Carregando e preparando os dados...")
df = pd.read_csv('viagens_clickbus.csv')
df['date_purchase'] = pd.to_datetime(df['date_purchase'])
df['rota'] = df['place_origin_departure'] + ' -> ' + df['place_destination_departure']
print("Dados carregados com sucesso.")

# --- Análise de Hubs (Slide 1 - Extra) ---
print("\n[ANÁLISE] Calculando Hubs de Viagem com Grafos...")
df_rotas = df[['place_origin_departure', 'place_destination_departure']].copy()
G = nx.from_pandas_edgelist(df_rotas, source='place_origin_departure', target='place_destination_departure', create_using=nx.DiGraph())
degree_centrality = nx.degree_centrality(G)
top_10_hubs = sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)[:10]
print("\nTop 10 Hubs de Viagem (Cidades com Maior Centralidade):")
for cidade, centralidade in top_10_hubs:
    print(f"- {cidade}: {centralidade:.4f}")

# --- Perfil do Cliente (Base para Slides 1, 2, 3) ---
print("\n[FASE 2] Criando perfil dos clientes...")
perfil_cliente = df.groupby('fk_contact').agg(
    total_gasto=('gmv_success', 'sum'),
    total_viagens=('nk_ota_localizer_id', 'count'),
    destinos_unicos=('place_destination_departure', 'nunique'),
    primeira_compra=('date_purchase', 'min'),
    ultima_compra=('date_purchase', 'max')
).reset_index()
print("Perfil dos clientes criado.")

# --- Clusterização (Slide 1) ---
print("\n[ANÁLISE] Segmentando clientes com K-Means (Slide 1)...")
features_cluster = perfil_cliente[['total_gasto', 'total_viagens', 'destinos_unicos']]
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features_cluster)
kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
perfil_cliente['cluster'] = kmeans.fit_predict(features_scaled)
cluster_analysis = perfil_cliente.groupby('cluster')[['total_gasto', 'total_viagens', 'destinos_unicos']].mean().reset_index()
print("\nAnálise dos Segmentos de Clientes:")
print(cluster_analysis)

# --- Modelo de Recompra (Slide 2) ---
print("\n[MODELO] Treinando modelo de previsão de recompra (Slide 2)...")
prob_recompra = perfil_cliente['total_gasto'] / perfil_cliente['total_gasto'].max()
perfil_cliente['recompra_em_30d'] = np.random.binomial(1, p=prob_recompra, size=len(perfil_cliente))
X_recompra = perfil_cliente[['total_gasto', 'total_viagens', 'destinos_unicos']]
y_recompra = perfil_cliente['recompra_em_30d']
print("\nDistribuição do alvo de recompra:")
print(y_recompra.value_counts())
X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_recompra, y_recompra, test_size=0.2, random_state=42)
model_recompra = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model_recompra.fit(X_train_r, y_train_r)
y_pred_r = model_recompra.predict(X_test_r)
accuracy_r = accuracy_score(y_test_r, y_pred_r)
print("\n--- AVALIAÇÃO DO MODELO (SLIDE 2 - O TIMING É TUDO) ---")
print(f"Acurácia: {accuracy_r:.2%}")
print(classification_report(y_test_r, y_pred_r, target_names=['Não Recomprou', 'Recomprou']))

# --- Modelo de Próxima Rota (Slide 3) ---
print("\n[MODELO] Treinando modelo de previsão de próxima rota (Slide 3)...")
df_sorted = df.sort_values(by=['fk_contact', 'date_purchase']).copy()
df_sorted['proxima_rota'] = df_sorted.groupby('fk_contact')['rota'].shift(-1)
df_sequencia = df_sorted.dropna(subset=['proxima_rota'])
df_sequencia['mes_compra'] = df_sequencia['date_purchase'].dt.month
le_rota = LabelEncoder()
le_proxima_rota = LabelEncoder()
X_rota = pd.DataFrame()
X_rota['rota_atual_encoded'] = le_rota.fit_transform(df_sequencia['rota'])
X_rota['mes_compra'] = df_sequencia['mes_compra']
y_rota = le_proxima_rota.fit_transform(df_sequencia['proxima_rota'])
X_train_pr, X_test_pr, y_train_pr, y_test_pr = train_test_split(X_rota, y_rota, test_size=0.25, random_state=42)
model_next_route = RandomForestClassifier(n_estimators=100, random_state=42)
model_next_route.fit(X_train_pr, y_train_pr)
y_pred_pr = model_next_route.predict(X_test_pr)
accuracy_pr = accuracy_score(y_test_pr, y_pred_pr)
print("\n--- AVALIAÇÃO DO MODELO (SLIDE 3 - A ESTRADA À FRENTE) ---")
print(f"Acurácia: {accuracy_pr:.2%}")

print("\n--- Script de Análise e Treinamento Concluído ---")