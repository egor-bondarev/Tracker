import React, { useState, ChangeEvent } from 'react';
import { ApolloProvider, useQuery } from '@apollo/client';
import client from './apollo-client';
import { GET_TASK_IN_PERIOD } from './queries';
import logo from './logo.svg';
import './App.css';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
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