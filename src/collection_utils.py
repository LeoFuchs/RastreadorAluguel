import json
import os
from datetime import datetime
from typing import Any


def deduplicar_urls(urls: list[str], urls_ja_vistas: set[str] | None = None) -> list[str]:
    urls_unicas = []
    urls_vistas = set() if urls_ja_vistas is None else urls_ja_vistas

    for url in urls:
        if url and url not in urls_vistas:
            urls_unicas.append(url)
            urls_vistas.add(url)

    return urls_unicas


def salvar_metadados(arquivo_csv: str, metadados: dict[str, Any]) -> str:
    arquivo_metadados = f"{os.path.splitext(arquivo_csv)[0]}.metadata.json"
    with open(arquivo_metadados, "w", encoding="utf-8") as arquivo:
        json.dump(metadados, arquivo, ensure_ascii=False, indent=2)
    return arquivo_metadados


def criar_metadados(
    plataforma: str,
    bairro: str,
    url_busca: str,
    quantidade_urls: int,
    inicio: datetime,
    fim: datetime,
) -> dict[str, Any]:
    return {
        "plataforma": plataforma,
        "bairro": bairro,
        "url_busca": url_busca,
        "quantidade_urls": quantidade_urls,
        "inicio": inicio.isoformat(timespec="seconds"),
        "fim": fim.isoformat(timespec="seconds"),
        "duracao_segundos": round((fim - inicio).total_seconds(), 2),
    }
