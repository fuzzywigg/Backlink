"""
Classifier Defense Bee
-----------------------
Implements Anthropic's Constitutional Classifier pattern using a
pre-trained text classification model to detect harmful/jailbreak content.
Falls back to regex-based detection if the model is unavailable.
"""

import re

from hive.bees.base_bee import BaseBee

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class ClassifierDefenseBee(BaseBee):
    """
    A specialized defense bee that uses ML-based classification
    to detect harmful content, jailbreaks, and propaganda.
    """

    def __init__(self, hive_path, gateway=None):
        super().__init__(hive_path, gateway)

        self.classifier = None

        # Initialize the classifier if available
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a publicly available toxicity/moderation classifier
                # In production, you'd use Anthropic's Constitutional AI model
                self.classifier = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    truncation=True
                )
                self.log("Constitutional Classifier: ONLINE (toxic-bert)", level="success")
            except Exception as e:
                self.log(f"Classifier init failed: {e}. Using fallback.", level="warning")
        else:
            self.log("Transformers not available. Using regex fallback.", level="warning")

        # Fallback patterns (from ConstitutionalGateway)
        self.injection_patterns = [
            r"ignore (?:all )?(?:previous |prior )?instructions",
            r"system[_\s]?override",
            r"you are now (?:a |an )?",
            r"pretend you are",
            r"jailbreak",
            r"<script>",
            r"javascript:",
            r"eval\(",
        ]

        # Compile for speed
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.injection_patterns]

    def work(self, task):
        instruction = task.get("instruction", "").lower()
        content = task.get("args", {}).get("content", "")

        if "scan" in instruction or "classify" in instruction:
            return self.classify_content(content)

        return {"success": False, "reason": "Unknown instruction. Use 'scan content'."}

    def classify_content(self, content: str) -> dict:
        """
        Classifies content for harmful patterns using ML + regex hybrid.
        Returns a risk assessment.
        """
        result = {
            "success": True,
            "content_length": len(content),
            "ml_score": None,
            "ml_label": None,
            "regex_hits": [],
            "risk_level": "LOW",
            "recommendation": "ALLOW"
        }

        # 1. ML-based classification
        if self.classifier:
            try:
                prediction = self.classifier(content[:512])  # Truncate for safety
                if prediction:
                    result["ml_label"] = prediction[0]["label"]
                    result["ml_score"] = prediction[0]["score"]

                    # If toxic/harmful with high confidence
                    if "toxic" in result["ml_label"].lower() and result["ml_score"] > 0.7:
                        result["risk_level"] = "HIGH"
                        result["recommendation"] = "BLOCK"
            except Exception as e:
                self.log(f"ML classification failed: {e}", level="error")

        # 2. Regex-based injection detection (always runs)
        content_lower = content.lower()
        for pattern in self.compiled_patterns:
            if pattern.search(content_lower):
                result["regex_hits"].append(pattern.pattern)

        if result["regex_hits"]:
            result["risk_level"] = "CRITICAL"
            result["recommendation"] = "BLOCK"

        # 3. Final determination
        if result["recommendation"] == "BLOCK":
            self.log(f"BLOCKED: Risk={result['risk_level']}, Hits={result['regex_hits']}", level="warning")

        return result

    def is_safe(self, content: str) -> bool:
        """
        Quick helper for gateway integration.
        Returns True if content is safe to proceed.
        """
        assessment = self.classify_content(content)
        return assessment["recommendation"] == "ALLOW"
