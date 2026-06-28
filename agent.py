import json
import os
from google import genai
from google.genai import types
from tvm_tools import (
    solve_pv, solve_fv, solve_i, solve_n,
    force_of_interest, rate_conversion,
    TVMProblem
)
from pydantic import ValidationError

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are a precise SOA FM / IAI CM1 exam TVM solver agent.

Your job has TWO steps only:
STEP 1 - Extract parameters from the user's question as JSON.
STEP 2 - After receiving the calculation result, explain it 
clearly using FM notation.

EXTRACTION RULES:
- Always express rates as decimals (0.06 not 6%)
- Always express n in periods (not years unless period = year)
- Return ONLY valid JSON in Step 1. No prose. No markdown.
- solve_for must be one of: pv, fv, i, n, delta, nominal_to_effective

JSON format for Step 1:
{
  "solve_for": "pv",
  "pv": null,
  "fv": 10000,
  "i": 0.06,
  "n": 5,
  "pmt": null,
  "i_nominal": null,
  "m": null,
  "convert_to": null
}

EXPLANATION RULES (Step 2):
- Use SOA FM notation: i, δ, v, PV, FV, n
- Show the formula first
- Show the calculation
- Give the final answer clearly
- Keep it under 150 words
""".strip()


def extract_params(user_query: str) -> dict:
    """Ask Gemini to extract TVM parameters as JSON."""
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=f"Extract TVM parameters as JSON: {user_query}"
    )
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def explain_result(user_query: str,
                   params: dict,
                   result: dict) -> str:
    """Ask Gemini to explain the result in FM notation."""
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=(
            f"User asked: {user_query}\n"
            f"Parameters extracted: {params}\n"
            f"Python solver result: {result}\n"
            f"Now explain this result clearly "
            f"using FM notation."
        )
    )
    return response.text.strip()


def route_and_solve(params: dict) -> dict:
    """Route to correct Python solver based on solve_for."""
    solve_for = params.get("solve_for", "")

    try:
        if solve_for == "pv":
            problem = TVMProblem(
                fv=params.get("fv"),
                i=params.get("i"),
                n=params.get("n"),
                solve_for="pv"
            )
            return solve_pv(problem.fv, problem.i, problem.n)

        elif solve_for == "fv":
            problem = TVMProblem(
                pv=params.get("pv"),
                i=params.get("i"),
                n=params.get("n"),
                solve_for="fv"
            )
            return solve_fv(problem.pv, problem.i, problem.n)

        elif solve_for == "i":
            problem = TVMProblem(
                pv=params.get("pv"),
                fv=params.get("fv"),
                n=params.get("n"),
                solve_for="i"
            )
            return solve_i(problem.pv, problem.fv, problem.n)

        elif solve_for == "n":
            problem = TVMProblem(
                pv=params.get("pv"),
                fv=params.get("fv"),
                i=params.get("i"),
                solve_for="n"
            )
            return solve_n(problem.pv, problem.fv, problem.i)

        elif solve_for == "delta":
            return force_of_interest(params.get("i"))

        elif solve_for == "nominal_to_effective":
            return rate_conversion(
                i_nominal=params.get("i_nominal"),
                m=params.get("m"),
                convert_to=params.get("convert_to",
                                      "effective")
            )

        else:
            return {"error": f"Unknown solve_for: {solve_for}"}

    except ValidationError as e:
        return {"error": str(e)}


def run_agent(user_query: str) -> str:
    """
    Full pipeline:
    1. Extract params from query
    2. Validate with Pydantic
    3. Solve with Python
    4. Explain with Gemini
    """
    try:
        # Step 1: Extract
        params = extract_params(user_query)

        # Step 2 & 3: Validate + Solve
        result = route_and_solve(params)

        # Step 4: Explain
        if "error" in result:
            return f"❌ Error: {result['error']}"

        explanation = explain_result(user_query,
                                     params, result)
        return explanation

    except json.JSONDecodeError:
        return ("❌ Could not parse your question. "
                "Please rephrase with clear FM values.")
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"import json
import os
from google import genai
from google.genai import types
from tvm_tools import (
    solve_pv, solve_fv, solve_i, solve_n,
    force_of_interest, rate_conversion,
    TVMProblem
)
from pydantic import ValidationError

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are a precise SOA FM / IAI CM1 exam TVM solver agent.

Your job has TWO steps only:
STEP 1 - Extract parameters from the user's question as JSON.
STEP 2 - After receiving the calculation result, explain it 
clearly using FM notation.

EXTRACTION RULES:
- Always express rates as decimals (0.06 not 6%)
- Always express n in periods (not years unless period = year)
- Return ONLY valid JSON in Step 1. No prose. No markdown.
- solve_for must be one of: pv, fv, i, n, delta, nominal_to_effective

JSON format for Step 1:
{
  "solve_for": "pv",
  "pv": null,
  "fv": 10000,
  "i": 0.06,
  "n": 5,
  "pmt": null,
  "i_nominal": null,
  "m": null,
  "convert_to": null
}

EXPLANATION RULES (Step 2):
- Use SOA FM notation: i, δ, v, PV, FV, n
- Show the formula first
- Show the calculation
- Give the final answer clearly
- Keep it under 150 words
""".strip()


def extract_params(user_query: str) -> dict:
    """Ask Gemini to extract TVM parameters as JSON."""
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=f"Extract TVM parameters as JSON: {user_query}"
    )
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def explain_result(user_query: str,
                   params: dict,
                   result: dict) -> str:
    """Ask Gemini to explain the result in FM notation."""
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=(
            f"User asked: {user_query}\n"
            f"Parameters extracted: {params}\n"
            f"Python solver result: {result}\n"
            f"Now explain this result clearly "
            f"using FM notation."
        )
    )
    return response.text.strip()


def route_and_solve(params: dict) -> dict:
    """Route to correct Python solver based on solve_for."""
    solve_for = params.get("solve_for", "")

    try:
        if solve_for == "pv":
            problem = TVMProblem(
                fv=params.get("fv"),
                i=params.get("i"),
                n=params.get("n"),
                solve_for="pv"
            )
            return solve_pv(problem.fv, problem.i, problem.n)

        elif solve_for == "fv":
            problem = TVMProblem(
                pv=params.get("pv"),
                i=params.get("i"),
                n=params.get("n"),
                solve_for="fv"
            )
            return solve_fv(problem.pv, problem.i, problem.n)

        elif solve_for == "i":
            problem = TVMProblem(
                pv=params.get("pv"),
                fv=params.get("fv"),
                n=params.get("n"),
                solve_for="i"
            )
            return solve_i(problem.pv, problem.fv, problem.n)

        elif solve_for == "n":
            problem = TVMProblem(
                pv=params.get("pv"),
                fv=params.get("fv"),
                i=params.get("i"),
                solve_for="n"
            )
            return solve_n(problem.pv, problem.fv, problem.i)

        elif solve_for == "delta":
            return force_of_interest(params.get("i"))

        elif solve_for == "nominal_to_effective":
            return rate_conversion(
                i_nominal=params.get("i_nominal"),
                m=params.get("m"),
                convert_to=params.get("convert_to",
                                      "effective")
            )

        else:
            return {"error": f"Unknown solve_for: {solve_for}"}

    except ValidationError as e:
        return {"error": str(e)}


def run_agent(user_query: str) -> str:
    """
    Full pipeline:
    1. Extract params from query
    2. Validate with Pydantic
    3. Solve with Python
    4. Explain with Gemini
    """
    try:
        # Step 1: Extract
        params = extract_params(user_query)

        # Step 2 & 3: Validate + Solve
        result = route_and_solve(params)

        # Step 4: Explain
        if "error" in result:
            return f"❌ Error: {result['error']}"

        explanation = explain_result(user_query,
                                     params, result)
        return explanation

    except json.JSONDecodeError:
        return ("❌ Could not parse your question. "
                "Please rephrase with clear FM values.")
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"
