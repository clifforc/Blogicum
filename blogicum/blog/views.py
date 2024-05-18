from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from django.urls import reverse_lazy

from .forms import PostForm, CommentForm
from .models import Post, Category, User, Comment


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.POSTS_BY_PAGE

    def get_queryset(self):
        return Post.objects.published()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self, *args, **kwargs):
        post = super().get_object(*args, **kwargs)
        if post.author != self.request.user:
            return get_object_or_404(
                Post.objects.all(),
                pk=self.kwargs['pk']
            )
        return post


class CategoryPostsView(DetailView):
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    paginate_by = settings.POSTS_BY_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['page_obj'] = Post.objects.filter(category=category, is_published=True).order_by('created_at')
        return context


class UserProfileView(ListView):
    model = User
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
        return Post.objects.filter(
            author__username=self.kwargs['username']
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class EditProfileView(OnlyAuthorMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user != instance:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:edit_profile',
                            kwargs={'username': self.request.user.username})


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.id})


class PostEditView(PostMixin, OnlyAuthorMixin, UpdateView):

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.id})


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PostForm(instance=self.object)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse_lazy('blog:index')


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comments.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post,
                                               pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, id=kwargs['comment_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class EditCommentView(OnlyAuthorMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class DeleteCommentView(OnlyAuthorMixin, CommentMixin, DeleteView):
    ...

