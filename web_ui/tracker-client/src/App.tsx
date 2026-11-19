import React from 'react';
import './App.css';
import TasksTable from './TaskTable';

const App: React.FC = () => {
  return (
    <div className="App-page">
      <div className="App-page-header">
        <div className="App-page-header-logo">
          <div className="App-page-header-logo-name">Task Tracker</div>
          <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@400&display=swap" rel="stylesheet"/>
        </div>
      </div>
      
      <div className="App-page-result">
        <TasksTable />
      </div>
    </div>
  );
};

export default App;