import pandas as pd
import pytest
from solar_pv_analytics.data_ingestion.loaders import load_pvgis_tmy_from_csv


@pytest.fixture
def mock_pvgis_csv_data() -> str:
    """Cria um CSV em memória simulando o formato de saída do PVGIS."""
    header = "\n" * 17  # Simula as 17 linhas de cabeçalho
    data = (
        "time(UTC),T2m,G(h),Gb(n),Gd(h),WS10m\n"
        "20250101:0000,20.0,0,0,0,1.5\n"
        "20250101:0100,19.5,0,0,0,1.4\n"
        "20250101:1200,28.0,800,700,100,2.0\n"
    )
    return header + data


def test_load_pvgis_tmy_from_csv_success(mock_pvgis_csv_data, tmp_path):
    """
    Testa o carregamento bem-sucedido de um arquivo CSV do PVGIS.
    Verifica a renomeação de colunas e a formatação do índice.
    """
    p = tmp_path / "mock_pvgis.csv"
    p.write_text(mock_pvgis_csv_data)
    
    df = load_pvgis_tmy_from_csv(str(p), tz="America/Sao_Paulo")

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    
    expected_columns = ["temp_air", "ghi", "dni", "dhi", "wind_speed"]
    assert all(col in df.columns for col in expected_columns)
    
    assert isinstance(df.index, pd.DatetimeIndex)
    assert str(df.index.tz) == "America/Sao_Paulo"
    assert df.shape[0] == 3


def test_load_pvgis_tmy_from_csv_file_not_found():
    """Testa o comportamento da função quando o arquivo não existe."""
    df = load_pvgis_tmy_from_csv("caminho/inexistente.csv", tz="America/Sao_Paulo")
    assert df is None
