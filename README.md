# ☀️ SolarPV Analytics Simulator

## 1. Nome e Descrição do Projeto

O SolarPV Analytics Simulator é uma aplicação web interativa desenvolvida em Python para a simulação e análise de desempenho de sistemas fotovoltaicos. Utilizando o poder da biblioteca pvlib para os cálculos físicos e o Streamlit para uma interface de usuário intuitiva, a ferramenta permite que usuários configurem um sistema fotovoltaico virtual, obtenham dados meteorológicos de previsão em tempo real via API e visualizem a produção de energia esperada.

O objetivo principal do projeto é fornecer uma ferramenta acessível para engenheiros, estudantes e entusiastas de energia solar para estimar o desempenho de um sistema fotovoltaico em qualquer localização, facilitando a tomada de decisões e estudos de viabilidade.

## 2. Funcionalidades Principais

- **Interface Web Interativa:** Construída com Streamlit para uma experiência de usuário amigável, permitindo a configuração de parâmetros em tempo real sem a necessidade de conhecimento em programação.
- **Simulação Fotovoltaica Avançada:** Utiliza o pvlib, a biblioteca padrão da indústria, para modelar com precisão todos os componentes da cadeia de conversão de energia, desde a irradiância solar até a potência AC injetada na rede.
- **Dados Meteorológicos de Previsão:** Integra-se com a API Open-Meteo para buscar dados de previsão meteorológica para os próximos 7 dias, incluindo irradiância solar (GHI, DNI, DHI), temperatura e velocidade do vento.
- **Seleção Dinâmica de Componentes:** Permite que o usuário selecione módulos fotovoltaicos e inversores diretamente das bibliotecas do System Advisor Model (SAM), oferecendo um alto grau de personalização.
- **Visualização Detalhada de Resultados:** Apresenta os resultados da simulação através de métricas de resumo (Energia Total, Potência de Pico, Performance Ratio) e gráficos interativos (gerados com Plotly) para análise temporal da geração de energia e das condições de irradiância.
- **Exportação de Dados:** Permite o download dos resultados da simulação em formato .csv para análises externas e elaboração de relatórios.

## 3. Arquitetura do Sistema

O projeto é construído sobre uma arquitetura modular que separa as responsabilidades em diferentes camadas, garantindo manutenibilidade e escalabilidade.

### Descrição Textual

- **Camada de Interface (`app.py`):** Ponto de entrada da aplicação construída com Streamlit, responsável por renderizar a interface, coletar parâmetros e exibir resultados.
- **Camada de Simulação (`solar_pv_analytics/simulation.py`):** Contém a lógica para construir objetos do pvlib e executar o ModelChain para cálculos da simulação.
- **Camada de Dados (`solar_pv_analytics/data_ingestion/loaders.py`):** Abstrai as fontes de dados, conecta a API Open-Meteo, processa respostas e formata DataFrames compatíveis.
- **Módulos Utilitários (`solar_pv_analytics/utils/`):** Inclui validadores de configuração (`config_models.py`) e funções de suporte como logging.

## 4. Requisitos e Dependências

Requisitos: Python 3.8 ou superior.

Dependências listadas em `requirements.txt`:

```
pvlib==0.11.1
pandas==2.2.2
numpy==1.26.4
pydantic==2.8.2
typer==0.12.3
pyyaml==6.0.1
matplotlib==3.9.1
requests==2.32.3
pytest==8.3.2
streamlit==1.38.0
plotly==5.22.0
```

## 5. Instruções de Instalação e Execução

```
# Clonar o repositório
git clone https://github.com/seu-usuario/SolarPV-Analytics-Simulator.git
cd SolarPV-Analytics-Simulator

# Criar e ativar ambiente virtual
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar o app Streamlit
streamlit run app.py
```

Após executar o último comando, o navegador abrirá automaticamente a interface da aplicação.

## 6. Estrutura de Diretórios

```
SolarPV-Analytics-Simulator/
│
├── app.py
├── config/
│   └── config.yaml
├── data/
│   └── pvgis/
│       └── brasilia_pvgis.csv
├── solar_pv_analytics/
│   ├── __init__.py
│   ├── data_ingestion/
│   │   └── loaders.py
│   ├── pv_system/
│   │   └── simulation.py
│   └── utils/
│       ├── config_models.py
│       └── logging_setup.py
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## 7. Exemplos de Uso

- Abra a aplicação via Streamlit.
- Configure latitude, longitude, sistema fotovoltaico e período.
- Execute a simulação clicando no botão.
- Analise resultados e gráficos.
- Exporte dados para CSV se desejar.

## 8. Créditos

Desenvolvedoras:

- Amanda Mendonça
- Leticia Augusto