import pydantic

from .base import BaseSchema


class DBGearOptions(BaseSchema):
    """Common options for Project and Environment configurations"""

    # Database construction options
    create_foreign_key_constraints: bool = pydantic.Field(
        default=True,
        description="Whether to create foreign key constraints during database construction"
    )

    # Future options can be added here
    # create_indexes: bool = True
    # validate_data_integrity: bool = True
    # enable_triggers: bool = True
