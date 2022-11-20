from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm


POSTS_IN_PAGE: int = 10
TITTLE: int = 30


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = author.posts.count()
    paginator = Paginator(posts, POSTS_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'count': count,
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    pub_date = post.pub_date
    post_title = post.text[:TITTLE]
    author = post.author
    author_posts = author.posts.all().count()
    context = {
        'post': post,
        'post_title': post_title,
        'pub_date': pub_date,
        'author': author,
        'author_posts': author_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required(login_url="users:login")
def post_create(request):
    """Добавления поста."""

    template = "posts/post_create.html"

    form = PostForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect("posts:profile", request.user)

    return render(request, template, {"form": form})


@login_required(login_url="users:login")
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)
