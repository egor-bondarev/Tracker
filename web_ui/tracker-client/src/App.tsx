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
    <div className="App">
      <header className="App-header">
        <h1>Task Tracker</h1>
        <TasksTable />
      </header>
    </div>
  );
};

export default App;