import ast
import fnmatch
import re
from typing import Any, List, Tuple


def _resolve_get(obj: Any, key: str) -> Any:
    return obj[key] if isinstance(obj, dict) else getattr(obj, key)


def parse(expr: str, **kwargs) -> Any:
    tokens = _tokenize(expr)
    return _execute_tokens(tokens, **kwargs)


def _execute_tokens(tokens: List[Tuple[str, Any]], **kwargs) -> Any:
    value = kwargs[tokens[0][1]]
    first_slice_done = False

    for token_type, data in tokens[1:]:
        if token_type == 'identity':
            continue
        elif token_type == 'slice':
            value = _apply_slice(value, data, first_slice_done)
            first_slice_done = True
        elif token_type == 'index':
            value = value[data]
        elif token_type == 'multi':
            value = _apply_multi_selector(value, data, **kwargs)
        elif token_type in ('attr', 'map_key'):
            value = _apply_key_selector(value, data)
        elif token_type == 'map_keys_var':
            keys = kwargs[data]
            value = [value[k] for k in keys]
        elif token_type == 'at_var':  # NEW: @ syntax
            keys = kwargs[data]
            value = _apply_at_selector(value, keys)
        else:
            raise RuntimeError(f'Unknown token type: {token_type}')

    return value


def _apply_at_selector(value: Any, keys: List[Any]) -> List[Any]:
    """Apply @ selector to extract first occurrence of each key across items."""
    if isinstance(value, list):
        result = []
        for key in keys:
            # Find first item that has this key
            for item in value:
                if isinstance(item, dict) and key in item:
                    result.append(item[key])
                    break
        return result
    elif isinstance(value, dict):
        return [value.get(k) for k in keys if k in value]
    else:
        raise ValueError(f"@ selector requires list or dict, got {type(value)}")


def _apply_slice(value: Any, slice_data: Tuple[int, int], first_slice_done: bool) -> Any:
    s, e = slice_data
    if isinstance(value, dict):
        return {k: v[s:e] for k, v in value.items()}
    elif not first_slice_done:
        return value[s:e]
    else:
        return [elem[s:e] for elem in value]


def _apply_multi_selector(value: Any, subs: List[Tuple[str, Any]], **kwargs) -> Any:
    # Special case: single @var selector
    if len(subs) == 1 and subs[0][0] == 'at_var':
        return _apply_single_selector(value, subs[0][0], subs[0][1], **kwargs)

    results = []
    keys = []

    for sub_type, sub_data in subs:
        sub_val = _apply_single_selector(value, sub_type, sub_data, **kwargs)
        results.append(sub_val)
        # Handle @var case for keys
        if sub_type == 'at_var':
            keys.extend(kwargs[sub_data])
        else:
            keys.append(sub_data)

    # Transform to list-of-dict if conditions are met
    if (_should_transform_to_dict(results, subs)):
        return _create_dict_records(results, keys)
    else:
        return results


def _apply_single_selector(value: Any, selector_type: str, selector_data: Any, **kwargs) -> Any:
    if selector_type == 'slice':
        s, e = selector_data
        return value[s:e]
    elif selector_type == 'index':
        return value[selector_data]
    elif selector_type in ('map_key', 'attr'):
        return _apply_key_selector(value, selector_data)
    elif selector_type == 'map_keys_var':
        keys = kwargs[selector_data]
        return [value[k] for k in keys]
    elif selector_type == 'at_var':  # NEW: @ syntax in multi-selector
        keys = kwargs[selector_data]
        # For multi-selector, return a list of dicts with one key-value per dict
        result = []
        for key in keys:
            # Find first item that has this key
            for item in value:
                if isinstance(item, dict) and key in item:
                    result.append({key: item[key]})
                    break
        return result
    else:
        raise RuntimeError(f'Unknown selector type: {selector_type}')


def _apply_key_selector(value: Any, key: str) -> Any:
    if isinstance(value, dict) and any(ch in key for ch in '*?'):
        return {k: v for k, v in value.items() if fnmatch.fnmatch(k, key)}
    elif isinstance(value, list):
        result = []
        for item in value:
            try:
                result.append(_resolve_get(item, key))
            except (KeyError, AttributeError):
                # Skip items that don't have the key/attribute
                continue
        return result
    else:
        return _resolve_get(value, key)


def _should_transform_to_dict(results: List[Any], subs: List[Tuple[str, Any]]) -> bool:
    # Modified to handle @var case
    if not all(isinstance(r, list) for r in results):
        return False
    if len({len(r) for r in results}) != 1:
        return False
    # Check if all selectors are key-like (including @var)
    for st, _ in subs:
        if st not in ('map_key', 'attr', 'at_var'):
            return False
    return True


def _create_dict_records(results: List[List[Any]], keys: List[Any]) -> List[dict]:
    record_len = len(results[0])
    row_wise = []

    # Flatten keys if they contain lists (from @var)
    flat_keys = []
    for k in keys:
        if isinstance(k, list):
            flat_keys.extend(k)
        else:
            flat_keys.append(k)

    # Create dict records
    idx = 0
    for i in range(record_len):
        row = {}
        for j, result_list in enumerate(results):
            if j < len(keys) and isinstance(keys[j], list):
                # This result came from @var, might have multiple values
                num_keys = len(keys[j])
                for k_idx, key in enumerate(keys[j]):
                    if idx+k_idx < len(result_list):
                        row[key] = result_list[idx+k_idx]
                idx += num_keys
            else:
                row[flat_keys[j]] = result_list[i]
        row_wise.append(row)
    return row_wise


def _needs_parsing(expr: str) -> bool:
    expr = expr.strip()
    return any(ch in expr for ch in ':[') or any(ch in expr for ch in '*?@')  # Added @


def translate(expr: str, **kwargs):
    m = re.search(r'([><])', expr)
    if not m:
        raise ValueError('expression must contain < or >')
    op = m.group()
    left_raw, right_raw = (part.strip() for part in expr.split(op, 1))
    dest_raw, src_raw = (right_raw, left_raw) if op == '>' else (left_raw, right_raw)
    if _needs_parsing(src_raw):
        value = parse(src_raw, **kwargs)
    else:
        try:
            value = ast.literal_eval(src_raw)
        except Exception:
            value = kwargs[src_raw]
    if not _needs_parsing(dest_raw):
        kwargs[dest_raw] = value
    else:
        _assign(dest_raw, value, **kwargs)


def _tokenize(expr: str) -> List[Tuple[str, Any]]:
    expr = expr.replace(' ', '')
    tokens: List[Tuple[str, Any]] = []
    idx = 0

    # Skip optional '&' prefix
    if idx < len(expr) and expr[idx] == '&':
        idx += 1

    # Parse variable name
    start = idx
    while idx < len(expr) and (expr[idx].isalnum() or expr[idx] == '_'):
        idx += 1
    tokens.append(('var', expr[start:idx]))

    # Parse selectors
    while idx < len(expr):
        if expr[idx] != ':':
            raise ValueError(f'Unexpected char: {expr[idx]!r}')
        idx += 1

        if expr[idx] == '[':
            idx, token = _parse_bracket_selector(expr, idx)
            tokens.append(token)
        elif expr[idx] == '@':  # NEW: Handle @ syntax
            idx += 1
            start = idx
            while idx < len(expr) and (expr[idx].isalnum() or expr[idx] == '_'):
                idx += 1
            var_name = expr[start:idx]
            tokens.append(('at_var', var_name))
        else:
            idx, token = _parse_simple_selector(expr, idx)
            tokens.append(token)

    return tokens


def _parse_bracket_selector(expr: str, idx: int) -> Tuple[int, Tuple[str, Any]]:
    j = expr.find(']', idx)
    if j == -1:
        raise ValueError("']' not found")
    inner = expr[idx+1:j]
    idx = j+1

    # Multi-selector (comma-separated)
    if ',' in inner:
        parts = [p for p in inner.split(',') if p]  # Remove empty parts
        subs: List[Tuple[str, Any]] = []
        for p in parts:
            subs.append(_parse_selector_part(p))
        return idx, ('multi', subs)

    # Single selector
    if inner == '-':
        return idx, ('identity', None)
    elif re.fullmatch(r'(-?\d*)\.\.(-?\d*)', inner):
        s, e = inner.split('..')
        return idx, ('slice', (int(s) if s else None, int(e) if e else None))
    else:
        return idx, _parse_selector_part(inner)


def _parse_simple_selector(expr: str, idx: int) -> Tuple[int, Tuple[str, Any]]:
    start = idx
    while idx < len(expr) and expr[idx] != ':':
        idx += 1
    segment = expr[start:idx]
    return idx, _parse_selector_part(segment)


def _parse_selector_part(part: str) -> Tuple[str, Any]:
    if part.startswith('@'):  # NEW: Handle @ in selector part
        return ('at_var', part[1:])
    elif re.fullmatch(r'(-?\d*)\.\.(-?\d*)', part):
        s, e = part.split('..')
        return ('slice', (int(s) if s else None, int(e) if e else None))
    elif part.lstrip('-').isdigit():
        return ('index', int(part))
    elif part.startswith('#'):
        return ('map_key', part[1:])
    elif any(ch in part for ch in '*?'):
        return ('map_key', part)
    else:
        return ('map_keys_var', part)


def _assign(path: str, value: Any, **kwargs) -> None:
    tokens = _tokenize(path)
    var_name = tokens[0][1]
    if len(tokens) == 1:
        kwargs[var_name] = value
    else:
        _write(kwargs[var_name], tokens[1:], value, **kwargs)


def _write(obj: Any, tokens: List[Tuple[str, Any]], value: Any, **kwargs) -> None:
    value_type, data = tokens[0]
    rest = tokens[1:]

    def _iter_pairs(src, _value):
        if isinstance(_value, list) and len(_value) == len(src):
            return zip(src, _value)
        return ((item, _value) for item in src)

    if value_type in ('attr', 'map_key'):
        key = data
        if isinstance(obj, dict) and any(ch in key for ch in '*?'):
            for mk in [k for k in obj if fnmatch.fnmatch(k, key)]:
                v = value[mk] if isinstance(value, dict) and mk in value else value
                if rest:
                    _write(obj[mk], rest, v, **kwargs)
                else:
                    obj[mk] = v
            return
        if isinstance(obj, list):
            vals = value if isinstance(value, list) and len(value) == len(obj) else [value]*len(obj)
            for sub_obj, v in zip(obj, vals):
                if rest:
                    nxt = sub_obj[key] if isinstance(sub_obj, dict) else getattr(sub_obj, key)
                    _write(nxt, rest, v, **kwargs)
                else:
                    if isinstance(sub_obj, dict):
                        sub_obj[key] = v
                    else:
                        setattr(sub_obj, key, v)
            return
        if not rest:
            if isinstance(obj, dict):
                obj[key] = value
            else:
                setattr(obj, key, value)
        else:
            nxt = obj[key] if isinstance(obj, dict) else getattr(obj, key)
            _write(nxt, rest, value, **kwargs)
    elif value_type == 'index':
        idx = data
        if not rest:
            obj[idx] = value
        else:
            _write(obj[idx], rest, value, **kwargs)
    elif value_type == 'multi':
        subs = data
        vals = (value if isinstance(value, list) and len(value) == len(subs)
                else [value]*len(subs))
        for (sub_tok, sub_data), v in zip(subs, vals):
            _write(obj, [(sub_tok, sub_data)]+rest, v, **kwargs)
    elif value_type == 'slice':
        s, e = data
        sub = obj[s:e]
        if not rest:
            obj[s:e] = value
        else:
            for sub_obj, sub_value in _iter_pairs(sub, value):
                _write(sub_obj, rest, sub_value, **kwargs)
    elif value_type == 'map_keys_var':
        keys = kwargs[data]
        if not rest:
            for k, sub_value in _iter_pairs(keys, value):
                obj[k] = sub_value
        else:
            for k, sub_value in _iter_pairs(keys, value):
                _write(obj[k], rest, sub_value, **kwargs)
    elif value_type == 'at_var':  # NEW: Handle @var in write
        keys = kwargs[data]
        if not rest:
            for i, (k, sub_value) in enumerate(_iter_pairs(keys, value)):
                obj[i][k] = sub_value
        else:
            for i, (k, sub_value) in enumerate(_iter_pairs(keys, value)):
                _write(obj[i][k], rest, sub_value, **kwargs)
    elif value_type == 'identity':
        _write(obj, rest, value, **kwargs)
    else:
        raise RuntimeError(f'Unhandled token type: {value_type}')


