from math import log2

ENTROPY_THRESHOLD = 4.5

def shannon_entropy(s: str) -> float:
    if not s or len(s) < 4:
        return 0.0
    p = [s.count(c) / len(s) for c in set(s)]
    return -sum(x * log2(x) for x in p if x > 0)

def calculate_confidence(token: str, secret_type: str, line_context: str, file_path: str) -> dict:
    confidence = 1.0
    reasons = []

    if secret_type in {"AWS_ACCESS_KEY", "AWS_SECRET_KEY", "Stripe_Live", "GitHub_Token"}:
        confidence *= 1.3
        reasons.append("strong_pattern")
    elif secret_type in {"OpenAI", "Anthropic"}:
        confidence *= 1.2
        reasons.append("api_pattern")
    elif secret_type == "HIGH-ENTROPY":
        confidence *= 0.7
        reasons.append("entropy_only")

    f_low = file_path.lower()
    if any(w in f_low for w in ("readme", "doc", "example", "sample", "demo")):
        confidence *= 0.1
        reasons.append("documentation_file")
    if any(w in f_low for w in ("test", "spec", "mock", "fixture")):
        confidence *= 0.1
        reasons.append("test_file")
    if any(w in f_low for w in ("template", ".sample", ".dist", "fake")):
        confidence *= 0.1
        reasons.append("template_file")
    if any(w in f_low for w in ("config", "settings", "env", "production")):
        confidence *= 1.2
        reasons.append("production_file")

    l_low = line_context.lower()
    
    test_words = ["example", "placeholder", "dummy", "fake", "todo", "fixme", 
                  "test", "sample", "demo", "mock", "template"]
    if any(w in l_low for w in test_words):
        confidence *= 0.05
        reasons.append("test_context")

    stripped = line_context.lstrip()
    if stripped.startswith(("#", "//", "/*", "*", "--")):
        confidence *= 0.3
        reasons.append("commented_out")

    if any(w in l_low for w in ("api_key", "secret", "token", "password")):
        confidence *= 1.1
        reasons.append("variable_assignment")
    if "os.environ" in line_context or "getenv" in line_context:
        confidence *= 0.8
        reasons.append("env_var_usage")

    ent = shannon_entropy(token)
    if ent >= 5.5:
        confidence *= 1.2
        reasons.append("very_high_entropy")
    elif ent >= 4.2:
        confidence *= 1.0
        reasons.append("moderate_entropy")
    elif ent >= 3.0:
        confidence *= 0.6
        reasons.append("low_entropy")
    else:
        confidence *= 0.3
        reasons.append("very_low_entropy")

    if len(token) > 50:
        confidence *= 1.05
        reasons.append("long_token")
    elif len(token) < 20:
        confidence *= 0.6
        reasons.append("short_token")

    chars = sum((any(c.islower() for c in token),
                 any(c.isupper() for c in token),
                 any(c.isdigit() for c in token),
                 any(c in "+/=_-" for c in token)))
    if chars >= 3:
        confidence *= 1.05
        reasons.append("diverse_chars")
    elif chars <= 1:
        confidence *= 0.5
        reasons.append("limited_chars")

    if any(pattern in token.lower() for pattern in ['123456', 'abcdef', 'fake', 'test']):
        confidence *= 0.05
        reasons.append("predictable_pattern")

    confidence = max(0.01, min(1.0, confidence))
    
    level = ("HIGH" if confidence >= 0.8 else
             "MEDIUM" if confidence >= 0.5 else
             "LOW" if confidence >= 0.2 else
             "VERY_LOW")
    
    return {
        "score": round(confidence, 3),
        "level": level,
        "reasons": reasons
    }