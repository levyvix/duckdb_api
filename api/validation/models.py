from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class User(BaseModel):
    id: int | None = None
    name: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    address: dict = Field(...)
    phone: str
    website: str
    company: dict
    model_config = ConfigDict(from_attributes=True)


class Post(BaseModel):
    id: int | None = None
    user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: "userId" if field_name == "user_id" else field_name,
    )


class Comment(BaseModel):
    id: int | None = None
    post_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    body: str = Field(..., min_length=1)
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: "postId" if field_name == "post_id" else field_name,
    )


class Todo(BaseModel):
    id: int | None = None
    user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)
    completed: bool
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: "userId" if field_name == "user_id" else field_name,
    )


class Album(BaseModel):
    id: int | None = None
    user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: "userId" if field_name == "user_id" else field_name,
    )


class Photo(BaseModel):
    id: int | None = None
    album_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)
    url: HttpUrl
    thumbnail_url: HttpUrl
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: {"album_id": "albumId", "thumbnail_url": "thumbnailUrl"}.get(
            field_name, field_name
        ),
    )


class TestModel(BaseModel):
    """Test model for testing purposes."""

    id: int | None = None
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)
