import pytest
from math import log2
from lykos.confidence import shannon_entropy, calculate_confidence

class TestShannonEntropy:
    def test_empty_string(self):
        assert shannon_entropy("") == 0.0
    
    def test_short_string(self):
        """entropy of strings shorter than 4 characters"""
        assert shannon_entropy("ab") == 0.0
        assert shannon_entropy("abc") == 0.0
    
    def test_uniform_distribution(self):
        """entropy of string with uniform character distribution"""
        result = shannon_entropy("abcd")
        expected = -4 * (0.25 * log2(0.25))
        assert abs(result - expected) < 1e-10
    
    def test_single_character(self):
        assert shannon_entropy("aaaa") == 0.0
        assert shannon_entropy("bbbbbbbb") == 0.0
    
    def test_mixed_distribution(self):
        # "aabcd" - 'a' appears twice, others once each
        result = shannon_entropy("aabcd")
        p_a = 2/5  # 'a' appears 2 times out of 5
        p_others = 1/5  # 'b', 'c', 'd' each appear once
        expected = -(p_a * log2(p_a) + 3 * (p_others * log2(p_others)))
        assert abs(result - expected) < 1e-10
    
    def test_high_entropy_token(self):
        high_entropy_token = "aB3x9K2mQ7nR4sT6uV8wX1yZ5"
        result = shannon_entropy(high_entropy_token)
        assert result > 4.0  

class TestCalculateConfidence:
    
    def test_basic_structure(self):
        result = calculate_confidence("test_token", "GitHub_Token", "api_key = 'test'", "config.py")
        
        assert isinstance(result, dict)
        assert "score" in result
        assert "level" in result
        assert "reasons" in result
        assert isinstance(result["score"], float)
        assert result["level"] in ["HIGH", "MEDIUM", "LOW", "VERY_LOW"]
        assert isinstance(result["reasons"], list)
    
    def test_strong_secret_types(self):
        strong_types = ["AWS_ACCESS_KEY", "AWS_SECRET_KEY", "Stripe_Live", "GitHub_Token"]
        
        for secret_type in strong_types:
            result = calculate_confidence("AKIAIOSFODNN7EXAMPLE", secret_type, "key = value", "config.py")
            assert "strong_pattern" in result["reasons"]
    
    def test_api_secret_types(self):
        api_types = ["OpenAI", "Anthropic"]
        
        for secret_type in api_types:
            result = calculate_confidence("sk-1234567890abcdef", secret_type, "api_key = value", "config.py")
            assert "api_pattern" in result["reasons"]
    
    def test_entropy_only_type(self):
        result = calculate_confidence("randomstring123", "HIGH-ENTROPY", "data = value", "script.py")
        assert "entropy_only" in result["reasons"]
    
    def test_documentation_files(self):
        doc_files = ["README.md", "docs/example.py", "sample_config.json", "demo.txt"]
        
        for file_path in doc_files:
            result = calculate_confidence("secret123", "GitHub_Token", "token = value", file_path)
            assert "documentation_file" in result["reasons"]
            assert result["score"] < 0.2 
    
    def test_test_files(self):
        """test confidence reduction for test files"""
        test_files = ["test_auth.py", "spec/config_spec.rb", "mock_data.json", "fixtures/test.py"]
        
        for file_path in test_files:
            result = calculate_confidence("secret123", "GitHub_Token", "token = value", file_path)
            assert "test_file" in result["reasons"]
            assert result["score"] < 0.2
    
    def test_template_files(self):
        """test confidence reduction for template files"""
        template_files = ["config.template", "settings.sample", "env.dist", "fake_config.py"]
        
        for file_path in template_files:
            result = calculate_confidence("secret123", "GitHub_Token", "token = value", file_path)
            assert "template_file" in result["reasons"]
            assert result["score"] < 0.2
    
    def test_production_files(self):
        prod_files = ["config/production.py", "settings.py", ".env", "app_config.json"]
        
        for file_path in prod_files:
            result = calculate_confidence("secret123", "GitHub_Token", "token = value", file_path)
            assert "production_file" in result["reasons"]
    
    def test_test_context_keywords(self):
        test_contexts = [
            "example_token = 'placeholder'",
            "# This is a dummy value for testing",
            "TODO: replace with real token",
            "fake_api_key = 'sample123'",
            "mock_secret = 'demo_value'"
        ]
        
        for context in test_contexts:
            result = calculate_confidence("secret123", "GitHub_Token", context, "config.py")
            assert "test_context" in result["reasons"]
            assert result["score"] < 0.1
    
    def test_commented_lines(self):
        comments = [
            "# api_key = 'secret123'",
            "// token = 'abc123'",
            "/* secret = 'hidden' */",
            "* password = 'test'",
            "-- db_pass = 'secret'"
        ]
        
        for comment in comments:
            result = calculate_confidence("secret123", "GitHub_Token", comment, "config.py")
            assert "commented_out" in result["reasons"]
    
    def test_variable_assignment_context(self):
        assignments = [
            "api_key = 'secret123'",
            "secret_token = 'abc'",
            "password = 'hidden'"
        ]
        
        for assignment in assignments:
            result = calculate_confidence("secret123", "GitHub_Token", assignment, "config.py")
            assert "variable_assignment" in result["reasons"]
    
    def test_environment_variable_usage(self):
        """confidence reduction for environment variable use"""
        env_contexts = [
            "token = os.environ.get('API_KEY')",
            "secret = getenv('SECRET_KEY')"
        ]
        
        for context in env_contexts:
            result = calculate_confidence("secret123", "GitHub_Token", context, "config.py")
            assert "env_var_usage" in result["reasons"]
    
    def test_entropy_levels(self):
        # high entroopy
        high_entropy = "aB3x9K2mQ7nR4sT6uV8wX1yZ5pD4fG7h"
        result_high = calculate_confidence(high_entropy, "HIGH-ENTROPY", "token = value", "script.py")
        
        medium_entropy = "abc123def456ghi789jkl"
        result_medium = calculate_confidence(medium_entropy, "HIGH-ENTROPY", "token = value", "script.py")
        
        # low entropy token
        very_low_entropy = "aaaaaaaa"
        result_very_low = calculate_confidence(very_low_entropy, "HIGH-ENTROPY", "token = value", "script.py")
        
        assert result_high["score"] > result_very_low["score"]
        assert result_medium["score"] > result_very_low["score"]
        
        high_entropy_reasons = result_high["reasons"]
        assert any(reason in high_entropy_reasons for reason in ["very_high_entropy", "moderate_entropy"])
        
        medium_entropy_reasons = result_medium["reasons"] 
        assert any(reason in medium_entropy_reasons for reason in ["moderate_entropy", "low_entropy"])
        
        assert "very_low_entropy" in result_very_low["reasons"]
    
    def test_token_length_effects(self):

        long_token = "a" * 60
        result_long = calculate_confidence(long_token, "GitHub_Token", "token = value", "config.py")
        assert "long_token" in result_long["reasons"]
        
        short_token = "abc123"
        result_short = calculate_confidence(short_token, "GitHub_Token", "token = value", "config.py")
        assert "short_token" in result_short["reasons"]
    
    def test_character_diversity(self):
        diverse_token = "aB3_+/"
        result_diverse = calculate_confidence(diverse_token, "GitHub_Token", "token = value", "config.py")
        assert "diverse_chars" in result_diverse["reasons"]
        
        limited_token = "aaaaaaaa"
        result_limited = calculate_confidence(limited_token, "GitHub_Token", "token = value", "config.py")
        assert "limited_chars" in result_limited["reasons"]
    
    def test_predictable_patterns(self):
        predictable_tokens = ["123456789", "abcdefghij", "fake_token_123", "test_secret"]
        
        for token in predictable_tokens:
            result = calculate_confidence(token, "GitHub_Token", "token = value", "config.py")
            assert "predictable_pattern" in result["reasons"]
            assert result["score"] < 0.1
    
    def test_confidence_bounds(self):
        result = calculate_confidence("secret123", "GitHub_Token", "token = value", "config.py")
        assert 0.01 <= result["score"] <= 1.0
    
    def test_confidence_levels(self):
        high_result = calculate_confidence(
            "AKIAIOSFODNN7EXAMPLE123",
            "AWS_ACCESS_KEY",
            "aws_access_key = 'value'",
            "production/config.py"
        )
        
        very_low_result = calculate_confidence(
            "fake123456",
            "GitHub_Token",
            "# example token for testing",
            "test/readme.md"
        )
        
        assert high_result["level"] in ["HIGH", "MEDIUM"]
        assert very_low_result["level"] == "VERY_LOW"
    
    def test_complex_scenarios(self):
        
        real_aws = calculate_confidence(
            "AKIAIHOPCMMNW7QRKXYZ",  # no trigger words like example etc
            "AWS_ACCESS_KEY",
            "AWS_ACCESS_KEY_ID = 'AKIAIHOPCMMNW7QRKXYZ'",
            "config/production.py"
        )
        assert real_aws["score"] > 0.5
        assert real_aws["level"] in ["MEDIUM", "HIGH"]
        
        commented_example = calculate_confidence(
            "fake_token_123",
            "GitHub_Token",
            "# github_token = 'your_token_here'  # example placeholder",
            "README.md"
        )
        assert commented_example["score"] < 0.05
        assert commented_example["level"] == "VERY_LOW"
        
        env_usage = calculate_confidence(
            "some_random_string",
            "HIGH-ENTROPY",
            "api_key = os.environ.get('API_KEY', 'some_random_string')",
            "app/main.py"
        )
        assert "env_var_usage" in env_usage["reasons"]
        assert "entropy_only" in env_usage["reasons"]


class TestEdgeCases:
    
    def test_empty_inputs(self):
        """empty inputs"""
        result = calculate_confidence("", "GitHub_Token", "", "")
        assert isinstance(result, dict)
        assert 0.01 <= result["score"] <= 1.0
    
    def test_special_characters(self):
        result = calculate_confidence(
            "token!@#$%^&*()",
            "GitHub_Token",
            "key = 'value with spaces and symbols !@#'",
            "path/with spaces/file.py"
        )
        assert isinstance(result, dict)
        assert 0.01 <= result["score"] <= 1.0
    
    def test_unicode_characters(self):
        """unicode characters"""
        result = calculate_confidence(
            "tökén_wíth_accénts",
            "GitHub_Token",
            "# cómment with ñ and ü",
            "fíle_nämé.py"
        )
        assert isinstance(result, dict)
        assert 0.01 <= result["score"] <= 1.0

if __name__ == "__main__":
    pytest.main([__file__])