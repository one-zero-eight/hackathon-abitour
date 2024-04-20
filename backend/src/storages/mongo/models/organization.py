from typing import Any

from src.custom_pydantic import CustomModel
from src.storages.mongo.models.__base__ import CustomDocument


class OrganizationSchema(CustomModel):
    name: str
    "Наименование организации"
    contacts: Any = None
    "Контактные данные организации"
    documents: Any = None
    "Документы организации"


class Organization(OrganizationSchema, CustomDocument):
    pass
