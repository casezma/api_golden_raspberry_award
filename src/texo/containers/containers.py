from dependency_injector import containers, providers
from infra.django_prize_repository import DjangoPrizeRepository


class ApplicationContainer(containers.DeclarativeContainer):
    prize_repository = providers.Factory(DjangoPrizeRepository)
