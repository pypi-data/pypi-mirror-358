# CLAUDE.md

## Development Commands

```bash
# Testing
python -m pytest tests/ -v

# Code Quality  
mypy flake8_elegant_objects/
ruff check flake8_elegant_objects/
ruff format flake8_elegant_objects/

# Plugin Usage
python -m flake8_elegant_objects --show-source path/to/files/*.py
flake8 --select=EO path/to/files/
```

## Architecture

Flake8 plugin enforcing Elegant Objects principles (27 error codes EO001-EO027).

**Core Components:**
- `__init__.py`: ElegantObjectsPlugin orchestrating analysis
- `base.py`: Principles base class, Violations type, ErrorCodes (EO001-EO027)
- `no_er_name.py`: NoErName (EO001-EO004) 
- `no_mutable_objects.py`: NoMutableObjects (EO008, EO015-EO027)
- Other principle checkers: (EO005-EO007, EO009-EO014)

**Pattern:** Plugin uses Principles which provides Violations (no None)

## Error Codes

### Naming Violations (EO001-EO004)
- **EO001**: Class name violates -er principle
- **EO002**: Method name violates -er principle
- **EO003**: Variable name violates -er principle
- **EO004**: Function name violates -er principle

### Object Behavior (EO005-EO007)
- **EO005**: Null (None) usage
- **EO006**: Code in constructor
- **EO007**: Getter/setter methods

### Mutable Object Violations (EO008, EO015-EO027)
- **EO008**: Mutable dataclass violation
- **EO015**: Mutable class attribute violation
- **EO016**: Mutable instance attribute violation
- **EO017**: Instance attribute mutation violation
- **EO018**: Augmented assignment mutation violation
- **EO019**: Mutating method call violation
- **EO020**: Subscript assignment mutation violation
- **EO021**: Chained mutation violation
- **EO022**: Missing factory methods violation
- **EO023**: Mutable default argument violation
- **EO024**: Missing immutability enforcement violation
- **EO025**: Copy-on-write violation
- **EO026**: Aliasing violation (exposing mutable state)
- **EO027**: Defensive copy violation

### Design and Architecture (EO009-EO014)
- **EO009**: Static methods
- **EO010**: isinstance/type casting
- **EO011**: Public methods without contracts
- **EO012**: Test methods with non-assertThat statements
- **EO013**: ORM/ActiveRecord patterns
- **EO014**: Implementation inheritance

## Elegant Objects Principles

**MUST follow:**
- No null (None) - use empty lists instead
- No code in constructors  
- No getters/setters
- No mutable objects
- NO "-ER" NAMES: Manager, Controller, Helper, Handler, Parser, etc
- No static methods
- No instanceof/type casting  
- No public methods without contracts
- No statements in test methods except assertThat
- No ORM/ActiveRecord
- No implementation inheritance

**Philosophy:**
- Objects are living partners, not data containers
- Declarative over imperative (`new Sorted(apples)` not `new Sorter().sort(apples)`)
- Fail fast with exceptions, not null checks
- Composition over inheritance
- Immutability implied by design, not keywords

## Code Style

- No useless comments
- Types: `Violations = list[Violation]`
- Return empty lists `[]` instead of `None`
- Extend lists instead of checking for None