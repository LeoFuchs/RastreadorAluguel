# Dados processados

Este diretório armazena os resultados da comparação diária.

O arquivo `compare_daily_urls.py` cria um CSV por plataforma e bairro, por exemplo:

```text
zapimoveis_vila_mariana_novos.csv
quintoandar_vila_mariana_novos.csv
```

Cada arquivo contém uma coluna `URL` com os anúncios presentes na coleta mais recente e que não apareceram em nenhuma coleta dos sete dias anteriores. São usadas as coletas disponíveis nesse intervalo. Arquivos só são gerados quando há uma coleta mais recente e pelo menos uma coleta anterior disponível nos sete dias.
