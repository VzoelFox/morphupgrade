import pytest
from transisi.common.result import Result, Sukses, Gagal

def test_result_backward_compatibility():
    # Test Sukses
    res_sukses = Result.sukses("Data Penting")
    assert res_sukses['sukses'] == True
    assert res_sukses['data'] == "Data Penting"
    assert res_sukses['error'] is None
    assert res_sukses.get('data') == "Data Penting"
    assert 'sukses' in res_sukses

    # Test Gagal
    res_gagal = Result.gagal("Error Fatal")
    assert res_gagal['sukses'] == False
    assert res_gagal['data'] is None
    assert res_gagal['error'] == "Error Fatal"
    assert res_gagal.get('error') == "Error Fatal"

    # Test Invalid Key
    with pytest.raises(KeyError):
        _ = res_sukses['invalid_key']

    assert res_sukses.get('invalid', 'default') == 'default'
