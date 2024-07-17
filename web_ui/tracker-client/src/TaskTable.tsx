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
      <div>
        <label>
          Start Date:
          <input
            type="string"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>
        <label>
          End Date:
          <input
            type="string"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
        <button onClick={fetchGraphQLData}>Show Tasks</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Description</th>
            <th>Start Timestamp</th>
            <th>Finish Timestamp</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id}>
              <td>{task.id}</td>
              <td>{task.description}</td>
              <td>{task.startTimestamp}</td>
              <td>{task.finishTimestamp}</td>
              <td>{task.duration}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TasksTable;
