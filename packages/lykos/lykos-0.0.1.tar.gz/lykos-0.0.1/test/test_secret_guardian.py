import pytest
import subprocess
import sys
import os
from unittest.mock import patch, mock_open, MagicMock, call
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

try:
    from lykos.secret_guardian import SecretGuardian, main
except ImportError:
    try:
        sys.path.insert(0, os.path.join(parent_dir, 'lykos'))
        from lykos.secret_guardian import SecretGuardian, main
    except ImportError as e:
        print(f"Failed to import SecretGuardian: {e}")
        print(f"Current directory: {current_dir}")
        print(f"Parent directory: {parent_dir}")
        print(f"Python path: {sys.path}")
        sys.exit(1)

class TestSecretGuardian:    
    def setup_method(self):
        self.guardian = SecretGuardian()
    
    def test_guardian_initialization(self):
        guardian = SecretGuardian()
        assert guardian.report_file == ".secrets_report.json"
    
    @patch('subprocess.run')
    def test_check_git_repo_valid(self, mock_run):
        """Test git repository check - valid repo"""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.guardian.check_git_repo()
        
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, check=True
        )
    
    @patch('subprocess.run')
    def test_check_git_repo_invalid(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        with patch('builtins.print') as mock_print:
            result = self.guardian.check_git_repo()
        
        assert result is False
        mock_print.assert_called_with("Not in a git repository.")
    
    @patch('subprocess.check_output')
    def test_get_repo_info_success(self, mock_check_output):
        mock_check_output.side_effect = [
            "main",  # current branch
            "https://github.com/user/repo.git",  # remote origin
            "42"  # commit count
        ]
        
        result = self.guardian.get_repo_info()
        
        expected = {
            'branch': 'main',
            'remote': 'https://github.com/user/repo.git',
            'commit_count': 42
        }
        assert result == expected
    
    @patch('subprocess.check_output')
    def test_get_repo_info_no_remote(self, mock_check_output):
        """Test repo info when no remote is configured"""
        def side_effect(cmd, **kwargs):
            if "branch" in cmd:
                return "main"
            elif "remote" in cmd:
                raise subprocess.CalledProcessError(1, 'git')
            elif "rev-list" in cmd:
                return "42"
        
        mock_check_output.side_effect = side_effect
        
        result = self.guardian.get_repo_info()
        
        assert result['branch'] == 'main'
        assert result['remote'] == "No remote configured"
        assert result['commit_count'] == 42
    
    @patch('subprocess.check_output')
    def test_get_repo_info_failure(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(1, 'git')
        
        result = self.guardian.get_repo_info()
        
        assert result is None
    
    @patch.object(SecretGuardian, 'setup_protection')
    @patch.object(SecretGuardian, 'print_final_recommendations')
    @patch.object(SecretGuardian, 'get_repo_info')
    def test_full_scan_and_clean_no_secrets(self, mock_get_repo, mock_print_recs, mock_setup):
        """Test full scan when no secrets are found"""
        mock_get_repo.return_value = {
            'branch': 'main',
            'remote': 'https://github.com/test/repo.git',
            'commit_count': 10
        }
        
        mock_scanner = MagicMock()
        mock_scanner.scan_commits.return_value = []
        mock_scanner.generate_report.return_value = {}
        
        secret_guardian_module = sys.modules[self.guardian.__module__]
        
        with patch.object(secret_guardian_module, 'SecretScanner', return_value=mock_scanner):
            with patch('builtins.print') as mock_print:
                result = self.guardian.full_scan_and_clean(recent_commits=5)
        
        assert result is True
        mock_scanner.scan_commits.assert_called_once_with(recent=5)
        mock_setup.assert_called_once()
        mock_print.assert_any_call("No secrets found! Repository is clean.")
        mock_print_recs.assert_not_called()
    
    @patch.object(SecretGuardian, 'setup_protection')
    @patch.object(SecretGuardian, 'print_final_recommendations')
    @patch.object(SecretGuardian, 'get_repo_info')
    def test_full_scan_and_clean_with_secrets(self, mock_get_repo, mock_print_recs, mock_setup):
        """Test full scan when secrets are found"""
        mock_get_repo.return_value = {'branch': 'main', 'remote': 'origin', 'commit_count': 5}
        
        secrets = [{'token': 'AKIATEST123', 'type': 'AWS_ACCESS_KEY'}]
        
        mock_scanner = MagicMock()
        mock_scanner.scan_commits.return_value = secrets
        mock_scanner.generate_report.return_value = {'secrets': secrets}
        
        mock_cleaner = MagicMock()
        mock_cleaner.check_dependencies.return_value = True
        mock_cleaner.clean_history.return_value = True
        
        secret_guardian_module = sys.modules[self.guardian.__module__]
        
        with patch.object(secret_guardian_module, 'SecretScanner', return_value=mock_scanner):
            with patch.object(secret_guardian_module, 'HistoryCleaner', return_value=mock_cleaner):
                result = self.guardian.full_scan_and_clean()
        
        assert result is True
        mock_cleaner.clean_history.assert_called_once_with(secrets, force=False)
        mock_setup.assert_called_once()
        mock_print_recs.assert_called_once_with(secrets)
    
    @patch.object(SecretGuardian, 'get_repo_info')
    def test_full_scan_missing_dependencies(self, mock_get_repo):
        """Test full scan when git-filter-repo is missing"""
        mock_get_repo.return_value = {'branch': 'main', 'remote': 'origin', 'commit_count': 5}
        
        secrets = [{'token': 'AKIATEST123', 'type': 'AWS_ACCESS_KEY'}]
        
        mock_scanner = MagicMock()
        mock_scanner.scan_commits.return_value = secrets
        mock_scanner.generate_report.return_value = {'secrets': secrets}
        
        mock_cleaner = MagicMock()
        mock_cleaner.check_dependencies.return_value = False
        
        secret_guardian_module = sys.modules[self.guardian.__module__]
        
        with patch.object(secret_guardian_module, 'SecretScanner', return_value=mock_scanner):
            with patch.object(secret_guardian_module, 'HistoryCleaner', return_value=mock_cleaner):
                with patch('builtins.print') as mock_print:
                    result = self.guardian.full_scan_and_clean()
        
        assert result is False
        mock_print.assert_any_call("Cannot proceed without git-filter-repo")
    
    @patch.object(SecretGuardian, 'update_gitignore')
    def test_setup_protection_success(self, mock_update_gitignore):
        """Test setting up protection successfully"""
        mock_guard = MagicMock()
        mock_guard.install_git_hook.return_value = True
        
        secret_guardian_module = sys.modules[self.guardian.__module__]
        
        with patch.object(secret_guardian_module, 'PreCommitGuard', return_value=mock_guard):
            with patch('builtins.print') as mock_print:
                self.guardian.setup_protection()
        
        mock_guard.install_git_hook.assert_called_once()
        mock_update_gitignore.assert_called_once()
        mock_print.assert_any_call("Pre-commit hook installed successfully")
    
    @patch.object(SecretGuardian, 'update_gitignore')
    def test_setup_protection_hook_failure(self, mock_update_gitignore):
        """Test protection setup when hook installation fails"""
        mock_guard = MagicMock()
        mock_guard.install_git_hook.return_value = False
        
        secret_guardian_module = sys.modules[self.guardian.__module__]
        
        with patch.object(secret_guardian_module, 'PreCommitGuard', return_value=mock_guard):
            with patch('builtins.print') as mock_print:
                self.guardian.setup_protection()
        
        mock_print.assert_any_call("Failed to install pre-commit hook")
    
    @patch('builtins.open', new_callable=mock_open, read_data="existing content\n")
    @patch('pathlib.Path.exists')
    def test_update_gitignore_existing_file(self, mock_exists, mock_file):
        """Test updating existing .gitignore file"""
        mock_exists.return_value = True
        
        entries = ["new_entry", "existing content", "another_new_entry"]
        
        with patch('builtins.print') as mock_print:
            self.guardian.update_gitignore(entries)
        
        # should write new entries that dont already exist
        mock_file.assert_any_call(Path(".gitignore"), 'a')
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        assert "new_entry" in written_content
        assert "another_new_entry" in written_content
        
        mock_print.assert_called_with("Added 2 entries to .gitignore")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_update_gitignore_new_file(self, mock_exists, mock_file):
        mock_exists.return_value = False
        
        entries = ["entry1", "entry2"]
        
        with patch('builtins.print') as mock_print:
            self.guardian.update_gitignore(entries)
        
        mock_file.assert_any_call(Path(".gitignore"), 'a')
        mock_print.assert_called_with("Added 2 entries to .gitignore")
    
    def test_print_final_recommendations_aws_secrets(self):
        """Test printing recommendations for AWS secrets"""
        secrets = [
            {
                'token': 'AKIATEST1234567890',
                'type': 'AWS_ACCESS_KEY',
                'commit': 'abc123'
            },
            {
                'token': 'secretkey1234567890abcdef',
                'type': 'AWS_SECRET_KEY', 
                'commit': 'def456'
            }
        ]
        
        with patch('builtins.print') as mock_print:
            self.guardian.print_final_recommendations(secrets)
        
        # check that aws-specific recs are printed
        printed_lines = [str(call.args[0]) for call in mock_print.call_args_list]
        aws_recommendations = [line for line in printed_lines if "AWS IAM Console" in line]
        assert len(aws_recommendations) >= 1
    
    def test_print_final_recommendations_multiple_types(self):
        """Test recommendations for multiple secret types"""
        secrets = [
            {'token': 'AKIATEST1234567890', 'type': 'AWS_ACCESS_KEY'},
            {'token': 'ghp_test1234567890', 'type': 'GitHub_Token'},
            {'token': 'sk-test1234567890', 'type': 'OpenAI'},
            {'token': 'sk_live_test123', 'type': 'Stripe_Live'}
        ]
        
        with patch('builtins.print') as mock_print:
            self.guardian.print_final_recommendations(secrets)
        
        printed_lines = [str(call.args[0]) for call in mock_print.call_args_list]
        printed_text = '\n'.join(printed_lines)
        
        # check service-specific recommendations
        assert "AWS IAM Console" in printed_text
        assert "GitHub Settings" in printed_text  
        assert "OpenAI Platform" in printed_text
        assert "Stripe Dashboard" in printed_text


class TestMainFunction:
    
    @patch.object(SecretGuardian, 'check_git_repo')
    @patch.object(SecretGuardian, 'full_scan_and_clean')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_full_scan(self, mock_exit, mock_args, mock_full_scan, mock_check_repo):
        """Test main function with --full-scan"""
        mock_args.return_value = MagicMock(
            full_scan=True, scan_only=False, clean_only=False, 
            setup_protection=False, check_current=False,
            recent=10, dry_run=False, force=False,
            report=".secrets_report.json"
        )
        mock_check_repo.return_value = True
        mock_full_scan.return_value = True
        
        main()
        
        mock_full_scan.assert_called_once_with(
            recent_commits=10, dry_run=False, force=False
        )
        mock_exit.assert_called_once_with(0)
    
    @patch.object(SecretGuardian, 'check_git_repo')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_scan_only(self, mock_exit, mock_args, mock_check_repo):
        """Test main function with --scan-only"""
        mock_args.return_value = MagicMock(
            full_scan=False, scan_only=True, clean_only=False,
            setup_protection=False, check_current=False,
            recent=None, dry_run=False, force=False,
            report=".secrets_report.json"
        )
        mock_check_repo.return_value = True
        
        mock_scanner = MagicMock()
        mock_scanner.scan_commits.return_value = []
        mock_scanner.generate_report.return_value = {}
        
        main_module = sys.modules[main.__module__]
        
        with patch.object(main_module, 'SecretScanner', return_value=mock_scanner):
            main()
        
        mock_scanner.scan_commits.assert_called_once_with(all_commits=True)
        mock_exit.assert_called_once_with(0)
    
    @patch.object(SecretGuardian, 'check_git_repo')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_clean_only(self, mock_exit, mock_args, mock_check_repo):
        mock_args.return_value = MagicMock(
            full_scan=False, scan_only=False, clean_only=True,
            setup_protection=False, check_current=False,
            recent=None, dry_run=True, force=True,
            report=".secrets_report.json"
        )
        mock_check_repo.return_value = True
        
        mock_cleaner = MagicMock()
        mock_cleaner.check_dependencies.return_value = True
        mock_cleaner.load_secrets_report.return_value = [{'token': 'test'}]
        mock_cleaner.clean_history.return_value = True
        
        main_module = sys.modules[main.__module__]
        
        with patch.object(main_module, 'HistoryCleaner', return_value=mock_cleaner):
            main()
        
        mock_cleaner.clean_history.assert_called_once_with([{'token': 'test'}], force=True)
        mock_exit.assert_called_once_with(0)
    
    @patch.object(SecretGuardian, 'setup_protection')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_setup_protection(self, mock_exit, mock_args, mock_setup):
        """Test main function with --setup-protection"""
        mock_args.return_value = MagicMock(
            full_scan=False, scan_only=False, clean_only=False,
            setup_protection=True, check_current=False,
            report=".secrets_report.json"
        )
        
        with patch('builtins.print') as mock_print:
            main()
        
        mock_setup.assert_called_once()
        mock_print.assert_called_with("Protection setup complete!")
        mock_exit.assert_called_once_with(0)
    
    @patch.object(SecretGuardian, 'check_git_repo')
    @patch('pathlib.Path.glob')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_check_current(self, mock_exit, mock_args, mock_glob, mock_check_repo):
        """Test main function with --check-current"""
        mock_args.return_value = MagicMock(
            full_scan=False, scan_only=False, clean_only=False,
            setup_protection=False, check_current=True,
            report=".secrets_report.json"
        )
        mock_check_repo.return_value = True
        
        mock_glob.return_value = [Path("test.py"), Path("main.py")]
        
        mock_guard = MagicMock()
        mock_guard.scan_files.return_value = []
        mock_guard.report_violations.return_value = True
        
        main_module = sys.modules[main.__module__]
        
        with patch.object(main_module, 'PreCommitGuard', return_value=mock_guard):
            main()
        
        mock_guard.scan_files.assert_called_once_with(["test.py", "main.py"])
        mock_exit.assert_called_once_with(0)
    
    @patch.object(SecretGuardian, 'check_git_repo')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_not_git_repo(self, mock_exit, mock_args, mock_check_repo):
        """Test main function when not in git repository"""
        mock_args.return_value = MagicMock(
            full_scan=True, setup_protection=False,
            recent=None,
            report=".secrets_report.json"
        )
        mock_check_repo.return_value = False
        
        mock_exit.side_effect = SystemExit
        
        with pytest.raises(SystemExit):
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_clean_missing_dependencies(self, mock_exit, mock_args):
        """Test main clean-only when dependencies missing"""
        mock_args.return_value = MagicMock(
            full_scan=False, scan_only=False, clean_only=True,
            setup_protection=False, check_current=False,
            report=".secrets_report.json"
        )
        
        mock_cleaner = MagicMock()
        mock_cleaner.check_dependencies.return_value = False
        mock_cleaner.load_secrets_report.return_value = None
        
        mock_exit.side_effect = SystemExit
        
        main_module = sys.modules[main.__module__]
        
        with patch.object(SecretGuardian, 'check_git_repo', return_value=True):
            with patch.object(main_module, 'HistoryCleaner', return_value=mock_cleaner):
                with patch('builtins.print'):
                    with pytest.raises(SystemExit):
                        main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch.object(SecretGuardian, 'check_git_repo')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_scan_with_secrets_found(self, mock_exit, mock_args, mock_check_repo):
        """Test main scan-only when secrets are found (should exit 1)"""
        mock_args.return_value = MagicMock(
            full_scan=False, scan_only=True, clean_only=False,
            setup_protection=False, check_current=False,
            recent=5, report=".secrets_report.json"
        )
        mock_check_repo.return_value = True
        
        mock_scanner = MagicMock()
        mock_scanner.scan_commits.return_value = [{'token': 'secret'}]
        mock_scanner.generate_report.return_value = {'secrets': [{'token': 'secret'}]}
        
        main_module = sys.modules[main.__module__]
        
        with patch.object(main_module, 'SecretScanner', return_value=mock_scanner):
            main()
        
        mock_scanner.scan_commits.assert_called_once_with(recent=5)
        mock_exit.assert_called_once_with(1)


class TestEdgeCases:    
    def test_guardian_with_custom_report_file(self):
        """Test guardian with custom report file"""
        guardian = SecretGuardian()
        guardian.report_file = "custom_report.json"
        assert guardian.report_file == "custom_report.json"
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_update_gitignore_permission_error(self, mock_open):
        """Test gitignore update with permission error"""
        guardian = SecretGuardian()
        
        with pytest.raises(IOError):
            guardian.update_gitignore(["test_entry"])
    
    def test_print_recommendations_empty_secrets(self):
        """Test recommendations with empty secrets list"""
        guardian = SecretGuardian()
        
        with patch('builtins.print') as mock_print:
            guardian.print_final_recommendations([])
        
        printed_lines = [str(call.args[0]) for call in mock_print.call_args_list]
        assert any("SECURITY ACTIONS" in line for line in printed_lines)
    
    @patch('subprocess.check_output')
    def test_repo_info_partial_failure(self, mock_check_output):
        def side_effect(cmd, **kwargs):
            if "branch" in cmd:
                return "feature-branch"
            elif "remote" in cmd:
                raise subprocess.CalledProcessError(1, 'git')
            elif "rev-list" in cmd:
                raise subprocess.CalledProcessError(1, 'git')
        
        mock_check_output.side_effect = side_effect
        
        guardian = SecretGuardian()
        result = guardian.get_repo_info()
        
        assert result['branch'] == 'feature-branch'
        assert result['remote'] == "No remote configured"
        assert result['commit_count'] == 0


class TestIntegration:
    @patch('subprocess.run')
    @patch('subprocess.check_output')
    @patch.object(SecretGuardian, 'setup_protection')
    def test_complete_workflow_integration(self, mock_setup, mock_check_output, mock_run):
        """Test complete workflow integration"""
        guardian = SecretGuardian()
        
        mock_run.return_value = MagicMock(returncode=0)
        mock_check_output.side_effect = [
            "main",  
            "https://github.com/test/repo.git", 
            "100"  
        ]
        
        secrets = [
            {'token': 'AKIATEST123', 'type': 'AWS_ACCESS_KEY', 'commit': 'abc123'},
            {'token': 'ghp_test456', 'type': 'GitHub_Token', 'commit': 'def456'}
        ]
        mock_scanner = MagicMock()
        mock_scanner.scan_commits.return_value = secrets
        mock_scanner.generate_report.return_value = {'secrets': secrets}
        
        # Mock cleaner success
        mock_cleaner = MagicMock()
        mock_cleaner.check_dependencies.return_value = True
        mock_cleaner.clean_history.return_value = True
        
        secret_guardian_module = sys.modules[guardian.__module__]
        
        with patch.object(secret_guardian_module, 'SecretScanner', return_value=mock_scanner):
            with patch.object(secret_guardian_module, 'HistoryCleaner', return_value=mock_cleaner):
                with patch('builtins.print') as mock_print:
                    result = guardian.full_scan_and_clean(recent_commits=10, force=True)
        
        assert result is True
        mock_scanner.scan_commits.assert_called_once_with(recent=10)
        mock_cleaner.clean_history.assert_called_once_with(secrets, force=True)
        mock_setup.assert_called_once()
        
        printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
        assert any("Secret Guardian" in msg for msg in printed_messages)
        assert any("Step 1: Scanning" in msg for msg in printed_messages)
        assert any("Step 2: Cleaning" in msg for msg in printed_messages)


if __name__ == "__main__":    
    pytest.main([__file__, "-v"])