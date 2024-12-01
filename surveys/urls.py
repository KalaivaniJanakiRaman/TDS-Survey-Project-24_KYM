from django.urls import path
from . import views

urlpatterns = [
    # User Authentication URLs
    path('register/',views.register_view,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),

    # Dashboard URLs
    path('creator/dashboard/',views.creator_dashboard,name='creator_dashboard'),
    path('taker/dashboard/',views.taker_dashboard,name='taker_dashboard'),

    # Survey Creator URLs
    path('surveys/create/',views.create_survey,name='create_survey'),
    path('surveys/edit/<int:survey_id>/',views.edit_survey,name='edit_survey'),
    path('surveys/publish/<int:survey_id>/',views.publish_survey,name='publish_survey'),
    path('surveys/close/<int:survey_id>/',views.close_survey,name='close_survey'),
    path('surveys/manage/',views.manage_surveys,name='manage_surveys'),
    path('surveys/results/<int:survey_id>/',views.view_survey_results,name='view_survey_results'),
    path('surveys/republish/<int:survey_id>/',views.republish_survey,name='republish_survey'),

    # Survey Taker URLs
    path('surveys/available/',views.list_available_surveys,name='list_available_surveys'),
    path('surveys/take/<int:survey_id>/',views.take_survey,name='take_survey'),
    path('surveys/completed/<int:survey_id>/',views.survey_completed,name='survey_completed'),
    path('surveys/take/republished/<int:survey_id>/',views.take_survey_republished,name='take_survey_republished'),

   
    # Home URL  
    path('',views.home,name='home'),  
]