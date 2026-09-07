import json
import ollama

from app.core.config import settings
from app.schemas.expense import AIInsight

class AIService:
    @staticmethod
    async def generate_insight(summary_data: dict) -> AIInsight | None:
        if not summary_data.get("by_category"):
            return AIInsight(
                summary="No expense data available to analyze yet.",
                tips=["Start logging your daily expenses to recieve personalized savings tips."]
            )

        client = ollama.AsyncClient(
            host=getattr(settings, "OLLAMA_HOST", "http://localhost:11434")
        )

        prompt = f"""
            Analyze this user's monthly finances:
            - Total Spending: ${summary_data.get('total_spending')}
            - Current Month Spending: ${summary_data.get('current_month_spending')}
            - Category Breakdown: {summary_data.get('by_category')}

            Provide:
            1. A 2-sentence summary highlighting the top spending area.
            2. Exactly 3 realistic, actionable tips to reduce expenses.
            Respond ONLY with a valid JSON object in this format:
            {{
                "summary": "...",
                "tips": ["tip 1", "tip 2", "tip 3"]
            }}
            """

        try:
            response = await client.chat(
                model=getattr(settings, "OLLAMA_MODEL", "qwen2.5:3b"),
                messages=[
                    {"role": "system", "content": "You are a professional financial advisor. Always respond in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                format="json",
                options={
                    "temperature": 0.3,
                    "num_ctx": 2048,
                    "top_p": 0.9
                }
            )
            result_json = json.loads(response.message.content)
            return AIInsight(**result_json)
        except Exception as e:
            return AIInsight(
                summary="AI service is currently unavailable.",
                tips=["Ensure your local ollama server is running."]
            )