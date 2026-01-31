"""
Queen Task Router
-----------------
Implements the "Router" Pattern for intelligent task decomposition.
Uses Gemini 2.0 schemas to strictly enforce the output structure of valid plans.
"""

import json
import os
from typing import Any

from hive.utils.llm import LLMClient


class TaskRouter:
    """
    Analyzes high-level instructions and routes them to specific bees
    using a structured execution plan.
    """

    def __init__(self, llm_client: LLMClient = None):
        # Pass a minimal config if initializing a new client
        self.llm = llm_client or LLMClient(config={"llm": {"model": "gemini-2.0-flash-exp"}})

    def route_task(self, instruction: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Analyze a task and return a routing plan.
        """
        # 1. Define the Schema for the Plan
        plan_schema = {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "description": "A concise summary of what the user wants to achieve."
                },
                "complexity": {
                    "type": "string",
                    "enum": ["simple", "complex"],
                    "description": "Simple tasks need 1 bee. Complex tasks need coordination."
                },
                "reasoning": {
                    "type": "string",
                    "description": "Explanation of why these specific bees were chosen."
                },
                "assignments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "bee_type": {
                                "type": "string",
                                "enum": ["scout", "dj", "show_prep", "weather", "stream_monitor", "treasury", "security", "kv_store"],
                                "description": "The specific type of bee agent to handle this sub-task."
                            },
                            "instruction": {
                                "type": "string",
                                "description": "Specific, actionable instruction for this bee."
                            },
                            "task_args": {
                                "type": "object",
                                "description": "Key-value pairs of arguments to pass to the bee's work() method."
                            },
                            "order": {
                                "type": "integer",
                                "description": "Execution order (1-based index). Bees with same order run in parallel."
                            }
                        },
                        "required": ["bee_type", "instruction", "order"]
                    }
                }
            },
            "required": ["intent", "complexity", "assignments"]
        }

        # 2. Construct the Prompt
        # We inject available bees context to help the LLM make good decisions
        prompt = f"""
        You are the Routing Logic for the Hive Queen.
        Your goal is to break down a high-level User Instruction into a concrete Execution Plan.

        AVAILABLE BEES:
        - scout: Research, web scraping, link analysis.
        - dj: Play music, manage playlist, buy songs (with treasury approval).
        - show_prep: Write scripts, find trivia, research topics.
        - weather: Check weather for specific locations.
        - stream_monitor: Check stream health (bitrate = technical).
        - treasury: (Planned) Handle payments/wallets.
        - security: Audio logs/files, check permissions, scan repos.
        - kv_store: Read/Write persistent memory.

        USER INSTRUCTION: "{instruction}"

        CONTEXT: {json.dumps(context or {})}

        OUTPUT SCHEMA (JSON):
        {json.dumps(plan_schema, indent=2)}

        Generate a VALID JSON object matching this schema exactly.
        """

        # 3. Call LLM with Generation Config (JSON Mode)
        try:
            # Access the underlying GenerativeModel instance
            model = self.llm.default_model

            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json"
                    # "response_schema": plan_schema # Disabled to allow dynamic task_args
                }
            )

            return json.loads(response.text)

        except Exception as e:
            print(f"Router Error: {e}")
            return {
                "intent": "Error in routing",
                "complexity": "simple",
                "assignments": [],
                "error": str(e)
            }

if __name__ == "__main__":
    # Self-test
    print("Initializing Router...")
    # Mocking correct environment for the test
    os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', '')

    router = TaskRouter()

    test_instruction = "Check the stream health and then find me some news about AI agents."
    print(f"\nRouting Instruction: '{test_instruction}'")

    plan = router.route_task(test_instruction)
    print("\nGenerated Plan:")
    print(json.dumps(plan, indent=2))
