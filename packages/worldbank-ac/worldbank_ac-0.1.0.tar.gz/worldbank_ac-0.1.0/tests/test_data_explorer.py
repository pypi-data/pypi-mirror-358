from .getter import get_importations, get_exportations, get_pib
import pandas as pd


def test_get_importations():
    df = get_import("FRA", "2010", "2020")
    assert isinstance(df, pd.DataFrame), "La fonction doit retourner un DataFrame"
    assert not df.empty, "Le DataFrame ne doit pas être vide"
    assert 'country_name' in df.columns, "Le DataFrame doit contenir la colonne 'country_name'"
    assert 'value' in df.columns, "Le DataFrame doit contenir la colonne 'value'"

def test_get_exportations():
    df = get_export("FRA", "2010", "2020")
    assert isinstance(df, pd.DataFrame), "La fonction doit retourner un DataFrame"
    assert not df.empty, "Le DataFrame ne doit pas être vide"
    assert 'country_name' in df.columns, "Le DataFrame doit contenir la colonne 'country_name'"
    assert 'value' in df.columns, "Le DataFrame doit contenir la colonne 'value'"

def test_get_pib():
    df = get_pib("FRA", "2010", "2020")
    assert isinstance(df, pd.DataFrame), "La fonction doit retourner un DataFrame"
    assert not df.empty, "Le DataFrame ne doit pas être vide"
    assert 'country_name' in df.columns, "Le DataFrame doit contenir la colonne 'country_name'"
    assert 'value' in df.columns, "Le DataFrame doit contenir la colonne 'value'"

def main():
    print("Test des importations pour la France de 2010 à 2020 :")
    test_get_importations()
    print("Test des exportations pour la France de 2010 à 2020 :")
    test_get_exportations()
    print("Test du PIB pour la France de 2010 à 2020 :")
    test_get_pib()
    print("Tous les tests ont réussi !")

if __name__ == "__main__":
    main()