from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts:login')
def home(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard:dashboard')
    return render(request, 'home.html')
