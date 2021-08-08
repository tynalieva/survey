from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .forms import *
from .models import *


def index(request):
    # posts = Post.objects.all()
    return render(request, 'index.html')


def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    posts = Post.objects.filter(category_id=slug)
    return render(request, 'post/category_detail.html', locals())


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    image = post.get_image
    images = post.images.exclude(id=image.id)
    return render(request, 'post/post_detail.html', locals())


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


def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.add_message(request, messages.INFO, 'Successfully deleted')
        return redirect('home')
    return render(request, 'post/post_delete.html')


class CreatePostView(generic.CreateView):
    queryset = Post.objects.all()
    form_class = PostForm
    template_name = 'main/create_post.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

# class CreatePostView(generic.CreateView):
#     queryset = Post.objects.all()
#     form_class = PostForm
#     template_name = 'main/post_create.html'
#
#     def form_valid(self, form):
#         form.instance.owner = self.request.user3
#         return super().form_valid(form)

