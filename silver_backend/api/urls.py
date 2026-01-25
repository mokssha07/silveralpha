from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.status, name='status'),
    path('globe/nodes/', views.globe_nodes, name='globe_nodes'),
    path('node/<int:node_id>/', views.node_detail, name='node_detail'),
    path('dashboard/summary/', views.dashboard_summary, name='dashboard_summary'),
    path('dashboard/chart/', views.chart_data, name='chart_data'),
]
