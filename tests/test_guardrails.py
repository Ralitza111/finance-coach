"""
Unit tests for Finance Coach Guardrails System
Tests input validation, content safety, rate limiting, and output validation.
"""

import pytest
from datetime import datetime, timedelta
from guardrails import FinanceGuardrails, create_guardrails


class TestInputValidation:
    """Test input validation functionality."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_empty_query(self):
        """Test that empty queries are rejected."""
        is_valid, _, error = self.guardrails.validate_input("", "test_session")
        assert not is_valid
        assert "valid question" in error.lower()
    
    def test_whitespace_only_query(self):
        """Test that whitespace-only queries are rejected."""
        is_valid, _, error = self.guardrails.validate_input("   \n\t  ", "test_session")
        assert not is_valid
        assert "valid question" in error.lower()
    
    def test_excessive_length_query(self):
        """Test that overly long queries are rejected."""
        long_query = "a" * 2500  # Exceeds MAX_INPUT_LENGTH (2000)
        is_valid, _, error = self.guardrails.validate_input(long_query, "test_session")
        assert not is_valid
        assert "too long" in error.lower()
    
    def test_valid_query(self):
        """Test that valid queries pass validation."""
        is_valid, sanitized, error = self.guardrails.validate_input(
            "What is diversification?",
            "test_session"
        )
        assert is_valid
        assert sanitized == "What is diversification?"
        assert error is None
    
    def test_query_sanitization(self):
        """Test that queries are properly sanitized."""
        query = "What   is   \n\n diversification?   "
        is_valid, sanitized, _ = self.guardrails.validate_input(query, "test_session")
        assert is_valid
        assert "  " not in sanitized  # Multiple spaces removed
        assert sanitized.strip() == sanitized  # No leading/trailing whitespace


class TestProhibitedContent:
    """Test prohibited content detection."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_pump_and_dump_blocked(self):
        """Test that pump and dump schemes are blocked."""
        query = "How can I set up a pump and dump scheme?"
        is_valid, _, error = self.guardrails.validate_input(query, "test_session")
        assert not is_valid
        assert "pump and dump" in error.lower()
    
    def test_insider_trading_blocked(self):
        """Test that insider trading queries are blocked."""
        query = "How do I profit from insider trading information?"
        is_valid, _, error = self.guardrails.validate_input(query, "test_session")
        assert not is_valid
        assert "insider trading" in error.lower()
    
    def test_guaranteed_returns_blocked(self):
        """Test that guaranteed returns claims are blocked."""
        query = "Tell me about investments with guaranteed returns"
        is_valid, _, error = self.guardrails.validate_input(query, "test_session")
        assert not is_valid
        assert "guaranteed returns" in error.lower()
    
    def test_legitimate_query_not_blocked(self):
        """Test that legitimate queries are not blocked."""
        query = "What are the risks of investing in stocks?"
        is_valid, _, error = self.guardrails.validate_input(query, "test_session")
        assert is_valid


class TestMaliciousPatterns:
    """Test detection of malicious input patterns."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_sql_injection_blocked(self):
        """Test that SQL injection patterns are blocked."""
        query = "'; DROP TABLE users; --"
        is_valid, _, error = self.guardrails.validate_input(query, "test_session")
        assert not is_valid
        assert "cannot be processed" in error.lower() or "invalid" in error.lower()
    
    def test_script_injection_blocked(self):
        """Test that script injection attempts are blocked."""
        query = "<script>alert('xss')</script>"
        is_valid, _, error = self.guardrails.validate_input(query, "test_session")
        assert not is_valid
    
    def test_excessive_special_chars(self):
        """Test that queries with too many special characters are rejected."""
        query = "!!!@@@###$$$%%%^^^&&&***((())))))))"
        is_valid, _, error = self.guardrails.validate_input(query, "test_session")
        assert not is_valid
        assert "special characters" in error.lower()


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_per_minute_rate_limit(self):
        """Test that per-minute rate limit is enforced."""
        session_id = "rate_test_1"
        query = "What is a stock?"
        
        # First 10 queries should pass
        for i in range(10):
            is_valid, _, _ = self.guardrails.validate_input(query, session_id)
            assert is_valid, f"Query {i+1} should pass"
        
        # 11th query should fail
        is_valid, _, error = self.guardrails.validate_input(query, session_id)
        assert not is_valid
        assert "too many requests" in error.lower()
    
    def test_different_sessions_independent(self):
        """Test that different sessions have independent rate limits."""
        query = "What is a stock?"
        
        # Session 1: use 10 queries
        for i in range(10):
            is_valid, _, _ = self.guardrails.validate_input(query, "session_1")
            assert is_valid
        
        # Session 2: should still work
        is_valid, _, _ = self.guardrails.validate_input(query, "session_2")
        assert is_valid


class TestOutputValidation:
    """Test output validation functionality."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_empty_response_rejected(self):
        """Test that empty responses are rejected."""
        is_valid, _, error = self.guardrails.validate_output("", "test query")
        assert not is_valid
        assert "couldn't generate" in error.lower()
    
    def test_valid_response_passes(self):
        """Test that valid responses pass validation."""
        response = "Diversification is a risk management strategy..."
        is_valid, enhanced, error = self.guardrails.validate_output(response, "What is diversification?")
        assert is_valid
        assert enhanced  # Should return enhanced response
        assert error is None
    
    def test_prescriptive_language_sanitized(self):
        """Test that overly prescriptive language is sanitized."""
        response = "You must absolutely invest in this stock immediately!"
        is_valid, sanitized, _ = self.guardrails.validate_output(response, "test query")
        
        assert is_valid
        assert "must absolutely" not in sanitized.lower()
        assert "immediately" not in sanitized or "might consider" in sanitized
    
    def test_guaranteed_returns_sanitized(self):
        """Test that 'guaranteed returns' is replaced."""
        response = "This investment offers guaranteed returns of 10% per year."
        is_valid, sanitized, _ = self.guardrails.validate_output(response, "test query")
        
        assert is_valid
        assert "guaranteed returns" not in sanitized.lower()
        assert "potential returns" in sanitized.lower()
    
    def test_disclaimer_added_for_tax_query(self):
        """Test that tax disclaimers are added for tax-related queries."""
        response = "A Roth IRA allows tax-free withdrawals in retirement."
        query = "Should I choose Roth IRA or Traditional IRA for taxes?"
        
        is_valid, enhanced, _ = self.guardrails.validate_output(response, query)
        
        assert is_valid
        assert "tax disclaimer" in enhanced.lower() or "tax professional" in enhanced.lower()
    
    def test_disclaimer_added_for_investment_query(self):
        """Test that investment disclaimers are added for specific recommendations."""
        response = "Based on your portfolio, consider adding bonds."
        query = "Should I buy Tesla stock?"
        
        is_valid, enhanced, _ = self.guardrails.validate_output(response, query)
        
        assert is_valid
        # Should have some form of disclaimer
        assert len(enhanced) > len(response)


class TestUsageStats:
    """Test usage statistics and monitoring."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_session_stats(self):
        """Test that session statistics are tracked correctly."""
        session_id = "stats_test"
        query = "What is a stock?"
        
        # Make 5 queries
        for i in range(5):
            self.guardrails.validate_input(query, session_id)
        
        stats = self.guardrails.get_usage_stats(session_id)
        
        assert stats["session_id"] == session_id
        assert stats["total_queries"] == 5
        assert stats["queries_last_hour"] == 5
        assert stats["queries_last_minute"] == 5
    
    def test_overall_stats(self):
        """Test that overall statistics are calculated correctly."""
        # Make queries from multiple sessions
        for i in range(3):
            session_id = f"session_{i}"
            for j in range(2):
                self.guardrails.validate_input(f"Query {j}", session_id)
        
        stats = self.guardrails.get_usage_stats()
        
        assert stats["total_sessions"] >= 3
        assert stats["total_queries"] >= 6


class TestSanitization:
    """Test input and output sanitization."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_control_characters_removed(self):
        """Test that control characters are removed from input."""
        query = "What is\x00 a stock\x1F?"
        is_valid, sanitized, _ = self.guardrails.validate_input(query, "test_session")
        
        assert is_valid
        assert "\x00" not in sanitized
        assert "\x1F" not in sanitized
    
    def test_repeated_characters_limited(self):
        """Test that excessive repeated characters are limited."""
        query = "Hellooooooooooo world!!!!!!!!!!!!"
        is_valid, sanitized, _ = self.guardrails.validate_input(query, "test_session")
        
        assert is_valid
        # Should limit consecutive characters to 3
        assert "oooooooo" not in sanitized
        assert "!!!!!!!!" not in sanitized


# Integration Tests
class TestGuardrailsIntegration:
    """Test guardrails integration scenarios."""
    
    def setup_method(self):
        """Setup test instance."""
        self.guardrails = create_guardrails()
    
    def test_full_validation_flow(self):
        """Test complete validation flow from input to output."""
        # Valid query
        query = "What is diversification in investing?"
        session_id = "integration_test"
        
        # Step 1: Validate input
        is_valid, sanitized, error = self.guardrails.validate_input(query, session_id)
        assert is_valid
        assert sanitized == query
        
        # Step 2: Simulate agent response
        response = "Diversification is the practice of spreading investments across various assets to reduce risk."
        
        # Step 3: Validate output
        is_valid_output, enhanced, output_error = self.guardrails.validate_output(response, sanitized)
        assert is_valid_output
        assert len(enhanced) >= len(response)  # May have disclaimers added
    
    def test_blocked_query_flow(self):
        """Test that blocked queries stop the flow early."""
        query = "How to manipulate the stock market?"
        session_id = "blocked_test"
        
        # Should fail at input validation
        is_valid, sanitized, error = self.guardrails.validate_input(query, session_id)
        assert not is_valid
        assert error  # Should have error message
        assert "market manipulation" in error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
