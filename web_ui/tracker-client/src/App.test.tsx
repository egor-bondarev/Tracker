import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import App from './App';

const originalFetch = global.fetch;

afterEach(() => {
  global.fetch = originalFetch;
});

test('Search sends the selected date range to GraphQL and displays the task', async () => {
  const startDate = '2026-01-01 09:00:00';
  const endDate = '2026-01-01 18:00:00';
  const task = {
    id: 1,
    description: 'Review deployment',
    startTimestamp: '2026-01-01 10:00:00',
    finishTimestamp: '2026-01-01 10:05:00',
    duration: '00:05:00',
  };
  const fetchMock = jest.fn<ReturnType<typeof fetch>, Parameters<typeof fetch>>();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ data: { tasksInPeriod: [task] } }),
  } as Response);
  global.fetch = fetchMock;

  render(<App />);
  const [startInput, endInput] = screen.getAllByRole('textbox');
  fireEvent.change(startInput, { target: { value: startDate } });
  fireEvent.change(endInput, { target: { value: endDate } });
  fireEvent.click(screen.getByRole('button', { name: 'Search' }));

  expect(await screen.findByRole('row', { name: /Review deployment.*00:05:00/ }))
    .toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledTimes(1);
  const [url, options] = fetchMock.mock.calls[0];
  expect(url).toBe('/graphql');
  expect(options?.method).toBe('POST');
  const { query, variables } = JSON.parse(options?.body as string);
  expect(query).toContain('tasksInPeriod');
  expect(variables).toEqual({ startDate, endDate });
});
