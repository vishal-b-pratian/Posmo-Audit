from django.urls import path, include
from rest_framework import routers
from .views import *

# router = routers.DefaultRouter()
# router.register(r'content', ContentViewSet)
# router.register(r'link', LinksViewSet)

urlpatterns = [
   #  path("", getRoutes, name="get-routes"),
    path("urls/",LinksViewSet),
    path('viewKeywordSummary/<str:channel_id>',View_Keyword_Summary),
    path('ContentUnmapped/<str:channel_id>',Content_Fetch_Unmapped)
] 

    
# urlpatterns = [
#         path('', views.index)
# ]  