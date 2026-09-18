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

## Componentes principais

- `generate_zap_data.py`: coleta anúncios do Zap Imóveis para um bairro por execução. Aceita `--paginas` para sobrescrever a configuração padrão.
- `generate_quintoandar_data.py`: coleta sequencialmente todos os bairros definidos em `BairroInfo`.
- `compare_daily_urls.py`: compara as duas coletas mais recentes e gera os anúncios novos.

## Bairros configurados

Atualmente, os coletores e o comparador estão configurados para:

- `vila_mariana`
- `vila_saude`
- `bosque_saude`

As configurações de busca ficam no início de cada coletor. Ao adicionar ou remover bairros, atualize também `BAIRROS` em `compare_daily_urls.py`.

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
- O processo ainda não possui agendamento, testes automatizados ou persistência além dos CSVs.
