from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Post, Comment


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, id=kwargs['comment_id'])
        if instance.author != request.user:
            raise PermissionError
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})
