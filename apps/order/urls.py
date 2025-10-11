from django.urls import path
from .views import toggle_favorite,ApplyCopon,CheckOutOrder,CreateOrderView,add_to_cart,cart_count,show_item,remove_from_cart,get_cart_org

app_name='order'

urlpatterns = [
   path("add/<int:file_id>/", add_to_cart, name="add_to_cart"),
   path("count/", cart_count, name="cart_count"),
   path('get-card/',show_item,name='get_card'),
   path("remove/<int:file_id>/", remove_from_cart, name="remove_from_cart"),
   path("cart/", get_cart_org, name="cart"),
   path('createOrder/',CreateOrderView.as_view(),name='createOrder'),
   path('checkoutorder/<int:order_id>/',CheckOutOrder.as_view(),name='CheckOrder'),
   path('apply_copon/<int:order_id>/',ApplyCopon.as_view(),name='apply_copon'),
   path('toggle-favorite/<int:file_id>/', toggle_favorite, name='toggle_favorite'),


]