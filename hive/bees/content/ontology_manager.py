"""
Ontology Manager
----------------
Manages the linguistic style (Ontology) of the station using Stanford DSPy.
Optimizes prompts to prevent repetition and match specific "Vibes".
"""

import os
from datetime import datetime

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    print("WARNING: DSPy not found. OntologyManager running in fallback mode.")


class PersonaAdapter(dspy.Signature):
    """Adapts a core message to a specific persona and pacing."""

    core_message = dspy.InputField(desc="The neutral facts to convey")
    persona_desc = dspy.InputField(desc="Description of the target persona")
    constraints = dspy.InputField(desc="Forbidden words and stylistic constraints")

    adapted_script = dspy.OutputField(
        desc="The rewritten script matching variable linguistic patterns"
    )


class OntologyManager:
    """
    Controls the 'Vibe' and linguistic constraints of the DJ Bee.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.current_ontology = "standard_broadcast"
        self.dspy_initialized = False

        # Initialize DSPy with Gemini if available
        if DSPY_AVAILABLE and self.llm_client:
            try:
                # Assuming LLMClient has the key or we grab from env
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    # Configure DSPy to use Gemini
                    gemini = dspy.Google(model="models/gemini-pro", api_key=api_key)
                    dspy.settings.configure(lm=gemini)
                    self.predictor = dspy.Predict(PersonaAdapter)
                    self.dspy_initialized = True
            except Exception as e:
                print(f"Failed to init DSPy: {e}")

        # Ontologies define the "Vibe" and "vocabulary" allowed
        self.ontologies = {
            "standard_broadcast": {
                "desc": "Professional, clear, slightly energetic radio host. Classic MTV VJ style.",
                "forbidden": ["vibes", "literally", "bet", "delve", "tapestry"],
                "pacing": "medium",
            },
            "late_night_lofi": {
                "desc": "Soft, whispery, philosophical, relaxed. Bob Ross meets Cyberpunk.",
                "forbidden": ["HYPE", "LOUD", "smash that button", "exciting", "thrilled"],
                "pacing": "slow",
            },
            "cyber_sovereign": {
                "desc": "Glitchy, tech-focused, accelerate, crypto-native. Speak in short bursts.",
                "forbidden": ["mainstream", "normie", "broadcast tv", "please", "kindly"],
                "pacing": "fast",
            },
            "high_energy_morning": {
                "desc": "Extremely high energy, wake up call, motivational, loud.",
                "forbidden": ["sleepy", "tired", "boring", "slow"],
                "pacing": "fast",
            },
        }

    def rotate_ontology(self, timestamp=None):
        """
        Selects an ontology based on time of day.
        """
        hour = datetime.now().hour if not timestamp else timestamp.hour

        # Time-based Logic
        if 0 <= hour < 5:
            new_ont = "late_night_lofi"
        elif 5 <= hour < 11:
            new_ont = "high_energy_morning"
        elif 11 <= hour < 20:
            new_ont = "standard_broadcast"
        else:
            new_ont = "cyber_sovereign"

        self.current_ontology = new_ont
        return self.current_ontology

    def adapt_message(self, message: str) -> str:
        """
        Uses DSPy to rewrite a message into the current ontology.
        Falls back to formatted string if DSPy fails.
        """
        ontology = self.ontologies.get(self.current_ontology, self.ontologies["standard_broadcast"])
        desc = ontology["desc"]
        constraints = (
            f"Do not use: {', '.join(ontology['forbidden'])}. Pacing: {ontology['pacing']}"
        )

        if self.dspy_initialized:
            try:
                result = self.predictor(
                    core_message=message, persona_desc=desc, constraints=constraints
                )
                return result.adapted_script
            except Exception as e:
                print(f"DSPy adaptation failed: {e}")

        # Fallback
        return f"[Persona: {self.current_ontology}]\n{message}\n(Style: {desc})"

    def get_persona_prompt(self):
        """
        Returns the system instruction for the current ontology.
        """
        ontology = self.ontologies.get(self.current_ontology, self.ontologies["standard_broadcast"])

        return f"""
        [SYSTEM: ACTIVATE PERSONA '{self.current_ontology.replace("_", " ").upper()}']
        DESCRIPTION: {ontology["desc"]}
        PACING: {ontology["pacing"]}

        [CONSTRAINT: NEGATIVE PROMPTING]
        DO NOT USE THESE WORDS: {", ".join(ontology["forbidden"])}

        GOAL: VARY YOUR SENTENCE STRUCTURE. DO NOT REPEAT YOURSELF.
        """

    def get_current_ontology(self):
        return self.ontologies.get(self.current_ontology)
