from enum import Enum


class FlowControlAnnotations(Enum):
    AgentDidTerminateSelf = "sys_agent_did_terminate_self"
    InvisibleAction = "sys_invisible"
    OriginMessageId = "sys_origin_message"
    OriginChatId = "sys_origin_chat"
