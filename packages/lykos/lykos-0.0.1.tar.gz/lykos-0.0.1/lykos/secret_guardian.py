import argparse
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
import os

from lykos.secret_scanner import SecretScanner
from lykos.git_secrets_cleaner import GitSecretsCleaner
from lykos.pre_commit_guard import PreCommitGuard
from lykos.secret_utils import ensure_ignored

class SecretGuardian:
    def __init__(self):
        self.report_file = ".secrets_report.json"
        
    def check_git_repo(self):
        try:
            subprocess.run(["git", "rev-parse", "--git-dir"], 
                          capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            print("Not in a git repository.")
            return False
    
    def get_repo_info(self):
        try:
            branch = subprocess.check_output(
                ["git", "branch", "--show-current"], text=True
            ).strip()
            
            try:
                remote = subprocess.check_output(
                    ["git", "remote", "get-url", "origin"], text=True
                ).strip()
            except subprocess.CalledProcessError:
                remote = "No remote configured"
            
            try:
                commit_count = int(subprocess.check_output(
                    ["git", "rev-list", "--count", "HEAD"], text=True
                ).strip())
            except subprocess.CalledProcessError:
                commit_count = 0
            
            return {
                'branch': branch,
                'remote': remote,
                'commit_count': commit_count
            }
        except subprocess.CalledProcessError:
            return None
    
    def full_scan_and_clean(self, recent_commits=None, dry_run=False, min_confidence='MEDIUM'):
        print("Secret Guardian - Full Scan and Clean")
        print("=" * 50)

        self.update_gitignore(['.secrets_report.json', '.env', '*.whl'])
        try:
            subprocess.run(
                ["git", "rm", "--cached", "--quiet", ".secrets_report.json"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            pass

        repo_info = self.get_repo_info()
        if repo_info:
            print(f"Repository: {repo_info['branch']} ({repo_info['commit_count']} commits)")
            if repo_info['remote'] != "No remote configured":
                print(f"Remote: {repo_info['remote']}")
        
        print(f"\nStep 1: Scanning for secrets (confidence: {min_confidence}+)...")
        scanner = SecretScanner()
        
        if recent_commits:
            secrets = scanner.scan_commits(recent=recent_commits, min_confidence=min_confidence)
        else:
            secrets = scanner.scan_commits(all_commits=True, min_confidence=min_confidence)
        
        report = scanner.generate_report(secrets, self.report_file)
        
        if not secrets:
            print("No secrets found! Repository is clean.")
            self.setup_protection(min_confidence=min_confidence)
            return True
        
        by_confidence = defaultdict(int)
        for secret in secrets:
            confidence_level = secret['confidence']['level']
            by_confidence[confidence_level] += 1
        
        print(f"\nFound {len(secrets)} secrets:")
        for level in ['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW']:
            count = by_confidence[level]
            if count > 0:
                print(f"   {level}: {count}")
        
        print(f"\nStep 2: Cleaning {len(secrets)} secrets from history...")
        cleaner = GitSecretsCleaner(dry_run=dry_run)
        
        if not cleaner.check_repo_clean():
            print("Repository has uncommitted changes")
            return False
        
        success = cleaner.clean_history_advanced(secrets, min_confidence=min_confidence)
                
        if not success:
            return False
        
        if not dry_run:
            print("\nStep 3: Setting up future protection...")
            self.setup_protection(min_confidence=min_confidence)
        
        self.print_final_recommendations(secrets)
        
        return True

    def setup_protection(self, min_confidence: str = 'MEDIUM'):

        for dot in ('.env', '.env.local'):
            if os.path.exists(dot):
                ensure_ignored(dot)

        guard = PreCommitGuard(min_confidence=min_confidence)
        if guard.install_git_hook():
            print("Pre-commit hook installed successfully")
            print(f"Hook configured with {min_confidence} confidence threshold")
        else:
            print("Failed to install pre-commit hook")

        secretsignore_path = Path(".secretsignore")
        if not secretsignore_path.exists():
            with secretsignore_path.open('w') as f:
                f.write(
                    """
                    # Add false-positive secrets here (one per line)
                    # Comments start with #
                    # Example:
                    # sk_test_fake_api_key_for_testing
                    # AKIATEST123456789EXAMPLE
                    """.lstrip()
                )
            print("Created .secretsignore template")

        # ── 3️⃣  append common secret patterns to .gitignore
        gitignore_entries = [
            "# Secret files",
            ".env",
            ".env.local",
            ".env.*.local",
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",
            ".secrets_report.json",
            "# AWS",
            ".aws/credentials",
            "# SSH",
            "id_rsa",
            "id_ed25519",
        ]
        self.update_gitignore(gitignore_entries)
    
    def update_gitignore(self, entries):
        gitignore_path = Path(".gitignore")
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                current_content = f.read()
        else:
            current_content = ""
        
        new_entries = []
        for entry in entries:
            if entry not in current_content:
                new_entries.append(entry)
        
        if new_entries:
            with open(gitignore_path, 'a') as f:
                if current_content and not current_content.endswith('\n'):
                    f.write('\n')
                f.write('\n'.join(new_entries) + '\n')
            print(f"Added {len(new_entries)} entries to .gitignore")
    
    def print_final_recommendations(self, secrets):
        print("\n" + "=" * 50)
        print("CRITICAL SECURITY ACTIONS REQUIRED:")
        print("=" * 50)
        
        by_confidence = defaultdict(list)
        for secret in secrets:
            confidence_level = secret['confidence']['level']
            by_confidence[confidence_level].append(secret)
        
        high_confidence_secrets = by_confidence['HIGH']
        if high_confidence_secrets:
            print(f"\nURGENT - HIGH CONFIDENCE SECRETS ({len(high_confidence_secrets)} found):")
            
            by_type = defaultdict(list)
            for secret in high_confidence_secrets:
                secret_type = secret['type']
                by_type[secret_type].append(secret)
            
            for secret_type, secret_list in by_type.items():
                print(f"\n  {secret_type} ({len(secret_list)} found):")
                for secret in secret_list:
                    confidence_score = secret['confidence']['score']
                    print(f"• {secret['token'][:8]}...{secret['token'][-4:]} (confidence: {confidence_score:.3f})")
                    
                if secret_type.startswith("AWS"):
                    print("→ Go to AWS IAM Console > Access keys")
                elif secret_type.startswith("GitHub"):
                    print("→ Go to GitHub Settings > Developer settings > Personal access tokens")
                elif secret_type.startswith("OpenAI"):
                    print("→ Go to OpenAI Platform > API keys")
                elif secret_type.startswith("Stripe"):
                    print("→ Go to Stripe Dashboard > Developers > API keys")
                elif secret_type.startswith("Anthropic"):
                    print("→ Go to Anthropic Console > API keys")

        medium_count = len(by_confidence['MEDIUM'])
        low_count = len(by_confidence['LOW'])
        very_low_count = len(by_confidence['VERY_LOW'])
        
        if medium_count > 0:
            print(f"\nMEDIUM CONFIDENCE: {medium_count} secrets (review recommended)")
        if low_count > 0:
            print(f"LOW CONFIDENCE: {low_count} secrets (likely false positives)")
        if very_low_count > 0:
            print(f"VERY LOW CONFIDENCE: {very_low_count} secrets (probably false positives)")
    
        print("\nPREVENTION MEASURES:")
        print("- Pre-commit hook installed to block future secrets")
        print("- .gitignore updated to exclude common secret files")
        print("- Run 'lykos guard --check-files <file>' to check files manually")

def main():
    parser = argparse.ArgumentParser(
        description="Secret Guardian - Complete Git secret management with confidence scoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lykos --full-scan --confidence HIGH
  lykos --full-scan --recent 50 --confidence MEDIUM
  lykos --scan-only --confidence HIGH
  lykos --clean-only scope history --confidence HIGH
  lykos --setup-protection --confidence MEDIUM
        """
    )
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--full-scan", action="store_true",
                             help="Complete workflow: scan, clean, and protect")
    action_group.add_argument("--scan-only", action="store_true", 
                             help="Only scan for secrets")
    action_group.add_argument("--clean-only", action="store_true",
                             help="Only clean history (requires existing report)")
    action_group.add_argument("--setup-protection", action="store_true",
                             help="Only setup protection (pre-commit hooks)")
    action_group.add_argument("--check-current", action="store_true",
                             help="Check current working directory for secrets")
    
    parser.add_argument("--recent", type=int, metavar="N",
                       help="Only scan last N commits (default: all commits)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without executing")
    parser.add_argument("--scope", choices=['working', 'history'], default='working',
                       help='Cleaning method (working=current files, history=full git history)')
    parser.add_argument("--report", default=".secrets_report.json",
                       help="Path to secrets report file")
    parser.add_argument("--confidence", choices=['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW'], 
                       default='MEDIUM', help='Min confidence level for operations (default: MEDIUM)')
    
    args = parser.parse_args()
    
    guardian = SecretGuardian()
    guardian.report_file = args.report
    
    if not args.setup_protection and not guardian.check_git_repo():
        sys.exit(1)
    
    success = True
    
    if args.full_scan:
        success = guardian.full_scan_and_clean(
            recent_commits=args.recent,
            dry_run=args.dry_run,
            min_confidence=args.confidence
        )
    
    elif args.scan_only:
        scanner = SecretScanner()
        if args.recent:
            secrets = scanner.scan_commits(recent=args.recent, min_confidence=args.confidence)
        else:
            secrets = scanner.scan_commits(all_commits=True, min_confidence=args.confidence)
        scanner.generate_report(secrets, guardian.report_file)
        
        if secrets:
            high_confidence_secrets = [s for s in secrets if s['confidence']['level'] == 'HIGH']
            success = len(high_confidence_secrets) == 0
        else:
            success = True
    
    elif args.clean_only:
        cleaner = GitSecretsCleaner(dry_run=args.dry_run)
        if not cleaner.check_repo_clean():
            sys.exit(1)
        secrets = cleaner.load_secrets(guardian.report_file)
        if secrets:
            if args.scope == 'working':
                success = cleaner.clean_history_simple(secrets, min_confidence=args.confidence)
            else:
                success = cleaner.clean_history_advanced(secrets, min_confidence=args.confidence)
    
    elif args.setup_protection:
        guardian.setup_protection(min_confidence=args.confidence)
        print("Protection setup complete!")
    
    elif args.check_current:
        guard = PreCommitGuard(min_confidence=args.confidence)
        py_files = list(Path(".").glob("**/*.py"))
        violations = guard.scan_files([str(f) for f in py_files])
        clean = guard.report_violations(violations)
        
        if violations:
            high_confidence_violations = [v for v in violations if v['confidence']['level'] == 'HIGH']
            success = len(high_confidence_violations) == 0
        else:
            success = True
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()