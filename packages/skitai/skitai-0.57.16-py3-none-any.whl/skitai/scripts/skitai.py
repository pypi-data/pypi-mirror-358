import sys
import os
from .commands import smtpda, status, pstats, init

def help ():
    print ("usage: skitai <command> [<options>]")
    print ("command:")
    print ("  init: initialize atila app development")
    print ("  init-django-orm: initialize atila app with django ORM development")
    print ("  smtpda: contril SMTP Delivery Agent")
    print ("  status: view app status")
    print ("  pstats: view profiling statistics")
    sys.exit ()

def main ():
    try:
        cmd = sys.argv [1]
    except IndexError:
        help ()

    sys.argv.pop (1)
    if cmd == "smtpda":
        smtpda.main ()
    elif cmd == "status":
        status.main ()
    elif cmd == "pstats":
        pstats.main ()
    elif cmd == "init-django-orm":
        init.main (django_orm = True)
    elif cmd == "init":
        init.main (django_orm = False)
    else:
        print ("unknown conmand")


if __name__ == "__main__":
    main ()
