from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required



@login_required
def delete_user(request):
    """
    Allows a logged-in user to delete their own account.
    """

    user = request.user

    logout(request)          # log them out before deleting
    user.delete()            # triggers post_delete signal

    return redirect("home") 
