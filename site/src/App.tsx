import type { RunStats, Summary, TestToRun } from './models'
import SummaryList from './SummaryList'
import { RunSummary } from './RunSummary'
import { useResource } from './useResource'

function App() {
  const summary = useResource<Summary>('test_results/summary.json')
  const viewTest = new URLSearchParams(window.location.search).get('view_test')
  const stats = useResource<RunStats>(viewTest ? `test_results/${viewTest}/stats.json` : undefined)
  const testToRun = useResource<TestToRun>(viewTest ? `test_results/${viewTest}/test.json` : undefined)

  const selectedRunSummary = summary.state === 'Loaded' && viewTest
    ? summary.data.tests.find(test => test.output_folder === viewTest)
    : undefined;

  return (
    <div className="pagecontainer bg-white margin-auto">
      {!viewTest && <>
        <div className="panel padding-2">
          <h1>Simple Agent Benchmark</h1>
        </div>
        <div className="padding-2">

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
          </p></div>

        {summary.state == 'Loaded' && (
          <SummaryList tests={summary.data.tests} />
        )}
      </>}
      {summary.state == "Loaded" && testToRun.state === "Loaded" && stats.state === "Loaded" && <>
        {selectedRunSummary ? (
          <RunSummary test_to_run={testToRun.data} stats={stats.data} run_summary={selectedRunSummary} />
        ) : (
          <div className="panel padding-2">
            <h2>Test not found</h2>
            <p>The requested test does not exist or has not been run yet.</p>
          </div>
        )}
        </>}

    </div>
  )
}

export default App
