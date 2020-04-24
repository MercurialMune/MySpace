from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import django.utils.timezone as now
from django.contrib.postgres.fields import ArrayField
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
    post_ids = ArrayField( models.IntegerField( default=0 ), default=list ) # add a post_id field to save ids of all posts under that category
    created_at = models.DateTimeField( default=now.now, editable=False ) # its better to use default= than auto_add (in my own opinion). Make it uneditable
    updated_at = models.DateTimeField( default=now.now )# its better to use default= than auto_add (in my own opinion)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = timezone.now() # new posts creation date
        self.updated_at = timezone.now() # old posts update date
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


class NewsLetterRecipients( models.Model ):
    name = models.CharField( max_length=30 )
    email = models.EmailField()


# create a signal to listen for each time you save a post and update the post_id field in Category model
def update_post_id_field_in_category_model(sender, instance, **kwargs):
    if not instance.id in instance.category.post_ids: # to avoid duplicate post ids in category.post_id field
        instance.category.post_ids.append(instance.id) # add the post id to the category.post_id field
        instance.category.save() # save the category


# connect that signal
post_save.connect( update_post_id_field_in_category_model, sender=Post )
