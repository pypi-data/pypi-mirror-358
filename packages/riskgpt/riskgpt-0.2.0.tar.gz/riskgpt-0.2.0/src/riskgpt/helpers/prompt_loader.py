from pathlib import Path
from typing import Any, Dict, Optional

import yaml  # type: ignore
from config.settings import RiskGPTSettings
from models.common import Prompt

# ``PROMPT_DIR`` is defined in a way that allows tests to override it using
# ``monkeypatch`` even when the module is reloaded.  On reload the module's
# globals are reused, therefore we only set the default value if it has not been
# provided already.  This mirrors the behaviour of environment derived
# configuration without hard coding the value on every reload.
if "PROMPT_DIR" not in globals():
    PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str, version: Optional[str] = None) -> Dict[str, Any]:
    if version is None:
        settings = RiskGPTSettings()
        version = settings.DEFAULT_PROMPT_VERSION

    path = PROMPT_DIR / name / f"{version}.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    prompt = Prompt(**data)
    return prompt.model_dump()


def load_system_prompt(version: Optional[str] = None) -> str:
    """Return the system prompt text for reuse across chains."""
    data = load_prompt("system", version)
    return data["template"]
