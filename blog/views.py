from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BlogPost, Comment
from .forms import BlogPostForm, CommentForm
from django.db.models import Q

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog_list.html', {'posts': posts})

def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    comments = post.comments.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('blog:blog_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog:blog_list')
    else:
        form = BlogPostForm()

    return render(request, 'blog_form.html', {'form': form})

@login_required
def blog_update(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk, author=request.user)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        # print("////",form)
        if form.is_valid():
            form.save()
            return redirect('blog:blog_detail', pk=pk)
    else:
        form = BlogPostForm(instance=blog)

    return render(request, 'blog_form.html', {'form': form})

@login_required
def blog_delete(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk, author=request.user)
    blog.delete()
    return redirect('blog:blog_list')

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('blog:blog_detail', pk=post_pk)

@login_required
def view_comment(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    comments = Comment.objects.filter(post=post).order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('blog:view_comment', pk=pk)
    else:
        form = CommentForm()

    return render(request, 'vew_comment.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    return render(request, 'search_results.html', {'results': results, 'query': query})