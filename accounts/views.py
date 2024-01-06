from itertools import count
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import FollowerList, FollowingList
from django.views.decorators.csrf import csrf_exempt
import json
   
# Create your views here.
User = get_user_model()

def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/explore')
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            # messages.success(request, "Successfully Logged in")
            return HttpResponseRedirect('/explore')
        else:
            messages.warning(request, 'Invalid Credentials Please enter valid details')
            print("Invalid Credentials Please enter valid detail")
            return HttpResponseRedirect('userlogin')
        

    return render(request, 'authentication/login-normal.html')


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/explore')
    if request.method == 'POST':
        firstname = request.POST['fname']
        lastname = request.POST['lname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        #Run checks for input
        # if email == user.email:
        #     messages.warning(request, 'email ID already exist')
        #     return redirect('registration')
        try:
            user = User.objects.create_user(
                username,
                first_name=firstname, 
                last_name = lastname, 
                email=email, 
                password=password
            )
            
            user.save()
            user = authenticate(username=email, password=password)
            login(request, user)

        except Exception as e:
            print(e)
            messages.warning(request, e)
            return HttpResponseRedirect('/accounts/register')    


        # messages.success(request, "Account Created Successfully!")
        return redirect('/explore')

    return render(request, 'authentication/signup-normal.html')

def Handlelogout(request):
    logout(request)
    return HttpResponseRedirect('/')

@csrf_exempt
def follow_user(request):
    """
    function to follow a user it is related to the follwer list and following list of the user
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    try:
        to_follow = User.objects.get(id=body.get('user_id'))
        followinglist = FollowingList.objects.get_or_create(account=request.user)
        res = followinglist[0].follow(to_follow)
        count = FollowerList.objects.get(account=to_follow).followers.count()
        print(count)
    except:
        res = 'user does not exist'
    return JsonResponse({'response': res, 'count': count, 'status':200})
@csrf_exempt
def unfollow_user(request):
    """
    function to unfollow a user
    """   
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode) 
    try:
        to_unfollow = User.objects.get(id=body.get('user_id'))

        followinglist = FollowingList.objects.get_or_create(account=request.user)
        res = followinglist[0].unfollow(to_unfollow)

        count = FollowerList.objects.get(account=to_unfollow).followers.count()
        print(count)
        
    except:
        res = 'user does not exist'    
    return JsonResponse({'response': res, 'count': count, 'status':200})


def edit_profile(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            img = request.FILES.get('p_image')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            print(img)

            edit_user = User.objects.get(id=request.user.id)
            edit_user.first_name = fname
            edit_user.last_name = lname
            edit_user.email = email

            if img is not None: 
                edit_user.profile_image = img
            try:
                edit_user.save()
                messages.success(request, 'profile edited successfully')
            except:
                messages.warning(request, 'Email address already exists')
            return redirect(f'/{request.user.username}')
            
    
    raise Http404