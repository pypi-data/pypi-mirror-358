from agentsociety.chat.box.free_flow_box import BoxResultMeta, FreeFlowBox, BoxMeta
from agentsociety.chat.history import History, HistoryContent, ContentType, Actor, HistoryArtifact
from agentsociety.chat.free.routers import CategoricalIntentContext, IntentRouter
from agentsociety.prompting import get_llm_supplier
from agentsociety.log import logger

from typing import List, Optional, Tuple, Dict
from enum import Enum


class YesNo(Enum):
    YES = 1
    NO = 2


YesNoContext = CategoricalIntentContext(
    YesNo, {
        YesNo.YES: ["yes", "yes.", "yes!", "Yes", "Yes.", "Yes!"],
        YesNo.NO: ["no", "no.", "no!", "No", "No.", "No!"]
    }
)

yes_no_router = IntentRouter(YesNoContext, top_n=1)


class FreeFlowSequenceErrorRouter(FreeFlowBox):
    
    def __init__(self, sequence: List[FreeFlowBox]) -> None:
        super().__init__("FreeFlowSequenceErrorRouter")
        self.sequence: List[FreeFlowBox] = sequence
        self.failed_at: Optional[int] = None
        self.router_cache: Dict[int, IntentRouter] = {}
        
        self.long_llm = get_llm_supplier().make_llm(temperature=0.2, max_tokens=2048)
        self.short_llm = get_llm_supplier().make_llm(temperature=0.2, max_tokens=10)

    def generate(self, history: History) -> HistoryContent:
        result = self.long_llm.invoke(history.render_tuples())
        reply = result.content
        
        return HistoryContent(reply, Actor.AGENT, ContentType.UNDEFINED, annotations={'BOX_NAME': self.box_name})

    def _make_intent_router(self, stage: int) -> IntentRouter:
        retry_steps = [s for i, s in enumerate(self.sequence) if i <= self.failed_at]
        retry_step_name_to_obj = {s.get_box_meta().unique_name: s for s in retry_steps}
        
        enum_entries = {}
        enum_entries["GiveUp"] = -1
        
        for i, step in enumerate(retry_steps):
            enum_entries[step.get_box_meta().unique_name] = i
        
        stage_enum = Enum(f'ChoicesStage-{stage}', enum_entries)
        
        categorical_example = {stage_enum.GiveUp: ["give up", "end flow", "stop flow", "stop solving task", "stop"]}
        
        for element in stage_enum:
            if element.name == 'GiveUp':
                continue
            categorical_example[element] = retry_step_name_to_obj[element.name].get_box_meta().aliases + [retry_step_name_to_obj[element.name].get_box_meta().unique_name]
        
        intent_context = CategoricalIntentContext(stage_enum, categorical_example)
        intent_router = IntentRouter(intent_context, top_n=1)
        
        return intent_router

    def _get_intent_router(self) -> IntentRouter:
        if self.failed_at not in self.router_cache:
            router = self._make_intent_router(self.failed_at)
            self.router_cache[self.failed_at] = router
        return self.router_cache[self.failed_at]

    def set_pointer(self, ptr: int):
        self.failed_at = ptr

    def generate_system_prompt(self, history: History) -> HistoryContent:
        failed_step: FreeFlowBox = self.sequence[self.failed_at]
        failed_box_meta = failed_step.get_box_meta()
        
        retry_steps = [s for i, s in enumerate(self.sequence) if i <= self.failed_at]
        
        retry_step_list_entries = [f"- {s.get_box_meta().unique_name}" for s in retry_steps]
        
        return self._prepare_system_content(
            f"Hey AI, you failed at the step '{failed_box_meta.unique_name}' of the process. Now you need to decided where you want to continue or if you want to give up.\n"
            f"Here are the steps that you can go to next to retry:\n{"\n".join(retry_step_list_entries)}\n\n"
            "You can also choose to give up if you think that is the best way to proceed!\n"
            "Please elaborate on why you want to go to the step you choose, take as many steps as you want! Make the choice without involving the user!\n"
            "Do not try to solve the step you go to yet, just choose the step and eloborate on why but do not perform the action of the step."
        )

    def check_user_input(self, history: History) -> bool:
        return False
    
    def check_failure(self, history: History) -> Tuple[bool, BoxResultMeta | None]:
        return False, None
    
    def check_completion(self, history: History) -> Tuple[bool | BoxResultMeta | None]:
        clone = history.clone()
        
        check_completion_msg = self._prepare_system_content("Have you made your choice?")
        
        clone.add_content(check_completion_msg)
        
        result = self.short_llm.invoke(clone.render_tuples())
        reply = result.content
        
        category = yes_no_router.determine_category(reply)
        
        if category != YesNo.YES:
            return False, None
        
        last_msg = history.get_latest_agent_message()
        
        category = self._get_intent_router().determine_category(last_msg.content)
        
        if category is None:
            return False, None
        
        return True, BoxResultMeta(new_annotations={'category': category.name, 'next_step': f"{category.value}"}, new_artifacts={})
    
    def on_completion(self, history: History, box_meta: BoxResultMeta) -> HistoryContent:
        return self._prepare_system_content(f"Category '{box_meta.new_annotations['category']}' chosen", annotations=box_meta.new_annotations)

    def on_failure(self, history: History, box_meta: BoxResultMeta) -> HistoryContent:
        raise RuntimeError("illegal state reached")


class FreeFlowSequence:
    
    def __init__(self, name: str, sequence: List[FreeFlowBox]) -> None:
        self.name: str = name
        self.sequence: List[FreeFlowBox] = sequence
        self.fail_router: FreeFlowSequenceErrorRouter = FreeFlowSequenceErrorRouter(self.sequence)

    def gave_up(self, history: History) -> bool:
        return history.get_artifact_content('GIVE_UP', 'false') == 'true'
    
    def is_done(self, history: History) -> bool:
        return history.get_artifact_content('IS_DONE', 'false') == 'true'

    def step(self, history: History) -> HistoryContent:
        gave_up = history.get_artifact_content('GIVE_UP', 'false') == 'true'
        is_done = history.get_artifact_content('IS_DONE', 'false') == 'true'
        if gave_up:
            return HistoryContent("this chat is over because you have given up.", Actor.SYSTEM, ContentType.UNDEFINED)
        if is_done:
            return HistoryContent("The task is done!", Actor.SYSTEM, ContentType.UNDEFINED, artifacts=[HistoryArtifact("IS_DONE", "true")])
        
        current_step, is_done = self.determine_sequence_step(history)
        if not is_done:
            return self.run_step_action(history, current_step)
        else:
            return HistoryContent("The task is done!", Actor.SYSTEM, ContentType.UNDEFINED, artifacts=[HistoryArtifact("IS_DONE", "true")])

    def determine_sequence_step(self, history: History) -> Tuple[int, bool]:
        for i, s in enumerate(self.sequence):
            art_names = s.get_artifact_names()
            
            step_success = history.get_artifact_content(art_names.success_artifact, 'false') == 'true'
            step_failed = history.get_artifact_content(art_names.failure_artifact, 'false') == 'true'
            
            if step_failed:
                return i, False

            if not step_success:
                return i, False
        return len(self.sequence), True

    def jump_to_step(self, choose_msg: HistoryContent, from_: int, to: int) -> HistoryContent:
        logger.info(f"Asserting {to} <= {from_}")
        assert to <= from_
        for s in self.sequence[to:from_+1]:
            art_names = s.get_artifact_names()
            choose_msg.add_artifact(HistoryArtifact(art_names.success_artifact, 'false'))
            choose_msg.add_artifact(HistoryArtifact(art_names.failure_artifact, 'false'))
        
        return choose_msg

    def give_up(self, msg: HistoryContent) -> HistoryContent:
        msg.add_artifact(HistoryArtifact('GIVE_UP', 'true'))
        return msg

    def run_step_action(self, history: History, step: int) -> HistoryContent:
        step_box = self.sequence[step]
        box_arts = step_box.get_artifact_names()
        box_failed = history.get_artifact_content(box_arts.failure_artifact, 'false') == 'true'
        
        if box_failed:
            self.fail_router.set_pointer(step)
            new_msg = self.fail_router.step(history)
            
            if (next_step := new_msg.annotations.get('next_step', None)) is not None:
                next_step_int = int(next_step)
                if next_step_int == -1:
                    return self.give_up(new_msg)
                return self.jump_to_step(new_msg, step, next_step_int)
            else:
                return new_msg
        else:
            return step_box.step(history)
