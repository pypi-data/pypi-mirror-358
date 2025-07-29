from data_explorer.getter import get_export, get_import, get_pib

def test_export_sn():
    df = get_export("SN")
    assert not df.empty
    assert "valeur" in df.columns

def test_import_sn():
    df = get_import("SN")
    assert not df.empty
    assert "valeur" in df.columns

def test_pib_multi():
    df = get_pib(["SN", "FR"])
    assert not df.empty
    assert "code_pays" in df.columns
