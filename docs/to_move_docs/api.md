# API Documentation

This document provides an overview of the API endpoints available in the RootzEngine project.

## Endpoints

### GET /status
- **Description**: Returns the status of the API.
- **Response**:
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```

### POST /analyze
- **Description**: Analyzes the provided data.
- **Request Body**:
  ```json
  {
    "data": "<data-to-analyze>"
  }
  ```
- **Response**:
  ```json
  {
    "result": "<analysis-result>"
  }
  ```
