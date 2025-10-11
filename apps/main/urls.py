from django.urls import path
from . import views

app_name='main'

urlpatterns = [
   path('',views.main,name='index'),
   path('slider-list/',views.slider_list_view,name='sliders'),
    path('slider-list2/',views.slider_list_view2,name='sliders2'),
    path('slider-main/',views.slider_main_view,name='main_slider'),
    path('slider-banner/',views.active_banners,name='banner'),
    path('about/',views.about,name='about'),
    path('call/',views.call,name='call'),
    path('faq/',views.faq,name='faq'),

]