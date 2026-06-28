import math
from pydantic import BaseModel, field_validator
from typing import Optional, Literal


class TVMProblem(BaseModel):
    pv: Optional[float] = None
    fv: Optional[float] = None
    i: Optional[float] = None
    n: Optional[int] = None
    pmt: Optional[float] = None
    solve_for: Literal["pv", "fv", "i", "n", "pmt"]

    @field_validator('i')
    @classmethod
    def check_rate(cls, v):
        if v is not None and v > 1:
            raise ValueError(
                f"i={v} looks like a percentage — "
                f"pass as decimal (e.g. 0.06 not 6)"
            )
        return v

    @field_validator('n')
    @classmethod
    def check_n(cls, v):
        if v is not None and v <= 0:
            raise ValueError(
                f"n={v} must be a positive integer"
            )
        return v


def solve_pv(fv: float, i: float, n: int) -> dict:
    """
    Call this to find Present Value given FV, i, n.
    Formula: PV = FV * (1+i)^-n
    """
    try:
        pv = fv * (1 + i) ** (-n)
        return {"result": {"pv": round(pv, 2)}}
    except Exception as e:
        return {"error": str(e)}


def solve_fv(pv: float, i: float, n: int) -> dict:
    """
    Call this to find Future Value given PV, i, n.
    Formula: FV = PV * (1+i)^n
    """
    try:
        fv = pv * (1 + i) ** n
        return {"result": {"fv": round(fv, 2)}}
    except Exception as e:
        return {"error": str(e)}


def solve_i(pv: float, fv: float, n: int) -> dict:
    """
    Call this to find effective interest rate given PV, FV, n.
    Formula: i = (FV/PV)^(1/n) - 1
    """
    try:
        i = (fv / pv) ** (1 / n) - 1
        return {"result": {"i": round(i, 6),
                           "i_percent": round(i * 100, 4)}}
    except Exception as e:
        return {"error": str(e)}


def solve_n(pv: float, fv: float, i: float) -> dict:
    """
    Call this to find number of periods given PV, FV, i.
    Formula: n = ln(FV/PV) / ln(1+i)
    """
    try:
        n = math.log(fv / pv) / math.log(1 + i)
        return {"result": {"n": round(n, 4)}}
    except Exception as e:
        return {"error": str(e)}


def force_of_interest(i: float) -> dict:
    """
    Call this to convert effective rate i to force of interest delta.
    Formula: delta = ln(1+i)
    """
    try:
        delta = math.log(1 + i)
        return {"result": {"delta": round(delta, 6),
                           "i_input": i}}
    except Exception as e:
        return {"error": str(e)}


def rate_conversion(i_nominal: float, m: int,
                    convert_to: str) -> dict:
    """
    Call this to convert between nominal and effective rates.
    i_nominal: nominal rate as decimal
    m: compounding frequency per year
    convert_to: "effective" or "force"
    """
    try:
        i_eff = (1 + i_nominal / m) ** m - 1
        if convert_to == "effective":
            return {"result": {
                "i_effective": round(i_eff, 6),
                "i_effective_percent": round(i_eff * 100, 4)
            }}
        elif convert_to == "force":
            delta = math.log(1 + i_eff)
            return {"result": {
                "i_effective": round(i_eff, 6),
                "delta": round(delta, 6)
            }}
        else:
            return {"error": "convert_to must be "
                             "'effective' or 'force'"}
    except Exception as e:
        return {"error": str(e)}
