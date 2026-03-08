from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts import views as account_views
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Login at root
    path("", auth_views.LoginView.as_view(template_name="registration/login.html",
                                            redirect_authenticated_user=True,),name="login", ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),

    # Role redirect
    path("home/", account_views.home_router, name="home"),
    path("home/student/", account_views.student_home, name="student_home"),
    path("home/teacher/", account_views.teacher_home, name="teacher_home"),

    # courses list
    path("courses/", include("courses.urls")),

    # registration page
    path("register/", account_views.register, name="register"),

    # search function
    path("search/", account_views.teacher_search, name="teacher_search"),

    path("dm/<int:user_id>/", account_views.dm_chat, name="dm_chat"),
    path("users/", account_views.user_directory, name="user_directory"),

    path("profile/", account_views.profile_view, name="profile"),

    # swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # api endpoints
    path("api/", include("accounts.api_urls")),
    path("api/", include("courses.api_urls")),
    path("api/", include("realtime.api_urls")),
    path("api/", include("social.api_urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)