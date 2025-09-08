"""Módulo para coleta de dados meteorológicos de arquivos locais e APIs."""

import logging
import pandas as pd
import requests
import streamlit as st 
from typing import Optional
from solar_pv_analytics.utils.config_models import DataSourcesConfig


@st.cache_data
def load_weather_data(tmy_path='data/pvgis/brasilia_pvgis.csv', tz='America/Sao_Paulo'):
    """
    Carrega e formata os dados meteorológicos TMY do PVGIS.
    Garante que o índice esteja ordenado.
    """
    tmy_data = pd.read_csv(
        tmy_path, skiprows=17, nrows=8760,
        usecols=["time(UTC)", "T2m", "G(h)", "Gb(n)", "Gd(h)", "WS10m"], index_col=0
    )
    tmy_data.index = pd.to_datetime(tmy_data.index, format="%Y%m%d:%H%M", utc=True)
    tmy_data = tmy_data.tz_convert(tz)
    
    column_mapping = {
        "T2m": "temp_air", "G(h)": "ghi", "Gb(n)": "dni",
        "Gd(h)": "dhi", "WS10m": "wind_speed",
    }
    tmy_data.rename(columns=column_mapping, inplace=True)
    
    # Garante que o índice da série temporal esteja ordenado.
    # Isso é crucial para fatiamentos (.loc) e seleções de intervalo confiáveis.
    tmy_data.sort_index(inplace=True)
    
    return tmy_data


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
        # Corrigir manejo do índice para timezone
        tmy_data.index = pd.to_datetime(tmy_data.index, format="%Y%m%d:%H%M", utc=True)
        tmy_data.index = tmy_data.index.tz_localize(None).tz_localize(tz)
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

def fetch_live_weather_forecast(latitude: float, longitude: float, tz: str) -> Optional[pd.DataFrame]:
    """
    Busca e formata dados de previsão do tempo, incluindo irradiância solar, da API Open-Meteo.

    Args:
        latitude (float): Latitude do local desejado.
        longitude (float): Longitude do local desejado.
        tz (str): Timezone no formato IANA (ex: 'America/Sao_Paulo').

    Returns:
        Optional[pd.DataFrame]: Um DataFrame com dados meteorológicos formatados para o pvlib
                                ou None em caso de falha na requisição.
    """
    logging.info(f"Buscando previsão do tempo da Open-Meteo para lat={latitude}, lon={longitude}")
    
    # URL base da API
    api_url = "https://api.open-meteo.com/v1/forecast"
    
    # Parâmetros da requisição, incluindo os campos de irradiância solar
    # shortwave_radiation = GHI, direct_normal_irradiance = DNI, diffuse_radiation = DHI
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,wind_speed_10m,shortwave_radiation,direct_normal_irradiance,diffuse_radiation",
        "timezone": tz,
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Lança uma exceção para status de erro (4xx ou 5xx)
        
        data = response.json()['hourly']
        df = pd.DataFrame(data)
        
        # Converte a coluna de tempo e a define como índice
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        
        # Renomeia as colunas para o padrão esperado pelo pvlib.ModelChain
        column_mapping = {
            "temperature_2m": "temp_air",
            "wind_speed_10m": "wind_speed",
            "shortwave_radiation": "ghi",
            "direct_normal_irradiance": "dni",
            "diffuse_radiation": "dhi",
        }
        df.rename(columns=column_mapping, inplace=True)
        
        logging.info("Previsão da Open-Meteo obtida e formatada com sucesso.")
        return df

    except requests.RequestException as e:
        logging.error(f"Falha ao conectar-se à API Open-Meteo: {e}", exc_info=True)
        return None
    except KeyError as e:
        logging.error(f"Resposta da API inesperada. Chave não encontrada: {e}", exc_info=True)
        return None
