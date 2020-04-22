from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post,NewsLetterRecipients,Category
from .forms import NewsLetterForm
from django.http import HttpResponse, Http404,HttpResponseRedirect
from .email import send_welcome_email


def post_list_by_category(request , category_slug):
    categories = Category.objects.all()
    post = Post.objects.filter(status='published')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        post = post.filter(category=category)
    return render(request, 'blog/category/list_by_category.html', {'categories': categories, 'post': post, 'category': category})


def post_list_view(request, category_slug=None):
    categories = Category.objects.all()
    post = Post.objects.filter(status='published')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        post = post.filter(category=category)
    list_objects = Post.published.all()
    recent = Post.objects.order_by('publish')[0:5]
    paginator = Paginator(list_objects, 1)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['email']
            recipient = NewsLetterRecipients(name = name,email =email)
            recipient.save()
            send_welcome_email(name,email)
            HttpResponseRedirect('post_list_view')
    else:
        form = NewsLetterForm()
    return render(request, 'blog/post/list.html', {'posts': posts,"letterForm":form, 'recent': recent, 'categories': categories, 'post': post})

def post_detail_view(request, year, month, day, post, category_slug=None):
    categories = Category.objects.all()
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        post = post.filter(category=category)
    if request.method == 'POST':
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['email']
            recipient = NewsLetterRecipients(name = name,email =email)
            recipient.save()
            HttpResponseRedirect('post_detail_view')
    else:
        form = NewsLetterForm()
    return render(request, 'blog/post/detail.html', {'post': post,"letterForm":form, 'categories': categories})

def search_results(request, category_slug=None):
    categories = Category.objects.all()
    post = Post.objects.filter(status='published')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        post = post.filter(category=category)
    if 'article' in request.GET and request.GET["article"]:
        search_term = request.GET.get("article")
        searched_articles = Post.search_by_title(search_term)
        message = f"{search_term}"

        return render(request, 'blog/post/search.html',{"message":message,"articles": searched_articles, 'categories': categories, 'post': post})

    else:
        message = "You haven't searched for any term"
        return render(request, 'blog/post/search.html',{"message":message, 'categories': categories, 'post': post})