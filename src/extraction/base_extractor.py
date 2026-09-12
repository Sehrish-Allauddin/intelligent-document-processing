from abc import ABC, abstractmethod


class BaseExtractor(ABC):

    @abstractmethod
    def extract(self, ocr_results):
        pass