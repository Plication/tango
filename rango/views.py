# -- coding: utf-8 --
import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page


def index1(request):
    # request.session.set_test_cookie()
    # # return HttpResponse("<h1>rango say hey!!!</h1><a href='about/'>到about</a>'")
    # # 获得category对象，按likes值倒序排列，取前五
    # category_list = Category.objects.order_by('-likes')[:5]
    # context_dict = {'categories': category_list}
    # return render(request, 'rango/index.html', context_dict)

    # 利用cookie获取网站访问计数
    category_list = Category.objects.all()
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visits = int(request.COOKIES.get('visits', '1'))
    reset_last_visit_time = False
    response = render(request, 'rango/index.html', context_dict)

    if 'last_visit' in request.COOKIES:
        # Yes it does! Get the cookie's value.
        last_visit = request.COOKIES['last_visit']
        # Cast the value to a Python date/time object.
        last_visit_time = datetime.datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.datetime.now() - last_visit_time).days > 0:
            visits = visits + 1
            # ...and flag that the cookie last visit needs to be updated
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so flag that it should be set.
        reset_last_visit_time = True

        context_dict['visits'] = visits

        # Obtain our Response object early so we can add cookie information.
        response = render(request, 'rango/index.html', context_dict)

    if reset_last_visit_time:
        response.set_cookie('last_visit', datetime.datetime.now())
        response.set_cookie('visits', visits)

    # Return response back to the user, updating any cookies that need changed.
    return response


# 基于cookie的session
def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response



def category(request, category_name_slug):
    context_dict = {}

    try:
        # get()获得slug值为category_name_slug的category对象，没有的话会抛出DoseNotExits
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        context_dict['category'] = category

        # 检索出以上category的pages
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages

        context_dict['category_name_slug'] = category_name_slug

    except Category.DoesNotExist as e:
        print(e)

    return render(request, 'rango/category.html', locals())


from rango.forms import CategoryForm, UserForm, UserProfileForm


@login_required
def add_category(request):
    if request.method == 'POST':     # a http POST request
        form = CategoryForm(request.POST)  # 根据POST的数据来创建一个CategoryForm对象

        if form.is_valid():        # 判断表单是否有效，有效则保存categroy对象至数据库
            form.save(commit=True)
            return index(request)    # 返回主页
        else:
            print(form.errors)

    else:
        form = CategoryForm()   # 如果request不是POST，显示填写form页面

    # ☆☆☆  这行错将form写成from，导致模板无法加载参数，页面没有表单
    # return render(request, 'rango/add_category.html', {'from': form})
    return render(request, 'rango/add_category.html', locals())


from rango.forms import PageForm


@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:                 # 取得form数据之后进行相关修改再保存
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)  # 重定向，交给category页面

        else:
            print(form.errors)
    else:
        form = PageForm()

    return render(request, 'rango/add_page.html/', {'cat': cat, 'form': form})


def register(request):

    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():    # If the two forms are valid...
            user = user_form.save()   # Save the user's form data to the database.

            user.set_password(user.password)  # Now we hash the password with the set_password method.
            user.save()             # Once hashed, we can update the user object.

            profile = profile_form.save(commit=False)  # 将post上来的profile_form数据保存,暂时不提交给数据库，以便修改
            # 创建两个模型实例之间的连接.创建新的User模型实例后,
            # 需要用profile.user = user把它关联到UserProfile实例
            profile.user = user

            # 如果用户通过form表单提交了图片，那么放进UserProfile 实例
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            # 检查完毕，将UserProfile 实例保存
            profile.save()
            registered = True  # 将注册状态改为Ture

        # 如果表单不可用，显示错误信息
        else:
            print(user_form.errors, profile_form.errors)
    # 如果不是post请求，那么显示两个空白表单给用户
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', locals())


def user_login(request):

    if request.method == 'POST':   # 如果不存在变量，get方法返回none, request.POST['name']会返回valueError
        username = request.POST.get('username')  # 从用户post的表单中将用户名和密码抽离出来
        password = request.POST.get('password')

        # 通过数据库验证，如果用户名密码存在，authenticate方法返回一个user对象，否则返回none
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active: # 如果用户激活，调用login方法(django.contrib.auth中定义)让用户登陆，返回主页
                login(request, user)   # 如果用户成功登录,那么我们传递给模板的上下文变量会包含一个用户变量
                return HttpResponseRedirect('/rango/')

            else:  # 如果用户已在使用
                return HttpResponse('账户不可用')

        else:   # 如果用户名密码错误，authenticate返回none，在控制台打印出信息
            print('无效的用户名：{0}，密码：{1}'.format(username, password))
            return HttpResponse('用户名或者密码错误')

    # 如果不是post请求，显示登陆页面
    else:
        return render(request, 'rango/login.html', {})


#
@login_required  # 使用该装饰器确保只有已经登陆的用户才能看到这个view
def restricted(request):
    return HttpResponse('您已登陆')


@login_required      # 已登录用户才能注销
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')  # 注销后返回主页










def about(request):

    # return HttpResponse("Rango says here is the about page</h1><a href='/rango/'>Index</a>")
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render(request, 'rango/about.html', locals())