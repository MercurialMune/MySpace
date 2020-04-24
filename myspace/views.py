from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, NewsLetterRecipients, Category
from .forms import NewsLetterForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .email import send_welcome_email
from random import sample


def post_list_by_category(request, category_slug):
    categories = Category.objects.all()
    post = Post.objects.filter( status='published' )
    if category_slug:
        category = get_object_or_404( Category, slug=category_slug )
        post = post.filter( category=category )
    return render( request, 'blog/category/list_by_category.html',
                   {'categories': categories, 'post': post, 'category': category} )


def post_list_view(request, category_slug=None):
    categories = Category.objects.all()
    post = Post.objects.all()
    if category_slug:
        category = get_object_or_404( Category, slug=category_slug )
        post = post.filter( category=category )
    list_objects = Post.published.filter( status='published' )
    recent = Post.objects.order_by( 'publish' )[0:5]

    # make a dictionary like {
    # category1 : ['post', 'post'],
    # category2 : ['post', 'post']
    # }
    categorypostdictionary = {category: list(set([Post.objects.get( id=x ) for x in category.post_ids if len( category.post_ids ) > 2])) for
            category in categories}
    # categorypostdictionary = all categories with their posts in a dictionary
    # set() returns non duplicates

    twopercategory = { x: sample(categorypostdictionary[x], 2) for x in categorypostdictionary if len(list(set(categorypostdictionary[x]))) > 1 }  # remove categories with less than two posts - for uniformity
    # twopercategory = only categories with two or more posts in a dictionary
    # sample() randomizes the queryset per page... effect only seen with a large number of posts per category

    paginator = Paginator( list_objects, 1 )
    page = request.GET.get( 'page' )
    try:
        posts = paginator.page( page )
    except PageNotAnInteger:
        posts = paginator.page( 1 )
    except EmptyPage:
        posts = paginator.page( paginator.num_pages )
    if request.method == 'POST':
        form = NewsLetterForm( request.POST )
        if form.is_valid():
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['email']
            recipient = NewsLetterRecipients( name=name, email=email )
            recipient.save()
            send_welcome_email( name, email )
            HttpResponseRedirect( 'post_list_view' )
    else:
        form = NewsLetterForm()
    return render( request, 'blog/post/list.html',
                   {'posts': posts, "letterForm": form, 'recent': recent, 'categories': categories, 'post': post, 'twopercategory':twopercategory} )


def post_detail_view(request, year, month, day, post, category_slug=None):
    categories = Category.objects.all()
    post = get_object_or_404( Post, slug=post, status='published', publish__year=year, publish__month=month,
                              publish__day=day )
    if category_slug:
        category = get_object_or_404( Category, slug=category_slug )
        post = post.filter( category=category )
    if request.method == 'POST':
        form = NewsLetterForm( request.POST )
        if form.is_valid():
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['email']
            recipient = NewsLetterRecipients( name=name, email=email )
            recipient.save()
            HttpResponseRedirect( 'post_detail_view' )
    else:
        form = NewsLetterForm()
    return render( request, 'blog/post/detail.html', {'post': post, "letterForm": form, 'categories': categories} )


def search_results(request, category_slug=None):
    categories = Category.objects.all()
    post = Post.objects.filter( status='published' )
    if category_slug:
        category = get_object_or_404( Category, slug=category_slug )
        post = post.filter( category=category )
    if 'article' in request.GET and request.GET["article"]:
        search_term = request.GET.get( "article" )
        searched_articles = Post.search_by_title( search_term )
        message = f"{search_term}"

        return render( request, 'blog/post/search.html',
                       {"message": message, "articles": searched_articles, 'categories': categories, 'post': post} )

    else:
        message = "You haven't searched for any term"
        return render( request, 'blog/post/search.html', {"message": message, 'categories': categories, 'post': post} )
