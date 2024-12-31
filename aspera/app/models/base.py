import re
import uuid

from sqlalchemy import Column, DateTime, UUID, MetaData

from sqlalchemy.sql import func, text
from sqlalchemy.ext.declarative import as_declarative, declared_attr


def camel_to_snake(name):
    # 找到大写字母并在其前面加上下划线，然后将所有字母转换为小写
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 处理连续的大写字母情况（例如，HTTPResponse -> http_response）
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


@as_declarative()
class Base:
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4())
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)
