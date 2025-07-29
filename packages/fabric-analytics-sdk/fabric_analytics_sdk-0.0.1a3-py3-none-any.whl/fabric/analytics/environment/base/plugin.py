from abc import ABC, abstractmethod


class IPlugin(ABC):
    @abstractmethod
    def in_context(self) -> bool:
        raise Exception("Method Not Implemented")
