"""Основной модуль приложения."""
from fastapi import FastAPI, status
from fastapi.exceptions import (
    RequestValidationError,
    HTTPException,
    ResponseValidationError,
)
from fastapi.responses import JSONResponse

from src.auth.router import router as auth_router
from src.tweet.router import router as tweet_router

app_api: FastAPI = FastAPI(title='Tweeter Clone')


@app_api.exception_handler(ResponseValidationError)
async def validation_response_exception_handler(request, exc) -> JSONResponse:
    """
    Функция для обработки исключения ResponseValidationError.

    Args:
        request: request
        exc: информация об ошибке

    Returns:
         JSONResponse: ответ с информацией об ошибке
    """
    return JSONResponse(
        content={
            'result': 'false',
            'error_type': exc.errors()[0]['type'],
            'error_message': exc.errors()[0]['msg'],
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app_api.exception_handler(RequestValidationError)
async def validation_request_exception_handler(request, exc) -> JSONResponse:
    """
    Функция для обработки исключения RequestValidationError.

    Args:
        request: request
        exc: информация об ошибке

    Returns:
         JSONResponse: ответ с информацией об ошибке
    """
    return JSONResponse(
        content={
            'result': 'false',
            'error_type': exc.errors()[0]['type'],
            'error_message': exc.errors()[0]['msg'],
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app_api.exception_handler(HTTPException)
async def http_exception_handler(request, exc) -> JSONResponse:
    """
    Функция для обработки исключения HTTPException.

    Args:
        request: request
        exc: информация об ошибке

    Returns:
         JSONResponse: ответ с информацией об ошибке
    """
    return JSONResponse(
        content={
            'result': 'false',
            'error_type': 'HTTPException',
            'error_message': exc.detail,
        },
        status_code=exc.status_code,
    )


app_api.include_router(prefix='/api', router=auth_router)
app_api.include_router(prefix='/api', router=tweet_router)
