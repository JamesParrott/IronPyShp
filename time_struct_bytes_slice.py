import itertools
import random
import timeit
import struct


NUM_TESTS = 5000
N = random.randint(200,5000)


lengths = [random.randint(4,32) for __ in range(N)]

cumulative_lengths = list(itertools.accumulate(lengths))

total_length = sum(lengths)

data = [bytes(random.randint(0,255) for __ in range(length)) for length in lengths]


buffer = bytearray(b"".join(data))

def unpack_via_slicing():
    start = 0
    for variable, end in zip(data, cumulative_lengths):
        assert buffer[start:end] == variable
        start = end



fmt_str = f'<{"".join(f"{length}s" for length in lengths)}'

struct_ = struct.Struct(fmt_str)

def unpack_via_struct():
    for variable, expected in zip(struct_.unpack(buffer), data):
        assert variable == expected

print(f'{N=}')
# print(f'{len(data)=}, {data[:2]=},{data[-2:]=}')

unpack_via_slicing()
unpack_via_struct()

t_slice = timeit.timeit(unpack_via_slicing, globals = globals(), number=NUM_TESTS)
t_struct = timeit.timeit(unpack_via_struct, globals = globals(), number=NUM_TESTS)

print(f'{t_slice=}')
print(f'{t_struct=}')