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
    if not isAuth(request):
        return render(request, 'login.html')
    return projects(request)

def login(request):
    if isAuth(request):
        return home(request)
    print("HELLO!!---->")
    if request.method == 'POST':
        username = request.POST['username']
        password = hashlib.sha256(request.POST['password'].encode()).hexdigest()
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("HeRa")
            #return home(request)
            return redirect("/")
        else:
            messages.info(request,'Neteisingi duomenys')
            return redirect('/')
    else:
        return redirect('/')

def register(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password1 = hashlib.sha256(request.POST['password1'].encode()).hexdigest()
        password2 = hashlib.sha256(request.POST['password2'].encode()).hexdigest()
        firstname = request.POST['name']
        lastname = request.POST['surname']

        if lastname == "" or firstname == "" or email == "" or username == "":
            messages.info(request,'Reikai užpildyti visus laukus')
            return redirect('register')
        else:
            if password1 == password2:
                if User.objects.filter(username=username).exists():
                    messages.info(request,'Vartotojas užimtas')
                    return redirect('register')
                elif User.objects.filter(email=email).exists():
                    messages.info(request,'Toks paštas jau užregistruotas')
                    return redirect('register')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password1, first_name=firstname, last_name=lastname)
                    user.save()
                    userId = User.objects.filter(username=username).last().id
                    userProjectsSqlPush = userProjectsSql(userId=userId)
                    userProjectsSqlPush.save()
                    messages.info(request,'Vartotojas sukurtas')
                    return render(request, 'login.html')
                    
            else:
                messages.info(request,'Slaptažodžiai neatitinka')
                return redirect('register')

    else:
        return render(request, 'register.html')

def registerHtml(request):
    return render(request, 'register.html')

def toHome(request):
    if not isAuth(request):
        return render(request, 'login.html')
    return redirect('/')

def toAddUAB(request):
    if not isAuth(request):
        return render(request, 'login.html')
    return render(request, 'uab_add.html')

def toAddUABinfo(request):
    if not isAuth(request):
        return render(request, 'login.html')
    uabId = request.POST['uabId']
    data = datetime.date.today()
    busena = infoUABSql.objects.filter(id=uabId).last().busena
    return render(request, 'uab_addInfo.html', {'busena': busena,'uabId': uabId,'data': data})

def toSaNariai(request):
    if not isAuth(request):
        return render(request, 'login.html')
    users = User.objects.all()
    return render(request, 'sa_nariai.html',  {'users': users})

def projects(request):
    if not isAuth(request):
        return render(request, 'login.html')
    projects = projectSql.objects.all()
    projectslist = projectSql.objects.values_list('id', flat=True)
    for x in projectslist:
        print(x)
    return render(request, 'main.html', {'projects': projects, 'projectslist': projectslist})

def rinkodara(request):
    if not isAuth(request):
        return render(request, 'login.html')
    return rinkodaraHTML(request, False,0)

def rinkodaraHTML(request, prideti, projectId):
    if not isAuth(request):
        return render(request, 'login.html')
    infoUABs = infoUABSql.objects.all()
    return render(request, 'rinkodara.html', {'infoUABs': infoUABs, 'prideti': prideti,'projectId': projectId})

def project_lookout(request):
    if not isAuth(request):
        return render(request, 'login.html')
    id = request.GET['id']
    return projectlook(request, id)

def projectlook(request, projectId):
    if not isAuth(request):
        return render(request, 'login.html')
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
    if not isAuth(request):
        return render(request, 'login.html')
    id = request.GET['id']
    return uablook(request, id)

def uablook(request, uabId):
    if not isAuth(request):
        return render(request, 'login.html')
    uab = infoUABSql.objects.filter(id=uabId).last()
    info = reversed(infoUABTrackerSql.objects.filter(UABid=uabId).order_by('date').all())
    return  render(request, 'uab_look.html',{'uab': uab,'info': info})

def myProjects(request):
    if not isAuth(request):
        return render(request, 'login.html')
    userId = auth.get_user(request).id
    projects = projectSql.objects.all()
    if userProjectsSql.objects.filter(userId=userId).exists():
        projectslist = userProjectsSql.objects.filter(userId=userId).last().projectsId
        if len(projectslist) > 0:
            if(projectslist[0]==","):
                projectslist = projectslist[1:]
            projectslist = projectslist.split(",")
            projectslist = [int(x) for x in projectslist]
        else:
            projectslist = [""]
    else:
        projectslist = [""]
    return render(request, 'main.html', {'projects': projects,'projectslist': projectslist})

def disconect(request):
    if not isAuth(request):
        return render(request, 'login.html')
    auth.logout(request)
    return redirect('/')

def projectAddHtml(request):
    if not isAuth(request):
        return render(request, 'login.html')
    return render(request, 'project_add.html')

def projectAdd(request):
    if not isAuth(request):
        return render(request, 'login.html')


    userId = auth.get_user(request).id
    userName = auth.get_user(request).first_name
    userLName = auth.get_user(request).last_name
    userFName = userName + " " + userLName
    name = request.POST['name']
    textas = request.POST['text']
    date = request.POST['date']
    if not projectSql.objects.filter(pavadinimas=name).exists() and not projectSql.objects.filter(data=date).exists():
        projectSqlPush = projectSql(pavadinimas=name,busena=0,data=date,aprasymas=textas,author=userId,author_name=userFName,moderators=userId)
        projectSqlPush.save()
        projectId = projectSql.objects.filter(author=userId).last().id
        print(projectId)
        
        
        other = userProjectsSql.objects.filter(userId=userId).last()
        if userProjectsSql.objects.filter(userId=userId).exists():
            other.projectsId = "," + str(projectId)
            other.save()

        return projectlook(request, projectId)
    else:
        return projects(request)


def busenos_keitimas(request):
    if not isAuth(request):
        return render(request, 'login.html')
    busena = request.POST['inlineRadioOptions']
    id = request.POST['id']

    projectSqlPush = projectSql.objects.filter(id=id).last()
    projectSqlPush.busena = busena
    projectSqlPush.save()

    return projectlook(request, id)

def join_project(request):
    if not isAuth(request):
        return render(request, 'login.html')
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
    if not isAuth(request):
        return render(request, 'login.html')
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
    if not isAuth(request):
        return render(request, 'login.html')
    pav = request.POST['name']
    tipas = request.POST['type']
    email = request.POST['email']
    nr =  request.POST['number']
    tekstas = request.POST['tekstas']

    uabPushSql = infoUABSql(pavadinimas=pav,busena=0,tipas=tipas,email=email,numeris=nr,tekstas=tekstas)
    uabPushSql.save()
    return rinkodara(request)

def uabAddInfo(request):
    if not isAuth(request):
        return render(request, 'login.html')
    id = request.POST['uabId']
    tekstas = request.POST['text']
    data = request.POST['date']
    busena = request.POST['inlineRadioOptions']
    fname = auth.get_user(request).first_name
    lname = auth.get_user(request).last_name
    fullname = fname + " " + lname

    userId = auth.get_user(request).id

    if data == "":
        data = datetime.date.today()

    uabBusena = infoUABSql.objects.filter(id=id).last()
    uabBusena.busena = busena
    uabBusena.save()

    check = infoUABTrackerSql.objects.filter(tekstas=tekstas).last()
    if check is None:
        inforUabTrackerSqlPush = infoUABTrackerSql(UABid=id, tekstas=tekstas,date=data,authId=userId,authName=fullname,busena=busena)
        inforUabTrackerSqlPush.save()

    return uablook(request, id)

def add_uabsToProject(request):
    if not isAuth(request):
        return render(request, 'login.html')
    projectId = request.POST['projectId']
    return rinkodaraHTML(request, True, projectId)

def uab_add_project(request):
    if not isAuth(request):
        return render(request, 'login.html')
    projectId = request.POST['projectId']
    uabId = request.POST['uabId']
    uab = infoUABSql.objects.filter(id=uabId).last()
    project = projectSql.objects.filter(id=projectId).last()
    if not projectUABsSql.objects.filter(UABid=uabId).exists():
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

def delete_project(request):
    if not isAuth(request):
        return render(request, 'login.html')
    projectId = request.POST['projectId']
    projectSql.objects.filter(id=projectId).delete()
    return redirect('/')

def projectUab_delete(request):
    if not isAuth(request):
        return render(request, 'login.html')
    id = request.POST['id']
    projectId = request.POST['projectId']
    projectUABsSql.objects.filter(id=id).delete()
    return projectlook(request, projectId)

def to_edit_uab(request):
    if not isAuth(request):
        return render(request, 'login.html')
    uabId = request.POST['uabId']
    uab = infoUABSql.objects.filter(id=uabId).last()
    return render(request, "uab_update.html",{'uab': uab})

def edit_uab(request):
    if not isAuth(request):
        return render(request, 'login.html')
    uabId = request.POST['uabId']
    tipas = request.POST['type']
    email = request.POST['email']
    nr = request.POST['number']
    pav = request.POST['name']
    tekstas = request.POST['tekstas']

    updateUAB = infoUABSql.objects.filter(id=uabId).last()
    updateUAB.pavadinimas = pav
    updateUAB.numeris = nr
    updateUAB.email = email
    updateUAB.tipas = tipas
    if not tekstas == "":
        updateUAB.tekstas = tekstas
    updateUAB.save()

    return uablook(request, uabId)