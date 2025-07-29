from abc import ABC, abstractmethod

from event_scraper_generics.types.submission import ScraperTypes, GroupEventsKernel, EventsToUploadFromCalendarID


class Scraper(ABC):
    """
    The class used to retrieve information from a particular source type.
    """
    @abstractmethod
    def connect_to_source(self) -> None:
        pass

    @abstractmethod
    def retrieve_from_source(self, event_kernel: GroupEventsKernel) -> list[EventsToUploadFromCalendarID]:
        """
        Takes GroupEventKernel and returns list[EventsToUploadFromCalendarID]
        """
        pass

    @abstractmethod
    def close_connection_to_source(self) -> None:
        pass

    @abstractmethod
    def get_source_type(self) -> ScraperTypes:
        pass


