import argparse
import logging
import os
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:
    from src.collection_utils import criar_metadados, deduplicar_urls, salvar_metadados
    from src.config import ZAPIMOVEIS_BAIRROS
except ModuleNotFoundError:
    from collection_utils import criar_metadados, deduplicar_urls, salvar_metadados
    from config import ZAPIMOVEIS_BAIRROS


BairroInfo = ZAPIMOVEIS_BAIRROS
logger = logging.getLogger(__name__)


def extrair_codigo_fonte_com_rolagem(url: str) -> str:
    opcoes = Options()
    opcoes.add_argument("--headless=new")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=opcoes)
    try:
        driver.get(url)
        time.sleep(5)

        codigo_fonte = ""
        posicao_rolagem = 0
        incremento_rolagem = 800
        altura_total = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script(f"window.scrollTo(0, {posicao_rolagem});")
            time.sleep(1)
            posicao_rolagem += incremento_rolagem

            nova_altura = driver.execute_script("return document.body.scrollHeight")
            if posicao_rolagem >= nova_altura:
                codigo_fonte = driver.page_source
                break

            altura_total = nova_altura

        return codigo_fonte
    finally:
        driver.quit()


def gerar_url_busca_bairro(bairro: str, pagina: int) -> str:
    configuracao = BairroInfo[bairro]
    zona = configuracao["zona"]
    return (
        "https://www.zapimoveis.com.br/aluguel/apartamentos/"
        f"{zona}/?__ab=olx:control,zap-newldp:control,super-high:control,"
        "exp-aa-test:control,novopos:new,rp-imob:enabled"
        f"&pagina={pagina}"
    )


def salvar_csv(urls: list[str], bairro: str, data_dir: str, inicio: datetime, fim: datetime) -> str:
    os.makedirs(data_dir, exist_ok=True)
    arquivo = os.path.join(data_dir, f"zapimoveis_{bairro}_{datetime.now().strftime('%Y_%m_%d')}.csv")
    pd.DataFrame({"URL": urls}).to_csv(arquivo, index=False)
    metadados = criar_metadados("zapimoveis", bairro, gerar_url_busca_bairro(bairro, 1), len(urls), inicio, fim)
    salvar_metadados(arquivo, metadados)
    return arquivo


def coletar_urls_do_bairro(
    bairro: str, paginas: int = None, urls_ja_vistas: set[str] | None = None
) -> list[str]:
    if paginas is None:
        paginas = BairroInfo[bairro]["paginas"]

    urls = []
    for pagina in range(1, paginas + 1):
        url_busca = gerar_url_busca_bairro(bairro, pagina)
        codigo_fonte = extrair_codigo_fonte_com_rolagem(url_busca)
        soup = BeautifulSoup(codigo_fonte, "lxml")

        divs = soup.find_all("div", {"data-position": True})
        for div in divs:
            for link in div.find_all("a", href=True):
                urls.append(link["href"])

    return deduplicar_urls(urls, urls_ja_vistas)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Coleta URLs de aluguel do Zap Imóveis por bairro.")
    parser.add_argument("--bairro", choices=sorted(BairroInfo.keys()))
    parser.add_argument("--paginas", type=int, default=None)
    args = parser.parse_args()

    bairros = [args.bairro] if args.bairro else BairroInfo
    urls_ja_vistas = set()
    for bairro in bairros:
        inicio = datetime.now()
        try:
            urls = coletar_urls_do_bairro(bairro, args.paginas, urls_ja_vistas)
            hoje = datetime.now().strftime("%Y_%m_%d")
            pasta_saida = os.path.join("data", "raw", "zapimoveis", bairro, hoje)
            arquivo = salvar_csv(urls, bairro, pasta_saida, inicio, datetime.now())
            logger.info("Zap Imóveis: %s URLs para %s; arquivo: %s", len(urls), bairro, arquivo)
        except Exception:
            logger.exception("Falha ao coletar Zap Imóveis para %s", bairro)


if __name__ == "__main__":
    main()
