
from cgitb import text
from operator import le, length_hint
from turtle import title
from django.shortcuts import render,redirect,get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.test import tag

from accounts.views import User
from .models import Bookmark, Post, Comment
from accounts.models import FollowerList, FollowingList
from taggit.models import Tag, TaggedItem
from .forms import PostForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

# Create your views here.

def homepage(request):
    return render(request, 'homepage.html')

def explore(request):
    tags = Tag.objects.all()
    tags = list(reversed(tags))
    tags = tags[:8]
    # tags = Tag.objects.all().most_common()[:3]
    # tags = Post.objects.all().tags.most_common()[:4]
    posts = Post.objects.all()
    posts = list(reversed(posts))
    for post in posts:
        print(post.tags.name)



    # form = PostForm(request.POST)
    # if request.method == 'POST':
       
    #     # if form.is_valid():
    #     newpost = form.save(commit=False)
    #     newpost.posted_by = request.user
    #     newpost.save()
    #     # Without this next line the tags won't be saved.
    #     form.save_m2m()

    return render(request, 'explore.html', {"tags": tags, "posts": posts})

@login_required
def addPost(request):
    if request.method != 'POST':
        raise Http404
    
    # form = PostForm(request.POST)
    # # if form.is_valid():
    # try:
    #     newpost = form.save(commit=False)
    #     newpost.posted_by = request.user
    #     newpost.save()
    #     # Without this next line the tags won't be saved.
    #     form.save_m2m()
    # except Exception as e:
    #     print(e)
    # # else:
    # #     print("something went wrong")


    new_post = Post(
        posted_by = request.user,
        title = request.POST.get('title'),
        text = request.POST.get('text'),
        image = request.FILES.get('image'),
    )

    new_post.save()

    tags = request.POST.get('tags')
    tags.replace(" ", "")
    tag_list = tags.split(",")
    for tag in tag_list:
        new_post.tags.add(tag)

    new_post.save()
    return redirect('explore')

def viewPost(request, id):
    try:
        post = Post.objects.get(id=id)
        post.increase_view()
        creator = post.posted_by
        comments = Comment.objects.filter(post=post)
        post_tags = post.tags.all()
        tags = []
        for t in post_tags:
            tags.append(t.name)
        print(tags)
        related_posts = Post.objects.filter(tags__name__in=tags).distinct().exclude(id=id)

        print(related_posts)

        if post.likes.filter(id=request.user.id).exists():
            liked = True
        else:
            liked = False
        bm = False
        if request.user.is_authenticated:
            bookmark = Bookmark.objects.get(user=request.user)
            if bookmark.post.filter(id=post.id).exists():
                bm = True
            else:
                bm = False


    except Exception as e:
        print(e)
        raise Http404
    if post:
        contexts = {
            "post": post, 
            "liked": liked,
            "bookmarked": bm,
            "creator": creator, 
            "comments": reversed(comments),
            "comment_count": len(comments),
            "related_posts": related_posts
        }
        return render(request, 'view_post.html', contexts)

@login_required
def add_comment(request):
    if request.method != 'POST':
        return HttpResponse('forbidden')
    user = request.user

    post_id = request.POST.get('post_id')
    try:
        post = Post.objects.get(id=post_id)
    except:
        raise Http404    
    comment = request.POST.get('comment')
    
    comm = Comment(
        post=post,
        user=user,
        content=comment
    )
    comm.save()
    return redirect('view_post', id=post_id)


@csrf_exempt
def postlike(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            post_id = body.get('post_id')
            post = Post.objects.get(id=post_id)
        except Exception as e:
            print(e)
            raise Http404
        is_liked=False
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            is_liked=False
        else:
            post.likes.add(request.user)
            # notify.send(request.user, recipient=post.author, actor=request.user,
            #     verb='liked your post', nf_type='liked_post')
            is_liked=True

        return JsonResponse({'is_liked': is_liked, 'count': post.likecount()})

@csrf_exempt
def toggle_bookmark(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            post_id = body.get('post_id')
            post = Post.objects.get(id=post_id)
        except Exception as e:
            print(e)
            raise Http404
        bookmark = Bookmark.objects.get(user=request.user)
        bm = False
        if bookmark.post.filter(id=post.id).exists():
            bookmark.post.remove(post)
            bm=False
        else:
            bookmark.post.add(post)
            bm=True
        return JsonResponse({"bookmarked": bm})

def profile(request, uname):
    user = get_object_or_404(User, username=uname)
    posts = Post.objects.filter(posted_by=user)
    user_followers = FollowerList.objects.get_or_create(account=user)   
    user_followings = FollowingList.objects.get_or_create(account=user)
    current_user = False
    if user == request.user:
        current_user = True
    is_followed = False
    if not current_user:
        if user_followers[0].followers.filter(id=request.user.id).exists():
            is_followed = True
    print(is_followed)

    user.visit_profile()
    
    context = {
        'profile': user,
        'posts': posts,
        'no_of_posts': len(posts),
        'followers': user_followers[0].followers.count(),
        'followings': user_followings[0].followings.count(),
        'is_followed': is_followed,
        'current_user': current_user

    }
    return render(request, 'profile-page.html', context)

@login_required
def view_analytics(request, uname):
    if request.user.username != uname:
        raise Http404

    _posts = Post.objects.filter(posted_by=request.user)
    followers = FollowerList.objects.get_or_create(account=request.user)
    following = FollowingList.objects.get_or_create(account=request.user)
    total_likes = 0

    user_posts = []
    for p in _posts:
        con = {}
        con["post"] = p
        comments = Comment.objects.filter(post=p)
        con["comments"] = len(comments)
        total_likes += p.likecount()
        user_posts.append(con)      
        
    
    context = {
        "user_posts": user_posts,
        "followers": followers[0].followers.count(),
        "following": following[0].followings.count(),
        'no_of_posts': len(user_posts),
        "total_likes": total_likes
    }
    return render(request, 'analytics-page.html', context)

@login_required
def view_bookmarks(request, uname):
    if request.user.username != uname:
        raise Http404
    my_bookmarks = Bookmark.objects.get_or_create(user=request.user)
    my_bookmarks = my_bookmarks[0].post.all()
    return render(request, 'view_bookmarks.html', {'bookmarks': my_bookmarks, 'lenb': len(my_bookmarks)})

def get_tag(request, tag):
    posts = Post.objects.filter(tags__name__in=[tag]).distinct()
    print(posts)
    return render(request, 'tags_filter.html', {'posts': posts, 'tag': tag})


def search(request):
    query = request.GET.get("q")
    search_results = Post.objects.filter(title__icontains=query)
    length = len(search_results)
    return render(request, 'search-page.html', {"posts": search_results, 'length': length})