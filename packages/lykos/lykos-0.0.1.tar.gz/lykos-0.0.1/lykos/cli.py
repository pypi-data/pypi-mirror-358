import argparse
import sys
from pathlib import Path

from lykos.secret_scanner import SecretScanner
from lykos.pre_commit_guard import PreCommitGuard
from lykos.secret_guardian import SecretGuardian
from lykos.git_secrets_cleaner import GitSecretsCleaner

def create_parser():
    parser = argparse.ArgumentParser(
        prog='lykos',
        description='Lykos - Yet another Git secret management toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
E.g.:
  lykos scan --all --confidence MEDIUM     
  lykos scan --recent 50 --confidence HIGH     
  lykos scan --branch main --confidence HIGH  
  lykos guard --install --confidence HIGH
  lykos guard --check-staged --confidence MEDIUM
  lykos protect --recent 100 --confidence HIGH
        '''
    )
    
    parser.add_argument('--version', action='version', version='Secret Guardian 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    ## scan
    scan_parser = subparsers.add_parser(
        'scan', 
        help='Scan git history for secrets',
        description='Scan git repository for potential secrets using patterns and entropy analysis'
    )
    scan_group = scan_parser.add_mutually_exclusive_group(required=True)
    scan_group.add_argument('--all', action='store_true', help='Scan all commits across all branches')
    scan_group.add_argument('--recent', type=int, metavar='N', help='Scan last N commits on current branch')
    scan_group.add_argument('--branch', metavar='BRANCH', help='Scan all commits on specific branch (without switching)')
    
    scan_parser.add_argument('--output', '-o', default='.secrets_report.json', 
                           help='Output JSON file (default: .secrets_report.json)')
    scan_parser.add_argument('--entropy', type=float, default=4.5,
                           help='Entropy threshold for detection (default: 4.5)')
    scan_parser.add_argument('--confidence', choices=['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW'], 
                           default='LOW', help='Minimum confidence level to report (default: LOW)')

    scan_parser.add_argument('--save-report', action='store_true',
                       help='Save detailed report to file (default: interactive mode)')

    # guard
    guard_parser = subparsers.add_parser(
        'guard', 
        help='Prevent secrets in future commits',
        description='Install and manage pre-commit hooks to prevent secrets'
    )
    guard_group = guard_parser.add_mutually_exclusive_group(required=True)
    guard_group.add_argument('--install', action='store_true', 
                           help='Install pre-commit hook')
    guard_group.add_argument('--check-staged', action='store_true',
                           help='Check staged files for secrets')
    guard_group.add_argument('--check-files', nargs='+', metavar='FILE',
                           help='Check specific files for secrets')
    guard_group.add_argument('--check-dir', metavar='DIR', 
                           help='Check directory for secrets')
    guard_parser.add_argument('--strict', action='store_true',
                            help='Strict mode (block commits for any violation)')
    guard_parser.add_argument('--entropy', type=float, default=4.5,
                            help='Entropy threshold (default: 4.5)')
    guard_parser.add_argument('--confidence', choices=['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW'], 
                            default='MEDIUM', help='Minimum confidence level to block commits (default: MEDIUM)')

    # clean
    clean_parser = subparsers.add_parser(
        'clean',
        help='Clean git history of secrets',
        description='Remove secrets from git history using git-filter-repo'
    )

    clean_parser.add_argument('--scope',
    choices=['head', 'all'],
    default='head',
    help='default: current branch only'
    )
    
    clean_parser.add_argument('--replace',
    action='append',
    metavar='OLD==NEW',
    )

    clean_parser.add_argument('--confidence',
    choices=['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW'],
    default='MEDIUM', help='Minimum confidence of scanner hits to clean'
    )

    # protect
    protect_parser = subparsers.add_parser(
        'protect',
        help='Complete protection workflow',
        description='Scans for secrets, clean history, and setup protection'
    )
    protect_parser.add_argument('--recent', type=int, metavar='N',
                              help='Only scans last n commits (default: all commits)')
    protect_parser.add_argument('--dry-run', action='store_true',
                              help='Show what would be done without executing')
    protect_parser.add_argument('--report', default='.secrets_report.json',
                              help='Path to secrets report file')
    protect_parser.add_argument('--confidence', choices=['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW'], 
                              default='MEDIUM', help='Minimum confidence level for operations (default: MEDIUM)')
    
    return parser

def cmd_scan(args):
    print("Scanning repository for secrets...")
    
    scanner = SecretScanner(entropy_threshold=args.entropy)
    
    if args.all:
        secrets = scanner.scan_commits(all_commits=True, min_confidence=args.confidence)
    elif args.recent:
        secrets = scanner.scan_commits(recent=args.recent, min_confidence=args.confidence)
    elif args.branch:
        secrets = scanner.scan_commits(target_branch=args.branch, min_confidence=args.confidence)
    
    if not getattr(args, 'save_report', False):
        scanner.show_interactive_summary(secrets, args.confidence)
        return 0
    else:
        report = scanner.generate_report(secrets, args.output)
        if secrets:
            high_confidence_secrets = [s for s in secrets if s['confidence']['level'] == 'HIGH']
            return 2 if high_confidence_secrets else 1
        return 0

def cmd_guard(args):
    guard = PreCommitGuard(
        entropy_threshold=args.entropy,
        strict_mode=args.strict,
        min_confidence=args.confidence
    )
    
    if args.install:
        print("Installing pre-commit hook...")
        success = guard.install_git_hook()
        return 0 if success else 1
        
    elif args.check_staged:
        print("Checking staged files...")
        violations = guard.scan_staged_files()
        clean = guard.report_violations(violations)
        
        if violations:
            high_confidence_violations = [v for v in violations if v['confidence']['level'] == 'HIGH']
            if high_confidence_violations:
                return 2
            elif not clean:
                return 1
            else:
                return 0  # warning only
        else:
            return 0  # no violations
        
    elif args.check_files:
        print(f"Checking {len(args.check_files)} files...")
        violations = guard.scan_files(args.check_files)
        clean = guard.report_violations(violations)
        
        if violations:
            high_confidence_violations = [v for v in violations if v['confidence']['level'] == 'HIGH']
            if high_confidence_violations:
                return 2
            elif not clean:
                return 1
            else:
                return 0
        else:
            return 0
        
    elif args.check_dir:
        print(f"Checking directory: {args.check_dir}")
        py_files = list(Path(args.check_dir).glob("**/*.py"))
        violations = guard.scan_files([str(f) for f in py_files])
        clean = guard.report_violations(violations)
        
        if violations:
            high_confidence_violations = [v for v in violations if v['confidence']['level'] == 'HIGH']
            if high_confidence_violations:
                return 2
            elif not clean:
                return 1
            else:
                return 0
        else:
            return 0

def cmd_protect(args):
    print("Starting complete protection workflow...")
    
    guardian = SecretGuardian()
    guardian.report_file = args.report
    
    if not guardian.check_git_repo():
        return 1
    
    success = guardian.full_scan_and_clean(
        recent_commits=args.recent,
        dry_run=args.dry_run,
        min_confidence=args.confidence
    )
    
    return 0 if success else 1

def cmd_clean(args):
    scanner = SecretScanner()
    auto_hits = scanner.scan_commits(
        all_commits=(args.scope == 'all'),
        min_confidence=args.confidence
    )

    manual = {}
    if args.replace:
        for pair in args.replace:
            if '==' not in pair:
                raise SystemExit('--replace must be OLD==NEW')
            old, new = pair.split('==', 1)
            manual[old] = new

    cleaner = GitSecretsCleaner(dry_run=False)
    ok = cleaner.clean_history_completely(auto_hits, min_confidence=args.confidence, extra_replacements=manual)
    return 0 if ok else 1

def cmd_status(args):
    print("Repo Security Status")
    print("=" * 40)
    
    guardian = SecretGuardian()
    
    if not guardian.check_git_repo():
        print("Not in a git repository")
        return 1
    
    repo_info = guardian.get_repo_info()
    if repo_info:
        print(f"Branch: {repo_info['branch']}")
        print(f"Commits: {repo_info['commit_count']}")
        print(f"Remote: {repo_info['remote']}")
    
    hook_path = Path(".git/hooks/pre-commit")
    if hook_path.exists():
        print("Pre-commit hook: Installed")
    else:
        print("Pre-commit hook: Not installed")
        print("Run: lykos guard --install")
    
    report_path = Path(".secrets_report.json")
    if report_path.exists():
        try:
            import json
            with open(report_path) as f:
                report = json.load(f)
            secrets = report.get('secrets', [])
            secret_count = len(secrets)
            print(f"Last scan: {secret_count} secrets found")
            
            if secret_count > 0:
                from collections import defaultdict
                by_confidence = defaultdict(int)
                for secret in secrets:
                    if 'confidence' in secret:
                        confidence_level = secret['confidence']['level']
                        by_confidence[confidence_level] += 1
                
                print("Confidence breakdown:")
                for level in ['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW']:
                    count = by_confidence[level]
                    if count > 0:
                        print(f"   {level}: {count}")
                
                high_count = by_confidence['HIGH']
                if high_count > 0:
                    print(f"URGENT: {high_count} HIGH confidence secrets need immediate attention!")
                    print("Run: lykos clean --confidence HIGH")
                else:
                    print("Run: lykos clean")
        except:
            print("Last scan: Report file corrupted")
    else:
        print("Last scan: No report found")
        print("Run: lykos scan --recent 50")
    
    print("\nQuick scan of current directory...")
    guard = PreCommitGuard(min_confidence="HIGH")
    py_files = list(Path(".").glob("*.py"))[:5]
    if py_files:
        violations = guard.scan_files([str(f) for f in py_files])
        if violations:
            high_confidence_violations = [v for v in violations if v['confidence']['level'] == 'HIGH']
            if high_confidence_violations:
                print(f"WARNING: {len(high_confidence_violations)} HIGH confidence secrets in current files")
            else:
                print(f"Found {len(violations)} potential secrets (low confidence)")
        else:
            print("No obvious secrets in current Python files")
    
    print("\nRecommendations:")
    print("1. Run full scan: lykos scan --all")
    print("2. Install protection: lykos guard --install --confidence HIGH") 
    print("3. Clean high-confidence secrets: lykos clean --confidence HIGH")
    print("4. For full protection: lykos protect --confidence HIGH")
    
    return 0

def main(argv=None):
    parser = create_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return 0

    try:
        args = parser.parse_args(argv)

        if args.command == 'scan':
            return cmd_scan(args)
        elif args.command == 'guard':
            return cmd_guard(args)
        elif args.command == 'protect':
            return cmd_protect(args)
        elif args.command == 'clean':
            return cmd_clean(args)
        elif args.command == 'status':
            return cmd_status(args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())