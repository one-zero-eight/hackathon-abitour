__all__ = ["TelegramWidgetData", "TelegramLoginResponse"]

from pydantic import BaseModel


class TelegramWidgetData(BaseModel):
    hash: str
    id: int
    auth_date: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None

    @property
    def string_to_hash(self) -> str:
        not_null_fields = self.model_dump(exclude_none=True, exclude={"hash"})
        return "\n".join([f"{k}={not_null_fields[k]}" for k in sorted(not_null_fields.keys())])

    @property
    def encoded(self) -> bytes:
        return self.string_to_hash.encode("utf-8").decode("unicode-escape").encode("ISO-8859-1")


class TelegramLoginResponse(BaseModel):
    need_to_connect: bool
