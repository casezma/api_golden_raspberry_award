from abc import ABC, abstractmethod
from uuid import uuid4, UUID


class Entity(ABC):
    """The Entity abstract class has an is_valid method which is resposible to validate
    this entity when it is applied on usecases."""
    @abstractmethod
    def is_valid(self) -> bool:
        ...


class Producer(Entity):
    def __init__(self, name: str, _id: UUID = None):
        self._id = uuid4() if _id is None else _id
        self.name = name

    def is_valid(self):
        """The Producer entity must have an UUID by default , the name be a string and not empty."""
        return isinstance(self._id, UUID) and \
            isinstance(self.name, str) and \
            self.name != ""


class Studios(Entity):
    def __init__(self, name: str, _id: UUID = None):
        self._id = uuid4() if _id is None else _id
        self.name = name

    def is_valid(self):
        """The Studios entity must have an UUID by default , the name be a string and not empty."""
        return isinstance(self._id, UUID) and \
            isinstance(self.name, str) and \
            self.name != ""


class Movie(Entity):

    def __init__(self, name: str, producer: Producer, studios: Studios, _id: UUID = None):
        self._id = uuid4() if _id is None else _id
        self.name = name
        self.producer = producer
        self.studios = studios

    def is_valid(self):
        """The Studios entity must have an UUID by default , the name be a string and not empty,
        a producer and studios entities.
        """
        return isinstance(self._id, UUID) and \
            isinstance(self.producer, Producer) and \
            isinstance(self.studios, Studios) and \
            self.name != ""


class Prize(Entity):
    def __init__(self, year: int, winner: bool, producer: Producer, _id: UUID = None):
        self._id = uuid4() if _id is None else _id
        self.year = year
        self.winner = winner
        self.producer = producer

    def is_valid(self):
        """The Prize entity must have an UUID by default , the name be a string and not empty,
        a producer and a winner boolean field. Following the specs, it is implied that the 
        smallest and largest years seems to be 1900 and 2099.
        """
        return isinstance(self._id, UUID) and \
            (isinstance(self.year, int) and self.year > 1900 and self.year < 2099) and \
            isinstance(self.winner, bool) and \
            isinstance(self.producer, Producer)
