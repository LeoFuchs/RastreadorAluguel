# Dados brutos

Este diretório armazena os dados coletados diretamente das plataformas.

## Estrutura esperada

```text
data/raw/
├── zapimoveis/
│   └── vila_mariana/
│       └── YYYY_MM_DD/
│           └── zapimoveis_vila_mariana_YYYY_MM_DD.csv
└── quintoandar/
    └── vila_mariana/
        └── YYYY_MM_DD/
            └── quintoandar_vila_mariana_YYYY_MM_DD.csv
```

Os arquivos são organizados por plataforma, bairro e data. Os nomes reais dos bairros vêm das configurações em `src/`.
