from collections import defaultdict

BLANK = '_'

def decide_0n1_03n_minimal(input_bits: str, max_steps=200_000, return_tape=False):
    # init tape with only 0/1; blanks elsewhere
    tape = defaultdict(lambda: BLANK)
    for i, ch in enumerate(input_bits):
        if ch not in ('0','1'):
            raise ValueError("Input must be over {0,1}.")
        tape[i] = ch

    steps = 0
    head = 0

    def left_boundary(h):
        # move left until blank, return that blank's index
        nonlocal steps
        while tape[h] != BLANK:
            h -= 1
            steps += 1
            if steps > max_steps: return None
        return h

    def right_boundary(h):
        # move right until blank, return that blank's index
        nonlocal steps
        while tape[h] != BLANK:
            h += 1
            steps += 1
            if steps > max_steps: return None
        return h

    # 1) Check: exactly one '1' and only 0/1 present
    # Find left blank, then move to first symbol
    lb = left_boundary(head)
    if lb is None: return ("timeout", None, steps)
    head = lb + 1
    ones = 0
    pos1 = None
    while tape[head] != BLANK:
        s = tape[head]
        if s == '1':
            ones += 1
            pos1 = head
            if ones > 1:
                # write reject bit and halt
                head = lb
                tape[head+1] = '0'
                return ("halt", 0, steps) if not return_tape else ("halt", 0, steps, tape, head)
        elif s != '0':
            head = lb
            tape[head+1] = '0'
            return ("halt", 0, steps) if not return_tape else ("halt", 0, steps, tape, head)
        head += 1
        steps += 1
        if steps > max_steps: return ("timeout", None, steps)

    if ones != 1:
        head = lb
        tape[head+1] = '0'
        return ("halt", 0, steps) if not return_tape else ("halt", 0, steps, tape, head)

    # 2) Main loop: erase one left 0, then three right 0s
    while True:
        # find a left 0 (from pos1-1 scanning left)
        h = pos1 - 1
        left_zero = None
        while tape[h] != BLANK:
            if tape[h] == '0':
                left_zero = h
                break
            h -= 1
            steps += 1
            if steps > max_steps: return ("timeout", None, steps)
        if left_zero is None:
            break  # no more left zeros

        # erase that left zero
        tape[left_zero] = BLANK

        # erase three right zeros
        erased = 0
        h = pos1 + 1
        while erased < 3:
            if tape[h] == BLANK:
                # not enough zeros on right
                head = lb
                tape[head+1] = '0'
                return ("halt", 0, steps) if not return_tape else ("halt", 0, steps, tape, head)
            if tape[h] == '0':
                tape[h] = BLANK
                erased += 1
            # if it's '1' (shouldn't be; only one 1), just skip
            h += 1
            steps += 1
            if steps > max_steps: return ("timeout", None, steps)

    # 3) verify no leftover zeros on the right
    h = pos1 + 1
    while tape[h] != BLANK:
        if tape[h] == '0':
            head = lb
            tape[head+1] = '0'
            return ("halt", 0, steps) if not return_tape else ("halt", 0, steps, tape, head)
        h += 1
        steps += 1
        if steps > max_steps: return ("timeout", None, steps)

    # 4) accept: write 1 to the cell right of the head (head sits on left boundary blank)
    head = lb
    tape[head+1] = '1'
    return ("halt", 1, steps) if not return_tape else ("halt", 1, steps, tape, head)

# Quick sanity checks (n in N, allowing n=0 so "1" should be accepted)
tests = [
    "", "0", "1", "01", "10", "001", "01000",    # 01000 is 0^1 1 0^3 -> accept
    "001000000",                                  # 0^2 1 0^6 -> accept
    "0001000000000",                              # 0^3 1 0^9 -> accept
    "00010000", "0010000", "111", "101000"       # rejects
]
for w in tests:
    status, bit, steps = decide_0n1_03n_minimal(w)
    print(f"{w!r:>12} -> {status}, out={bit}")
