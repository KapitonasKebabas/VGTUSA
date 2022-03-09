from django.contrib.auth.models import User, auth
from .models import infoProject as projectSql
from urllib import request
from django.shortcuts import render, redirect

def isJoinedProject(userId, projectId):
    modList = projectSql.objects.filter(id=projectId).last().moderators.split(",")
    users = User.objects.all()
    modArr = []
    yraList = True
    for mod in modList:
        if int(mod) == int(userId) and yraList == True:
            print(mod + " " + str(userId))
            yraList = False
            break

    return yraList

def isAuth(request):
    boolas = False
    if request.user.is_authenticated:
        print("auth")
        boolas = True
    else:
        print("No auth")
        #return redirect('login.html')
    return boolas