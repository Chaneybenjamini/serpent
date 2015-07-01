import bitcoin as b
import random
import sys
import math
from ethereum import tester as t
import substitutes
import time

vals = [random.randrange(2**256) for i in range(12)]

test_points = [b.jacobian_multiply((b.Gx, b.Gy, 1), r) for r in vals]

G = [b.Gx, b.Gy, 1]
Z = [0, 0, 1]


def neg_point(p):
    return [p[0], b.P - p[1], p[2]]

s = t.state()
s.block.gas_limit = 10000000
t.gas_limit = 1000000

tests = sys.argv[1:]

if '--log' in tests:
    t.set_logging_level(int((tests+[1])[tests.index('--log') + 1]))

if '--modexp' in tests or not len(tests):
    c = s.abi_contract('modexp.se')
    print "Starting modexp tests"

    for i in range(0, len(vals) - 2, 3):
        o1 = substitutes.modexp_substitute(vals[i], vals[i+1], vals[i+2])
        o2 = c.call(vals[i], vals[i+1], vals[i+2], profiling=1)
        # assert o1["gas"] == o2["gas"], (o1, o2)
        assert o1["output"] == o2["output"], (o1, o2)

if '--ecrecover' in tests or not len(tests):
    c = s.contract('ecrecover.se')
    print "Starting ecrecover tests"

    for i in range(5):
        print 'trying ecrecover_test', vals[i*2], vals[i*2+1]
        k = vals[i*2]
        h = vals[i*2+1]
        V, R, S = b.ecdsa_raw_sign(b.encode(h, 256, 32), k)
        aa = time.time()
        o1 = substitutes.ecrecover_substitute(h, V, R, S)
        print 'sub', time.time() - aa
        a = time.time()
        o2 = s.profile(t.k0, c, 0, funid=0, abi=[h, V, R, S])
        print time.time() - a
        # assert o1["gas"] == o2["gas"], (o1, o2, h, V, R, S)
        assert o1["output"] == o2["output"], (o1, o2, h, V, R, S)

    # Explicit tests

    data = [[
        0xf007a9c78a4b2213220adaaf50c89a49d533fbefe09d52bbf9b0da55b0b90b60,
        0x1b,
        0x5228fc9e2fabfe470c32f459f4dc17ef6a0a81026e57e4d61abc3bc268fc92b5,
        0x697d4221cd7bc5943b482173de95d3114b9f54c5f37cc7f02c6910c6dd8bd107
    ]]

    for datum in data:
        o1 = substitutes.ecrecover_substitute(*datum)
        o2 = s.profile(t.k0, c, 0, funid=0, abi=datum)
        # assert o1["gas"] == o2["gas"], (o1, o2, datum)
        assert o1["output"] == o2["output"], (o1, o2, datum)
