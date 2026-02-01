# Finance Coach Guardrails System

## Overview

The Finance Coach application now includes a comprehensive guardrails system to ensure safe, compliant, and responsible AI interactions. This system protects both users and the application from inappropriate content, abuse, and compliance violations.

## Features

### 1. **Input Validation**
- **Length Limits**: Prevents excessively long queries (max 2000 characters)
- **Sanitization**: Removes control characters and normalizes whitespace
- **Pattern Detection**: Identifies and blocks malicious patterns (SQL injection, XSS attempts)
- **Empty Query Prevention**: Rejects empty or whitespace-only inputs

### 2. **Content Safety**
- **Prohibited Topics Detection**: Blocks queries about:
  - Crypto trading bots
  - Pump and dump schemes
  - Insider trading
  - Market manipulation
  - Guaranteed returns / risk-free investments
  - Get rich quick schemes
  - Penny stock tips
  - Forex scams
  - Ponzi/pyramid schemes

- **Sensitive Topics Flagging**: Extra disclaimers for:
  - Tax advice
  - Legal advice
  - Specific investment recommendations
  - Medical expenses
  - Bankruptcy
  - Divorce finances
  - Estate planning

### 3. **Rate Limiting**
- **Per-Minute Limit**: 10 queries per minute per session
- **Per-Hour Limit**: 100 queries per hour per session
- **Automatic Cleanup**: Old query records are automatically removed

### 4. **Output Validation**
- **Empty Response Check**: Ensures agents generate meaningful responses
- **Disclaimer Addition**: Automatically adds appropriate disclaimers based on query content
- **Language Sanitization**: Replaces overly prescriptive language with educational alternatives
  - "you must" → "you may want to"
  - "guaranteed returns" → "potential returns"
  - "risk-free" → "lower-risk"

### 5. **Intent Analysis (LLM-Powered)**
- Analyzes query safety and appropriateness
- Determines if query requests specific advice vs. general education
- Identifies high-risk or speculative topics
- Provides reasoning for safety decisions

### 6. **Monitoring & Analytics**
- Session-based usage tracking
- Query history per session
- Active session monitoring
- Usage statistics for abuse detection

## Technical Implementation

### Architecture

```
User Query
    ↓
Input Validation (guardrails.validate_input)
    ↓
Intent Check (guardrails.check_query_intent)
    ↓
Query Routing (multi_agent_router)
    ↓
Agent Execution (specialized_agents)
    ↓
Output Validation (guardrails.validate_output)
    ↓
Enhanced Response with Disclaimers
```

### Key Components

#### `guardrails.py`
Main guardrails module with:
- `FinanceGuardrails` class
- Input/output validation methods
- Rate limiting logic
- Content safety checks
- Monitoring utilities

#### `app.py` Integration
- Guardrails initialized during system startup
- Integrated into `process_query()` method
- Applied to all user queries automatically

## Usage Examples

### Example 1: Normal Query (Passes All Checks)
```
User: "What is diversification in investing?"
✅ Input validation: PASS
✅ Intent check: PASS (educational)
✅ Processing: Routed to Finance Q&A Agent
✅ Output validation: PASS
→ Response with educational content + standard disclaimer
```

### Example 2: Prohibited Topic (Blocked)
```
User: "How can I set up a pump and dump scheme?"
❌ Input validation: FAIL
→ Error: "I cannot assist with questions about pump and dump..."
```

### Example 3: Rate Limit Exceeded
```
User: [11th query in one minute]
❌ Rate limit: FAIL
→ Error: "Too many requests. Please wait a moment..."
```

### Example 4: Sensitive Topic (Extra Disclaimers)
```
User: "Should I put all my retirement savings in Tesla stock?"
✅ Input validation: PASS
✅ Intent check: PASS (but flagged as specific advice)
✅ Processing: Routed to Portfolio Analyzer
✅ Output validation: PASS
→ Response + Investment Disclaimer + General Disclaimer
```

## Configuration

### Rate Limits
Adjust in `guardrails.py`:
```python
MAX_QUERIES_PER_MINUTE = 10  # Default: 10
MAX_QUERIES_PER_HOUR = 100   # Default: 100
```

### Input Length
Adjust in `guardrails.py`:
```python
MAX_INPUT_LENGTH = 2000  # Default: 2000 characters
```

### Prohibited Topics
Add to `PROHIBITED_TOPICS` list in `guardrails.py`:
```python
PROHIBITED_TOPICS = [
    "crypto trading bots",
    "pump and dump",
    # Add more...
]
```

### Sensitive Topics
Add to `SENSITIVE_TOPICS` list in `guardrails.py`:
```python
SENSITIVE_TOPICS = [
    "tax advice",
    "legal advice",
    # Add more...
]
```

## Logging

All guardrails actions are logged:
```
INFO - FinanceGuardrails initialized
INFO - Validating input for session default
WARNING - Prohibited topic detected: pump and dump
INFO - ✅ Input validation passed
WARNING - Rate limit exceeded for session abc123 (per-minute)
INFO - ✅ Output validation passed
```

Logs are saved to: `logs/finance_assistant_YYYYMMDD.log`

## Monitoring

### Get Usage Statistics
```python
# Per session
stats = assistant.guardrails.get_usage_stats(session_id="user123")
# Returns: {
#     "session_id": "user123",
#     "total_queries": 45,
#     "queries_last_hour": 12,
#     "queries_last_minute": 3
# }

# Overall
stats = assistant.guardrails.get_usage_stats()
# Returns: {
#     "total_sessions": 10,
#     "total_queries": 150,
#     "active_sessions": 5
# }
```

## Compliance Benefits

### Financial Regulations
✅ **Educational Focus**: Enforces educational content vs. specific advice
✅ **Disclaimers**: Automatic addition of appropriate disclaimers
✅ **Risk Warnings**: Flags and handles high-risk topics appropriately
✅ **Licensed Professional Referrals**: Recommends consulting licensed professionals

### Data Protection
✅ **Input Sanitization**: Prevents injection attacks
✅ **Session Isolation**: Separate tracking per session
✅ **No PII Storage**: Doesn't store personal information

### Platform Safety
✅ **Rate Limiting**: Prevents abuse and DoS attacks
✅ **Content Filtering**: Blocks inappropriate/illegal content
✅ **Monitoring**: Tracks usage patterns for anomaly detection

## Testing Guardrails

### Test Prohibited Content
```python
query = "How do I manipulate stock prices?"
is_valid, sanitized, error = guardrails.validate_input(query)
assert not is_valid
assert "cannot assist" in error.lower()
```

### Test Rate Limiting
```python
session_id = "test_session"
# Send 11 queries in quick succession
for i in range(11):
    is_valid, _, error = guardrails.validate_input(f"Query {i}", session_id)
    if i < 10:
        assert is_valid
    else:
        assert not is_valid
        assert "too many requests" in error.lower()
```

### Test Output Sanitization
```python
response = "You must absolutely invest in this stock for guaranteed returns!"
is_valid, sanitized, _ = guardrails.validate_output(response, "test query")
assert "must absolutely" not in sanitized.lower()
assert "guaranteed returns" not in sanitized.lower()
```

## Future Enhancements

### Planned Features
- [ ] User authentication and personalized rate limits
- [ ] Machine learning-based anomaly detection
- [ ] Sentiment analysis for query intent
- [ ] Multi-language support for content filtering
- [ ] Real-time compliance rule updates
- [ ] Integration with external content moderation APIs
- [ ] Advanced abuse pattern detection
- [ ] Automatic reporting for serious violations

### Configuration UI
- [ ] Admin dashboard for guardrails configuration
- [ ] Real-time monitoring dashboard
- [ ] Usage analytics visualization
- [ ] Alert system for suspicious activity

## Troubleshooting

### Issue: False Positives
**Problem**: Legitimate queries are being blocked

**Solution**: 
1. Check logs to identify which check failed
2. Adjust pattern matching in `_check_prohibited_content()`
3. Add exceptions for specific terms if needed

### Issue: Rate Limit Too Restrictive
**Problem**: Legitimate users hitting rate limits

**Solution**:
1. Increase `MAX_QUERIES_PER_MINUTE` or `MAX_QUERIES_PER_HOUR`
2. Implement user-specific rate limits
3. Add rate limit bypass for authenticated users

### Issue: Excessive Disclaimers
**Problem**: Too many disclaimers on responses

**Solution**:
1. Adjust `SENSITIVE_TOPICS` list to reduce false triggers
2. Modify `_add_disclaimers()` logic to consolidate disclaimers
3. Check query content more precisely before adding disclaimers

## Support

For questions or issues with the guardrails system:
1. Check logs in `logs/finance_assistant_YYYYMMDD.log`
2. Review error messages for specific failure reasons
3. Consult this documentation for configuration options
4. Contact the development team for assistance

## License

This guardrails system is part of the Finance Coach application and follows the same license terms.

---

**Last Updated**: February 1, 2026
**Version**: 1.0.0
