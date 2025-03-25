import re
import operator

DEBUG_MODE = False  # Set to False to hide debug output

# Tokenizer
def tokenize(expression):
    tokens = []
    i = 0
    while i < len(expression):
        char = expression[i]

        if char.isspace():
            i += 1
            continue

        # Numbers
        if char.isdigit() or (char == '.' and i + 1 < len(expression) and expression[i + 1].isdigit()):
            num_str = ''
            while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                num_str += expression[i]
                i += 1
            tokens.append(('NUMBER', float(num_str)))
            continue

        # Multi-char operators
        if i + 1 < len(expression):
            two_char = expression[i:i+2]
            if two_char in ['==', '!=', '<=', '>=']:
                tokens.append(('OPERATOR', two_char))
                i += 2
                continue

        # Keywords (true, false, and, or)
        if char.isalpha():
            ident = ''
            while i < len(expression) and expression[i].isalpha():
                ident += expression[i]
                i += 1
            ident_lower = ident.lower()
            if ident_lower == 'true':
                tokens.append(('BOOLEAN', True))
            elif ident_lower == 'false':
                tokens.append(('BOOLEAN', False))
            elif ident_lower in ['and', 'or']:
                tokens.append(('OPERATOR', ident_lower))
            else:
                raise SyntaxError(f"Unknown keyword '{ident}'")
            continue

        # Single-char operators
        if char in '+-*/()<>!%^':
            tokens.append(('OPERATOR', char))
            i += 1
            continue

        raise SyntaxError(f"Invalid character '{char}' in expression")
    return tokens

# Precedence table
precedence = {
    'or': 0,
    'and': 1,
    '==': 2, '!=': 2, '<': 2, '>': 2, '<=': 2, '>=': 2,
    '+': 3, '-': 3,
    '*': 4, '/': 4, '%': 4,
    '^': 5,
    '!': 6
}

# Infix to postfix conversion
def infix_to_postfix(tokens):
    output = []
    stack = []
    prev_token = None

    for token_type, token_value in tokens:
        if token_type in ['NUMBER', 'BOOLEAN']:
            output.append((token_type, token_value))
        elif token_type == 'OPERATOR':
            if token_value == '(':
                stack.append(token_value)
            elif token_value == ')':
                while stack and stack[-1] != '(':
                    output.append(('OPERATOR', stack.pop()))
                if not stack:
                    raise SyntaxError("Mismatched parentheses")
                stack.pop()
            else:
                if token_value == '-' and (prev_token is None or prev_token[0] == 'OPERATOR'):
                    output.append(('NUMBER', -1.0))
                    stack.append('*')
                elif token_value == '!' and (prev_token is None or prev_token[0] == 'OPERATOR'):
                    stack.append(token_value)
                else:
                    while (stack and stack[-1] != '(' and
                           precedence[token_value] <= precedence.get(stack[-1], -1)):
                        output.append(('OPERATOR', stack.pop()))
                    stack.append(token_value)
        prev_token = (token_type, token_value)

    while stack:
        if stack[-1] in '()':
            raise SyntaxError("Mismatched parentheses")
        output.append(('OPERATOR', stack.pop()))
    return output

# Operator functions
operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '%': operator.mod,
    '^': operator.pow,
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    'and': lambda a, b: a and b,
    'or': lambda a, b: a or b,
    '!': lambda a: not a
}

# Evaluation with strict type checking
def evaluate_postfix(postfix_tokens):
    stack = []
    for token in postfix_tokens:
        token_type, token_value = token

        if token_type in ['NUMBER', 'BOOLEAN']:
            stack.append(token_value)
            if DEBUG_MODE:
                print(f"[DEBUG] Push {token_value} → Stack: {stack}")

        elif token_type == 'OPERATOR':
            if token_value == '!':
                a = stack.pop()
                if type(a) is not bool:
                    raise TypeError(f"TypeError: '!' cannot operate on {type(a).__name__.upper()}")
                result = operators[token_value](a)
                if DEBUG_MODE:
                    print(f"[DEBUG] !{a} → {result}")
                stack.append(result)
            else:
                b = stack.pop()
                a = stack.pop()

                if token_value in ['+', '-', '*', '/', '%', '^']:
                    if type(a) not in [int, float] or type(b) not in [int, float]:
                        raise TypeError(
                            f"TypeError: '{token_value}' cannot operate on {type(a).__name__.upper()} and {type(b).__name__.upper()}"
                        )
                elif token_value in ['==', '!=', '<', '>', '<=', '>=']:
                    if type(a) != type(b):
                        raise TypeError(
                            f"TypeError: '{token_value}' cannot compare {type(a).__name__.upper()} and {type(b).__name__.upper()}"
                        )
                elif token_value in ['and', 'or']:
                    if type(a) is not bool or type(b) is not bool:
                        raise TypeError(
                            f"TypeError: '{token_value}' requires two BOOLEANS, got {type(a).__name__.upper()} and {type(b).__name__.upper()}"
                        )

                result = operators[token_value](a, b)
                if DEBUG_MODE:
                    print(f"[DEBUG] {a} {token_value} {b} → {result}")
                stack.append(result)
    return stack[0]

# Main loop
if __name__ == "__main__":
    while True:
        try:
            expression = input("Enter a mathematical expression (or 'exit' to quit): ")
            if expression.lower() == "exit":
                break
            tokens = tokenize(expression)
            postfix = infix_to_postfix(tokens)

            if DEBUG_MODE:
                print("[DEBUG] Tokens:", tokens)
                print("[DEBUG] Postfix:", postfix)

            result = evaluate_postfix(postfix)
            print("Result:", result)
        except Exception as e:
            print("Error:", e)
