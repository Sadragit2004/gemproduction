from django.urls import path
from . import views

app_name='panel'

urlpatterns = [

   path('panel',views.dashboard_view,name='panel'),
   path('order-list/',views.user_orders_list_view,name='order-list'),
   path('order-detail/<int:order_id>/',views.order_detail_view,name='order-detail'),
   path('favorites/', views.favorites_list, name='favorites_list'),
   path('favorites/delete/<int:favorite_id>/', views.delete_favorite, name='delete_favorite'),
   path('favorites/delete-all/', views.delete_all_favorites, name='delete_all_favorites'),
   path('editprofile/',views.Edit_profile.as_view(),name='edit_profile')

]