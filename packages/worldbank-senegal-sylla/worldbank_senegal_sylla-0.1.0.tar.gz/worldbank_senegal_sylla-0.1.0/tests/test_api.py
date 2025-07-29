
import unittest
import pandas as pd
from src.worldbank import get_export, get_import, get_pib

class TestWorldBankAPI(unittest.TestCase):
    
    def test_get_export(self):
        """Test de la fonction get_export"""
        df = get_export("SN", "2020", "2023")
        
        # Vérifications de base
        self.assertIsInstance(df, pd.DataFrame)
        if not df.empty:
            self.assertIn("pays", df.columns)
            self.assertIn("code", df.columns)
            self.assertIn("date", df.columns)
            self.assertIn("valeur", df.columns)
            self.assertEqual(df["code"].iloc[0], "SN")
    
    def test_get_import(self):
        """Test de la fonction get_import"""
        df = get_import("SN", "2020", "2023")
        
        self.assertIsInstance(df, pd.DataFrame)
        if not df.empty:
            self.assertIn("pays", df.columns)
            self.assertIn("code", df.columns)
            self.assertIn("date", df.columns)
            self.assertIn("valeur", df.columns)
    
    def test_get_pib(self):
        """Test de la fonction get_pib"""
        df = get_pib(["SN"], "2020", "2023")
        
        self.assertIsInstance(df, pd.DataFrame)
        if not df.empty:
            self.assertIn("code_pays", df.columns)
            self.assertEqual(df["code_pays"].iloc[0], "SN")
    
    def test_get_pib_multiple_countries(self):
        """Test avec plusieurs pays"""
        df = get_pib(["SN", "FR"], "2022", "2023")
        
        self.assertIsInstance(df, pd.DataFrame)
        if not df.empty:
            codes_pays = df["code_pays"].unique()
            self.assertIn("SN", codes_pays)

if __name__ == "__main__":
    unittest.main() 
