# -- coding: utf-8 --
from django import forms
from django.contrib.auth.models import User

from rango.models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):   # 加入参数为了控制用户输入
    name = forms.CharField(max_length=128,
                           help_text="添加目录：",
                           error_messages={'required': '用户名不能为空'})
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Category
        fields = ('name',)  # 用fields或者exclude来定义表单需要展示的字段


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text='请输入标题')
    url = forms.URLField(max_length=200, help_text='请输入地址')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        # we can either exclude the category field from the form,
        exclude = ('category',)
        # or specify the fields to include (i.e. not include the category field)
        # fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If url is not empty and doesn't start with 'http://', prepend 'http://'.
        if url and url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data


#  用户
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # 添加表单的属性

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')












