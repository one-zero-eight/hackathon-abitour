"""
Модуль для работы с пользователями. Например, позволяет получить данные текущего пользователя.
"""

__all__ = ["router"]

from beanie import PydanticObjectId

from src.api.custom_router_class import EnsureAuthenticatedAPIRouter
from src.api.dependencies import UserDep, ModeratorDep
from src.exceptions import NotEnoughPermissionsException, ObjectNotFound
from src.logging_ import logger
from src.modules.files.repository import upload_file_from_fastapi
from src.modules.review.repository import review_repository
from src.modules.review.schemas import ReviewWithOrganizationInfo
from src.modules.user.repository import user_repository
from src.modules.user.schemas import ViewUser
from fastapi import Request, UploadFile

router = EnsureAuthenticatedAPIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    responses={200: {"description": "Данные пользователя"}},
)
async def get_me(user: UserDep) -> ViewUser:
    """
    Получить данные текущего пользователя
    """
    return ViewUser.model_validate(user.model_dump())


@router.get(
    "/me/reviews",
    responses={200: {"description": "Отзывы пользователя"}},
)
async def get_my_reviews(user: UserDep) -> list[ReviewWithOrganizationInfo]:
    """
    Получить отзывы пользователя
    """
    return await review_repository.read_for_me(user.id)


@router.put("/me/set-documents", responses={200: {"description": "Документы успешно загружены"}})
async def set_documents(user: UserDep, documents: list[PydanticObjectId]) -> None:
    """
    Установить документы пользователя
    """
    await user_repository.set_documents(user.id, documents)


@router.put(
    "/me/request-approvement/{organization_id}",
    responses={200: {"description": "Запрос на подтверждение успешно отправлен"}},
)
async def request_approvement(
    user: UserDep, organization_id: PydanticObjectId, upload_file_obj: UploadFile | None = None
) -> None:
    """
    Отправить запрос на подтверждение
    """
    if upload_file_obj is not None:
        logger.info(f"Uploading file {upload_file_obj.filename}")
        file_obj = await upload_file_from_fastapi(upload_file_obj)
        await user_repository.request_approvement(user.id, organization_id=organization_id, file_obj_id=file_obj.id)
    else:
        logger.info("Requesting approvement without file")
        await user_repository.request_approvement(user.id, organization_id=organization_id)


@router.post(
    "/logout",
    responses={200: {"description": "Выход из аккаунта"}},
)
async def logout(request: Request) -> None:
    """
    Выход из аккаунта
    """
    request.session.clear()


@router.get(
    "/with-pending-approvement",
    responses={
        200: {"description": "Пользователи с ожидающим подтверждением"},
        **NotEnoughPermissionsException.responses,
    },
)
async def get_users_with_pending_approvement(_moder: ModeratorDep) -> list[ViewUser]:
    """
    Получить пользователей с ожидающим подтверждением
    """
    users = await user_repository.read_with_pending_approvement()
    return [ViewUser.model_validate(user.model_dump()) for user in users]


@router.get(
    "/by-id/{user_id}",
    responses={
        200: {"description": "Пользователь"},
        **NotEnoughPermissionsException.responses,
        **ObjectNotFound.responses,
    },
)
async def get_user_by_id(_moder: ModeratorDep, user_id: PydanticObjectId) -> ViewUser:
    """
    Получить пользователя по идентификатору
    """

    target_user = await user_repository.read(user_id)
    if target_user is None:
        raise ObjectNotFound(f"Пользователь с ID `{user_id}` не найден")
    return ViewUser.model_validate(target_user.model_dump())


@router.post(
    "/by-id/{user_id}/approve",
    responses={200: {"description": "Пользователь одобрен или отклонен"}, **NotEnoughPermissionsException.responses},
)
async def approve_user(
    moder: ModeratorDep, user_id: PydanticObjectId, is_approve: bool, comment: str | None = None
) -> ViewUser:
    """
    Одобрить или отклонить пользователя
    """

    target_user = await user_repository.approve_user(
        is_approve=is_approve, user_id=user_id, source_user_id=moder.id, comment=comment or ""
    )
    return ViewUser.model_validate(target_user.model_dump())
