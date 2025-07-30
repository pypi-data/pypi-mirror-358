import pika
import json
from pika.channel import Channel
from agentsociety.chat.history import History, HistoryDelta, HistoryContent, Actor, ContentType, HistoryArtifact
from agentsociety.chat.artifact import TaskArtifacts, TaskArtifact
from agentsociety.chat.box.free_flow_graph import FreeFlowSequence
from agentsociety.log import logger

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pika.spec
import requests
import time
import traceback

@dataclass
class AgentMetadata:
    name: str
    description: str
    tags: List[str]
    
    def to_payload(self):
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags
        }

AGENT_BASE_PATH = "/agent"
AGENT_DEBUG_ERROR_INDICATOR = "AGENT_DEBUG_ERROR_INDICATOR"

class AgentSocietyWorker:
    
    def __init__(self, connection_params: pika.ConnectionParameters, user_id: str, agent_metadata: AgentMetadata, host: str, free_flow: FreeFlowSequence, debug_mode = False) -> None:
        self.connection = pika.BlockingConnection(parameters=connection_params)
        
        self.user_id = user_id
        self.agent_meta = agent_metadata
        self.host = host
        self.free_flow_seq = free_flow
        self.debug_mode: bool = debug_mode

    def get_queue_name(self) -> str:
        queue_name = self._register_agent_and_get_queue_name()
        
        if queue_name is None:
            raise RuntimeError("Could not retrieve queue name")
        return queue_name

    def _register_agent_and_get_queue_name(self) -> Optional[str]:
        for _ in range(10):
            try:
                agent_data = self._try_get_agent()
                
                if agent_data is not None:
                    if self._check_agent_up_to_date(agent_data):
                        return agent_data["queue_name"]
                    else:
                        self._delete_mismatching_agent()
                
                registration_result = self._register_agent()
                
                if registration_result is not None:
                    return registration_result
                
                logger.warning("Could not get queue name, retrying after wait!")
            except Exception as e:
                logger.error(f"Something went wrong registring: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.info("retrying after wait")

            time.sleep(3)
        return None

    def _register_agent(self) -> Optional[str]:
        logger.info("agent does not exist trying to create it")
        result = requests.post(f"{self.host}{AGENT_BASE_PATH}", json=self.agent_meta.to_payload(), headers={"user-id": self.user_id})
        if result.status_code <= 299:
            logger.info(f"STATUS {result.status_code}: {result.json()}")
            return result.json()["queue_name"]
        return None

    def _delete_mismatching_agent(self):
        logger.info("Found old agent metadata under this name, deleting old agent for re-creation.")
        result = requests.delete(f"{self.host}{AGENT_BASE_PATH}", json={"name": self.agent_meta.name}, headers={"user-id": self.user_id})
        
        if result.status_code != 200:
            raise RuntimeError(f"The deletion of the agent {self.agent_meta.name} failed, expected 200, got {result.status_code}")
    
    def _try_get_agent(self) -> Optional[Dict[str, Any]]:
        result = requests.get(f"{self.host}{AGENT_BASE_PATH}", json={"name": self.agent_meta.name}, headers={"user-id": self.user_id})
        
        if result.status_code <= 299:
            return result.json()
        
        return None

    def _check_agent_up_to_date(self, received_data: Dict[str, Any]) -> bool:
        return \
            self.agent_meta.name == received_data["name"] and \
            self.agent_meta.description == received_data["description"] and \
            self.agent_meta.tags == received_data["tags"]

    def _send_messages_reply_success(self, chn: Channel, method: pika.spec.Basic.Deliver, delta: HistoryDelta, task_id: str):
        body_serialized = delta.to_json()
        body_serialized["status"] = "Successful"
        body_serialized["type"] = "ChatMessages"
        
        body = {
            "task_id": task_id,
            "generic_body": body_serialized
        }
        logger.info(json.dumps(body))
        chn.basic_publish(exchange='dispatcher', routing_key='', body=json.dumps(body))
        chn.basic_ack(method.delivery_tag)
        logger.info("Sent messages response to dispatcher")
        
    def _send_artifacts_reply_success(self, chn: Channel, method: pika.spec.Basic.Deliver, artifacts: TaskArtifacts, task_id: str):
        body_serialized = artifacts.to_json()
        body_serialized["status"] = "Successful"
        body_serialized["type"] = "Artifact"
        
        body = {
            "task_id": task_id,
            "generic_body": body_serialized
        }
        logger.info(json.dumps(body))
        chn.basic_publish(exchange='dispatcher', routing_key='', body=json.dumps(body))
        chn.basic_ack(method.delivery_tag)
        logger.info("Sent messages response to dispatcher")
    
    def _send_reply_failed(self, chn: Channel, method: pika.spec.Basic.Deliver, task_id: str):
        body_serialized = {
            "status": "Failed"
        }
        
        body = {
            "task_id": task_id,
            "generic_body": body_serialized
        }
        
        chn.basic_publish(exchange='dispatcher', routing_key='', body=json.dumps(body))
        chn.basic_ack(method.delivery_tag)
        logger.info("Sent response to dispatcher")

    def _queue_callback(self, chn: Channel, method: pika.spec.Basic.Deliver, props: pika.spec.BasicProperties, body: bytes):
        logger.info("received a message")
        try:
            payload = json.loads(body)
        except Exception as e:
            logger.error("failed to decode json payload")
            chn.basic_nack(method.delivery_tag, requeue=False)
        
        try:
            task_id = payload["task_id"]
            task_type = payload["task_type"]
            msg_body = payload["body"]
            
            history = History.from_json(msg_body)
            if task_type == "ChatMessage":
                next_msg = self.free_flow_seq.step(history)
                delta = HistoryDelta([next_msg])
                self._send_messages_reply_success(chn, method, delta, task_id)
            elif task_type == "Artifact":
                next_msg = self.free_flow_seq.step(history)
                artifact = TaskArtifact("test", next_msg.content)
                self._send_artifacts_reply_success(chn, method, TaskArtifacts(results=[artifact]), task_id)

        except Exception as e:
            logger.error(f"Could not convert python object into History: {e}\n{traceback.format_exc()}")
            if not self.debug_mode:
                self._send_reply_failed(chn, method, task_id)
            else:
                if task_type == "ChatMessage":
                    logger.warning("Sending error as message response because of debug mode!")
                    self._send_messages_reply_success(chn, method, self._build_debug_history(e), task_id)
                elif task_type == "Artifact":
                    logger.warning("Sending error as task response because of debug mode!")
                    error_artifact = TaskArtifact("error_report", self._build_debug_content(e))
                    self._send_artifacts_reply_success(chn, method, TaskArtifacts(results=[error_artifact]), task_id)

    def _build_debug_history(self, exc: Exception) -> HistoryDelta:
        error_message = self._build_debug_content(exc)
        return HistoryDelta([
            HistoryContent(
                error_message, 
                Actor.SYSTEM, 
                ContentType.UNDEFINED, 
                user_input_required=True, 
                annotations={AGENT_DEBUG_ERROR_INDICATOR: self.agent_meta.name}, 
                artifacts=[HistoryArtifact(AGENT_DEBUG_ERROR_INDICATOR, self.agent_meta.name)]
            )
        ])

    def _build_debug_content(self, exc: Exception) -> str:
        return (
            f"### Internal Server Error in agent '{self.agent_meta.name}'\n"
            "======\n"
            "During internal processing an exception occurred:\n"
            "```txt\n"
            f"{"\n".join(traceback.format_exception(exc))}\n"
            "```\n"
            "======\n"
            "> This exception is being reported because the agent host enabled debug mode. To retry instead debug mode must be disabled."
        )

    def listen_to_queue(self):
        queue_name = self.get_queue_name()
        
        logger.info("Waiting 3 seconds before connecting...")
        time.sleep(3)
        logger.info("Starting to consume!")
        
        for _ in range(5):
            try:
                channel = self.connection.channel()
                channel.basic_consume(queue_name, on_message_callback=self._queue_callback, auto_ack=False)
                channel.start_consuming()
            except Exception as e:
                logger.error(f"Something went wrong connecting to the queue: {e}, retrying in 3 seconds")
            time.sleep(3)
        logger.error("Connection has failed. Retries exhausted.")
