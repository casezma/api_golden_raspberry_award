from abc import ABC, abstractmethod
from typing import List


class PrizeRepository(ABC):
    """The prize repository is the repository from the Prize Entity"""
    @abstractmethod
    def create(self, year: int, movie: 'MovieInputDTO', winner: bool):
        ...

    @abstractmethod
    def all_winners(self) -> List['PrizeOutputDTO']:
        ...

    @abstractmethod
    def delete_all(self):
        ...


class MovieInputDTO:
    """To avoid passing the Entity to repository, it will be passed a MovieInputDTO in
    case of the system requirements may change """

    def __init__(self,
                 _id: str,
                 name: str,
                 producer_name: str,
                 studio_name: str):
        self._id = _id
        self.name = name
        self.producer_name = producer_name
        self.studio_name = studio_name


class PrizeOutputDTO:
    """To avoid passing the Entity to repository, it will be passed a PrizeOutputDTO in
    case of the system requirements may change """

    def __init__(self,
                 _id: str,
                 year: int,
                 name: str,
                 producer: str,
                 studios: str,
                 winner: bool):
        self._id = _id
        self.year = year
        self.name = name
        self.producer = producer
        self.studios = studios
        self.winner = winner
