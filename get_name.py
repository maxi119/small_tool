
import sys, os
from subprocess import Popen, PIPE, STDOUT
from multiprocessing.pool import ThreadPool
import threading

rslt = {}
g_lock = threading.RLock()

look_dns = "192.168.1.240"
mode_ping = True

def do_ping( *args ):
    import re
    global rslt
    pattern = None
    if mode_ping:
        re.compile( "Ping\s(\w+)\s\w*" )
    else:
        pattern = re.compile( u"名稱:\s+(.+)", re.UNICODE )
    x = args[0]
    #sys.stdout.write( "\nto %s --" % x )
    p = None
    if mode_ping:
        p = Popen( ['ping', '-a', x] , shell=True, stdin=PIPE, stdout=PIPE)
    else:
        p = Popen( ['nslookup', x, '192.168.1.240'] , shell=True, stdin=PIPE, stdout=PIPE)
    while True:
        line = p.stdout.readline()
        if not line:
            break
        line = line.decode( 'big5' )
        if line.strip():
            g = pattern.match( line )
            if g and g.groups():
                with g_lock:
                    rslt[ x ] = g.groups()[0].strip()
                break
    p.terminate()

def main():

    ips = [ "192.168.1.%d"%i  for i in xrange(2, 255 )  ]

    pool = ThreadPool( 10 )
    q = []
    for x in ips:
        q.append( pool.apply_async( do_ping, [x] ) )

    for r in q:
        r.get()

    for k, v in rslt.items():
        print ( "%s  => %s"%(k, v) )
    print( "end" )

if __name__ == "__main__":
    main()

