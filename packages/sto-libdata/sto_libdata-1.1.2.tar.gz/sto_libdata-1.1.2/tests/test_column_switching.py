import numpy
import pandas as pd

from sto_libdata.dataframe_handling.normalization import NormalizationHandler
from sto_libdata.dataframe_handling.shared import NamedDataFrame
from tests.test_normalization_handling import assert_dataframe_dict_equality

def test_column_swiching():
    fac_table = pd.DataFrame({
        "ID": list(range(1, 6)),
        "VAL": list(numpy.random.random(5)),
        "CO_COUNTRY": ["ES", "DE", "ES", "FR", "FR"]
     })

    dim_country = pd.DataFrame({
        "ID": [1, 2, 3],
        "CO": ["ES", "DE", "FR"]
    })

    expected = pd.DataFrame({
        "ID": fac_table["ID"],
        "VAL": fac_table["VAL"],
        "ID_COUNTRY": [1, 2, 1, 3, 3]
    })

    expected_dict = {
        "FAC": expected,
        "DIM": dim_country
    }

    normhandler = NormalizationHandler(NamedDataFrame("FAC", fac_table), NamedDataFrame("DIM", dim_country))

    normhandler.swap_column_values(
        exchange_table="FAC",
        exchange_column="CO_COUNTRY",
        key_table="DIM",
        key_column="CO",
        new_column="ID"
    )

    normhandler.rename_column("FAC", "CO_COUNTRY", "ID_COUNTRY")

    output = normhandler.get_state()

    assert_dataframe_dict_equality(output, expected_dict)
