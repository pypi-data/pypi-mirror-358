from dataclasses import dataclass
from os.path import exists
import json


@dataclass
class UserInfoJson:
    email: str


@dataclass
class QuizInfo:
    min_supported_app_version: str = ""


@dataclass
class VariableJson:
    param_name: str
    param_type: str
    param_value: str


@dataclass
class TestCaseJson:
    inputs: list[VariableJson]
    expected: VariableJson


@dataclass
class QuestionJson:
    id: int
    title: str
    text: str
    code_template: str
    code: str
    test_cases: list[TestCaseJson]
    is_passed: str


@dataclass
class PythonQuizJson:
    id: str
    title: str
    questions: list[QuestionJson]


@dataclass
class JsonLoadResult:
    user_info: UserInfoJson
    quizes: list[PythonQuizJson]
    quiz_info: QuizInfo


def get_quiz_json(file_path: str) -> JsonLoadResult:
    if not exists(file_path):
        raise FileExistsError(f"<{file_path}> not found")
    load_result = JsonLoadResult(
        quiz_info=QuizInfo(),
        user_info=UserInfoJson(email=""),
        quizes=[]
    )
    with open(file_path, encoding='UTF-8') as f:
        json_data = json.load(f)
        load_result.user_info.email = json_data["user_info"]["email"]
        load_result.quiz_info.min_supported_app_version = json_data[
            "quiz_info"]["min_supported_app_version"]
        # map quizes
        for quiz_json in json_data["quizes"]:
            quiz_obj = PythonQuizJson(
                id=quiz_json["id"],
                title=quiz_json["title"],
                questions=[]
            )
            # map questions
            for question_json in quiz_json["questions"]:
                quiz_obj.questions.append(
                    QuestionJson(
                        id=int(question_json["id"]),
                        title=question_json["title"],
                        text=question_json["text"],
                        code_template=question_json["code_template"],
                        code=question_json["code"],
                        test_cases=_get_test_cases(
                            question_json["test_cases"]
                        ),
                        is_passed=question_json.get("is_passed", "")
                    )
                )
            load_result.quizes.append(quiz_obj)

    return load_result


def _get_test_cases(case_list: list[dict[str, dict[str, str]]]) -> list[TestCaseJson]:
    def parse_param_value(pname: str, pv: dict[str, str]) -> VariableJson:
        if "value" in pv and "type" in pv:
            return VariableJson(
                param_name=pname,
                param_type=pv["type"],
                param_value=pv["value"])
        raise ValueError(f"Unsupported param: name = {pname}, value={str(pv)}")

    def parse_param(c: dict[str, dict[str, str]]) -> TestCaseJson:
        # ищем expected
        # ищем все остальные параметры, кроме "expected"
        expected_var = c["expected"]
        exp = VariableJson(
            param_name="expected",
            param_type=expected_var["type"],
            param_value=expected_var["value"]
        )
        inputs = [parse_param_value(input_param_name, param_val) for input_param_name,
                  param_val in c.items() if input_param_name != "expected"]

        return TestCaseJson(
            inputs=inputs,
            expected=exp
        )

    return [
        parse_param(c) for c in case_list
    ]
