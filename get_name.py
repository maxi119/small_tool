
import sys, os
from subprocess import Popen, PIPE, STDOUT
from multiprocessing.pool import ThreadPool
import threading


look_dns = "192.168.1.240"

def do_ping( *args ):
    import re
    global rslt
    pattern = None
    x = args[0]
    mode_ping = args[1]
    rslt = args[2]
    g_lock = args[3]

    if mode_ping:
        pattern = re.compile( "Ping\s(\w+)\s\w*" )
    else:
        pattern = re.compile( u"名稱:\s+(.+)", re.UNICODE )
    sys.stdout.write( "to %s --\n" % x )
    p = None
    if mode_ping:
        p = Popen( ['ping', '-a', x] , shell=True, stdin=PIPE, stdout=PIPE)
    else:
        p = Popen( ['nslookup', x, look_dns] , shell=True, stdin=PIPE, stdout=PIPE)
    while True:
        line = p.stdout.readline()
        if not line:
            break
        line = line.decode( 'big5' )
        if line.strip():
            g = pattern.match( line )
            if g and g.groups():
                with g_lock:
                    rslt[ x ]['name_' + ("ping" if mode_ping else "look") ] = g.groups()[0].strip()
                break
    p.terminate()

def main():

    ips = [ "192.168.1.%d"%i  for i in xrange(2, 255 )  ]

    pool = ThreadPool( 30 )
    rslt = {}
    glock = threading.RLock()
    q = []
    for x in ips:
        rslt[x] = {}
        q.append( pool.apply_async( do_ping, [x, True, rslt, glock] ) )
        q.append( pool.apply_async( do_ping, [x, False, rslt, glock ] ) )

    for r in q:
        r.get()
    print('\n\n\n')

    for k, v in rslt.items():
        name_ping = v.get( 'name_ping' )
        name_look = v.get( 'name_look')
        if name_ping or name_look:
            print ( "%s  => %s  ,%s  "%(k, str( name_ping ), str( name_look ) ) )
    print( "end" )

if __name__ == "__main__":
    main()

