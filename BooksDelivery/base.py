from django.http import HttpResponse
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from helpers.csv import CSV

class BaseCSVModel:
    @classmethod
    def csv_dto(cls, instance):
        return instance

    @classmethod
    def arrays_newline(cls):
        return False

    @classmethod
    def csv(cls):
        instances = tuple(map(lambda i: cls.csv_dto(i), cls.objects.all()))
        exporter = CSV(cls.csv_schema(), instances, arrays_newline=cls.arrays_newline())

        return exporter.generate()

class BaseCSVExportAPI(ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        return HttpResponse(self.model.csv())

def csv_map_instances_ids(instances):
    return tuple(map(lambda i: str(i.id), instances))

CSV_CHANGE = {
    "Change": False,
}
