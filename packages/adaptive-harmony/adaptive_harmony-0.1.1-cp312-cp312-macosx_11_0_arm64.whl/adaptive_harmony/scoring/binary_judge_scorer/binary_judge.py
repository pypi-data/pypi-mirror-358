from pydantic import BaseModel, Field
from typing import Literal
import json

from adaptive_harmony import StringThread, InferenceModel
from adaptive_harmony.core.utils import SingleTurnShot, stringify_thread
from adaptive_harmony.scoring import Scorer, ScoreWithMetadata
from adaptive_harmony.scoring.binary_judge_scorer.prompts import BinaryJudgeShot, SYSTEM, USER, DEFAULT_SHOTS
from adaptive_harmony.scoring.exceptions import IgnoreScoreException
from adaptive_harmony.scoring.utils import validate_thread_last_assistant, separate_context_from_last_user_turn


class BinaryJudgeOutput(BaseModel):
    reasoning: str = Field(description="Reasoning to support the rationale behind the score")
    score: Literal["PASS", "FAIL", "NA"] = Field(description="The score for the sample")


class BinaryJudgeScorer(Scorer):
    """
    Binary judge for scoring samples as PASS, FAIL or NA using few-shot prompting.
    If custom shots are provided, they are used instead of the default shots.
    """

    def __init__(
        self,
        model: InferenceModel,
        criteria: str,
        shots: list[BinaryJudgeShot] | None = None,
    ):
        self.model = model
        self.criteria = criteria
        # Score mapping
        self.scores_map = dict(PASS=1.0, FAIL=0.0)

        self._original_shots = shots or DEFAULT_SHOTS
        self._shots = self.format_user_shots(shots or DEFAULT_SHOTS)

    @property
    def shots(self) -> list[BinaryJudgeShot]:
        return self._original_shots

    @shots.setter
    def shots(self, shots: list[BinaryJudgeShot]):
        self._original_shots = shots
        self._shots = self.format_user_shots(shots)

    @staticmethod
    def extract_user_template_kwargs(thread: StringThread) -> dict[str, str]:

        validate_thread_last_assistant(thread)
        # Separate conversation context from last user turn
        context_turns, user_question = separate_context_from_last_user_turn(thread)
        context_str = stringify_thread(StringThread(context_turns))
        completion = thread.last_content()

        assert user_question, "There must be at least one user turn"
        return dict(
            context=context_str,
            user_question=user_question,
            completion=completion,
        )

    def format_user_shots(self, shots: list[BinaryJudgeShot]) -> list[SingleTurnShot]:
        """
        Turn a possibly multi turn example into a single turn one,
        with appropriate kwargs to format the task's prompt templates
        """
        new_shots: list[SingleTurnShot] = []
        for shot in shots:
            user_template_kwargs = self.extract_user_template_kwargs(shot.thread)
            user_template_kwargs["criteria"] = shot.criteria or self.criteria
            single_turn_shot = SingleTurnShot(
                user=user_template_kwargs,
                assistant={
                    "json_answer": self.model.render_pydantic_model(
                        BinaryJudgeOutput(
                            reasoning=shot.reasoning,
                            score=shot.score,
                        )
                    )
                },
            )
            new_shots.append(single_turn_shot)

        return new_shots

    def get_judge_prompt(self, thread: StringThread) -> StringThread:
        """Build the judging prompt for a given sample."""
        # build the real user template kwargs
        user_template_kwargs = self.extract_user_template_kwargs(thread)
        user_template_kwargs["criteria"] = self.criteria
        # system kwarg
        output_json_schema = self.model.render_schema(BinaryJudgeOutput)

        # system
        prompt = StringThread().system(SYSTEM.format(json_schema=output_json_schema))
        # shots
        for shot in self._shots:
            prompt = prompt.user(USER.format(**shot["user"]))
            prompt = prompt.assistant(shot["assistant"]["json_answer"])
        # real input
        prompt = prompt.user(USER.format(**user_template_kwargs))

        return prompt

    async def score(self, sample: StringThread) -> ScoreWithMetadata:
        judging_prompt = self.get_judge_prompt(sample)
        try:
            _, parsed_output = await self.model.generate_and_validate(judging_prompt, BinaryJudgeOutput)
            float_score = self.scores_map.get(parsed_output.score)
            # NA case, ignore score
            if float_score is None:
                raise IgnoreScoreException(f"Non applicable score: {parsed_output.reasoning}")
            else:
                return ScoreWithMetadata(score=float_score, metadata={"reasoning": parsed_output.reasoning})
        except Exception as e:
            raise e

    @classmethod
    def from_playground_export(cls, model: InferenceModel, shots: list[dict], logging_name: str | None = None) -> "BinaryJudgeScorer":
        """
        Create a BinaryJudgeScorer from a list of shots exported from the Playground.

        Example of shots:
        [
            {
                "criteria": "The assistant should give a number between 1 and 10",
                "judgement": "{\n  \"reasoning\": \"The given completion is a number, but it is not between 1 and 10.\",\n  \"score\": \"FAIL\"\n}",
                "thread": [
                    [
                        "user",
                        "Give me a number"
                    ],
                    [
                        "assistant",
                        "12"
                    ]
                ]
            },
            ...
        ]
        """
        if not shots:
            raise ValueError("No shots provided")

        criteria = shots[0]["criteria"]
        for shot in shots:
            if shot["criteria"] != criteria:
                raise ValueError("All shots do not have the same criteria")


        formatted_shots = []
        for shot in shots:
            judgement = json.loads(shot["judgement"])
            formatted_shots.append(BinaryJudgeShot(
                criteria=shot["criteria"],
                reasoning=judgement["reasoning"],
                score=judgement["score"],
                thread=StringThread([tuple(turn) for turn in shot["thread"]])
            ))

        return cls(
            model=model,
            criteria=criteria,
            shots=formatted_shots,
        )
