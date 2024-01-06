from unicodedata import category
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from taggit.managers import TaggableManager

# Create your models here.

class Post(models.Model):
    # CONTENT_TYPES = (
    #     ('text', 'text'),
    #     ('image', 'image'),
    #     ('video', 'video')
    # )
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    # content_type = models.CharField(choices=CONTENT_TYPES, max_length=30)

    text = models.TextField()
    image = models.ImageField(upload_to='posts/images', height_field=None, width_field=None, max_length=None, null=True)
    # video = models.FileField(upload_to='posts/videos', null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])])

    category = models.CharField(max_length=200, blank=True, null=True)
    tags = TaggableManager()
    likes=models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes',blank=True)
    views = models.BigIntegerField(default=0)

    date_posted = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f'{self.posted_by.username}\'s Post- {self.title}'

    def likecount(self):
        return self.likes.count()

    def increase_view(self):
        self.views += 1
        self.save()
        return "viewed"


class Comment(models.Model):
	post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	content=models.TextField()
	timestamp=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return 'comment on {} by {}'.format(self.post.title,self.user.username)

class SubComment(models.Model):
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='subcomments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ManyToManyField(Post, verbose_name="bookmarks", blank=True)

    def __str__(self):
        return self.user.username