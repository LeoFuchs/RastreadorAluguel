import argparse
import logging
import os
import re
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

try:
    from src.collection_utils import criar_metadados, deduplicar_urls, salvar_metadados
    from src.config import QUINTOANDAR_BAIRROS
except ModuleNotFoundError:
    from collection_utils import criar_metadados, deduplicar_urls, salvar_metadados
    from config import QUINTOANDAR_BAIRROS


BairroInfo = QUINTOANDAR_BAIRROS
logger = logging.getLogger(__name__)


def extrair_codigo_fonte_com_rolagem(url: str) -> str:
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(5)

        def quantidade_de_apartamentos() -> int:
            return len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='house-card-container-rent']"))

        while True:
            quantidade_anterior = quantidade_de_apartamentos()
            botoes_ver_mais = driver.find_elements(By.XPATH, "//button[contains(text(), 'Ver mais')]")
            if not botoes_ver_mais:
                break

            botoes_ver_mais[0].click()
            time.sleep(5)

            if quantidade_de_apartamentos() <= quantidade_anterior:
                break

        return driver.page_source
    finally:
        driver.quit()


def normalizar_url_imovel(href: str) -> str | None:
    correspondencia = re.search(r"/(imovel|classificado)/(\d+)(?:/|$)", href)
    if correspondencia is None:
        return None

    categoria = correspondencia.group(1)
    identificador = correspondencia.group(2)
    return f"https://www.quintoandar.com.br/{categoria}/{identificador}/"


def coletar_urls_do_bairro(bairro: str) -> list[str]:
    url_busca = BairroInfo[bairro]
    codigo_fonte = extrair_codigo_fonte_com_rolagem(url_busca)
    soup = BeautifulSoup(codigo_fonte, "lxml")

    urls = []
    cards = soup.find_all("div", {"data-testid": "house-card-container-rent"})
    for card in cards:
        for link in card.find_all("a", href=True):
            url_imovel = normalizar_url_imovel(link["href"])
            if url_imovel is not None:
                urls.append(url_imovel)

    return deduplicar_urls(urls)


def salvar_csv(urls: list[str], bairro: str, inicio: datetime, fim: datetime) -> str:
    hoje = datetime.now().strftime("%Y_%m_%d")
    pasta_saida = os.path.join("data", "raw", "quintoandar", bairro, hoje)
    os.makedirs(pasta_saida, exist_ok=True)

    arquivo = os.path.join(pasta_saida, f"quintoandar_{bairro}_{hoje}.csv")
    pd.DataFrame({"URL": urls}).to_csv(arquivo, index=False)
    metadados = criar_metadados("quintoandar", bairro, BairroInfo[bairro], len(urls), inicio, fim)
    salvar_metadados(arquivo, metadados)
    return arquivo


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    argparse.ArgumentParser(
        description="Coleta URLs de aluguel do Quinto Andar para todos os bairros configurados."
    ).parse_args()

    for bairro in BairroInfo:
        inicio = datetime.now()
        try:
            urls = coletar_urls_do_bairro(bairro)
            fim = datetime.now()
            arquivo = salvar_csv(urls, bairro, inicio, fim)
        except Exception:
            logger.exception("Falha ao coletar Quinto Andar para %s", bairro)
            continue

        logger.info("Quinto Andar: %s URLs para %s; arquivo: %s", len(urls), bairro, arquivo)


if __name__ == "__main__":
    main()
