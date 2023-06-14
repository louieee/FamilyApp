from rest_framework.viewsets import ModelViewSet

from core.models import Pipeline


class PipelineAPI(ModelViewSet):
    queryset = Pipeline.objects.all()
