# Rastreador de Aluguel

Este projeto coleta e compara anúncios de aluguel de diferentes bairros de São Paulo, buscando automatizar a identificação de imóveis novos em plataformas como Zap Imóveis e Quinto Andar.

## Objetivo

A ideia principal é monitorar listas de imóveis por bairro, faixa de preço e área, armazenar essas listas em arquivos estruturados e comparar o conteúdo entre datas para identificar anúncios que surgiram recentemente.

Com isso, o projeto ajuda a:

- acompanhar a oferta de aluguel por região;
- identificar imóveis novos em relação ao dia anterior;
- reduzir a necessidade de checar manualmente cada plataforma;
- servir como base para análise de mercado e comparação entre bairros.

## Fluxo do projeto

1. Coleta dos dados
   - acessa as páginas de busca das plataformas;
   - carrega os resultados de imóveis;
   - extrai os links dos anúncios;
   - salva os dados em arquivos CSV.

2. Organização por bairro e data
   - cada execução gera registros por bairro e por data;
   - os dados ficam organizados em pastas temáticas.

3. Comparação entre dias
   - o sistema lê os dados mais recentes e os compara com o período anterior;
   - mantém apenas os imóveis que não apareciam antes;
   - gera uma lista de anúncios novos.

## Estrutura do repositório

```text
RastreadorAluguel/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── generate_zap_data.py
│   ├── generate_quintoandar_data.py
│   └── compare_daily_urls.py
├── data/
│   ├── raw/
│   │   ├── README.md
│   │   ├── zapimoveis/
│   │   └── quintoandar/
│   ├── processed/
│   │   └── README.md
│   └── README.md
├── notebooks/
│   └── legacy/
│       └── README.md
└── docs/
    └── README.md
```

## Pastas principais

### src/
Contém os scripts Python responsáveis pela coleta e processamento dos dados.

- `generate_zap_data.py`: coleta anúncios do Zap Imóveis.
- `generate_quintoandar_data.py`: coleta anúncios do Quinto Andar.
- `compare_daily_urls.py`: compara CSVs de diferentes dias e gera novidades.

### data/
Armazena os dados em bruto e os resultados processados.

- `data/raw/`: arquivos diários antes da comparação.
- `data/processed/`: listas finais de anúncios novos.

### notebooks/
Mantém a referência histórica dos notebooks originais, que foram convertidos em Python para facilitar manutenção e execução automatizada.

## Bairros monitorados

O projeto cobre os seguintes bairros de São Paulo:

- Santa Cecília
- Perdizes
- Barra Funda

## Requisitos

Para executar o projeto, você precisará de:

- Python 3.10+
- pandas
- selenium
- beautifulsoup4
- requests
- lxml

## Instalação

1. Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

### Coletar dados do Zap Imóveis

```bash
python src/generate_zap_data.py --bairro santa_cecilia --paginas 2
```

### Coletar dados do Quinto Andar

```bash
python src/generate_quintoandar_data.py --bairro perdizes
```

### Comparar dados entre dias

```bash
python src/compare_daily_urls.py
```

## Observações

- Os dados são coletados a partir de páginas públicas e podem variar conforme a estrutura dos sites.
- O processo depende da disponibilidade e estabilidade dos elementos HTML.
- O repositório foi reorganizado para facilitar manutenção e expandir a coleta para mais bairros ou plataformas.

## Finalidade

Este projeto é uma solução prática de automação para monitoramento de imóveis em aluguel, útil para quem deseja acompanhar oportunidades em mercados específicos de forma estruturada e recorrente.
