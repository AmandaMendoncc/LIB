"""Módulo para coleta de dados meteorológicos de arquivos locais e APIs."""

import logging
import pandas as pd
import requests
from typing import Optional

from solar_pv_analytics.utils.config_models import DataSourcesConfig

def load_pvgis_tmy_from_csv(file_path: str, tz: str) -> Optional[pd.DataFrame]:
    """
    Carrega dados TMY de um arquivo CSV do PVGIS, formata o índice e renomeia colunas.

    Args:
        file_path (str): O caminho para o arquivo CSV do PVGIS.
        tz (str): A timezone para localizar o índice de tempo.

    Returns:
        Optional[pd.DataFrame]: DataFrame com colunas padronizadas para pvlib
                                ('ghi', 'dni', 'dhi', 'temp_air', 'wind_speed')
                                ou None se o arquivo não for encontrado.
    """
    logging.info(f"Carregando dados TMY do PVGIS do arquivo: {file_path}")
    try:
        tmy_data = pd.read_csv(
            file_path,
            skiprows=17,
            nrows=8760,
            usecols=["time(UTC)", "T2m", "G(h)", "Gb(n)", "Gd(h)", "WS10m"],
            index_col=0
        )
        tmy_data.index = pd.to_datetime(tmy_data.index, format="%Y%m%d:%H%M", utc=True)
        tmy_data = tmy_data.index.tz_localize(None).tz_localize(tz)
        tmy_data.index.name = "time"

        # Renomeia colunas para o padrão esperado pelo pvlib.ModelChain
        column_mapping = {
            "T2m": "temp_air",
            "G(h)": "ghi",
            "Gb(n)": "dni",
            "Gd(h)": "dhi",
            "WS10m": "wind_speed",
        }
        tmy_data.rename(columns=column_mapping, inplace=True)
        
        logging.info("Dados do PVGIS carregados e formatados com sucesso.")
        return tmy_data
    except FileNotFoundError:
        logging.error(f"Arquivo não encontrado: {file_path}", exc_info=True)
        return None

def fetch_open_meteo_forecast(lat: float, lon: float, tz: str, api_url: str) -> Optional[pd.DataFrame]:
    """
    Busca a previsão do tempo da API Open-Meteo.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        tz (str): Timezone no formato IANA (ex: 'America/Sao_Paulo').
        api_url (str): URL base da API Open-Meteo.

    Returns:
        Optional[pd.DataFrame]: DataFrame com dados de previsão ou None em caso de falha.
    """
    logging.info(f"Buscando previsão do tempo da Open-Meteo para lat={lat}, lon={lon}")
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": tz,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Lança exceção para status de erro HTTP
        
        data = response.json()['hourly']
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        
        logging.info("Previsão da Open-Meteo obtida com sucesso.")
        return df
    except requests.RequestException:
        logging.error("Falha ao buscar dados da Open-Meteo.", exc_info=True)
        return None