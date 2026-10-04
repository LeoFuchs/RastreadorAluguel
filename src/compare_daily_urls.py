import os
import logging
from datetime import datetime, timedelta

import pandas as pd

try:
    from src.config import PLATAFORMAS
except ModuleNotFoundError:
    from config import PLATAFORMAS


logger = logging.getLogger(__name__)


def listar_pastas_por_data(base_dir: str) -> list[str]:
    if not os.path.exists(base_dir):
        return []
    return sorted(
        [nome for nome in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, nome))],
        key=lambda d: datetime.strptime(d, "%Y_%m_%d") if d.count("_") == 2 else datetime.min,
    )


def comparar_urls(arquivo_hoje: str, arquivos_anteriores: list[str]) -> list[str]:
    hoje_df = pd.read_csv(arquivo_hoje)

    if "URL" not in hoje_df.columns:
        raise ValueError(f"Arquivo com coluna inválida: {arquivo_hoje}")

    urls_hoje = set(hoje_df["URL"].dropna().astype(str))
    urls_anteriores = set()
    for arquivo_anterior in arquivos_anteriores:
        anterior_df = pd.read_csv(arquivo_anterior)
        if "URL" not in anterior_df.columns:
            raise ValueError(f"Arquivo com coluna inválida: {arquivo_anterior}")
        urls_anteriores.update(anterior_df["URL"].dropna().astype(str))

    return sorted(urls_hoje - urls_anteriores)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    base_root = os.path.join("data", "raw")
    output_root = os.path.join("data", "processed")
    os.makedirs(output_root, exist_ok=True)

    for plataforma, bairros in PLATAFORMAS.items():
        for bairro in bairros:
            caminho_plataforma = os.path.join(base_root, plataforma, bairro)
            if not os.path.exists(caminho_plataforma):
                continue

            datas = listar_pastas_por_data(caminho_plataforma)
            if len(datas) < 2:
                continue

            hoje = datas[-1]
            data_hoje = datetime.strptime(hoje, "%Y_%m_%d").date()
            primeiro_dia = data_hoje - timedelta(days=7)
            datas_anteriores = []
            for data in datas[:-1]:
                try:
                    data_anterior = datetime.strptime(data, "%Y_%m_%d").date()
                except ValueError:
                    continue
                if primeiro_dia <= data_anterior < data_hoje:
                    datas_anteriores.append(data)

            arquivo_hoje = os.path.join(caminho_plataforma, hoje, f"{plataforma}_{bairro}_{hoje}.csv")
            arquivos_anteriores = [
                os.path.join(caminho_plataforma, data, f"{plataforma}_{bairro}_{data}.csv")
                for data in datas_anteriores
            ]
            arquivos_anteriores = [arquivo for arquivo in arquivos_anteriores if os.path.exists(arquivo)]

            if not os.path.exists(arquivo_hoje) or not arquivos_anteriores:
                continue

            try:
                urls_novas = comparar_urls(arquivo_hoje, arquivos_anteriores)
                arquivo_saida = os.path.join(output_root, f"{plataforma}_{bairro}_novos.csv")
                pd.DataFrame({"URL": urls_novas}).to_csv(arquivo_saida, index=False)
                logger.info(
                    "%s / %s: %s novos comparados com %s coletas anteriores; arquivo: %s",
                    plataforma,
                    bairro,
                    len(urls_novas),
                    len(arquivos_anteriores),
                    arquivo_saida,
                )
            except Exception:
                logger.exception("Falha ao comparar %s / %s", plataforma, bairro)


if __name__ == "__main__":
    main()
