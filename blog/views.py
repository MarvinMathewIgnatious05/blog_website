from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils.text import slugify
from .models import BlogPost, Category, Tag, BlogImage, Comment
from .forms import BlogPostForm, CommentForm

def blog_list(request):
    if request.user.is_authenticated:
        posts = BlogPost.objects.select_related('author', 'category').prefetch_related('tags').filter(
            Q(status='published', visibility='public') | Q(author=request.user)
        ).order_by('-created_at')
    else:
        posts = BlogPost.objects.select_related('author', 'category').prefetch_related('tags').filter(
            status='published', visibility='public'
        ).order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, pk=None, slug=None):
    if slug:
        post = get_object_or_404(BlogPost.objects.select_related('author', 'category').prefetch_related('tags'), slug=slug)
    else:
        post = get_object_or_404(BlogPost.objects.select_related('author', 'category').prefetch_related('tags'), pk=pk)

    # Permission check for drafts or private posts
    if post.status == 'draft' or post.visibility == 'private':
        if not request.user.is_authenticated or (post.author != request.user and not request.user.is_staff):
            messages.error(request, "You do not have permission to view this private post or draft.")
            return redirect('blog:blog_list')

    comments = post.comments.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to add a comment.')
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('blog:blog_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

@login_required(login_url='login')
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user

            # Action routing (Draft vs Publish)
            action = request.POST.get('action')
            if action == 'draft':
                blog.status = 'draft'
            elif action == 'publish':
                blog.status = 'published'

            # 2-stage save for media path ordering
            image_file = blog.image
            if image_file:
                blog.image = None
            blog.save()  # Generates blog.id

            if image_file:
                blog.image = image_file
                blog.save()  # Saves file with author_id and blog_id in path

            # Tags processing
            tags_str = request.POST.get('tags_data', '') or form.cleaned_data.get('tags_input', '')
            if tags_str:
                tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
                blog.tags.clear()
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
                    blog.tags.add(tag_obj)

            if blog.status == 'draft':
                messages.info(request, 'Draft saved successfully!')
            else:
                messages.success(request, 'Blog post published successfully!')
            return redirect('blog:blog_detail', pk=blog.pk)
        else:
            messages.error(request, 'Please review and fix the validation errors in the form.')
    else:
        form = BlogPostForm()

    categories = Category.objects.all()
    return render(request, 'blog/blog_form.html', {
        'form': form,
        'title': 'Create New Post',
        'categories': categories,
        'is_edit': False
    })

@login_required(login_url='login')
def blog_update(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    
    if blog.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('blog:blog_detail', pk=pk)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)

            # Support image removal if user clicked 'Remove Image'
            if request.POST.get('remove_cover_image') == 'true':
                blog.image = None

            action = request.POST.get('action')
            if action == 'draft' or action == 'unpublish':
                blog.status = 'draft'
            elif action == 'publish' or action == 'save':
                blog.status = 'published'

            blog.save()

            # Update tags
            tags_str = request.POST.get('tags_data', '') or form.cleaned_data.get('tags_input', '')
            if tags_str:
                tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
                blog.tags.clear()
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
                    blog.tags.add(tag_obj)
            else:
                blog.tags.clear()

            messages.success(request, 'Post updated successfully!')
            return redirect('blog:blog_detail', pk=pk)
        else:
            messages.error(request, 'Please review and fix the validation errors in the form.')
    else:
        initial_tags = ", ".join([t.name for t in blog.tags.all()])
        form = BlogPostForm(instance=blog, initial={'tags_input': initial_tags})

    categories = Category.objects.all()
    return render(request, 'blog/blog_form.html', {
        'form': form,
        'title': 'Edit Post',
        'blog': blog,
        'categories': categories,
        'is_edit': True,
        'current_tags': [t.name for t in blog.tags.all()]
    })

@login_required(login_url='login')
def upload_content_image(request):
    """
    Handles image uploads inserted inside the rich text content editor.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        post_id = request.POST.get('post_id')

        blog = None
        if post_id and post_id.isdigit():
            blog = BlogPost.objects.filter(pk=int(post_id), author=request.user).first()

        if not blog:
            blog = BlogPost.objects.create(
                author=request.user,
                title="Untitled Draft",
                content="",
                status="draft"
            )

        blog_image = BlogImage.objects.create(post=blog, image=image_file)
        return JsonResponse({
            'success': True,
            'url': blog_image.image.url,
            'post_id': blog.pk
        })
    return JsonResponse({'success': False, 'error': 'No image file uploaded.'}, status=400)

@login_required(login_url='login')
def check_slug_unique(request):
    """
    AJAX helper to check slug uniqueness in real time.
    """
    slug = request.GET.get('slug', '').strip().lower()
    post_id = request.GET.get('post_id')
    
    qs = BlogPost.objects.filter(slug=slug)
    if post_id and post_id.isdigit():
        qs = qs.exclude(pk=int(post_id))
        
    is_unique = not qs.exists()
    return JsonResponse({'slug': slug, 'is_unique': is_unique})

@login_required(login_url='login')
def blog_delete(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    
    if blog.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('blog:blog_detail', pk=pk)
        
    blog.delete()
    messages.success(request, 'Post deleted successfully.')
    return redirect('blog:blog_list')

@login_required(login_url='login')
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    
    if comment.user != request.user and comment.post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('blog:blog_detail', pk=post_pk)
        
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('blog:blog_detail', pk=post_pk)

@login_required(login_url='login')
def view_comment(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    comments = Comment.objects.filter(post=post).select_related('user').order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('blog:view_comment', pk=pk)
    else:
        form = CommentForm()

    return render(request, 'blog/view_comment.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

def search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = BlogPost.objects.select_related('author', 'category').prefetch_related('tags').filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        ).filter(status='published', visibility='public').order_by('-created_at')

    return render(request, 'blog/search_results.html', {'results': results, 'query': query})