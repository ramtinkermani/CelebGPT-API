import json
import inspect
from typing import get_type_hints
from dataclasses import fields, is_dataclass

from Schemas import DataClasses
from Schemas.DataClasses import *
from Clients.OpenAIClient import OpenAIClient
from helpers import extract_json_from_markdown


def serialize_class_schema(cls):
    if not is_dataclass(cls):
        raise ValueError(f"{cls.__name__} is not a data class")

    schema = {
        'entity_type': cls.__name__,
        'fields': {}
    }

    for field in fields(cls):
        field_type = get_type_hints(cls)[field.name]
        module_name = field_type.__module__
        qualified_name = field_type.__qualname__

        schema['fields'][field.name] = get_entity_class_schema(qualified_name) \
            if module_name == 'DataClasses' \
            else f"{qualified_name}" \
            if hasattr(field_type, '__module__') \
            else str(field_type)
    return schema


def serialize_dataclass_to_json_schema(cls):
    """ Recursively generates a JSON schema for dataclasses """
    result = {
        'type': 'object',
        'properties': {},
    }
    hints = get_type_hints(cls)
    for field in fields(cls):
        field_type = hints[field.name]
        if hasattr(field_type, '__origin__'):  # Check if it's a generic type
            if field_type.__origin__ is list:
                element_type = field_type.__args__[0]
                result['properties'][field.name] = {
                    'type': 'array',
                    'items': serialize_dataclass_to_json_schema(element_type) if is_dataclass(element_type) else {'type': element_type.__name__.lower()}
                }
            else:
                result['properties'][field.name] = {'type': 'unknown'}
        elif issubclass(field_type, Enum):
            result['properties'][field.name] = {
                'type': 'string',
                'enum': [e.value for e in field_type]
            }
        else:
            result['properties'][field.name] = {'type': field_type.__name__.lower()}
    return result


def get_root_class_type(entity_name):
    prompt = f"""Given this entity name ```{entity_name}``` ,
                    Update the entity_name if it's misspelled ('Robert Deniro' => 'Robert De Niro').
                    Also give me the type of the entity from the following list
                    If this is now a well-known entity (Person, Movie, Song, Art work, Book, etc) nor a Celebrity, 
                    return 'None':
                 {[name for name, member in CelebTypes.__members__.items()]}
              """
    openai_client = OpenAIClient()
    result = openai_client.gptAsk({"question": prompt, "jsonOutput": True}, "{'entity_name': str, 'entity_type': str}")
    res = json.loads(extract_json_from_markdown(result))
    entity_type = res['entity_type']
    if entity_type == 'None':
        return None

    entity_name = res['entity_name']
    entity_class_name = CelebTypes[entity_type].value
    return {"entity_class_name": entity_class_name, "entity_name": entity_name}


def get_entity_class_schema(entityClassName):
    entity_classes = [obj for name, obj in inspect.getmembers(DataClasses, inspect.isclass)
                      if hasattr(obj, 'is_custom_class') and obj.is_custom_class and name == f'{entityClassName}']

    if len(entity_classes) > 0:
        return serialize_dataclass_to_json_schema(entity_classes[0])

