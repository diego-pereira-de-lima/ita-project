from pathlib import Path
import pandas as pd

class SinanDownloader:
    """
    Classe para baixar e consolidar dados do SINAN (via pysus) 
    para múltiplas doenças e anos, salvando arquivos em formato Parquet.

    Atributos:
        destino (Path): Caminho da pasta onde os arquivos serão salvos.
    """

    def __init__(self, destino_path):
        """
        Inicializa o caminho de destino para salvar os arquivos.

        Parâmetros:
        - destino_path (str or Path): Caminho da pasta no Google Drive ou local.
        """
        self.destino = Path(destino_path)
        self.destino.mkdir(parents=True, exist_ok=True)

    def baixar_doencas(self, list_doenca, list_year, sinan):
        """
        Baixa e consolida os dados de uma lista de doenças e anos fornecidos.

        Parâmetros:
        - list_doenca (list): Lista de códigos das doenças (ex: ["FTIF", "TUBE"]).
        - list_year (list): Lista dos anos desejados (ex: [2018, 2019, 2020]).
        - sinan (obj): Objeto ou módulo `sinan` do pysus.online_data, já importado.

        Retorna:
        - df_hist (pd.DataFrame): DataFrame com todos os registros baixados e concatenados.
        """
        df_hist = pd.DataFrame()

        for doenca in list_doenca:
            print(f"🔄 Baixando dados de: {doenca}")
            try:
                files = sinan.get_files(dis_code=doenca, year=list_year)
            except Exception as e:
                print(f"⚠️ Erro ao buscar arquivos da doença {doenca}: {e}")
                continue

            for i, year in enumerate(list_year):
                try:
                    file_parquet = files[i].download()
                    df_temp = file_parquet.to_dataframe()
                    df_temp["ano"] = year
                    df_hist = pd.concat([df_hist, df_temp], axis=0)
                except Exception as e:
                    print(f"Falha no download ou processamento para {doenca} - {year}: {e}")

            # Salva o acumulado por doença
            try:
                df_hist.to_parquet(self.destino / f"SINAN_{doenca}.parquet")
                print(f"Arquivo salvo: SINAN_{doenca}.parquet")
            except Exception as e:
                print(f"Erro ao salvar o arquivo de {doenca}: {e}")

        return df_hist