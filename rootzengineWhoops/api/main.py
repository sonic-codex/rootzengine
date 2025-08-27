from fastapi import FastAPI
from rootzengine.core.config import RootzEngineSettings
from storage.azure import AzureBlobStorage
from storage.local import LocalStorage

app = FastAPI()
settings = RootzEngineSettings()

if settings.azure.connection_string:
    storage = AzureBlobStorage(settings.azure)
else:
    storage = LocalStorage()

@app.on_event("startup")
async def startup_event():
    # ...existing code...
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # ...existing code...
    pass