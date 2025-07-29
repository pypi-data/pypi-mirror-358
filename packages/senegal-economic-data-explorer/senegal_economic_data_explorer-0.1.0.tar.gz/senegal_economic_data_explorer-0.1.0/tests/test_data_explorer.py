"""
Tests unitaires pour le package data_explorer
"""

import unittest
import pandas as pd
from unittest.mock import patch, Mock
from data_explorer import get_export, get_import, get_pib


class TestDataExplorer(unittest.TestCase):
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.mock_response = {
            "metadata": {},
            "data": [
                {
                    "country": {"id": "SN", "value": "Senegal"},
                    "date": "2023",
                    "value": 1000000000
                },
                {
                    "country": {"id": "SN", "value": "Senegal"},
                    "date": "2022",
                    "value": 950000000
                }
            ]
        }
    
    @patch('data_explorer.getter.requests.get')
    def test_get_export(self, mock_get):
        """Test de la fonction get_export"""
        # Configuration du mock
        mock_response = Mock()
        mock_response.json.return_value = [
            {"metadata": "info"},
            [
                {
                    "country": {"id": "SN", "value": "Senegal"},
                    "date": "2023",
                    "value": 5000000000
                }
            ]
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Appel de la fonction
        df = get_export("SN", 2023, 2023)
        
        # Vérifications
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('exportations_usd', df.columns)
        self.assertIn('annee', df.columns)
        self.assertIn('code_pays', df.columns)
        self.assertEqual(df['code_pays'].iloc[0], 'SN')
    
    @patch('data_explorer.getter.requests.get')
    def test_get_import(self, mock_get):
        """Test de la fonction get_import"""
        # Configuration du mock
        mock_response = Mock()
        mock_response.json.return_value = [
            {"metadata": "info"},
            [
                {
                    "country": {"id": "SN", "value": "Senegal"},
                    "date": "2023",
                    "value": 6000000000
                }
            ]
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Appel de la fonction
        df = get_import("SN", 2023, 2023)
        
        # Vérifications
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('importations_usd', df.columns)
        self.assertIn('annee', df.columns)
        self.assertEqual(len(df), 1)
    
    @patch('data_explorer.getter.requests.get')
    def test_get_pib_single_country(self, mock_get):
        """Test de la fonction get_pib avec un seul pays"""
        # Configuration du mock
        mock_response = Mock()
        mock_response.json.return_value = [
            {"metadata": "info"},
            [
                {
                    "country": {"id": "SN", "value": "Senegal"},
                    "date": "2023",
                    "value": 27000000000
                }
            ]
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Appel de la fonction
        df = get_pib("SN", 2023, 2023)
        
        # Vérifications
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('pib_usd', df.columns)
        self.assertEqual(df['code_pays'].iloc[0], 'SN')
    
    @patch('data_explorer.getter.requests.get')
    def test_get_pib_multiple_countries(self, mock_get):
        """Test de la fonction get_pib avec plusieurs pays"""
        # Configuration du mock pour plusieurs appels
        responses = [
            [
                {"metadata": "info"},
                [
                    {
                        "country": {"id": "SN", "value": "Senegal"},
                        "date": "2023",
                        "value": 27000000000
                    }
                ]
            ],
            [
                {"metadata": "info"},
                [
                    {
                        "country": {"id": "FR", "value": "France"},
                        "date": "2023",
                        "value": 2900000000000
                    }
                ]
            ]
        ]
        
        mock_response = Mock()
        mock_response.json.side_effect = responses
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Appel de la fonction
        df = get_pib(["SN", "FR"], 2023, 2023)
        
        # Vérifications
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('SN', df['code_pays'].values)
        self.assertIn('FR', df['code_pays'].values)
    
    @patch('data_explorer.getter.requests.get')
    def test_empty_response(self, mock_get):
        """Test avec une réponse vide de l'API"""
        # Configuration du mock avec réponse vide
        mock_response = Mock()
        mock_response.json.return_value = [{"metadata": "info"}, []]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Appel de la fonction
        df = get_export("XX", 2023, 2023)
        
        # Vérifications
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
    
    @patch('data_explorer.getter.requests.get')
    def test_api_error(self, mock_get):
        """Test de gestion d'erreur API"""
        # Configuration du mock pour lever une exception
        mock_get.side_effect = Exception("API Error")
        
        # Appel de la fonction
        df = get_export("SN", 2023, 2023)
        
        # Vérifications
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)


if __name__ == '__main__':
    unittest.main()
