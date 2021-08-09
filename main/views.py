from datetime import timedelta

from django.contrib import messages
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from .forms import *
from .models import *


class HomePageView(generic.ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'
    paginate_by = 2

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
        context['images'] = self.get_object().images.exclude(id=image.id)
        return context


def post_create(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=3)

    if request.method == 'POST':
        post_form = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        if post_form.is_valid() and formset.is_valid():
            post = post_form.save()

            for form in formset.cleaned_data:
                image = form['image']
                Image.objects.create(image=image, post=post)
            return redirect(post.get_absolute_url())
    else:
        post_form = PostForm()
        formset = ImageFormSet(queryset=Image.objects.none())

    return render(request, 'post/post_create.html', locals())


def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=3)
    post_form = PostForm(request.POST or None, instance=post)
    formset = ImageFormSet(request.POST or None, request.FILES or None, queryset=Image.objects.filter(post=post))

    if post_form.is_valid() and formset.is_valid():
        post = post_form.save()

        for form in formset:
            image = form.save(commit=False)
            image.post = post
            image.save()
        return redirect(post.get_absolute_url())

    return render(request, 'post/post_update.html', locals())


class PostDeleteView(generic.DeleteView):
    model = Post
    template_name = 'post/post_delete.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.add_message(request, messages.INFO, 'Successfully deleted')
        return HttpResponseRedirect(success_url)
