# agent-society-lib

## Overview

This Python library is designed for building and managing agent workflows, embedding management, task orchestration, and message handling in distributed systems. It provides a modular architecture that simplifies integration with modern technologies like RabbitMQ, OpenAI, and LangChain for natural language processing and task automation.

## Key Features
1. <b>Collaborative Multi-Agent Systems</b></br>
Build intelligent agents that work as part of larger systems, each specializing in one aspect of a problem. These agents communicate and collaborate to tackle complex tasks through a modular and scalable framework.

2. <b>Customizable and Connected</b></br>
Define agents with one-to-many stages of processing, tailored to specific problems. Seamlessly integrate external systems, such as MILP solvers or fine-tuned LLMs, to enhance the system's functionality.

3. <b>Distributed Problem-Solving</b> </br>
Enables efficient problem-solving by dividing tasks among specialized agents that interact intelligently, achieving holistic solutions across diverse domains.

## Installation

Install the library using pip:

```shell
pip install agent-society-lib
```

## Quick Start

This section showcases how to implement a simple song-writer agent.

### Define your Free-Flow-Box
*box/song_writer.py*
```python
from typing import Tuple, Optional
from agentsociety.chat.box.free_flow_box import BoxMeta, BoxResultMeta, FreeFlowBox
from agentsociety.chat.box.shared import yes_no_router,  YesNo
from agentsociety.chat.history import History, HistoryContent, Actor, ContentType, HistoryArtifact
from agentsociety.prompting import get_llm_supplier, create_generic_chain, load_template_txt
from enum import Enum

class SongWriterFlags(Enum):
    SongWritingFailed = "SONG_WRITING_FAILED"
    SongWritingSuccessful = "SONG_WIRITING_SUCCESS"
    SongWritingAttempts = "SONG_WRITING_ATTEMPTS"


class SongWritingBox(FreeFlowBox):
    
    def __init__(self):
        super().__init__("SONG_WRITING")
        self.long_llm = get_llm_supplier().make_llm(temperature=0.2, max_tokens=2048)
        self.short_llm = get_llm_supplier().make_llm(temperature=0.2, max_tokens=10)
    
    def get_box_meta(self) -> BoxMeta:
        return BoxMeta(
            "Song Writing",
            ["Wiritng", "Writing Songtext", "Generating the text for a song"]
        )
    
    def generate_system_prompt(self, history: History) -> HistoryContent:
        return self._prepare_system_content(
            "AI, your task is to write a songtext given the instructions provided in the previous message.\n"
            "Make sure to try and incooperate as much of the instructions as possible into the songtext that you create!\n"
            "You should respond with the full song-text always, you will get opportunities to refine it until you deem it finished!"
        )
    
    def generate(self, history: History) -> HistoryContent:
        result = self.long_llm.invoke(history.render_tuples())
        reply = result.content
        
        return HistoryContent(reply, Actor.AGENT, ContentType.UNDEFINED, annotations={'BOX_NAME': self.box_name})
    
    def check_user_input(self, history: History) -> bool:        
        return False

    def check_completion(self, history: History) -> Tuple[bool, BoxResultMeta | None]:
        cloned_history = history.clone()
        
        completion_check = self._prepare_system_content(
            "Does this songtext incooperate all the requirements outlined in the initial message? "
            "Please reply with 'yes' or 'no'"
        )
        
        cloned_history.add_content(completion_check)
        
        result = self.short_llm.invoke(cloned_history.render_tuples())
        reply = result.content
        
        category = yes_no_router.determine_category(reply)
        
        if category == YesNo.YES:
            meta = BoxResultMeta({}, {})
            return True, meta
        return False, None
    
    def check_failure(self, history: History) -> Tuple[bool, BoxResultMeta | None]:
        num_attempts = int(
            history.get_artifact_content(SongWriterFlags.SongWritingAttempts.value, "0")
        )
        
        if num_attempts >= 5:
            return True, BoxResultMeta({}, {})

        cloned_history = history.clone()
        
        failure_check = self._prepare_system_content(
            "For the chat history, check if the latest draft (if present) is obviously wrong. "
            "If there is no draft yet, reply with 'no'. If there is a draft but there is nothing wrong with it reply with 'no' as well. "
            "If there is a draft with a mistake reply with 'yes'!"
            )
        
        cloned_history.add_content(failure_check)
        
        result = self.short_llm.invoke(cloned_history.render_tuples())
        reply = result.content
        
        category = yes_no_router.determine_category(reply)
        
        if category == YesNo.YES:
            meta = BoxResultMeta({}, {})
            return True, meta
        
        return False, None

    def on_completion(self, history: History, box_meta: BoxResultMeta) -> HistoryContent:
        latest_agent_message = history.get_latest_agent_message()
        
        return self._prepare_system_content(
            f"Songtext was written successfully, here it is:\n{latest_agent_message.content}",
            artifacts=[HistoryArtifact(SongWriterFlags.SongWritingSuccessful.value, 'true')],
            annotations={
                "sys_terminate_self": "true"
            }
        )
    
    def on_failure(self, history: History, box_meta: BoxResultMeta) -> HistoryContent:
        return self._prepare_system_content(
            'The writing of the Songtext has failed!', 
            artifacts=[
                HistoryArtifact(SongWriterFlags.SongWritingFailed.value, 'true')
            ]
        )

    def custom_processing_step(self, history: History) -> Tuple[bool, Optional[HistoryContent]]:
        latest_msg = history.get_latest_message()
        
        if latest_msg is None:
            # No custom processing necessary
            return False, None
        
        if latest_msg.sender != Actor.AGENT:
            # No custom processing necessary
            return False, None
        
        current_attempts = int(
            history.get_artifact_content(SongWriterFlags.SongWritingAttempts.value, "0")
        )
        
        # Instruct the AI to refine the songtext
        return True, self._prepare_system_content(
            'Looks like your songtext is not yet perfect! Please refine it a bit more!',
            artifacts=[
                HistoryArtifact(
                    SongWriterFlags.SongWritingAttempts,
                    str(current_attempts + 1)
                )
            ]
        )

```
### Define your Free-Flow-Sequence
*box/agent.py*
```python
from agentsociety.chat.box.free_flow_box import FreeFlowBox
from agentsociety.chat.box.free_flow_graph import FreeFlowSequence
from agentsociety.chat.history import History, HistoryContent, Actor, ContentType

from box.songtext_writer import SongWritingBox

def make_songwriter_flow() -> FreeFlowSequence:
    """
    Makes the Songwriter flow
    """
    writer = SongWritingBox()
    
    return FreeFlowSequence("songwriter seq", [writer])

```


### Define your agent
```python
import pika
from agentsociety.worker import AgentSocietyWorker
from agentsociety.worker import AgentMetadata

from box.agent import make_songwriter_flow

metadata = AgentMetadata(
    name="song_writer_agent",
    description="An agent that can write and create songs",
    tags=[
        "song writer", "song text writer"
    ]
)

worker = AgentSocietyWorker(
    pika.ConnectionParameters(
        '<your-rabbitmq-host>', 
        port=<your-rabbitmq-port>
    ),
    user_id="<your-user-id>",
    agent_metadata=metadata,
    host="<chat-server-host>",
    free_flow=make_songwriter_flow()
)
```
### Start listening to the queue
```python
worker.listen_to_queue()
```

### Dependencies
- RabbitMQ (pika)
- OpenAI/Gemini/Groq
- LangChain
- ChromaDB
- Python 3.12.8+

## License

This project is licensed under the MIT License. See the LICENSE file for details.
