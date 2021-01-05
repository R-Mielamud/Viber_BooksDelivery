from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserAPIView, OrderAPIView, RequisitesAPIView, BillAPIView

router = DefaultRouter()
router.register(r"users", UserAPIView)
router.register(r"orders", OrderAPIView)
router.register(r"requisites", RequisitesAPIView)
router.register(r"bills", BillAPIView)

urlpatterns = [
    path("", include(router.urls))
]
