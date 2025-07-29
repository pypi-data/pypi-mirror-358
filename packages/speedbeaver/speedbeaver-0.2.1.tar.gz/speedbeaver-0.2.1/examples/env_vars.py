import os

from speedbeaver.handlers import LogTestSettings

os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("STREAM__JSON_LOGS", "YES")
os.environ.setdefault("LOGGER_NAME", "env-var-app")

import uvicorn
from fastapi import FastAPI

import speedbeaver

app = FastAPI()
# Note: The test settings are mostly for our integration tests
speedbeaver.quick_configure(
    app, test=LogTestSettings(file_name="env_vars.test.log")
)

logger = speedbeaver.get_logger()


@app.get("/")
async def index():
    await logger.ainfo("I should be a secret!", log_tag="hidden")
    await logger.awarning(
        "This should be the only thing you see!", log_tag="visible"
    )
    return {"message": "Testing environment variables."}


if __name__ == "__main__":
    uvicorn.run(app)
