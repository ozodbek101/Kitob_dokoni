from django.shortcuts import render


from .models import Post


def home_page(request):
    posts = Post.objects.all()
    
    
    return render(
        request=request, 
        template_name="home_page.html",
        context={ "posts":  posts}
    )
