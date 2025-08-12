from django.contrib import admin
from django.urls import path, include  # ajoute include ici

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ajoute cette ligne pour inclure les URLs de ton app "cvparser"
    path('cvparser/', include('cvparser.urls')),
    path('nerapp/', include('nerapp.urls')),
    path('scoring/', include('scoringapp.urls')),
    path('scoring1/', include('scoringapp1.urls')), 

]
