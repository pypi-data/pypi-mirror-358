import sys
from enum import Enum
import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from claire_sensor.operations import Operations
from claire_sensor.protocol import Protocol

logger = logging.getLogger(__name__)
logging.basicConfig(
    # filename='claire-sensor.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
            logging.FileHandler("claire-sensor.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
)

app = FastAPI()

ops = Operations()

class MessagingOperation(str, Enum):
    send = "send"
    receive = "receive"
    check = "check"

@app.get("/")
async def root():
    return {"message": "Hello World from Claire-sensor agent"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

@app.get("/help", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/operations")
async def provide_operations():
    msg = f"See possible operations: {MessagingOperation.send}, {MessagingOperation.receive}, {MessagingOperation.check}"
    return {"message": msg}

@app.get("/operations/{operation}")
async def get_model(operation: MessagingOperation, address: str, msg_count: int = 0, protocol: Protocol = Protocol.AMQP):
    if operation is MessagingOperation.send:
        log_msg = f"Sending {msg_count} messages to {address}"
        logger.info(log_msg)
        result = ops.send_messages(protocol, address, msg_count)
        logger.info(f"Finished sending messages. ecode: {result}")
        return {"operation": operation, "message": log_msg, "address": address, "count": msg_count,
                "ecode": result.returncode, "stderr": result.stderr, "stdout": result.stdout}

    if operation.value == MessagingOperation.receive:
        log_msg = f"Receiving {msg_count} messages from {address}"
        logger.info(log_msg)
        result = ops.receive_messages(protocol, address, msg_count)
        logger.info(f"Finished receiving messages. ecode: {result}")
        return {"operation": operation, "message": log_msg, "address": address, "count": msg_count,
                "ecode": result.returncode, "stderr": result.stderr, "stdout": result.stdout}

    log_msg = f"Checking address {address} for expected message count"
    logger.info(log_msg)
    return {"operation": operation, "message": log_msg, "address": address, "expected_count": msg_count}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    # create file /tmp/xxx & return content of it
    # use in URL "//" to get leading "/" in path
    content = ""
    with open("/tmp/xxx", "w") as file:
        file.write("Hello, this is some text written to a file!\n")
        file.write("Another line here.\n")

    with open(file_path, "r") as file:
        content = file.read()
    return {"file_path": file_path, "content": content}



# Optional CLI launcher
def run():
    import uvicorn
    uvicorn.run("claire_sensor.main:app", host="0.0.0.0", port=8123)