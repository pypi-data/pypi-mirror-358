import os

def main (django_orm = False):
    print ("downloading manage.py")
    os.system ("wget https://gitlab.com/skitai/atila/-/raw/master/atila/collabo/django/manage.py")

    print ("creating project")
    os.system ("chmod +x manage.py")

    if not django_orm:
        os.system ("./manage.py startatila")
        os.system ("rm -f manage.py")
        print ("created on backend directory")
        os.system ("chmod +x skitaid.py")
        return

    os.system ("./manage.py startproject")
    os.system ("chmod +x skitaid.py")

    print ("atila project created on backend")
    print ("django project has been created on backend/models")
    print ("please modify backend/models/settings.py")
    print ("usage:")
    print ("  ./manage.py migrate")
    print ("  ./manage.py collectstatic")
    print ("  ./manage.py createsuperuser")
    print ("  ./manage.py startapp myapp")
    print ("  ./manage.py makemigration --empty myapp")
