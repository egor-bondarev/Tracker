"""Smoke test for a disposable stack only: creates a task, then verifies persistence."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from http.client import HTTPException
import os
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

RECORD = os.getenv('SMOKE_RECORD_URL', 'http://127.0.0.1:8000')
ANALYTICS = os.getenv('SMOKE_ANALYTICS_URL', 'http://127.0.0.1:8001')
WEB = os.getenv('SMOKE_WEB_URL')
MARKER = 'deployment-smoke-persistence'


def request(url, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    with urlopen(Request(url, data=data, headers={'Content-Type': 'application/json'}), timeout=5) as response:
        return json.load(response)


def wait_for_api(url):
    for attempt in range(30):
        try:
            request(url + '/openapi.json')
            return
        except (URLError, OSError, HTTPException):
            if attempt == 29:
                raise
            time.sleep(2)


def verify():
    result = request((WEB or ANALYTICS) + '/graphql', {'query': '''{
        tasksInPeriod(startDate: "2000-01-01", endDate: "2100-01-01") {
            id description duration
        }
    }'''})
    assert not result.get('errors'), result
    matches = [task for task in result['data']['tasksInPeriod'] if task['description'] == MARKER]
    assert len(matches) == 1, result
    assert matches[0]['duration'] == '00:05:00', result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['create', 'verify'])
    args = parser.parse_args()
    wait_for_api(RECORD)
    wait_for_api(ANALYTICS)
    if WEB:
        with urlopen(WEB, timeout=5) as response:
            assert b'id="root"' in response.read(), 'Tracker page is missing the React root'
        assert request(WEB + '/api/ready') == {'status': 'ready'}, 'Record API is not proxied'
    if args.phase == 'create':
        start = (datetime.now(timezone.utc) + timedelta(days=1)).replace(tzinfo=None, microsecond=0)
        task = request(RECORD + '/add-record/new/?is_task_finished=false', {
            'description': MARKER, 'timestamp': start.isoformat(),
        })
        result = request(RECORD + '/add-record/finish/', {
            'id': task['id'], 'timestamp': (start + timedelta(minutes=5)).isoformat(),
        })
        assert result['duration'] == '00:05:00', result
    verify()
    print(f'Deployment smoke {args.phase}: passed')
