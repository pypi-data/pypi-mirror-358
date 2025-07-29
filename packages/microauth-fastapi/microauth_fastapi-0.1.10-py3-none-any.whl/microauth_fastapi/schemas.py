import uuid
from pydantic import BaseModel, Field, EmailStr, HttpUrl


class User(BaseModel):
    class Config:
        validate_by_name = True

    sub: uuid.UUID = Field(
        title='ID',
        description='The unique ID of the user.',
        alias='id'
    )
    email: EmailStr = Field(
        title='Email',
        description='Email address.'
    )
    given_name: str = Field(
        title='Given Name',
        description='Given name or the first name of the user.'
    )
    family_name: str = Field(
        title='Family Name',
        description='Family name or the last name of the user.'
    )
    name: str = Field(
        title='Name',
        description='Full name of the user.'
    )
    picture: HttpUrl = Field(
        title='Picture URL',
        description='The profile picture URL of the user.'
    )
    email_verified: bool = Field(
        title='Email Verified',
        description='Boolean value to indicate either the email is verified or not.'
    )
    roles: list[str] = Field(
        title='Roles',
        description='List of roles if any.',
        default=[],
        example=['admin', 'editor', 'customer']
    )
    permissions: list[str] = Field(
        title='Permissions',
        description='List of permissions if any.',
        default=[],
        example=['invoice:read', 'invoice:write', 'invoice:delete']
    )
    tenant_id: uuid.UUID = Field(
        title='Tenant ID',
        description='The ID of the tenant to which the user belongs.'
    )
    updated_at: int = Field(
        title='Updated At',
        description='The timestamp when the user object was updated.'
    )
