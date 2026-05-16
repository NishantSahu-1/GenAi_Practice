import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setResult(null)

    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      const data = await response.json()
      if (!response.ok) {
        setError(data.error || 'Request failed.')
      } else if (!data.success) {
        setError(data.error || 'Unable to execute query.')
      } else {
        setResult(data)
      }
    } catch (err) {
      setError(err.message || 'Network error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>Gen AI SQL Web App</h1>
        <p>Ask a question about the <code>students</code> table and get SQL + results.</p>
      </header>

      <main>
        <form className="query-form" onSubmit={handleSubmit}>
          <label htmlFor="question">Your question</label>
          <textarea
            id="question"
            placeholder="e.g. Show the count of students by city"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Running...' : 'Generate and Run'}
          </button>
        </form>

        {error && <div className="error-box">{error}</div>}

        {result && (
          <section className="result-panel">
            <div className="result-block">
              <h2>Generated SQL</h2>
              <pre>{result.sql}</pre>
            </div>

            <div className="result-block">
              <h2>AI Presentation</h2>
              <p>{result.output}</p>
            </div>

            {result.columns && result.rows && result.rows.length > 0 && (
              <div className="result-block">
                <h2>Query Results</h2>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {result.columns.map((column) => (
                          <th key={column}>{column}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((value, cellIndex) => (
                            <td key={cellIndex}>{String(value)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      <footer>
        <p>Run <code>uvicorn api:app --reload</code> and start this frontend with <code>npm run dev</code>.</p>
      </footer>
    </div>
  )
}

export default App
