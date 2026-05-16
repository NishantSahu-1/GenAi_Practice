from pydantic import BaseModel, Field

class OutputSchema(BaseModel):
    type:str=Field(description="""
                   * Type of the output. 
                   * Striclty standardize it to "QUERY" or "REMARK" """)
    value:str=Field(description="""
                    * If type is "QUERY" then provide valid Mysql query.
                    * It the type is "REMARK" then provide the short remark or feedback on the user query.
""")