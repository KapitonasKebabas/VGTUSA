#from asyncio.windows_events import NULL
#from fnmatch import fnmatchcase
import re
from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import get_user_model
import hashlib
from django.contrib import messages
from .models import infoProject as projectSql
from .models import user_projects as userProjectsSql
from .models import infoUAB as infoUABSql
from .models import UABinfoTracker as infoUABTrackerSql
from .models import projectUABs as projectUABsSql
from .functions import *
import datetime
from array import *
#from .models import infoProject

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return projects(request)
    else:
        return render(request, 'login.html')

def login(request):
    print("HELLO!!---->")
    if request.method == 'POST':
        username = request.POST['username']
        password = hashlib.sha256(request.POST['password'].encode()).hexdigest()
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("HeRa")
            return home(request)
        else:
            messages.info(request,'wrong inputs')
            return redirect('/')
    else:
        return redirect('/')

def register(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password1 = hashlib.sha256(request.POST['password1'].encode()).hexdigest()
        password2 = hashlib.sha256(request.POST['password2'].encode()).hexdigest()

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'user taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email is taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                userId = User.objects.filter(username=username).last().id
                userProjectsSqlPush = userProjectsSql(userId=userId)
                userProjectsSqlPush.save()
                messages.info(request,'user created')
                return render(request, 'logIn.html')
                
        else:
            messages.info(request,'password not matched')
            return redirect('register')

    else:
        return render(request, 'register.html')

def registerHtml(request):
    return render(request, 'register.html')

def toHome(request):
    return redirect('/')

def toAddUAB(request):
    return render(request, 'uab_add.html')

def toAddUABinfo(request):
    uabId = request.POST['uabId']
    data = datetime.date.today()
    return render(request, 'uab_addInfo.html', {'uabId': uabId,'data': data})

def toSaNariai(request):
    users = User.objects.all()
    return render(request, 'sa_nariai.html',  {'users': users})

def projects(request):
    projects = projectSql.objects.all()
    projectslist = projectSql.objects.values_list('id', flat=True)
    for x in projectslist:
        print(x)
    return render(request, 'main.html', {'projects': projects, 'projectslist': projectslist})

def rinkodara(request):
    return rinkodaraHTML(request, False,0)

def rinkodaraHTML(request, prideti, projectId):

    infoUABs = infoUABSql.objects.all()
    return render(request, 'rinkodara.html', {'infoUABs': infoUABs, 'prideti': prideti,'projectId': projectId})

def project_lookout(request):
    id = request.GET['id']
    return projectlook(request, id)

def projectlook(request, projectId):
    project = projectSql.objects.filter(id=projectId).last()
    busena = project.busena
    projectAuth = project.author
    projectPav = project.pavadinimas
    user = User.objects.filter(id=projectAuth).last()
    userId = auth.get_user(request).id
    userName = user.first_name
    userLName = user.last_name
    userFName = userName + " " + userLName
    modList = projectSql.objects.filter(id=projectId).last().moderators.split(",")
    users = User.objects.all()
    modArr = []
    yraList = True
    yraList = isJoinedProject(userId, projectId)
    for mod in modList:
        for user in users:
            if int(mod) == user.id:
                modArr.append(user.first_name + " " + user.last_name)
    NotMyProject = True
    if int(userId) == int(projectId):
        NotMyProject = False
    #PatikrinimasArYraliste

    #UABS
    projectUABs = projectUABsSql.objects.filter(projectId=projectId).all()
                
    return render(request, 'project_look.html', {'project': project,'projectUABs': projectUABs,'NotMyProject': NotMyProject,'yraList': yraList, 'projectId': projectId, 'projectPav': projectPav,'modArr': modArr,'userId': userId,'projectAuth': projectAuth,'userFName': userFName,'busena': busena})

def uab_lookout(request):
    id = request.GET['id']
    return uablook(request, id)

def uablook(request, uabId):
    uab = infoUABSql.objects.filter(id=uabId).last()
    info = reversed(infoUABTrackerSql.objects.filter(UABid=uabId).order_by('date').all())
    return  render(request, 'uab_look.html',{'uab': uab,'info': info})

def myProjects(request):
    userId = auth.get_user(request).id
    projects = projectSql.objects.all()
    projectslist = userProjectsSql.objects.filter(userId=userId).last().projectsId
    projectslist = projectslist.split(",")
    projectslist = [int(x) for x in projectslist]
    print(userId)
    for  x in projectslist:
        print(x)

    return render(request, 'main.html', {'projects': projects,'projectslist': projectslist})

def disconect(request):
    auth.logout(request)
    return redirect('/')

def projectAddHtml(request):
    return render(request, 'project_add.html')

def projectAdd(request):
    if request.user.is_authenticated:
        userId = auth.get_user(request).id
        userName = auth.get_user(request).first_name
        userLName = auth.get_user(request).last_name
        userFName = userName + " " + userLName
        name = request.POST['name']
        textas = request.POST['text']
        date = request.POST['date']

        projectSqlPush = projectSql(pavadinimas=name,busena=0,data=date,aprasymas=textas,author=userId,author_name=userFName,moderators=userId)
        projectSqlPush.save()
        projectId = projectSql.objects.filter(author=userId).last().id
        print(projectId)
        
        other = userProjectsSql.objects.filter(userId=userId).projectsId
        if other == "":
            other = str(projectId)
            other.save()
        else:
            other = "," + str(projectId)
            other.save()


        return projectlook(request, projectId)

    else:
        return render(request, 'login.html')

def busenos_keitimas(request):
    busena = request.POST['inlineRadioOptions']
    id = request.POST['id']

    projectSqlPush = projectSql.objects.filter(id=id).last()
    projectSqlPush.busena = busena
    projectSqlPush.save()

    return projectlook(request, id)

def join_project(request):
    userId = request.POST['userId']
    projectId = request.POST['projectId']
    yraList = True
    yraList = isJoinedProject(userId, projectId)

    if yraList:
        projectSqlPush = projectSql.objects.filter(id=projectId).last()
        projectSqlPush.moderators = projectSqlPush.moderators + "," + userId
        projectSqlPush.save()

        userSqlPush = userProjectsSql.objects.filter(userId=userId).last()


        if userSqlPush is not None:
            print(userSqlPush.projectsId + "," + str(projectId))
            userSqlPush.projectsId = userSqlPush.projectsId + "," + str(projectId)
        else:
            userSqlPush.projectsId = str(projectId)
        userSqlPush.save()

    return projectlook(request, projectId)

def leave_project(request):
    userId = request.POST['userId']
    projectId = request.POST['projectId']
    print(str(projectId) + " ProjectId")
    projectSqlPush = projectSql.objects.filter(id=projectId).last()
    newStr=""
    for x in projectSqlPush.moderators.split(","):
        if int(x) != userId:
            newStr = newStr + "," + x
            break
    projectSqlPush.moderators = newStr[1:]
    projectSqlPush.save()

    userSqlPush = userProjectsSql.objects.filter(userId=userId).last()
    print(userSqlPush.projectsId.split(","))
    newStr=""
    for x in userSqlPush.projectsId.split(","):
        print(x)
        if int(x) != int(projectId):
            newStr = newStr + "," + x
    print(newStr + " ----> newStr")
    userSqlPush.projectsId = newStr[1:]
    userSqlPush.save()
    return projectlook(request, projectId)

def uabAdd(request):
    pav = request.POST['name']
    tipas = request.POST['type']
    email = request.POST['email']
    nr =  request.POST['number']

    uabPushSql = infoUABSql(pavadinimas=pav,busena=0,tipas=tipas,email=email,numeris=nr)
    uabPushSql.save()
    return rinkodara(request)

def uabAddInfo(request):
    id = request.POST['uabId']
    tekstas = request.POST['text']
    data = request.POST['date']
    fname = auth.get_user(request).first_name
    lname = auth.get_user(request).last_name
    fullname = fname + " " + lname

    userId = auth.get_user(request).id

    if data == "":
        data = datetime.date.today()

    check = infoUABTrackerSql.objects.filter(tekstas=tekstas).last()
    if check is None:
        inforUabTrackerSqlPush = infoUABTrackerSql(UABid=id, tekstas=tekstas,date=data,authId=userId,authName=fullname)
        inforUabTrackerSqlPush.save()

    return uablook(request, id)

def add_uabsToProject(request):
    projectId = request.POST['projectId']
    return rinkodaraHTML(request, True, projectId)

def uab_add_project(request):
    projectId = request.POST['projectId']
    uabId = request.POST['uabId']
    uab = infoUABSql.objects.filter(id=uabId).last()
    project = projectSql.objects.filter(id=projectId).last()

    projectUABsSqlPush = projectUABsSql(UABid=uabId,pavadinimasUAB=uab.pavadinimas,projectId=projectId,pavadinimasProject=project.pavadinimas,tipas=uab.tipas)
    projectUABsSqlPush.save()

    userId = auth.get_user(request).id
    fname = auth.get_user(request).first_name
    lname = auth.get_user(request).last_name
    fullname = fname + " " + lname
    tekstas = "Prideta prie remenciu imoniu projekte: " + str(project.pavadinimas)
    infoUABTrackerSqlPush = infoUABTrackerSql(UABid=uabId,tekstas=tekstas,date=datetime.date.today(),authName=fullname,authId=userId)
    infoUABTrackerSqlPush.save()

    return projectlook(request,projectId)
