from django.contrib.auth.models import User, auth
from .models import infoProject as projectSql

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