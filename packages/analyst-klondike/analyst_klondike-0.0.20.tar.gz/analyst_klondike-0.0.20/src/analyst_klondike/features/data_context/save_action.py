from dataclasses import dataclass
import json
from typing import Any

from analyst_klondike.features.data_context.data_state import TestCaseState
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


@dataclass
class SaveAction(BaseAction):
    type = "SAVE_ACTION"


def save_to_json(state: AppState):
    with open(state.current.opened_file_path,
              encoding='utf-8',
              mode='w') as f:
        data = _create_json(state)
        json.dump(data, f, indent=4, ensure_ascii=False)


def _create_json(state: AppState) -> Any:
    def _get_tasks(quiz_id: str):
        return (
            t for t in state.data.tasks.values() if t.quiz_id == quiz_id
        )

    d = {  # type: ignore
        "quiz_info": {
            "min_supported_app_version": state.current.opened_file_min_supported_app_version
        },
        "user_info": {
            "email": state.user_email
        },
        "quizes": [
            {
                "id": quiz.id,
                "title": quiz.title,
                "questions": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "text": t.description,
                        "code_template": t.code_template,
                        "code": t.code,
                        "test_cases": _test_cases_to_json(t.test_cases),
                        "is_passed": t.is_passed
                    } for t in _get_tasks(quiz.id)
                ]
            } for quiz in state.data.quizes.values()
        ]
    }
    return d  # type: ignore


def _test_cases_to_json(cases: list[TestCaseState]) -> list[dict[str, dict[str, str]]]:
    test_cases: list[dict[str, dict[str, str]]] = []
    for c in cases:
        test_cases_dict: dict[str, dict[str, str]] = {}
        for inp in c.inputs:
            test_cases_dict[inp.param_name] = {
                "value": inp.param_value,
                "type": inp.param_type
            }
        test_cases_dict["expected"] = {
            "value": c.expected.param_value,
            "type": c.expected.param_type
        }
        test_cases.append(test_cases_dict)
    return test_cases
