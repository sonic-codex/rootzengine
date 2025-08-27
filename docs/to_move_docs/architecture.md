# Architecture Overview

The RootzEngine project is designed with a modular architecture to ensure scalability and maintainability.

## Components

### API Service
- **Description**: Handles incoming requests and routes them to the appropriate services.
- **Technology**: FastAPI

### Analysis Worker
- **Description**: Processes data and performs analysis tasks.
- **Technology**: Python, TensorFlow

### Storage
- **Description**: Manages data storage and retrieval.
- **Technology**: Azure Blob Storage

## Data Flow
1. Client sends a request to the API service.
2. API service validates the request and forwards it to the analysis worker.
3. Analysis worker processes the data and stores the results in Azure Blob Storage.
4. API service retrieves the results and sends them back to the client.
