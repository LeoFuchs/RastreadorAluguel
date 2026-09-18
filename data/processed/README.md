# Dados processados

Este diretório armazena os resultados da comparação diária.

O arquivo `compare_daily_urls.py` cria um CSV por plataforma e bairro, por exemplo:

```text
zapimoveis_vila_mariana_novos.csv
quintoandar_vila_mariana_novos.csv
```

Cada arquivo contém uma coluna `URL` com os anúncios presentes na coleta mais recente e ausentes na coleta anterior. Arquivos só são gerados quando existem pelo menos duas datas válidas em `data/raw/`.
