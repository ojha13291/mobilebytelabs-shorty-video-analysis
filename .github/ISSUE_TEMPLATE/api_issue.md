---
name: API issue
about: Report issues with API endpoints or functionality
title: '[API] '
labels: api, bug
assignees: ''

---

**API Endpoint**
Which API endpoint is affected? (e.g., `/api/analyze`, `/health`, `/api/metrics`)

**HTTP Method**
- [ ] GET
- [ ] POST
- [ ] PUT
- [ ] DELETE
- [ ] PATCH

**Issue Type**
- [ ] 4xx Client Error
- [ ] 5xx Server Error
- [ ] Unexpected Response Format
- [ ] Missing Functionality
- [ ] Performance Issue
- [ ] Documentation Issue

**Request Details**
Please provide the request details:
```json
{
  "method": "POST",
  "url": "http://localhost:5001/api/analyze",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }
}
```

**Expected Response**
What response did you expect to receive?

**Actual Response**
What response did you actually receive?
```json
{
  "status": "error",
  "message": "..."
}
```

**Response Headers**
Include relevant response headers:
```
HTTP/1.1 500 Internal Server Error
Content-Type: application/json
```

**Error Messages**
Include any error messages from logs or response:
```
Error: ...
```

**Environment**
- Service Version: [e.g., v1.0.0]
- Deployment Method: [Docker/Local/Kubernetes]
- Configuration: [Any relevant config changes]

**Reproduction Steps**
1. Start the service with configuration X
2. Send request to endpoint Y
3. Observe the error/behavior

**Frequency**
- [ ] Always reproducible
- [ ] Intermittent issue
- [ ] Happened once

**Impact**
- [ ] Blocking development
- [ ] Blocking production use
- [ ] Minor inconvenience
- [ ] Documentation only

**Additional Context**
Any other relevant information about the API issue:

**Possible Solution**
If you have ideas on how to fix this API issue, please describe them here.

**Checklist:**
- [ ] I have provided the full request and response details
- [ ] I have included error messages and logs
- [ ] I have specified the expected vs actual behavior
- [ ] I can reproduce this issue consistently (if applicable)