# Guardrails Quick Reference

## 🚀 Quick Start

```python
from guardrails import create_guardrails

# Initialize
guardrails = create_guardrails()

# Validate input
is_valid, sanitized, error = guardrails.validate_input(user_query, session_id)
if not is_valid:
    return error  # Show error to user

# Process query...
response = process_query(sanitized)

# Validate output
is_valid, enhanced, error = guardrails.validate_output(response, sanitized)
return enhanced  # Return enhanced response with disclaimers
```

## 🛡️ Protection Features

### Input Validation
| Check | Limit | Error Message |
|-------|-------|---------------|
| Empty query | N/A | "Please enter a valid question" |
| Max length | 2000 chars | "Your question is too long" |
| Rate limit (per min) | 10 queries | "Too many requests. Please wait" |
| Rate limit (per hour) | 100 queries | "Reached hourly limit" |

### Prohibited Topics
❌ Blocked: pump and dump, insider trading, market manipulation, guaranteed returns, risk-free investment, get rich quick, penny stock tips, forex scams, ponzi/pyramid schemes

### Malicious Patterns
❌ Blocked: SQL injection, XSS attempts, excessive special characters (>30%)

### Output Sanitization
| Original | Replaced With |
|----------|---------------|
| "you must" | "you may want to" |
| "guaranteed returns" | "potential returns" |
| "risk-free" | "lower-risk" |

## 📊 Monitoring

```python
# Per-session stats
stats = guardrails.get_usage_stats("session_123")
# Returns: total_queries, queries_last_hour, queries_last_minute

# Overall stats
stats = guardrails.get_usage_stats()
# Returns: total_sessions, total_queries, active_sessions
```

## ⚙️ Configuration

Edit `guardrails.py`:

```python
# Rate limits
MAX_QUERIES_PER_MINUTE = 10
MAX_QUERIES_PER_HOUR = 100

# Input length
MAX_INPUT_LENGTH = 2000

# Add prohibited topics
PROHIBITED_TOPICS = [
    "crypto trading bots",
    # Add more...
]

# Add sensitive topics (extra disclaimers)
SENSITIVE_TOPICS = [
    "tax advice",
    # Add more...
]
```

## 🔍 Troubleshooting

### False Positives
1. Check logs: `logs/finance_assistant_YYYYMMDD.log`
2. Find failing check in `_check_prohibited_content()`
3. Adjust pattern matching or add exceptions

### Rate Limit Issues
1. Increase limits in `guardrails.py`
2. Implement user-specific rate limits
3. Add bypass for authenticated users

### Missing Disclaimers
1. Check `SENSITIVE_TOPICS` list
2. Review `_add_disclaimers()` logic
3. Verify query content matching

## 📝 Example Responses

### Valid Query
```
User: "What is diversification?"
✅ Passed all checks
→ Educational response + standard disclaimer
```

### Blocked Query
```
User: "How to manipulate markets?"
❌ Prohibited content detected
→ "I cannot assist with questions about market manipulation..."
```

### Rate Limited
```
User: [11th query in 1 minute]
❌ Rate limit exceeded
→ "Too many requests. Please wait a moment..."
```

### Sanitized Output
```
Agent: "You must invest now for guaranteed returns!"
✅ Sanitized
→ "You may want to consider investing for potential returns..."
+ disclaimers
```

## 🧪 Testing

```bash
# Run guardrails tests
pytest tests/test_guardrails.py -v

# Run demo
python3 demo_guardrails.py
```

## 📚 Full Documentation

See [GUARDRAILS.md](GUARDRAILS.md) for complete documentation.
