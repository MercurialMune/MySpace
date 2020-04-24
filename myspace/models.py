from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import django.utils.timezone as now
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from django.db.models.signals import post_save


class tags( models.Model ):
    name = models.CharField( max_length=30 )

    def __str__(self):
        return self.name


# Custom Manager
class PublishedManager( models.Manager ):
    def get_queryset(self):
        return super( PublishedManager, self ).get_queryset().filter( status='published' )


# Category
class Category( models.Model ):
    name = models.CharField( max_length=150, db_index=True )
    slug = models.SlugField( max_length=150, unique=True, db_index=True )
    post_ids = ArrayField( models.IntegerField( default=0 ), default=list )
    created_at = models.DateTimeField( default=now.now, editable=False )
    updated_at = models.DateTimeField( default=now.now )

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super( Category, self ).save( *args, **kwargs )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse( 'post_list_by_category', args=[self.slug] )


# Post Model
class Post( models.Model ):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField( max_length=250 )
    slug = models.SlugField( max_length=250, unique_for_date='publish' )
    author = models.ForeignKey( User, related_name='blog_posts', on_delete=models.CASCADE, )
    body = models.TextField()
    publish = models.DateTimeField( default=timezone.now )
    created = models.DateTimeField( auto_now_add=True )
    updated = models.DateTimeField( auto_now=True )
    status = models.CharField( max_length=10, choices=STATUS_CHOICES, default='draft' )
    article_image = models.ImageField( upload_to='posts/' )
    tags = models.ManyToManyField( tags )
    category = models.ForeignKey( Category, related_name='blog_posts', on_delete=models.CASCADE )

    # The default manager
    objects = models.Manager()

    # Custom made manager
    published = PublishedManager()

    class Meta:
        ordering = ('-publish',)
        index_together = (('id', 'slug'),)

    @classmethod
    def search_by_title(cls, search_term):
        post = cls.objects.filter( title__icontains=search_term )
        return post

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse( 'post_detail_view',
                        args=[self.publish.year, self.publish.strftime( '%m' ), self.publish.strftime( '%d' ),
                              self.slug] )


def save_category_id(sender, instance, **kwargs):
    instance.category.post_ids.append(instance.id)
    instance.category.save()

post_save.connect( save_category_id, sender=Post )


class NewsLetterRecipients( models.Model ):
    name = models.CharField( max_length=30 )
    email = models.EmailField()
