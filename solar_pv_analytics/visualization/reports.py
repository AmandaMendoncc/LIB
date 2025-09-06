"""Módulo para criação de visualizações e relatórios dos resultados da simulação."""

import logging
from matplotlib import pyplot as plt
from pvlib.modelchain import ModelChain

def generate_report_figure(modelchain: ModelChain, source_name: str) -> plt.Figure:
    """
    Gera uma figura Matplotlib com os resultados da simulação.

    Args:
        modelchain (ModelChain): O objeto ModelChain com os resultados da simulação.
        source_name (str): O nome da fonte de dados (ex: 'TMY PVGIS', 'Clear-Sky').

    Returns:
        plt.Figure: A figura gerada contendo os gráficos de irradiância e potência.
    """
    logging.info(f"Gerando relatório gráfico para a fonte de dados: {source_name}")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)
    fig.suptitle(f"Resultados da Simulação - Fonte: {source_name}", fontsize=16)

    # Gráfico 1: Irradiância
    irradiance_cols = ['ghi', 'dni', 'dhi']
    # Checa quais colunas de irradiância estão disponíveis nos dados de entrada
    available_cols = [col for col in irradiance_cols if col in modelchain.results.weather.columns]
    if available_cols:
        modelchain.results.weather[available_cols].plot(ax=ax1, title="Irradiância de Entrada")
    ax1.set_ylabel("Irradiância (W/m^2)")
    ax1.grid(True)
    ax1.legend()

    # Gráfico 2: Geração de Energia AC
    modelchain.results.ac.plot(ax=ax2, title="Geração de Energia AC")
    ax2.set_ylabel("Potência (W)")
    ax2.grid(True)
    
    total_energy_kwh = modelchain.results.ac.sum() / 1000
    logging.info(f"Energia Total Gerada (AC) para '{source_name}': {total_energy_kwh:.2f} kWh")
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig