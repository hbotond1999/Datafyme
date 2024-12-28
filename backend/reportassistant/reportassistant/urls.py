"""
URL configuration for reportassistant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from django.views.i18n import set_language

urlpatterns = i18n_patterns(
    path('', RedirectView.as_view(url='/chat/')),
    path("home/", include("home.urls")),
    path("dbloader/", include("dbloader.urls")),
    path("reporter_agent/", include("reporter_agent.urls")),
    path('accounts/', include('accounts.urls')),
    path('db_configurator/', include('db_configurator.urls')),
    path('chat/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path('set_language/', set_language, name='set_language'),
    path('dashboard/', include('dashboard.urls')),
)
