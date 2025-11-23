from typing import Any

from app.schemas.errors import ErrorCode, ErrorResponse


def error_response(code: ErrorCode, message: str, description: str = "Ошибка выполнения") -> dict[str, Any]:
    """Генерирует структуру ответа для одной ошибки (example)."""
    return {
        "model": ErrorResponse,
        "description": description,
        "content": {"application/json": {"example": {"error": {"code": code, "message": message}}}},
    }


create_pr_responses = {
    201: {"description": "PR создан"},
    404: error_response(ErrorCode.NOT_FOUND, "author not found", "Автор/команда не найдены"),
    409: error_response(ErrorCode.PR_EXISTS, "PR id already exists", "PR уже существует"),
}

merge_pr_responses = {
    200: {"description": "PR в состоянии MERGED"},
    404: error_response(ErrorCode.NOT_FOUND, "PR not found", "PR не найден"),
}

# Сложный случай с множественными примерами (examples)
reassign_pr_responses = {
    200: {"description": "Переназначение выполнено"},
    404: error_response(ErrorCode.NOT_FOUND, "PR or user not found", "PR или пользователь не найден"),
    409: {
        "model": ErrorResponse,
        "description": "Нарушение доменных правил переназначения",
        "content": {
            "application/json": {
                "examples": {
                    "merged": {
                        "summary": "PR уже слит",
                        "value": {"error": {"code": ErrorCode.PR_MERGED, "message": "cannot reassign on merged PR"}},
                    },
                    "not_assigned": {
                        "summary": "Ревьювер не назначен",
                        "value": {"error": {"code": ErrorCode.NOT_ASSIGNED, "message": "user is not a reviewer"}},
                    },
                    "no_candidate": {
                        "summary": "Нет кандидатов",
                        "value": {
                            "error": {"code": ErrorCode.NO_CANDIDATE, "message": "no active replacement candidate"}
                        },
                    },
                }
            }
        },
    },
}
