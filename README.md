# Projeto MyNextRide - Challenge FIAP

## Descrição

Este projeto é a entrega final para o challenge da FIAP em parceria com a ClickBus. A solução consiste em uma aplicação web de Business Intelligence que analisa dados de viagens de ônibus para extrair insights sobre o comportamento dos usuários.

A aplicação utiliza uma arquitetura moderna com um backend em Python (Flask) que serve os dados analisados a partir de um banco de dados Oracle, e um frontend customizado (HTML, CSS, JavaScript) que consome esses dados e os exibe em um dashboard interativo.

## Estrutura de Pastas
mynextride_project/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── 1_geracao_dados.py
├── 2_persistencia_oracle.py
├── 3_analise_dados.ipynb
├── api.py
├── requirements.txt
└── README.md

## Pré-requisitos

- Python 3.8+
- Acesso a um banco de dados Oracle com as devidas credenciais (usuário, senha, DSN).
- Um ambiente virtual Python (recomendado).

## Como Configurar e Executar o Projeto

Siga os passos abaixo na ordem correta.

### 1. Preparar o Ambiente

Clone o repositório e crie um ambiente virtual:

```bash
git clone <url_do_seu_repositorio>
cd mynextride_project
python -m venv venv
source venv/bin/activate 
