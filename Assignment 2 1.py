#Taha Ahmed Siddiqui
#2019509

class LR1Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.non_terminals = set()
        self.terminals = set()
        self.lr1_items = []
        self.action = {}
        self.goto_table = {}  # Renamed from goto
        self.start_symbol = grammar[0][0]
        self.build_lr1_items()
        self.build_lr1_parsing_table()

    def closure(self, item_set):
        """
        Compute the closure of a LR(1) item set.
        """
        closure = item_set[:]
        i = 0
        while i < len(closure):
            item = closure[i]
            dot_pos = item[1].index(".")
            if dot_pos == len(item[1]) - 1:
                i += 1
                continue
            next_symbol = item[1][dot_pos + 1]
            if next_symbol in self.non_terminals:
                for production in self.grammar:
                    if production[0] == next_symbol:
                        lookaheads = set(item[2])
                        for j in range(dot_pos + 2, len(item[1])):
                            if item[1][j] in self.terminals:
                                lookaheads.add(item[1][j])
                        for lookahead in lookaheads:
                            new_item = (
                                next_symbol, ["."] + production[1], lookahead)
                            if new_item not in closure:
                                closure.append(new_item)
            i += 1
        return closure

    def goto(self, item_set, symbol):
        """
        Compute the Goto operation for a LR(1) item set and a symbol.
        """
        new_item_set = []
        for item in item_set:
            dot_pos = item[1].index(".")
            if dot_pos < len(item[1]) - 1 and item[1][dot_pos + 1] == symbol:
                new_item = (item[0], item[1][:dot_pos] +
                            symbol + "." + item[1][dot_pos + 2:], item[2])
                new_item_set.append(new_item)

        if len(new_item_set) == 0:
            return None
        else:
            return self.closure(new_item_set)

    def build_lr1_items(self):
        start_rule = self.grammar[0]
        start_item = (start_rule[0], ["."] + start_rule[1], "$")
        self.lr1_items.append(self.closure([start_item]))

        i = 0
        while i < len(self.lr1_items):
            current_item_set = self.lr1_items[i]
            for symbol in self.non_terminals.union(self.terminals):
                next_item_set = self.goto(current_item_set, symbol)
                if next_item_set and next_item_set not in self.lr1_items:
                    self.lr1_items.append(next_item_set)

            i += 1

        for i, item_set in enumerate(self.lr1_items):
            self.lr1_items[i] = {"index": i, "items": item_set}

    def build_lr1_parsing_table(self):
        for item_set in self.lr1_items:
            for item in item_set["items"]:
                dot_index = item[1].index(".")
                if dot_index < len(item[1]) - 1:
                    next_symbol = item[1][dot_index + 1]
                    if next_symbol in self.grammar[1]:
                        goto_index = self.get_goto_index(
                            item_set["index"], next_symbol)
                        if goto_index is not None:
                            self.goto_table[(
                                item_set["index"], next_symbol)] = goto_index
                    else:
                        if (item_set["index"], next_symbol) not in self.action:
                            self.action[(item_set["index"], next_symbol)] = []
                        self.action[(item_set["index"], next_symbol)].append(
                            "s" + str(item_set["index"]))
                elif item[0] != self.start_symbol:
                    for follow_symbol in item[2]:
                        if (item_set["index"], follow_symbol) not in self.action:
                            self.action[(item_set["index"],
                                         follow_symbol)] = []
                        self.action[(item_set["index"], follow_symbol)].append(
                            "r" + str(self.grammar.index((item[0], item[1]))))

        for i, item_set in enumerate(self.lr1_items):
            for item in item_set["items"]:
                if item[0] == self.start_symbol and item[1][-1] == ".":
                    if (item_set["index"], "$") not in self.action:
                        self.action[(item_set["index"], "$")] = []
                    self.action[(item_set["index"], "$")].append("acc")

    def get_goto_index(self, item_set_index, symbol):
        for item_set in self.lr1_items:
            if (item_set["index"], symbol) in self.goto_table and item_set_index == self.goto_table[(item_set["index"], symbol)]:
                return item_set["index"]
        return None

    def parse(self, input_string):
        stack = [0]
        input_string += "$"
        current_input = input_string[0]
        i = 0
        output = []
        while True:
            state = stack[-1]
            if (state, current_input) in self.action:
                action = self.action[(state, current_input)][0]
                if action.startswith("s"):
                    stack.append(int(action[1:]))
                    i += 1
                    current_input = input_string[i]
                    output.append(
                        {"stack": stack.copy(), "input": current_input, "action": action, "output": None})
                elif action.startswith("r"):
                    production = self.grammar[int(action[1:])]
                    for _ in range(len(production[1])):
                        stack.pop()
                    state = stack[-1]
                    stack.append(self.goto_table[(state, production[0])])
                    output.append({"stack": stack.copy(
                    ), "input": current_input, "action": action, "output": production})
                elif action == "acc":
                    output.append(
                        {"stack": stack.copy(), "input": current_input, "action": action, "output": None})
                    break
            else:
                raise Exception(
                    "LR(1) Parsing Error: No action found for state {state} and symbol {current_input}")
        return output


# Example grammar
grammar = [
    # Non-terminal symbols and their production rules
    {
        'E': [['T', 'E1']],
        'E1': [['+', 'T', 'E1'], ['']],
        'T': [['F', 'T1']],
        'T1': [['*', 'F', 'T1'], ['']],
        'F': [['(', 'E', ')'], ['id']],
    },
    # Terminal symbols
    ['id']
]


# Create the grammar
grammar = [
    ("E", ["T", "-", "E"]),
    ("E", ["T"]),
    ("T", ["F", "*", "T"]),
    ("T", ["F"]),
    ("F", ["id"])
]

lr1_parser = LR1Parser(grammar)
print("Sets of LR(1) items:")
for item_set in lr1_parser.lr1_items:
    print("Item Set", item_set["index"])
    for item in item_set["items"]:
        print(item[0] + " -> " + " ".join(item[1]) + ", " + ", ".join(item[2]))

print("\nLR(1) parsing table:")
print("Action:")
for key, value in lr1_parser.action.items():
    print("({}, {}) -> {}".format(key[0], key[1], ", ".join(value)))

print("\nGoto:")
# Call the function with required arguments to get the dictionary object
goto_dict = lr1_parser.goto(
    lr1_parser.action.keys(), lr1_parser.action.values())

# Iterate over key-value pairs in goto_dict
for key, value in goto_dict.items():
    print("({}, {}) -> {}".format(key[0], key[1], value))

input_str = "a b c d"
success, output = lr1_parser.parse(input_str)
if success:
    print("\nParsing of the string \"{}\" using the LR(1) parser:".format(input_str))
    print("Updated Stack: ", lr1_parser.stack)
    print("Current Input: ", lr1_parser.current_input)
    print("Operation: Accept")
else:
    print("\nParsing of the string \"{}\" using the LR(1) parser:".format(input_str))
    print("Updated Stack: ", lr1_parser.stack)
    print("Current Input: ", lr1_parser.current_input)
    print("Operation: Error")
    print("Output: ", output)
