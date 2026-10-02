from django.db import models
from django.conf import settings
from django.utils.text import slugify
import os

def blog_cover_upload_path(instance, filename):
    """
    Path format: users/<author_id>/blogs/<blog_id>/cover/cover.<ext>
    """
    author_id = instance.author.id if instance.author and instance.author.id else 'unknown'
    blog_id = f"{instance.id:03d}" if instance.id else "temp"
    ext = filename.split('.')[-1].lower()
    return os.path.join('users', str(author_id), 'blogs', str(blog_id), 'cover', f'cover.{ext}')

def blog_content_upload_path(instance, filename):
    """
    Path format: users/<author_id>/blogs/<blog_id>/content/image-<seq>.<ext>
    """
    author_id = instance.post.author.id if instance.post and instance.post.author and instance.post.author.id else 'unknown'
    blog_id = f"{instance.post.id:03d}" if instance.post and instance.post.id else "temp"
    ext = filename.split('.')[-1].lower()
    
    if instance.pk:
        img_name = f"image-{instance.pk:03d}.{ext}"
    else:
        existing_count = instance.post.content_images.count() + 1 if instance.post and instance.post.pk else 1
        img_name = f"image-{existing_count:03d}.{ext}"
        
    return os.path.join('users', str(author_id), 'blogs', str(blog_id), 'content', img_name)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(blank=True, default='')
    content = models.TextField()
    image = models.ImageField(upload_to=blog_cover_upload_path, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "post"
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class BlogImage(models.Model):
    post = models.ForeignKey(BlogPost, related_name='content_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=blog_content_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Content Image for {self.post.title}"


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"
