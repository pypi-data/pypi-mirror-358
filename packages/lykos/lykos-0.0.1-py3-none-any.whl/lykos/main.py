import argparse, json, re, subprocess, sys, textwrap
from collections import defaultdict
from math import log2
from lykos.patterns import ENTROPY_REGEX, PATTERNS as _P, is_false_positive

ENTROPY_THRESHOLD = 4.5
PATTERNS = {
    "AWS" : _P["AWS_ACCESS_KEY"],
    "Google" : _P["Google_API"],
    "Stripe" : _P["Stripe_Live"],
    "OpenAI" : _P["OpenAI"],
}

def sh(cmd):
    return subprocess.check_output(cmd, text=True).strip().splitlines()

def shannon_entropy(s):
    if not s or len(s) < 8:  
        return 0.0
    
    if re.match(r'^\d{10,13}$', s):
        return 0.0
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', s.lower()):  # UUID
        return 0.0
        
    p = [s.count(c) / len(s) for c in set(s)]
    return -sum(x * log2(x) for x in p if x > 0)

def suspicious_strings(blob):
    suspects = []
    for line in blob.splitlines():
        if any(indicator in line for indicator in ['"commit":', '"token":', '"type":']):
            continue
            
        for name, pat in PATTERNS.items():
            for m in re.finditer(pat, line):
                token = m.group(0)
                if not is_false_positive(token):
                    suspects.append((token, name))
        
        for token in ENTROPY_REGEX.findall(line):
            if shannon_entropy(token) > ENTROPY_THRESHOLD and not is_false_positive(token):
                suspects.append((token, "HIGH-ENTROPY"))
    return suspects

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--recent", type=int, metavar="N")
    g.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if args.all:
        commits = sh(["git", "rev-list", "--reverse", "--all"])
    else:
        commits = sh(["git", "rev-list", "--reverse", f"-n{args.recent}", "HEAD"])

    first_seen = defaultdict(lambda: None)

    for c in commits:
        blobs = sh(["git", "ls-tree", "-r", "-z", c])
        blob_shas = [part for part in blobs if len(part) == 40]  # crude
        for sha in blob_shas:
            try:
                blob = subprocess.check_output(["git", "cat-file", "-p", sha], text=True, errors="ignore")
            except subprocess.CalledProcessError:
                continue
            for token, label in suspicious_strings(blob):
                if first_seen[token] is None:
                    first_seen[token] = (c, label)

    if not first_seen:
        print("No obvious secrets found.")
        print("Repository appears clean!")
        return

    print(f"\n🔑 Found {len(first_seen)} potential secrets:")
    for token, (commit, label) in first_seen.items():
        print(textwrap.dedent(f"""\
            ─────────────────────────────────────────
            Type     : {label}
            Commit   : {commit[:10]}
            Token    : {token[:6]}…{token[-4:]}   (len={len(token)})
            """))

    print(f"\nSummary: {len(first_seen)} secrets detected")
    print("If these are real secrets, please take immediate action!!")

    with open(".leak_report.json", "w") as f:
        json.dump(first_seen, f, indent=2)

if __name__ == "__main__":
    main()