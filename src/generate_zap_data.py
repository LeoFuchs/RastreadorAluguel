import argparse
import os
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


BairroInfo = {
    "santa_cecilia": {
        "zona": "sp+sao-paulo+centro+sta-cecilia",
        "paginas": 2,
    },
    "perdizes": {
        "zona": "sp+sao-paulo+zona-oeste+perdizes",
        "paginas": 4,
    },
    "barra_funda": {
        "zona": "sp+sao-paulo+zona-oeste+barra-funda",
        "paginas": 2,
    },
}


def extrair_codigo_fonte_com_rolagem(url: str) -> str:
    driver = webdriver.Chrome()
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


def salvar_csv(urls: list[str], bairro: str, data_dir: str) -> str:
    os.makedirs(data_dir, exist_ok=True)
    arquivo = os.path.join(data_dir, f"zapimoveis_{bairro}_{datetime.now().strftime('%Y_%m_%d')}.csv")
    pd.DataFrame({"URL": urls}).to_csv(arquivo, index=False)
    return arquivo


def coletar_urls_do_bairro(bairro: str, paginas: int = None) -> list[str]:
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

    return urls


def main():
    parser = argparse.ArgumentParser(description="Coleta URLs de aluguel do Zap Imóveis por bairro.")
    parser.add_argument("--bairro", required=True, choices=sorted(BairroInfo.keys()))
    parser.add_argument("--paginas", type=int, default=None)
    args = parser.parse_args()

    bairro = args.bairro
    paginas = args.paginas
    urls = coletar_urls_do_bairro(bairro, paginas)

    hoje = datetime.now().strftime("%Y_%m_%d")
    pasta_saida = os.path.join("data", "raw", "zapimoveis", bairro, hoje)
    arquivo = salvar_csv(urls, bairro, pasta_saida)

    print(f"Total de URLs coletadas para {bairro}: {len(urls)}")
    print(f"Arquivo salvo em: {arquivo}")


if __name__ == "__main__":
    main()
