from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from calculadora.calculadoraOperadores import Calculadora

app = FastAPI()
calc = Calculadora()

class Operacao(BaseModel):
    op: str
    a: float
    b: Optional[float] = None

@app.post("/calcular")
def calcular(operacao: Operacao):
    try:
        resultado = calc.operate(operacao.op, operacao.a, operacao.b)
        return {"resultado": resultado}
    except ZeroDivisionError as zde:
        raise HTTPException(status_code=400, detail=f"Erro: {zde}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
