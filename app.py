import streamlit as st
import pandas as pd
from pipeline.bot import SqlGPT


def run_query(user_query: str):
    sqlgpt = SqlGPT()
    response = sqlgpt.get_sql_query(user_query)

    if getattr(response, "type", None) == "QUERY":
        query = response.value
        sql_result = sqlgpt.get_query_result(query)

        if isinstance(sql_result, tuple) and len(sql_result) == 3:
            executed, rows_or_error, columns = sql_result
        else:
            executed, rows_or_error = sql_result
            columns = None

        if not executed:
            return {
                "success": False,
                "sql": query,
                "error": rows_or_error,
                "output": None,
                "rows": None,
                "columns": None,
            }

        try:
            output_text = sqlgpt.get_output(rows_or_error)
        except Exception as exc:
            output_text = f"AI presentation failed: {exc}"

        return {
            "success": True,
            "sql": query,
            "error": None,
            "output": str(output_text),
            "rows": rows_or_error,
            "columns": columns,
        }

    return {
        "success": False,
        "sql": None,
        "error": getattr(response, "value", "Could not generate a SQL query."),
        "output": None,
        "rows": None,
    }


def main():
    st.set_page_config(page_title="Gen AI SQL Frontend", page_icon="🧠", layout="wide")
    st.title("Gen AI SQL Assistant")
    st.write(
        "Enter a question about the `students` table, and the app will generate SQL, run it against MySQL, and show the result."
    )

    with st.expander("About this app"):
        st.markdown(
            """
            - The app uses the `pipeline` package to generate SQL from natural language.
            - It executes the SQL against the configured MySQL database.
            - It presents both the generated SQL and the query results.
            """
        )

    user_query = st.text_area("Your question", height=180)
    run_button = st.button("Generate SQL and Run")

    if run_button:
        if not user_query.strip():
            st.warning("Please enter a question before running the query.")
            return

        with st.spinner("Generating SQL and executing query..."):
            result = run_query(user_query)

        if result["error"]:
            st.error(result["error"])

        if result["sql"]:
            st.subheader("Generated SQL")
            st.code(result["sql"])

        if result["success"] and result["rows"] is not None:
            st.subheader("Query Results")
            try:
                df = pd.DataFrame(result["rows"], columns=result.get("columns"))
                if not df.empty:
                    st.dataframe(df)
                else:
                    st.info("Query executed successfully but returned no rows.")
            except Exception:
                st.write(result["rows"])

        if result["output"]:
            st.subheader("AI Presentation")
            st.write(result["output"])

    st.sidebar.header("Configuration")
    st.sidebar.markdown(
        """
        Set your MySQL credentials in a `.env` file or environment variables.

        - `MYSQL_HOST` or `DB_HOST`
        - `MYSQL_PORT` or `DB_PORT`
        - `MYSQL_USER`
        - `MYSQL_PASSWORD`
        - `MYSQL_DATABASE` or `DB_NAME`
        """
    )


if __name__ == "__main__":
    main()
