"""
Ponto de entrada principal e Interface de Linha de Comando (CLI) para o projeto.

Este script utiliza a biblioteca Typer para criar uma CLI robusta que orquestra
o pipeline de simulação: carregar configuração, obter dados, construir o sistema,
executar a simulação e gerar relatórios.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
import yaml
from pydantic import ValidationError
from pvlib.location import Location

from solar_pv_analytics.data_ingestion.loaders import load_pvgis_tmy_from_csv
from solar_pv_analytics.pv_system.simulation import build_pv_system, run_simulation
from solar_pv_analytics.utils.config_models import AppConfig
from solar_pv_analytics.utils.logging_setup import setup_logging
from solar_pv_analytics.visualization.reports import generate_report_figure

# Cria a aplicação CLI com Typer
app = typer.Typer(
    name="SolarPV-Analytics",
    help="Uma ferramenta CLI para executar simulações de sistemas fotovoltaicos com PVlib."
)

def load_and_validate_config(config_path: Path) -> Optional[AppConfig]:
    """Carrega o YAML e valida com o modelo Pydantic."""
    try:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return AppConfig(**config_dict)
    except FileNotFoundError:
        logging.error(f"Arquivo de configuração não encontrado em: {config_path}")
    except ValidationError as e:
        logging.error(f"Erro de validação no arquivo de configuração:\n{e}")
    except Exception:
        logging.error("Erro inesperado ao carregar a configuração.", exc_info=True)
    return None


@app.command()
def run(
    config_path: Path = typer.Option(
        "config/config.yaml",
        "--config",
        "-c",
        help="Caminho para o arquivo de configuração YAML."
    ),
    run_clearsky: bool = typer.Option(
        True, 
        help="Executar simulação usando o modelo clear-sky."
    ),
    run_pvgis: bool = typer.Option(
        True,
        help="Executar simulação usando dados do arquivo TMY do PVGIS."
    )
):
    """
    Executa o pipeline completo de simulação fotovoltaica.
    """
    setup_logging()
    logging.info("Iniciando o pipeline SolarPV-Analytics...")

    config = load_and_validate_config(config_path)
    if not config:
        raise typer.Exit(code=1)

    location = Location(
        latitude=config.location.latitude,
        longitude=config.location.longitude,
        tz=config.location.tz,
        altitude=config.location.altitude,
        name=config.location.name
    )
    pv_system = build_pv_system(config.pv_system)

    if run_pvgis:
        logging.info("\n" + "="*50 + "\nCENÁRIO: SIMULAÇÃO COM DADOS TMY DO PVGIS\n" + "="*50)
        weather_pvgis = load_pvgis_tmy_from_csv(
            str(config.data_sources.pvgis_tmy_path),
            config.location.tz
        )
        if weather_pvgis is not None:
            mc_pvgis = run_simulation(pv_system, location, weather_pvgis)
            fig = generate_report_figure(mc_pvgis, "TMY PVGIS")
            fig.show()

    if run_clearsky:
        logging.info("\n" + "="*50 + "\nCENÁRIO: SIMULAÇÃO COM DADOS CLEAR-SKY\n" + "="*50)
        times = pd.date_range(
            start=config.simulation_times.clearsky_start,
            end=config.simulation_times.clearsky_end,
            freq=config.simulation_times.frequency,
            tz=location.tz
        )
        weather_clearsky = location.get_clearsky(times)
        mc_clearsky = run_simulation(pv_system, location, weather_clearsky)
        fig = generate_report_figure(mc_clearsky, "Clear-Sky Model")
        fig.show()
    
    # Bloqueia a execução para que as janelas dos gráficos possam ser vistas
    import matplotlib.pyplot as plt
    if run_pvgis or run_clearsky:
        logging.info("Feche as janelas dos gráficos para finalizar o programa.")
        plt.show()

    logging.info("Pipeline SolarPV-Analytics concluído.")


if __name__ == "__main__":
    app()