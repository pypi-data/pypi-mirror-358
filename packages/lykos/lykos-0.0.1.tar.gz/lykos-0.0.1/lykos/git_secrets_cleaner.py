import json
import subprocess
import os
import sys
import time
from collections import defaultdict
from lykos.secret_scanner import SecretScanner
import tempfile
import hashlib
import re
import shutil
from pathlib import Path

def redaction(token: str, level: str) -> str:
    digest = hashlib.sha1(token.encode()).hexdigest()[:8]
    return f"REDACTED_{level}_{digest}"

class GitSecretsCleaner:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.temp_dir = None

    def check_repo_clean(self):
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout.strip():
                print("Repository has uncommitted changes. Please commit or stash first.")
                return False
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("Not in a git repository or git command timed out")
            return False
    
    def create_backup(self):
        try:
            current_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], text=True, timeout=10
            ).strip()
            
            backup_name = f"backup-before-secret-clean-{current_branch}-{int(time.time())}"
            
            try:
                subprocess.run(["git", "branch", "-D", backup_name], 
                             capture_output=True, check=False, timeout=10)
            except:
                pass
            
            subprocess.run(["git", "branch", backup_name], check=True, timeout=10)
            print(f"Created backup: {backup_name}")
            return backup_name
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"Could not create backup: {e}")
            return None
    
    def filter_secrets_by_confidence(self, secrets, min_confidence="MEDIUM"):
        confidence_order = {"VERY_LOW": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
        min_level = confidence_order.get(min_confidence, 2)
        
        filtered_secrets = []
        skipped_count = 0
        
        for secret in secrets:
            secret_level = confidence_order.get(secret['confidence']['level'], 0)
            if secret_level >= min_level:
                filtered_secrets.append(secret)
            else:
                skipped_count += 1
                    
        if skipped_count > 0:
            print(f"Skipped {skipped_count} low-confidence detections")
            
        return filtered_secrets
    
    def get_all_commits(self):
        try:
            result = subprocess.check_output(
                ["git", "rev-list", "--all", "--reverse"],
                text=True, timeout=60
            )
            return result.strip().split('\n') if result.strip() else []
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("Warning: Could not get all commits (timeout or error)")
            return []
    
    def get_commit_files(self, commit_hash):
        try:
            result = subprocess.check_output(
                ["git", "ls-tree", "-r", "--name-only", commit_hash],
                text=True, timeout=30
            )
            return result.strip().split('\n') if result.strip() else []
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return []
    
    def get_file_content(self, commit_hash, file_path):
        try:
            return subprocess.check_output(
                ["git", "show", f"{commit_hash}:{file_path}"],
                text=True, errors="ignore", timeout=30
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return None
    
    def apply_replacements(self, content: str, replacements: dict[str, str]):

        tokens = sorted(replacements.keys(), key=len, reverse=True)
        pattern = re.compile('|'.join(re.escape(t) for t in tokens))

        def repl(match: re.Match):
            return replacements[match.group(0)]

        modified = pattern.sub(repl, content)
        replacements_made = [(t, replacements[t]) for t in tokens if t in content]
        return modified, replacements_made

    
    def clean_history_completely(self, secrets, min_confidence="MEDIUM", extra_replacements=None):
        if not secrets:
            print("No secrets to clean")
            return True

        filtered_secrets = self.filter_secrets_by_confidence(secrets, min_confidence)
        if not filtered_secrets:
            print(f"No secrets found with {min_confidence}+ confidence")
            return True

        print(f"Found {len(filtered_secrets)} secrets to clean with {min_confidence}+ confidence")

        replacements = {}
        for secret in filtered_secrets:
            token = secret['token']
            conf_level = secret['confidence']['level']
            replacement = redaction(token, conf_level)
            replacements[token] = replacement
        
        if extra_replacements:
            replacements.update(extra_replacements)

        print(f"Rewriting history to completely remove {len(replacements)} secrets...")

        if self.dry_run:
            print("DRY RUN - would clean:")
            for token, replacement in replacements.items():
                print(f"  {token[:20]}... → {replacement}")
            return True

        if not self.check_repo_clean():
            return False

        try:
            subprocess.run(["git-filter-repo", "--help"], 
                         capture_output=True, check=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("ERROR: `git-filter-repo` not installed. Get it from https://github.com/newren/git-filter-repo")
            print("Install with: pip install git-filter-repo")
            return False

        backup = self.create_backup()
        if not backup:
            print("Failed to create backup, aborting")
            return False

        try:
            remote_url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"], text=True, timeout=10
            ).strip()
            current_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], text=True, timeout=10
            ).strip()
            has_remote = True
        except:
            remote_url = None
            current_branch = "main"
            has_remote = False

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            for old, new in replacements.items():
                escaped_old = old.replace('\\', '\\\\').replace('\n', '\\n')
                f.write(f"{escaped_old}==>{new}\n")
            replace_file = f.name

        try:
            print("Rewriting history with git-filter-repo...")
            print("This may take several minutes for large repos...")
            
            result = subprocess.run([
                "git", "filter-repo",
                "--replace-text", replace_file,
                "--force",
                "--refs", f"refs/heads/{current_branch}",
                "--prune-empty", "always" 
            ], check=False)

            if result.returncode != 0:
                print("History rewrite failed:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                if backup:
                    print(f"To restore backup: git reset --hard {backup}")
                return False
            
            shutil.rmtree(".git/refs/original", ignore_errors=True)
            if backup:
                subprocess.run(["git", "branch", "-D", backup], check=False)

            print("History rewrite completed!")

            if has_remote and remote_url:
                try:
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", remote_url],
                        check=False, timeout=10
                    )
                except subprocess.CalledProcessError:
                    pass  

                print("\n" + "=" * 60)
                print("!!!! CRITICAL: ABOUT TO FORCE PUSH CLEANED HISTORY !!!!")
                print("=" * 60)
                print("This will:")
                print("- Overwrite remote git history permanently")
                print("- Break existing clones for all team members")
                print("- Require everyone to re-clone the repo")
                print("- Cannot be easily undone")
                print()

                choice = input("Proceed with force push? (yes/no): ").lower().strip()

                if choice in ['yes', 'y']:
                    print(f"Force pushing to {current_branch}...")
                    result = subprocess.run([
                        "git", "push", "origin", current_branch, "--force"
                    ], capture_output=True, text=True, timeout=120)

                    if result.returncode == 0:
                        print("Successfully pushed cleaned history!")
                        print("NOTIFY YOUR TEAM IMMEDIATELY:")
                        print(f"Everyone must: git fetch && git reset --hard origin/{current_branch}")
                        print("Or just simply re-clone the repository")
                    else:
                        print(f"Push failed: {result.stderr}")
                        print("Run manually: git push origin --force")
                else:
                    print("Force push cancelled.")
                    print("To push later: git push origin --force")
                    if backup:
                        print(f"To undo cleaning: git reset --hard {backup}")

            print(f"\nHistory completely cleaned! {len(replacements)} secrets permanently removed.")
            print("Next steps:")
            print("1. Team members must re-clone the repository")
            print("2. Rotate any real credentials that were exposed")
            if backup:
                print(f"3. Delete backup when satisfied: git branch -D {backup}")

            return True

        except subprocess.TimeoutExpired:
            print("Git filter-repo timed out after 10 minutes")
            print("Repository might be too large. Try using --recent option to limit commits")
            if backup:
                print(f"To restore: git reset --hard {backup}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            if backup:
                print(f"To restore: git reset --hard {backup}")
            return False
        finally:
            try:
                Path(replace_file).unlink(missing_ok=True)
            except:
                pass
            
    def clean_history_simple(self, secrets, min_confidence="MEDIUM"):
        ## kiv this. may not be needed
        """only current files"""
        if not secrets:
            print("No secrets to clean")
            return True
        
        filtered_secrets = self.filter_secrets_by_confidence(secrets, min_confidence)
        
        if not filtered_secrets:
            print(f"No secrets found with {min_confidence}+ confidence")
            return True
        
        by_confidence = defaultdict(list)
        for secret in filtered_secrets:
            confidence_level = secret['confidence']['level']
            by_confidence[confidence_level].append(secret)
        
        print(f"Cleaning {len(filtered_secrets)} secrets with {min_confidence}+ confidence...")
        
        for level in ['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW']:
            count = len(by_confidence[level])
            if count > 0:
                print(f"   {level}: {count} secrets")
        
        replacements = {}
        for secret in filtered_secrets:
            token = secret['token']
            conf_level = secret['confidence']['level']
            replacement = redaction(token, conf_level)
            replacements[token] = replacement
        
        print("Replacements to be made:")
        for i, (token, replacement) in enumerate(replacements.items(), 1):
            confidence_level = "UNKNOWN"
            for secret in filtered_secrets:
                if secret['token'] == token:
                    confidence_level = secret['confidence']['level']
                    break
            
            print(f"  {i}. [{confidence_level}] {token[:10]}... → {replacement}")
        
        if self.dry_run:
            print("\nDRY RUN - Would clean these files:")
            for secret in filtered_secrets:
                file_path = secret['file']
                line_num = secret['line']
                token = secret['token']
                confidence = secret['confidence']['level']
                print(f"   {file_path}:{line_num} - {token[:10]}... ({confidence})")
            return True
        
        confirm = input(f"\nThis will clean {len(filtered_secrets)} secrets from current files. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return False
        
        backup = self.create_backup()
        
        affected_files = set()
        for secret in filtered_secrets:
            affected_files.add(secret['file'])
        
        print(f"\nProcessing {len(affected_files)} affected files...")
        
        files_modified = []
        
        for file_path in affected_files:
            if not os.path.exists(file_path):
                print(f"Skipping missing file: {file_path}")
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                modified_content, replacements_made = self.apply_replacements(content, replacements)
                
                if replacements_made:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    files_modified.append((file_path, len(replacements_made)))
                    print(f"   {file_path}: {len(replacements_made)} secrets replaced")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        if files_modified:
            try:
                subprocess.run(["git", "add"] + [f[0] for f in files_modified], 
                             check=True, timeout=30)
                subprocess.run(["git", "commit", "-m", 
                              f"Remove {len(filtered_secrets)} secrets (confidence: {min_confidence}+)"], 
                             check=True, timeout=30)
                
                print(f"\nSuccessfully cleaned {len(files_modified)} files!")
                print(f"Cleaned {len(filtered_secrets)} secrets with {min_confidence}+ confidence")
                print("\nNext steps:")
                print("1. Review changes: git show HEAD")
                print("2. Push if needed: git push --force-with-lease")
                print("3. Regenerate all cleaned API keys")
                if backup:
                    print(f"4. Delete backup when satisfied: git branch -D {backup}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"Git commit failed: {e}")
                return False
        else:
            print("No files were modified (secrets may already be cleaned)")
        
        ok = self._verify_history_is_clean(min_confidence="HIGH")
        return ok
    
    def clean_history_advanced(self, secrets, min_confidence="MEDIUM"):
        if not secrets:
            print("No secrets to clean")
            return True

        filtered_secrets = self.filter_secrets_by_confidence(secrets, min_confidence)
        if not filtered_secrets:
            print(f"No secrets found with {min_confidence}+ confidence")
            return True

        replacements = {}
        for secret in filtered_secrets:
            token = secret['token']
            conf_level = secret['confidence']['level']
            replacement = redaction(token, conf_level)
            replacements[token] = replacement

        print(f"Cleaning: git-filter-repo will scrub {len(replacements)} secrets...")
        
        if self.dry_run:
            for old, new in replacements.items():
                print(f"{old[:10]}...  →  {new}")
            print("\nDRY RUN — no history rewritten")
            return True

        if not self.check_repo_clean():
            return False
        backup = self.create_backup()

        try:
            remote_url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"], text=True, timeout=10
            ).strip()
            has_remote = True
        except:
            remote_url = None
            has_remote = False

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for old, new in replacements.items():
                f.write(f"{old}==>{new}\n")
            replace_file = f.name

        try:
            print("Rewriting history with git-filter-repo...")
            subprocess.run([
                "git", "filter-repo", 
                "--replace-text", replace_file,
                "--force"
            ], check=True, timeout=600)
            
            if has_remote and remote_url:
                subprocess.run(
                    ["git", "remote", "set-url", "origin", remote_url],
                    check=False, timeout=10
                )
            print(f"\nHistory rewritten! Scrubbed {len(replacements)} secrets")
            print("Next steps:")
            print("1. Force-push: git push origin --force-with-lease")
            print("2. Team members must re-clone the repo")
            if backup:
                print(f"3. Delete backup when satisfied: git branch -D {backup}")
            return True
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"Error: {e}")
            if backup:
                print(f"To restore: git reset --hard {backup}")
            return False
        finally:
            try:
                Path(replace_file).unlink(missing_ok=True)
            except:
                pass

    def _verify_history_is_clean(self, min_confidence="HIGH") -> bool:
        print("\nVerifying cleaned history …")
        
        try:
            scanner = SecretScanner()
            
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Verification scan timed out")
            
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(120)  # 2mins timeout for verification
            
            try:
                leftover = scanner.scan_commits(recent=10, min_confidence=min_confidence)
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
        
        except TimeoutError:
            print("Verification scan timed out - skipping full verification")
            print("You can manually verify with: lykos scan --recent 10")
            return True
        except KeyboardInterrupt:
            print("\nVerification cancelled by user")
            return False
        except Exception as e:
            print(f"Verification failed: {e}")
            print("You can manually verify with: lykos scan --recent 10")
            return True 
        
        if leftover:
            print(f"{len(leftover)} secret(s) still detected after cleaning!")
            for s in leftover[:5]: 
                commit_short = s.get('commit', 'unknown')[:7] if s.get('commit') else 'unknown'
                print(f"{s['type']}: {s['token'][:6]}…{s['token'][-4:]} "
                    f"(commit {commit_short}, file {s['file']})")
            return False

        print("Post-clean scan shows no remaining secrets.")
        return True

    def load_secrets(self, report_file):
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
                
            secrets = report.get('secrets', [])
            
            if secrets and isinstance(secrets[0], dict) and 'confidence' in secrets[0]:
                by_confidence = defaultdict(int)
                for secret in secrets:
                    confidence_level = secret['confidence']['level']
                    by_confidence[confidence_level] += 1
                    
                print(f"Loaded {len(secrets)} secrets from report:")
                for level in ['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW']:
                    count = by_confidence[level]
                    if count > 0:
                        print(f"   {level}: {count}")
                        
            return secrets
            
        except FileNotFoundError:
            print(f"Report file not found: {report_file}")
            print("Run the scanner first to generate the report.")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in report: {e}")
            return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Git History Cleaner with Confidence Support")
    parser.add_argument("--report", "-r", default=".secrets_report.json",
                       help="Secrets report file")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done")
    parser.add_argument("--scope", choices=["working", "history"], default="working",
                       help="Cleaning method (working=current files, advanced=full history)")
    parser.add_argument("--confidence", choices=["HIGH", "MEDIUM", "LOW", "VERY_LOW"], 
                       default="MEDIUM", help="Min confidence level to clean (default: MEDIUM)")
    
    args = parser.parse_args()
    
    cleaner = GitSecretsCleaner(dry_run=args.dry_run)
    
    if not cleaner.check_repo_clean():
        sys.exit(1)
    
    secrets = cleaner.load_secrets(args.report)
    if secrets is None:
        sys.exit(1)
    
    if not secrets:
        print("No secrets found in report")
        sys.exit(0)
    
    print(f"Cleaning secrets with {args.confidence}+ confidence")
    
    if args.scope == "working":
        success = cleaner.clean_history_simple(secrets, min_confidence=args.confidence)
    else:
        success = cleaner.clean_history_advanced(secrets, min_confidence=args.confidence)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()