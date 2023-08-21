class Rule:
    def __init__(self, typ: str, action = None):
        assert typ in ['move', 'rw']
        if typ == 'move':
            direction, next_state = action
            assert direction in ['L', 'C', 'R']
        self.type = typ
        self.action = action or {}

    def add_rw(self, symbol: str, action: tuple[str, str]):
        if self.type == 'move':
            raise Exception("Read/write rule conflicts with movement rule")
        if symbol in self.action and self.action[symbol] != action:
            raise Exception("Conflicting read/write rules")
        self.action[symbol] = action

    def apply(self, symbol: str) -> tuple[str, str]:
        if self.type == 'move':
            return self.action
        elif self.type == 'rw':
            return self.action.get(symbol, (None, None))
    
    def __str__(self):
        return self.type + " " + str(self.action)

class Rules:
    def __init__(self, desc: str):
        # forward rules
        self.forward: dict[str, Rule] = {}
        # reverse rules
        self.reverse: dict[str, Rule] = {}

        for line in desc.strip().split('\n'):
            if line.strip().startswith("#") or len(line.strip()) == 0:
                continue
            assert '->' in line
            lhs, rhs = [side.split(',') for side in line.replace(' ', '').split('->')]
            assert len(rhs) == 2
            if len(lhs) == 2: # Read/write rule
                state = lhs[0]
                read = lhs[1]
                write = rhs[0]
                next_state = rhs[1]

                self.forward.setdefault(state, Rule("rw")).add_rw(read, (write, next_state))
                self.reverse.setdefault(next_state, Rule("rw")).add_rw(write, (read, state))
            elif len(lhs) == 1: # Movement rule
                state = lhs[0]
                direction = rhs[0]
                next_state = rhs[1]

                if state in self.forward:
                    raise Exception(f"Conflicting movement rule detected: {line}")
                self.forward[state] = Rule("move", (direction, next_state))

                rev_direction = 'R' if direction == 'L' else 'L' if direction == 'R' else 'C'
                if next_state in self.reverse and self.reverse[next_state].action != (rev_direction, state):
                    raise Exception(f"Conflicting reverse movement rule detected: {line}")
                self.reverse[next_state] = Rule("move", (rev_direction, state))
        
    def __str__(self):
        return "Forward:\n" + "\n".join([str(key) + "->" + str(value) for key, value in self.forward.items()]) + \
            "\nReverse:\n" + "\n".join([str(key) + "->" + str(value) for key, value in self.reverse.items()])


class TuringMachine:
    def __init__(self, rules: Rules, tape: dict[int, int], initial_state: str):
        assert isinstance(rules, Rules)
        self.rules = rules
        self.tape = tape.copy()
        self.state = initial_state
        self.head_loc = 0
        self.halted = False
    
    def apply_rule(self, rules: Rules) -> bool:
        if self.state not in rules: # HALT
            self.halted = True
            return True
        action, next_state = rules[self.state].apply(self.tape.get(self.head_loc, '_'))
        if next_state == None: # HALT
            self.halted = True
            return True
        
        if rules[self.state].type == 'move':
            if action == 'L':
                self.head_loc -= 1
            elif action == 'R':
                self.head_loc += 1
        else:
            self.tape[self.head_loc] = action

        self.state = next_state
        return False

    def forward(self) -> bool:
        return self.apply_rule(self.rules.forward)
    
    def reverse(self) -> bool:
        return self.apply_rule(self.rules.reverse)

def binary_string(n: int, bits: int) -> str:
    return ''.join([str((n >> k) & 1) for k in range(bits-1, -1, -1)])

def longest_computation_path(tm_rules: Rules, initial_state:str, input_length: int) -> int:
    print('finding longest computation path of Turing machine, may take forever (google "Halting Problem")')
    longest = 0
    for inp in range(2 ** input_length):
        bstr = binary_string(inp, bits=input_length)
        tm = TuringMachine(tm_rules, {i:c for i, c in enumerate(bstr)}, initial_state)
        timer = 0
        while not tm.forward():
            timer += 1
        longest = max(longest, timer)
    return longest