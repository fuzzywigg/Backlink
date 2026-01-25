"""
Base Bee Agent - The template for all worker bees in the hive.

All bees inherit from this class and implement their specific work() method.
Bees communicate through the honeycomb (shared state files), not directly.
Updated to support Constitutional Governance.
"""

import json
import logging
import uuid
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hive.utils.prompt_engineer import PromptEngineer
from hive.utils.state_manager import StateManager
from hive.utils.storage_adapter import StorageAdapter


class BaseBee(ABC):
    """
    Abstract base class for all bee agents.
    Now equipped with a Constitutional Gateway for ethical checks.

    Bees follow the stigmergy pattern:
    - Read from honeycomb (shared state)
    - Do their work
    - Write results back to honeycomb
    - No direct bee-to-bee communication
    """

    BEE_TYPE = "base"
    BEE_NAME = "Base Bee"
    CATEGORY = "general"

    def __init__(self, hive_path: str | None = None, gateway: Any = None):
        """
        Initialize the bee.

        Args:
            hive_path: Path to the root hive directory.
            gateway: Instance of ConstitutionalGateway for governance checks.
        """
        # Logging setup
        self.logger = logging.getLogger(self.BEE_NAME)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f"[%(asctime)s] [{self.BEE_TYPE.upper()}] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        if hive_path is None:
            # Default to hive directory relative to this file
            # hive/bees/base_bee.py -> parent=bees -> parent=hive -> parent=root
            hive_path = Path(__file__).parent.parent.parent
        
        self.hive_path = Path(hive_path)
        # Standard structure: root/hive/honeycomb
        self.honeycomb_path = self.hive_path / "hive" / "honeycomb"
        self.gateway = gateway

        # Generate Unique Bee ID
        self.bee_id = f"{self.BEE_TYPE}_{str(uuid.uuid4())[:8]}"

        # Logic Brain (Gemini 3)
        from hive.utils.gemini_client import Gemini3Client

        try:
            self.llm_client = Gemini3Client()
        except Exception as e:
            self.llm_client = None
            self.logger.warning(f"Gemini 3 Client failed to initialize: {e}")

        # Initialize State Manager
        # StateManager expects the path to the 'hive' directory to find 'honeycomb' inside it
        self.state_manager = StateManager(self.hive_path / "hive")

        # Initialize Storage Adapter
        self.storage = StorageAdapter(self.honeycomb_path)

        # Initialize Wisdom Manager (System 3)
        from hive.utils.wisdom_manager import WisdomManager
        self.wisdom_manager = WisdomManager(self.hive_path)

    @abstractmethod
    def work(self, task: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Perform the bee's primary function.
        Must be implemented by subclasses.
        """
        pass

    def run(self, task: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Main entry point. Wraps work() with validation and error handling.
        """
        self.started_at = datetime.now(timezone.utc)
        start_time = time.time()
        self.log(f"Starting work... Task: {task.get('id') if task else 'None'}")

        try:
            # 1. Validate (if Gateway exists)
            if self.gateway:
                action_context = {"bee": self.BEE_TYPE, "task": task}
                is_valid, reason = self.gateway.validate_action(action_context)
                if not is_valid:
                    self.log(f"Action BLOCKED by Gateway: {reason}", level="error")
                    return {
                        "success": False,
                        "error": "constitutional_block",
                        "reason": reason,
                        "bee_id": self.bee_id,
                        "duration_seconds": time.time() - start_time,
                    }

            # 2. Execute
            work_result = self.work(task)

            # 3. Log Success
            self.completed_at = datetime.now(timezone.utc)
            duration = time.time() - start_time
            self.log(f"Work complete in {duration:.2f}s")
            return {
                "success": True,
                "result": work_result,
                "bee_id": self.bee_id,
                "duration_seconds": duration,
            }

        except Exception as e:
            self.completed_at = datetime.now(timezone.utc)
            self.log(f"CRITICAL FAILURE: {e}", level="error")
            return {
                "success": False,
                "error": str(e),
                "bee_id": self.bee_id,
                "duration_seconds": time.time() - start_time,
            }

    # ─────────────────────────────────────────────────────────────
    # STATE / HONEYCOMB INTERFACE
    # ─────────────────────────────────────────────────────────────

    def _read_json(self, filename: str) -> dict[str, Any]:
        """Read a JSON file using StorageAdapter."""
        if filename == "state.json":
            return self.state_manager.read_state()

        return self.storage.read(filename)

    def _write_json(self, filename: str, data: dict[str, Any]) -> None:
        """Write a JSON file using StorageAdapter."""
        if filename == "state.json":
            self.state_manager.write_state(data, self.BEE_TYPE)
            return

        self.storage.write(filename, data)

    # ─────────────────────────────────────────────────────────────
    # CONVENIENCE METHODS
    # ─────────────────────────────────────────────────────────────

    def read_state(self) -> dict[str, Any]:
        """Read state.json."""
        return self._read_json("state.json")

    def write_state(self, updates: dict[str, Any]) -> None:
        """Write/Update state.json."""
        self._write_json("state.json", updates)

    def read_tasks(self) -> dict[str, Any]:
        """Read tasks.json."""
        return self._read_json("tasks.json")

    def write_task(self, task: dict[str, Any]) -> str:
        """Add a new task to pending queue."""
        tasks = self.read_tasks()
        if "pending" not in tasks:
            tasks["pending"] = []

        task_id = str(uuid.uuid4())
        task["id"] = task_id
        task["status"] = "pending"
        task["created_at"] = datetime.now(timezone.utc).isoformat()

        tasks["pending"].append(task)
        self._write_json("tasks.json", tasks)
        return task_id

    def claim_task(self, task_id_or_type: str) -> dict[str, Any] | None:
        """Claim a task from the pending queue."""
        tasks = self.read_tasks()
        pending = tasks.get("pending", [])

        found_index = -1
        found_task = None

        for i, task in enumerate(pending):
            if task.get("id") == task_id_or_type or task.get("type") == task_id_or_type:
                found_index = i
                found_task = task
                break

        if found_task:
            tasks["pending"].pop(found_index)
            found_task["status"] = "in_progress"
            found_task["started_at"] = datetime.now(timezone.utc).isoformat()
            found_task["worker_bee_id"] = self.bee_id

            if "in_progress" not in tasks:
                tasks["in_progress"] = []
            tasks["in_progress"].append(found_task)

            self._write_json("tasks.json", tasks)
            return found_task

        return None

    def complete_task(self, task_id: str, result: dict[str, Any]) -> None:
        """Mark a task as completed."""
        tasks = self.read_tasks()
        in_progress = tasks.get("in_progress", [])

        found_index = -1
        found_task = None

        for i, task in enumerate(in_progress):
            if task.get("id") == task_id:
                found_index = i
                found_task = task
                break

        if found_task:
            tasks["in_progress"].pop(found_index)
            found_task["status"] = "completed"
            found_task["completed_at"] = datetime.now(timezone.utc).isoformat()
            found_task["result"] = result

            if "completed" not in tasks:
                tasks["completed"] = []
            tasks["completed"].append(found_task)
            
            self._write_json("tasks.json", tasks)

    def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed (may retry if attempts < max)."""
        tasks = self.read_tasks()
        in_progress = tasks.get("in_progress", [])
        
        found_index = -1
        found_task = None

        for i, task in enumerate(in_progress):
            if task.get("id") == task_id:
                found_index = i
                found_task = task
                break
                
        if found_task:
            tasks["in_progress"].pop(found_index)
            found_task["last_error"] = error
            found_task["failed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Simple retry logic
            attempts = found_task.get("attempts", 0) + 1
            found_task["attempts"] = attempts
            max_attempts = found_task.get("max_attempts", 3)

            if attempts < max_attempts:
                # Retry - put back in pending
                found_task["status"] = "pending"
                if "pending" not in tasks:
                    tasks["pending"] = []
                tasks["pending"].append(found_task)
            else:
                # Max attempts reached
                found_task["status"] = "failed"
                if "failed" not in tasks:
                    tasks["failed"] = []
                tasks["failed"].append(found_task)

            self._write_json("tasks.json", tasks)

    def read_intel(self) -> dict[str, Any]:
        """Read the accumulated intelligence."""
        return self._read_json("intel.json")

    def write_intel(self, category: str, key: str, data: dict[str, Any]) -> None:
        """Add or update intel in a category."""
        intel = self.read_intel()
        if category not in intel:
            intel[category] = {}

        if key in intel[category]:
            # Merge with existing
            intel[category][key] = self._deep_merge(intel[category][key], data)
        else:
            intel[category][key] = data

        if "_meta" not in intel:
            intel["_meta"] = {}
        intel["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._write_json("intel.json", intel)
    
    def update_intel(self, updates: dict[str, Any]) -> None:
        """Direct update to intel.json."""
        intel = self.read_intel()
        intel.update(updates)
        self._write_json("intel.json", intel)

    def add_listener_intel(self, node_id: str, intel_data: dict[str, Any]) -> None:
        """Convenience method to add listener intel."""
        intel = self.read_intel()
        existing = intel.get("listeners", {}).get("known_nodes", {}).get(node_id, {})

        # Ensure notes are appended, not replaced
        if "notes" in intel_data and "notes" in existing:
            intel_data["notes"] = existing["notes"] + intel_data["notes"]

        # Ensure numeric fields are accumulated
        for field in ["dao_credits", "donation_total", "interaction_count"]:
            if field in intel_data and field in existing:
                intel_data[field] = existing[field] + intel_data[field]

        intel_data["last_seen"] = datetime.now(timezone.utc).isoformat()
        if "first_seen" not in existing:
            intel_data["first_seen"] = intel_data["last_seen"]

        self.write_intel("listeners", f"known_nodes.{node_id}", intel_data)

    def post_alert(self, message: str, priority: bool = False) -> None:
        """Post an alert to state.json."""
        state = self._read_json("state.json")
        if "alerts" not in state:
            state["alerts"] = {"priority": [], "general": [], "normal": []}

        alert = {
            "message": message,
            "from": self.BEE_TYPE,
            "at": datetime.now(timezone.utc).isoformat(),
        }
        
        category = "priority" if priority else "normal"
        if category not in state["alerts"]:
            state["alerts"][category] = []
        state["alerts"][category].append(alert)
        
        self.write_state(state)

    # ─────────────────────────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────────────────────────

    def log(self, message: str, level: str = "info") -> None:
        """Log a message (for debugging/monitoring)."""
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"[{timestamp}] [{level.upper()}] [{self.bee_id}] {message}") 
        # Also use standard logger
        if level.lower() == "error":
            self.logger.error(message)
        elif level.lower() == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def _deep_merge(self, base: dict, updates: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _ask_llm_json(self, prompt_engineer: PromptEngineer, user_input: str) -> dict[str, Any]:
        """
        Structured LLM Query using Gemini 3 Native Structured Output.
        """
        if not self.llm_client:
            return {"error": "LLM Client not initialized"}

        # 0. Inject System 3 Wisdom (Episodic Memory)
        try:
            wisdom = self.wisdom_manager.get_relevant_wisdom()

            # Add Global Constraints if any
            if wisdom.get("constraints"):
                prompt_engineer.add_section("SYSTEM 3 WISDOM (LEARNED CONSTRAINTS)")
                for constraint in wisdom["constraints"]:
                    prompt_engineer.add_constraint(f"[LEARNED] {constraint['content']}")

            # Add Theology/Context
            if wisdom.get("theology", {}).get("core_tenets"):
                prompt_engineer.add_context("\n".join(wisdom["theology"]["core_tenets"]))

        except Exception as w_err:
            self.log(f"Wisdom retrieval failed: {w_err}", level="warning")

        # Enforce Global JSON Preference
        prompt_engineer.add_constraint("OUTPUT MUST BE RAW JSON. NO PYTHON CODE BLOCKS.")
        system_prompt = prompt_engineer.build_system_prompt()

        try:
            response = self.llm_client.generate_content(
                prompt=f"{system_prompt}\n\nUSER INPUT: {user_input}",
                thinking_level="low",
                response_schema=None, 
            )

            if "error" in response:
                return response

            # Parse
            return PromptEngineer.parse_json_output(response.get("text", ""))

        except Exception as e:
            self.log(f"LLM Structure Failure: {e}", level="error")
            return {"error": str(e)}


class EmployedBee(BaseBee):
    """
    A bee that has a specific role or employment (e.g. DJ, Researcher).
    """
    BEE_TYPE = "employed"
    CATEGORY = "content"


class ScoutBee(BaseBee):
    """
    A bee that looks for things (trends, sponsors).
    """
    BEE_TYPE = "scout"
    CATEGORY = "research"


class OnlookerBee(BaseBee):
    """
    A bee that observes (monitoring, logging).
    """
    BEE_TYPE = "onlooker"
    CATEGORY = "research"
