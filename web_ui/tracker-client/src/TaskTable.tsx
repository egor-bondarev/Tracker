// TasksTable.tsx
import React, { useState } from 'react';
interface Task {
    id: number;
    description: string;
    startTimestamp: string;
    finishTimestamp: string;
    duration: string;
  }

const TasksTable: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const fetchGraphQLData = async () => {
    const query = `
      query GetTasksInPeriod($startDate: String!, $endDate: String!) {
        tasksInPeriod(startDate: $startDate, endDate: $endDate) {
          id
          description
          startTimestamp
          finishTimestamp
          duration
        }
      }
    `;

    const variables = {
      startDate: new String(startDate),
      endDate: new String(endDate),
    };

    try {
      const response = await fetch('http://0.0.0.0:8001/graphql', {
        method: 'POST',
        //mode: 'no-cors',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          variables,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      console.log(result)
      setTasks(result.data.tasksInPeriod);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleFetchTasks = () => {
    fetchGraphQLData();
  };

  return (
    <div>
      <div className='App-page-result-settings'>
      <div className='App-page-result-settings-search'>
        <input
          input-data-placeholder="true"
          placeholder="Set start date"
          className='App-page-result-settings-search-input-start-date'
          id='start-date-input'
          type="string"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
        <input
          input-data-placeholder="true"
          placeholder="Set finish date"
          className='App-page-result-settings-search-input-finish-date'
          type="string"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />
        <button className='App-page-result-settings-search-button' onClick={fetchGraphQLData}>Search</button>
      </div>
    </div>
    <div className="App-page-result-table-container">
      <table className="App-page-result-table">
        <thead>
          <tr>
            <th>Description</th>
            <th>Start Timestamp</th>
            <th>Finish Timestamp</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id}>
              <td>{task.description}</td>
              <td>{task.startTimestamp}</td>
              <td>{task.finishTimestamp}</td>
              <td>{task.duration}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </div>
    
  );
};

export default TasksTable;
