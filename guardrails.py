"""
Guardrails for AI Finance Assistant
Implements safety checks, input validation, and compliance measures.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class FinanceGuardrails:
    """
    Comprehensive guardrails system for financial AI assistant.
    
    Features:
    - Input validation and sanitization
    - Content safety checks
    - Financial compliance validation
    - Rate limiting
    - Prohibited content detection
    - Response validation
    """
    
    # Prohibited topics that should not be handled
    PROHIBITED_TOPICS = [
        "crypto trading bots",
        "pump and dump",
        "insider trading",
        "market manipulation",
        "guaranteed returns",
        "risk-free investment",
        "get rich quick",
        "penny stock tips",
        "forex scam",
        "ponzi scheme",
        "pyramid scheme",
    ]
    
    # Sensitive topics requiring extra disclaimers
    SENSITIVE_TOPICS = [
        "tax advice",
        "legal advice",
        "specific investment recommendation",
        "medical expenses",
        "bankruptcy",
        "divorce finances",
        "estate planning",
    ]
    
    # Maximum input length
    MAX_INPUT_LENGTH = 2000
    
    # Rate limiting settings
    MAX_QUERIES_PER_MINUTE = 10
    MAX_QUERIES_PER_HOUR = 100
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """Initialize guardrails system."""
        self.llm = llm
        self.query_history = defaultdict(list)  # Track queries by session
        logger.info("FinanceGuardrails initialized")
    
    def validate_input(self, query: str, session_id: str = "default") -> Tuple[bool, str, Optional[str]]:
        """
        Comprehensive input validation.
        
        Args:
            query: User's input query
            session_id: Session identifier for rate limiting
            
        Returns:
            Tuple of (is_valid, sanitized_query, error_message)
            - is_valid: True if query passes all checks
            - sanitized_query: Cleaned version of query
            - error_message: Error description if invalid, None if valid
        """
        logger.info(f"Validating input for session {session_id}")
        
        # Check 1: Empty or whitespace only
        if not query or not query.strip():
            return False, "", "⚠️ Please enter a valid question."
        
        # Check 2: Length validation
        if len(query) > self.MAX_INPUT_LENGTH:
            return False, "", f"⚠️ Your question is too long. Please limit to {self.MAX_INPUT_LENGTH} characters (current: {len(query)})."
        
        # Check 3: Rate limiting
        rate_limit_ok, rate_limit_msg = self._check_rate_limit(session_id)
        if not rate_limit_ok:
            return False, "", rate_limit_msg
        
        # Check 4: Sanitize input
        sanitized_query = self._sanitize_input(query)
        
        # Check 5: Check for prohibited content
        is_safe, safety_msg = self._check_prohibited_content(sanitized_query)
        if not is_safe:
            return False, "", safety_msg
        
        # Check 6: Check for malicious patterns
        is_safe_pattern, pattern_msg = self._check_malicious_patterns(sanitized_query)
        if not is_safe_pattern:
            return False, "", pattern_msg
        
        # Record successful validation
        self._record_query(session_id)
        
        logger.info("✅ Input validation passed")
        return True, sanitized_query, None
    
    def _sanitize_input(self, query: str) -> str:
        """Remove potentially harmful characters and normalize input."""
        # Remove excessive whitespace
        sanitized = " ".join(query.split())
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)
        
        # Limit repeated characters (prevent spam patterns)
        sanitized = re.sub(r'(.)\1{4,}', r'\1\1\1', sanitized)
        
        return sanitized.strip()
    
    def _check_prohibited_content(self, query: str) -> Tuple[bool, str]:
        """Check if query contains prohibited financial topics."""
        query_lower = query.lower()
        
        for prohibited in self.PROHIBITED_TOPICS:
            if prohibited in query_lower:
                logger.warning(f"Prohibited topic detected: {prohibited}")
                return False, f"""⚠️ I cannot assist with questions about {prohibited}.

This topic may involve:
- Illegal activities
- Unethical financial practices
- High-risk schemes

I'm designed to provide educational financial information and promote responsible investing practices.

Please ask me about:
- General financial concepts
- Investment education
- Retirement planning
- Portfolio diversification
- Tax-advantaged accounts"""
        
        return True, ""
    
    def _check_malicious_patterns(self, query: str) -> Tuple[bool, str]:
        """Detect potentially malicious input patterns."""
        # Check for SQL injection patterns
        sql_patterns = [
            r"(?i)(union\s+select|drop\s+table|delete\s+from|insert\s+into)",
            r"(?i)(--|\;|\/\*|\*\/)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, query):
                logger.warning("Potential SQL injection pattern detected")
                return False, "⚠️ Your query contains characters that cannot be processed. Please rephrase."
        
        # Check for script injection
        script_patterns = [
            r"(?i)<script",
            r"(?i)javascript:",
            r"(?i)onerror\s*=",
            r"(?i)onclick\s*=",
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, query):
                logger.warning("Potential script injection detected")
                return False, "⚠️ Your query contains invalid formatting. Please use plain text."
        
        # Check for excessive special characters (potential obfuscation)
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\.\,\?\!\-\(\)\$\%]', query)) / len(query) if query else 0
        if special_char_ratio > 0.3:
            logger.warning(f"Excessive special characters: {special_char_ratio:.2%}")
            return False, "⚠️ Your query contains too many special characters. Please simplify."
        
        return True, ""
    
    def _check_rate_limit(self, session_id: str) -> Tuple[bool, str]:
        """Check if session has exceeded rate limits."""
        now = datetime.now()
        session_queries = self.query_history[session_id]
        
        # Clean old queries
        one_hour_ago = now - timedelta(hours=1)
        session_queries = [q for q in session_queries if q > one_hour_ago]
        self.query_history[session_id] = session_queries
        
        # Check per-minute limit
        one_minute_ago = now - timedelta(minutes=1)
        recent_queries = [q for q in session_queries if q > one_minute_ago]
        
        if len(recent_queries) >= self.MAX_QUERIES_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for session {session_id} (per-minute)")
            return False, f"⚠️ Too many requests. Please wait a moment before asking another question. (Limit: {self.MAX_QUERIES_PER_MINUTE} per minute)"
        
        # Check per-hour limit
        if len(session_queries) >= self.MAX_QUERIES_PER_HOUR:
            logger.warning(f"Rate limit exceeded for session {session_id} (per-hour)")
            return False, f"⚠️ You've reached the hourly limit of {self.MAX_QUERIES_PER_HOUR} questions. Please try again later."
        
        return True, ""
    
    def _record_query(self, session_id: str):
        """Record a query timestamp for rate limiting."""
        self.query_history[session_id].append(datetime.now())
    
    def validate_output(self, response: str, query: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate agent response before returning to user.
        
        Args:
            response: Agent's response
            query: Original user query
            
        Returns:
            Tuple of (is_valid, enhanced_response, warning_message)
        """
        logger.info("Validating output response")
        
        # Check 1: Empty response
        if not response or not response.strip():
            logger.warning("Empty response generated")
            return False, "", "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
        
        # Check 2: Check if response contains sensitive topic disclaimers
        enhanced_response = self._add_disclaimers(response, query)
        
        # Check 3: Check for inappropriate financial advice language
        enhanced_response = self._sanitize_output(enhanced_response)
        
        logger.info("✅ Output validation passed")
        return True, enhanced_response, None
    
    def _add_disclaimers(self, response: str, query: str) -> str:
        """Add appropriate disclaimers based on query content."""
        query_lower = query.lower()
        disclaimers = []
        
        # Check for sensitive topics
        for sensitive in self.SENSITIVE_TOPICS:
            if sensitive in query_lower:
                if "tax" in sensitive.lower():
                    disclaimers.append("📋 **Tax Disclaimer**: Tax laws are complex and vary by location and situation. This is educational information only. Consult a certified tax professional or CPA for tax advice specific to your situation.")
                elif "legal" in sensitive.lower():
                    disclaimers.append("⚖️ **Legal Disclaimer**: This is not legal advice. Consult a licensed attorney for legal matters.")
                elif "investment" in sensitive.lower():
                    disclaimers.append("📈 **Investment Disclaimer**: This is educational information, not investment advice. All investments carry risk. Consult a licensed financial advisor before making investment decisions.")
        
        # Always add general disclaimer if not already present
        if "not financial advice" not in response.lower() and "educational purposes" not in response.lower():
            disclaimers.append("⚠️ **General Disclaimer**: This information is for educational purposes only and does not constitute financial, investment, tax, or legal advice. Always consult qualified professionals before making financial decisions.")
        
        # Add disclaimers to response
        if disclaimers:
            disclaimer_text = "\n\n---\n\n" + "\n\n".join(disclaimers)
            return response + disclaimer_text
        
        return response
    
    def _sanitize_output(self, response: str) -> str:
        """
        Sanitize output to ensure it doesn't contain inappropriate financial advice language.
        
        Replaces overly prescriptive language with educational alternatives.
        """
        # Patterns to check and replace
        prescriptive_patterns = {
            r'\byou should (definitely|absolutely|certainly|immediately)\b': 'you might consider',
            r'\byou must\b': 'you may want to',
            r'\bI recommend that you\b': 'one option to consider is',
            r'\bguaranteed (returns|profit|gains)\b': 'potential returns',
            r'\brisk-free\b': 'lower-risk',
            r'\bcan\'t lose\b': 'historically stable',
        }
        
        sanitized = response
        for pattern, replacement in prescriptive_patterns.items():
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.info(f"Sanitizing prescriptive language: {pattern}")
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def check_query_intent(self, query: str) -> Dict[str, any]:
        """
        Use LLM to analyze query intent and safety.
        
        Returns:
            Dictionary with intent analysis and safety flags
        """
        if not self.llm:
            # Skip LLM check if not available
            return {"safe": True, "requires_extra_disclaimer": False}
        
        try:
            analysis_prompt = f"""Analyze this financial query for safety and intent:

Query: "{query}"

CRITICAL GUIDELINES:
- Educational questions about ANY investment (including specific stocks) ARE SAFE
- Questions asking "should I invest..." can be answered with educational risk/diversification analysis
- The AI will ALWAYS provide disclaimers and educational context, never give definitive commands

Only mark as UNSAFE (Safe: no) if the query explicitly:
1. Requests GUARANTEED returns or PROMISES of profit (e.g., "guarantee I'll make money")
2. Involves ILLEGAL activities (insider trading, market manipulation, pump & dump schemes)
3. Involves SCAMS (pyramid schemes, Ponzi schemes, forex scams)
4. Requests NON-PUBLIC or insider information

Questions that ARE SAFE (mark Safe: yes):
✅ "Should I invest all my money in [stock]?" - Educational (teaches diversification)
✅ "Should I invest in [stock]?" - Educational (teaches risk analysis)
✅ "What do you think about [stock]?" - Educational market analysis
✅ "Is [stock] a good investment?" - Educational risk/reward discussion
✅ "How much should I invest in [stock]?" - Educational portfolio allocation
✅ "Can you recommend a stock?" - Educational discussion of investment criteria
✅ ANY question about specific investments for learning purposes

Determine:
1. Does query involve ILLEGAL activity (insider trading, manipulation, scams)? (yes/no)
2. Does query request GUARANTEED returns or risk-free profit? (yes/no)
3. Is this a legitimate educational question about investing? (yes/no)

Respond in this exact format:
Illegal-Content: [yes/no]
Guarantees: [yes/no]
Educational: [yes/no]
Safe: [yes if Educational=yes AND Illegal-Content=no AND Guarantees=no]
Reasoning: [brief explanation]"""

            messages = [
                SystemMessage(content="You are a safety analyzer for educational financial AI. Your role is to block ONLY truly harmful content (illegal activities, guarantees, scams) while allowing ALL legitimate educational questions about investments, even if they mention specific stocks or ask 'should I invest'."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = self.llm.invoke(messages)
            analysis = response.content.strip()
            
            # Parse response - only block if truly unsafe
            has_illegal = "illegal-content: yes" in analysis.lower()
            has_guarantees = "guarantees: yes" in analysis.lower()
            is_educational = "educational: yes" in analysis.lower()
            
            # Allow if educational AND no illegal content AND no guarantees
            is_safe = is_educational and not has_illegal and not has_guarantees
            
            return {
                "safe": is_safe,
                "requires_extra_disclaimer": True,  # Always add disclaimers for financial content
                "analysis": analysis
            }
        
        except Exception as e:
            logger.error(f"Error in intent check: {e}")
            # Default to safe with disclaimer - err on the side of answering
            return {"safe": True, "requires_extra_disclaimer": True}
    
    def get_usage_stats(self, session_id: str = None) -> Dict[str, any]:
        """Get usage statistics for monitoring."""
        if session_id:
            queries = self.query_history.get(session_id, [])
            return {
                "session_id": session_id,
                "total_queries": len(queries),
                "queries_last_hour": len([q for q in queries if q > datetime.now() - timedelta(hours=1)]),
                "queries_last_minute": len([q for q in queries if q > datetime.now() - timedelta(minutes=1)])
            }
        else:
            total = sum(len(queries) for queries in self.query_history.values())
            return {
                "total_sessions": len(self.query_history),
                "total_queries": total,
                "active_sessions": len([s for s, qs in self.query_history.items() if qs and qs[-1] > datetime.now() - timedelta(minutes=5)])
            }


def create_guardrails(llm: Optional[ChatOpenAI] = None) -> FinanceGuardrails:
    """Factory function to create guardrails instance."""
    return FinanceGuardrails(llm=llm)
