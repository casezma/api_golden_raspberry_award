from abc import ABC, abstractmethod
from collections import defaultdict
import logging
from typing import Dict, List
from repository.prize_repository import PrizeRepository


logger = logging.getLogger(__name__)


class Filter(ABC):

    @abstractmethod
    def execute(self):
        ...

    @abstractmethod
    def get_schema(self):
        ...


class FilterSchema:

    @abstractmethod
    def dict(self) -> dict:
        ...


class IntervalCannotBeCalculatedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ProducerPreviousFollowingWinFilterSchema(FilterSchema):
    """This Filter Schema responsible to return the information of the interval 
    and the previous and following win from the producer."""

    def __init__(self, producer: str, year: int):
        self.producer = producer
        self.previous_win = None
        self.following_win = None
        self.__year = year

    def get_interval(self):
        """Calculates the interval of the previous and following wins. 
        If at least one of them are None, it  will return None or else it returns the 
        calculated interval"""
        if self.previous_win is None or self.following_win is None:
            return None
        return self.following_win - self.previous_win

    def update(self, winning_year: int):
        """Updates the previous and the following win of the producer
        for each iteration."""
        self.__update_case_previous_and_following_win_is_not_none(winning_year)
        self.__update_case_previous_and_following_win_is_none(winning_year)

    def __update_case_previous_and_following_win_is_none(self, winning_year):
        """If the previous and following case are None, then it will compare
        the first informed prize with the last one, and then it will update
        the previous and following variables"""
        if self.previous_win is None and self.following_win is None:
            if self.__year >= winning_year:
                self.previous_win = winning_year
                self.following_win = self.__year

            else:
                self.previous_win = self.__year
                self.following_win = winning_year

    def __update_case_previous_and_following_win_is_not_none(self, winning_year):
        """If the previous and following case are NOT None, then it will compare
        the first informed prize with the last one, and then it will update
        the previous and following variables"""

        if not self.previous_win is None and not self.following_win is None:
            if self.previous_win >= winning_year:
                aux = self.previous_win
                self.previous_win = winning_year
                self.following_win = aux
            else:
                aux = self.following_win
                self.following_win = winning_year
                self.previous_win = aux

    def dict(self) -> dict:
        return {
            "producer": self.producer,
            "interval": self.get_interval(),
            "previousWin": self.previous_win,
            "followingWin": self.following_win
        }


class PrizeIntervalFilterSchema(FilterSchema):
    """This is the Filter Schema responsible to return the min and max producers lists"""

    def __init__(
            self,
            _min: List[ProducerPreviousFollowingWinFilterSchema],
            _max: List[ProducerPreviousFollowingWinFilterSchema]):

        self._min: List[ProducerPreviousFollowingWinFilterSchema] = _min
        self._max: List[ProducerPreviousFollowingWinFilterSchema] = _max

    def dict(self) -> dict:
        return {
            "min": self._min,
            "max": self._max
        }


class PrizeIntervalFilter:
    """In order to filter the producer with the longest gap between two consecutive awards, and what
       got two awards faster this filter returns a schema that can be used from the usecase to present
       in a django view."""

    def __init__(self, repo: PrizeRepository):
        self.repo = repo
        self.__producers: Dict[int,
                               ProducerPreviousFollowingWinFilterSchema] = dict()
        self.__min_interval_producers: List[ProducerPreviousFollowingWinFilterSchema] = list(
        )
        self.__max_interval_producers: List[ProducerPreviousFollowingWinFilterSchema] = list(
        )

    def get_schema(self) -> PrizeIntervalFilterSchema:
        return PrizeIntervalFilterSchema(
            _min=self.__min_interval_producers,
            _max=self.__max_interval_producers)

    def execute(self):
        """This command get from the repository all the prize winners.

        For each prize winner, it gets the produce_name as the key and 
        saves a ProducerPreviousFollowingWinFilterSchema object in the
        __self.producers dict.

        After iterating it, it filters all the users that won more than one time.

        For each producer that won more than one time, it will sort who has the smallest and the 
        biggest gap, populating the min and max producers lists (self.__min_interval_producers and
        self.__max_interval_producers)
        """
        items = self.repo.all_winners()

        for item in items:
            producer_name = item.producer
            if producer_name in self.__producers:
                producer = self.__producers.get(producer_name)

                try:
                    producer.update(item.year)
                except IntervalCannotBeCalculatedException as interval_not_calculated:
                    logging.debug(str(interval_not_calculated))
                continue
            producer = ProducerPreviousFollowingWinFilterSchema(
                producer=producer_name,
                year=item.year)

            self.__producers[item.producer] = producer

        producers_that_won_more_than_one_time = list(
            filter(lambda x: x.get_interval() is not None, self.__producers.values()))
        producers_interval_dict = defaultdict(list)
        for producer in producers_that_won_more_than_one_time:
            producers_interval_dict[producer.get_interval()].append(producer)

        if sorted_producers_interval_dict := list(sorted(producers_interval_dict)):
            min_producer_index = sorted_producers_interval_dict[0]
            max_producer_index = sorted_producers_interval_dict[-1]
            self.__min_interval_producers = list(sorted(
                producers_interval_dict[min_producer_index], key=lambda x: x.previous_win))
            self.__max_interval_producers = list(sorted(
                producers_interval_dict[max_producer_index], key=lambda x: x.previous_win))
