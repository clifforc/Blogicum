from django.urls import path

from .views import UserProfileView, PostCreateView, EditProfileView, \
    PostEditView, PostDeleteView, PostListView, PostDetailView, \
    AddCommentView, EditCommentView, DeleteCommentView, CategoryPostsView

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', PostEditView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/', EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/', DeleteCommentView.as_view(), name='delete_comment'),
    path('category/<slug:category_slug>/', CategoryPostsView.as_view(), name='category_posts'),
    path('profile/<slug:username>/', UserProfileView.as_view(), name='profile'),
    path('profile/<slug:username>/edit/', EditProfileView.as_view(), name='edit_profile'),
]
