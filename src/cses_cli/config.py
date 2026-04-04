"""Configuration management for CSES CLI."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".cses-cli"
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class Config:
    """CSES CLI configuration."""

    timeout: float = 5.0
    python_command: str = "python3"
    solutions_dir: Optional[str] = None

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from ~/.cses-cli/config.toml."""
        config = cls()
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "rb") as f:
                    data = tomllib.load(f)
                if "timeout" in data:
                    config.timeout = float(data["timeout"])
                if "python_command" in data:
                    config.python_command = str(data["python_command"])
                if "solutions_dir" in data:
                    config.solutions_dir = str(data["solutions_dir"])
            except Exception:
                pass
        return config

    def save(self) -> None:
        """Save configuration to ~/.cses-cli/config.toml."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        lines = [
            "# CSES CLI Configuration",
            f'timeout = {self.timeout}',
            f'python_command = "{self.python_command}"',
        ]
        if self.solutions_dir:
            lines.append(f'solutions_dir = "{self.solutions_dir}"')
        CONFIG_FILE.write_text("\n".join(lines) + "\n")


def get_config() -> Config:
    """Get the current configuration."""
    return Config.load()
