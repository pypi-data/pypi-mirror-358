from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from copy import copy, deepcopy
import json
from langchain.schema import SystemMessage, AIMessage, HumanMessage, BaseMessage
from agentsociety.chat.utils import HistoryArtifactCompatible

from agentsociety.log import logger


class Actor(Enum):
    """
    Enumeration of possible message senders in the chat history.
    """
    SYSTEM = "system"
    USER = "user"
    AGENT = "ai"

    def to_exportable_name(self) -> str:
        """
        Converts the Actor enum to its exportable string representation.

        Returns:
            str: The exportable name of the actor.
        """
        match self.name:
            case 'SYSTEM':
                return 'SYSTEM'
            case 'AGENT':
                return 'AGENT'
            case 'USER':
                return 'USER'
            case _:
                raise RuntimeError(f'weird user name {self.name}')

    @classmethod
    def from_exportable_name(cls, name: str):
        """
        Creates an Actor enum instance from its exportable string name.

        Args:
            name (str): The exportable name of the actor.

        Returns:
            Actor: The corresponding Actor enum member.
        """
        match name:
            case 'SYSTEM':
                return cls.SYSTEM
            case 'AGENT':
                return cls.AGENT
            case 'USER':
                return cls.USER


class ContentType(Enum):
    """
    Enumeration of different types of content that can appear in the chat history.
    """
    UNDEFINED = 0


    @classmethod
    def from_int(cls, value: Optional[int]) -> 'ContentType':
        """
        Creates a ContentType enum instance from an integer value.

        Args:
            value (Optional[int]): The integer value representing the content type.

        Returns:
            ContentType: The corresponding ContentType enum member.
        """
        if value is None:
            return ContentType.UNDEFINED
        return ContentType(value)


class Command:
    
    def to_json(self) -> Dict[str, Any]:
        raise NotImplementedError()
    
class TerminateSelfCommand(Command):

    def __init__(self, success: bool, artifacts: Optional[List[str]] = None, annotations: Optional[List[str]] = None):
        super().__init__()
        self.successful = success
        self.artifacts = artifacts
        self.annotations = annotations
        
        if success:
            assert artifacts is None
            assert annotations is None
        elif success is False:
            assert artifacts is not None
            assert annotations is not None
    
    def to_json(self) -> Dict[str, Any]:
        if self.successful:
            param_dict = {
                "status": "Success",
                "details": {
                    "artifacts": self.artifacts,
                    "annotation": self.annotations
                }
            }
        else:
            param_dict = {
                "status": "Failure",
                "details": {
                    "reason": None
                }
            }
        
        return {
            "command": "TerminateSelf",
            "parameters": param_dict
        }


class TerminateChildCommand(Command):
    
    def __init__(self):
        super().__init__()
    
    def to_json(self):
        return {
            "command": "TerminateChildren",
        }


class CallAgentCommand(Command):
    
    def __init__(self, agent_name: str):
        super().__init__()
        self.agent_name =  agent_name

    def to_json(self):
        return {
            "command": "CallAgent",
            "parameters": self.agent_name
        }

class HistoryContent:
    """
    Represents a single entry in the chat history, including the message content, sender, and metadata.
    """

    def __init__(
        self,
        content: str,
        sender: Actor,
        content_type: ContentType = ContentType.UNDEFINED,
        user_input_required: bool = False,
        annotations: Dict[str, str] = None,
        artifacts: List['HistoryArtifact'] = None,
        command: Optional[Command] = None
    ) -> None:
        """
        Initializes a HistoryContent instance.

        Args:
            content (str): The textual content of the message.
            sender (Actor): The actor who sent the message.
            content_type (ContentType): The type of content.
            user_input_required (bool, optional): Indicates if user input is required. Defaults to False.
            annotations (Dict[str, str], optional): Additional annotations for the message. Defaults to None.
            artifacts (List[HistoryArtifact], optional): Associated artifacts. Defaults to None.
        """
        self.content: str = content
        self.sender: Actor = sender
        self.content_type = content_type
        self.annotations: Dict[str, str] = {} if annotations is None else annotations
        self.artifacts: List[HistoryArtifact] = [] if artifacts is None else artifacts
        self.user_input_required: bool = user_input_required
        self.command = command

    def render(self) -> str:
        """
        Renders the message in a readable string format.

        Returns:
            str: The formatted message string.
        """
        return f"<{self.sender.name}>: {self.content}\n"

    def render_tuple(self) -> Tuple[str, str]:
        """
        Renders the message as a tuple of sender and content.

        Returns:
            Tuple[str, str]: A tuple containing the sender's value and the message content.
        """
        return (self.sender.value, self.content)

    def render_langchain(self, simple: bool) -> BaseMessage:
        """
        Converts the message to a LangChain BaseMessage object.

        Args:
            simple (bool): If True, simplifies the message format.

        Returns:
            BaseMessage: The corresponding LangChain message object.
        """
        match self.sender:
            case Actor.SYSTEM:
                if not simple:
                    return SystemMessage(self.content)
                else:
                    return HumanMessage(self.content)
            case Actor.USER:
                return HumanMessage(self.content)
            case Actor.AGENT:
                return AIMessage(self.content)
            case _:
                raise RuntimeError(f"Unknown role for message: '{self.sender}'")

    def clone(self) -> 'HistoryContent':
        """
        Creates a deep copy of the HistoryContent instance.

        Returns:
            HistoryContent: The cloned HistoryContent object.
        """
        return HistoryContent(
            copy(self.content),
            copy(self.sender),
            copy(self.content_type),
            self.user_input_required,
            deepcopy(self.annotations)
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Serializes the HistoryContent instance to a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: The serialized representation of the HistoryContent.
        """
        return {
            "content": self.content,
            "sender": self.sender.to_exportable_name(),
            "content_type": self.content_type.value,
            "user_input_required": self.user_input_required,
            "annotations": self.annotations,
            "artifacts": {a.ref: a.content for a in self.artifacts},
            "command": self.command.to_json() if self.command else None
        }

    @classmethod
    def from_json(cls, payload: Dict[str, Any]) -> 'HistoryContent':
        """
        Deserializes a JSON dictionary to create a HistoryContent instance.

        Args:
            payload (Dict[str, Any]): The JSON payload.

        Returns:
            HistoryContent: The deserialized HistoryContent object.
        """
        content = HistoryContent(
            content=payload['content'],
            sender=Actor.from_exportable_name(payload['sender']),
            content_type=ContentType.from_int(payload['content_type']),
            annotations=payload.get("annotations", {})
        )
        content.user_input_required = payload.get('user_input_required', False)
        if "artifacts" in payload:
            logger.info(payload["artifacts"])
            artifact_list = [HistoryArtifact(k, v) for k, v in payload["artifacts"].items()]
            content.artifacts = artifact_list

        return content

    def add_artifact(self, artifact: 'HistoryArtifact'):
        """
        Adds an artifact to the message.

        Args:
            artifact (HistoryArtifact): The artifact to add.
        """
        self.artifacts.append(artifact)


_FALSE = 'false'
_TRUE = 'true'


class HistoryArtifact:
    """
    Represents an artifact associated with a history content, such as additional data or metadata.
    """

    def __init__(self, ref: str, content: str) -> None:
        """
        Initializes a HistoryArtifact instance.

        Args:
            ref (str): The reference identifier for the artifact.
            content (str): The content or data of the artifact.
        """
        self.ref: str = ref
        self.content: str = content

    def clone(self) -> 'HistoryArtifact':
        """
        Creates a copy of the HistoryArtifact instance.

        Returns:
            HistoryArtifact: The cloned HistoryArtifact object.
        """
        return HistoryArtifact(self.ref, self.content)

    @classmethod
    def from_object(cls, ref: str, obj: HistoryArtifactCompatible) -> 'HistoryArtifact':
        """
        Creates a HistoryArtifact from an object that is compatible with HistoryArtifact.

        Args:
            ref (str): The reference identifier for the artifact.
            obj (HistoryArtifactCompatible): The object to convert into an artifact.

        Returns:
            HistoryArtifact: The created HistoryArtifact object.
        """
        return cls(ref, obj.to_text())

    @classmethod
    def from_bool_flag(cls, name: Enum, bool_val: bool) -> 'HistoryArtifact':
        """
        Creates a HistoryArtifact from a boolean flag.

        Args:
            name (Enum): The name of the flag.
            bool_val (bool): The boolean value of the flag.

        Returns:
            HistoryArtifact: The created HistoryArtifact object.
        """
        str_name = name.value
        str_val = _TRUE if bool_val else _FALSE

        return cls(str_name, str_val)


class HistoryDelta:
    """
    Represents a set of changes (delta) to be applied to the chat history.
    """

    def __init__(self, content: List[HistoryContent]) -> None:
        """
        Initializes a HistoryDelta instance.

        Args:
            content (List[HistoryContent]): A list of HistoryContent objects representing the changes.
        """
        self.content: List[HistoryContent] = content

    def to_json(self) -> Dict[str, Any]:
        """
        Serializes the HistoryDelta to a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: The serialized representation of the HistoryDelta.
        """
        return {
            "content": [c.to_json() for c in self.content]
        }


class History:
    """
    Manages the complete chat history, including messages and associated artifacts.

    Note:
        - Methods starting with an underscore (`_`) are private helper methods and should not be called directly.
    """

    def __init__(self, content: Optional[List[HistoryContent]] = None) -> None:
        """
        Initializes a History instance.

        Args:
            content (Optional[List[HistoryContent]], optional): Initial list of HistoryContent. Defaults to None.
        """
        self.content: List[HistoryContent] = [] if content is None else content
        self.artifacts: Dict[str, HistoryArtifact] = {}
        # Stores all changes to artifacts
        self.delta_content: List[HistoryContent] = []

        self._setup_artifact_cache()

    def _setup_artifact_cache(self):
        """
        Initializes the artifact cache based on the existing content.

        Note:
            This is a private helper method and should not be called directly.
        """
        for c in self.content:
            self._update_artifact_cache_from_content(c)

    def _update_artifact_cache_from_content(self, content: HistoryContent):
        """
        Updates the artifact cache with artifacts from a given HistoryContent.

        Args:
            content (HistoryContent): The content from which to extract artifacts.

        Note:
            This is a private helper method and should not be called directly.
        """
        artifacts = content.artifacts

        for a in artifacts:
            self.artifacts[a.ref] = a

    def render(self) -> str:
        """
        Renders the entire chat history as a single formatted string.

        Returns:
            str: The formatted chat history.
        """
        return "\n".join([m.render() for m in self.content])

    def render_tuples(self) -> List[Tuple[str, str]]:
        """
        Renders the chat history as a list of tuples containing sender and content.

        Returns:
            List[Tuple[str, str]]: The list of sender-content tuples.
        """
        return [m.render_tuple() for m in self.content]

    def render_langchain(self, simple: bool) -> List[BaseMessage]:
        """
        Converts the entire chat history to a list of LangChain BaseMessage objects.

        Args:
            simple (bool): If True, simplifies the message formats.

        Returns:
            List[BaseMessage]: The list of LangChain message objects.
        """
        return [m.render_langchain(simple) for m in self.content]

    def clone(self) -> 'History':
        """
        Creates a deep copy of the History instance.

        Returns:
            History: The cloned History object.
        """
        return History([m.clone() for m in self.content])

    def get_delta(self) -> HistoryDelta:
        """
        Retrieves the current set of changes (delta) in the history.

        Returns:
            HistoryDelta: The delta representing recent changes.
        """
        return HistoryDelta(
            self.delta_content
        )

    def add_delta(self, delta: HistoryDelta):
        """
        Applies a set of changes (delta) to the history.

        Args:
            delta (HistoryDelta): The delta to apply.
        """
        for c in delta.content:
            self.add_content(c)

    def add_content(self, content: HistoryContent):
        """
        Adds a new HistoryContent to the history and updates artifacts.

        Args:
            content (HistoryContent): The content to add.
        """
        self.content.append(content)
        self.delta_content.append(content)

        self._update_artifact_cache_from_content(content)

    def get_artifact(self, artifact_ref: str) -> Optional[HistoryArtifact]:
        """
        Retrieves an artifact by its reference identifier.

        Args:
            artifact_ref (str): The reference identifier of the artifact.

        Returns:
            Optional[HistoryArtifact]: The retrieved artifact or None if not found.
        """
        return self.artifacts.get(artifact_ref)

    def get_artifact_bool_flag(self, artifact_ref: Enum) -> bool:
        """
        Retrieves a boolean flag from the artifacts based on its reference identifier.

        Args:
            artifact_ref (Enum): The enum representing the artifact reference.

        Returns:
            bool: The boolean value of the artifact flag.
        """
        return self.get_artifact_content(artifact_ref.value, _FALSE) == _TRUE

    def get_artifact_content(self, artifact_ref: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves the content of an artifact by its reference identifier.

        Args:
            artifact_ref (str): The reference identifier of the artifact.
            default (Optional[str], optional): The default value to return if the artifact is not found. Defaults to None.

        Returns:
            Optional[str]: The content of the artifact or the default value.
        """
        if (artifact := self.get_artifact(artifact_ref)) is not None:
            return artifact.content
        return default

    def get_latest_system_instruction_content_type(self) -> Optional[ContentType]:
        """
        Retrieves the content type of the latest system instruction in the history.

        Returns:
            Optional[ContentType]: The content type or None if no system instruction is found.
        """
        for c in reversed(self.content):
            if c.sender == Actor.SYSTEM:
                return c.content_type
        return None

    def get_system_instruction_type_stack(self) -> List[ContentType]:
        """
        Retrieves a list of all system instruction content types in the history.

        Returns:
            List[ContentType]: The list of system instruction content types.
        """
        system_instructions = [c for c in self.content if c.sender == Actor.SYSTEM]
        return [m.content_type for m in system_instructions]

    def get_latest_agent_message(self) -> Optional[HistoryContent]:
        """
        Retrieves the latest message sent by the agent.

        Returns:
            Optional[HistoryContent]: The latest agent message or None if not found.
        """
        for c in reversed(self.content):
            if c.sender == Actor.AGENT:
                return c
        return None

    def get_latest_non_user_message(self) -> Optional[HistoryContent]:
        """
        Retrieves the latest message sent by either the agent or the system.

        Returns:
            Optional[HistoryContent]: The latest non-user message or None if not found.
        """
        for c in reversed(self.content):
            if c.sender in [Actor.AGENT, Actor.SYSTEM]:
                return c
        return None

    def get_latest_message(self) -> Optional[HistoryContent]:
        """
        Retrieves the most recent message in the history.

        Returns:
            Optional[HistoryContent]: The latest message or None if the history is empty.
        """
        if len(self.content) == 0:
            return None
        return self.content[-1]

    def is_last_message_choice(self) -> bool:
        """
        Determines if the last system instruction requires a user choice.

        Returns:
            bool: True if the last message is a choice type, False otherwise.
        """
        content_type = self.get_latest_system_instruction_content_type()
        return content_type in [
            ContentType.FORMALIZE_OPTIONS,
            ContentType.EXPANSION_OPTIONS,
            ContentType.PARAMETERIZE_OPTIONS
        ]

    def to_json(self) -> Dict[str, Any]:
        """
        Serializes the entire chat history to a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: The serialized representation of the History.
        """
        return {
            "content": [c.to_json() for c in self.content]
        }

    @classmethod
    def from_json(cls, payload: List[Dict[str, Any]]) -> 'History':
        """
        Deserializes a JSON payload to create a History instance.

        Args:
            payload (List[Dict[str, Any]]): The JSON payload representing the chat history.

        Returns:
            History: The deserialized History object.
        """
        logger.info(payload)
        messages = [HistoryContent.from_json(p) for p in payload["content"]]

        return History(messages)