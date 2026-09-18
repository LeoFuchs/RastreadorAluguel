import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.collection_utils import criar_metadados, deduplicar_urls, salvar_metadados
from src.compare_daily_urls import comparar_urls
from src.generate_quintoandar_data import normalizar_url_imovel


class CollectionUtilsTests(unittest.TestCase):
    def test_deduplicar_urls_preserva_ordem_e_remove_vazios(self):
        self.assertEqual(deduplicar_urls(["a", "a", "", "b", "a"]), ["a", "b"])

    def test_metadados_registram_quantidade_e_duracao(self):
        inicio = datetime(2026, 9, 18, 10, 0, 0)
        fim = datetime(2026, 9, 18, 10, 0, 2)
        metadados = criar_metadados("quintoandar", "vila_mariana", "https://busca", 3, inicio, fim)

        self.assertEqual(metadados["quantidade_urls"], 3)
        self.assertEqual(metadados["duracao_segundos"], 2.0)

    def test_salvar_metadados_cria_json(self):
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo_csv = str(Path(diretorio) / "coleta.csv")
            caminho = salvar_metadados(arquivo_csv, {"quantidade_urls": 4})

            with open(caminho, encoding="utf-8") as arquivo:
                self.assertEqual(json.load(arquivo)["quantidade_urls"], 4)


class ScraperTests(unittest.TestCase):
    def test_normalizar_url_preserva_categoria(self):
        self.assertEqual(
            normalizar_url_imovel("/classificado/129214854/alugar?rank=1"),
            "https://www.quintoandar.com.br/classificado/129214854/",
        )
        self.assertEqual(
            normalizar_url_imovel("/imovel/893329128/alugar/apartamento"),
            "https://www.quintoandar.com.br/imovel/893329128/",
        )

    def test_normalizar_url_rejeita_caminho_desconhecido(self):
        self.assertIsNone(normalizar_url_imovel("/buscar/129214854/"))


class ComparisonTests(unittest.TestCase):
    def test_comparar_urls_retorna_apenas_anuncios_novos(self):
        with tempfile.TemporaryDirectory() as diretorio:
            hoje = Path(diretorio) / "hoje.csv"
            ontem = Path(diretorio) / "ontem.csv"
            hoje.write_text("URL\na\nb\nb\n", encoding="utf-8")
            ontem.write_text("URL\na\n", encoding="utf-8")

            self.assertEqual(comparar_urls(str(hoje), str(ontem)), ["b"])


if __name__ == "__main__":
    unittest.main()
