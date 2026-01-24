"""
AI Finance Assistant - Multi-Agent System
Main application with Gradio web interface for local hosting.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
import gradio as gr

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Import API clients
from market_data_api import MarketDataAPI
from news_api import FinancialNewsAPI
from web_scraper import FinancialWebScraper

# Import multi-agent components
from multi_agent_router import create_router, QueryRouter
from specialized_agents import create_specialized_agents
from multi_agent_orchestrator import create_orchestrator, MultiAgentOrchestrator

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'finance_assistant_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AIFinanceAssistant:
    """Main AI Finance Assistant system with multi-agent coordination."""
    
    def __init__(
        self,
        openai_api_key: str,
        alpha_vantage_key: str = None,
        news_api_key: str = None
    ):
        """Initialize the AI Finance Assistant."""
        logger.info("🚀 Initializing AI Finance Assistant...")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3"))
        )
        logger.info(f"✅ LLM initialized: {os.getenv('LLM_MODEL', 'gpt-4o-mini')}")
        
        # Initialize API clients
        self.market_data_api = MarketDataAPI(alpha_vantage_key)
        self.news_api = FinancialNewsAPI(news_api_key)
        self.web_scraper = FinancialWebScraper()
        logger.info("✅ API clients initialized")
        
        # Load knowledge base (optional)
        self.retriever = self._load_knowledge_base(openai_api_key)
        
        # Create specialized agents
        self.agents = create_specialized_agents(
            self.llm,
            self.market_data_api,
            self.news_api,
            self.web_scraper,
            self.retriever
        )
        logger.info(f"✅ Created {len(self.agents)} specialized agents")
        
        # Create router and orchestrator
        self.router = create_router(self.llm)
        self.orchestrator = create_orchestrator(self.llm, self.agents)
        logger.info("✅ Router and orchestrator initialized")
        
        logger.info("🎉 AI Finance Assistant ready!")
    
    def _load_knowledge_base(self, openai_api_key: str):
        """Load FAISS knowledge base if available."""
        try:
            embeddings = OpenAIEmbeddings(api_key=openai_api_key)
            knowledge_base_path = "./knowledge_base/faiss_index"
            
            if os.path.exists(knowledge_base_path):
                logger.info(f"Loading knowledge base from {knowledge_base_path}")
                vector_store = FAISS.load_local(
                    knowledge_base_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                logger.info("✅ Knowledge base loaded successfully")
                return retriever
            else:
                logger.warning("⚠️  Knowledge base not found (optional)")
                return None
        except Exception as e:
            logger.error(f"❌ Error loading knowledge base: {e}")
            return None
    
    def process_query(self, query: str, thread_id: str = "default") -> tuple:
        """
        Process a user query through the multi-agent system.
        
        Args:
            query: User's question
            thread_id: Conversation thread ID
            
        Returns:
            Tuple of (response, routing_info)
        """
        logger.info(f"📥 Processing query: {query[:100]}...")
        
        try:
            # Route the query
            agent_names = self.router.route_query(query)
            routing_info = self.router.explain_routing(query, agent_names)
            logger.info(f"🔀 {routing_info}")
            
            # Execute agent(s)
            if len(agent_names) == 1:
                response = self.orchestrator.execute_single_agent(
                    agent_names[0],
                    query,
                    thread_id
                )
            else:
                response = self.orchestrator.execute_multiple_agents(
                    agent_names,
                    query,
                    thread_id
                )
            
            logger.info(f"✅ Response generated ({len(response)} chars)")
            return response, routing_info
            
        except Exception as e:
            logger.error(f"❌ Error processing query: {e}", exc_info=True)
            error_msg = f"I apologize, but I encountered an error processing your question: {str(e)}\n\nPlease try rephrasing your question or contact support if the issue persists."
            return error_msg, "Error occurred"
    
    def get_system_info(self) -> str:
        """Get information about the system and available agents."""
        info = "## 🤖 AI Finance Assistant - System Information\n\n"
        info += "### Available Agents:\n\n"
        
        agent_info = self.orchestrator.get_agent_info()
        for name, details in agent_info.items():
            info += f"**{details['name']}**\n"
            info += f"- Tools: {details['tool_count']}\n"
            info += f"- Capabilities: {', '.join(details['tools'])}\n\n"
        
        return info


def create_gradio_interface(assistant: AIFinanceAssistant):
    """Create Gradio web interface."""
    
    # Custom CSS for better appearance
    custom_css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    .agent-info {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    """
    
    def chat_interface(message, history):
        """Process chat message and return response."""
        if not message or message.strip() == "":
            return history
        
        # Process query
        response, routing_info = assistant.process_query(message)
        
        # Format response with routing info
        full_response = f"*{routing_info}*\n\n{response}"
        
        # Gradio 6.0 format with dictionaries (required for avatar_images)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": full_response})
        
        return history
    
    def get_quick_example(example_type):
        """Return example queries."""
        examples = {
            "stock_price": "What's the current price of Apple stock?",
            "portfolio": "Analyze this portfolio: AAPL (10 shares), MSFT (15 shares), GOOGL (5 shares)",
            "retirement": "I'm 30 years old and want to retire at 65. If I save $500/month with 7% returns, how much will I have?",
            "tax": "What's the difference between a Traditional IRA and Roth IRA?",
            "education": "What is diversification and why is it important?"
        }
        return examples.get(example_type, "")
    
    # Create Gradio interface
    with gr.Blocks(title="AI Finance Assistant") as interface:
        gr.Markdown("""
        # 🏦 AI Finance Assistant
        ### Your Personal Financial Education Companion
        
        Ask me anything about:
        - 💬 Financial concepts and terminology
        - 📊 Portfolio analysis and diversification
        - 📈 Real-time stock prices and market data
        - 🎯 Retirement planning and financial goals
        - 💰 Tax strategies and retirement accounts
        
        **⚠️ Important**: This is for educational purposes only. Not financial advice. Consult licensed professionals for specific situations.
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_label=True,
                    avatar_images=(None, "🤖")
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask me about stocks, portfolios, retirement planning, taxes, or financial concepts...",
                        lines=2,
                        scale=4
                    )
                    submit_btn = gr.Button("Send 💬", scale=1, variant="primary")
                
                # Clear button
                clear_btn = gr.Button("🔄 Clear Conversation", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📚 Quick Examples")
                
                gr.Markdown("**Stock Prices:**")
                stock_btn = gr.Button("📈 Check Stock Price", size="sm")
                
                gr.Markdown("**Portfolio Analysis:**")
                portfolio_btn = gr.Button("📊 Analyze Portfolio", size="sm")
                
                gr.Markdown("**Retirement Planning:**")
                retirement_btn = gr.Button("🎯 Plan Retirement", size="sm")
                
                gr.Markdown("**Tax Education:**")
                tax_btn = gr.Button("💰 IRA vs Roth IRA", size="sm")
                
                gr.Markdown("**Financial Education:**")
                education_btn = gr.Button("💬 Learn About Diversification", size="sm")
        
        # System information accordion
        with gr.Accordion("🤖 System Information", open=False):
            system_info = gr.Markdown(assistant.get_system_info())
        
        # Event handlers
        # Event handlers
        def submit_and_clear(message, history):
            """Submit message and clear input."""
            updated_history = chat_interface(message, history)
            return updated_history, ""
        
        submit_btn.click(
            submit_and_clear,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        msg_input.submit(
            submit_and_clear,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        clear_btn.click(lambda: [], outputs=[chatbot])
        
        # Quick example buttons
        stock_btn.click(lambda: get_quick_example("stock_price"), outputs=[msg_input])
        portfolio_btn.click(lambda: get_quick_example("portfolio"), outputs=[msg_input])
        retirement_btn.click(lambda: get_quick_example("retirement"), outputs=[msg_input])
        tax_btn.click(lambda: get_quick_example("tax"), outputs=[msg_input])
        education_btn.click(lambda: get_quick_example("education"), outputs=[msg_input])
        
        gr.Markdown("""
        ---
        ### 📊 Data Sources
        - **Market Data**: yFinance (real-time), Alpha Vantage (optional)
        - **News**: NewsAPI (optional)
        - **Education**: Investopedia, financial education sites
        
        ### 🔐 Privacy
        - No personal data stored
        - Conversations are session-based only
        - API keys secured via environment variables
        
        **Built with ❤️ for democratizing financial literacy**
        """)
    
    return interface


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Finance Assistant")
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    parser.add_argument("--port", type=int, default=7860, help="Port to run on (default: 7860)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for required API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("❌ OPENAI_API_KEY not found in environment variables!")
        print("\n❌ Error: OPENAI_API_KEY is required!")
        print("Please set it in your .env file or environment variables.")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Optional API keys
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    news_api_key = os.getenv("NEWS_API_KEY")
    
    if not alpha_vantage_key:
        logger.warning("⚠️  Alpha Vantage API key not found (optional)")
    if not news_api_key:
        logger.warning("⚠️  News API key not found (optional)")
    
    # Initialize assistant
    try:
        assistant = AIFinanceAssistant(
            openai_api_key=openai_api_key,
            alpha_vantage_key=alpha_vantage_key,
            news_api_key=news_api_key
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize assistant: {e}", exc_info=True)
        sys.exit(1)
    
    # Create and launch Gradio interface
    interface = create_gradio_interface(assistant)
    
    logger.info(f"🌐 Launching Gradio interface on {args.host}:{args.port}")
    print(f"\n{'='*60}")
    print("🏦 AI Finance Assistant - Starting...")
    print(f"{'='*60}")
    print(f"🌐 Access the interface at: http://{args.host}:{args.port}")
    if args.share:
        print("🔗 Creating public link (share=True)...")
    print(f"{'='*60}\n")
    
    interface.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True
    )


if __name__ == "__main__":
    main()
