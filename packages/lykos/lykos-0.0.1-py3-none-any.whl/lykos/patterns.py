import re

PATTERNS = {
    "AWS_ACCESS_KEY"      : r"AKIA[0-9A-Z]{16}",
    "AWS_SECRET_KEY"      : r"[A-Za-z0-9/+=]{40}",
    "AWS_TEMP_ACCESS_KEY" : r"ASIA[0-9A-Z]{16}",
    "Stripe_Live" : r"sk_live_[0-9A-Za-z]{20,34}",
    "Stripe_Test" : r"sk_test_[0-9A-Za-z]{24,32}",
    "OpenAI"      : r"sk-[A-Za-z0-9_-]{30,}",
    "OpenAI_Org"  : r"org-[A-Za-z0-9]{24}",
    "Anthropic"   : r"sk-ant-api03-[A-Za-z0-9_-]{40,}",
    "Deepseek"    : r"sk-[A-Za-z0-9]{20,29}",
    "Google_API"       : r"AIza[0-9A-Za-z_-]{35}",
    "Firebase_API_Key" : r"AIza[0-9A-Za-z_-]{35}",
    "Twilio_Account_SID" : r"AC[a-fA-F0-9]{32}",
    "Twilio_Auth_Token"  : r"[A-Fa-f0-9]{32}",
    "SendGrid_API_Key"   : r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}",
    "Discord_Bot_Token"  : r"[MNO][A-Za-z\d_-]{23,25}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27,39}",
    "GitHub_Token" : r"ghp_[A-Za-z0-9]{36}",
    "Bearer_Token" : r"[Bb]earer\s+[A-Za-z0-9+/=]{20,}",
    "JWT"          : r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
    "Private_Key"  : r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
    "Generic_Password": (
        r"(?ix)"
        r"(?:password|pwd|pass|passwd)"
        r"\s*[:=]\s*"
        r"['\"]?"
        r"(?=[^\s]{8,64}$)"
        r"(?=.*[A-Za-z])"
        r"(?=.*\d)"
        r"[A-Za-z\d!@#$%^&*()_+{}\[\]:;\"'.,<>/?\\|-]{8,64}"
        r"['\"]?"
    )
}

ENTROPY_REGEX = re.compile(r"[A-Za-z0-9+/=.#@!$%^&*_~\-]{20,}")

FALSE_POSITIVES = {
    "EXAMPLE_KEY", "YOUR_API_KEY_HERE", "xxxxxxxxxxxxxxxx", "[REDACTED]",
    
    "fake", "test", "sample", "demo", "mock", "example", "placeholder", 
    "dummy", "fakeuser", "testuser", "samplekey", "demokey",
    
    "your_key_here", "insert_key_here", "replace_with_your_key",
    "api_key_here", "secret_here", "token_here",
}

BINARY_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.exe', '.bin', 
    '.so', '.dll', '.dylib', '.zip', '.tar', '.gz', '.ico', '.whl',
    '.mp3', '.mp4', '.mov', '.woff', '.woff2', '.ttf', '.eot'
}

TEXT_SENSITIVE_EXTENSIONS = {
    '.env', '.yaml', '.yml', '.ini', '.conf', '.json', '.xml',
    '.txt', '.py', '.js', '.ts', '.java', '.rb', '.go', '.rs', '.php'
}

_user_whitelist_cache = None

def load_user_whitelist():
    global _user_whitelist_cache
    if _user_whitelist_cache is not None:
        return _user_whitelist_cache

    try:
        with open('.secretsignore', 'r') as f:
            _user_whitelist_cache = {line.strip() for line in f 
                                     if line.strip() and not line.startswith('#')}
    except FileNotFoundError:
        _user_whitelist_cache = set()
    return _user_whitelist_cache


def is_false_positive(token: str) -> bool:
    token_clean = token.strip()

    if token_clean in FALSE_POSITIVES:
        return True

    if token_clean in load_user_whitelist():
        return True

    if len(set(token_clean)) == 1:
        return True

    return False

__all__ = ["PATTERNS", "ENTROPY_REGEX", "FALSE_POSITIVES", "is_false_positive"]
