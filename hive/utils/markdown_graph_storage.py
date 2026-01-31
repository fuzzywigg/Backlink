import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MarkdownKnowledgeGraph:
    """
    A utility to manage a Knowledge Graph stored as flat Markdown files.

    Adopted from: https://github.com/mccartykim/md_knowledge_graph_mcp

    Each entity is a Markdown file.
    Relationships are defined as: `- verb [[TargetEntity]] context`
    """

    def __init__(self, directory_path: str):
        self.directory = Path(directory_path)
        # Ensure directory exists
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)

        # Pattern: - verb [[target]] context
        self.entity_pattern = re.compile(r"- (.*?) \[\[(.*?)\]\](?: (.*))?")

    def create_entity(self, name: str) -> bool:
        """Create a new entity markdown file."""
        file_path = self.directory / f"{name}.md"
        if file_path.exists():
            logger.debug(f"Entity '{name}' already exists.")
            return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {name}\n\n")
            return True
        except Exception as e:
            logger.error(f"Failed to create entity '{name}': {e}")
            return False

    def add_observation(self, entity_name: str, observation: str) -> bool:
        """Add an observation (text block) to an entity."""
        file_path = self.directory / f"{entity_name}.md"
        if not file_path.exists():
            # Auto-create if not exists? For now, fail as per original spec,
            # or maybe auto-create is better? Original spec returns False.
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if "## Relationships" in content:
                parts = content.split("## Relationships")
                # Ensure proper spacing
                pre_content = parts[0]
                if not pre_content.endswith("\n\n"):
                    pre_content += "\n" if pre_content.endswith("\n") else "\n\n"

                new_content = pre_content + f"{observation}\n\n" + "## Relationships" + parts[1]
            else:
                new_content = content
                if new_content and not new_content.endswith("\n\n"):
                    new_content += "\n" if new_content.endswith("\n") else "\n\n"
                new_content += f"{observation}\n\n"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        except Exception as e:
            logger.error(f"Failed to add observation to '{entity_name}': {e}")
            return False

    def add_relationship(self, source: str, verb: str, target: str, context: str = "") -> bool:
        """Add a relationship: Source - verb -> Target."""
        file_path = self.directory / f"{source}.md"
        if not file_path.exists():
            return False

        if source == target:
            logger.warning(f"Prevented self-referential relationship for {source}")
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Format: - verb [[Target]] context
            rel_line = f"- {verb} [[{target}]]"
            if context:
                rel_line += f" {context}"
            rel_line += "\n"

            if "## Relationships" not in content:
                if not content.endswith("\n"):
                    content += "\n"
                content += "## Relationships\n" + rel_line
            else:
                parts = content.split("## Relationships")
                # Append to existing section
                content = parts[0] + "## Relationships" + parts[1].rstrip() + "\n" + rel_line

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to add relationship {source}->{target}: {e}")
            return False

    def get_full_graph(self) -> dict[str, Any]:
        """Return the complete knowledge graph as a dict."""
        graph = {"entities": {}, "relationships": []}

        for file_path in self.directory.glob("*.md"):
            entity_name = file_path.stem

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                continue

            lines = content.split("\n")
            observations = []
            relationships = []
            in_relationships = False

            for line in lines:
                stripped = line.strip()
                if line.startswith("## Relationships"):
                    in_relationships = True
                    continue
                elif line.startswith("## ") and in_relationships:
                    # New section started
                    in_relationships = False

                if in_relationships and stripped.startswith("- "):
                    match = self.entity_pattern.match(stripped)
                    if match:
                        groups = match.groups()
                        verb, target = groups[0], groups[1]
                        # group 3 is optional context
                        ctx = groups[2] if len(groups) > 2 and groups[2] else ""

                        rel = {
                            "source": entity_name,
                            "verb": verb,
                            "target": target,
                            "context": ctx or "",
                        }
                        relationships.append(rel)
                        graph["relationships"].append(rel)

                # Capture observations (non-header, non-relationship lines)
                elif not in_relationships and not line.startswith("#") and stripped:
                    observations.append(stripped)

            graph["entities"][entity_name] = {
                "name": entity_name,
                "observations": observations,
                "relationships": relationships,
            }

        return graph

    def delete_entity(self, name: str) -> bool:
        """Delete an entity file and remove incoming links."""
        file_path = self.directory / f"{name}.md"
        if not file_path.exists():
            return False

        try:
            os.remove(file_path)
            # Remove relationships in other files pointing to this entity
            for other_file in self.directory.glob("*.md"):
                self._remove_relationships_to(other_file, name)
            return True
        except Exception as e:
            logger.error(f"Failed to delete entity '{name}': {e}")
            return False

    def _remove_relationships_to(self, file_path: Path, target_entity: str):
        """Helper to remove lines containing [[target_entity]]"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = [line for line in lines if f"[[{target_entity}]]" not in line]

            if len(new_lines) != len(lines):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
        except Exception as e:
            logger.error(f"Failed to clean relationships in {file_path}: {e}")
