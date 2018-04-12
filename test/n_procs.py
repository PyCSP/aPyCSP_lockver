#!/usr/bin/env python3
# -*- coding: latin-1 -*-
from common import *
import apycsp 
import os
import psutil
import sys
import time
import common
from apycsp import One2OneChannel, Any2OneChannel, One2AnyChannel, process, run_CSP

args = common.handle_common_args([
    (["np"], dict(type=int, help='number of procs', default=10, nargs="?")),
    ])

N_PROCS = args.np # 10 if len(sys.argv) < 2 else int(sys.argv[1])

@process
async def simple_proc(pid, checkin, cin):
    # check in
    await checkin(pid)
    # wait for poison
    while True:
        x = await cin()

@process
async def killer(chin, pch, nprocs):
    global rss
    print("Killer waiting for the other procs to call in")
    for i in range(nprocs):
        x = await chin()
    print("Done, checking memory usage")
    p = psutil.Process(os.getpid())
    rss = p.memory_info().rss
    print(f"RSS now {rss}  {rss/(1024**2)}M")
    print("now poisioning")
    await pch.poison()
    return rss

def run_n_procs(n):
    print(f"Running with {n} simple_procs")
    ch = Any2OneChannel()
    pch =  One2AnyChannel()
    t1 = time.time()
    tasks = [simple_proc(i, ch.write, pch.read) for i in range(N_PROCS)]
    tasks.append(killer(ch.read, pch, n))
    t2 = time.time()
    res = run_CSP(*tasks)
    t3 = time.time()
    rss = res[-1]
    tcr = t2-t1
    trun = t3-t2
    print("Creating tasks: {:15.3f} us  {:15.3f} ms  {:15.9f} s".format(1_000_000 * tcr,  1000 * tcr,  tcr))
    print("Running  tasks: {:15.3f} us  {:15.3f} ms  {:15.9f} s".format(1_000_000 * trun, 1000 * trun, trun))
    print("{" + (f'"nprocs" : {n}, "t1" : {t1}, "t2" : {t2}, "t3" : {t3}, "tcr" : {tcr}, "trun" : {trun}, "rss" : {rss}') + "}")

run_n_procs(N_PROCS)
