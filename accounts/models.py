from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from content.models import Bookmark


class UserManager(BaseUserManager):

    def create_user(self, username, first_name, last_name, email, is_creator = False, password=None):
        if not email:
                raise ValueError('Users must have an email address')
		# if not username:
		# 	raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username = username,
            first_name=first_name,
            last_name=last_name,
            is_creator = is_creator
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, first_name, last_name, password):
        user = self.create_user(
            username= username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            password=password,
            # username=self.normalize_email(email),
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def get_profile_image_filepath(self, filename):
	return 'profile/' + str(self.pk) + '/profile_image.png'

def get_default_profile_image():
	return "profile/default_profile.jpg"

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=20, unique=True)
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)

    display_email = models.BooleanField(default=False)

    is_creator = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    profile_visits = models.BigIntegerField(default=0)
    profile_impressions = models.BigIntegerField(default=0)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index('profile/' + str(self.pk) + "/"):]

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    def get_email(self):
        return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def visit_profile(self):
        self.profile_visits += 1
        self.save()
        return True

    def impression(self):
        self.profile_impressions += 1
        self.save()
        return True



# Every user has a followers list 
class FollowerList(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name='follower_owner')
    followers = models.ManyToManyField(User, blank=True, related_name='followers')

    def __str__(self):
        return f'{self.account}: {self.followers.count()}'

# Every user has a following list 
class FollowingList(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name='following_owner')
    followings = models.ManyToManyField(User, blank=True, related_name='followings')

    def __str__(self):
        return f'{self.account}: {self.followings.count()}'

    def follow(self, user):
        """
        function to follow a user if already not followed
        Running this function add the user who followed to the other person's Followers list(database)
        and the User's Following list(database)
        """
        if not self.followings.filter(id=user.id).exists():
            self.followings.add(user)
            fl = FollowerList.objects.get(account=user)
            fl.followers.add(self.account)
            return 'followed successfully'
        else:
            return 'already followed'    

    def unfollow(self, user):
        """
        function to Unfollow a user if already followed
        Running this function removes the user who unfollowed from the other person's Followers list(database)
        and the User's Following list(database)
        """
        if self.followings.filter(id=user.id).exists():
            self.followings.remove(user)
            f1 = FollowerList.objects.get(account=user)
            f1.followers.remove(self.account)
            return 'unfollowed successfully'
        else:
            return 'have not followed yet'    
                




def user_created(sender, instance, created, *args, **kwargs):
    user = instance
    if created:
        try:
            # welcome_email(user.email)
            bookmark = Bookmark(user=user)
            bookmark.save()
        except:
            return

post_save.connect(user_created, sender=settings.AUTH_USER_MODEL)