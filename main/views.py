from datetime import timedelta

from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from .forms import *
from .models import *
from .permissions import UserPermissionsMixin


class HomePageView(generic.ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_template_names(self):
        template_name = super(HomePageView, self).get_template_names()
        search = self.request.GET.get('query')
        if search:
            template_name = 'search.html'
        return template_name

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('query')
        filter = self.request.GET.get('filter')


        if search:
            context['posts'] = Post.objects.filter(Q(title__icontains=search)|
                                                   Q(description__icontains=search))

        elif filter == 'new':
            start_date = timezone.now() - timedelta(days=2)
            context['posts'] = Post.objects.filter(created_at__gte=start_date)

        else:
            context['post'] = Post.objects.all()

        return context


class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'post/category_detail.html'
    context_object_name = 'category'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.slug = kwargs.get('slug', None)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(category_id=self.slug)
        return context


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'post/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_object().get_image
        stuff = get_object_or_404(Post, id=self.kwargs['pk'])
        total_likes = stuff.total_likes()

        liked = False

        try:
            stuff.like.filter(email=self.request.user.email)
            if stuff.like.filter(email=self.request.user.email).exists():
                liked = True
            else:
                liked = False
        except Exception as identifier:
            liked = False

        context['images'] = self.get_object().images.exclude(id=image.id)
        context['total_likes'] = total_likes
        context['liked'] = liked
        return context


@login_required(login_url='login')
def post_create(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=3)

    if request.method == 'POST':
        post_form = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        if post_form.is_valid() and formset.is_valid():
            post = post_form.save(commit=False)
            post.owner = request.user

            for form in formset.cleaned_data:
                try:
                    image = form['image']
                    post.save()
                    Image.objects.create(image=image, post=post)
                    return redirect(post.get_absolute_url())
                except Exception as identifier:
                    image = None
                    messages.info(request, "Image is required")
                    return redirect('post_create')


    else:
        post_form = PostForm()
        formset = ImageFormSet(queryset=Image.objects.none())

    return render(request, 'post/post_create.html', locals())


def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.owner:
        ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=3)
        post_form = PostForm(request.POST or None, instance=post)
        formset = ImageFormSet(request.POST or None, request.FILES or None, queryset=Image.objects.filter(post=post))

        if post_form.is_valid() and formset.is_valid():
            post = post_form.save()

            for form in formset:
                images = form.save(commit=False)
                images.post = post
                images.save()
            return redirect(post.get_absolute_url())

        return render(request, 'post/post_update.html', locals())
    else:
        messages.add_message(request, messages.INFO, "Only post owner can update POST!")
        return redirect('home')


class PostDeleteView(UserPermissionsMixin, generic.DeleteView):
    model = Post
    template_name = 'post/post_delete.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.add_message(request, messages.INFO, 'Successfully deleted')
        return HttpResponseRedirect(success_url)


def like(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    liked = False
    print(post.like)
    if post.like.filter(email=request.user.email).exists():
        post.like.remove(request.user)
        liked = False
    else:
        post.like.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('post_detail', args=[str(pk)]))


class CommentCreateView(generic.CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post/comment_create.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        form.instance.owner = self.request.user
        return super().form_valid(form)


