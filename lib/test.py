import ast

class CognitiveComplexityCalculator:
    def __init__(self):
        pass

    def calculate_cognitive_complexity(self, node, nesting_level=0):
        """
        Calculates the Cognitive Complexity of a given code structure represented by an abstract syntax tree (AST).
        
        :param node: AST node to analyze
        :param nesting_level: Current level of nesting (used for recursive calls)
        :return: Cognitive Complexity score
        """
        complexity = 0

        if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity += 1  # Increment for the structure itself
            if nesting_level > 0:
                complexity += nesting_level  # Increment for nesting level
            nesting_level += 1

        # Handle specific cases like 'elif', 'else', and 'except'
        if isinstance(node, ast.If):
            if hasattr(node, 'orelse') and node.orelse:
                for orelse_node in node.orelse:
                    if isinstance(orelse_node, ast.If):
                        complexity += 1  # 'elif' gets a structural increment
                    elif not isinstance(orelse_node, ast.Pass):
                        complexity += 1  # 'else' gets a hybrid increment

        if isinstance(node, ast.Try):
            if hasattr(node, 'handlers') and node.handlers:
                for handler in node.handlers:
                    complexity += 1  # Each 'except' block gets an increment

        # Recursively calculate complexity for child nodes
        for child in ast.iter_child_nodes(node):
            complexity += self.calculate_cognitive_complexity(child, nesting_level)

        return complexity

    def compute_cognitive_complexity_from_code(self, source_code):
        """
        Computes the Cognitive Complexity score from source code.
        
        :param source_code: The source code to analyze as a string
        :return: Cognitive Complexity score
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"Syntax error in the provided code: {e}")
            return None

        return self.calculate_cognitive_complexity(tree)


if __name__ == "__main__":
    # Example usage
    sample_code = """
    def example_function(x):
        if x > 0:
            for i in range(x):
                if i % 2 == 0:
                    print(i)
                else:
                    print(-i)
        else:
            try:
                raise ValueError("x must be positive")
            except ValueError as e:
                print(e)
    """

    calculator = CognitiveComplexityCalculator()
    complexity_score = calculator.compute_cognitive_complexity_from_code(sample_code)
    print(f"Cognitive Complexity: {complexity_score}")
