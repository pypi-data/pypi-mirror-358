from __future__ import annotations

from adaptive_harmony import StringThread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adaptive_harmony import StringTurn


def validate_thread_last_assistant(thread: StringThread):
    turns = thread.get_turns()
    assert len(turns) > 0, "The thread must have at least one turn"
    assert turns[-1].role == "assistant", "The last turn must be an assistant turn"


def separate_context_from_last_user_turn(
    thread: StringThread,
    include_system_prompt: bool = False,
) -> tuple[list[StringTurn], str | None]:
    """
    Separates turns into context and last user turn.
    Includes system prompt in context if include_system_prompt is True.
    If there is no user turn, last user turn is None.
    """
    validate_thread_last_assistant(thread)
    turns = thread.get_turns()
    user_question = None
    user_question_idx = -1
    # find last user turn
    for i, turn in enumerate(turns):
        if turn.role == "user":
            user_question = turn.content
            user_question_idx = i
    # take up to last turn if there was no user
    # or up to last user turn if there was
    if not include_system_prompt and turns[0].role == "system":
        turns = turns[1:]

    context_turns = (
        [turn for turn in turns[:-1]] if user_question is None else [turn for turn in turns[:user_question_idx]]
    )

    return context_turns, user_question
