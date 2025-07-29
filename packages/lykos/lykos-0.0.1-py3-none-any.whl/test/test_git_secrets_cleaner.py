import pytest
import json
import os
import sys
from unittest.mock import patch, mock_open, MagicMock, call
import subprocess

GitSecretsCleaner = None
main = None

from lykos.git_secrets_cleaner import GitSecretsCleaner, main

class TestGitSecretsCleanerInit:
    def test_init_default(self):
        cleaner = GitSecretsCleaner()
        assert cleaner.dry_run is False
        assert cleaner.temp_dir is None
    
    def test_init_dry_run(self):
        cleaner = GitSecretsCleaner(dry_run=True)
        assert cleaner.dry_run is True
        assert cleaner.temp_dir is None

class TestCheckRepoClean:
    @patch('subprocess.run')
    def test_repo_clean_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        cleaner = GitSecretsCleaner()
        result = cleaner.check_repo_clean()
        
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "status", "--porcelain"], 
            capture_output=True, text=True, timeout=10
        )
    
    @patch('subprocess.run')
    def test_repo_has_changes(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = " M modified_file.py\n"
        mock_run.return_value = mock_result
        
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.check_repo_clean()
        
        assert result is False
        mock_print.assert_called_with("Repository has uncommitted changes. Please commit or stash first.")


class TestFilterSecretsByConfidence:    
    def setup_method(self):
        self.secrets = [
            {'token': 'high_secret', 'confidence': {'level': 'HIGH'}},
            {'token': 'medium_secret', 'confidence': {'level': 'MEDIUM'}},
            {'token': 'low_secret', 'confidence': {'level': 'LOW'}},
            {'token': 'very_low_secret', 'confidence': {'level': 'VERY_LOW'}},
        ]
    
    def test_filter_medium_confidence(self):
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.filter_secrets_by_confidence(self.secrets, "MEDIUM")
        
        assert len(result) == 2
        assert result[0]['confidence']['level'] == 'HIGH'
        assert result[1]['confidence']['level'] == 'MEDIUM'
        mock_print.assert_called_with("Skipped 2 low-confidence detections")
    
    def test_filter_high_confidence(self):
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.filter_secrets_by_confidence(self.secrets, "HIGH")
        
        assert len(result) == 1
        assert result[0]['confidence']['level'] == 'HIGH'
        mock_print.assert_called_with("Skipped 3 low-confidence detections")


class TestApplyReplacements:
    
    def test_apply_replacements_success(self):
        cleaner = GitSecretsCleaner()
        content = "api_key = 'secret123' and token = 'secret456'"
        replacements = {'secret123': 'REDACTED_001', 'secret456': 'REDACTED_002'}
        
        modified_content, replacements_made = cleaner.apply_replacements(content, replacements)
        
        expected_content = "api_key = 'REDACTED_001' and token = 'REDACTED_002'"
        assert modified_content == expected_content
        assert len(replacements_made) == 2
        assert ('secret123', 'REDACTED_001') in replacements_made
        assert ('secret456', 'REDACTED_002') in replacements_made
    
    def test_apply_replacements_no_matches(self):
        cleaner = GitSecretsCleaner()
        content = "no secrets here"
        replacements = {'secret123': 'REDACTED_001'}
        
        modified_content, replacements_made = cleaner.apply_replacements(content, replacements)
        
        assert modified_content == content
        assert len(replacements_made) == 0


class TestGitOperations:    
    @patch('subprocess.check_output')
    def test_get_all_commits_success(self, mock_check_output):
        """Test successful commit retrieval"""
        mock_check_output.return_value = "commit1\ncommit2\ncommit3\n"
        
        cleaner = GitSecretsCleaner()
        result = cleaner.get_all_commits()
        
        assert result == ["commit1", "commit2", "commit3"]
        mock_check_output.assert_called_once_with(
            ["git", "rev-list", "--all", "--reverse"],
            text=True, timeout=60
        )
    
    @patch('subprocess.check_output')
    def test_get_all_commits_error(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "git")
        
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.get_all_commits()
        
        assert result == []
        mock_print.assert_called_with("Warning: Could not get all commits (timeout or error)")

class TestCleanHistorySimple:
    def setup_method(self):
        self.secrets = [
            {
                'token': 'secret123',
                'confidence': {'level': 'HIGH'},
                'file': 'config.py',
                'line': 10
            }
        ]
    
    def test_clean_history_simple_no_secrets(self):
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.clean_history_simple([])
        
        assert result is True
        mock_print.assert_called_with("No secrets to clean")
    
    def test_clean_history_simple_dry_run(self):
        """Test dry run mode"""
        cleaner = GitSecretsCleaner(dry_run=True)
        
        with patch('builtins.print') as mock_print:
            result = cleaner.clean_history_simple(self.secrets, "MEDIUM")
        
        assert result is True
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("DRY RUN - Would clean these files:" in call for call in print_calls)
    
    @patch('builtins.input')
    def test_clean_history_simple_cancelled(self, mock_input):
        mock_input.return_value = 'n'
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.clean_history_simple(self.secrets, "MEDIUM")
        
        assert result is False
        mock_print.assert_called_with("Cancelled")

class TestCleanHistoryCompletely:
    def setup_method(self):
        """Setup test data"""
        self.secrets = [
            {
                'token': 'secret123',
                'confidence': {'level': 'HIGH'},
                'file': 'config.py',
                'line': 10
            }
        ]
    
    def test_clean_history_completely_no_secrets(self):
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.clean_history_completely([])
        
        assert result is True
        mock_print.assert_called_with("No secrets to clean")
    
    def test_clean_history_completely_dry_run(self):
        cleaner = GitSecretsCleaner(dry_run=True)
        
        with patch('builtins.print') as mock_print:
            result = cleaner.clean_history_completely(self.secrets, "HIGH")
        
        assert result is True
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("DRY RUN - would clean:" in call for call in print_calls)

class TestLoadSecrets:    
    def test_load_secrets_success(self):
        secrets_data = {
            'secrets': [
                {'token': 'secret1', 'confidence': {'level': 'HIGH'}},
                {'token': 'secret2', 'confidence': {'level': 'MEDIUM'}}
            ]
        }
        
        mock_file_content = json.dumps(secrets_data)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            cleaner = GitSecretsCleaner()
            
            with patch('builtins.print') as mock_print:
                result = cleaner.load_secrets('test_report.json')
        
        assert result == secrets_data['secrets']
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Loaded 2 secrets from report:" in call for call in print_calls)
    
    def test_load_secrets_file_not_found(self):
        """Test when report file doesn't exist"""
        cleaner = GitSecretsCleaner()
        
        with patch('builtins.print') as mock_print:
            result = cleaner.load_secrets('nonexistent.json')
        
        assert result is None
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Report file not found:" in call for call in print_calls)


class TestVerificationSimple:    
    def test_verify_method_exists(self):
        cleaner = GitSecretsCleaner()
        assert hasattr(cleaner, '_verify_history_is_clean')
        assert callable(getattr(cleaner, '_verify_history_is_clean'))

class TestEdgeCases:    
    def test_filter_secrets_empty_list(self):
        cleaner = GitSecretsCleaner()
        result = cleaner.filter_secrets_by_confidence([], "MEDIUM")
        assert result == []
    
    def test_apply_replacements_empty_replacements(self):
        cleaner = GitSecretsCleaner()
        content = "some content"
        result_content, replacements_made = cleaner.apply_replacements(content, {})
        
        assert result_content == content
        assert replacements_made == []
    
    def test_confidence_level_case_sensitivity(self):
        secrets = [{'token': 'test', 'confidence': {'level': 'high'}}]  # lowercase
        
        cleaner = GitSecretsCleaner()
        result = cleaner.filter_secrets_by_confidence(secrets, "HIGH")
        
        assert len(result) == 0


class TestMainFunctionSimplified: 
    @patch('sys.exit')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_basic_flow(self, mock_parse_args, mock_exit):
        mock_args = MagicMock()
        mock_args.report = '.secrets_report.json'
        mock_args.dry_run = False
        mock_args.scope = 'working'
        mock_args.confidence = 'MEDIUM'
        mock_parse_args.return_value = mock_args
        
        with patch.object(GitSecretsCleaner, 'check_repo_clean', return_value=True):
            with patch.object(GitSecretsCleaner, 'load_secrets', return_value=[]):
                main()
        assert mock_exit.called
        assert all(call.args[0] == 0 for call in mock_exit.call_args_list)
    
    @patch('sys.exit')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_with_secrets(self, mock_parse_args, mock_exit):
        mock_args = MagicMock()
        mock_args.report = '.secrets_report.json'
        mock_args.dry_run = False
        mock_args.scope = 'working'
        mock_args.confidence = 'MEDIUM'
        mock_parse_args.return_value = mock_args
        
        test_secrets = [{'token': 'secret123', 'confidence': {'level': 'HIGH'}}]
        
        with patch.object(GitSecretsCleaner, 'check_repo_clean', return_value=True):
            with patch.object(GitSecretsCleaner, 'load_secrets', return_value=test_secrets):
                with patch.object(GitSecretsCleaner, 'clean_history_simple', return_value=True):
                    main()
        
        mock_exit.assert_called_with(0)
    
    @patch('sys.exit')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_repo_not_clean(self, mock_parse_args, mock_exit):
        mock_args = MagicMock()
        mock_args.report = '.secrets_report.json' 
        mock_args.dry_run = False
        mock_args.scope = 'working'
        mock_args.confidence = 'MEDIUM'
        mock_parse_args.return_value = mock_args
        
        with patch.object(GitSecretsCleaner, 'check_repo_clean', return_value=False):
            with patch.object(GitSecretsCleaner, 'load_secrets', return_value=None):
                main()

        assert mock_exit.called, "Expected main function to call sys.exit"

if __name__ == "__main__":
    pytest.main([__file__])