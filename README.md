
# SolarPV Analytics

Este projeto é uma ferramenta de linha de comando (CLI) para executar simulações de performance de sistemas fotovoltaicos utilizando a biblioteca `pvlib` em Python. A arquitetura é modular, configurável e extensível.

## Funcionalidades

- **Configuração Centralizada**: Todos os parâmetros (localização, sistema PV, caminhos de dados) são gerenciados em um único arquivo `config/config.yaml`.  
- **Validação de Dados**: Utiliza `Pydantic` para garantir que o arquivo de configuração seja válido antes da execução, evitando erros.  
- **Ingestão de Dados Flexível**: Suporta o carregamento de dados meteorológicos de arquivos locais (formato TMY do PVGIS).  
- **Simulação com `pvlib.ModelChain`**: Orquestra a simulação completa, desde o cálculo da irradiância no plano do painel até a conversão de energia AC pelo inversor.  
- **Geração de Relatórios**: Cria visualizações claras da irradiância de entrada e da potência AC gerada.  
- **CLI Robusta**: Utiliza `Typer` para fornecer uma interface de linha de comando fácil de usar.  

## Estrutura do Projeto

SolarPV_Analytics/
├── config/
│   └── config.yaml
├── data/
│   └── pvgis/
│       └── brasilia_pvgis.csv
├── solar_pv_analytics/
│   ├── utils/
│   ├── data_ingestion/
│   ├── pv_system/
│   └── visualization/
├── tests/
├── main.py
├── requirements.txt
└── README.md

## Instalação

1. **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd SolarPV_Analytics
    ```

2. **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate    # No Windows: venv\Scripts\activate
    ```

3. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Como Usar

A ferramenta é executada através do `main.py` pela linha de comando.

### Comando Básico

Execute a simulação usando o arquivo de configuração padrão (`config/config.yaml`):

```bash
python main.py
```

Isso irá executar os dois cenários padrão: simulação com dados TMY do PVGIS e com dados de céu claro (clear-sky).

### Opções da CLI

- **Especificar um arquivo de configuração diferente:**
    ```bash
    python main.py --config /caminho/para/seu/config.yaml
    ```

- **Executar apenas um dos cenários:**
    ```bash
    # Apenas PVGIS
    python main.py --no-run-clearsky

    # Apenas Clear-Sky
    python main.py --no-run-pvgis
    ```

- **Ver a ajuda:**
    ```bash
    python main.py --help
    ```

## Executando os Testes

Para garantir que os componentes principais estão funcionando corretamente, execute os testes unitários com pytest:

```bash
pytest
```
