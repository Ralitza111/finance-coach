"""
Multi-Agent Orchestrator for AI Finance Assistant
Coordinates multiple agents and synthesizes their responses.
Supports parallel agent execution for reduced latency.
"""

import asyncio
import logging
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """Orchestrates multiple agents and synthesizes responses."""
    
    def __init__(self, llm: ChatOpenAI, agents: Dict[str, Any]):
        """
        Initialize the orchestrator.
        
        Args:
            llm: Language model for synthesis
            agents: Dictionary of agent instances
        """
        self.llm = llm
        self.agents = agents
        self.executor = ThreadPoolExecutor(max_workers=5)  # For parallel execution
        logger.info(f"MultiAgentOrchestrator initialized with {len(agents)} agents")
        logger.info("✨ Parallel execution enabled for multiple agents")
    
    def execute_single_agent(
        self,
        agent_name: str,
        query: str,
        thread_id: str = "default"
    ) -> str:
        """
        Execute a single agent query.
        
        Args:
            agent_name: Name of the agent to execute
            query: User's query
            thread_id: Thread ID for conversation history
            
        Returns:
            Agent's response
        """
        logger.info(f"Executing single agent: {agent_name}")
        
        if agent_name not in self.agents:
            logger.error(f"Agent {agent_name} not found")
            return f"Error: Agent '{agent_name}' not available."
        
        try:
            agent = self.agents[agent_name]
            response = agent.invoke(query, thread_id=thread_id)
            return response
        except Exception as e:
            logger.error(f"Error executing {agent_name}: {e}")
            return f"Error from {agent_name}: {str(e)}"
    
    def execute_multiple_agents(
        self,
        agent_names: List[str],
        query: str,
        thread_id: str = "default",
        parallel: bool = True
    ) -> str:
        """
        Execute multiple agents and synthesize their responses.
        Supports parallel execution for reduced latency.
        
        Args:
            agent_names: List of agent names to execute
            query: User's query
            thread_id: Thread ID for conversation history
            parallel: Whether to execute agents in parallel (default: True)
            
        Returns:
            Synthesized response from all agents
        """
        logger.info(f"Executing multiple agents: {', '.join(agent_names)}")
        
        if parallel and len(agent_names) > 1:
            logger.info("⚡ Using parallel execution for reduced latency")
            agent_responses = self._execute_agents_parallel(agent_names, query, thread_id)
        else:
            # Sequential execution (fallback or single agent)
            agent_responses = self._execute_agents_sequential(agent_names, query, thread_id)
        
        # Synthesize responses
        if len(agent_responses) == 1:
            # Single agent, return directly
            return list(agent_responses.values())[0]
        else:
            # Multiple agents, synthesize
            return self._synthesize_responses(query, agent_responses)
    
    def _execute_agents_sequential(
        self,
        agent_names: List[str],
        query: str,
        thread_id: str
    ) -> Dict[str, str]:
        """Execute agents sequentially (original method)."""
        agent_responses = {}
        for agent_name in agent_names:
            if agent_name in self.agents:
                try:
                    agent = self.agents[agent_name]
                    response = agent.invoke(query, thread_id=thread_id)
                    agent_responses[agent_name] = response
                    logger.info(f"✅ {agent_name} completed")
                except Exception as e:
                    logger.error(f"❌ Error from {agent_name}: {e}")
                    agent_responses[agent_name] = f"Error: {str(e)}"
            else:
                logger.warning(f"Agent {agent_name} not found")
        return agent_responses
    
    def _execute_agents_parallel(
        self,
        agent_names: List[str],
        query: str,
        thread_id: str
    ) -> Dict[str, str]:
        """
        Execute agents in parallel using ThreadPoolExecutor.
        Significantly reduces latency when multiple agents are needed.
        """
        def execute_agent(agent_name: str) -> tuple:
            """Helper function to execute a single agent."""
            if agent_name not in self.agents:
                logger.warning(f"Agent {agent_name} not found")
                return agent_name, f"Error: Agent not found"
            
            try:
                agent = self.agents[agent_name]
                response = agent.invoke(query, thread_id=thread_id)
                logger.info(f"✅ {agent_name} completed")
                return agent_name, response
            except Exception as e:
                logger.error(f"❌ Error from {agent_name}: {e}")
                return agent_name, f"Error: {str(e)}"
        
        # Execute all agents in parallel
        import time
        start_time = time.time()
        
        futures = [
            self.executor.submit(execute_agent, agent_name)
            for agent_name in agent_names
        ]
        
        # Collect results
        agent_responses = {}
        for future in futures:
            agent_name, response = future.result()
            agent_responses[agent_name] = response
        
        elapsed = time.time() - start_time
        logger.info(f"⚡ Parallel execution completed in {elapsed:.2f}s (saved ~{len(agent_names)*2-elapsed:.1f}s)")
        
        return agent_responses
    
    def _synthesize_responses(
        self,
        query: str,
        agent_responses: Dict[str, str]
    ) -> str:
        """
        Synthesize responses from multiple agents into a coherent answer.
        
        Args:
            query: Original user query
            agent_responses: Dictionary mapping agent names to their responses
            
        Returns:
            Synthesized response
        """
        logger.info(f"Synthesizing responses from {len(agent_responses)} agents")
        
        # Format agent responses
        formatted_responses = "\n\n".join([
            f"=== {self._format_agent_name(name)} ===\n{response}"
            for name, response in agent_responses.items()
        ])
        
        synthesis_prompt = f"""You are synthesizing responses from multiple specialized financial AI agents.

Original User Query: "{query}"

Agent Responses:
{formatted_responses}

Instructions:
1. Combine all agent responses into ONE comprehensive, well-organized answer
2. Eliminate redundancy while preserving all unique information
3. Organize information logically (e.g., data first, then analysis, then recommendations)
4. Maintain the educational tone
5. Keep all disclaimers about not being financial advice
6. Use clear headings and bullet points for readability
7. Make it feel like a single, cohesive response (not separate agent outputs)

Synthesized Response:"""

        try:
            messages = [
                SystemMessage(content="You are an expert at synthesizing information from multiple sources into clear, comprehensive responses."),
                HumanMessage(content=synthesis_prompt)
            ]
            
            response = self.llm.invoke(messages)
            synthesized = response.content.strip()
            
            logger.info("✅ Successfully synthesized responses")
            return synthesized
            
        except Exception as e:
            logger.error(f"❌ Error synthesizing responses: {e}")
            # Fallback: return concatenated responses
            return formatted_responses
    
    def _format_agent_name(self, agent_name: str) -> str:
        """Format agent name for display."""
        name_map = {
            "finance_qa": "Finance Q&A Agent 💬",
            "portfolio_analyzer": "Portfolio Analyzer Agent 📊",
            "market_analyst": "Market Analyst Agent 📈",
            "goal_planner": "Goal Planner Agent 🎯",
            "tax_educator": "Tax Educator Agent 💰"
        }
        return name_map.get(agent_name, agent_name)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all available agents."""
        return {
            name: agent.get_info()
            for name, agent in self.agents.items()
        }


def create_orchestrator(
    llm: ChatOpenAI,
    agents: Dict[str, Any]
) -> MultiAgentOrchestrator:
    """
    Factory function to create an orchestrator.
    
    Args:
        llm: Language model for synthesis
        agents: Dictionary of agent instances
        
    Returns:
        MultiAgentOrchestrator instance
    """
    return MultiAgentOrchestrator(llm, agents)
