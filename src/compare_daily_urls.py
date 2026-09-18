import os
import logging
from datetime import datetime

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


def comparar_urls(arquivo_hoje: str, arquivo_ontem: str) -> list[str]:
    hoje_df = pd.read_csv(arquivo_hoje)
    ontem_df = pd.read_csv(arquivo_ontem)

    if "URL" not in hoje_df.columns or "URL" not in ontem_df.columns:
        raise ValueError(f"Arquivos com colunas inválidas: {arquivo_hoje} | {arquivo_ontem}")

    urls_hoje = set(hoje_df["URL"].dropna().astype(str))
    urls_ontem = set(ontem_df["URL"].dropna().astype(str))
    novas = sorted(urls_hoje - urls_ontem)
    return novas


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
            ontem = datas[-2]
            arquivo_hoje = os.path.join(caminho_plataforma, hoje, f"{plataforma}_{bairro}_{hoje}.csv")
            arquivo_ontem = os.path.join(caminho_plataforma, ontem, f"{plataforma}_{bairro}_{ontem}.csv")

            if not os.path.exists(arquivo_hoje) or not os.path.exists(arquivo_ontem):
                continue

            try:
                urls_novas = comparar_urls(arquivo_hoje, arquivo_ontem)
                arquivo_saida = os.path.join(output_root, f"{plataforma}_{bairro}_novos.csv")
                pd.DataFrame({"URL": urls_novas}).to_csv(arquivo_saida, index=False)
                logger.info("%s / %s: %s novos; arquivo: %s", plataforma, bairro, len(urls_novas), arquivo_saida)
            except Exception:
                logger.exception("Falha ao comparar %s / %s", plataforma, bairro)


if __name__ == "__main__":
    main()
