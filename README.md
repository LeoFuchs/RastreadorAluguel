# Rastreador de Aluguel

> Coleta diária de anúncios de aluguel e identificação de imóveis novos em São Paulo.

O projeto usa Selenium para carregar páginas dinâmicas do Zap Imóveis e do Quinto Andar, extrai os links dos anúncios e compara coletas de datas diferentes.

## Fluxo

1. Um coletor acessa uma plataforma e salva um CSV por bairro e data em `data/raw/`.
2. `compare_daily_urls.py` compara as duas datas mais recentes de cada plataforma e bairro.
3. Os links que aparecem apenas na coleta mais recente são salvos em `data/processed/`.

## Estrutura do repositório

```text
RastreadorAluguel/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── config.py
│   ├── collection_utils.py
│   ├── generate_zap_data.py
│   ├── generate_quintoandar_data.py
│   └── compare_daily_urls.py
├── .github/
│   └── workflows/
│       └── daily-collection.yml
├── data/
│   ├── raw/
│   │   ├── README.md
│   │   ├── zapimoveis/
│   │   └── quintoandar/
│   ├── processed/
│   │   └── README.md
│   └── README.md
└── docs/
    └── README.md
```

## Componentes principais

- `config.py`: configura URLs, bairros e paginação por plataforma.
- `collection_utils.py`: deduplica URLs e grava metadados das coletas.
- `generate_zap_data.py`: coleta anúncios do Zap Imóveis. Sem `--bairro`, processa todos os bairros configurados; aceita `--paginas` para sobrescrever a configuração padrão.
- `generate_quintoandar_data.py`: coleta sequencialmente todos os bairros definidos em `BairroInfo`.
- `compare_daily_urls.py`: compara as duas coletas mais recentes e gera os anúncios novos.

## Bairros configurados

Atualmente, os coletores e o comparador estão configurados para:

- `vila_mariana`
- `vila_saude`
- `bosque_saude`

As configurações de busca ficam em `src/config.py`. Ao adicionar ou remover bairros, altere somente esse arquivo.

## Requisitos e instalação

- Python 3.10+
- Google Chrome compatível com o Selenium WebDriver

Crie e ative um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No PowerShell do Windows, ative o ambiente com `.\.venv\Scripts\Activate.ps1`.

## Execução

Execute os comandos a partir da raiz do repositório.

### Coletar dados do Zap Imóveis

```bash
python src/generate_zap_data.py --bairro vila_mariana
python src/generate_zap_data.py --bairro vila_mariana --paginas 2
python src/generate_zap_data.py
```

### Coletar dados do Quinto Andar

```bash
python src/generate_quintoandar_data.py
```

Esse comando processa todos os bairros de `BairroInfo` em sequência e cria um CSV para cada um.

### Comparar dados entre dias

```bash
python src/compare_daily_urls.py
```

### Executar a rotina diária no GitHub Actions

O workflow `.github/workflows/daily-collection.yml` pode ser iniciado manualmente ou executado diariamente pelo agendamento configurado. Ele instala Python, Chrome e as dependências, executa os dois coletores, compara as coletas e commita os CSVs e metadados gerados no repositório.

Para permitir o commit automático, o workflow usa `permissions: contents: write`. O horário do `cron` é UTC.

## Formato dos dados

Os CSVs usam uma coluna `URL`. O coletor do Quinto Andar normaliza anúncios para URLs canônicas, preservando a categoria necessária para o acesso:

```text
https://www.quintoandar.com.br/imovel/893329128/
https://www.quintoandar.com.br/classificado/129214854/
```

## Observações

- O comparador ignora bairros sem pelo menos duas datas disponíveis.
- Os dados coletados podem conter anúncios fora do bairro nominal quando a plataforma amplia os resultados da busca.
- As páginas podem mudar de estrutura ou bloquear automações.
- Cada coleta também gera um arquivo `.metadata.json` com plataforma, bairro, URL de busca, quantidade de URLs, início, fim e duração.
- Dentro de cada plataforma, um anúncio encontrado em mais de um bairro é salvo somente no primeiro bairro da ordem configurada para a execução do dia.
