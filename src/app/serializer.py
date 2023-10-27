from rest_framework import serializers


class PrizeInfoSerializer(serializers.Serializer):
    producer = serializers.CharField()
    interval = serializers.IntegerField()
    previousWin = serializers.IntegerField()
    followingWin = serializers.IntegerField()


class PrizeIntervalSerializer(serializers.Serializer):
    min = serializers.ListField(child=PrizeInfoSerializer())
    max = serializers.ListField(child=PrizeInfoSerializer())
