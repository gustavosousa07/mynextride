import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR, DATE, FLOAT, INTEGER

# --- ATENÇÃO: PREENCHA COM SUAS CREDENCIAIS DO ORACLE DB ---
DB_USER = "RM566473"
DB_PASSWORD = "fiap25"
DB_DSN = "oracle.fiap.com.br:1521/orcl"
TABLE_NAME = 'viagens'

try:
    df = pd.read_csv('viagens_clickbus.csv')
except FileNotFoundError:
    print("Erro: Execute o script '1_geracao_dados.py' primeiro para gerar o CSV.")
    exit()

connection_string = f"oracle+oracledb://{DB_USER}:{DB_PASSWORD}@{DB_DSN}"

try:
    engine = create_engine(connection_string)

    dtype_mapping = {
        'nk_ota_localizer_id': VARCHAR(40),
        'fk_contact': VARCHAR(40),
        'date_purchase': DATE,
        'time_purchase': VARCHAR(10),
        'place_origin_departure': VARCHAR(100),
        'place_destination_departure': VARCHAR(100),
        'place_origin_return': VARCHAR(100),
        'place_destination_return': VARCHAR(100),
        'fk_departure_ota_bus_company': VARCHAR(100),
        'fk_return_ota_bus_company': VARCHAR(100),
        'gmv_success': FLOAT,
        'total_tickets_quantity_success': INTEGER
    }
    
    df['date_purchase'] = pd.to_datetime(df['date_purchase'])

    print("Conectando ao Oracle DB e inserindo os dados...")
    df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False, dtype=dtype_mapping, chunksize=1000)

    print(f"Dados salvos com sucesso no Oracle DB na tabela '{TABLE_NAME}'.")

except Exception as e:
    print(f"Ocorreu um erro ao conectar ou inserir dados no Oracle: {e}")

finally:
    if 'engine' in locals():
        engine.dispose()