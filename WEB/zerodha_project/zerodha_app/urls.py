from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('stock-graph/', views.generate_stock_graph, name='stock_graph'),
]