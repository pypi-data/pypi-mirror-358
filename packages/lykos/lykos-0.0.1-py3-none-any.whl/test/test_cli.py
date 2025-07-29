import pytest
import json
from unittest.mock import patch, mock_open, MagicMock, call
from pathlib import Path

from lykos.cli import main, cmd_scan, cmd_clean, cmd_guard, cmd_protect, cmd_status, create_parser

class TestlykosMainCLI:

    def setup_method(self):
        self.sample_secrets = [
            {
                'token': 'AKIATEST123456789012',
                'type': 'AWS_ACCESS_KEY',
                'commit': 'abc123',
                'file': 'config.py',
                'line': 10
            }
        ]
        self.sample_report = {
            'scan_date': '2024-01-15T10:30:00Z',
            'repository': 'test-repo',
            'secrets': self.sample_secrets
        }

    def test_main_help_display(self):
        with patch('sys.argv', ['lykos']), \
             patch('builtins.print') as mock_print:
            
            result = main()
            assert result == 0
            
    def test_cmd_scan_all_commits(self):
        args = MagicMock()
        args.all = True
        args.recent = None
        args.entropy = 4.5
        args.output = '.secrets_report.json'
        
        with patch('lykos.cli.SecretScanner') as mock_scanner_class, \
            patch('builtins.print') as mock_print:
            
            mock_scanner = MagicMock()
            mock_scanner.scan_commits.return_value = self.sample_secrets
            mock_scanner.generate_report.return_value = self.sample_report
            mock_scanner_class.return_value = mock_scanner
            
            result = cmd_scan(args)
            
            assert result == 1
            
            mock_scanner_class.assert_called_once_with(entropy_threshold=4.5)
            mock_scanner.scan_commits.assert_called_once_with(all_commits=True)
            mock_scanner.generate_report.assert_called_once_with(self.sample_secrets, '.secrets_report.json')

    def test_cmd_scan_recent_commits(self):
        """lykos scan --recent 50"""
        args = MagicMock()
        args.all = False
        args.recent = 50
        args.entropy = 4.5
        args.output = '.secrets_report.json'
        
        with patch('lykos.cli.SecretScanner') as mock_scanner_class:
            
            mock_scanner = MagicMock()
            mock_scanner.scan_commits.return_value = []
            mock_scanner.generate_report.return_value = {'secrets': []}
            mock_scanner_class.return_value = mock_scanner
            
            result = cmd_scan(args)
            
            assert result == 0
            
            mock_scanner.scan_commits.assert_called_once_with(recent=50)

    def test_cmd_clean_success(self):
        """lykos clean --force"""
        args = MagicMock()
        args.dry_run = False
        args.report = '.secrets_report.json'
        args.force = True
        
        with patch('lykos.cli.HistoryCleaner') as mock_cleaner_class, \
             patch('builtins.print') as mock_print:
            
            mock_cleaner = MagicMock()
            mock_cleaner.check_dependencies.return_value = True
            mock_cleaner.check_repo_status.return_value = True
            mock_cleaner.load_secrets_report.return_value = self.sample_secrets
            mock_cleaner.clean_history.return_value = True
            mock_cleaner_class.return_value = mock_cleaner
            
            result = cmd_clean(args)
            
            assert result == 0
            
            mock_cleaner.check_dependencies.assert_called_once()
            mock_cleaner.check_repo_status.assert_called_once()
            mock_cleaner.load_secrets_report.assert_called_once_with('.secrets_report.json')
            mock_cleaner.clean_history.assert_called_once_with(self.sample_secrets, force=True)
            
            printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
            assert any("Cleaning secrets" in msg for msg in printed_messages)

    def test_cmd_clean_missing_dependencies(self):
        args = MagicMock()
        args.dry_run = False
        args.report = '.secrets_report.json'
        args.force = False
        
        with patch('lykos.cli.HistoryCleaner') as mock_cleaner_class:
            
            mock_cleaner = MagicMock()
            mock_cleaner.check_dependencies.return_value = False
            mock_cleaner_class.return_value = mock_cleaner
            
            result = cmd_clean(args)
            
            assert result == 1
            
            mock_cleaner.check_dependencies.assert_called_once()
            mock_cleaner.check_repo_status.assert_not_called()

    def test_cmd_guard_install(self):
        args = MagicMock()
        args.install = True
        args.check_staged = False
        args.check_files = None
        args.check_dir = None
        args.entropy = 4.5
        args.strict = False
        
        with patch('lykos.cli.PreCommitGuard') as mock_guard_class, \
             patch('builtins.print') as mock_print:
            
            mock_guard = MagicMock()
            mock_guard.install_git_hook.return_value = True
            mock_guard_class.return_value = mock_guard
            
            result = cmd_guard(args)
            
            assert result == 0
            
            mock_guard_class.assert_called_once_with(entropy_threshold=4.5, strict_mode=False)
            mock_guard.install_git_hook.assert_called_once()
            
            printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
            assert any("Installing pre-commit hook" in msg for msg in printed_messages)

    def test_cmd_guard_check_staged(self):
        """lykos guard --check-staged"""
        args = MagicMock()
        args.install = False
        args.check_staged = True
        args.check_files = None
        args.check_dir = None
        args.entropy = 4.5
        args.strict = False
        
        with patch('lykos.cli.PreCommitGuard') as mock_guard_class:
            
            mock_guard = MagicMock()
            mock_guard.scan_staged_files.return_value = []
            mock_guard.report_violations.return_value = True
            mock_guard_class.return_value = mock_guard
            
            result = cmd_guard(args)
            
            assert result == 0
            
            mock_guard.scan_staged_files.assert_called_once()
            mock_guard.report_violations.assert_called_once_with([])

    def test_cmd_guard_check_files(self):
        """lykos guard --check-files file1.py file2.py"""
        args = MagicMock()
        args.install = False
        args.check_staged = False
        args.check_files = ['file1.py', 'file2.py']
        args.check_dir = None
        args.entropy = 4.5
        args.strict = True
        
        with patch('lykos.cli.PreCommitGuard') as mock_guard_class, \
             patch('builtins.print') as mock_print:
            
            mock_guard = MagicMock()
            mock_guard.scan_files.return_value = [{'type': 'AWS_ACCESS_KEY'}]
            mock_guard.report_violations.return_value = False
            mock_guard_class.return_value = mock_guard
            
            result = cmd_guard(args)
            
            assert result == 1
            
            mock_guard.scan_files.assert_called_once_with(['file1.py', 'file2.py'])
            
            printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
            assert any("Checking 2 files" in msg for msg in printed_messages)

    def test_cmd_guard_check_dir(self):
        args = MagicMock()
        args.install = False
        args.check_staged = False
        args.check_files = None
        args.check_dir = 'src/'
        args.entropy = 4.5
        args.strict = False
        
        with patch('lykos.cli.PreCommitGuard') as mock_guard_class, \
             patch('pathlib.Path.glob') as mock_glob, \
             patch('builtins.print') as mock_print:
            
            mock_glob.return_value = [Path('src/cli.py'), Path('src/config.py')]
            
            mock_guard = MagicMock()
            mock_guard.scan_files.return_value = []
            mock_guard.report_violations.return_value = True
            mock_guard_class.return_value = mock_guard
            
            result = cmd_guard(args)
            
            assert result == 0
            
            mock_guard.scan_files.assert_called_once_with(['src/cli.py', 'src/config.py'])
            
            printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
            assert any("Checking directory: src/" in msg for msg in printed_messages)

    def test_cmd_protect_success(self):
        """lykos protect --recent 100 --force"""
        args = MagicMock()
        args.recent = 100
        args.dry_run = False
        args.force = True
        args.report = '.secrets_report.json'
        
        with patch('lykos.cli.SecretGuardian') as mock_guardian_class, \
             patch('builtins.print') as mock_print:
            
            mock_guardian = MagicMock()
            mock_guardian.check_git_repo.return_value = True
            mock_guardian.full_scan_and_clean.return_value = True
            mock_guardian_class.return_value = mock_guardian
            
            result = cmd_protect(args)
            
            assert result == 0
            
            assert mock_guardian.report_file == '.secrets_report.json'
            
            mock_guardian.check_git_repo.assert_called_once()
            mock_guardian.full_scan_and_clean.assert_called_once_with(
                recent_commits=100,
                dry_run=False,
                force=True
            )
            
            printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
            assert any("complete protection workflow" in msg for msg in printed_messages)

    def test_cmd_protect_not_git_repo(self):
        args = MagicMock()
        args.recent = None
        args.dry_run = False
        args.force = False
        args.report = '.secrets_report.json'
        
        with patch('lykos.cli.SecretGuardian') as mock_guardian_class:
            
            mock_guardian = MagicMock()
            mock_guardian.check_git_repo.return_value = False
            mock_guardian_class.return_value = mock_guardian
            
            result = cmd_protect(args)
            
            assert result == 1
            
            mock_guardian.full_scan_and_clean.assert_not_called()

    def test_cmd_status_full_display(self):
        args = MagicMock()
        
        with patch('lykos.cli.SecretGuardian') as mock_guardian_class, \
            patch('lykos.cli.PreCommitGuard') as mock_guard_class, \
            patch('pathlib.Path.exists') as mock_exists, \
            patch('builtins.open', mock_open(read_data=json.dumps(self.sample_report))), \
            patch('pathlib.Path.glob') as mock_glob, \
            patch('builtins.print') as mock_print:
            
            mock_guardian = MagicMock()
            mock_guardian.check_git_repo.return_value = True
            mock_guardian.get_repo_info.return_value = {
                'branch': 'main',
                'commit_count': 250,
                'remote': 'https://github.com/team/project.git'
            }
            mock_guardian_class.return_value = mock_guardian
            
            mock_guard = MagicMock()
            mock_guard.scan_files.return_value = []
            mock_guard_class.return_value = mock_guard
            
            mock_exists.return_value = True
            mock_glob.return_value = [Path('main.py'), Path('config.py')]
            
            result = cmd_status(args)
            
            assert result == 0

    def test_main_full_integration(self):
        
        with patch('sys.argv', ['lykos', 'scan', '--recent', '25', '--entropy', '5.0']), \
            patch('lykos.cli.SecretScanner') as mock_scanner_class:
            
            mock_scanner = MagicMock()
            mock_scanner.scan_commits.return_value = []
            mock_scanner.generate_report.return_value = {'secrets': []}
            mock_scanner_class.return_value = mock_scanner
            
            result = main()
            
            assert result == 0
            mock_scanner_class.assert_called_once_with(entropy_threshold=5.0)
            mock_scanner.scan_commits.assert_called_once_with(recent=25)

    def test_main_keyboard_interrupt(self):
        with patch('sys.argv', ['lykos', 'scan', '--all']), \
             patch('lykos.cli.SecretScanner') as mock_scanner_class, \
             patch('builtins.print') as mock_print:
            
            mock_scanner_class.side_effect = KeyboardInterrupt()
            result = main()
            assert result == 1   
                        
            printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
            assert any("cancelled by user" in msg.lower() for msg in printed_messages)

    def test_main_unexpected_exception(self):
        with patch('sys.argv', ['lykos', 'scan', '--all']), \
             patch('lykos.cli.SecretScanner') as mock_scanner_class, \
             patch('builtins.print') as mock_print:
            
            mock_scanner_class.side_effect = Exception("Something went wrong")
            result = main()
            assert result == 1
            
            printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
            assert any("Unexpected error" in msg for msg in printed_messages)

    def test_parser_structure(self):
        parser = create_parser()
        
        subparsers = parser._subparsers._group_actions[0]
        subcommand_names = list(subparsers.choices.keys())
        
        expected_commands = ['scan', 'clean', 'guard', 'protect', 'status']
        for cmd in expected_commands:
            assert cmd in subcommand_names
        
        scan_parser = subparsers.choices['scan']
        scan_help = scan_parser.format_help()
        assert '--all' in scan_help
        assert '--recent' in scan_help
        assert '--entropy' in scan_help
        
        guard_parser = subparsers.choices['guard']
        guard_help = guard_parser.format_help()
        assert '--install' in guard_help
        assert '--check-staged' in guard_help
        assert '--check-files' in guard_help
        assert '--check-dir' in guard_help


if __name__ == "__main__":    
    pytest.main([__file__, "-v", "--tb=short"])