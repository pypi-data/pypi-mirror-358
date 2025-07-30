from agentsociety.chat.intent.intent_router import IntentRouter, CategoricalIntentContext
from enum import Enum


class YesNoForCompletion(Enum):
    Yes = 1
    No = 2


yes_no_refinement_completion_examples = {
    YesNoForCompletion.Yes: ["Yes", "I am done", "Yes I am done gathering information", "Yes the step is complete", "Yes this is enough", "Done", "It's done", "Complete"],
    YesNoForCompletion.No: ["No", "no" "It's not done yet", "Not complete", "Not enough information", "I need more time", "I want to keep on interviewing"]
}

YES_NO_COMPLETION_ROUTER = None

def get_yes_no_completion_router() -> IntentRouter:
    global YES_NO_COMPLETION_ROUTER

    if YES_NO_COMPLETION_ROUTER is None:
        context = CategoricalIntentContext(YesNoForCompletion, yes_no_refinement_completion_examples)
        YES_NO_COMPLETION_ROUTER = IntentRouter(context, top_n=1)
    return YES_NO_COMPLETION_ROUTER
