import { check } from 'k6';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js'
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: 1,
    duration: '1s',
    thresholds: {
        http_req_failed: ['rate<0.01'],
        http_req_duration: ['p(95)<200'],
    },
};

export function setup() {
    const url = `http://${__ENV.HOST}:${__ENV.PORT}/sample/add2db/`;
    const username = uuidv4()
    const payload = JSON.stringify({
        username: username
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const res = http.post(url, payload, params);
    
    check(res, {
        'is status 200': (r) => r.status === 200,
    });

    return username
}

export default function (username) {
    const url = `http://${__ENV.HOST}:${__ENV.PORT}/sample/${username}/`;


    const res = http.get(url);
    
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
    sleep(1)
}