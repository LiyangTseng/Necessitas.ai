"""
Reasoning Engine for Autonomous Market Intelligence

Handles high-level reasoning tasks using AWS Bedrock models for decision-making,
trend analysis, and strategic insights generation.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError
from loguru import logger


class ReasoningEngine:
    """
    Reasoning engine that uses AWS Bedrock models for autonomous decision-making.

    This component handles complex reasoning tasks like trend analysis, strategic
    insights, and autonomous task planning for the market intelligence agent.
    """

    def __init__(self, config: Dict):
        """Initialize the reasoning engine with Bedrock configuration."""
        self.config = config
        self.region = config.get('region', 'us-east-1')
        self.model_id = config.get('model_id', 'anthropic.claude-3-sonnet-20240229-v1:0')

        # Initialize Bedrock Runtime client
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=self.region
        )

        logger.info(f"🧠 Reasoning engine initialized with model {self.model_id}")

    async def plan_tasks(self, context_prompt: str) -> List[Dict]:
        """
        Use reasoning to plan autonomous tasks based on context.

        Args:
            context_prompt: Context and requirements for task planning

        Returns:
            List of planned tasks with priorities and reasoning
        """
        reasoning_prompt = f"""
        You are an autonomous market intelligence agent. Based on the context provided,
        plan a set of tasks to accomplish your objectives.

        Context:
        {context_prompt}

        For each task, provide:
        1. Task name and clear description
        2. Priority level (1-10, where 10 is highest)
        3. Reasoning for why this task is important
        4. Expected outcomes and success criteria
        5. Required data sources and tools
        6. Estimated complexity and time requirements

        Return your response as a JSON array of task objects.
        """

        try:
            response = await self._invoke_bedrock_model(reasoning_prompt)
            tasks = self._parse_task_planning_response(response)

            logger.info(f"📋 Planned {len(tasks)} tasks using reasoning")
            return tasks

        except Exception as e:
            logger.error(f"❌ Failed to plan tasks: {e}")
            return []

    async def analyze_trends(self, market_data: Dict) -> Dict:
        """
        Analyze market trends using reasoning capabilities.

        Args:
            market_data: Market data to analyze

        Returns:
            Trend analysis with insights and confidence scores
        """
        trend_analysis_prompt = f"""
        As a market intelligence expert, analyze the following data to identify trends:

        Market Data:
        {json.dumps(market_data, indent=2)}

        Analyze and identify:
        1. Emerging technology trends and their significance
        2. Strategic shifts in company focus areas
        3. Investment patterns and funding trends
        4. Competitive dynamics and market consolidation
        5. Potential disruptions and opportunities

        For each trend identified, provide:
        - Trend description and significance
        - Supporting evidence from the data
        - Confidence level (1-10)
        - Potential market impact
        - Timeline for trend development

        Return structured analysis results with reasoning.
        """

        try:
            response = await self._invoke_bedrock_model(trend_analysis_prompt)
            trends = self._parse_trend_analysis(response)

            logger.info(f"📈 Analyzed trends with {len(trends.get('trends', []))} insights")
            return trends

        except Exception as e:
            logger.error(f"❌ Failed to analyze trends: {e}")
            return {}

    async def generate_strategic_insights(self,
                                       company_data: Dict,
                                       market_context: Dict) -> Dict:
        """
        Generate strategic insights about companies and market dynamics.

        Args:
            company_data: Data about companies being analyzed
            market_context: Current market context and conditions

        Returns:
            Strategic insights with recommendations
        """
        insights_prompt = f"""
        As a strategic market analyst, analyze the following data to generate insights:

        Company Data:
        {json.dumps(company_data, indent=2)}

        Market Context:
        {json.dumps(market_context, indent=2)}

        Generate strategic insights that address:
        1. Competitive positioning and strategic advantages
        2. Market opportunities and threats
        3. Partnership and collaboration potential
        4. Investment and growth opportunities
        5. Risk factors and mitigation strategies

        For each insight, provide:
        - Clear description and rationale
        - Supporting evidence and data points
        - Strategic implications
        - Actionable recommendations
        - Confidence level and uncertainty factors

        Return comprehensive strategic analysis with reasoning.
        """

        try:
            response = await self._invoke_bedrock_model(insights_prompt)
            insights = self._parse_strategic_insights(response)

            logger.info(f"💡 Generated {len(insights.get('insights', []))} strategic insights")
            return insights

        except Exception as e:
            logger.error(f"❌ Failed to generate strategic insights: {e}")
            return {}

    async def evaluate_company_similarity(self,
                                        company_pairs: List[Dict]) -> Dict:
        """
        Evaluate strategic similarity between company pairs.

        Args:
            company_pairs: List of company pairs to evaluate

        Returns:
            Similarity analysis with reasoning
        """
        similarity_prompt = f"""
        As a market intelligence expert, evaluate the strategic similarity between these company pairs:

        Company Pairs:
        {json.dumps(company_pairs, indent=2)}

        For each pair, analyze:
        1. Business model similarities and differences
        2. Technology focus and investment areas
        3. Market positioning and target customers
        4. Strategic partnerships and ecosystem relationships
        5. Competitive dynamics and market overlap

        Provide similarity scores (0-1) with detailed reasoning for:
        - Strategic alignment
        - Technology convergence
        - Market competition
        - Partnership potential

        Return structured similarity analysis with confidence levels.
        """

        try:
            response = await self._invoke_bedrock_model(similarity_prompt)
            similarities = self._parse_similarity_analysis(response)

            logger.info(f"🔍 Evaluated similarity for {len(company_pairs)} company pairs")
            return similarities

        except Exception as e:
            logger.error(f"❌ Failed to evaluate company similarity: {e}")
            return {}

    async def predict_market_movements(self,
                                    historical_data: Dict,
                                    current_indicators: Dict) -> Dict:
        """
        Predict potential market movements based on data analysis.

        Args:
            historical_data: Historical market and company data
            current_indicators: Current market indicators and signals

        Returns:
            Market predictions with confidence levels
        """
        prediction_prompt = f"""
        As a market intelligence expert, analyze the following data to predict market movements:

        Historical Data:
        {json.dumps(historical_data, indent=2)}

        Current Indicators:
        {json.dumps(current_indicators, indent=2)}

        Based on patterns and trends, predict:
        1. Likely market consolidation or fragmentation
        2. Emerging competitive threats and opportunities
        3. Technology adoption and disruption patterns
        4. Investment and funding trends
        5. Strategic partnership and acquisition activity

        For each prediction, provide:
        - Predicted outcome and timeline
        - Supporting evidence and reasoning
        - Confidence level (1-10)
        - Key assumptions and risk factors
        - Potential alternative scenarios

        Return structured predictions with detailed reasoning.
        """

        try:
            response = await self._invoke_bedrock_model(prediction_prompt)
            predictions = self._parse_market_predictions(response)

            logger.info(f"🔮 Generated {len(predictions.get('predictions', []))} market predictions")
            return predictions

        except Exception as e:
            logger.error(f"❌ Failed to predict market movements: {e}")
            return {}

    async def _invoke_bedrock_model(self, prompt: str) -> str:
        """Invoke the Bedrock model with the given prompt."""
        try:
            # Prepare the request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Invoke the model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )

            # Parse the response
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']

            return content

        except ClientError as e:
            logger.error(f"❌ Bedrock model invocation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error invoking Bedrock model: {e}")
            raise

    def _parse_task_planning_response(self, response: str) -> List[Dict]:
        """Parse task planning response from the model."""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # Fallback: parse structured text
            return self._parse_structured_tasks(response)

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
                current_task = {
                    'name': line.replace('Task:', '').strip(),
                    'type': 'data_collection',
                    'priority': 5
                }
            elif line.startswith('Priority:'):
                current_task['priority'] = int(line.split(':')[1].strip())
            elif line.startswith('Description:'):
                current_task['description'] = line.replace('Description:', '').strip()
            elif line.startswith('Reasoning:'):
                current_task['reasoning'] = line.replace('Reasoning:', '').strip()

        if current_task:
            tasks.append(current_task)

        return tasks

    def _parse_trend_analysis(self, response: str) -> Dict:
        """Parse trend analysis from model response."""
        try:
            trends = {
                'trends': [],
                'confidence_scores': [],
                'market_insights': []
            }

            # Extract trend information using regex
            import re
            trend_pattern = r'Trend \d+: (.+?)(?=Trend \d+:|$)'
            trend_matches = re.findall(trend_pattern, response, re.DOTALL)

            for i, trend_text in enumerate(trend_matches):
                trend = {
                    'id': i + 1,
                    'description': trend_text.strip(),
                    'confidence': self._extract_confidence_score(trend_text),
                    'significance': self._extract_significance(trend_text)
                }
                trends['trends'].append(trend)

            return trends

        except Exception as e:
            logger.error(f"❌ Failed to parse trend analysis: {e}")
            return {}

    def _parse_strategic_insights(self, response: str) -> Dict:
        """Parse strategic insights from model response."""
        insights = {
            'insights': [],
            'recommendations': [],
            'risk_factors': [],
            'opportunities': []
        }

        # Simple parsing - in production, use more sophisticated NLP
        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('Key Insights:'):
                current_section = 'insights'
            elif line.startswith('Recommendations:'):
                current_section = 'recommendations'
            elif line.startswith('Risk Factors:'):
                current_section = 'risk_factors'
            elif line.startswith('Opportunities:'):
                current_section = 'opportunities'
            elif line and current_section:
                insights[current_section].append(line)

        return insights

    def _parse_similarity_analysis(self, response: str) -> Dict:
        """Parse similarity analysis from model response."""
        try:
            analysis = {
                'similarity_scores': [],
                'strategic_insights': [],
                'competitive_analysis': {}
            }

            # Extract similarity scores
            import re
            score_pattern = r'Similarity.*?(\d+\.?\d*)'
            scores = re.findall(score_pattern, response)

            for score in scores:
                analysis['similarity_scores'].append(float(score))

            return analysis

        except Exception as e:
            logger.error(f"❌ Failed to parse similarity analysis: {e}")
            return {}

    def _parse_market_predictions(self, response: str) -> Dict:
        """Parse market predictions from model response."""
        predictions = {
            'predictions': [],
            'confidence_levels': [],
            'timeline_estimates': []
        }

        # Extract prediction information
        import re
        prediction_pattern = r'Prediction \d+: (.+?)(?=Prediction \d+:|$)'
        prediction_matches = re.findall(prediction_pattern, response, re.DOTALL)

        for i, prediction_text in enumerate(prediction_matches):
            prediction = {
                'id': i + 1,
                'description': prediction_text.strip(),
                'confidence': self._extract_confidence_score(prediction_text),
                'timeline': self._extract_timeline(prediction_text)
            }
            predictions['predictions'].append(prediction)

        return predictions

    def _extract_confidence_score(self, text: str) -> float:
        """Extract confidence score from text."""
        import re
        confidence_match = re.search(r'confidence[:\s]+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if confidence_match:
            return float(confidence_match.group(1))
        return 5.0  # Default confidence

    def _extract_significance(self, text: str) -> str:
        """Extract significance level from text."""
        if 'high' in text.lower():
            return 'high'
        elif 'medium' in text.lower():
            return 'medium'
        elif 'low' in text.lower():
            return 'low'
        return 'medium'

    def _extract_timeline(self, text: str) -> str:
        """Extract timeline estimate from text."""
        import re
        timeline_match = re.search(r'(short|medium|long)-term', text, re.IGNORECASE)
        if timeline_match:
            return timeline_match.group(1)
        return 'medium-term'

