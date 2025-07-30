from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

from agentsociety.chat.history import History, HistoryContent, HistoryDelta, HistoryArtifact, Actor, ContentType, TerminateSelfCommand
from agentsociety.log import logger

@dataclass
class BoxResultMeta:
    new_annotations: Dict[str, str]
    new_artifacts: Dict[str, str]


@dataclass
class BoxMeta:
    unique_name: str
    aliases: List[str]


@dataclass
class ArtifactNames:
    success_artifact: str
    failure_artifact: str
    initial_artifact: str


class FreeFlowBox:
    """
    Simple Conversation segement.
    Flow A (Box is the first box in a new chat):
    1. User starts a conversation
    2. New chat with the box is created that contains the user's message to start the agent
    3. system prompt is inserted
    4. Generation loop (via step method) -> Implementation Specific
    
    Flow B (Box comes after several other boxes):
    1. Previous box finishes
    2. Box adds system prompt
    3. Generation loop (via step method) -> Implementation Specific
    """
    
    def __init__(self, box_name: str) -> None:
        self.box_name: str = box_name
    
    def get_box_meta(self) -> BoxMeta:
        """
        Method to retrieve the box metadata.
        Please override this method.
        """
        pass
    
    def check_completion(self, history: History) -> Tuple[bool, Optional[BoxResultMeta]]:
        """
        Check the completion, possibly return some data.
        Please override this method. This method is to be used to analyze the history and the check for completion.
        """
        pass
    
    def check_failure(self, history: History) -> Tuple[bool, Optional[BoxResultMeta]]:
        """
        Check for failure, possibly return some data.
        Please override this method. This method is to be used to analyze the history and to check for agent failure.
        """
        pass
    
    def check_user_input(self, history: History) -> bool:
        """
        Checks if we need user input. 
        Please override and implement code that checks if the latest HistoryContent needs `user_input_required` to be `True`.
        """
        pass
    
    def generate(self, history: History) -> HistoryContent:
        """
        Generate a message. This is called by `step` when there is no custom processing step.
        Please override this method with the common message generation logic.
        """
        pass

    def on_completion(self, history: History, box_meta: BoxResultMeta) -> HistoryContent:
        """
        What to generate upon completion. Please override this method.
        """
        pass
    
    def on_failure(self, history: History, box_meta: BoxResultMeta) -> HistoryContent:
        """
        what to generate upon failure. Please override this method.
        """
        pass
    
    def generate_system_prompt(self, history: History) -> HistoryContent:
        """
        Method to create the system prompt
        The system prompt is appended upon entering the box, there can be one to many messages prior to entering the box.
        Thus this message will not be the first message in the chat.
        This message is only visible to the agent itself.
        """
        pass
    
    def _prepare_system_content(self, content: str, annotations: Dict[str, str] = {}, artifacts: List[HistoryArtifact] = None) -> HistoryContent:
        """
        Makes a message with the sender 'system' that only visible to the agent, not visible to the user.
        """
        return HistoryContent(
            content, Actor.SYSTEM, annotations={**annotations, 'BOX_NAME': self.box_name}, artifacts=artifacts
        )
    
    def _prepare_failure_content(self, content: str, annotations: Dict[str, str] = {}, artifacts: List[HistoryArtifact] = None) -> HistoryContent:
        """
        Makes a message that initiates an unsuccessful termination
        """
        return HistoryContent(
            content, Actor.SYSTEM, annotations=annotations, artifacts=artifacts, command=TerminateSelfCommand(success=False)
        )
    
    def _last_msg_same_box(self, history: History) -> bool:
        last_msg = history.get_latest_non_user_message()
        if last_msg is None:
            return False
        return last_msg.annotations.get('BOX_NAME', 'NONE') == self.box_name
    
    def _is_agent_instruction_present(self, history: History) -> bool:
        """
        Checks if the system prompt of this FreeFlowBox is present in the chat.
        Please do not override this method.
        """
        artifact_names = self.get_artifact_names()
        instruction_flag = history.get_artifact_content(artifact_names.initial_artifact, 'false')
        
        return instruction_flag == 'true'

    def get_artifact_names(self) -> ArtifactNames:
        """
        Returns the default artifacts for the FreeFlowBox instance.
        Please do not override this method.
        """
        return ArtifactNames(
            f"{self.box_name}_COMPLETED",
            f"{self.box_name}_FAILED",
            f"{self.box_name}_INITIALIZED"
        )
    
    def _get_initialization_artifacts(self) -> List[HistoryArtifact]:
        """
        Helper method.
        Please do not override.
        """
        artifact_names = self.get_artifact_names()
        return [
            HistoryArtifact(artifact_names.success_artifact, 'false'),
            HistoryArtifact(artifact_names.failure_artifact, 'false'),
            HistoryArtifact(artifact_names.initial_artifact, 'true')
        ]
    
    def _get_initialization_reset_artifact(self) -> HistoryArtifact:
        """
        Helper method.
        Please do not override.
        """
        artifact_names = self.get_artifact_names()
    
        return HistoryArtifact(
            artifact_names.initial_artifact, 'false'
        )
    
    def init(self, history: History) -> HistoryContent:
        """
        Called by `step` at initialization.
        Please do not override.
        """
        system_prompt = self.generate_system_prompt(history)
        reset_artifacts = self._get_initialization_artifacts()
        for ra in reset_artifacts:
            system_prompt.add_artifact(ra)
        return system_prompt
    
    def custom_processing_step(self, history: History) -> Tuple[bool, Optional[HistoryContent]]:
        """
        Can be overridden to implement more complex custom behavior.
        This can be useful to avoid blowing up the `generate` method.
        If this method returns (`True`, HistoryContent) that history content object will be returned from the FreeFlowBox.
        If it returns (`False`, None) generate() will be called for result generation.
        """
        return False, None

    def _generate_completion(self, history: History, complete_meta: BoxMeta) -> HistoryContent:
        """
        Helper method.
        Please do not override.
        """
        completion_msg = self.on_completion(history, complete_meta)
        
        artifacts = self.get_artifact_names()
        
        completion_msg.add_artifact(
            HistoryArtifact(artifacts.success_artifact, "true")
        )
        
        completion_msg.add_artifact(
            self._get_initialization_reset_artifact()
        )
        
        return completion_msg

    def _generate_failure(self, history: History, failure_meta: BoxMeta) -> HistoryContent:
        """
        Helper method.
        Please do not override.
        """
        failure_msg = self.on_failure(history, failure_meta)
        
        artifacts = self.get_artifact_names()
        
        failure_msg.add_artifact(
            HistoryArtifact(artifacts.failure_artifact, "true")
        )
        
        failure_msg.add_artifact(
            self._get_initialization_reset_artifact()
        )
        
        return failure_msg

    def step(self, history: History) -> Optional[HistoryContent]:
        """
        This method is the method that is called to generate Messages.
        Every time the FreeFlowBox generates something it works through this method.
        Please do not overwrite this method.
        """
        if not self._is_agent_instruction_present(history):
            # Called after the new chat for this agent has been created
            new_msg = self.init(history)
        else:
            # Called when system prompt is present
            complete, complete_meta = self.check_completion(history)
            if complete:
                logger.info("LLM figured that this step was successful")
                return self._generate_completion(history, complete_meta)
            
            failed, failed_meta = self.check_failure(history)
            if failed:
                return self._generate_failure(history, failed_meta)

            has_msg, msg = self.custom_processing_step(history)

            if has_msg:
                new_msg = msg
            else:
                new_msg = self.generate(history)

        fake_history = history.clone()
        fake_history.add_content(new_msg)
        
        user_input_required = self.check_user_input(fake_history)
        
        if user_input_required:
            # If user input is required, set the flag to copy this message to the caller
            new_msg.user_input_required = True
            return new_msg
        return new_msg

