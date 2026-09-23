import ast
import operator
from datetime import datetime


class LenoTools:
    def __init__(self, web_search):
        self.web = web_search

    def calculator(self, expression):
        try:
            tree = ast.parse(
                expression,
                mode="eval"
            )

            operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow
            }

            def calculate(node):
                if isinstance(node, ast.Expression):
                    return calculate(node.body)

                if isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)):
                        return node.value
                    raise ValueError("Invalid number.")

                if isinstance(node, ast.UnaryOp):
                    value = calculate(node.operand)

                    if isinstance(node.op, ast.USub):
                        return -value

                    if isinstance(node.op, ast.UAdd):
                        return value

                    raise ValueError("Invalid unary operator.")

                if isinstance(node, ast.BinOp):
                    left = calculate(node.left)
                    right = calculate(node.right)

                    operation = operators.get(
                        type(node.op)
                    )

                    if operation is None:
                        raise ValueError(
                            "Operator not allowed."
                        )

                    return operation(left, right)

                raise ValueError("Invalid expression.")

            return str(calculate(tree))

        except Exception as error:
            return f"Calculation error: {error}"

    def current_time(self):
        return datetime.now().strftime(
            "%A, %d %B %Y, %I:%M:%S %p"
        )

    def search_web(self, query):
        return self.web.search(
            query,
            max_results=5
        )

    def execute(self, tool_name, argument):
        if tool_name == "calculator":
            return self.calculator(argument)

        if tool_name == "time":
            return self.current_time()

        if tool_name == "web_search":
            return self.search_web(argument)

        if tool_name == "action":
            return (
                "ACTION REQUEST RECEIVED: "
                + argument
                + "\n"
                "This action is recognized but the required "
                "external integration is not connected yet."
            )

        return f"Unknown tool: {tool_name}"