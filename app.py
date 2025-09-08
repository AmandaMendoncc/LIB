import sys
import os
import pandas as pd
import plotly.express as px
import pvlib
import streamlit as st
from pvlib.location import Location
from pvlib.modelchain import ModelChain
import logging

# Configuração básica de logging para depuração no terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adiciona o diretório raiz ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from solar_pv_analytics.data_ingestion.loaders import fetch_live_weather_forecast
from solar_pv_analytics.pv_system.simulation import build_pv_system
from solar_pv_analytics.utils.config_models import PVSystemConfig

def validate_weather_data(df: pd.DataFrame) -> (pd.DataFrame, list):
    required_columns = ['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']
    warnings = []
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return None, [f"Erro Crítico: As seguintes colunas obrigatórias estão faltando nos dados da API: {', '.join(missing_cols)}"]
    
    if df[required_columns].isnull().values.any():
        nan_counts = df[required_columns].isnull().sum()
        warnings.append(f"Aviso: Valores nulos encontrados e tratados. Contagem por coluna: {nan_counts[nan_counts > 0].to_dict()}")
        
        df[required_columns] = df[required_columns].interpolate(method='time')
        df[required_columns] = df[required_columns].fillna(0)
    
    df[required_columns] = df[required_columns].apply(pd.to_numeric, errors='coerce')
    return df, warnings

@st.cache_resource
def get_sam_data():
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
    return sandia_modules, cec_inverters

sandia_modules, cec_inverters = get_sam_data()

# Inicialização segura das chaves do session_state
if 'simulation_results' not in st.session_state:
    st.session_state['simulation_results'] = None
if 'weather_results' not in st.session_state:
    st.session_state['weather_results'] = None
if 'date_range' not in st.session_state:
    st.session_state['date_range'] = None

# --- INTERFACE DO USUÁRIO (SIDEBAR) ---

st.sidebar.header('Parâmetros da Simulação')

st.sidebar.subheader('1. Localização')
lat = st.sidebar.number_input('Latitude', value=-15.79, format="%.4f")
lon = st.sidebar.number_input('Longitude', value=-47.91, format="%.4f")
tz = 'America/Sao_Paulo'

st.sidebar.subheader('2. Configuração do Sistema Fotovoltaico')
surface_tilt = st.sidebar.slider('Inclinação (graus)', 0, 90, 20)
surface_azimuth = st.sidebar.slider('Orientação (Azimute, 180°=Norte)', 0, 360, 180)

st.sidebar.subheader('3. Componentes')
module_list = list(sandia_modules.keys())
default_module_idx = module_list.index('Canadian_Solar_CS6K_275M') if 'Canadian_Solar_CS6K_275M' in module_list else 0
selected_module_name = st.sidebar.selectbox('Módulo Fotovoltaico', module_list, index=default_module_idx)

inverter_list = list(cec_inverters.keys())
default_inverter_idx = inverter_list.index('SMA_America__SB5000TL_US_22__240V_') if 'SMA_America__SB5000TL_US_22__240V_' in inverter_list else 0
selected_inverter_name = st.sidebar.selectbox('Inversor', inverter_list, index=default_inverter_idx)

st.sidebar.info("A simulação será executada para a previsão dos próximos 7 dias a partir da data atual.")
run_button = st.sidebar.button('Executar Simulação de Previsão', type='primary')

# --- LÓGICA PRINCIPAL E VISUALIZAÇÃO ---

st.title('☀️ Simulador de Previsão de Energia Solar')
st.markdown("""
Bem-vindo ao simulador de sistemas fotovoltaicos. Utilize o painel à esquerda para configurar os parâmetros
de localização e do sistema. A simulação utilizará **dados de previsão em tempo real** da API Open-Meteo.
""")

if run_button:
    with st.spinner('Buscando e validando dados de previsão...'):
        raw_weather_data = fetch_live_weather_forecast(lat, lon, tz)

        if raw_weather_data is None:
            st.error("Não foi possível obter os dados meteorológicos da API.")
            st.stop()
        
        weather_data, warnings = validate_weather_data(raw_weather_data)
        if weather_data is None:
            st.error(warnings[0])
            st.stop()
        for warning in warnings:
            st.warning(warning)
                
    with st.spinner('Executando simulação do sistema fotovoltaico...'):
        try:
            location = Location(latitude=lat, longitude=lon, tz=tz, name="Local Simulado")
            system_config = PVSystemConfig(
                surface_tilt=surface_tilt, surface_azimuth=surface_azimuth,
                module_name=selected_module_name, inverter_name=selected_inverter_name,
                modules_per_string=10, strings_per_inverter=1,
                temperature_model_type='sapm', rack_type='open_rack_glass_glass'
            )
            pv_system = build_pv_system(system_config)
            mc = ModelChain(pv_system, location)
            mc.run_model(weather_data)
            
            if hasattr(mc, 'results') and mc.results is not None:
                st.session_state['simulation_results'] = mc.results
                st.session_state['weather_results'] = mc.weather if hasattr(mc, 'weather') else weather_data
            else:
                st.error("A simulação foi executada, mas não gerou resultados.")
                st.stop()
        except Exception as e:
            st.error("Ocorreu um erro inesperado durante a simulação do PVlib.")
            st.exception(e)
            st.stop()

# Exibição dos resultados na interface:
if st.session_state['simulation_results'] is not None:
    results = st.session_state['simulation_results']
    weather_results = st.session_state['weather_results']

    st.success('Simulação de previsão concluída com sucesso!')
    st.header('Resumo do Desempenho Previsto')

    total_energy_kwh = results.ac.sum() / 1000
    peak_power_kw = results.ac.max() / 1000

    col1, col2, col3 = st.columns(3)
    col1.metric("Energia Total Prevista", f"{total_energy_kwh:.2f} kWh")
    col2.metric("Potência de Pico Prevista", f"{peak_power_kw:.2f} kW")
    
    # Se possível, calcula o PR com irradiância no plano do painel do resultado
    if hasattr(results, 'total_irrad') and 'poa_global' in results.total_irrad.columns:
        poa_total = results.total_irrad['poa_global'].sum() / 1000
        nominal_power_dc = sandia_modules[selected_module_name]['Impo'] * sandia_modules[selected_module_name]['Vmpo'] * 10
        pr = (total_energy_kwh / (poa_total * nominal_power_dc / 1000)) * 100 if poa_total > 0 else 0
        col3.metric("Performance Ratio (PR)", f"{pr:.1f} %")
    else:
        col3.metric("Performance Ratio (PR)", "N/A")

    st.header('Análise Gráfica da Previsão')
    tab1, tab2 = st.tabs(["⚡ Geração de Energia", "☀️ Dados de Irradiância (Entrada)"])
    with tab1:
        fig_power = px.line(results.ac, title='Previsão de Geração de Energia AC')
        fig_power.update_layout(xaxis_title='Data e Hora', yaxis_title='Potência (W)')
        st.plotly_chart(fig_power, use_container_width=True)
    with tab2:
        fig_irradiance = px.line(weather_results, y=['ghi', 'dni', 'dhi'], title='Previsão dos Componentes da Irradiância Solar (Entrada)')
        fig_irradiance.update_layout(xaxis_title='Data e Hora', yaxis_title='Irradiância (W/m²)')
        st.plotly_chart(fig_irradiance, use_container_width=True)

    # Exportação CSV (exemplo básico)
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=True).encode('utf-8')

    csv_data = convert_df_to_csv(results.ac.to_frame('Potencia_AC_W'))

    st.download_button(
        label="📥 Exportar Resultados para CSV",
        data=csv_data,
        file_name=f"simulacao_pv_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
