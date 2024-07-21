// TasksTable.tsx
import moment, { Moment } from 'moment';
import Datetime from 'react-datetime';
import 'react-datetime/css/react-datetime.css';
import CustomInputDateTime from './InputDateField';
import React, { useState, useRef, useEffect, ChangeEvent } from 'react';
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

  const [selectedStartDateTime, setSelectedStartDateTime] = useState<Moment | string>('');
  const [inputStartValue, setInputStartValue] = useState<string>('');
  const [isStartPickerOpen, setIsStartPickerOpen] = useState<boolean>(false);
  const startDatePickerRef = useRef<HTMLInputElement>(null);

  const [selectedFinishDateTime, setSelectedFinishDateTime] = useState<Moment | string>('');
  const [inputFinishValue, setInputFinishValue] = useState<string>('');
  const [isFinishPickerOpen, setIsFinishPickerOpen] = useState<boolean>(false);
  const finishDatePickerRef = useRef<HTMLInputElement>(null);

  const containerStartDateRef = useRef<HTMLDivElement>(null);
  const containerFinishDateRef = useRef<HTMLDivElement>(null);

  const handleStartDateChange = (date: Moment | string) => {
    if (moment.isMoment(date)) {
      setSelectedStartDateTime(date);
      setInputStartValue(date.format('YYYY-MM-DD HH:mm:00'));
    } else {
      setSelectedStartDateTime('');
      setInputStartValue('');
    }
  };

  const handleFinishDateChange = (date: Moment | string) => {
    if (moment.isMoment(date)) {
      setSelectedFinishDateTime(date);
      setInputFinishValue(date.format('YYYY-MM-DD HH:mm:00'));
    } else {
      setSelectedFinishDateTime('');
      setInputFinishValue('');
    }
  };

  const handleInputStartChange = (event: ChangeEvent<HTMLInputElement>) => {
    setInputStartValue(event.target.value);
  };

  const handleInputFinishChange = (event: ChangeEvent<HTMLInputElement>) => {
    setInputFinishValue(event.target.value);
  };

  const openStartDateCalendar = () => {
    setIsStartPickerOpen(true);
  };
  const openFinishDateCalendar = () => {
    setIsFinishPickerOpen(true);
  };

  const closeStartDateCalendar = () => {
    setIsStartPickerOpen(false);
  };
  const closeFinishDateCalendar = () => {
    setIsFinishPickerOpen(false);
  };

  const handleClickOutside = (event: MouseEvent) => {
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
              dateFormat="YYYY-MM-DD"
              timeFormat="HH:mm:00"
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
              dateFormat="DD/MM/YYYY"
              timeFormat="HH:mm"
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
