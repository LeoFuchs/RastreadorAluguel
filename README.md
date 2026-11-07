# Rastreador de Aluguel

> Coleta diária de anúncios do Quinto Andar e curadoria automática de imóveis para aluguel em São Paulo.

O projeto usa Selenium para coletar URLs do Quinto Andar, identifica anúncios novos e usa o Gemini para classificá-los. Os resultados são registrados em CSV e enviados para uma aba do Google Sheets. Por enquanto, o fluxo diário consulta somente o Quinto Andar.

## Fluxo diário

O workflow `.github/workflows/daily-collection.yml` pode ser iniciado manualmente ou roda diariamente às 10:00 UTC.

1. `generate_quintoandar_data.py` coleta URLs para cada bairro configurado e salva CSVs e metadados em `data/raw/quintoandar/`.
2. `compare_daily_urls.py` compara a coleta mais recente com as coletas disponíveis dos sete dias anteriores e salva anúncios novos em `data/processed/`.
3. `curadoria_imoveis.py` lê esses anúncios, extrai detalhes das páginas e solicita ao Gemini uma classificação em JSON.
4. As classificações são acrescentadas à aba configurada do Google Sheets e ao CSV diário em `data/curated/`.
5. `urls_processadas.json` registra URLs concluídas e `urls_pendentes.json` mantém as que ainda precisam ser processadas. A fila permite continuar em execuções futuras respeitando o limite diário.
6. O workflow commita os dados coletados e o estado da curadoria no repositório. Se alguma URL falhar, salva a fila e então sinaliza falha na execução.

## Estrutura do repositório

```text
RastreadorAluguel/
├── src/
│   ├── config.py
│   ├── collection_utils.py
│   ├── generate_quintoandar_data.py
│   ├── compare_daily_urls.py
│   └── curadoria_imoveis.py
├── .github/workflows/daily-collection.yml
└── data/
    ├── raw/quintoandar/
    ├── processed/
    └── curated/
```

## Componentes e bairros

- `config.py`: configura URLs e bairros do Quinto Andar.
- `collection_utils.py`: deduplica URLs e grava metadados das coletas.
- `generate_quintoandar_data.py`: coleta sequencialmente todos os bairros configurados.
- `compare_daily_urls.py`: compara a coleta mais recente com as coletas disponíveis dos sete dias anteriores.
- `curadoria_imoveis.py`: extrai dados dos anúncios novos, classifica-os com Gemini e envia os resultados ao Google Sheets e ao CSV local.

Os bairros configurados em `src/config.py` são `vila_mariana`, `vila_saude` e `bosque_saude`.

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

## Configuração do Gemini e Google Sheets

Configure estes **secrets** no repositório GitHub:

- `GEMINI_API_KEY`: chave de API para classificar os anúncios com Gemini.
- `GOOGLE_SHEETS_SPREADSHEET_ID`: ID da planilha.
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: JSON da conta de serviço. Compartilhe a planilha com o e-mail dessa conta e conceda acesso de editor.

Variáveis opcionais do repositório:

- `GEMINI_MODEL`: modelo Gemini; padrão `gemini-2.5-flash`.
- `GOOGLE_SHEETS_WORKSHEET`: nome da aba; padrão `Curadoria Imóveis`. Se não existir, o script tenta criá-la.
- `CURATORIA_MAX_URLS`: máximo de URLs selecionadas da fila por execução; padrão `25`.

O workflow usa `permissions: contents: write` para persistir CSVs, URLs processadas e a fila pendente no repositório.

## Execução manual

Execute os comandos a partir da raiz do repositório:

```bash
python src/generate_quintoandar_data.py
python src/compare_daily_urls.py
python src/curadoria_imoveis.py
```

Para executar a curadoria manualmente, configure antes as mesmas variáveis de ambiente e credenciais usadas pelo workflow. O coletor processa os bairros em sequência; o comparador só gera resultados quando há uma coleta atual e pelo menos uma coleta anterior disponível nos sete dias.

## Formato e observações dos dados

Os CSVs usam uma coluna `URL`. O coletor normaliza anúncios para URLs canônicas, preservando a categoria necessária para o acesso:

```text
https://www.quintoandar.com.br/imovel/893329128/
https://www.quintoandar.com.br/classificado/129214854/
```

- Os dados coletados podem conter anúncios fora do bairro nominal quando os resultados do Quinto Andar incluem imóveis de áreas próximas.
- As páginas podem mudar de estrutura ou bloquear automações.
- Cada coleta também gera um arquivo `.metadata.json` com plataforma, bairro, URL de busca, quantidade de URLs, início, fim e duração.
- Um anúncio encontrado em mais de um bairro é salvo somente no primeiro bairro da ordem configurada para a execução do dia.
- A classificação depende do conteúdo acessível na página do anúncio e da disponibilidade das APIs Gemini e Google Sheets.
