from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    path('news/', views.news_list, name='news-list'),
    path('news/<str:slug>/', views.news_detail, name='news-detail'),
    path('news/<str:slug>/view/', views.news_view, name='news-view'),
    path('news/<str:slug>/cover/', views.news_cover, name='news-cover'),
    path('news/<str:slug>/images/<int:image_id>/', views.news_image, name='news-image'),
    path('news/content-images/<uuid:token>/', views.news_content_image, name='news-content-image'),
    path('news/<str:slug>/slides/<int:slide_id>/', views.news_slide, name='news-slide'),
    path('recruitment/status/', views.recruitment_status, name='recruitment-status'),
    path('recruitment/applications/', views.recruitment_submit, name='recruitment-submit'),
    path('recruitment/applications/<int:pk>/resume/', views.resume_download, name='resume-download'),
]
