import { useState, useEffect } from 'react'
import type { Summary } from './models'
import SummaryList from './summary_list'

type LoadState<T> = {
  state: 'Pending'
} | {
  state: 'Loading'
} | {
  state: 'Loaded'
  data: T
} | {
  state: 'Error'
  error: any
}

function App() {
  const [summary, setSummary] = useState<LoadState<Summary>>({ state: 'Pending' })

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setSummary({ state: 'Loading' })
        const response = await fetch('test_results/summary.json')
        const data = await response.json()
        setSummary({ state: 'Loaded', data })
      } catch (error) {
        console.error('Error loading summary.json:', error)
        setSummary({ state: 'Error', error })
      }
    }

    fetchSummary()
  }, [])

  return (
      <div className="pagecontainer">
        <h1>Simple Agent Benchmark</h1>
        <h2>What is this?</h2>
        <p>
          As AI's get better and better, benchmarking them becomes fuzzier and
          fuzzier. While in the past 'do this computation' was good enough,
          now we can give them much more abstract tasks. This page attempts
          to solve this problem by using visual benchmarks - something that
          is easy for a human to compare. This allows the agent to take
          creative license and produce a result that is observably 'good'
          rather than provably 'correct'.
        </p>
        <p>
          Technically, this project takes the form of a very very simple
          agent. The agent is just a loop that takes an initial prompt and an
          initial set of files, and then runs the AI on them, providing the
          agent with some simple tools and 100 iterations. To judge the
          results, it is expected that the test will output an index.html
          file, which will be embedded here. To aid in figuring out what is
          going on, the complete message log is also available, and can be
          viewed by clicking the 'View Message Log' link.
        </p>

        {summary.state == 'Loaded' && (
          <SummaryList tests={summary.data.tests} />
        )}

      </div>
  )
}

export default App
