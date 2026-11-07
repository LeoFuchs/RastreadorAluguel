# Dados processados

Este diretório armazena os resultados da comparação diária.

O arquivo `compare_daily_urls.py` cria um CSV por bairro, por exemplo:

```text
quintoandar_vila_mariana_novos.csv
```

Cada arquivo contém uma coluna `URL` com os anúncios presentes na coleta mais recente e que não apareceram nas coletas disponíveis dos sete dias anteriores. Arquivos só são gerados quando há uma coleta mais recente e pelo menos uma coleta anterior disponível nos sete dias.
