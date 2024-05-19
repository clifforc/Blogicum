from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.utils import timezone
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from django.urls import reverse_lazy, reverse

from .forms import PostForm, CommentForm, ProfileForm
from .models import Post, Category, User, Comment


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.POSTS_BY_PAGE
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.published()


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self, queryset=None):
        published_posts = Post.objects.published()
        user_posts = Post.objects.filter(author=self.request.user)
        posts = published_posts | user_posts
        return get_object_or_404(posts, pk=self.kwargs['post_id'])


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(PostMixin, UserPassesTestMixin, UpdateView):

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post_id = self.kwargs.get(self.pk_url_kwarg)
        return redirect('blog:post_detail', post_id=post_id)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.id})


class PostDeleteView(PostMixin, UserPassesTestMixin, DeleteView):

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_BY_PAGE
    slug_url_kwarg = 'category_slug'

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs[self.slug_url_kwarg])
        return Post.objects.filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category, slug=self.kwargs[self.slug_url_kwarg])
        if not category.is_published:
            raise Http404
        context['category'] = category
        return context


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = settings.POSTS_BY_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context

    def get_queryset(self):
        user_profile = get_object_or_404(
            User, username=self.kwargs['username'])
        queryset = Post.objects.filter(author=user_profile)

        if self.request.user == user_profile:
            return queryset.annotate(
                comment_count=Count('comments')).order_by('-pub_date')
        else:
            today = timezone.now()
            return queryset.filter(
                pub_date__lte=today
            ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comments.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post,
                                               pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


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


class CommentUpdateView(UserPassesTestMixin, CommentMixin, UpdateView):
    form_class = CommentForm

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author


class CommentDeleteView(UserPassesTestMixin, CommentMixin, DeleteView):
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author
