from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline.bot import SqlGPT


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    success: bool
    sql: str | None = None
    error: str | None = None
    output: str | None = None
    columns: list[str] | None = None
    rows: list[list[Any]] | None = None


app = FastAPI(title="Gen AI SQL API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest) -> QueryResponse:
    sql_gpt = SqlGPT()
    response = sql_gpt.get_sql_query(request.question)

    if getattr(response, "type", None) != "QUERY":
        return QueryResponse(
            success=False,
            error=getattr(response, "value", "Unable to generate SQL."),
        )

    query = response.value
    result = sql_gpt.get_query_result(query)

    if isinstance(result, tuple) and len(result) == 3:
        success, rows, columns = result
    elif isinstance(result, tuple) and len(result) == 2:
        success, rows = result
        columns = None
    else:
        return QueryResponse(success=False, error="Query execution returned invalid data.")

    if not success:
        return QueryResponse(success=False, sql=query, error=str(rows))

    row_list = [list(row) for row in rows]
    return QueryResponse(
        success=True,
        sql=query,
        output=str(sql_gpt.get_output(rows)),
        columns=columns,
        rows=row_list,
    )
