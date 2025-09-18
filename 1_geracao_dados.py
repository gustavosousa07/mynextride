import pandas as pd
from faker import Faker
import random
from datetime import datetime

fake = Faker('pt_BR')

NUMERO_DE_REGISTROS = 10000
NUMERO_DE_CLIENTES_UNICOS = 2500 # <<< MUDANÇA: Vamos criar um número fixo de clientes

print("Gerando uma base de clientes recorrentes...")
# --- MUDANÇA: Criar uma lista de IDs de clientes primeiro ---
lista_de_clientes = [fake.uuid4() for _ in range(NUMERO_DE_CLIENTES_UNICOS)]
print(f"{NUMERO_DE_CLIENTES_UNICOS} clientes únicos criados.")

cidades_populares = [
    'São Paulo, SP', 'Rio de Janeiro, RJ', 'Belo Horizonte, MG', 'Curitiba, PR',
    'Florianópolis, SC', 'Porto Alegre, RS', 'Salvador, BA', 'Recife, PE',
    'Fortaleza, CE', 'Brasília, DF', 'Goiânia, GO', 'Campinas, SP'
]

viacoes = [
    'Viacao Cometa', 'Viacao 1001', 'Expresso Guanabara', 'Viacao Itapemirim',
    'Auto Viacao Catarinense', 'Expresso do Sul'
]

dados = []
for _ in range(NUMERO_DE_REGISTROS):
    is_round_trip = random.choice([True, False])
    origem_ida = random.choice(cidades_populares)
    destino_ida = random.choice([c for c in cidades_populares if c != origem_ida])
    viacao_ida = random.choice(viacoes)
    data_compra = fake.date_between(start_date='-3y', end_date='today')

    if is_round_trip:
        origem_retorno = destino_ida
        destino_retorno = origem_ida
        viacao_retorno = random.choice(viacoes)
    else:
        origem_retorno = '0'
        destino_retorno = '0'
        viacao_retorno = '1'
        
    registro = {
        'nk_ota_localizer_id': fake.uuid4(),
        # --- MUDANÇA: Escolher um cliente aleatório da nossa lista ---
        'fk_contact': random.choice(lista_de_clientes),
        'date_purchase': data_compra.strftime('%Y-%m-%d'),
        'time_purchase': fake.time(),
        'place_origin_departure': origem_ida,
        'place_destination_departure': destino_ida,
        'place_origin_return': origem_retorno,
        'place_destination_return': destino_retorno,
        'fk_departure_ota_bus_company': viacao_ida,
        'fk_return_ota_bus_company': viacao_retorno,
        'gmv_success': round(random.uniform(50.0, 450.0), 2),
        'total_tickets_quantity_success': random.randint(1, 4)
    }
    dados.append(registro)

df_viagens = pd.DataFrame(dados)
df_viagens.to_csv('viagens_clickbus.csv', index=False)

print(f"\nArquivo 'viagens_clickbus.csv' gerado com sucesso com dados de clientes recorrentes!")