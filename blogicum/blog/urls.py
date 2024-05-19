from django.urls import path

from .views import PostListView, PostDetailView, PostCreateView, \
    PostUpdateView, PostDeleteView, CommentCreateView, CommentUpdateView, \
    CommentDeleteView, CategoryDetailView, ProfileListView, \
    ProfileUpdateView

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='delete_post'),

    path('posts/<int:pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/', CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/', CommentDeleteView.as_view(), name='delete_comment'),

    path('category/<slug:category_slug>/', CategoryDetailView.as_view(), name='category_posts'),

    path('profile/<slug:username>/', ProfileListView.as_view(), name='profile'),
    path('edit_profile/', ProfileUpdateView.as_view(), name='edit_profile'),
]
