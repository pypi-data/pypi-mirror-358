import json
from pathlib import Path
from jsonschema import validate

class _consttype:

    definitions = {}
    class _ConstTypeError(TypeError):
        pass

    def __repr__(self):
        return 'Constant type definitions.'

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self._ConstTypeError(f"Can't rebind const '{name}'")
        self.__dict__[name] = value

    def __getattr__(self, name: str):
        pass

    def __del__(self):
        self.__dict__.clear()

    def __init__(self) -> None:

        p = Path(__import__('drivers').__file__).parent / 'schema'
        for path in list(p.glob('**/*.json')):
            with path.open() as f:
                data = json.load(f)
                key = data.get('title', path.stem)
                self.definitions[key] = data
        
        if 'base' not in self.definitions:
            self.definitions['base'] = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": "https://pph_driver.com/base.schema.json",
                "title": "base",
                "description": "base",
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "string"
                    },
                    "thing_dest_address": {
                        "type": "string"
                    },
                    "message_log_id": {
                        "type": "string"
                    },
                    "request": {
                        "type": "object",
                        "properties": {
                            "thing_id": {
                                "type": "string"
                            },
                            "command_id": {
                                "type": "string"
                            },
                            "command_params": {
                                "type": "object"
                            }
                        },
                        "required": ["thing_id", "command_id", "command_params"]
                    }
                },
                "required": ["service_id", "thing_dest_address", "message_log_id", "request"]
            }
    
    def validate_schema(self, data: dict):

        validate(instance=data, schema=self.definitions['base'])
        schema_name = data['request']['command_id']
        if schema_name in self.definitions:
            validate(instance=data['request']['command_params'], schema=self.definitions[schema_name])
        else:
            return f'command_params of "{schema_name}" is not validated since JSON Schema is not defined.'

import sys
sys.modules[__name__] = _consttype()
