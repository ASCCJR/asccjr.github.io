"""Restricted, non-executing source analysis for exception risk after field removal.

Conditional on exact built-in dict responses, required string fields, and this tiny
Python subset. Unsupported syntax -> UNKNOWN. This is not a security sandbox or
an analyzer for arbitrary Python, OpenAPI, semantic correctness or production.
"""
from __future__ import annotations
import ast
import hashlib
from typing import Any

VERSION = 'bounded-source-1'

class Unsupported(ValueError):
    pass

class ModeledException(Exception):
    pass


def source_hash(source: str) -> str:
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def analyze(source: str, before: dict, after: dict) -> dict[str, Any]:
    result = {'version': VERSION, 'answer': 'UNKNOWN', 'basis': 'unsupported',
              'before': None, 'after': None, 'field_references': [],
              'scope': 'exact_builtin_dict_required_strings_no_external_effects'}
    try:
        if not isinstance(source, str) or len(source.encode()) > 16000:
            raise Unsupported('source_size')
        tree = ast.parse(source)
        if sum(1 for _ in ast.walk(tree)) > 256:
            raise Unsupported('node_limit')
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
            raise Unsupported('one_function_required')
        fn = tree.body[0]
        args = fn.args
        if (fn.decorator_list or len({a.arg for a in args.args}) != 2 or len(args.args) != 2 or args.posonlyargs or args.kwonlyargs
                or args.vararg or args.kwarg or args.defaults or args.kw_defaults):
            raise Unsupported('unsupported_signature')
        body_name = args.args[0].arg
        schemas = []
        for schema in (before, after):
            if (set(schema) != {'type', 'properties', 'required', 'additionalProperties'}
                    or schema['type'] != 'object' or schema['additionalProperties'] is not False
                    or not isinstance(schema['properties'], dict)
                    or set(schema['required']) != set(schema['properties'])
                    or any(v != {'type': 'string'} for v in schema['properties'].values())):
                raise Unsupported('exact_string_response_contract_required')
            schemas.append(set(schema['properties']))
        refs = set()
        def expression(node, fields, check_only=False):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str): return 'STR'
                if node.value is None: return 'NONE'
            if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == body_name:
                if not isinstance(node.slice, ast.Constant) or not isinstance(node.slice.value, str):
                    raise Unsupported('dynamic_field')
                refs.add(node.slice.value)
                if not check_only and node.slice.value not in fields: raise ModeledException('KeyError')
                return 'STR'
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                left = expression(node.left, fields, check_only)
                right = expression(node.right, fields, check_only)
                if not check_only and (left, right) != ('STR', 'STR'): raise ModeledException('TypeError')
                return 'STR'
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and not node.keywords:
                obj = node.func.value
                if node.func.attr == 'get' and isinstance(obj, ast.Name) and obj.id == body_name:
                    if (len(node.args) not in (1, 2) or not isinstance(node.args[0], ast.Constant)
                            or not isinstance(node.args[0].value, str)):
                        raise Unsupported('get_shape')
                    key = node.args[0].value
                    refs.add(key)
                    default = 'NONE'
                    if len(node.args) == 2:
                        if not isinstance(node.args[1], ast.Constant): raise Unsupported('get_default')
                        default = expression(node.args[1], fields, check_only)
                    return 'STR' if check_only or key in fields else default
                if node.func.attr in {'upper', 'lower'} and not node.args:
                    kind = expression(obj, fields, check_only)
                    if not check_only and kind != 'STR': raise ModeledException('AttributeError')
                    return 'STR'
            raise Unsupported('expression:' + type(node).__name__)
        def statement(nodes, fields, check_only=False):
            # Validate ALL branches before computing any result; unsupported code is never ignored.
            if len(nodes) != 1: raise Unsupported('single_return_or_try_required')
            node = nodes[0]
            if isinstance(node, ast.Return): return expression(node.value, fields, check_only)
            if isinstance(node, ast.Try):
                if (node.orelse or node.finalbody or len(node.handlers) != 1
                        or not isinstance(node.handlers[0].type, ast.Name)
                        or node.handlers[0].type.id != 'KeyError' or node.handlers[0].name):
                    raise Unsupported('handler_shape')
                if check_only:
                    statement(node.body, fields, True)
                    statement(node.handlers[0].body, fields, True)
                    return 'STR'
                try: return statement(node.body, fields)
                except ModeledException as error:
                    if str(error) != 'KeyError': raise
                    return statement(node.handlers[0].body, fields)
            raise Unsupported('statement:' + type(node).__name__)
        statements = fn.body
        if statements and isinstance(statements[0], ast.Expr) and isinstance(statements[0].value, ast.Constant) and isinstance(statements[0].value.value, str):
            statements = statements[1:]
        statement(statements, schemas[0], True)
        outcomes = []
        for fields in schemas:
            try:
                statement(statements, fields)
                outcomes.append('COMPLETES')
            except ModeledException as error:
                outcomes.append(str(error))
        result.update(before=outcomes[0], after=outcomes[1], field_references=sorted(refs))
        if outcomes[0] != 'COMPLETES':
            result['basis'] = 'baseline_not_established'
        else:
            result.update(answer='NO' if outcomes[1] == 'COMPLETES' else 'YES', basis='bounded_source_inference')
    except (Unsupported, SyntaxError, RecursionError, ValueError, TypeError, KeyError) as error:
        result['basis'] = str(error)
    return result
