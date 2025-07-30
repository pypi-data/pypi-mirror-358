from dataclasses import dataclass, field
from typing import Any, MutableMapping, TypeAlias
from typing_extensions import Self

from yupy.icomparable_schema import EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.locale import locale
from yupy.schema import Schema
from yupy.util.concat_path import concat_path
from yupy.validation_error import ValidationError, Constraint

__all__ = ('MappingSchema',)

_SchemaShape: TypeAlias = MutableMapping[str, ISchema[Any]]


@dataclass
class MappingSchema(EqualityComparableSchema):
    _type: _SchemaExpectedType = field(init=False, default=dict)
    _fields: _SchemaShape = field(init=False, default_factory=dict)

    # @property
    # def fields(self) -> _SchemaShape:
    #     return self._fields

    def shape(self, fields: _SchemaShape) -> Self:
        if not isinstance(fields, dict):  # Перевірка залишається на dict, оскільки shape визначається через dict
            raise ValidationError(
                Constraint("shape", locale["shape"])
            )
        for key, item in fields.items():
            if not isinstance(item, ISchema):
                raise ValidationError(
                    Constraint("shape_values", locale["shape_values"]),
                    key,
                    invalid_value=item
                )
        self._fields = fields
        return self

    def validate(self, value: Any, abort_early: bool = True, path: str = "~") -> Any:
        super().validate(value, abort_early, path)
        return self._validate_shape(value, abort_early, path)

    def _validate_shape(self, value: MutableMapping[str, Any],
                        abort_early: bool = True,
                        path: str = "~") -> MutableMapping[str, Any]:

        errs: list[ValidationError] = []
        for k, f in self._fields.items():
            path_ = concat_path(path, k)
            try:
                if k not in value:
                    if not self._fields[k]._optional:
                        raise ValidationError(
                            Constraint("required", self._fields[k]._required, path_),
                            path_, invalid_value=value
                        )

                    value[k] = self._fields[k].validate(None, abort_early, path_)
                else:
                    value[k] = self._fields[k].validate(value[k], abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    raise ValidationError(err.constraint, path_, invalid_value=value)
                errs.append(err)
        if errs:
            raise ValidationError(
                Constraint('object', 'invalid object', path),
                path, errs, invalid_value=value
            )
        return value

    def __getitem__(self, item: str) -> ISchema:
        return self._fields[item]
