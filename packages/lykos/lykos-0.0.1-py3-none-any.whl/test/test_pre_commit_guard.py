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

from lykos.pre_commit_guard import PreCommitGuard, main, ENTROPY_THRESHOLD

class TestPreCommitGuard:
    
    def setup_method(self):
        self.guard = PreCommitGuard()
    
    def test_guard_initialization(self):
        guard = PreCommitGuard()
        assert guard.entropy_threshold == ENTROPY_THRESHOLD
        assert guard.strict_mode is False
        assert guard.violations == []
        
        strict_guard = PreCommitGuard(entropy_threshold=5.0, strict_mode=True)
        assert strict_guard.entropy_threshold == 5.0
        assert strict_guard.strict_mode is True
    
    def test_shannon_entropy_calculation(self):
        """Test Shannon entropy calculation"""
        #  empty string
        assert self.guard.shannon_entropy("") == 0.0
        
        # short string
        assert self.guard.shannon_entropy("abc") == 0.0
        
        # uniforrm distribution
        high_entropy = self.guard.shannon_entropy("abcdefghijklmnop")
        assert high_entropy > 3.5
        
        # repeated chars (low entropy)
        low_entropy = self.guard.shannon_entropy("aaaaaaaaaaaaaaaa")
        assert low_entropy == 0.0
        
        # mixed case with numbers (medium entropy)
        mixed_entropy = self.guard.shannon_entropy("aA1bB2cC3dD4eE5f")
        assert 2.0 < mixed_entropy <= 4.0
    
    def test_is_false_positive(self):
        # test known false positives
        assert self.guard.is_false_positive("EXAMPLE_KEY_123456789") is True
        assert self.guard.is_false_positive("API_KEY_HERE") is True
        assert self.guard.is_false_positive("REPLACE_WITH_YOUR_KEY") is True
        assert self.guard.is_false_positive("AKIAIOSFODNN7EXAMPLE") is True
        
        # test case sensitivity
        assert self.guard.is_false_positive("example_key_123456789") is True
        assert self.guard.is_false_positive("api_key_here") is True
        
        # actual fake secrets (should not be false positives)
        assert self.guard.is_false_positive("AKIATEST123456789012") is False
        assert self.guard.is_false_positive("sk-abcdef1234567890abcdef1234567890abcdef1234") is False
    
    def test_is_test_file(self):
        assert self.guard.is_test_file("test_something.py") is True
        assert self.guard.is_test_file("something_test.py") is True
        assert self.guard.is_test_file("test/test_file.py") is True
        assert self.guard.is_test_file("spec/user_spec.rb") is True
        assert self.guard.is_test_file("mocks/mock_api.js") is True
        assert self.guard.is_test_file("fixtures/sample_data.json") is True
        assert self.guard.is_test_file("examples/example_config.yaml") is True
        
        assert self.guard.is_test_file("main.py") is False
        assert self.guard.is_test_file("src/app.py") is False
        assert self.guard.is_test_file("config.json") is False
    
    def test_scan_content_patterns(self):
        test_content = """
# AWS Keys
aws_access_key = "AKIATEST123456789012"
aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYREALKEY"

# OpenAI Key  
openai_key = "sk-abcdef1234567890abcdef1234567890abcdef1234"

# GitHub Token
github_token = "ghp_1234567890abcdef1234567890abcdef123456"

# Stripe Keys
stripe_live = "sk_live_1234567890abcdef12345678"
stripe_test = "sk_test_1234567890abcdef12345678"

# Google API
google_api = "AIzaSyC1234567890abcdef1234567890abcdef123"

# JWT Token
jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Private Key
private_key = "-----BEGIN RSA PRIVATE KEY-----"
        """
        
        violations = self.guard.scan_content(test_content, "test_file.py")
        
        assert len(violations) >= 3, f"Expected at least 3 violations, got {len(violations)}"
        
        for violation in violations:
            assert 'type' in violation
            assert 'token' in violation
            assert 'file' in violation
            assert 'line' in violation
            assert 'context' in violation
            assert 'severity' in violation
    
    def test_scan_content_comments_ignored(self):
        """Test that comments are ignored during scanning"""
        test_content = """
# This is a comment with AKIAIOSFODNN7EXAMPLE
// comment with sk-1234567890abcdef1234567890abcdef12345678
/* block comment with ghp_1234567890abcdef1234567890abcdef123456 */
* another comment style
-- SQL comment with API key: AIzaSyC1234567890abcdef1234567890abcdef123

actual_key = "AKIAIOSFODNN7REALKEY"
        """
        
        violations = self.guard.scan_content(test_content, "test_file.py")
        
        assert len(violations) >= 1
        for violation in violations:
            assert "actual_key" in violation['context']
    
    def test_scan_content_high_entropy(self):
        """high entropy detection"""
        test_content = """
random_string = "aB3dE6fG9hI2jK5lM8nO1pQ4rS7tU0vW"
base64_like = "SGVsbG9Xb3JsZEhlbGxvV29ybGRIZWxsb1dvcmxk"
hex_string = "1a2b3c4d5e6f7890abcdef1234567890abcdef12"
another_random = "zY8xW3vU6tR9qN2mL5kJ8hG4fD1aC9bE"

simple_string = "aaaaaaaaaaaaaaaaaaaa"
readable_text = "this_is_just_readable_text"
        """
        
        violations = self.guard.scan_content(test_content, "test_file.py")
        
        entropy_violations = [v for v in violations if v['type'] == 'HIGH_ENTROPY']
        assert len(entropy_violations) >= 1
        
        for violation in entropy_violations:
            assert violation['entropy'] > self.guard.entropy_threshold
            assert violation['severity'] == 'MEDIUM'
    
    @patch('subprocess.run')
    def test_get_staged_files_success(self, mock_run):
        """Test getting staged files successfully"""
        mock_run.return_value = MagicMock(
            stdout="file1.py\nfile2.js\nfile3.txt\n",
            returncode=0
        )
        
        files = self.guard.get_staged_files()
        
        assert files == ["file1.py", "file2.js", "file3.txt"]
        mock_run.assert_called_once_with(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, check=True
        )
    
    @patch('subprocess.run')
    def test_get_staged_files_empty(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="",
            returncode=0
        )
        
        files = self.guard.get_staged_files()
        
        assert files == []
    
    @patch('subprocess.run')
    def test_get_staged_files_failure(self, mock_run):
        """Test getting staged files when git command fails"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        files = self.guard.get_staged_files()
        
        assert files == []
    
    @patch('subprocess.run')
    def test_get_file_content_staged(self, mock_run):
        """Test getting staged file content"""
        mock_run.return_value = MagicMock(
            stdout="file content here",
            returncode=0
        )
        
        content = self.guard.get_file_content("test.py", staged=True)
        
        assert content == "file content here"
        mock_run.assert_called_once_with(
            ["git", "show", ":test.py"],
            capture_output=True, text=True, check=True
        )
    
    @patch('builtins.open', new_callable=mock_open, read_data="file content from disk")
    def test_get_file_content_from_disk(self, mock_file):
        """Test getting file content from disk"""
        content = self.guard.get_file_content("test.py", staged=False)
        
        assert content == "file content from disk"
        mock_file.assert_called_once_with("test.py", 'r', encoding='utf-8', errors='ignore')
    
    @patch('subprocess.run')
    def test_get_file_content_failure(self, mock_run):
        """Test getting file content when command fails"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        content = self.guard.get_file_content("test.py", staged=True)
        
        assert content == ""
    
    @patch.object(PreCommitGuard, 'get_file_content')
    @patch.object(PreCommitGuard, 'get_staged_files')
    def test_scan_staged_files(self, mock_get_files, mock_get_content):
        """Test scanning staged files"""
        mock_get_files.return_value = ["test.py", "config.json", "image.jpg"]
        mock_get_content.side_effect = [
            'api_key = "AKIATEST123456789012"',  
            '{"key": "value"}',  # config.json
            ""  # image.jpg (should be skipped)
        ]
        
        violations = self.guard.scan_staged_files()
        
        assert mock_get_content.call_count == 2
        mock_get_content.assert_any_call("test.py", staged=True)
        mock_get_content.assert_any_call("config.json", staged=True)
        
        assert len(violations) >= 1
    
    @patch('os.path.exists')
    @patch.object(PreCommitGuard, 'get_file_content')
    def test_scan_files(self, mock_get_content, mock_exists):
        """Test scanning specific files"""
        mock_exists.side_effect = [True, True, False]
        mock_get_content.side_effect = [
            'secret = "sk-1234567890abcdef1234567890abcdef12345678"',
            'normal code here',
        ]
        
        files = ["file1.py", "file2.py", "nonexistent.py"]
        violations = self.guard.scan_files(files)
        
        assert mock_get_content.call_count == 2
        mock_get_content.assert_any_call("file1.py", staged=False)
        mock_get_content.assert_any_call("file2.py", staged=False)
        
        assert len(violations) >= 1
    
    def test_report_violations_none(self):
        with patch('builtins.print') as mock_print:
            result = self.guard.report_violations([])
        
        assert result is True
        mock_print.assert_not_called()
    
    def test_report_violations_high_severity(self):
        violations = [
            {
                'type': 'AWS_ACCESS_KEY',
                'token': 'AKIATEST123456789012',
                'file': 'config.py',
                'line': 10,
                'context': 'aws_key = "AKIATEST123456789012"',
                'severity': 'HIGH'
            },
            {
                'type': 'OpenAI',
                'token': 'sk-1234567890abcdef1234567890abcdef12345678',
                'file': 'app.py',
                'line': 25,
                'context': 'openai_key = "sk-1234567890abcdef1234567890abcdef12345678"',
                'severity': 'HIGH'
            }
        ]
        
        with patch('builtins.print') as mock_print:
            result = self.guard.report_violations(violations)
        
        assert result is False
        
        printed_calls = [call for call in mock_print.call_args_list if call.args]
        printed_lines = [str(call.args[0]) for call in printed_calls]
        printed_text = '\n'.join(printed_lines)
        
        assert "SECURITY ALERT" in printed_text
        assert "HIGH SEVERITY" in printed_text
        assert "AWS_ACCESS_KEY" in printed_text or "OpenAI" in printed_text
    
    def test_report_violations_medium_severity(self):
        """Test reporting medium severity violations"""
        violations = [
            {
                'type': 'HIGH_ENTROPY',
                'token': 'aB3dE6fG9hI2jK5lM8nO1pQ4rS7tU0vW',
                'file': 'data.py',
                'line': 15,
                'context': 'random_data = "aB3dE6fG9hI2jK5lM8nO1pQ4rS7tU0vW"',
                'entropy': 4.8,
                'severity': 'MEDIUM'
            }
        ]
        
        with patch('builtins.print') as mock_print:
            result = self.guard.report_violations(violations)
        
        assert result is False
        
        printed_calls = [call for call in mock_print.call_args_list if call.args]
        printed_lines = [str(call.args[0]) for call in printed_calls]
        printed_text = '\n'.join(printed_lines)
        
        assert "MEDIUM SEVERITY" in printed_text
        assert "HIGH_ENTROPY" in printed_text
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.chmod')
    def test_install_git_hook_success(self, mock_chmod, mock_file, mock_mkdir, mock_exists):
        """Test successful git hook installation"""
        mock_exists.return_value = True 
        
        with patch('builtins.print') as mock_print:
            result = self.guard.install_git_hook()
        
        assert result is True
        
        mock_file.assert_called_once()
        mock_chmod.assert_called_once()
        
        printed_lines = [str(call.args[0]) for call in mock_print.call_args_list]
        assert any("Pre-commit hook installed" in line for line in printed_lines)
    
    @patch('pathlib.Path.exists')
    def test_install_git_hook_no_git_repo(self, mock_exists):
        """test git hook installation when not in git repo"""
        mock_exists.return_value = False
        
        with patch('builtins.print') as mock_print:
            result = self.guard.install_git_hook()
        
        assert result is False
        mock_print.assert_called_with("❌ Not in a git repository")
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('pathlib.Path.mkdir')
    def test_install_git_hook_permission_error(self, mock_mkdir, mock_file, mock_exists):
        """Test git hook installation with permission error"""
        mock_exists.return_value = True
        
        with patch('builtins.print') as mock_print:
            result = self.guard.install_git_hook()
        
        assert result is False
        
        printed_calls = [call for call in mock_print.call_args_list if call.args]
        printed_lines = [str(call.args[0]) for call in printed_calls]
        assert any("Failed to install hook" in line for line in printed_lines)


class TestMainFunction:    
    @patch.object(PreCommitGuard, 'install_git_hook')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_install_hook_success(self, mock_exit, mock_args, mock_install):
        """Test main function with --install-hook"""
        mock_args.return_value = MagicMock(
            install_hook=True, scan_staged=False, files=None,
            strict=False, entropy=ENTROPY_THRESHOLD
        )
        mock_install.return_value = True
        
        mock_exit.side_effect = SystemExit
        
        with pytest.raises(SystemExit):
            main()
        
        mock_install.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch.object(PreCommitGuard, 'install_git_hook')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_install_hook_failure(self, mock_exit, mock_args, mock_install):
        mock_args.return_value = MagicMock(
            install_hook=True, scan_staged=False, files=None,
            strict=False, entropy=ENTROPY_THRESHOLD
        )
        mock_install.return_value = False
        
        mock_exit.side_effect = SystemExit
        
        with pytest.raises(SystemExit):
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch.object(PreCommitGuard, 'scan_staged_files')
    @patch.object(PreCommitGuard, 'report_violations')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_scan_staged_clean(self, mock_exit, mock_args, mock_report, mock_scan):
        """Test main function scanning staged files with no violations"""
        mock_args.return_value = MagicMock(
            install_hook=False, scan_staged=True, files=None,
            strict=False, entropy=ENTROPY_THRESHOLD
        )
        mock_scan.return_value = []
        mock_report.return_value = True
        
        mock_exit.side_effect = SystemExit
        
        with pytest.raises(SystemExit):
            main()
        
        mock_scan.assert_called_once()
        mock_report.assert_called_once_with([])
        mock_exit.assert_called_once_with(0)
    
    @patch.object(PreCommitGuard, 'scan_staged_files')
    @patch.object(PreCommitGuard, 'report_violations')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_scan_staged_violations(self, mock_exit, mock_args, mock_report, mock_scan):
        mock_args.return_value = MagicMock(
            install_hook=False, scan_staged=True, files=None,
            strict=False, entropy=ENTROPY_THRESHOLD
        )
        violations = [{'type': 'AWS_ACCESS_KEY', 'token': 'test'}]
        mock_scan.return_value = violations
        mock_report.return_value = False
        
        mock_exit.side_effect = SystemExit
        
        with pytest.raises(SystemExit):
            main()
        
        mock_scan.assert_called_once()
        mock_report.assert_called_once_with(violations)
        mock_exit.assert_called_once_with(1)
    
    @patch.object(PreCommitGuard, 'scan_files')
    @patch.object(PreCommitGuard, 'report_violations')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_scan_specific_files(self, mock_exit, mock_args, mock_report, mock_scan):
        mock_args.return_value = MagicMock(
            install_hook=False, scan_staged=False, files=["test.py", "config.js"],
            strict=True, entropy=5.0
        )
        mock_scan.return_value = []
        mock_report.return_value = True
        
        mock_exit.side_effect = SystemExit
        
        with pytest.raises(SystemExit):
            main()
        
        mock_scan.assert_called_once_with(["test.py", "config.js"])
        mock_exit.assert_called_once_with(0)
    
    @patch('subprocess.run')
    @patch.object(PreCommitGuard, 'scan_staged_files')
    @patch.object(PreCommitGuard, 'report_violations')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_default_git_repo(self, mock_exit, mock_args, mock_report, mock_scan, mock_subprocess):
        """Test main function default behavior in git repo"""
        mock_args.return_value = MagicMock(
            install_hook=False, scan_staged=False, files=None,
            strict=False, entropy=ENTROPY_THRESHOLD
        )
        mock_subprocess.return_value = MagicMock(returncode=0)  # git command succeeds
        mock_scan.return_value = []
        mock_report.return_value = True
        
        mock_exit.side_effect = SystemExit
        
        with pytest.raises(SystemExit):
            main()
        
        mock_subprocess.assert_called_once_with(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, check=True
        )
        mock_scan.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('subprocess.run')
    @patch('pathlib.Path.glob')
    @patch.object(PreCommitGuard, 'scan_files')
    @patch.object(PreCommitGuard, 'report_violations')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_default_not_git_repo(self, mock_exit, mock_args, mock_report, 
                                      mock_scan, mock_glob, mock_subprocess):
        """Test main function default behavior outside git repo"""
        mock_args.return_value = MagicMock(
            install_hook=False, scan_staged=False, files=None,
            strict=False, entropy=ENTROPY_THRESHOLD
        )
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'git')
        mock_glob.return_value = [Path("test.py"), Path("main.py")]
        mock_scan.return_value = []
        mock_report.return_value = True
        
        mock_exit.side_effect = SystemExit
        
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit):
                main()
        
        mock_scan.assert_called_once_with(["test.py", "main.py"])
        mock_print.assert_any_call("Not in git repo, scanning current directory Python files...")
        mock_exit.assert_called_once_with(0)

class TestEdgeCases:
    
    def test_entropy_edge_cases(self):
        guard = PreCommitGuard()
        
        # None input
        assert guard.shannon_entropy(None) == 0.0
        # single character
        assert guard.shannon_entropy("a") == 0.0
        
        # 2 characters
        assert guard.shannon_entropy("ab") == 0.0
        
        # min length for calculation
        assert guard.shannon_entropy("abcd") > 0.0
    
    def test_patterns_coverage(self):
        guard = PreCommitGuard()
        
        test_strings = {
            "AWS_ACCESS_KEY": "AKIATEST123456789012",  
            "AWS_SECRET_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "Google_API": "AIzaSyC1234567890abcdef1234567890abcdef123",
            "Stripe_Live": "sk_live_1234567890abcdef12345678",
            "Stripe_Test": "sk_test_1234567890abcdef12345678",
            "OpenAI": "sk-abcdef1234567890abcdef1234567890abcdef1234",  
            "GitHub_Token": "ghp_1234567890abcdef1234567890abcdef123456",
            "JWT": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.test",
            "Private_Key": "-----BEGIN RSA PRIVATE KEY-----",
            "Bearer_Token": "Bearer abcdef1234567890abcdef1234567890"
        }
        
        for pattern_name, test_string in test_strings.items():
            content = f'key = "{test_string}"'
            violations = guard.scan_content(content, "test.py")
            
            assert len(violations) > 0, f"No violations found for pattern {pattern_name} with string: {test_string}"
    
    def test_binary_file_extensions(self):
        """Test that tje binary files are properly skipped"""
        guard = PreCommitGuard()
        
        binary_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.exe', 
            '.bin', '.so', '.dll', '.dylib', '.zip', '.tar', '.gz'
        ]
        
        with patch.object(guard, 'get_staged_files') as mock_get_files:
            with patch.object(guard, 'get_file_content') as mock_get_content:
                files = [f"file{ext}" for ext in binary_extensions] + ["text.py"]
                mock_get_files.return_value = files
                mock_get_content.return_value = "some content"
                
                violations = guard.scan_staged_files()
                
                mock_get_content.assert_called_once_with("text.py", staged=True)
    
    def test_strict_mode_test_files(self):
        """Test strict mode behavior with test files"""
        strict_guard = PreCommitGuard(strict_mode=True)
        normal_guard = PreCommitGuard(strict_mode=False)
        
        test_content = 'secret = "aB3dE6fG9hI2jK5lM8nO1pQ4rS7tU0vW"'
        
        normal_violations = normal_guard.scan_content(test_content, "test_file.py")
        
        strict_violations = strict_guard.scan_content(test_content, "test_file.py")
        
        assert len(normal_violations) >= len(strict_violations)


class TestIntegration:
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.chmod')
    def test_complete_hook_installation_workflow(self, mock_chmod, mock_file, mock_mkdir,
                                                mock_exists, mock_subprocess):
        """Test complete hook installation workflow"""
        mock_exists.return_value = True
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        guard = PreCommitGuard()
        
        with patch('builtins.print') as mock_print:
            result = guard.install_git_hook()
        
        assert result is True
        
        written_content = mock_file().write.call_args_list
        hook_script = ''.join(call.args[0] for call in written_content)
        
        assert "pre_commit_guard import PreCommitGuard" in hook_script
        assert "guard.scan_staged_files()" in hook_script
        assert "sys.exit(1)" in hook_script
        
        mock_chmod.assert_called_once()
        
        printed_calls = [call for call in mock_print.call_args_list if call.args]
        printed_lines = [str(call.args[0]) for call in printed_calls]
        assert any("hook installed" in line.lower() for line in printed_lines)
    
    @patch.object(PreCommitGuard, 'get_staged_files')
    @patch.object(PreCommitGuard, 'get_file_content')
    def test_complete_scanning_workflow(self, mock_get_content, mock_get_files):
        """Test complete scanning workflow with mixed content"""
        mock_get_files.return_value = ["app.py", "config.json", "test.py"]
        
        file_contents = {
            "app.py": '''
import os
# This is fine
database_url = os.getenv("DATABASE_URL")
            ''',
            "config.json": '''
{
    "api_key": "AKIATEST123456789012",
    "secret": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYREALKEY"
}
            ''',
            "test.py": '''
# Test file with mock data
mock_key = "sk-abcdef1234567890abcdef1234567890abcdef1234"
            '''
        }
        
        def get_content_side_effect(filepath, staged=True):
            return file_contents.get(filepath, "")
        
        mock_get_content.side_effect = get_content_side_effect
        
        guard = PreCommitGuard()
        violations = guard.scan_staged_files()
        
        assert len(violations) >= 1
        
        files_with_violations = {v['file'] for v in violations}
        assert len(files_with_violations) >= 1
        
        for violation in violations:
            assert violation['file'] in ["config.json", "test.py"]
            assert violation['line'] > 0
            assert len(violation['token']) > 0


if __name__ == "__main__":
    
    pytest.main([__file__, "-v"])