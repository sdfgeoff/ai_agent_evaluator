import type { Message } from './llm_models';
import { MessageView } from './MessageView';
import type { TestToRun, RunStats, TestSummary } from './models';
import { Tags } from './Tags';


export const MessageLog: React.FC<{ messages: Message[] }> = ({ messages }) => {
  console.log(messages)
  return <div className="d-flex gap-1 flex-column">
    {messages.map((message, index) => (
      <MessageView message={message} key={index} />
    ))}
  </div>;
};


export const RunSummary: React.FC<{ test_to_run: TestToRun; stats: RunStats; run_summary: TestSummary }> = ({ test_to_run, stats, run_summary }) => {
  return <div>
    <div className="panel padding-2">
      <h1>{test_to_run.provider.name} {test_to_run.model.key}: {test_to_run.test_parameters.name}</h1>
    </div>
    <div className="panel-light padding-x-2 padding-y-1">
      <Tags tags={test_to_run.test_parameters.tags} />
      <p>
        {test_to_run.test_parameters.blurb}
      </p>
    </div>
    <div className="padding-2">
      <table>
        <tbody>
          <tr>
            <th>Run Date:</th>
            <td>{stats.run_date ? new Date(stats.run_date).toLocaleString() : 'N/A'}</td>
          </tr>
          <tr>
            <th>Time Taken:</th>
            <td>{stats.time_seconds.toFixed(0)} seconds</td>
          </tr>
          <tr>
            <th>Finish Reason:</th>
            <td>{stats.finish_reason || 'N/A'}</td>
          </tr>
          <tr>
            <td>&nbsp;</td>
            <td></td>
          </tr>
          <tr>
            <th>Provider:</th>
            <td>{test_to_run.provider.name}</td>
          </tr>
          <tr>
            <th>Model:</th>
            <td>{test_to_run.model.key}</td>
          </tr>

        </tbody>
      </table>
      <h2 className="padding-y-1">
        Output
      </h2>
      <div className="padding-y-1">
      <a href={`/test_results/${run_summary.output_folder}/index.html`}>Open Fullscreen</a><br/>
      <a href={`/test_results/${run_summary.output_folder}.zip`}>Download Zip</a>
      </div>
      <iframe src={`/test_results/${run_summary.output_folder}/index.html`} title="Test Output" style={{
        width: '100%',
        height: '75vh',
      }}></iframe>
      <h2 className="padding-y-1">Message Log</h2>
      <MessageLog messages={stats.log} />
    </div>

  </div>;
};
