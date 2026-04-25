import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

PRIORITY_PROMPT = """You are a task prioritization assistant. Analyze the task below and assign a priority level.

Task Title: {title}
Task Description: {description}

Respond ONLY with a valid JSON object in this exact format (no markdown, no extra text):
{{
  "priority": "high" | "medium" | "low",
  "reasoning": "One sentence explaining why."
}}

Priority guidelines:
- high: Urgent, blocking others, production issues, security, deadlines within 24h
- medium: Important but not urgent, affects multiple users, should be done this week
- low: Nice-to-have, minor improvements, no immediate impact
"""


async def get_ai_priority(title: str, description: str | None) -> dict:
    prompt = PRIORITY_PROMPT.format(
        title=title,
        description=description or "No description provided.",
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1},
                },
            )
            response.raise_for_status()
            raw_text = response.json().get("response", "")
            result = json.loads(raw_text.strip())
            priority = result.get("priority", "medium").lower()
            reasoning = result.get("reasoning", "AI prioritized this task.")

            if priority not in ("high", "medium", "low"):
                priority = "medium"

            return {"priority": priority, "reasoning": reasoning}

    except httpx.ConnectError:
        logger.warning("Ollama not reachable — falling back to medium priority.")
        return {
            "priority": "medium",
            "reasoning": "AI service unavailable. Defaulted to medium priority.",
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to parse Ollama response: %s", e)
        return {
            "priority": "medium",
            "reasoning": "Could not parse AI response. Defaulted to medium priority.",
        }
    except Exception as e:
        logger.error("Unexpected error calling Ollama: %s", e)
        return {
            "priority": "medium",
            "reasoning": "Unexpected error during AI prioritization.",
        }

