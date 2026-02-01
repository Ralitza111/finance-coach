"""
Guardrails Demo Script
Demonstrates various guardrail features and protections.
"""

from guardrails import create_guardrails


def print_result(title, is_valid, message, sanitized=None):
    """Print formatted result."""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    if is_valid:
        print("✅ PASSED")
        if sanitized:
            print(f"Sanitized Query: {sanitized}")
    else:
        print("❌ BLOCKED")
    print(f"Message: {message}")


def main():
    """Run guardrails demonstration."""
    print("\n" + "="*60)
    print("🛡️  FINANCE COACH GUARDRAILS DEMONSTRATION")
    print("="*60)
    
    # Initialize guardrails
    guardrails = create_guardrails()
    
    # Test 1: Valid query
    print("\n\n📝 VALID QUERIES")
    query = "What is diversification in investing?"
    is_valid, sanitized, error = guardrails.validate_input(query, "demo_session")
    print_result(
        "Valid Educational Query",
        is_valid,
        error if error else "Query accepted and sanitized",
        sanitized
    )
    
    # Test 2: Prohibited content - pump and dump
    print("\n\n🚫 PROHIBITED CONTENT DETECTION")
    query = "How can I set up a pump and dump scheme?"
    is_valid, sanitized, error = guardrails.validate_input(query, "demo_session")
    print_result(
        "Prohibited Topic: Pump and Dump",
        is_valid,
        error if error else "Allowed"
    )
    
    # Test 3: Prohibited content - insider trading
    query = "How do I profit from insider trading?"
    is_valid, sanitized, error = guardrails.validate_input(query, "demo_session")
    print_result(
        "Prohibited Topic: Insider Trading",
        is_valid,
        error if error else "Allowed"
    )
    
    # Test 4: Malicious pattern - SQL injection
    print("\n\n🔒 MALICIOUS PATTERN DETECTION")
    query = "'; DROP TABLE users; --"
    is_valid, sanitized, error = guardrails.validate_input(query, "demo_session")
    print_result(
        "SQL Injection Attempt",
        is_valid,
        error if error else "Allowed"
    )
    
    # Test 5: Script injection
    query = "<script>alert('xss')</script>"
    is_valid, sanitized, error = guardrails.validate_input(query, "demo_session")
    print_result(
        "Script Injection Attempt",
        is_valid,
        error if error else "Allowed"
    )
    
    # Test 6: Input sanitization
    print("\n\n🧹 INPUT SANITIZATION")
    query = "What   is    a   stock?   \n\n  "
    is_valid, sanitized, error = guardrails.validate_input(query, "demo_session")
    print_result(
        "Excessive Whitespace Removal",
        is_valid,
        error if error else "Sanitized successfully",
        sanitized
    )
    
    # Test 7: Length validation
    print("\n\n📏 LENGTH VALIDATION")
    query = "a" * 2500  # Exceeds 2000 char limit
    is_valid, sanitized, error = guardrails.validate_input(query, "demo_session")
    print_result(
        "Excessive Query Length (2500 chars)",
        is_valid,
        error if error else "Allowed"
    )
    
    # Test 8: Rate limiting
    print("\n\n⏱️  RATE LIMITING")
    print("\nSimulating rapid-fire queries...")
    rate_limit_session = "rate_test"
    test_query = "What is a stock?"
    
    for i in range(12):
        is_valid, _, error = guardrails.validate_input(test_query, rate_limit_session)
        if i < 10:
            status = "✅ PASS" if is_valid else "❌ FAIL"
            print(f"Query {i+1}/12: {status}")
        else:
            print(f"\nQuery {i+1}/12 (should be rate limited):")
            print_result(
                f"Rate Limit Test - Query {i+1}",
                is_valid,
                error if error else "Allowed"
            )
    
    # Test 9: Output validation and sanitization
    print("\n\n📤 OUTPUT VALIDATION & SANITIZATION")
    
    # Prescriptive language
    response = "You must absolutely invest in this stock immediately for guaranteed returns!"
    query_context = "What should I invest in?"
    is_valid, sanitized, error = guardrails.validate_output(response, query_context)
    print_result(
        "Prescriptive Language Sanitization",
        is_valid,
        "Original had prescriptive language, now sanitized" if is_valid else error,
        sanitized[:100] + "..." if len(sanitized) > 100 else sanitized
    )
    
    # Test 10: Disclaimer addition
    print("\n\n📋 AUTOMATIC DISCLAIMER ADDITION")
    response = "A Roth IRA allows tax-free withdrawals in retirement."
    query_context = "Should I choose Roth or Traditional IRA?"
    is_valid, enhanced, error = guardrails.validate_output(response, query_context)
    print(f"\nOriginal Response Length: {len(response)} chars")
    print(f"Enhanced Response Length: {len(enhanced)} chars")
    print(f"Disclaimers Added: {'Yes' if len(enhanced) > len(response) else 'No'}")
    if len(enhanced) > len(response):
        print("\nAdded Disclaimers Preview:")
        disclaimer_part = enhanced[len(response):]
        print(disclaimer_part[:200] + "..." if len(disclaimer_part) > 200 else disclaimer_part)
    
    # Test 11: Usage statistics
    print("\n\n📊 USAGE STATISTICS")
    stats = guardrails.get_usage_stats(rate_limit_session)
    print(f"\nSession: {stats['session_id']}")
    print(f"Total Queries: {stats['total_queries']}")
    print(f"Last Hour: {stats['queries_last_hour']}")
    print(f"Last Minute: {stats['queries_last_minute']}")
    
    overall_stats = guardrails.get_usage_stats()
    print(f"\nOverall Statistics:")
    print(f"Total Sessions: {overall_stats['total_sessions']}")
    print(f"Total Queries: {overall_stats['total_queries']}")
    print(f"Active Sessions: {overall_stats['active_sessions']}")
    
    # Summary
    print("\n\n" + "="*60)
    print("🎯 DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nThe guardrails system provides:")
    print("✅ Input validation and sanitization")
    print("✅ Prohibited content detection")
    print("✅ Malicious pattern blocking")
    print("✅ Rate limiting protection")
    print("✅ Output sanitization")
    print("✅ Automatic disclaimer addition")
    print("✅ Usage monitoring and statistics")
    print("\n📚 For full documentation, see GUARDRAILS.md")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
