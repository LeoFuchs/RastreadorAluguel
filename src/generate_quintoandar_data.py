import argparse
import os
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


BairroInfo = {
    "santa_cecilia": "https://www.quintoandar.com.br/alugar/imovel/santa-cecilia-sao-paulo-sp-brasil/de-3000-a-6000-reais/apartamento/kitnet/de-45-a-110-m2",
    "perdizes": "https://www.quintoandar.com.br/alugar/imovel/perdizes-sao-paulo-sp-brasil/de-3000-a-6000-reais/apartamento/kitnet/de-45-a-110-m2",
    "barra_funda": "https://www.quintoandar.com.br/alugar/imovel/barra-funda-sao-paulo-sp-brasil/de-3000-a-6000-reais/apartamento/kitnet/de-45-a-110-m2",
}


def extrair_codigo_fonte_com_rolagem(url: str) -> str:
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(5)

        def is_button_visible() -> bool:
            return len(driver.find_elements(By.XPATH, "//button[contains(text(), 'Ver mais')]")) > 0

        while is_button_visible():
            driver.find_element(By.XPATH, "//button[contains(text(), 'Ver mais')]").click()
            time.sleep(7)

        return driver.page_source
    finally:
        driver.quit()


def coletar_urls_do_bairro(bairro: str) -> list[str]:
    url_busca = BairroInfo[bairro]
    codigo_fonte = extrair_codigo_fonte_com_rolagem(url_busca)
    soup = BeautifulSoup(codigo_fonte, "lxml")

    urls = []
    cards = soup.find_all("div", {"data-testid": "house-card-container-rent"})
    for card in cards:
        for link in card.find_all("a", href=True):
            urls.append(link["href"])

    return urls


def salvar_csv(urls: list[str], bairro: str) -> str:
    hoje = datetime.now().strftime("%Y_%m_%d")
    pasta_saida = os.path.join("data", "raw", "quintoandar", bairro, hoje)
    os.makedirs(pasta_saida, exist_ok=True)

    arquivo = os.path.join(pasta_saida, f"quintoandar_{bairro}_{hoje}.csv")
    pd.DataFrame({"URL": urls}).to_csv(arquivo, index=False)
    return arquivo


def main():
    parser = argparse.ArgumentParser(description="Coleta URLs de aluguel do Quinto Andar por bairro.")
    parser.add_argument("--bairro", required=True, choices=sorted(BairroInfo.keys()))
    args = parser.parse_args()

    bairro = args.bairro
    urls = coletar_urls_do_bairro(bairro)
    arquivo = salvar_csv(urls, bairro)

    print(f"Total de URLs coletadas para {bairro}: {len(urls)}")
    print(f"Arquivo salvo em: {arquivo}")


if __name__ == "__main__":
    main()
