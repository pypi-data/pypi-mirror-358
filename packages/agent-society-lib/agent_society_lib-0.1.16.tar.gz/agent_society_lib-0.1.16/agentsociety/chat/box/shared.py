from agentsociety.chat.free.routers import CategoricalIntentContext, IntentRouter
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
