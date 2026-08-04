from django.db import models

class AdmissionApplication(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.course}"

class ContactInquiry(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    course_interest = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending') # pending, viewed
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.full_name} - {self.course_interest}"

class Achievement(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='achievements/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/')
    date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.title

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/')
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='blogs/thumbnails/', null=True, blank=True, help_text="Image shown on the blog list page.")
    image = models.ImageField(upload_to='blogs/', null=True, blank=True, help_text="Large image shown inside the blog detail page.")
    content_p1 = models.TextField(null=True, blank=True, help_text="First paragraph of the blog.")
    quote = models.TextField(null=True, blank=True, help_text="A highlighted quote in the blog.")
    content_p2 = models.TextField(null=True, blank=True, help_text="Second paragraph of the blog.")
    date = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, help_text="e.g., 'Student, Crash course, Tanur'")
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class HomePageVideo(models.Model):
    youtube_url = models.URLField(help_text="Full YouTube URL or embed link")
    updated_at = models.DateTimeField(auto_now=True)
    def get_embed_url(self):
        import re
        match = re.search(r'(?:v=|youtu\.be/|embed/)([^&?]+)', self.youtube_url)
        if match:
            return f"https://www.youtube-nocookie.com/embed/{match.group(1)}?rel=0"
        return self.youtube_url
    def __str__(self):
        return self.youtube_url

class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, help_text="e.g., 'HOD', 'Mentor'")
    image = models.ImageField(upload_to='team/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Brochure(models.Model):
    file = models.FileField(upload_to='brochures/', help_text="Upload the PDF brochure")
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Brochure updated on {self.updated_at}"

class Notification(models.Model):
    text = models.CharField(max_length=500)
    link = models.URLField(blank=True, null=True, help_text="Optional link for the notification")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.text
