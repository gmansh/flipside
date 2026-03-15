from abc import ABC, abstractmethod


class BaseAutomation(ABC):
    name: str
    schedule: str  # cron expression, e.g. "0 7 * * *"

    @abstractmethod
    async def run(self) -> list[list[int]]:
        """Execute the automation and return a 6x22 board to display."""
        ...

    def get_param_schema(self) -> list[dict]:
        """Return list of configurable parameter definitions.

        Each entry: {"key": str, "label": str, "type": "text"|"number"|"cron", "value": any}
        """
        return []

    def get_params(self) -> dict:
        """Return current parameter values as {key: value}."""
        return {}

    def set_params(self, params: dict) -> None:
        """Update parameters from {key: value}. Only sets known keys."""
        pass
