from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Tuple
from repository.prize_repository import PrizeRepository, MovieInputDTO
from domain.prize.entity import Producer, Prize, Studios, Movie
from repository.filters import PrizeIntervalFilter


class UseCase(ABC):
    """The base class of use cases must have the execute method."""
    @abstractmethod
    def execute(self):
        ...


class PopulatePrizeData(UseCase):
    """This use case is responsible to populate the prize data."""
    class DTOOutput:
        def __init__(self, status: str, msg: str, data: dict = dict()):
            self.status = status
            self.msg = msg
            self.data = data

    def __init__(
            self,
            repo: PrizeRepository,
            producer_name: str,
            movie_name: str,
            studios_name: str,
            year: int,
            winner: bool):

        self.repo = repo
        self.producer_name = producer_name
        self.movie_name = movie_name
        self.studios_name = studios_name
        self.year = year
        self.winner = winner

    def execute(self) -> DTOOutput:
        """This command will check if the winner is 'yes'(True) or ''(False), or else
        it will returns a fail that the informed data is not valid.

        It will create all the Entities instances and check if they are valid.

        If they are, it will be sent to repository and then populate the repository.
        If everything works fine, then it will return a 'OK' status, or else it will
        return an error, informing which field is invalid.
        """
        try:
            if self.winner in ["yes", ""]:
                self.winner = self.winner == "yes"
                producer = Producer(name=self.producer_name)
                studios = Studios(name=self.studios_name)
                movie = Movie(name=self.movie_name,
                              producer=producer, studios=studios)
                prize = Prize(year=self.year, winner=self.winner,
                              producer=producer)

                is_valid, invalid_items = self.__all_entities_are_valid(
                    producer, studios, movie, prize)
                if is_valid:
                    movie_input_dto = MovieInputDTO(
                        _id=movie._id,
                        name=movie.name,
                        producer_name=movie.producer.name,
                        studio_name=movie.studios.name
                    )

                    self.repo.create(
                        year=self.year, movie=movie_input_dto, winner=self.winner)
                    return PopulatePrizeData.DTOOutput(status="OK", msg="Object created")
                return PopulatePrizeData.DTOOutput(status="FAILED", msg=f"Object not Created the fields {','.join(invalid_items)} are invalid")
            return PopulatePrizeData.DTOOutput(status="FAILED", msg=f"Object not Created winner field is invalid. Must be 'yes' or ''")
        except Exception as ex:
            return PopulatePrizeData.DTOOutput(status="ERROR", msg=f"Unexpected Error on PopulatePrizeDataUseCase - {ex}")

    def __all_entities_are_valid(self, *args) -> Tuple[bool, list]:
        not_valid = []
        for item in args:
            if not item.is_valid():
                not_valid.append(item.__class__.__name__)

        return (True, []) if not_valid == [] else (False, not_valid)


class DeleteAllDataUseCase(UseCase):
    """This use case is responsible to delete all the items from the database."""
    class DTOOutput:

        def __init__(self, status: str, msg: str, data: dict = dict()):
            self.status = status
            self.msg = msg
            self.data = data
            self.ts = datetime.now()

    def __init__(self, repo: PrizeRepository):
        self.repo = repo

    def execute(self):
        try:
            self.repo.delete_all()
            return DeleteAllDataUseCase.DTOOutput(status="OK", msg="Everything was deleted")
        except Exception as ex:
            return DeleteAllDataUseCase.DTOOutput(status="ERROR", msg="Unexpected error has ocurred when requested to delete all data.")


class ShowHighestAndLowestPrizeIntervals(UseCase):
    """It is responsible to return the interval prize data. """
    class PrizeDTO:
        def __init__(self,
                     producer: str,
                     interval: int,
                     previous_win: int,
                     following_win: int):

            self.procucer = producer
            self.interval = interval
            self.previous_win = previous_win
            self.following_win = following_win

        def dict(self):
            return {
                "producer": self.procucer,
                "interval": self.interval,
                "previousWin": self.previous_win,
                "followingWin": self.following_win
            }

    class DTOOutput:

        def __init__(self, msg: str, status: str, _min: list = list(), _max: list = list()):
            self.status: str = status
            self.msg: str = msg
            self._min: List[ShowHighestAndLowestPrizeIntervals.PrizeDTO] = _min
            self._max: List[ShowHighestAndLowestPrizeIntervals.PrizeDTO] = _max

    def __init__(
            self,
            repo: PrizeRepository):

        self.repo = repo

    def execute(self) -> DTOOutput:
        """It creates the filter, and then get its schema to return the min and max producers lists."""
        try:
            interval_filter = PrizeIntervalFilter(self.repo)
            interval_filter.execute()
            elements = interval_filter.get_schema()
            self._min = elements._min
            self._max = elements._max

            return ShowHighestAndLowestPrizeIntervals.DTOOutput(msg="OK", status="Prize Intervals retrieved successfully", _min=self._min, _max=self._max)
        except Exception as ex:
            return ShowHighestAndLowestPrizeIntervals.DTOOutput(
                msg="ERROR",
                status="An Unexpected error has ocurred when it was retrieving prize intervals data.")
