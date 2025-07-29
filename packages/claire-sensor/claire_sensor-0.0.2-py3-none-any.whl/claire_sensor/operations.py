import asyncio
import logging
import subprocess
from dataclasses import dataclass

from claire_sensor.protocol import Protocol

logger = logging.getLogger(__name__)

@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    def is_success(self) -> bool:
        return self.returncode == 0

    def summary(self) -> str:
        return f"Return code: {self.returncode}\nStdout: {self.stdout}\nStderr: {self.stderr}"


class Operations:

    @staticmethod
    def run_command_sync(cmd):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.info(f"[SYNC] Executing {cmd}")
        return CommandResult(
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr
        )

    @staticmethod
    async def run_command_async(cmd):
        logger.info(f"[ASYNC] Executing {cmd}")
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        return CommandResult(
            returncode=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )


    def send_messages(self, protocol: Protocol, address, message_count: int):
        logger.info(f"Sending {message_count} messages to {address} via {protocol}")
        # if protocol == Protocol.AMQP:
        #     pass
        cmd_data = self.run_command_sync("ls -al /tmp")
        logger.info(cmd_data.stderr)
        logger.info(cmd_data.stdout)
        return cmd_data


    def receive_messages(self, protocol, address, message_count):
        logger.info("Receiving messages")
        cmd_data = self.run_command_sync("ls -al ~")
        return cmd_data


