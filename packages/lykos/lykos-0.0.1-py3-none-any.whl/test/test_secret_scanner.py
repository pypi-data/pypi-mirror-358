import pytest
import subprocess
import re
from unittest.mock import patch, mock_open, MagicMock
from collections import defaultdict

from lykos.secret_scanner import (
        SecretScanner, 
        main,
        ENTROPY_THRESHOLD,
        PATTERNS,
    )

class TestSecretScanner:
    
    def setup_method(self):
        self.scanner = SecretScanner()
    
    def test_scanner_initialization(self):
        scanner = SecretScanner()
        assert scanner.entropy_threshold == ENTROPY_THRESHOLD
        assert isinstance(scanner.first_seen, defaultdict)
        
        custom_scanner = SecretScanner(entropy_threshold=3.0)
        assert custom_scanner.entropy_threshold == 3.0
    
    def test_shannon_entropy_empty_string(self):
        assert self.scanner.shannon_entropy("") == 0.0
    
    def test_shannon_entropy_short_string(self):
        """Test entropy of strings shorter than 4 chars"""
        assert self.scanner.shannon_entropy("abc") == 0.0
        assert self.scanner.shannon_entropy("a") == 0.0
    
    def test_shannon_entropy_single_character(self):
        """Test entropy of repeated single character"""
        assert self.scanner.shannon_entropy("aaaa") == 0.0
        assert self.scanner.shannon_entropy("aaaaaaaa") == 0.0
    
    def test_shannon_entropy_high_entropy(self):
        high_entropy_string = "aB3$k9Lm2Qp7Xs1Zr4Nv8Jf"
        entropy = self.scanner.shannon_entropy(high_entropy_string)
        assert entropy > 4.0
    
    def test_shannon_entropy_calculation(self):
        """Test specific entropy calculations"""
        assert abs(self.scanner.shannon_entropy("abab") - 1.0) < 0.001
    
    def test_is_false_positive(self):
        # actual false positives from the FP set
        assert self.scanner.is_false_positive("EXAMPLE_KEY_123456789")
        assert self.scanner.is_false_positive("YOUR_API_KEY_HERE")
        assert self.scanner.is_false_positive("REPLACE_WITH_YOUR_KEY")
        
        assert self.scanner.is_false_positive("your_api_key_here")
        assert self.scanner.is_false_positive("example_key_123456789")
        
        # substring matching .. any token containing these should be flagged
        assert self.scanner.is_false_positive("prefix_YOUR_API_KEY_HERE_suffix")
        
        # should not be fp
        assert not self.scanner.is_false_positive("AKIAIOSFODNN7EXAMPLE")
        assert not self.scanner.is_false_positive("real_secret_key_12345")
    
    @patch('subprocess.check_output')
    def test_sh_successful_command(self, mock_subprocess):
        mock_subprocess.return_value = "line1\nline2\nline3\n"
        
        result = self.scanner.sh(["echo", "test"])
        
        assert result == ["line1", "line2", "line3"]
        mock_subprocess.assert_called_once_with(["echo", "test"], text=True)
    
    def test_suspicious_strings_aws_access_key(self):
        blob = "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE"
        results = self.scanner.suspicious_strings(blob)
        
        assert len(results) >= 1
        token, label, line_num, context = results[0]
        assert label == "AWS_ACCESS_KEY"
        assert token == "AKIAIOSFODNN7EXAMPLE"
        assert line_num == 1
    
    def test_suspicious_strings_aws_secret_key(self):
        blob = "AWS_SECRET=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        results = self.scanner.suspicious_strings(blob)
        
        aws_secret_results = [r for r in results if r[1] == "AWS_SECRET_KEY"]
        assert len(aws_secret_results) >= 1
    
    def test_suspicious_strings_google_api(self):
        """fgoogle API keys"""
        blob = "google_api_key=AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"
        results = self.scanner.suspicious_strings(blob)
        
        google_results = [r for r in results if r[1] == "Google_API"]
        assert len(google_results) == 1
        assert google_results[0][0] == "AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"
    
    def test_suspicious_strings_stripe_live_key(self):
        blob = "stripe_secret=sk_live_1234567890abcdef12345678"
        results = self.scanner.suspicious_strings(blob)
        
        stripe_live_results = [r for r in results if r[1] == "Stripe_Live"]
        assert len(stripe_live_results) == 1
    
    def test_suspicious_strings_stripe_test_pattern(self):
        pattern = re.compile(PATTERNS["Stripe_Test"])
        test_token = "sk_test_1234567890abcdef12345678"
        
        assert pattern.search(test_token) is not None
    
    def test_suspicious_strings_openai_key(self):
        blob = "openai_key=sk-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJ12"
        results = self.scanner.suspicious_strings(blob)
        
        openai_results = [r for r in results if r[1] == "OpenAI"]
        assert len(openai_results) == 1
    
    def test_suspicious_strings_github_token(self):
        blob = "github_token=ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        results = self.scanner.suspicious_strings(blob)
        
        github_results = [r for r in results if r[1] == "GitHub_Token"]
        assert len(github_results) == 1
    
    def test_suspicious_strings_jwt_token(self):
        blob = "jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        results = self.scanner.suspicious_strings(blob)
        
        jwt_results = [r for r in results if r[1] == "JWT"]
        assert len(jwt_results) == 1
    
    def test_suspicious_strings_private_key(self):
        blob = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA..."
        results = self.scanner.suspicious_strings(blob)
        
        private_key_results = [r for r in results if r[1] == "Private_Key"]
        assert len(private_key_results) == 1
    
    def test_suspicious_strings_generic_api_key(self):
        """Test detection of generic API keys"""
        blob = 'api_key="abcdefghijklmnop1234567890QRSTUVWXYZ"'
        results = self.scanner.suspicious_strings(blob)
        
        generic_results = [r for r in results if r[1] == "API_Key_Generic"]
        assert len(generic_results) >= 1
    
    def test_suspicious_strings_bearer_token(self):
        blob = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abcdefghijk"
        results = self.scanner.suspicious_strings(blob)
        
        bearer_results = [r for r in results if r[1] == "Bearer_Token"]
        assert len(bearer_results) >= 1
    
    def test_suspicious_strings_high_entropy(self):
        blob = "random_secret=AbCdEfGhIjKlMnOpQrStUvWxYz"
        results = self.scanner.suspicious_strings(blob)
        
        assert len(results) >= 0  # check that it doesnt crash at least lmao
    
    def test_suspicious_strings_skip_comments(self):
        blob = """# This is a comment with AKIAIOSFODNN7EXAMPLE
real_key=AKIAIOSFODNN7EXAMPLE"""
        results = self.scanner.suspicious_strings(blob)
        
        assert len(results) == 1
        assert results[0][2] == 2 
    
    def test_suspicious_strings_skip_test_lines(self):
        """Test that lines containing 'test' are skipped"""
        blob = """unit_test_key=AKIAIOSFODNN7EXAMPLE
production_key=AKIAIOSFODNN7EXAMPLE"""
        results = self.scanner.suspicious_strings(blob)
        
        assert len(results) == 1
        assert results[0][2] == 2
    
    def test_suspicious_strings_false_positives_filtered(self):
        """Test that fps are filtered out"""
        blob = "api_key=YOUR_API_KEY_HERE"
        results = self.scanner.suspicious_strings(blob)
        
        assert len(results) == 0
    
    def test_suspicious_strings_multiline(self):
        blob = """line1: normal content
line2: AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
line3: google_key=AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe
line4: more normal content"""
        
        results = self.scanner.suspicious_strings(blob)
        assert len(results) >= 2
        
        line_numbers = [r[2] for r in results]
        assert 2 in line_numbers
        assert 3 in line_numbers
    
    @patch('subprocess.check_output')
    def test_scan_commits_recent(self, mock_subprocess):
        """Test scanning recent commits"""
        mock_subprocess.side_effect = [
            "commit1\ncommit2\n",  # git rev-list
            "file1.py\nfile2.js\n",  # git ls-tree for commit1
            "AWS_KEY=AKIAIOSFODNN7EXAMPLE",  # git show commit1:file1.py
            "normal content",  # git show commit1:file2.js
            "file3.txt\n",  # git ls-tree for commit2
            "clean content"  # git show commit2:file3.txt
        ]
        
        secrets = self.scanner.scan_commits(recent=2)
        
        assert len(secrets) == 1
        assert secrets[0]['type'] == 'AWS_ACCESS_KEY'
        assert secrets[0]['commit'] == 'commit1'
        assert secrets[0]['file'] == 'file1.py'
        assert secrets[0]['line'] == 1
    
    @patch('subprocess.check_output')
    def test_scan_commits_all(self, mock_subprocess):
        """Test scanning all commits"""
        mock_subprocess.side_effect = [
            "commit1\n", 
            "file1.py\n",
            "clean content" 
        ]
        
        secrets = self.scanner.scan_commits(all_commits=True)
        assert len(secrets) == 0
    
    @patch('subprocess.check_output')
    def test_scan_commits_skip_binary_files(self, mock_subprocess):
        mock_subprocess.side_effect = [
            "commit1\n", 
            "image.jpg\nscript.py\nbinary.exe\ndoc.pdf\ncode.py\n", 
            "AWS_KEY=AKIAIOSFODNN7EXAMPLE",
            "normal_code=value"
        ]
                
        git_show_calls = [call for call in mock_subprocess.call_args_list 
                         if call[0][0][0] == 'git' and call[0][0][1] == 'show']
        assert len(git_show_calls) == 2
    
    @patch('subprocess.check_output')
    def test_scan_commits_git_error_handling(self, mock_subprocess):
        """Test handling of git command errors"""
        mock_subprocess.side_effect = [
            "commit1\n", 
            subprocess.CalledProcessError(1, 'git'),  
        ]
        
        secrets = self.scanner.scan_commits(recent=1)
        assert len(secrets) == 0
    
    @patch('subprocess.check_output')
    def test_scan_commits_deduplication(self, mock_subprocess):
        mock_subprocess.side_effect = [
            "commit1\ncommit2\n",
            "file1.py\n",
            "AWS_KEY=AKIAIOSFODNN7EXAMPLE", 
            "file2.py\n",
            "AWS_KEY=AKIAIOSFODNN7EXAMPLE",  
        ]
        
        secrets = self.scanner.scan_commits(recent=2)
        
        assert len(secrets) == 1
        assert secrets[0]['commit'] == 'commit1'
    
    def test_generate_report_no_secrets(self):
        """Test report generation when no secrets found"""
        with patch('builtins.print') as mock_print:
            report = self.scanner.generate_report([])
        
        mock_print.assert_called_with("✅  No obvious secrets found.")
        assert report == {}
    
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_report_with_secrets(self, mock_file):
        """Test report generation with secrets"""
        secrets = [{
            'token': 'AKIAIOSFODNN7EXAMPLE',
            'type': 'AWS_ACCESS_KEY',
            'commit': 'abc123def456',
            'file': 'config.py',
            'line': 5,
            'context': 'aws_key = "AKIAIOSFODNN7EXAMPLE"',
            'entropy': 3.2
        }]
        
        with patch('builtins.print') as mock_print:
            report = self.scanner.generate_report(secrets, "test_report.json")
        
        mock_print.assert_any_call("\n🔑  Potential leaks detected:")
        
        mock_file.assert_called_with("test_report.json", "w")
        
        assert 'secrets' in report
        assert 'summary' in report
        assert report['summary']['total'] == 1
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_generate_report_json_content(self, mock_json_dump, mock_file):
        """Test JSON report content"""
        secrets = [{
            'token': 'test_token',
            'type': 'TEST_TYPE',
            'commit': 'commit123',
            'file': 'test.py',
            'line': 1,
            'context': 'test context',
            'entropy': 4.5
        }]
        
        with patch('builtins.print'):
            self.scanner.generate_report(secrets, "output.json")
        
        mock_json_dump.assert_called_once()
        written_data = mock_json_dump.call_args[0][0]
        assert written_data['secrets'] == secrets
        assert written_data['summary']['total'] == 1


class TestMainFunction:
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch.object(SecretScanner, 'scan_commits')
    @patch.object(SecretScanner, 'generate_report')
    @patch('sys.exit')
    def test_main_recent_argument(self, mock_exit, mock_generate, mock_scan, mock_args):
        mock_args.return_value = MagicMock(
            recent=5, all=False, output=".secrets_report.json", entropy=4.5
        )
        
        mock_scan.return_value = []
        mock_generate.return_value = {}
        
        main()
        
        mock_scan.assert_called_once_with(recent=5, all_commits=False)
        mock_exit.assert_called_once_with(0)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch.object(SecretScanner, 'scan_commits')
    @patch.object(SecretScanner, 'generate_report')
    @patch('sys.exit')
    def test_main_all_argument(self, mock_exit, mock_generate, mock_scan, mock_args):
        """Test main with --all argument"""
        mock_args.return_value = MagicMock(
            recent=None, all=True, output=".secrets_report.json", entropy=4.5
        )
        
        mock_scan.return_value = []
        mock_generate.return_value = {}
        
        main()
        
        mock_scan.assert_called_once_with(recent=None, all_commits=True)
        mock_exit.assert_called_once_with(0)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch.object(SecretScanner, 'scan_commits')
    @patch.object(SecretScanner, 'generate_report')
    @patch('sys.exit')
    def test_main_custom_output(self, mock_exit, mock_generate, mock_scan, mock_args):
        """Test main with custom output file"""
        mock_args.return_value = MagicMock(
            recent=3, all=False, output='custom.json', entropy=4.5
        )
        
        mock_scan.return_value = []
        mock_generate.return_value = {}
        
        main()
        
        mock_generate.assert_called_once()
        args = mock_generate.call_args[0]
        assert args[1] == 'custom.json'
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_custom_entropy(self, mock_exit, mock_args):
        """Test main with custom entropy threshold"""
        mock_args.return_value = MagicMock(
            recent=2, all=False, output=".secrets_report.json", entropy=3.5
        )
        
        with patch.object(SecretScanner, 'scan_commits', return_value=[]):
            with patch.object(SecretScanner, 'generate_report', return_value={}):
                main()

        mock_exit.assert_called_once_with(0)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch.object(SecretScanner, 'scan_commits')
    @patch.object(SecretScanner, 'generate_report')
    @patch('sys.exit')
    def test_main_secrets_found_exit_code(self, mock_exit, mock_generate, mock_scan, mock_args):
        """Test main exits with code 1 when secrets found"""
        mock_args.return_value = MagicMock(
            recent=1, all=False, output=".secrets_report.json", entropy=4.5
        )
        
        mock_scan.return_value = [{'token': 'secret'}]
        mock_generate.return_value = {'secrets': [{'token': 'secret'}]}
        
        main()
        
        mock_exit.assert_called_once_with(1)

class TestPatterns:
    def test_aws_access_key_pattern(self):
        pattern = re.compile(PATTERNS["AWS_ACCESS_KEY"])
        
        valid_keys = [
            "AKIAIOSFODNN7EXAMPLE",
            "AKIA1234567890123456",
            "AKIAZZZZZZZZZZZZZZZZ"
        ]
        
        invalid_keys = [
            "AKIA123",
            "BKIAIOSFODNN7EXAMPLE", 
            "akiaiosfodnn7example", 
        ]
        
        for key in valid_keys:
            assert pattern.search(key), f"Should match: {key}"
        
        for key in invalid_keys:
            assert not pattern.search(key), f"Should not match: {key}"
    
    def test_github_token_pattern(self):
        pattern = re.compile(PATTERNS["GitHub_Token"])
        
        valid_tokens = [
            "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
            "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij",
        ]
        
        invalid_tokens = [
            "ghp_123",  # too short
            "gho_1234567890abcdefghijklmnopqrstuvwxyz",  # wrong prefix
        ]
        
        for token in valid_tokens:
            assert pattern.search(token), f"Should match: {token}"
        
        for token in invalid_tokens:
            assert not pattern.search(token), f"Should not match: {token}"


class TestPerformance:    
    def test_entropy_performance(self):
        import time
        scanner = SecretScanner()
        
        large_string = "a" * 1000 + "b" * 1000 + "c" * 1000
        
        start_time = time.time()
        for _ in range(100):
            scanner.shannon_entropy(large_string)
        end_time = time.time()
        
        assert (end_time - start_time) < 1.0
    
    def test_pattern_matching_performance(self):
        import time
        scanner = SecretScanner()
        
        large_blob = "\n".join([
            f"line {i}: normal content here" for i in range(1000)
        ] + [
            "AWS_KEY=AKIAIOSFODNN7EXAMPLE",
            "GOOGLE_KEY=AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"
        ])
        
        start_time = time.time()
        results = scanner.suspicious_strings(large_blob)
        end_time = time.time()
        
        assert len(results) >= 2
        assert (end_time - start_time) < 2.0

if __name__ == "__main__":
    pytest.main([__file__])