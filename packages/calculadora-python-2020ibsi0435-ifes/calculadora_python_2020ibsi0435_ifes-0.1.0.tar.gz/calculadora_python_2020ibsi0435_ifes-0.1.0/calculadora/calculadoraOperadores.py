import math

class Calculadora:
    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Divisão por zero.")
        return a / b

    def sqrt(self, a: float) -> float:
        if a < 0:
            raise ValueError("Raiz de número negativo não permitida.")
        return math.sqrt(a)

    def operate(self, op: str, a: float, b: float = None) -> float:
        if not hasattr(self, op):
            raise ValueError(f"Operação '{op}' não suportada")
        method = getattr(self, op)
        if op == "sqrt":
            return method(a)
        if b is None:
            raise ValueError(f"Operação '{op}' requer dois operandos")
        return method(a, b)
