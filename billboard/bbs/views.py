from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import *
from .filters import PostFilter
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class IndexView(View):
    def get(self, request):
        my_job.delay()
        hello.delay()
        return HttpResponse('Hello!')

# Create your views here.
def index(request):
    bbs = Post.objects.all().order_by("dateCreation").reverse()[:10]
    # bbs = Post.objects.all().order_by("-id")
    categories = Category.objects.all()
    return render(request, 'index.html', context={'news': bbs, 'categories': categories})

def detail(request, id):
    new = Post.objects.get(id=id)
    post_comments = Comment.objects.filter(commentPost=Post.objects.get(id=id))
    return render(request, 'details.html', context={'new': new, 'post_comments': post_comments})


class PostList(ListView):
   model = Post
   ordering = '-dateCreation'
   template_name = 'bbs_list_all.html'
   context_object_name = 'news'
   paginate_by = 5


class PostSearch(ListView):
   model = Post
   ordering = '-dateCreation'
   template_name = 'search.html'
   context_object_name = 'posts'
   paginate_by = 5

   def get_queryset(self):
       queryset = super().get_queryset()
       self.filterset = PostFilter(self.request.GET, queryset)
       return self.filterset.qs

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       categories = Category.objects.all()
       context['categories'] = categories
       # Добавляем в контекст объект фильтрации.
       context['filterset'] = self.filterset
       return context


class PostbyCategList(ListView):
   model = Post
   template_name = 'bbs_list_cat.html'
   context_object_name = 'news'
   paginate_by = 5

   def get_queryset(self):
       return Post.objects.filter(categoryType=self.kwargs['slug']).order_by("dateCreation").reverse()


def postbycategory(request, slug):
    qs = Post.objects.filter(categoryType=slug).order_by("dateCreation").reverse()
    categories = Category.objects.all()
    namerus = catdictionary[slug]
    paginator = Paginator(qs, 3)
    print(paginator)
    page = request.GET.get('page')
    print(page)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    print(posts)
    return render(request, 'bbs_list_cat.html', {
        'posts': posts,
        'page': page,
        'categories': categories,
        'slug': slug,
        'namerus': namerus
    })


class PostDetail(DetailView):
   model = Post
   template_name = 'detail.html'
   context_object_name = 'new'
   queryset = Post.objects.all()


class PostDetailEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('bbs.change_post',)
    form_class = PostForm
    model = Post
    context_object_name = 'new'
    template_name = 'post_edit.html'

    def form_valid(self, form):
        # post = form.save(commit=False)
        # post.categoryType = 'AR'
        # Это если будет нужно сменить 'NW' на 'AR'
        form.save()
        return super(PostDetailEdit, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse('post_detail_show', kwargs={'id': self.object.pk})


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('bbs.delete_post',)
    model = Post
    context_object_name = 'new'
    template_name = 'post_delete.html'
    success_url = '/bbs_list/'


def create_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            #form.save()
            return HttpResponseRedirect('/bbs_list/')
    return render(request, 'post_edit.html', {'form': form})


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('bbs.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'

    def form_valid(self, form):
        userid = self.request.user.id
        post = form.save(commit=False)
        post.author = Author.objects.get(id=userid)
        form.save(commit=False)
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        # print('* * * * * * *', self.object.pk)
        return reverse('post_detail_show', kwargs={'id': self.object.pk})


@csrf_protect
@permission_required('bbs.add_comment',)
def comment_create_view(request, pk):
    #print('- - -comment_create_view- - >', pk)
    new = Post.objects.get(id=pk)
    #print('New:', new)
    if request.method == 'GET':
        #print('GET - - - >', pk)
        comment_form = CommentForm()
        context = {
            'new': new,
            'comment_form': comment_form,
        }
        return render(request, 'comment_create.html', context)

    elif request.method == 'POST':
        #print('POST - - - >', pk)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            #print('POST - - - >form.is_valid', pk)
            #commentUser = comment_form.cleaned_data.get('commentUser')
            commentUser = request.user
            text = comment_form.cleaned_data.get('text')
            Comment.objects.create(
                commentPost=new,
                commentUser=commentUser,
                text=text
            )
            context = {
                'new': new,
                'comment_form': comment_form,
            }
            return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': pk}))
        else:
            context = {
                'new': new,
                'comment_form': comment_form,
            }
            return render(request, 'comment_create.html', context)


@csrf_protect
@permission_required('bbs.change_comment',)
def comment_edit_view(request, id1, id2):
    #print('- - - comment_edit_view - - new:', id1, '- - comment:', id2)
    new = Post.objects.get(id=id1)
    #print('New:', new)
    comment = Comment.objects.get(id=id2)
    #print('Comment:', comment)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': id1}))
    return render(request, 'comment_edit.html', {'new': new, 'comment': comment, 'form': form})


class CommentDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('bbs.delete_comment',)
    #model = Comment
    template_name = 'comment_delete.html'
    success_url = '/bbs_list/'

    def get_object(self):
        #print('get_object')
        #print('- - - CommentDelete - - new:', id1, '- - comment:', id2)
        new = Post.objects.get(id=self.kwargs['id1'])
        #print('New:', new)
        idid1 = new.id
        #print('idid1',idid1)
        comment = Comment.objects.get(id=self.kwargs['id2'])
        #print('Comment:', comment)
        idid2 = comment.id
        #print('idid2',idid2)
        context = {'new': new, 'comment': comment}
        return comment
        #TODO надо передать и new и comment, но передается только comment, а context ничего не перадает (пусто)

    def delete(self, request, *args, **kwargs):
        comment2del = Comment.objects.get(id=self.kwargs['id2'])
        comment2del.delete()
        return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': id1}))


@csrf_protect
@permission_required('bbs.delete_comment',)
def comment_delete_view(request, id1, id2):
    #print('- - - comment_delete_view - - new:', id1, '- - comment:', id2)
    new = Post.objects.get(id=id1)
    #print('New:', new)
    comment = Comment.objects.get(id=id2)
    #print('Comment:', comment)
    if request.method == 'POST':
        #print('- - - form valid - - new:', id1, '- - comment:', id2)
        comment2del = Comment.objects.get(id=id2)
        comment2del.delete()
        return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': id1}))
    else:
        #No data submitted; create a blank form.
        form = CommentForm()
    return render(request, 'comment_delete.html', {'new': new, 'comment': comment})


@csrf_protect
@permission_required('bbs.change_comment',)
def comment_confirm_view(request, id1, id2):
    #print('- - - comment_confirm_view - - new:', id1, '- - comment:', id2)
    new = Post.objects.get(id=id1)
    #print('New:', new)
    comment2conf = Comment.objects.get(id=id2)
    #print('Comment:', comment)
    print('Begin:', comment2conf.confirmed)
    if request.method == 'POST':
        #print('- - - form valid - - new:', id1, '- - comment:', id2)
        comment2conf.confirmed = True
        comment2conf.save()
        #return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': id1}))
        return HttpResponseRedirect(reverse('responsestome'))
    else:
        #No data submitted; create a blank form.
        form = CommentForm()
    return render(request, 'comment_confirm.html', {'new': new, 'comment': comment2conf})

class ContactList(ListView):
    model = Post
    ordering = '-dateCreation'
    template_name = 'bbs_list_cat.html'
    context_object_name = 'news'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        print(user)
        if user.is_authenticated:
            print(user, 'is_authenticated')
            return Post.objects.filter(author=self.request.user)
        return Post.objects.filter(author=None)


@login_required
@csrf_protect
def MyPostList(request):
    qs = Post.objects.filter(author=request.user.id).order_by("dateCreation").reverse()
    return render(request, 'bbs_list_all_my.html', {'news': qs})

@login_required
@csrf_protect
def MyCommentList(request):
    qs = Comment.objects.filter(commentUser=request.user.id).distinct().order_by("dateCreation").reverse()
    post_qs = Post.objects.filter(comment__commentUser=request.user.id).distinct().order_by("dateCreation").reverse()
    #print(post_qs)
    #print(post_qs.count())
    return render(request, 'comment_all_my.html', {'comments': qs, 'news': post_qs})


@login_required
@csrf_protect
def ResponsesToMeList(request):
    qs = Comment.objects.filter(commentPost__author=request.user.id).order_by("dateCreation").reverse()
    post_qs = Post.objects.filter(author=request.user.id).order_by("dateCreation").reverse()
    #.order_by("dateCreation").reverse()
    return render(request, 'comment_all_to_me.html', {'comments': qs, 'news': post_qs})

