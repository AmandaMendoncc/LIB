"""Módulo para construção do sistema PV e execução de simulações com pvlib."""

import logging
import pandas as pd
import pvlib
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

from solar_pv_analytics.utils.config_models import PVSystemConfig

def build_pv_system(system_config: PVSystemConfig) -> PVSystem:
    """
    Constrói um objeto pvlib.PVSystem a partir dos parâmetros de configuração.

    Args:
        system_config (PVSystemConfig): Objeto Pydantic com os parâmetros do sistema.

    Returns:
        PVSystem: Objeto PVSystem configurado.
    """
    logging.info("Construindo o objeto PVSystem...")
    
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')

    module = sandia_modules[system_config.module_name]
    inverter = cec_inverters[system_config.inverter_name]
    
    temp_params = TEMPERATURE_MODEL_PARAMETERS[system_config.temperature_model_type][system_config.rack_type]

    system = PVSystem(
        surface_tilt=system_config.surface_tilt,
        surface_azimuth=system_config.surface_azimuth,
        module_parameters=module,
        inverter_parameters=inverter,
        temperature_model_parameters=temp_params,
        modules_per_string=system_config.modules_per_string,
        strings_per_inverter=system_config.strings_per_inverter,
    )
    logging.info("PVSystem construído com sucesso.")
    return system

def run_simulation(system: PVSystem, location: Location, weather_data: pd.DataFrame) -> ModelChain:
    """
    Executa o pvlib.ModelChain com um sistema, localização e dados meteorológicos.

    Args:
        system (PVSystem): O sistema fotovoltaico a ser simulado.
        location (Location): A localização da simulação.
        weather_data (pd.DataFrame): DataFrame contendo os dados meteorológicos
                                     com as colunas requeridas pelo ModelChain.

    Returns:
        ModelChain: O objeto ModelChain após a execução do modelo, com os resultados.
    """
    logging.info(f"Iniciando simulação com {len(weather_data)} registros de tempo.")
    
    mc = ModelChain(system, location)
    mc.run_model(weather_data)
    
    logging.info("Simulação concluída.")
    return mc