# PynDD (Python Dynamic DSL)

A lightweight Python library for dynamic data structure parsing and manipulation using a custom Domain Specific Language (DSL).

## Installation

```bash
pip install pyndd
```

## Quick Start

```python
from pyndd.parser import parse, translate

# Basic usage
data = {'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]}
names = parse('data:users:[#name]', data=data)
print(names)  # ['Alice', 'Bob']
```

## DSL Syntax Guide

### Basic Structure

The DSL uses a colon-separated syntax: `variable:accessor1:accessor2:...`

### Accessors

#### 1. Dictionary/Object Access (`#key`)

```python
data = {'user': {'name': 'Alice', 'age': 30}}
name = parse('data:#user:#name', data=data)
print(name)  # 'Alice'
```

#### 2. List/Array Access by Index (`number`)

```python
data = {'items': ['a', 'b', 'c', 'd']}
item = parse('data:#items:1', data=data)
print(item)  # 'b'
```

#### 3. Slice Access (`[start..end]`)

```python
data = {'items': ['a', 'b', 'c', 'd', 'e']}
subset = parse('data:#items:[1..4]', data=data)
print(subset)  # ['b', 'c', 'd']

# Open-ended slices
beginning = parse('data:#items:[..2]', data=data)  # ['a', 'b']
ending = parse('data:#items:[2..]', data=data)     # ['c', 'd', 'e']
all_items = parse('data:#items:[..]', data=data)   # ['a', 'b', 'c', 'd', 'e']
```

#### 4. Map Operations (`[#key]`)

Extract specific fields from each item in a list:

```python
data = {'users': [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25}
]}
names = parse('data:#users:[#name]', data=data)
print(names)  # ['Alice', 'Bob']

ages = parse('data:#users:[#age]', data=data)
print(ages)  # [30, 25]
```

#### 5. Pattern Matching (`*pattern*`)

Match keys using wildcards:

```python
data = {
    'user_alice': {'score': 100},
    'user_bob': {'score': 85},
    'admin_charlie': {'score': 95}
}

# Get all user_* entries
users = parse('data:user_*', data=data)
print(users)  # {'user_alice': {'score': 100}, 'user_bob': {'score': 85}}

# Get scores from user_* entries
user_scores = parse('data:user_*:[#score]', data=data)
print(user_scores)  # [100, 85]
```

#### 6. Multi-Selector Operations (`[selector1,selector2,...]`)

Combine multiple selectors to extract or access multiple elements at once:

```python
# Multi-index selection
data = {'items': list(range(10))}
selected = parse('data:#items:[1,3,5]', data=data)
print(selected)  # [1, 3, 5]

# Multi-slice selection
ranges = parse('data:#items:[1..3,5..8]', data=data)
print(ranges)  # [[1, 2], [5, 6, 7]]

# Mixed selectors (indices, slices, keys)
mixed = parse('data:#items:[0,2..4,7]', data=data)
print(mixed)  # [0, [2, 3], 7]
```

#### 7. Multi-Key Dictionary Extraction

Extract multiple fields to create structured objects:

```python
users = [
    {'name': 'Alice', 'age': 30, 'job': 'engineer'},
    {'name': 'Bob', 'age': 25, 'job': 'designer'}
]

# Extract multiple keys as structured objects
subset = parse('users:[#name,#age]', users=users)
print(subset)  # [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
```

#### 8. First-Match Selector (`@variable`)

Extract first occurrence of each key across list items:

```python
# Data with inconsistent key presence
teams = [
    {'frontend': 'React', 'backend': 'Node.js', 'db': 'MongoDB'},
    {'frontend': 'Vue', 'backend': 'Python', 'mobile': 'React Native'},  
    {'backend': 'Java', 'db': 'PostgreSQL', 'cloud': 'AWS'}
]
tech_keys = ['frontend', 'backend', 'cloud']

# Find first occurrence of each key
values = parse('teams:@tech_keys', teams=teams, tech_keys=tech_keys)
print(values)  # ['React', 'Node.js', 'AWS']

# In multi-selector context - returns structured format
structured = parse('teams:[@tech_keys,]', teams=teams, tech_keys=tech_keys)
print(structured)  # [{'frontend': 'React'}, {'backend': 'Node.js'}, {'cloud': 'AWS'}]
```

#### 9. Variable-based Key Access

Use variables to specify keys dynamically:

```python
data = {'items': ['x', 'y', 'z']}
indices = [0, 2]
selected = parse('data:#items:indices', data=data, indices=indices)
print(selected)  # ['x', 'z']
```

### Complex Examples

#### Advanced Multi-Selector Combinations

```python
# Complex nested data processing
teams = [
    {'name': 'Frontend', 'lead': 'Alice', 'tech': 'React', 'size': 5},
    {'name': 'Backend', 'lead': 'Bob', 'tech': 'Python', 'budget': 100000},
    {'name': 'DevOps', 'lead': 'Charlie', 'cloud': 'AWS', 'size': 3}
]

# Extract specific fields with fallback handling
fields = ['tech', 'cloud', 'budget']
result = parse('teams:[#name,#lead,@fields]', teams=teams, fields=fields)
print(result)  
# [['Frontend', 'Backend', 'DevOps'], 
#  ['Alice', 'Bob', 'Charlie'], 
#  [{'tech': 'React'}, {'tech': 'Python'}, {'cloud': 'AWS'}]]

# Slice the results
subset = parse('teams:[#name,#lead]:[1..3]', teams=teams)
print(subset)  # [{'name': 'Backend', 'lead': 'Bob'}, {'name': 'DevOps', 'lead': 'Charlie'}]
```

#### Chaining Operations

```python
data = {
    'departments': [
        {
            'name': 'Engineering',
            'employees': [
                {'name': 'Alice', 'skills': ['Python', 'JavaScript']},
                {'name': 'Bob', 'skills': ['Java', 'C++']}
            ]
        },
        {
            'name': 'Marketing',
            'employees': [
                {'name': 'Charlie', 'skills': ['SEO', 'Content']}
            ]
        }
    ]
}

# Get all employee names
all_names = parse('data:#departments:[#employees]:[#name]', data=data)
print(all_names)  # [['Alice', 'Bob'], ['Charlie']]

# Get skills of first employee in each department
first_skills = parse('data:#departments:[#employees]:0:[#skills]', data=data)
print(first_skills)  # [['Python', 'JavaScript'], ['SEO', 'Content']]
```

#### Nested Slicing

```python
data = {
    'matrix': [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
}

# Get middle 2x2 submatrix
submatrix = parse('data:#matrix:[1..3]:[1..3]', data=data)
print(submatrix)  # [[6, 7], [10, 11]]
```

## Data Modification with `translate()`

The `translate()` function allows you to modify data using assignment operations.

### Basic Assignment

```python
data = {'user': {'name': 'Alice'}}
translate('data:#user:#age < 30', data=data)
print(data)  # {'user': {'name': 'Alice', 'age': 30}}
```

### Bulk Assignment

```python
data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
translate('data:#users:[#age] < 25', data=data)
print(data)  # {'users': [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 25}]}
```

### Copy Data Between Structures

```python
source = {'items': [1, 2, 3]}
target = {}
translate('target:#copied < source:#items', source=source, target=target)
print(target)  # {'copied': [1, 2, 3]}
```

### Multi-Selector Assignment

```python
# Assign to multiple indices at once
data = {'items': [0, 0, 0, 0, 0]}
translate('data:#items:[1,3] < [10,30]', data=data)
print(data)  # {'items': [0, 10, 0, 30, 0]}

# Copy from multi-selector to slice
source = {'values': [1, 2, 3, 4, 5]}
target = {'result': [0, 0, 0]}
translate('source:#values:[1,3,4] > target:#result:[..]', source=source, target=target)
print(target)  # {'result': [2, 4, 5]}
```

## Advanced Features

### Robust Data Handling

The DSL gracefully handles missing keys and inconsistent data structures:

```python
# Mixed data structures
data = [
    {'name': 'Alice', 'age': 25, 'role': 'Engineer'},
    {'name': 'Bob', 'role': 'Designer'},  # missing 'age'
    {'name': 'Charlie', 'age': 30}        # missing 'role'
]

# Safely extract available data
names_ages = parse('data:[#name,#age]', data=data)
print(names_ages)  
# [{'name': 'Alice', 'age': 25}, {'name': 'Bob'}, {'name': 'Charlie', 'age': 30}]
```

### Pattern-based Operations

```python
config = {
    'db_host': 'localhost',
    'db_port': 5432,
    'db_name': 'myapp',
    'cache_host': 'redis-server',
    'cache_port': 6379
}

# Get all database-related configs
db_config = parse('config:db_*', config=config)
print(db_config)  # {'db_host': 'localhost', 'db_port': 5432, 'db_name': 'myapp'}
```


## Error Handling

The parser will raise `ValueError` for malformed expressions:

```python
try:
    parse('invalid syntax here', data={})
except ValueError as e:
    print(f"Parse error: {e}")
```

## Performance Notes

- The DSL parser is lightweight and suitable for runtime data manipulation
- Complex nested operations are supported but consider performance for deeply nested structures
- Pattern matching uses Python's `fnmatch` module internally

## License

MIT License