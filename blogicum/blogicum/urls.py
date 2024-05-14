from django.contrib import admin
from django.urls import path, include

blog_urls = 'blog.urls'
pages_urls = 'pages.urls'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(blog_urls)),
    path('pages/', include(pages_urls)),
]
