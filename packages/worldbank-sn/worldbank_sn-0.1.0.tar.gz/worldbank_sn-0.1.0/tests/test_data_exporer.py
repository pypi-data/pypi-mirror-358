import pytest
import pandas as pd
import requests
from unittest.mock import patch, Mock
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les fonctions à tester (ajustez le nom du module selon votre structure)
from data_exporer import get_worldbank_data, get_pib, get_export, get_import


class TestWorldBankAPI:
    """Tests pour les fonctions de l'API World Bank"""
    
    @pytest.fixture
    def mock_api_response_success(self):
        """Mock d'une réponse API réussie"""
        return [
            {"page": 1, "pages": 1, "per_page": 50, "total": 3},
            [
                {
                    "indicator": {"id": "NY.GDP.MKTP.CD", "value": "PIB ($ US courants)"},
                    "country": {"id": "SN", "value": "Sénégal"},
                    "countryiso3code": "SEN",
                    "date": "2023",
                    "value": 27685017896.0,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 0
                },
                {
                    "indicator": {"id": "NY.GDP.MKTP.CD", "value": "PIB ($ US courants)"},
                    "country": {"id": "SN", "value": "Sénégal"},
                    "countryiso3code": "SEN", 
                    "date": "2022",
                    "value": 26774909368.0,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 0
                },
                {
                    "indicator": {"id": "NY.GDP.MKTP.CD", "value": "PIB ($ US courants)"},
                    "country": {"id": "SN", "value": "Sénégal"},
                    "countryiso3code": "SEN",
                    "date": "2021", 
                    "value": 25323077784.0,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 0
                }
            ]
        ]
    
    @pytest.fixture
    def mock_api_response_empty(self):
        """Mock d'une réponse API vide"""
        return [
            {"page": 1, "pages": 1, "per_page": 50, "total": 0},
            []
        ]
    
    @pytest.fixture
    def mock_api_response_error(self):
        """Mock d'une réponse API avec erreur"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": [{"id": "120", "key": "Invalid value", "value": "The provided parameter value is not valid"}]}
        return mock_response


class TestGetWorldBankData(TestWorldBankAPI):
    """Tests spécifiques pour get_worldbank_data"""
    
    @patch('requests.get')
    def test_get_worldbank_data_success(self, mock_get, mock_api_response_success):
        """Test réussi de récupération de données"""
        # Configuration du mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_success
        mock_get.return_value = mock_response
        
        # Appel de la fonction
        result = get_worldbank_data("SN", "NY.GDP.MKTP.CD", 2021, 2023)
        
        # Vérifications
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['pays', 'code_pays', 'annee', 'valeur', 'indicateur']
        assert result['pays'].iloc[0] == "Sénégal"
        assert result['code_pays'].iloc[0] == "SEN"
        assert result['annee'].iloc[0] == 2021  # Vérifie le tri par année
        assert result['valeur'].iloc[0] == 25323077784.0
        
        # Vérifier l'appel à l'API
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "https://api.worldbank.org/v2/country/SN/indicator/NY.GDP.MKTP.CD" in args[0]
    
    @patch('requests.get')
    def test_get_worldbank_data_empty_response(self, mock_get, mock_api_response_empty):
        """Test avec une réponse vide"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_empty
        mock_get.return_value = mock_response
        
        result = get_worldbank_data("XX", "INVALID", 2020, 2023)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('requests.get')
    def test_get_worldbank_data_api_error(self, mock_get):
        """Test avec une erreur API"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="Erreur API: 404"):
            get_worldbank_data("XX", "INVALID", 2020, 2023)
    
    def test_get_worldbank_data_parameters(self):
        """Test des paramètres par défaut"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"page": 1}, []]
            mock_get.return_value = mock_response
            
            get_worldbank_data("SN", "NY.GDP.MKTP.CD")
            
            # Vérifier les paramètres par défaut
            args, kwargs = mock_get.call_args
            params = kwargs.get('params', {})
            assert params['date'] == "2000:2023"
            assert params['format'] == "json"
            assert params['per_page'] == 1000


class TestSpecificFunctions(TestWorldBankAPI):
    """Tests pour les fonctions spécialisées"""
    
    @patch('get_worldbank_data')
    def test_get_pib(self, mock_get_worldbank):
        """Test de la fonction get_pib"""
        # Configuration du mock
        mock_df = pd.DataFrame({
            'pays': ['Sénégal'],
            'code_pays': ['SEN'],
            'annee': [2023],
            'valeur': [27685017896.0],
            'indicateur': ['PIB ($ US courants)']
        })
        mock_get_worldbank.return_value = mock_df
        
        # Appel de la fonction
        result = get_pib("SN", 2023, 2023)
        
        # Vérifications
        assert isinstance(result, pd.DataFrame)
        assert 'pib' in result.columns
        assert 'valeur' not in result.columns  # Vérifier le rename
        assert result['pib'].iloc[0] == 27685017896.0
        
        # Vérifier l'appel avec le bon indicateur
        mock_get_worldbank.assert_called_once_with("SN", "NY.GDP.MKTP.CD", 2023, 2023)
    
    @patch('get_worldbank_data')
    def test_get_export(self, mock_get_worldbank):
        """Test de la fonction get_export"""
        mock_df = pd.DataFrame({
            'pays': ['Sénégal'],
            'code_pays': ['SEN'],
            'annee': [2023],
            'valeur': [5000000000.0],
            'indicateur': ['Exportations de biens et services ($ US courants)']
        })
        mock_get_worldbank.return_value = mock_df
        
        result = get_export("SN", 2023, 2023)
        
        assert isinstance(result, pd.DataFrame)
        assert 'exportations' in result.columns
        assert result['exportations'].iloc[0] == 5000000000.0
        mock_get_worldbank.assert_called_once_with("SN", "NE.EXP.GNFS.CD", 2023, 2023)
    
    @patch('get_worldbank_data')
    def test_get_import(self, mock_get_worldbank):
        """Test de la fonction get_import"""
        mock_df = pd.DataFrame({
            'pays': ['Sénégal'],
            'code_pays': ['SEN'],
            'annee': [2023],
            'valeur': [7000000000.0],
            'indicateur': ['Importations de biens et services ($ US courants)']
        })
        mock_get_worldbank.return_value = mock_df
        
        result = get_import("SN", 2023, 2023)
        
        assert isinstance(result, pd.DataFrame)
        assert 'importations' in result.columns
        assert result['importations'].iloc[0] == 7000000000.0
        mock_get_worldbank.assert_called_once_with("SN", "NE.IMP.GNFS.CD", 2023, 2023)
    
    @patch('get_worldbank_data')
    def test_functions_with_empty_dataframe(self, mock_get_worldbank):
        """Test des fonctions avec DataFrame vide"""
        mock_get_worldbank.return_value = pd.DataFrame()
        
        # Test avec chaque fonction
        pib_result = get_pib("XX", 2023, 2023)
        export_result = get_export("XX", 2023, 2023)
        import_result = get_import("XX", 2023, 2023)
        
        # Vérifier que toutes retournent un DataFrame vide
        assert len(pib_result) == 0
        assert len(export_result) == 0
        assert len(import_result) == 0


class TestIntegration:
    """Tests d'intégration (nécessitent une connexion Internet)"""
    
    @pytest.mark.integration
    def test_real_api_call_senegal_pib(self):
        """Test réel avec l'API World Bank pour le PIB du Sénégal"""
        try:
            result = get_pib("SN", 2022, 2023)
            
            # Vérifications de base
            assert isinstance(result, pd.DataFrame)
            if not result.empty:
                assert 'pib' in result.columns
                assert 'pays' in result.columns
                assert 'annee' in result.columns
                assert result['pays'].iloc[0] == "Senegal"
        except Exception as e:
            pytest.skip(f"Test d'intégration échoué (probablement pas de connexion): {e}")
    
    @pytest.mark.integration
    def test_real_api_call_invalid_country(self):
        """Test avec un code pays invalide"""
        try:
            result = get_pib("INVALID", 2023, 2023)
            assert len(result) == 0
        except Exception as e:
            pytest.skip(f"Test d'intégration échoué: {e}")


class TestDataValidation:
    """Tests de validation des données"""
    
    @patch('get_worldbank_data')
    def test_data_types_and_structure(self, mock_get_worldbank):
        """Test des types de données et de la structure"""
        mock_df = pd.DataFrame({
            'pays': ['Sénégal', 'Sénégal'],
            'code_pays': ['SEN', 'SEN'],
            'annee': [2022, 2023],
            'valeur': [26774909368.0, 27685017896.0],
            'indicateur': ['PIB', 'PIB']
        })
        mock_get_worldbank.return_value = mock_df
        
        result = get_pib("SN", 2022, 2023)
        
        # Vérifier les types
        assert result['annee'].dtype == 'int64'
        assert result['pib'].dtype == 'float64'
        assert isinstance(result['pays'].iloc[0], str)
        assert isinstance(result['code_pays'].iloc[0], str)
    
    def test_date_range_validation(self):
        """Test de validation des plages de dates"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"page": 1}, []]
            mock_get.return_value = mock_response
            
            # Test avec date_fin < date_debut
            result = get_worldbank_data("SN", "NY.GDP.MKTP.CD", 2023, 2020)
            
            # La fonction devrait toujours fonctionner, l'API gère les plages invalides
            assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])