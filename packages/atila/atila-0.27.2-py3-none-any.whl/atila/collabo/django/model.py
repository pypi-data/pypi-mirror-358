import datetime
import uuid
from rs4.attrdict import AttrDict
from ...collectors.multipart_collector import FileWrapper
from django.forms.models import model_to_dict
from . import fields

TZ_LOCAL = datetime.datetime.now (datetime.timezone.utc).astimezone().tzinfo
TZ_UTC = datetime.timezone.utc

def igNone (**filter):
    k, v = filter.popitem ()
    if v is not None:
        return Q (**filter)
    else:
        return Q ()

def utcnow ():
    return datetime.datetime.now ().astimezone (TZ_UTC)


try:
    from django.db.models import Q
    from django.db.models.fields import NOT_PROVIDED
    from django.db import models
    from django.core.exceptions import ValidationError

    _support_array_field = True
    try:
        from django.contrib.postgres.fields import ArrayField
    except ImportError:
        _support_array_field = False


    TYPE_MAP = [
        (models.URLField, str, 'url'),
        (models.UUIDField, uuid.UUID, 'uuid'),
        (models.FileField, FileWrapper, 'file'),
        (models.EmailField, str, 'email'),
        (models.DateTimeField, datetime.datetime, 'datetime'),
        (models.DateField, datetime.date, 'date'),
        (models.TimeField, datetime.time, 'time'),
        ((models.CharField, models.TextField, fields.CompressedTextField), str, 'str'),
        (models.JSONField, str, 'json'),
        (models.IntegerField, int, 'int'),
        ((models.FloatField, models.DecimalField), float, 'float'),
        (models.BooleanField, bool, 'bool'),
    ]
    if _support_array_field:
        TYPE_MAP.append ((ArrayField, list, 'list'))

except ImportError:
    from rs4.annotations import Uninstalled
    AtilaModel = Uninstalled ('django')

else:
    _TABLE_INFO_CACHE = {}

    class TableInfo:
        def __init__ (self, name, columns):
            self.name = name
            self.columns = columns
            self.pk = None
            self.fks = {}

            for field in self.columns.values ():
                if field.pk:
                    self.pk = field
                if field.related_model:
                    self.fks [field.name] = (field.column, field.related_model)


    class AtilaModel (models.Model):
        class Meta:
            abstract = True

        def dict (self, fields = None, exclude = None):
            d = model_to_dict (self, fields, exclude)
            for k in self.get_columns (): # add auto fields which ignored by model_to_dict
                if k in d or (fields and k not in fields):
                    continue
                d [k] = getattr (self, k)
            return d

        def set (self, __donot_use_this_variable__ = None, **payload):
            if isinstance (__donot_use_this_variable__, dict):
                assert not payload, "provided dict, keyword args is not avaliable"
                payload = __donot_use_this_variable__
            return self.validate_payload (payload, True)

        def validate_payload (self, payload, _set = False):
            ti = self.get_table_info ()
            for field in ti.columns.values ():
                curval = getattr (self, field.name)
                if (field.pk or field.related):
                    if field.name in payload:
                        raise ValidationError ('field {} has relation ship'.format (field.name))
                    continue

                if field.type_name == 'datetime':
                    if field.auto_now:
                        if field.name in payload:
                            raise ValidationError ('field {} is auto field'.format (field.name))
                        else:
                            continue
                    if field.auto_now_add:
                        if field.name in payload:
                            raise ValidationError ('field {} is auto field'.format (field.name))
                        else:
                            continue

                if field.name not in payload:
                    if not field.null and field.default is NOT_PROVIDED:
                        if not curval:
                            raise ValidationError ('field {} is missing'.format (field.name))
                    continue

                value = payload [field.name]
                if not field.null and value is None:
                    raise ValidationError ('field {} should not be NULL'.format (field.name))
                if not field.blank and value == '':
                    raise ValidationError ('field {} should not be blank'.format (field.name))

                if value == '' and field.null:
                    payload [field.name] = value = None

                if value is None:
                    continue

                if field.type and not isinstance (value, field.type):
                    raise ValidationError ('field {} type should be {}'.format (field.name, field.type_name))

                if field.choices:
                    if isinstance (field.choices [0], (list, tuple)):
                        choices = [item [0] for item in field.choices]
                    else:
                        choices = field.choices
                    if value not in choices:
                        raise ValidationError ('field {} has invalid value'.format (field.name))

                if field.validators:
                    for validate_func in field.validators:
                        validate_func (value)

            for k in payload:
                if '__' in k: # join update
                    continue
                if k not in ti.columns:
                    raise ValidationError ('field {} is not valid field'.format (k))

            if _set:
                for k, v in payload.items ():
                    setattr (self, k, v)

            return payload

        @classmethod
        def get_table_name (cls):
            return cls._meta.db_table

        @classmethod
        def get_columns (cls):
            return list (cls.get_table_info ().columns.keys ())

        @classmethod
        def get_pk (cls):
            return cls.get_table_info ().pk.column

        @classmethod
        def get_fks (cls):
            return cls.get_table_info ().fks

        @classmethod
        def get_table_info (cls):
            table_name = cls.get_table_name ()
            if table_name not in _TABLE_INFO_CACHE:
                _TABLE_INFO_CACHE [table_name] = TableInfo (table_name, cls.get_fields ())
            return _TABLE_INFO_CACHE [table_name]

        @classmethod
        def get_fields (cls):
            table_name = cls.get_table_name ()
            if table_name in _TABLE_INFO_CACHE:
                return _TABLE_INFO_CACHE [table_name].columns

            columns = {}
            for field in cls._meta.fields:
                field_type = None
                field_type_name = None
                for ftype, ptype, name in TYPE_MAP:
                    if isinstance (field, ftype):
                        field_type = ptype
                        field_type_name = name
                        break

                columns [field.name] = AttrDict (dict (
                    related = field.many_to_many or field.many_to_one or field.one_to_many or field.one_to_one,
                    column = field.column,
                    verbose_name = field.verbose_name,
                    type = field_type,
                    type_name = field_type_name,
                    pk = field.primary_key,
                    unique = field.unique,
                    max_length = None if field_type_name in ('file',) else field.max_length,
                    null = field.null,
                    blank = field.blank,
                    choices = field.choices,
                    help_text = field.help_text,
                    validators = field.validators,
                    default = field.default,
                    name = field.name,
                    related_model = field.related_model,
                    auto_now_add = field_type_name == 'datetime' and field.auto_now_add or False,
                    auto_now = field_type_name == 'datetime' and field.auto_now or False,
                    editable = field.editable,
                ))
            return columns

        @classmethod
        def get_field_spec (cls):
            columns = {}
            for k, field in cls.get_fields ().items ():
                if field.pk or field.related:
                    continue
                if field.auto_now or field.auto_now_add:
                    continue

                columns [k] = dict (
                    key = field.name,
                    name = field.verbose_name,
                    type = field.type_name,
                )
                if field.validators:
                    validators = []
                    for it in field.validators:
                        validator = it.__name__ if hasattr (it, '__name__') else it.__class__.__name__
                        if validator not in ("MaxLengthValidator",):
                            validators.append (validator)
                    if validators:
                        columns [k]['validators'] = validators

                if field.null or field.default is not NOT_PROVIDED:
                    columns [k]['null'] = True
                if field.blank:
                    columns [k]['blank'] = True
                if field.default is not NOT_PROVIDED:
                    columns [k]['default'] = field.default
                if field.choices:
                    columns [k]['choices'] = field.choices
                if field.max_length:
                    columns [k]['maxlen'] = field.max_length
                if field.help_text:
                    columns [k]['help'] = field.help_text

            return columns
