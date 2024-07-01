import { check } from 'k6';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js'
import http from 'k6/http';

export const options = {
    vus: 1,
    duration: '1s',
    thresholds: {
        http_req_failed: ['rate<0.01'],
        http_req_duration: ['p(95)<200'],
    },
};

export default function () {
    const url = `http://${__ENV.HOST}:${__ENV.PORT}/sample/add2db/`;
    const payload = JSON.stringify({
        username: uuidv4()
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
}