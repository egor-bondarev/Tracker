"""Report Tracker availability without writing any application data."""

import argparse
import json
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request(url, timeout, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {} if data is None else {"Content-Type": "application/json"}
    with urlopen(Request(url, data=data, headers=headers), timeout=timeout) as response:
        return response.read(65536)


def check_tracker(web_url, record_url, timeout=3):
    web_url = web_url.rstrip("/")
    record_url = record_url.rstrip("/")
    checks = []

    def check(name, url, accepts, failure, payload=None):
        try:
            body = request(url, timeout, payload)
            if not accepts(body):
                raise ValueError(failure)
        except HTTPError as exc:
            detail = f"HTTP {exc.code}"
        except (URLError, OSError, HTTPException):
            detail = "Connection failed or timed out"
        except ValueError:
            detail = failure
        else:
            checks.append({"name": name, "ok": True})
            return
        checks.append({"name": name, "ok": False, "detail": detail})

    def analytics_ok(body):
        result = json.loads(body)
        return (
            isinstance(result, dict)
            and not result.get("errors")
            and isinstance(result.get("data"), dict)
            and isinstance(result["data"].get("tasksInPeriod"), list)
        )

    check("web", web_url + "/", lambda body: b'id="root"' in body,
          "Tracker page was not found")
    check("analytics_db", web_url + "/graphql", analytics_ok,
          "GraphQL did not return a task list", {
              "query": (
                  '{ tasksInPeriod(startDate: "2100-01-01 00:00:00", '
                  'endDate: "2100-01-01 00:00:01") { id } }'
              )
          })
    check("record_db", record_url + "/ready",
          lambda body: json.loads(body) == {"status": "ready"},
          "Record API did not report readiness")
    check("record_proxy", web_url + "/api/ready",
          lambda body: json.loads(body) == {"status": "ready"},
          "Record API is not reachable through the web address")
    return {"ok": all(item["ok"] for item in checks), "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web-url", default="http://127.0.0.1:8080")
    parser.add_argument("--record-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=3, help="HTTP timeout in seconds")
    args = parser.parse_args()
    if not 0 < args.timeout < float("inf"):
        parser.error("--timeout must be a finite positive number")
    result = check_tracker(args.web_url, args.record_url, args.timeout)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
