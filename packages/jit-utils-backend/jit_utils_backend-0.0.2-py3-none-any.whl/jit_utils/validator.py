from dataclasses import MISSING, dataclass, fields

from commons.errcode import ElementErrorCode


@dataclass
class ParamsValidator:

    def __init__(self, __fullName__, **kwargs):
        for fieldInfo in fields(self):
            fieldName = fieldInfo.name
            if fieldName not in kwargs:
                # 没有默认值
                if fieldInfo.default is MISSING:
                    raise ElementErrorCode.PARAMS_MISSING_ERROR.formatReason(fullName=__fullName__, fieldName=fieldName)

            value = kwargs.get(fieldName, fieldInfo.default)
            try:
                value = fieldInfo.type(value)
            except ValueError:
                raise ElementErrorCode.PARAMS_TYPE_ERROR.formatReason(
                    fullName=__fullName__, expect=fieldInfo.type.__name__, actual=type(value).__name__
                )
            setattr(self, fieldName, value)
        if hasattr(self, "__post_init__"):
            self.__post_init__(__fullName__)
