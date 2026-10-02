# 🪶 BlogVerse - Production-Ready Django Blog Platform

**BlogVerse** is a modern, feature-rich, and secure blog publishing platform built with **Django**, **Python**, and modern frontend technologies. It features a complete user authentication system, structured user-bound media storage architecture, interactive rich-text publishing editor, category & tag organization, and responsive design.

---

## ✨ Features & Architecture Highlights

### 🛡️ 1. Authentication & Profile Management
- Custom user model (`CustomUser`) with phone numbers and profile pictures.
- Secure registration, authentication, login/logout, profile editing, and password resets.
- User profile images stored in isolated user directories (`media/users/<user_id>/profile/`).

### 📂 2. Structured Media Storage Architecture
Media uploads follow a clean, user-isolated hierarchical folder structure:
```
media/
└── users/
    └── {user_id}/
        ├── profile/
        │   └── profile.webp
        └── blogs/
            └── {blog_id}/
                ├── cover/
                │   └── cover.webp
                └── content/
                    ├── image-001.webp
                    └── image-002.webp
```

### ✍️ 3. Modern Publishing Experience & Editor
- **Real-Time Slugification**: Auto-generates unique, SEO-friendly slugs with live AJAX uniqueness verification (`/blog/check-slug/`).
- **Drag & Drop Cover Image Upload**: Interactive upload zone with live image previews, file info (name & size), replace/remove actions, and 5MB size limit validation.
- **Quill.js Rich-Text Editor**: Formatted content editor supporting Headings, Bold, Italic, Underline, Bullet/Numbered Lists, Blockquotes, Links, Code Blocks, and inline image uploads (`/blog/upload-content-image/`).
- **Short Excerpts**: Summaries for blog cards, search engine previews, and social sharing.
- **Organization**: Category select dropdowns and interactive **Tag Chips** (type & press Enter or `,` to add pills).
- **Post Status & Visibility**: Choose between `Draft` vs `Published` and `Public` vs `Private`.
- **Live Preview Modal**: Slide-over modal showing the exact public layout before publishing.
- **User-Isolated Auto-Save**: Auto-saves drafts to `localStorage` every 15 seconds, isolated strictly to each authenticated user ID.

### 🔒 4. Security & Validation
- Django CSRF protection on all form submissions.
- Strict ownership authorization: users can only view, edit, or delete their own draft/private posts.
- Server-side image validation (MIME type check and 5MB file size limit).
- Safe HTML rendering with sanitization for rich text contents.

---

## 📁 Project Structure

```
blog_website/
├── blog/                      # Blog application
│   ├── migrations/            # Database migrations
│   ├── forms.py               # BlogPostForm with clean validations & Tag inputs
│   ├── models.py              # BlogPost, Category, Tag, BlogImage, Comment models
│   ├── urls.py                # Blog URL routes
│   └── views.py               # View controllers & AJAX helper APIs
├── user_authentication/       # User auth application
│   ├── models.py              # CustomUser model & profile path helpers
│   ├── urls.py                # Auth URL routes
│   └── views.py               # Auth & profile views
├── blog_website/              # Root Django settings & URL configuration
│   ├── settings.py
│   └── urls.py
├── media/                     # Uploaded media files (git-ignored)
├── templates/                 # Global Jinja/Django HTML templates
│   ├── base.html              # Core navigation layout & stylesheets
│   ├── blog/
│   │   ├── blog_detail.html   # Post detail page
│   │   ├── blog_form.html     # Redesigned rich-text post editor
│   │   ├── blog_list.html     # Card grid feed page
│   │   └── search_results.html
│   └── user_authentication/   # Auth templates
├── db.sqlite3                 # SQLite database (Development)
├── manage.py
└── README.md
```

---

## ⚙️ Tech Stack & Requirements

- **Backend**: Python 3.10+, Django 5.x
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Typography & Icons**: Inter & Outfit fonts (Google Fonts), FontAwesome 6.5
- **Rich Text Editor**: Quill.js 1.3.6

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd blog_website
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install django pillow
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Initial Categories (Optional)
```bash
python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_website.settings'); django.setup(); from blog.models import Category; [Category.objects.get_or_create(name=c) for c in ['Technology', 'Programming', 'Design', 'Lifestyle', 'Business', 'General']]"
```

---

## 🔗 Main URL Routes

| URL Pattern | View Function | Description |
| :--- | :--- | :--- |
| `/` | `home` | Main feed / landing page |
| `/login/`, `/register/`, `/logout/` | Auth views | Authentication management |
| `/blog/bloglist/` | `blog_list` | Recent stories feed |
| `/blog/post/new/` | `blog_create` | Create a new blog post |
| `/blog/post/<int:pk>/` | `blog_detail` | View post by ID |
| `/blog/post/<slug:slug>/` | `blog_detail` | View post by URL slug |
| `/blog/post/<int:pk>/edit/` | `blog_update` | Edit existing blog post |
| `/blog/upload-content-image/` | `upload_content_image` | AJAX inline image upload API |
| `/blog/check-slug/` | `check_slug_unique` | AJAX slug uniqueness checker API |
