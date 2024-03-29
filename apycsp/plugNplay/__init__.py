#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
Contains common CSP processes such as Id, Delta, Prefix etc.

Copyright (c) 2018 John Markus Bjørndalen, jmb@cs.uit.no.
See LICENSE.txt for licensing details (MIT License).
"""

import asyncio
from apycsp import process, Alternative, Parallel


@process
async def Identity(cin, cout):
    """Copies its input stream to its output stream, adding a one-place buffer
    to the stream."""
    while 1:
        t = await cin()
        await cout(t)


@process
async def Prefix(cin, cout, prefixItem=None):
    t = prefixItem
    while True:
        await cout(t)
        t = await cin()


@process
async def SeqDelta2(cin, cout1, cout2):
    # Sequential version TODO: JCSP version sends the output in parallel. Should this be modified to do the same?
    while True:
        t = await cin()
        await cout1(t)
        await cout2(t)


@process
async def ParDelta2(cin, cout1, cout2):
    while True:
        t = await cin()
        # JCSP version uses a Par here, so we do the same.
        await Parallel(cout1(t),
                       cout2(t))


# experimental version to pinpoint the PAR overhead
@process
async def ParDelta2_t(cin, cout1, cout2):
    loop = asyncio.get_event_loop()
    # l = asyncio.get_event_loop()
    case = 10
    while True:
        t = await cin()
        # JCSP version uses a Par here, so we do the same.
        if case == 10:
            done, pending = await asyncio.wait([cout1(t), cout2(t)])
            [x.result() for x in done]  # need to do this to catch exceptions
        elif case == 11:
            done, pending = await asyncio.wait([cout1(t)])
            [x.result() for x in done]
            done, pending = await asyncio.wait([cout2(t)])
            [x.result() for x in done]
        elif case == 15:
            # Doesn't work. run_until_complete is already running outside this scope.
            loop.run_until_complete(asyncio.wait([cout1(t), cout2(t)]))
        elif case == 20:
            _ = await asyncio.gather(cout1(t), cout2(t))
        elif case == 21:
            _ = await asyncio.gather(cout1(t))
            _ = await asyncio.gather(cout2(t))
        elif case == 30:
            await cout1(t)
            await cout2(t)
        else:
            raise Exception("Fooo")
        # print(res)

Delta2 = ParDelta2


@process
async def Successor(cin, cout):
    """Adds 1 to the value read on the input channel and outputs it on the output channel.
    Infinite loop.
    """
    while True:
        await cout(await cin() + 1)


@process
async def SkipProcess():
    pass


@process
async def Mux2(cin1, cin2, cout):
    alt = Alternative(cin1, cin2)
    while True:
        c = await alt.priSelect()
        await cout(await c())
