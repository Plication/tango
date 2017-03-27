import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango.settings')

import django
django.setup()

from rango.models import Category, Page


def add_category(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]  # 该方法返回(object, created)元组
    return c


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(
        category=cat, title=title, url=url, views=views)[0]
    return p


def populate():
    python_cate = add_category('Python', views=128, likes=64)

    add_page(python_cate,
             title='Python官方教程',
             url='http://docs.python.org/2/tutorial')

    add_page(python_cate,
             title='怎样像计算机科学家一样思考',
             url='http:www.greenteapress.com/thinkpython/')

    add_page(python_cate,
             title='10分钟学会Python',
             url='http://korokithakis.net/tutorials/python/')

    django_cat = add_category('Django', views=66, likes=32)

    add_page(django_cat,
             title='Django Rocks',
             url='http://www.djangorocks.com')

    add_page(django_cat,
             title='How to Tango with Django',
             url='http://www.tangowithdjango.com')

    add_page(django_cat,
             title='Django Documentation 1.10',
             url='https://docs.djangoproject.com/en/1.10/')

    frame_cat = add_category('Others')

    add_page(frame_cat,
             title='PEP8编码规范',
             url='https://www.douban.com/note/134971609/')

    add_page(frame_cat,
             title='HTML/CSS教程',
             url='http://www.w3school.com.cn/h.asp')

    add_page(frame_cat,
             title='Bootstrap起步',
             url='http://v3.bootcss.com/getting-started/')

    add_page(frame_cat,
             title='Pycharm教程',
             url='http://blog.csdn.net/u013088062/article/details/50388329')

    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print('---{0}---{1}---'.format(c, p))


if __name__ == '__main__':
    print('开始脚本添加...')
    populate()