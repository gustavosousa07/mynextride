from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from sqlalchemy import create_engine
import oracledb
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- Configuração do Backend ---
app = Flask(__name__)
CORS(app)

# --- Conexão com o Oracle DB ---
DB_USER = "RM566473"
DB_PASSWORD = "fiap25"
DB_DSN = "oracle.fiap.com.br:1521/orcl"
TABLE_NAME = 'viagens'

try:
    engine = create_engine(
        "oracle+oracledb://",
        creator=lambda: oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    )
    connection_test = engine.connect()
    connection_test.close()
    print("Conexão com o Oracle DB estabelecida com sucesso pela API.")
except Exception as e:
    print(f"ERRO CRÍTICO ao criar a conexão da API com o Oracle: {e}")
    exit()

def get_data_from_db():
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", engine)
    df['date_purchase'] = pd.to_datetime(df['date_purchase'])
    return df

# --- Endpoints da API ---

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    df = get_data_from_db()
    total_receita = df['gmv_success'].sum()
    total_passagens = df['total_tickets_quantity_success'].sum()
    total_clientes = df['fk_contact'].nunique()
    
    kpis = {
        "receita_total": total_receita,
        "passagens_total": int(total_passagens),
        "clientes_unicos": int(total_clientes)
    }
    return jsonify(kpis)

@app.route('/api/top-routes', methods=['GET'])
def get_top_routes():
    df = get_data_from_db()
    df['rota'] = df['place_origin_departure'] + ' -> ' + df['place_destination_departure']
    top_rotas = df['rota'].value_counts().head(10).reset_index()
    top_rotas.columns = ['rota', 'quantidade']
    return top_rotas.to_json(orient='records')

@app.route('/api/seasonality', methods=['GET'])
def get_seasonality():
    df = get_data_from_db()
    df['mes_ano'] = df['date_purchase'].dt.to_period('M').astype(str)
    vendas_mes = df.groupby('mes_ano')['gmv_success'].sum().reset_index()
    vendas_mes.columns = ['mes', 'receita']
    return vendas_mes.to_json(orient='records')

@app.route('/api/hubs', methods=['GET'])
def get_hubs():
    df = get_data_from_db()
    df_rotas = df[['place_origin_departure', 'place_destination_departure']].copy()
    G = nx.from_pandas_edgelist(df_rotas, source='place_origin_departure', target='place_destination_departure', create_using=nx.DiGraph())
    degree_centrality = nx.degree_centrality(G)
    top_10_hubs = sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)[:10]
    hubs_json = [{"cidade": cidade, "centralidade": centralidade} for cidade, centralidade in top_10_hubs]
    return jsonify(hubs_json)

@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    df = get_data_from_db()
    perfil_cliente = df.groupby('fk_contact').agg(
        total_gasto=('gmv_success', 'sum'),
        total_viagens=('nk_ota_localizer_id', 'count'),
        destinos_unicos=('place_destination_departure', 'nunique')
    ).reset_index()

    features = perfil_cliente[['total_gasto', 'total_viagens', 'destinos_unicos']]
    if len(features) < 4:
        return jsonify({"error": "Dados insuficientes para clusterização"}), 500

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    perfil_cliente['cluster'] = kmeans.fit_predict(features_scaled)
    
    cluster_analysis = perfil_cliente.groupby('cluster')[['total_gasto', 'total_viagens', 'destinos_unicos']].mean().reset_index()

    # --- NOVO BLOCO: Atribuir Nomes aos Segmentos (Personas) ---
    # Primeiro, ordenamos os clusters pelo gasto total, do maior para o menor.
    # Isso garante que o Cluster "VIP" seja sempre o de maior gasto, independentemente do ID (0,1,2,3) que o KMeans atribuiu.
    cluster_analysis_sorted = cluster_analysis.sort_values(by='total_gasto', ascending=False)
    
    # Definimos os nomes (personas) na ordem do ranking
    nomes_segmentos = ['Cliente VIP', 'Cliente Fiel', 'Cliente Ocasional', 'Cliente Novo/Econômico']
    
    # Adicionamos a nova coluna com os nomes
    cluster_analysis_sorted['nome_segmento'] = nomes_segmentos
    # ----------------------------------------------------------------

    return cluster_analysis_sorted.to_json(orient='records')

@app.route('/api/segment_distribution', methods=['GET'])
def get_segment_distribution():
    # Reutiliza a lógica de clusterização
    df = get_data_from_db()
    perfil_cliente = df.groupby('fk_contact').agg(
        total_gasto=('gmv_success', 'sum'),
        total_viagens=('nk_ota_localizer_id', 'count'),
        destinos_unicos=('place_destination_departure', 'nunique')
    ).reset_index()

    features = perfil_cliente[['total_gasto', 'total_viagens', 'destinos_unicos']]
    if len(features) < 4:
        return jsonify({"error": "Dados insuficientes"}), 500

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    perfil_cliente['cluster'] = kmeans.fit_predict(features_scaled)
    
    # Lógica de nomear os segmentos
    cluster_analysis = perfil_cliente.groupby('cluster')[['total_gasto']].mean().reset_index()
    cluster_analysis_sorted = cluster_analysis.sort_values(by='total_gasto', ascending=False)
    nomes_segmentos = ['Cliente VIP', 'Cliente Fiel', 'Cliente Ocasional', 'Cliente Novo/Econômico']
    cluster_analysis_sorted['nome_segmento'] = nomes_segmentos
    
    # Junta os nomes de volta ao perfil do cliente
    perfil_cliente_com_nomes = pd.merge(perfil_cliente, cluster_analysis_sorted[['cluster', 'nome_segmento']], on='cluster')

    # Calcula a contagem de clientes por segmento nomeado
    distribution = perfil_cliente_com_nomes['nome_segmento'].value_counts().reset_index()
    distribution.columns = ['segmento', 'contagem']
    
    return distribution.to_json(orient='records')

@app.route('/api/new_customers_over_time', methods=['GET'])
def get_new_customers():
    df = get_data_from_db()
    perfil_cliente = df.groupby('fk_contact').agg(
        primeira_compra=('date_purchase', 'min')
    ).reset_index()
    
    perfil_cliente['mes_aquisicao'] = perfil_cliente['primeira_compra'].dt.to_period('M').astype(str)
    
    novos_clientes_por_mes = perfil_cliente.groupby('mes_aquisicao').size().reset_index(name='quantidade')
    novos_clientes_por_mes = novos_clientes_por_mes.sort_values(by='mes_aquisicao')
    
    return novos_clientes_por_mes.to_json(orient='records')

@app.route('/api/hub_details', methods=['GET'])
def get_hub_details():
    df = get_data_from_db()
    df_rotas = df[['place_origin_departure', 'place_destination_departure']].copy()
    G = nx.from_pandas_edgelist(
        df_rotas,
        source='place_origin_departure',
        target='place_destination_departure',
        create_using=nx.DiGraph()
    )

    # Pega os 10 maiores hubs com base na centralidade de grau (chegadas + partidas)
    degree_centrality = nx.degree_centrality(G)
    top_10_hubs_nodes = [
        item[0] for item in sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)[:10]
    ]

    # Calcula os graus de entrada (in-degree) e saída (out-degree) APENAS para os top 10 hubs
    in_degrees = G.in_degree(top_10_hubs_nodes)
    out_degrees = G.out_degree(top_10_hubs_nodes)

    # Monta o JSON para o frontend
    hub_details = []
    for hub_name in top_10_hubs_nodes:
        hub_details.append({
            "cidade": hub_name,
            "chegadas": in_degrees[hub_name],
            "partidas": out_degrees[hub_name]
        })

    return jsonify(hub_details)

if __name__ == '__main__':
    app.run(debug=True, port=5001)