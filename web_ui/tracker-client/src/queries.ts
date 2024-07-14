import { gql } from '@apollo/client';

export const GET_TASK_IN_PERIOD = gql`
    query GetTasksInPeriod($startDate: DateTime!, $endDate: DateTime!) {
        tasksInPeriod(start_date: $startDate, end_date: $endDate) {
            id
            description
            start_timestamp
            finish_timestamp
            duration
        }
    }
`;