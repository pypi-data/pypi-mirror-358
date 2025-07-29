import argparse, json, re, subprocess, sys
from collections import defaultdict
from lykos.patterns import PATTERNS, BINARY_EXTENSIONS, ENTROPY_REGEX, is_false_positive, load_user_whitelist
from lykos.confidence import (
    calculate_confidence,
    shannon_entropy,
    ENTROPY_THRESHOLD,
)
from lykos.secret_utils import ensure_report_ignored

EXCLUDED_FILES = {
    '.secrets_report.json',
    '.leak_report.json', 
    'secrets_report.json',
    'leak_report.json',
}

class SecretScanner:
    def __init__(self, entropy_threshold=ENTROPY_THRESHOLD):
        self.entropy_threshold = entropy_threshold
        self.first_seen = defaultdict(lambda: None)
        
    def sh(self, cmd):
        return subprocess.check_output(cmd, text=True).strip().splitlines()

    def get_current_branch(self):
        try:
            return subprocess.check_output(
                ["git", "branch", "--show-current"], 
                text=True
            ).strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def should_skip_file(self, file_path: str) -> bool:
        if any(file_path.endswith(ext) for ext in BINARY_EXTENSIONS):
            return True

        SAFE_DOTDIRS = {
            '.git',
            '.hg',
            '.svn',
        }
        for part in file_path.split('/'):
            if part.startswith('.'):
                return part in SAFE_DOTDIRS

        return False


    def detect_secrets_in_line(self, line, line_num, file_path):

        user_whitelist = load_user_whitelist()
        for whitelisted_token in user_whitelist:
            if whitelisted_token in line:
                return []
            
        detections = []
        tokens_found_in_line = set()  
        
        pattern_priority = [
            "AWS_ACCESS_KEY", "AWS_SECRET_KEY", "Stripe_Live", "GitHub_Token", 
            "OpenAI", "Anthropic", "Google_API", "Twilio_Account_SID", 
            "Twilio_Auth_Token", "SendGrid_API_Key", "Stripe_Test", "Deepseek"
        ]
        
        for pattern_name in pattern_priority:
            if pattern_name not in PATTERNS:
                continue
                
            pattern = PATTERNS[pattern_name]
            for match in re.finditer(pattern, line):
                token = match.group(0)
                
                if token in tokens_found_in_line:
                    continue
                
                if is_false_positive(token):
                    continue
                    
                confidence_data = calculate_confidence(token, pattern_name, line, file_path)
                    
                tokens_found_in_line.add(token)
                detections.append({
                    'token': token,
                    'type': pattern_name,
                    'line_num': line_num,
                    'context': line.strip()[:100],
                    'confidence': confidence_data,
                    'detection_method': 'pattern'
                })
        
        for token in ENTROPY_REGEX.findall(line):
            if token not in tokens_found_in_line:
                if (shannon_entropy(token) > self.entropy_threshold and 
                    not is_false_positive(token) and
                    not any(c.isdigit() for c in token[:5])):
                    
                    confidence_data = calculate_confidence(token, "HIGH-ENTROPY", line, file_path)
                    tokens_found_in_line.add(token)
                    
                    detections.append({
                        'token': token,
                        'type': "HIGH-ENTROPY",
                        'line_num': line_num,
                        'context': line.strip()[:100],
                        'confidence': confidence_data,
                        'detection_method': 'entropy'
                    })
                    
        return detections

    def scan_commits(self, recent=None, all_commits=False, min_confidence="LOW", target_branch=None):

        confidence_thresholds = {
            "HIGH": 0.8,
            "MEDIUM": 0.5, 
            "LOW": 0.2,
            "VERY_LOW": 0.05
        }
        min_threshold = confidence_thresholds.get(min_confidence, 0.2)
        
        if target_branch:
            print(f"Scanning all commits on branch: {target_branch}")
            try:
                subprocess.check_output(["git", "rev-parse", "--verify", f"refs/heads/{target_branch}"], 
                                    text=True, stderr=subprocess.DEVNULL)
                commits = self.sh(["git", "rev-list", "--reverse", target_branch])
                scan_mode = "target_branch"
            except subprocess.CalledProcessError:
                print(f"Error: Branch '{target_branch}' not found")
                return []
                
        elif all_commits:
            print("Scanning all branches and commits...")
            commits = self.sh(["git", "rev-list", "--reverse", "--all"])
            scan_mode = "all_commits"
            
        elif recent:
            current_branch = self.get_current_branch()
            print(f"Scanning last {recent} commits on branch: {current_branch}")
            commits = self.sh(["git", "rev-list", "--reverse", f"-n{recent}", "HEAD"])
            scan_mode = "recent"
            
        else:
            current_branch = self.get_current_branch()
            print(f"Scanning last 10 commits on branch: {current_branch}")
            commits = self.sh(["git", "rev-list", "--reverse", "-n10", "HEAD"])
            scan_mode = "recent"

        print(f"Scanning {len(commits)} commits...")
        secrets_found = []
        
        for i, commit_hash in enumerate(commits, 1):
            if i % 10 == 0:
                print(f"   Processed {i}/{len(commits)} commits...")
                
            try:
                files = self.sh(["git", "ls-tree", "-r", "--name-only", commit_hash])
                
                if scan_mode == "target_branch":
                    actual_branch = target_branch  
                elif scan_mode == "all_commits":
                    actual_branch = self.get_commit_branch(commit_hash)
                else:
                    actual_branch = self.get_current_branch()
                
                for file_path in files:
                    if self.should_skip_file(file_path):
                        continue
                        
                    try:
                        blob = subprocess.check_output(
                            ["git", "show", f"{commit_hash}:{file_path}"], 
                            text=True, errors="ignore"
                        )
                        
                        suspects = self.detect_secrets_in_file_content(blob, file_path)
                        
                        for suspect in suspects:
                            token = suspect['token']
                            confidence_score = suspect['confidence']['score']
                            
                            if confidence_score < min_threshold:
                                continue
                                
                            if self.first_seen[token] is None:
                                try:
                                    commit_info = subprocess.check_output(
                                        ["git", "show", "--format=%an|%ad|%s", "--no-patch", commit_hash],
                                        text=True
                                    ).strip().split('|')
                                    author = commit_info[0] if len(commit_info) > 0 else "unknown"
                                    date = commit_info[1] if len(commit_info) > 1 else "unknown"
                                    message = commit_info[2] if len(commit_info) > 2 else "unknown"
                                except:
                                    author = date = message = "unknown"
                                
                                secret_info = {
                                    'token': token,
                                    'type': suspect['type'],
                                    'commit': commit_hash,
                                    'branch': actual_branch,
                                    'author': author,
                                    'date': date,
                                    'message': message[:50] + "..." if len(message) > 50 else message,
                                    'file': file_path,
                                    'line': suspect['line_num'],
                                    'context': suspect['context'],
                                    'entropy': shannon_entropy(token),
                                    'confidence': suspect['confidence'],
                                    'detection_method': suspect['detection_method']
                                }
                                self.first_seen[token] = secret_info
                                secrets_found.append(secret_info)
                                
                    except subprocess.CalledProcessError:
                        continue
                        
            except subprocess.CalledProcessError:
                continue

        return secrets_found

    def detect_secrets_in_file_content(self, blob, file_path):
        detections = []
        
        for line_num, line in enumerate(blob.splitlines(), 1):
            line_detections = self.detect_secrets_in_line(line, line_num, file_path)
            detections.extend(line_detections)
        
        return detections
    
    def get_commit_branch(self, commit_hash):
        try:
            result = subprocess.check_output(
                ["git", "branch", "--contains", commit_hash, "--all"], 
                text=True
            ).strip()
            
            if not result:
                return "unknown"
                
            branches = []
            for line in result.split('\n'):
                branch = line.strip().replace('* ', '')
                if not branch.startswith('remotes/'):
                    branches.append(branch)
            
            if not branches:
                for line in result.split('\n'):
                    branch = line.strip().replace('* ', '')
                    if branch.startswith('remotes/'):
                        branch = branch.replace('remotes/origin/', '')
                        branches.append(branch)
            
            return branches[0] if branches else "unknown"
            
        except subprocess.CalledProcessError:
            return "unknown"
    
    def show_interactive_summary(self, secrets, confidence_level):
        if not secrets:
            print("No secrets found! Repo appears clean")
            return
        
        by_confidence = defaultdict(list)
        for secret in secrets:
            conf_level = secret['confidence']['level']
            by_confidence[conf_level].append(secret)
        
        print(f"\nFound {len(secrets)} potential secrets:")
        print("=" * 50)
        
        total_high = len(by_confidence['HIGH'])
        total_medium = len(by_confidence['MEDIUM'])
        total_low = len(by_confidence['LOW'])
        total_very_low = len(by_confidence['VERY_LOW'])
        
        if total_high > 0:
            print(f"HIGH confidence: {total_high} (IMMEDIATE ACTION REQUIRED)")
        if total_medium > 0:
            print(f"MEDIUM confidence: {total_medium} (review recommended)")
        if total_low > 0:
            print(f"LOW confidence: {total_low} (likely false positives)")
        if total_very_low > 0:
            print(f"VERY LOW confidence: {total_very_low} (probably false positives)")
        
        high_secrets = by_confidence['HIGH']
        if high_secrets:
            print(f"\nTop HIGH confidence secrets:")
            for i, secret in enumerate(high_secrets[:3], 1):
                print(f"  {i}. {secret['type']} in {secret['file']}:{secret['line']}")
        
        print("\nOptions:")
        print("  1. Clean HIGH confidence secrets (completely removes from history)")
        print("  2. Clean MEDIUM+ confidence secrets (completely removes from history)") 
        print("  3. Clean ALL secrets including fake/test (completely removes from history)")
        print("  4. Save report to file only (no cleaning)")
        print("  5. Exit")
        
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == "1":
            clean_level = "HIGH"
        elif choice == "2":
            clean_level = "MEDIUM"
        elif choice == "3":
            clean_level = "VERY_LOW"
        elif choice == "4":
            report = self.generate_report(secrets, ".secrets_report.json")
            print("Report saved. No cleaning performed.")
            return
        else:
            print("Exiting...")
            return
        
        print(f"\nCleaning {clean_level}+ confidence secrets...")
        print("This will completely remove secrets from ALL git history.")
        
        from lykos.git_secrets_cleaner import GitSecretsCleaner
        cleaner = GitSecretsCleaner(dry_run=False)
        if cleaner.check_repo_clean():
            self._clean_secrets_properly(cleaner, secrets, clean_level)

    def _clean_secrets_properly(self, cleaner, secrets, min_confidence):
        filtered_secrets = cleaner.filter_secrets_by_confidence(secrets, min_confidence)
        
        if not filtered_secrets:
            print(f"No secrets found with {min_confidence}+ confidence")
            return
        
        print(f"This will permanently remove {len(filtered_secrets)} secrets from git history.")
        print("Your team will need to re-clone after you push.")
        
        confirm = input(f"\nPermanently remove {len(filtered_secrets)} secrets? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return
        
        cleaner.clean_history_completely(filtered_secrets, min_confidence)

    def _clean_secrets_directly(self, cleaner, secrets, min_confidence):
        filtered_secrets = cleaner.filter_secrets_by_confidence(secrets, min_confidence)
        
        if not filtered_secrets:
            print(f"No secrets found with {min_confidence}+ confidence")
            return
        
        confirm = input(f"\nClean {len(filtered_secrets)} secrets? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return
        
        cleaner.clean_history_simple_from_memory(filtered_secrets, min_confidence)

    def generate_report(self, secrets, output_file=None):
        if not secrets:
            print("No secrets found!")
            print("Repository appears clean!")
            return {}

        by_confidence = defaultdict(list)
        by_branch = defaultdict(list)
        by_type = defaultdict(list)
        
        for secret in secrets:
            confidence_level = secret['confidence']['level']
            by_confidence[confidence_level].append(secret)
            
            branch_name = secret['branch']
            by_branch[branch_name].append(secret)
            
            secret_type = secret['type']
            by_type[secret_type].append(secret)

        print(f"\nFound {len(secrets)} potential secrets:")
        print("=" * 80)
        
        if len(by_branch) > 1:
            print(f"\nBranch Distribution:")
            for branch, branch_secrets in sorted(by_branch.items()):
                branch_high = len([s for s in branch_secrets if s['confidence']['level'] == 'HIGH'])
                branch_medium = len([s for s in branch_secrets if s['confidence']['level'] == 'MEDIUM'])
                risk_indicator = "[HIGH]" if branch_high > 0 else "[MED]" if branch_medium > 0 else "[LOW]"
                print(f"   {risk_indicator} {branch}: {len(branch_secrets)} secrets "
                    f"(HIGH: {branch_high}, MEDIUM: {branch_medium})")
        else:
            branch_name = list(by_branch.keys())[0] if by_branch else "unknown"
            print(f"\nBranch: {branch_name}")
        
        print(f"\nConfidence Analysis:")
        total_high = len(by_confidence['HIGH'])
        total_medium = len(by_confidence['MEDIUM']) 
        total_low = len(by_confidence['LOW'])
        total_very_low = len(by_confidence['VERY_LOW'])
        
        if total_high > 0:
            print(f"HIGH confidence: {total_high} (IMMEDIATE ACTION REQUIRED)")
        if total_medium > 0:
            print(f"MEDIUM confidence: {total_medium} (review recommended)")
        if total_low > 0:
            print(f"LOW confidence: {total_low} (likely false positives)")
        if total_very_low > 0:
            print(f"VERY LOW confidence: {total_very_low} (probably false positives)")
                
        print(f"\nSummary by type:")
        for secret_type, secret_list in by_type.items():
            avg_confidence = sum(s['confidence']['score'] for s in secret_list) / len(secret_list)
            high_count = len([s for s in secret_list if s['confidence']['level'] == 'HIGH'])
            risk_indicator = "[HIGH]" if high_count > 0 else "[MED]"
            print(f"   {risk_indicator} {secret_type}: {len(secret_list)} found "
                f"(avg confidence: {avg_confidence:.2f}, HIGH: {high_count})")
        
        print("\nDetailed findings:")
        print("=" * 80)
        
        if len(by_branch) > 1:
            for branch_name, branch_secrets in sorted(by_branch.items()):
                print(f"\nBRANCH: {branch_name} ({len(branch_secrets)} secrets)")
                print("-" * 60)
                
                sorted_secrets = sorted(branch_secrets, key=lambda x: x['confidence']['score'], reverse=True)
                
                for secret in sorted_secrets:
                    confidence = secret['confidence']
                    confidence_prefix = {
                        'HIGH': '[HIGH]',
                        'MEDIUM': '[MEDIUM]',
                        'LOW': '[LOW]', 
                        'VERY_LOW': '[VERY_LOW]'
                    }.get(confidence['level'], '[UNKNOWN]')
                    
                    print(f"""
    {confidence_prefix} CONFIDENCE: {confidence['level']} ({confidence['score']:.3f})
    Type     : {secret['type']}
    Commit   : {secret['commit'][:10]} ({secret['date']})
    Author   : {secret['author']}
    Message  : {secret['message']}
    File     : {secret['file']}
    Line     : {secret['line']}
    Token    : {secret['token'][:8]}...{secret['token'][-4:]} (len={len(secret['token'])}, entropy={secret['entropy']:.2f})
    Context  : {secret['context']}
    Reasons  : {', '.join(confidence['reasons'])}
    {'-' * 40}""")
        else:
            secrets_sorted = sorted(secrets, key=lambda x: x['confidence']['score'], reverse=True)
            
            for secret in secrets_sorted:
                confidence = secret['confidence']
                confidence_prefix = {
                    'HIGH': '[HIGH]',
                    'MEDIUM': '[MEDIUM]',
                    'LOW': '[LOW]', 
                    'VERY_LOW': '[VERY_LOW]'
                }.get(confidence['level'], '[UNKNOWN]')
                
                print(f"""
    {confidence_prefix} CONFIDENCE: {confidence['level']} ({confidence['score']:.3f})
    Type     : {secret['type']}
    Branch   : {secret['branch']}
    Commit   : {secret['commit'][:10]} ({secret['date']})
    Author   : {secret['author']}
    Message  : {secret['message']}
    File     : {secret['file']}
    Line     : {secret['line']}
    Token    : {secret['token'][:8]}...{secret['token'][-4:]} (len={len(secret['token'])}, entropy={secret['entropy']:.2f})
    Context  : {secret['context']}
    Reasons  : {', '.join(confidence['reasons'])}
    {'-' * 80}""")

        report_data = {
            'scan_info': {
                'total_secrets': len(secrets),
                'scan_date': subprocess.check_output(['date'], text=True).strip(),
                'by_type': {k: len(v) for k, v in by_type.items()},
                'by_confidence': {k: len(v) for k, v in by_confidence.items()},
                'by_branch': {k: len(v) for k, v in by_branch.items()},
                'confidence_summary': {
                    'high_risk_count': total_high,
                    'medium_risk_count': total_medium,
                    'low_risk_count': total_low,
                    'very_low_risk_count': total_very_low,
                    'avg_confidence': sum(s['confidence']['score'] for s in secrets) / len(secrets)
                }
            },
            'secrets': secrets
        }

        if output_file:
            ensure_report_ignored(output_file)

            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"\nDetailed report saved to: {output_file}")
            print(f"Remember to add {output_file} to .gitignore!")
            
        print(f"\nSmart Recommendations:")
        if total_high > 0:
            print(f"URGENT: Review {total_high} HIGH confidence secrets immediately")
            print("Use: lykos clean --confidence HIGH")
        if total_medium > 0:
            print(f"Review {total_medium} MEDIUM confidence detections")
        if total_low + total_very_low > total_high + total_medium:
            print("Most detections are low confidence - consider tuning patterns")
        
        if len(by_branch) > 1:
            high_risk_branches = [branch for branch, branch_secrets in by_branch.items() 
                                if any(s['confidence']['level'] == 'HIGH' for s in branch_secrets)]
            if high_risk_branches:
                print(f"Priority branches to clean: {', '.join(high_risk_branches)}")
                
        return report_data

def main():
    ap = argparse.ArgumentParser(description="Enhanced secret scanner with confidence scoring")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--recent", type=int, metavar="N", help="Scans last N commits")
    g.add_argument("--all", action="store_true", help="Scan all commits")
    ap.add_argument("--output", "-o", default=".secrets_report.json", 
                   help="Outputs JSON file (default: .secrets_report.json)")
    ap.add_argument("--entropy", type=float, default=ENTROPY_THRESHOLD,
                   help=f"Entropy threshold (default: {ENTROPY_THRESHOLD})")
    ap.add_argument("--confidence", choices=["HIGH", "MEDIUM", "LOW", "VERY_LOW"], default="LOW",
                   help="Min confidence level to report (default: LOW)")
    ap.add_argument("--branch", help="Scan specific branch (default: current)")
    
    args = ap.parse_args()

    if args.branch:
        try:
            subprocess.run(["git", "checkout", args.branch], check=True, capture_output=True)
            print(f"Switched to branch: {args.branch}")
        except subprocess.CalledProcessError:
            print(f"Failed to switch to branch: {args.branch}")
            sys.exit(1)

    scanner = SecretScanner(entropy_threshold=args.entropy)
    secrets = scanner.scan_commits(
        recent=args.recent, 
        all_commits=args.all, 
        min_confidence=args.confidence
    )
    
    if secrets:
        high_confidence_secrets = [s for s in secrets if s['confidence']['level'] == 'HIGH']
        print(f"\nNEXT STEPS:")
        if high_confidence_secrets:
            print(f"1. URGENT: Address {len(high_confidence_secrets)} HIGH confidence secrets")
        print(f"2. Add {args.output} to .gitignore")
        print(f"3. Use 'lykos clean --confidence HIGH' to remove high-confidence secrets")
        print(f"4. Rotate any real credentials found")
    
    high_confidence_count = len([s for s in secrets if s['confidence']['level'] == 'HIGH'])
    if high_confidence_count > 0:
        sys.exit(2)
    elif secrets:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()