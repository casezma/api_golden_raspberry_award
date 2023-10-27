from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.serializer import PrizeIntervalSerializer
from usecases.usecases import (
    ShowHighestAndLowestPrizeIntervals as ShowHighestAndLowestPrizeIntervalsUseCase)
from infra.django_prize_repository import DjangoPrizeRepository
from dependency_injector.wiring import inject, Provide
from texo.containers import ApplicationContainer


@api_view(["GET"])
@inject
def get_prize_interval_summary(
        request,
        repository: DjangoPrizeRepository = Provide[ApplicationContainer.prize_repository]):
    """
    This view gets two lists (min and max) from the usecase called ShowHighestAndLowestPrizeIntervalsUseCase.
    As the DTO Output from this usecase has a presenter method called dict, which returns the data for the specs 
    response format, those lists are iterated to pass this dict format to PrizeIntervalSerializer, which will
    return the right response.

    If the min and the max lists are empty, it indicates that the database is empty, responding and internal error 
    and requesting to user fix the problem and try again later.

    In case of an unexpected exception happen, there is a try-except which will get this unknown exception and then
    it will return to use a Unexpected error with internal error status code as well.

    There is a injection of the DjangoPrizeRepository from the dependency injector container, which is done by
    the @inject decorator.
    """

    try:
        elements: ShowHighestAndLowestPrizeIntervalsUseCase.DTOOutput = ShowHighestAndLowestPrizeIntervalsUseCase(
            repository).execute()
        prize_info_serializers = PrizeIntervalSerializer(data={
            "min": [x.dict() for x in elements._min],
            "max": [x.dict() for x in elements._max]
        })
        if prize_info_serializers.is_valid():
            if not prize_info_serializers['min'].value and not prize_info_serializers['max'].value:
                return Response(data={
                    "error": "Database is empty. Your CSV file must be empty or with some issues, fix it and run the application later."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(data=prize_info_serializers.data)
    except Exception:
        return Response(data={"error": "Unexpected error ocurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
