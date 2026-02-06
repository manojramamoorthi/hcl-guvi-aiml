"""
AI Service for generating insights and recommendations
Supports OpenAI GPT-4 and Claude
"""
from typing import Dict, List, Any, Optional
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

# Import AI SDKs
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AIService:
    """AI-powered insights and recommendations generator"""
    
    def __init__(self):
        """Initialize AI service based on configuration"""
        self.provider = settings.AI_PROVIDER
        
        if self.provider == "openai" and OPENAI_AVAILABLE:
            openai.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL
        elif self.provider == "claude" and ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
            self.model = settings.CLAUDE_MODEL
        else:
            raise ValueError(f"AI provider '{self.provider}' not available or configured")
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Call Claude API"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return message.content[0].text
    
    def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Generate AI completion using configured provider"""
        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == "claude":
            return self._call_claude(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")
    
    def generate_financial_insights(
        self,
        company_data: Dict,
        financial_ratios: Dict,
        cash_flow_analysis: Dict,
        language: str = "en"
    ) -> str:
        """
        Generate narrative insights about company's financial health
        
        Args:
            company_data: Company profile information
            financial_ratios: Calculated financial ratios
            cash_flow_analysis: Cash flow analysis results
            language: Output language (en, hi)
            
        Returns:
            AI-generated narrative insights
        """
        system_prompt = f"""You are a financial analyst specializing in SME (Small and Medium Enterprise) financial health assessment. 
Your role is to provide clear, actionable insights that non-finance business owners can understand.
Output language: {'English' if language == 'en' else 'Hindi'}"""
        
        lang_instruction = "" if language == "en" else "Respond in Hindi (Devanagari script)."
        
        user_prompt = f"""{lang_instruction}

Analyze the following financial data for {company_data.get('name', 'the company')} in the {company_data.get('industry', '')} industry:

Financial Ratios:
{json.dumps(financial_ratios, indent=2)}

Cash Flow Analysis:
{json.dumps(cash_flow_analysis, indent=2)}

Provide:
1. Overall financial health assessment (2-3 sentences)
2. Key strengths (3 points)
3. Areas for improvement (3 points)
4. Top 3 actionable recommendations

Keep it concise, clear, and practical for business owners."""
        
        return self.generate_completion(system_prompt, user_prompt)
    
    def generate_cost_optimization_suggestions(
        self,
        expense_data: Dict,
        industry_benchmarks: Dict,
        language: str = "en"
    ) -> List[Dict[str, str]]:
        """
        Generate cost optimization suggestions
        
        Returns:
            List of suggestions with category, description, potential_impact
        """
        system_prompt = f"""You are a business efficiency consultant specializing in cost optimization for SMEs.
Provide specific, actionable cost reduction strategies.
Output language: {'English' if language == 'en' else 'Hindi'}"""
        
        lang_instruction = "" if language == "en" else "Respond in Hindi."
        
        user_prompt = f"""{lang_instruction}

Analyze these expenses and suggest cost optimization opportunities:

Current Expenses:
{json.dumps(expense_data, indent=2)}

Industry Benchmarks:
{json.dumps(industry_benchmarks, indent=2)}

Provide 5 specific cost optimization suggestions in JSON format:
[
  {{
    "category": "expense category",
    "suggestion": "specific recommendation",
    "potential_impact": "expected savings or benefit",
    "priority": "high/medium/low"
  }}
]

Return ONLY valid JSON array, no other text."""
        
        response = self.generate_completion(system_prompt, user_prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response if wrapped in markdown
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            suggestions = json.loads(response)
            return suggestions
        except json.JSONDecodeError:
            # Fallback if parsing fails
            return [{
                "category": "General",
                "suggestion": response[:200],
                "potential_impact": "To be determined",
                "priority": "medium"
            }]
    
    def recommend_financial_products(
        self,
        company_profile: Dict,
        credit_score: int,
        financial_needs: List[str],
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Recommend suitable financial products
        
        Returns:
            List of product recommendations
        """
        system_prompt = f"""You are a financial products advisor for SMEs in India.
Recommend appropriate banking and NBFC products based on company profile and needs.
Output language: {'English' if language == 'en' else 'Hindi'}"""
        
        lang_instruction = "" if language == "en" else "Respond in Hindi."
        
        user_prompt = f"""{lang_instruction}

Company Profile:
- Industry: {company_profile.get('industry')}
- Annual Revenue: ₹{company_profile.get('annual_revenue', 0):,.0f}
- Credit Score: {credit_score}/900
- Financial Needs: {', '.join(financial_needs)}

Recommend 3-5 suitable financial products (loans, credit lines, insurance, etc.) in JSON format:
[
  {{
    "product_type": "type (loan/credit_line/insurance)",
    "product_name": "specific product name",
    "provider": "bank or NBFC name",
    "key_features": ["feature1", "feature2"],
    "eligibility": "brief eligibility criteria",
    "why_suitable": "explanation of suitability"
  }}
]

Return ONLY valid JSON array."""
        
        response = self.generate_completion(system_prompt, user_prompt)
        
        # Parse JSON
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            products = json.loads(response)
            return products
        except json.JSONDecodeError:
            return []
    
    def generate_investor_report(
        self,
        company_data: Dict,
        financial_summary: Dict,
        health_score: Dict,
        language: str = "en"
    ) -> str:
        """
        Generate a comprehensive, investor-ready financial report
        """
        system_prompt = f"""You are a senior investment analyst. Generate a professional, investor-ready financial report for an SME.
The report should be structured, data-driven, and highlight potential for scale while being transparent about risks.
Output language: {'English' if language == 'en' else 'Hindi'}"""
        
        user_prompt = f"""Generate an investment profile for {company_data.get('name')}.
        
Business Context:
- Industry: {company_data.get('industry')}
- Annual Revenue: ₹{company_data.get('annual_revenue', 0):,.0f}

Financial Performance Summary:
{json.dumps(financial_summary, indent=2)}

Health Assessment:
- Score: {health_score.get('total_score')}/100
- Grade: {health_score.get('grade')}

Please structure the report with the following sections:
1. Executive Summary
2. Business Overview & Market Position
3. Financial Performance Analysis
4. Risk Assessment & Mitigation
5. Growth Trajectory & Opportunity
6. Investment Recommendation

Use professional financial terminology and keep it rigorous yet accessible."""
        
        return self.generate_completion(system_prompt, user_prompt)

    def translate_content(self, content: str, target_language: str) -> str:
        """
        Translate content to target language
        
        Args:
            content: Text to translate
            target_language: Target language code (en, hi)
            
        Returns:
            Translated text
        """
        if target_language == "en":
            return content  # Already in English
        
        lang_name = "Hindi" if target_language == "hi" else target_language
        
        system_prompt = f"You are a professional translator. Translate financial and business content to {lang_name} accurately."
        user_prompt = f"Translate the following to {lang_name}:\n\n{content}"
        
        return self.generate_completion(system_prompt, user_prompt)


# Global AI service instance
ai_service = AIService() if (settings.OPENAI_API_KEY or settings.CLAUDE_API_KEY) else None
