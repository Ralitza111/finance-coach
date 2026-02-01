# Guardrails Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FINANCE COACH WITH GUARDRAILS                        │
└─────────────────────────────────────────────────────────────────────────────┘

                                 USER QUERY
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │         🛡️ GUARDRAILS LAYER - INPUT VALIDATION        │
        └────────────────────────────────────────────────────────┘
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                        ▼                         ▼
        ╔═══════════════════════════════╗   ╔═══════════════════════════════╗
        ║   ✅ VALIDATION CHECKS        ║   ║   ❌ BLOCKED IF FAILS         ║
        ╠═══════════════════════════════╣   ╠═══════════════════════════════╣
        ║ 1. Empty/whitespace           ║   ║ • Empty query                 ║
        ║ 2. Length (max 2000 chars)    ║   ║ • Too long (>2000 chars)      ║
        ║ 3. Rate limiting              ║   ║ • Rate limit exceeded         ║
        ║    - 10/minute                ║   ║ • Prohibited content          ║
        ║    - 100/hour                 ║   ║   - Pump & dump               ║
        ║ 4. Prohibited content         ║   ║   - Insider trading           ║
        ║ 5. Malicious patterns         ║   ║   - Market manipulation       ║
        ║    - SQL injection            ║   ║   - Guaranteed returns        ║
        ║    - XSS attempts             ║   ║ • Malicious patterns          ║
        ║ 6. Sanitization               ║   ║   - SQL injection             ║
        ║    - Whitespace cleanup       ║   ║   - Script injection          ║
        ║    - Control chars            ║   ║   - Excessive special chars   ║
        ╚═══════════════════════════════╝   ╚═══════════════════════════════╝
                        │                         │
                        ▼                         ▼
                SANITIZED QUERY            ERROR MESSAGE
                        │                         │
                        │                         └──────► User
                        ▼
        ┌────────────────────────────────────────────────────────┐
        │           🤖 INTENT ANALYSIS (LLM-powered)             │
        │   • Safety check                                       │
        │   • Educational vs specific advice                     │
        │   • Risk level assessment                              │
        └────────────────────────────────────────────────────────┘
                        │
                        ├─ Safe ──────────────┐
                        │                      │
                        └─ Unsafe ─────► Block query
                        │
                        ▼
        ┌────────────────────────────────────────────────────────┐
        │              🔀 QUERY ROUTER                           │
        │   Selects appropriate agent(s)                         │
        └────────────────────────────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────────────┐
        │          🤖 SPECIALIZED AGENTS                         │
        │                                                         │
        │  💬 Finance Q&A    📊 Portfolio    📈 Market Analyst  │
        │  🎯 Goal Planner   💰 Tax Educator                    │
        └────────────────────────────────────────────────────────┘
                        │
                        ▼
                  AGENT RESPONSE
                        │
                        ▼
        ┌────────────────────────────────────────────────────────┐
        │         🛡️ GUARDRAILS LAYER - OUTPUT VALIDATION       │
        └────────────────────────────────────────────────────────┘
                        │
                        ▼
        ╔═══════════════════════════════════════════════════════╗
        ║           OUTPUT SANITIZATION & ENHANCEMENT           ║
        ╠═══════════════════════════════════════════════════════╣
        ║ 1. Empty response check                               ║
        ║                                                        ║
        ║ 2. Prescriptive language sanitization:                ║
        ║    • "you must" → "you may want to"                   ║
        ║    • "guaranteed returns" → "potential returns"       ║
        ║    • "risk-free" → "lower-risk"                       ║
        ║                                                        ║
        ║ 3. Context-aware disclaimer addition:                 ║
        ║    • Tax queries → Tax disclaimer                     ║
        ║    • Investment queries → Investment disclaimer       ║
        ║    • Legal queries → Legal disclaimer                 ║
        ║    • All queries → General educational disclaimer     ║
        ╚═══════════════════════════════════════════════════════╝
                        │
                        ▼
              ENHANCED RESPONSE + DISCLAIMERS
                        │
                        ▼
                     USER 👤


┌─────────────────────────────────────────────────────────────────────────────┐
│                           📊 MONITORING LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Session Tracking:                Rate Limiting:                           │
│  • Query history                  • 10 queries/minute                      │
│  • Timestamps                     • 100 queries/hour                       │
│  • Pattern analysis               • Per-session isolation                 │
│                                                                             │
│  Logging:                         Statistics:                              │
│  • All validations                • Total queries                          │
│  • Blocked queries                • Active sessions                        │
│  • Sanitizations                  • Usage patterns                         │
│  • Rate limit events              • Anomaly detection                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════

EXAMPLE FLOWS:

1️⃣  VALID QUERY FLOW:
   User: "What is diversification?"
   ✅ Input validation → ✅ Intent check → 🔀 Route to Finance Q&A Agent
   → 🤖 Generate response → ✅ Output validation → 📋 Add disclaimer
   → ✅ Return enhanced response

2️⃣  BLOCKED QUERY FLOW (Prohibited Content):
   User: "How to pump and dump stocks?"
   ❌ Input validation FAILS → Prohibited content detected
   → ⚠️ Return error message → Stop processing

3️⃣  RATE LIMITED FLOW:
   User: [11th query in 1 minute]
   ❌ Rate limit check FAILS → Too many requests
   → ⚠️ Return rate limit message → Stop processing

4️⃣  SANITIZED OUTPUT FLOW:
   User: "Should I invest in Tesla?"
   ✅ Input validation → ✅ Intent check (flagged as specific advice)
   → 🔀 Route to Portfolio Analyzer → 🤖 Generate: "You must invest now!"
   → ✅ Output sanitization: "You may want to consider investing"
   → 📋 Add extra disclaimers → ✅ Return sanitized + enhanced response

═══════════════════════════════════════════════════════════════════════════════

KEY BENEFITS:

🔒 SECURITY            💼 COMPLIANCE           🎯 USER PROTECTION
• SQL injection        • Educational focus     • Blocks harmful content
  blocking             • Auto-disclaimers      • Prevents bad advice
• XSS prevention       • Risk warnings         • Rate limit protection
• Input sanitization   • Professional refs     • Clear error messages

📊 MONITORING          🧪 TESTED              📚 DOCUMENTED
• Usage tracking       • 26+ unit tests       • Full documentation
• Pattern detection    • Integration tests    • Quick reference
• Anomaly detection    • All tests passing    • Demo script

═══════════════════════════════════════════════════════════════════════════════
