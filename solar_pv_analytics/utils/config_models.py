"""
Módulo contendo os modelos Pydantic para validação do arquivo config.yaml.

A utilização de Pydantic garante que a configuração carregada tenha a estrutura
e os tipos de dados corretos antes que a aplicação comece a usá-la, prevenindo
erros em tempo de execução.
"""

from pydantic import BaseModel, FilePath, HttpUrl

class LocationConfig(BaseModel):
    """Valida a seção 'location' do config."""
    latitude: float
    longitude: float
    altitude: int
    tz: str
    name: str

class DataSourcesConfig(BaseModel):
    """Valida a seção 'data_sources' do config."""
    pvgis_tmy_path: FilePath
    
    class OpenMeteoAPIConfig(BaseModel):
        url: HttpUrl
    
    open_meteo_api: OpenMeteoAPIConfig

class PVSystemConfig(BaseModel):
    """Valida a seção 'pv_system' do config."""
    surface_tilt: int
    surface_azimuth: int
    modules_per_string: int
    strings_per_inverter: int
    module_name: str
    inverter_name: str
    temperature_model_type: str
    rack_type: str

class SimulationTimesConfig(BaseModel):
    """Valida a seção 'simulation_times' do config."""
    clearsky_start: str
    clearsky_end: str
    frequency: str

class AppConfig(BaseModel):
    """Modelo Pydantic raiz que engloba toda a configuração."""
    location: LocationConfig
    data_sources: DataSourcesConfig
    pv_system: PVSystemConfig
    simulation_times: SimulationTimesConfig