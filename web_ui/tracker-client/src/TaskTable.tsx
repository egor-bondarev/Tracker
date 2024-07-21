// TasksTable.tsx
// import 'react-datepicker/dist/react-datepicker.css';

import Datetime from 'react-datetime';
import 'react-datetime/css/react-datetime.css';
import CustomInputDateTime from './InputDateField';
import React, { useState, useRef, useEffect, ChangeEvent } from 'react';
import { Moment } from 'moment';
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

  const [selectedStartDateTime, setSelectedStartDateTime] = useState<string | Date | Moment | undefined>();
  const [inputStartValue, setInputStartValue] = useState<string>('');
  const [isStartPickerOpen, setIsStartPickerOpen] = useState<boolean>(false);
  const startDatePickerRef = useRef<HTMLInputElement>(null);

  const [selectedFinishDateTime, setSelectedFinishDateTime] = useState<string | Date | Moment | undefined>();
  const [inputFinishValue, setInputFinishValue] = useState<string>('');
  const [isFinishPickerOpen, setIsFinishPickerOpen] = useState<boolean>(false);
  const finishDatePickerRef = useRef<HTMLInputElement>(null);

  const containerStartDateRef = useRef<HTMLDivElement>(null);
  const containerFinishDateRef = useRef<HTMLDivElement>(null);

  function handleStartDateChange(date: string | Moment){
    setSelectedStartDateTime(date);
    setInputStartValue(date.toString());
  };

  const handleFinishDateChange = (date: string | Moment) => {
    setSelectedFinishDateTime(date);
    setInputFinishValue(date.toString());
  };

  const handleInputStartChange = (event: ChangeEvent<HTMLInputElement>) => {
    setInputStartValue(event.target.value);
  };

  const handleInputFinishChange = (event: ChangeEvent<HTMLInputElement>) => {
    setInputFinishValue(event.target.value);
  };

  function openStartDateCalendar() {
    setIsStartPickerOpen(true);
  };
  function openFinishDateCalendar() {
    setIsFinishPickerOpen(true);
  };

  function closeStartDateCalendar() {
    setIsStartPickerOpen(false);
  };
  function closeFinishDateCalendar() {
    setIsFinishPickerOpen(false);
  };

  function handleClickOutside(event: MouseEvent) {
    if (containerStartDateRef.current && !containerStartDateRef.current.contains(event.target as Node)) {
      closeStartDateCalendar();
    }
    if (containerFinishDateRef.current && !containerFinishDateRef.current.contains(event.target as Node)) {
      closeFinishDateCalendar();
    }
  };

  const handleFetchTasks = () => {
    fetchGraphQLData();
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const updatePickerPosition = (inputRef: React.RefObject<HTMLInputElement>, pickerClass: string) => {
    if (inputRef.current) {
      const inputRect = inputRef.current.getBoundingClientRect();
      const pickerElement = document.querySelector(`.${pickerClass}`) as HTMLElement;
      if (pickerElement) {
        pickerElement.style.position = 'absolute';
        pickerElement.style.top = `${inputRect.bottom + window.scrollY}px`;
        pickerElement.style.left = `${inputRect.left + window.scrollX}px`;
      }
    }
  };

  return (
    <div>
      <div className='App-page-result-settings'>
        <div className='App-page-result-settings-search'>
          <div ref={containerStartDateRef} style={{ position: 'relative' }}>
            <Datetime
              value={selectedStartDateTime}
              onChange={handleStartDateChange}
              renderInput={(props, openCalendar) => (
                <CustomInputDateTime
                  value={inputStartValue}
                  onClick={openStartDateCalendar}
                  onChange={handleInputStartChange}
                  className='App-page-result-settings-search-input-start-date'
                  ref={startDatePickerRef}
                />
              )}
              open={isStartPickerOpen}
              className='rdtPickerStartDateTime'
            />
          </div>
          <div ref={containerFinishDateRef} style={{ position: 'relative' }}>
            <Datetime
              value={selectedFinishDateTime}
              onChange={handleFinishDateChange}
              renderInput={(props, openCalendar) => (
                <CustomInputDateTime
                  value={inputFinishValue}
                  onClick={openFinishDateCalendar}
                  onChange={handleInputFinishChange}
                  className='App-page-result-settings-search-input-finish-date'
                  ref={finishDatePickerRef}
                />
              )}
              open={isFinishPickerOpen}
              className='rdtPickerFinishDateTime'
            />
          </div>
          <div>
            <button className='App-page-result-settings-search-button' onClick={fetchGraphQLData}>Search</button>
          </div>
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
