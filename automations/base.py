from abc import ABC, abstractmethod


class BaseAutomation(ABC):
    name: str
    schedule: str  # cron expression, e.g. "0 7 * * *"

    @abstractmethod
    async def run(self) -> list[list[int]]:
        """Execute the automation and return a 6x22 board to display."""
        ...
