import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from lykos.patterns import PATTERNS, ENTROPY_REGEX, is_false_positive, BINARY_EXTENSIONS, TEXT_SENSITIVE_EXTENSIONS, FALSE_POSITIVES
from lykos.confidence import (
    calculate_confidence,
    shannon_entropy,
    ENTROPY_THRESHOLD,
)
from lykos.secret_scanner import EXCLUDED_FILES

class PreCommitGuard:
    def __init__(self, entropy_threshold=ENTROPY_THRESHOLD, strict_mode=False, min_confidence="MEDIUM"):
        self.entropy_threshold = entropy_threshold
        self.strict_mode = strict_mode
        self.min_confidence = min_confidence
        self.violations = []

    def is_test_file(self, filepath):
        test_indicators = ['test', 'spec', 'mock', 'fixture', 'sample', 'example']
        path_lower = filepath.lower()
        return any(indicator in path_lower for indicator in test_indicators)
    
    def scan_content(self, content, filepath):
        violations = []
        confidence_thresholds = {
            "HIGH": 0.8,
            "MEDIUM": 0.5, 
            "LOW": 0.2,
            "VERY_LOW": 0.05
        }
        min_threshold = confidence_thresholds.get(self.min_confidence, 0.5)
        
        for line_num, line in enumerate(content.splitlines(), 1):                            
            for name, pattern in PATTERNS.items():
                for match in re.finditer(pattern, line):
                    token = match.group(0)
                    if not is_false_positive(token):
                        confidence_data = calculate_confidence(token, name, line, filepath)
                        
                        # report only if above confidence threshold
                        if confidence_data['score'] >= min_threshold:
                            violations.append({
                                'type': name,
                                'token': token,
                                'file': filepath,
                                'line': line_num,
                                'context': line[:100],
                                'confidence': confidence_data,
                                'detection_method': 'pattern'
                            })
            
            # skkip if in strict mode and test file
            if not (self.strict_mode and self.is_test_file(filepath)):
                for token in ENTROPY_REGEX.findall(line):
                    entropy = shannon_entropy(token)
                    if (entropy > self.entropy_threshold and 
                        not is_false_positive(token) and
                        not token.isdigit() and
                        not all(c.isalpha() for c in token)):
                        
                        confidence_data = calculate_confidence(token, "HIGH_ENTROPY", line, filepath)
                        
                        if confidence_data['score'] >= min_threshold:
                            violations.append({
                                'type': 'HIGH_ENTROPY',
                                'token': token,
                                'file': filepath,
                                'line': line_num,
                                'context': line.strip()[:100],
                                'entropy': entropy,
                                'confidence': confidence_data,
                                'detection_method': 'entropy'
                            })
        
        return violations
    
    def get_staged_files(self):
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True, text=True, check=True
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except subprocess.CalledProcessError:
            return []
    
    def get_file_content(self, filepath, staged=True):
        try:
            if staged:
                result = subprocess.run(
                    ["git", "show", f":{filepath}"],
                    capture_output=True, text=True, check=True
                )
                return result.stdout
            else:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except (subprocess.CalledProcessError, FileNotFoundError, UnicodeDecodeError):
            return ""
    
    def is_probably_binary(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        return ext in BINARY_EXTENSIONS

    def is_probably_text(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        return ext in TEXT_SENSITIVE_EXTENSIONS or ext == ''

    def scan_staged_files(self):
        files = self.get_staged_files()

        ALWAYS_CHECK = ['.env', '.env.local']
        files += [
            f for f in ALWAYS_CHECK
            if os.path.exists(f) and f not in files
        ]

        all_violations = []
        for filepath in files:
            if os.path.basename(filepath) in EXCLUDED_FILES or filepath == '.secretsignore':
                continue
            if self.is_probably_binary(filepath) or not self.is_probably_text(filepath):
                continue

            content = self.get_file_content(filepath, staged=True)
            if content:
                all_violations.extend(self.scan_content(content, filepath))
        return all_violations

    def scan_files(self, filepaths):
        all_violations = []
        for filepath in filepaths:
            if os.path.basename(filepath) in EXCLUDED_FILES or not os.path.exists(filepath):
                continue
            content = self.get_file_content(filepath, staged=False)
            if content:
                all_violations.extend(self.scan_content(content, filepath))
        return all_violations
    
    def report_violations(self, violations):
        if not violations:
            return True
        
        print("SECURITY ALERT: Potential secrets detected!")
        print("=" * 60)
        
        by_confidence = defaultdict(list)
        for v in violations:
            confidence_level = v['confidence']['level']
            by_confidence[confidence_level].append(v)
        
        print(f"\nConfidence Analysis (min threshold: {self.min_confidence}):")
        for level in ['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW']:
            count = len(by_confidence[level])
            if count > 0:
                print(f"   {level}: {count} violations")
        
        for level in ['HIGH', 'MEDIUM', 'LOW', 'VERY_LOW']:
            violations_at_level = by_confidence[level]
            if not violations_at_level:
                continue
                
            print(f"\n{level} CONFIDENCE ({len(violations_at_level)} violations):")
            for v in violations_at_level:
                entropy_info = f" (entropy: {v.get('entropy', 0):.2f})" if 'entropy' in v else ""
                confidence_score = v['confidence']['score']
                print(f"File: {v['file']}:{v['line']}")
                print(f"Type: {v['type']}{entropy_info}")
                print(f"Token: {v['token'][:8]}...{v['token'][-4:]}")
                print(f"Confidence: {confidence_score:.3f} ({v['confidence']['level']})")
                print(f"Context: {v['context']}")
                print()
        
        print("To fix:")
        print("1. Remove or redact the secrets from your files")
        print("2. Add false positives to .secretsignore")
        print("3. Use environment variables or secret management")
        print("4. Re-run this check or attempt to commit again")
        
        # only block commits for high confidence secrets unless in strict mode
        high_confidence_violations = by_confidence['HIGH']
        if high_confidence_violations:
            print(f"\nBLOCKING COMMIT: {len(high_confidence_violations)} HIGH confidence secrets found")
            return False
        elif self.strict_mode and violations:
            print(f"\nBLOCKING COMMIT: Strict mode enabled, found {len(violations)} total violations")
            return False
        else:
            medium_violations = by_confidence['MEDIUM']
            if medium_violations:
                print(f"\nWARNING: {len(medium_violations)} MEDIUM confidence secrets found, but allowing commit")
                print("Consider reviewing these before pushing to remote repository")
            return True
    
    def install_git_hook(self):
        git_dir = Path(".git")
        if not git_dir.exists():
            print("Not in a git repository")
            return False
            
        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        hook_file = hooks_dir / "pre-commit"
        
        hook_content = f'''#!/usr/bin/env python3
"""Pre-commit hook for secret detection"""
import sys
import subprocess
import os

hooks_dir = os.path.dirname(os.path.abspath(__file__))
git_dir = os.path.dirname(hooks_dir)
project_root = os.path.dirname(git_dir)

sys.path.insert(0, project_root)

lykos_path = os.path.join(project_root, 'lykos')
if os.path.exists(lykos_path):
    sys.path.insert(0, project_root)

try:
    try:
        from lykos.pre_commit_guard import PreCommitGuard
    except ImportError:
        from pre_commit_guard import PreCommitGuard
    
    # use {self.min_confidence} confidence threshold
    guard = PreCommitGuard(min_confidence="{self.min_confidence}")
    violations = guard.scan_staged_files()
    
    if violations:
        clean = guard.report_violations(violations)
        if not clean:
            print("\\nCommit rejected due to HIGH confidence secrets.")
            print("Fix the issues above and try again.")
            sys.exit(1)
        else:
            print("\\nWarnings found but commit allowed.")
            sys.exit(0)
    else:
        print("No secrets detected. Commit approved.")
        sys.exit(0)
        
except ImportError as e:
    print(f"Could not import pre_commit_guard: {{e}}")
    print("   Skipping secret check...")
    sys.exit(0)
except Exception as e:
    print(f"Error in pre-commit hook: {{e}}")
    sys.exit(0)  # Don't block commits on hook errors
'''
        
        try:
            with open(hook_file, 'w') as f:
                f.write(hook_content)
            
            os.chmod(hook_file, 0o755)
            
            print(f"Pre-commit hook installed at {hook_file}")
            print(f"Hook configured with {self.min_confidence} confidence threshold")
            print("Commits will now be automatically checked for secrets.")
            print("Add false positives to .secretsignore file if needed.")
            return True
            
        except Exception as e:
            print(f"Failed to install hook: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Prevent secrets in git commits with confidence scoring")
    parser.add_argument("--install-hook", action="store_true",
                       help="Install as git pre-commit hook")
    parser.add_argument("--scan-staged", action="store_true",
                       help="Scan staged files (for use in pre-commit hook)")
    parser.add_argument("--files", nargs="*",
                       help="Specific files to scan")
    parser.add_argument("--strict", action="store_true",
                       help="Strict mode (block commits for any violation)")
    parser.add_argument("--entropy", type=float, default=ENTROPY_THRESHOLD,
                       help=f"Entropy threshold (default: {ENTROPY_THRESHOLD})")
    parser.add_argument("--confidence", choices=["HIGH", "MEDIUM", "LOW", "VERY_LOW"], 
                       default="MEDIUM", help="Min confidence level to report (default: MEDIUM)")
    
    args = parser.parse_args()
    
    guard = PreCommitGuard(
        entropy_threshold=args.entropy,
        strict_mode=args.strict,
        min_confidence=args.confidence
    )
    
    if args.install_hook:
        success = guard.install_git_hook()
        sys.exit(0 if success else 1)
    
    if args.scan_staged:
        violations = guard.scan_staged_files()
    elif args.files:
        violations = guard.scan_files(args.files)
    else:
        try:
            subprocess.run(["git", "rev-parse", "--git-dir"], 
                          capture_output=True, check=True)
            violations = guard.scan_staged_files()
        except subprocess.CalledProcessError:
            print("Not in git repo, scanning current directory Python files...")
            py_files = list(Path(".").glob("*.py"))
            violations = guard.scan_files([str(f) for f in py_files])
    
    clean = guard.report_violations(violations)
    
    if violations:
        high_confidence_count = len([v for v in violations if v['confidence']['level'] == 'HIGH'])
        print(f"\nFound {len(violations)} potential secret(s)")
        if high_confidence_count > 0:
            sys.exit(2)
        elif not clean:
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        print("No secrets detected!")
        sys.exit(0)

if __name__ == "__main__":
    main()