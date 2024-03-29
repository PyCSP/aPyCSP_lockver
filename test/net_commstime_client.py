#!/usr/bin/env python3
import asyncio
import time
import common
import apycsp.net
from apycsp.plugNplay import Prefix, Delta2, Successor
from apycsp import run_CSP, process


args = common.handle_common_args([
    (("-s", "--serv"), dict(help="specify server as host:port (use multiple times for multiple servers)", action="append", default=[]))
])
if len(args.serv) < 1:
    apycsp.net.setup_client()
else:
    for sp in args.serv:
        apycsp.net.setup_client(sp)

loop = asyncio.get_event_loop()


@process
async def consumer(cin):
    "Commstime consumer process"
    # N = 5000
    N = 500
    ts = time.time
    t1 = ts()
    await cin()
    t1 = ts()
    for i in range(N):
        await cin()
    t2 = ts()
    dt = t2 - t1
    tchan = dt / (4 * N)
    print("DT = %f.\nTime per ch : %f/(4*%d) = %f s = %f us" %
          (dt, dt, N, tchan, tchan * 1000000))
    print("consumer done, posioning channel")
    await cin.poison()
    return tchan


def CommsTimeBM():
    # Get access to remote channels.
    # TODO: we can only run this benchmark once before we need to restart the server side
    # as we will need to re_create the channels between each benchmark run (the first run will poison them)
    a = apycsp.net.get_channel_proxy_s("a")
    b = apycsp.net.get_channel_proxy_s("b")
    c = apycsp.net.get_channel_proxy_s("c")
    d = apycsp.net.get_channel_proxy_s("d")

    print("Running commstime test")
    # Rather than pass the objects and get the channel ends wrong, or doing complex
    # addons like in csp.net, i simply pass the write and read functions as channel ends.
    # Note: c.read.im_self == c, also check im_func, im_class
    rets = run_CSP(Prefix(c.read, a.write, prefixItem=0),    # initiator
                   Delta2(a.read, b.write, d.write),         # forwarding to two
                   Successor(b.read, c.write),               # feeding back to prefix
                   consumer(d.read))                         # timing process
    return rets[-1]


CommsTimeBM()
