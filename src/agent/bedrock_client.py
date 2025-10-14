"""
AWS Bedrock AgentCore Client

Handles communication with AWS Bedrock AgentCore for reasoning and task planning.
This is the core component that enables autonomous decision-making capabilities.
"""

import json
import logging
from typing import Dict, List, Optional, Any
import asyncio

import boto3
from botocore.exceptions import ClientError
from loguru import logger


class BedrockAgentClient:
    """
    Client for interacting with AWS Bedrock AgentCore.

    Provides methods for invoking agents, managing sessions, and handling
    reasoning tasks for autonomous market intelligence.
    """

    def __init__(self, config: Dict):
        """Initialize the Bedrock AgentCore client."""
        self.config = config
        self.region = config.get('region', 'us-east-1')

        # Initialize Bedrock Runtime client
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=self.region
        )

        # Initialize Bedrock Agent Runtime client
        self.bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime',
            region_name=self.region
        )

        self.agent_id = config.get('agent_id')
        self.agent_alias_id = config.get('agent_alias_id', 'TSTALIASID')

        logger.info(f"🤖 Bedrock AgentCore client initialized for region {self.region}")

    async def invoke_agent(self,
                          session_id: str,
                          input_text: str,
                          session_state: Optional[Dict] = None) -> Dict:
        """
        Invoke the Bedrock agent with a reasoning task.

        Args:
            session_id: Unique session identifier
            input_text: Natural language input for the agent
            session_state: Optional session state to maintain context

        Returns:
            Agent response with reasoning and actions
        """
        try:
            # Prepare the input
            agent_input = {
                'inputText': input_text,
                'sessionId': session_id
            }

            if session_state:
                agent_input['sessionState'] = session_state

            # Invoke the agent
            response = self.bedrock_agent_runtime.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,
                inputText=input_text,
                sessionState=session_state or {}
            )

            # Process the streaming response
            result = await self._process_agent_response(response)

            logger.info(f"✅ Agent invoked successfully for session {session_id}")
            return result

        except ClientError as e:
            logger.error(f"❌ Failed to invoke agent: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error invoking agent: {e}")
            raise

    async def _process_agent_response(self, response) -> Dict:
        """Process the streaming response from the agent."""
        result = {
            'completion': '',
            'trace': [],
            'session_state': {},
            'reasoning_steps': []
        }

        try:
            # Process the streaming response
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        # Decode the chunk
                        chunk_text = chunk['bytes'].decode('utf-8')
                        result['completion'] += chunk_text

                elif 'trace' in event:
                    # Capture reasoning trace
                    trace = event['trace']
                    result['trace'].append(trace)

                    # Extract reasoning steps
                    if 'orchestrationTrace' in trace:
                        orchestration = trace['orchestrationTrace']
                        if 'rationale' in orchestration:
                            result['reasoning_steps'].append({
                                'type': 'rationale',
                                'content': orchestration['rationale']
                            })

                elif 'sessionState' in event:
                    result['session_state'] = event['sessionState']

        except Exception as e:
            logger.error(f"❌ Error processing agent response: {e}")
            raise

        return result

    async def plan_market_analysis_tasks(self,
                                       context: Dict,
                                       session_id: str) -> List[Dict]:
        """
        Use the agent to plan market analysis tasks.

        Args:
            context: Current market context and data
            session_id: Session identifier

        Returns:
            List of planned tasks with priorities and reasoning
        """
        planning_prompt = f"""
        As an autonomous market intelligence agent, analyze the current context and plan tasks.

        Current Context:
        - Market state: {context.get('market_state', 'Unknown')}
        - Companies monitored: {len(context.get('companies', []))}
        - Last analysis: {context.get('last_analysis', 'Never')}
        - Recent events: {context.get('recent_events', 0)}

        Plan the next set of tasks to:
        1. Monitor company activities and strategic moves
        2. Analyze market trends and patterns
        3. Update similarity analysis between companies
        4. Identify emerging opportunities and threats

        For each task, provide:
        - Task name and description
        - Priority level (1-10)
        - Reasoning for the task
        - Expected outcomes
        - Required data sources

        Return your plan as a structured JSON response.
        """

        try:
            result = await self.invoke_agent(session_id, planning_prompt)

            # Parse the agent's response to extract tasks
            tasks = self._parse_task_planning_response(result['completion'])

            logger.info(f"📋 Planned {len(tasks)} market analysis tasks")
            return tasks

        except Exception as e:
            logger.error(f"❌ Failed to plan market analysis tasks: {e}")
            return []

    def _parse_task_planning_response(self, response_text: str) -> List[Dict]:
        """Parse the agent's task planning response."""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                tasks_data = json.loads(json_match.group())
                return tasks_data.get('tasks', [])

            # Fallback: parse structured text
            return self._parse_structured_tasks(response_text)

        except Exception as e:
            logger.error(f"❌ Failed to parse task planning response: {e}")
            return []

    def _parse_structured_tasks(self, text: str) -> List[Dict]:
        """Parse structured task descriptions from text."""
        tasks = []
        lines = text.split('\n')

        current_task = {}
        for line in lines:
            line = line.strip()
            if line.startswith('Task:'):
                if current_task:
                    tasks.append(current_task)
                current_task = {'name': line.replace('Task:', '').strip()}
            elif line.startswith('Priority:'):
                current_task['priority'] = int(line.split(':')[1].strip())
            elif line.startswith('Description:'):
                current_task['description'] = line.replace('Description:', '').strip()
            elif line.startswith('Reasoning:'):
                current_task['reasoning'] = line.replace('Reasoning:', '').strip()

        if current_task:
            tasks.append(current_task)

        return tasks

    async def analyze_company_similarity(self,
                                      company_data: Dict,
                                      session_id: str) -> Dict:
        """
        Use the agent to analyze company similarities.

        Args:
            company_data: Data about companies to analyze
            session_id: Session identifier

        Returns:
            Analysis results with similarity insights
        """
        analysis_prompt = f"""
        Analyze the strategic similarities between these companies:

        Company Data:
        {json.dumps(company_data, indent=2)}

        For each company, consider:
        1. Strategic focus areas and business models
        2. Technology investments and partnerships
        3. Market positioning and competitive advantages
        4. Recent announcements and strategic moves

        Identify:
        - Companies with similar strategic directions
        - Emerging competitive clusters
        - Potential partnership opportunities
        - Market convergence patterns

        Provide detailed reasoning for your analysis and return structured results.
        """

        try:
            result = await self.invoke_agent(session_id, analysis_prompt)

            # Parse the analysis results
            analysis = self._parse_similarity_analysis(result['completion'])

            logger.info(f"🔍 Completed similarity analysis for {len(company_data)} companies")
            return analysis

        except Exception as e:
            logger.error(f"❌ Failed to analyze company similarity: {e}")
            return {}

    def _parse_similarity_analysis(self, response_text: str) -> Dict:
        """Parse similarity analysis results from agent response."""
        try:
            # Extract structured data from the response
            analysis = {
                'similarity_clusters': [],
                'strategic_insights': [],
                'competitive_analysis': {},
                'recommendations': []
            }

            # Parse clusters
            import re
            cluster_pattern = r'Cluster \d+: (.+?)(?=Cluster \d+:|$)'
            clusters = re.findall(cluster_pattern, response_text, re.DOTALL)

            for i, cluster in enumerate(clusters):
                analysis['similarity_clusters'].append({
                    'id': i + 1,
                    'description': cluster.strip(),
                    'companies': self._extract_companies_from_text(cluster)
                })

            return analysis

        except Exception as e:
            logger.error(f"❌ Failed to parse similarity analysis: {e}")
            return {}

    def _extract_companies_from_text(self, text: str) -> List[str]:
        """Extract company names from text."""
        # Simple extraction - in production, use NER
        companies = []
        company_names = ['Amazon', 'Google', 'Microsoft', 'Apple', 'Meta',
                        'OpenAI', 'Anthropic', 'Nvidia', 'Tesla', 'Netflix']

        for company in company_names:
            if company.lower() in text.lower():
                companies.append(company)

        return companies

    async def detect_market_trends(self,
                                market_data: Dict,
                                session_id: str) -> Dict:
        """
        Use the agent to detect market trends and patterns.

        Args:
            market_data: Market data to analyze
            session_id: Session identifier

        Returns:
            Trend analysis results
        """
        trend_prompt = f"""
        Analyze the following market data to identify trends and patterns:

        Market Data:
        {json.dumps(market_data, indent=2)}

        Identify:
        1. Emerging trends in technology and business models
        2. Shifts in market dynamics and competitive landscape
        3. Investment patterns and strategic moves
        4. Potential disruptions and opportunities

        For each trend, provide:
        - Trend description and significance
        - Supporting evidence from the data
        - Confidence level (1-10)
        - Potential impact on the market

        Return structured trend analysis results.
        """

        try:
            result = await self.invoke_agent(session_id, trend_prompt)

            # Parse trend analysis
            trends = self._parse_trend_analysis(result['completion'])

            logger.info(f"📈 Detected {len(trends.get('trends', []))} market trends")
            return trends

        except Exception as e:
            logger.error(f"❌ Failed to detect market trends: {e}")
            return {}

    def _parse_trend_analysis(self, response_text: str) -> Dict:
        """Parse trend analysis results."""
        try:
            trends = {
                'trends': [],
                'confidence_scores': [],
                'market_insights': []
            }

            # Extract trend information
            import re
            trend_pattern = r'Trend \d+: (.+?)(?=Trend \d+:|$)'
            trend_matches = re.findall(trend_pattern, response_text, re.DOTALL)

            for i, trend_text in enumerate(trend_matches):
                trends['trends'].append({
                    'id': i + 1,
                    'description': trend_text.strip(),
                    'confidence': self._extract_confidence_score(trend_text)
                })

            return trends

        except Exception as e:
            logger.error(f"❌ Failed to parse trend analysis: {e}")
            return {}

    def _extract_confidence_score(self, text: str) -> float:
        """Extract confidence score from text."""
        import re
        confidence_match = re.search(r'confidence[:\s]+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if confidence_match:
            return float(confidence_match.group(1))
        return 5.0  # Default confidence

    async def generate_insights(self,
                              analysis_data: Dict,
                              session_id: str) -> Dict:
        """
        Generate actionable insights from analysis data.

        Args:
            analysis_data: Analysis results to generate insights from
            session_id: Session identifier

        Returns:
            Generated insights and recommendations
        """
        insights_prompt = f"""
        Based on the following analysis data, generate actionable insights:

        Analysis Data:
        {json.dumps(analysis_data, indent=2)}

        Generate insights that answer:
        1. What are the key strategic patterns in the market?
        2. Which companies are converging or diverging strategically?
        3. What opportunities exist for partnerships or investments?
        4. What risks should be monitored?

        Provide specific, actionable recommendations with supporting evidence.
        """

        try:
            result = await self.invoke_agent(session_id, insights_prompt)

            insights = {
                'key_insights': [],
                'recommendations': [],
                'risk_factors': [],
                'opportunities': []
            }

            # Parse insights from response
            insights = self._parse_insights_response(result['completion'])

            logger.info(f"💡 Generated {len(insights.get('key_insights', []))} insights")
            return insights

        except Exception as e:
            logger.error(f"❌ Failed to generate insights: {e}")
            return {}

    def _parse_insights_response(self, response_text: str) -> Dict:
        """Parse insights from agent response."""
        insights = {
            'key_insights': [],
            'recommendations': [],
            'risk_factors': [],
            'opportunities': []
        }

        # Simple parsing - in production, use more sophisticated NLP
        lines = response_text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('Key Insights:'):
                current_section = 'key_insights'
            elif line.startswith('Recommendations:'):
                current_section = 'recommendations'
            elif line.startswith('Risk Factors:'):
                current_section = 'risk_factors'
            elif line.startswith('Opportunities:'):
                current_section = 'opportunities'
            elif line and current_section:
                insights[current_section].append(line)

        return insights
