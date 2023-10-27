from typing import List
from app.models import Producer, Studios, Movie, Prize
from repository.prize_repository import MovieInputDTO, PrizeOutputDTO, PrizeRepository


class DjangoPrizeRepository(PrizeRepository):

    def create(self, year: int, movie: MovieInputDTO, winner: bool):
        """This is responsible to create all the instances for the Django
        models. If there are not any of the following models instantes in
        database it will create."""

        producer, _ = Producer.objects.get_or_create(
            name=movie.producer_name,
            defaults={"name": movie.producer_name})

        studios, _ = Studios.objects.get_or_create(
            name=movie.studio_name,
            defaults={"name": movie.studio_name})

        movie, _ = Movie.objects.get_or_create(
            name=movie.name,
            studios=studios,
            producer=producer,
            defaults={
                "name": movie.name,
                "studios": studios,
                "producer": producer}
        )

        Prize.objects.get_or_create(year=year, movie=movie, winner=winner,
                                    defaults={
                                        "year": year, "movie": movie, "winner": winner
                                    })

    def all_winners(self) -> List[PrizeOutputDTO]:

        items = []
        for item in Prize.objects.filter(winner=True):
            prize_output_dto = PrizeOutputDTO(
                _id=item.id,
                year=item.year,
                name=item.movie.name,
                producer=item.movie.producer.name,
                studios=item.movie.studios.name,
                winner=item.winner)
            items.append(prize_output_dto)
        return items

    def delete_all(self):

        Producer.objects.all().delete()
        Studios.objects.all().delete()
        Movie.objects.all().delete()
        Prize.objects.all().delete()
