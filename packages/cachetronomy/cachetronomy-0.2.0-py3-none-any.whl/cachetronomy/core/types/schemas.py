from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Sequence, Type, TypeVar, override

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import SettingsConfigDict


class CacheMetadata(BaseModel):
    key: str
    fmt: str = Field('json', description='serialization format')
    expire_at: datetime
    tags: list[str] = Field(default_factory=list)
    saved_by_profile: str
    version: int = Field(1, ge=1)

    @property
    def tags_json(self) -> str:
        return json.dumps(self.tags)
    
    @model_validator(mode='before')
    @classmethod
    def check_tags(cls, values: dict[str, Any]) -> dict[str, Any]:
        DEFAULT_TAGS = ['default']  
        if values.get('tags') is None:
            values['tags'] = DEFAULT_TAGS.copy()
        return values


class CacheEntry(CacheMetadata):
    data: Any


class ExpiredEntry(BaseModel):
    key: str
    expire_at: datetime


class AccessLogEntry(BaseModel):
    key: str
    access_count: int = Field(..., ge=0)
    last_accessed: datetime
    last_accessed_by_profile: str

    model_config: SettingsConfigDict = SettingsConfigDict(frozen=True)


class EvictionLogEntry(BaseModel):
    id: int | None
    key: str
    evicted_at: datetime
    reason: str
    last_access_count: int = Field(..., ge=0)
    evicted_by_profile: str

    model_config: SettingsConfigDict = SettingsConfigDict(frozen=True)


T = TypeVar('T')

class CustomQuery(BaseModel):
    query: str
    params: Sequence[Any] | None = ()
    schema_type: Type[T] | None = Field(
        description='''
                    If provided, rows are deserialized into this model; 
                    otherwise the row dicts are returned.
                    '''
    )
    autocommit: bool = Field(
        default=False,
        description='''
                    Set True for statements that mutate the DB so a COMMIT is issued.
                    '''
    )

    @model_validator(mode='after')
    def _warn_on_write_without_commit(self):
        cmds: set = {'insert', 'update', 'delete', 'drop', 'alter'}
        lowered = self.query.lstrip().lower()
        if not self.autocommit and any(lowered.startswith(cmd) for cmd in cmds):
            raise ValueError(
                '''
                Write-query detected: set autocommit=True 
                or manage the transaction yourself.
                '''
            )
        return self