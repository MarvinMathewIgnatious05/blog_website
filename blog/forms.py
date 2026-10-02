from django import forms
from .models import BlogPost, Category, Tag, Comment
from django.utils.text import slugify
import re

class BlogPostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Add tags separated by commas...',
            'id': 'tags-input-hidden'
        })
    )

    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'excerpt', 'content', 'image', 'category', 'visibility', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'How I Built My First Django Application',
                'maxlength': '255',
                'required': True,
                'id': 'post-title-input'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'how-i-built-my-first-django-application',
                'id': 'post-slug-input'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'A short summary of your article used in cards, previews, and search results...',
                'maxlength': '300',
                'id': 'post-excerpt-input'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control d-none',
                'rows': 12,
                'id': 'post-content-textarea'
            }),
            'image': forms.FileInput(attrs={
                'class': 'file-input-hidden',
                'accept': 'image/*',
                'id': 'cover-image-input'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'post-category-select'
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'post-visibility-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'post-status-select'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').strip().lower()
        if slug:
            if not re.match(r'^[a-z0-9-]+$', slug):
                raise forms.ValidationError("Slug can only contain lowercase letters, numbers, and hyphens.")
            qs = BlogPost.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("This slug is already used by another post. Please choose a unique slug.")
        return slug

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if hasattr(image, 'size') and image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Cover image file size cannot exceed 5MB.")
            if hasattr(image, 'content_type') and not image.content_type.startswith('image/'):
                raise forms.ValidationError("Uploaded file must be a valid image format (JPEG, PNG, WEBP, GIF).")
        return image

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a respectful comment...',
                'required': True
            })
        }
