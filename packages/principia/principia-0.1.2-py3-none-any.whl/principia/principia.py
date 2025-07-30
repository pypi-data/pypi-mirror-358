# -*- coding: utf-8 -*-
"""
principia.py: The Assertion/Error Driven Development (Principia) Engine.

Version: 6.0 (Semantic Engine)

This library provides a comprehensive framework for formalizing and verifying
software assumptions, designed to be intuitive for both human developers and
Language Learning Models (LLMs). Its goal is to eliminate entire classes of
runtime errors by forcing the declaration of intent and outcome.

The library is layered, offering tools of increasing abstraction:

1.  The Principia Engine (@principia.contract): A declarative, "aspect-oriented"
    framework for applying validation contracts to functions. This is the
    recommended, highest-level interface.

2.  The Semantic Layer (be_a, be_in_range, etc.): A rich, extensible
    vocabulary of readable, reusable checks that express developer intent and
    serve as the building blocks for contracts.

3.  Imperative Tools (ensure, ensure_precondition): Low-level functions for
    direct, inline validation when a full contract is not necessary.
"""

import builtins
import functools
import inspect
import os
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from io import TextIOBase
from typing import Any, Dict, List, Type, Union
import sys
# ==============================================================================
# SECTION 1: CUSTOM EXCEPTION TAXONOMY
# A clear hierarchy of exceptions for specific failure consequences.
# ==============================================================================

class PrincipiaError(Exception):
    """Base class for all custom exceptions raised by the principia library."""
    pass

class PreconditionError(PrincipiaError, TypeError):
    """
    Raised for fundamental precondition failures, like incorrect types,
    protocol violations, or shadowed built-ins. Inherits from TypeError to
    signal a severe contract violation.
    """
    pass

class InvalidArgumentError(PrincipiaError, ValueError):
    """
    Raised when an argument is of the correct type but has an inappropriate
    value (e.g., out of range). Inherits from ValueError.
    """
    pass

class IllegalStateError(PrincipiaError, RuntimeError):
    """
    Raised when a method is invoked at an illegal time or an object is in an
    improper state for the requested operation.
    """
    pass

class ConfigurationError(PrincipiaError):
    """Raised when an environmental or configuration-related issue is detected."""
    pass


# ==============================================================================
# SECTION 2: THE Principia ENGINE (DECLARATIVE CONTRACTS)
# The highest level of abstraction for applying contracts to functions.
# ==============================================================================

class AssuranceMatcher:
    """
    Emulates Rust's `match` syntax for expressive, chainable validation.

    This class provides a fluent interface to check a single value against
    a series of conditions, raising a specific consequence for the first
    condition that fails.
    """
    def __init__(self, value: Any, name: str = "Value"):
        self._value = value
        self._name = name
        self._arms: List[tuple] = []

    def must(
        self,
        success_condition: Callable[[Any], bool],
        then_raise: Type[BaseException],
        message: str
    ) -> "AssuranceMatcher":
        """
        Defines an arm that requires a condition to be TRUE for success.
        This is the preferred, readable way to build contracts.
        """
        # Invert the success condition to create the internal failure condition.
        failure_condition = lambda v: not success_condition(v)
        self._arms.append((failure_condition, then_raise, message))
        return self

    def on(
        self,
        failure_condition: Callable[[Any], bool],
        then_raise: Type[BaseException],
        message: str
    ) -> "AssuranceMatcher":
        """
        Defines an arm based on a condition that returns TRUE for failure.
        Useful for low-level or inverted logic checks.
        """
        self._arms.append((failure_condition, then_raise, message))
        return self

    def check(self) -> Any:
        """
        Executes the validation, raising the first matching consequence.
        Returns the original value if all checks pass.
        """
        for condition_func, error_cls, msg_template in self._arms:
            is_failure_match = False
            try:
                # A failure occurs if the failure condition returns True.
                # If the check itself raises an exception (e.g., TypeError during
                # a comparison), we treat that as a failure of the check itself.
                is_failure_match = condition_func(self._value)
            except Exception:
                is_failure_match = True

            if is_failure_match:
                formatted_message = msg_template.format(
                    value=repr(self._value),
                    name=self._name
                )
                raise error_cls(formatted_message)
        return self._value


@dataclass(frozen=True)
class AssumptionContract:
    """A declarative, reusable contract of assumptions for a function."""
    preconditions: Dict[str, AssuranceMatcher] = field(default_factory=dict)
    postcondition: AssuranceMatcher = None
    environment: AssuranceMatcher = None
    on_success: Union[str, Callable[[], None]] = None


def contract(*contracts: AssumptionContract):
    """
    A decorator that applies one or more AssumptionContracts to a function,
    wrapping it in a full validation lifecycle (environment, preconditions,
    postconditions).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            all_checks_passed = True
            for c in contracts:
                try:
                    if c.environment:
                        c.environment.check()

                    for arg_name, matcher_template in c.preconditions.items():
                        if arg_name in bound_args.arguments:
                            arg_value = bound_args.arguments[arg_name]
                            actual_matcher = matcher_template.__class__(arg_value, name=arg_name)
                            actual_matcher._arms = matcher_template._arms
                            actual_matcher.check()
                except Exception:
                    all_checks_passed = False
                    raise

            result = func(*args, **kwargs)

            for c in contracts:
                try:
                    if c.postcondition:
                        post_matcher = c.postcondition.__class__(result, name="ReturnValue")
                        post_matcher._arms = c.postcondition._arms
                        post_matcher.check()
                except Exception:
                    all_checks_passed = False
                    raise

            if all_checks_passed:
                for c in contracts:
                    if c.on_success:
                        if isinstance(c.on_success, str):
                            print(c.on_success)
                        elif callable(c.on_success):
                            c.on_success()
            return result
        return wrapper
    return decorator


# ==============================================================================
# SECTION 3: THE SEMANTIC VALIDATION LAYER
# A rich vocabulary of readable checks to be used with the AssuranceMatcher.
# To extend the library, simply add new functions in this style.
# ==============================================================================

# --- Type and Structure Checks ---
def be_a(expected_type: type) -> Callable[[Any], bool]:
    """Checks if a value is an instance of a given type."""
    return lambda v: isinstance(v, expected_type)

def conform_to(protocol_class: type) -> Callable[[Any], bool]:
    """Checks if an object conforms to a protocol using an Abstract Base Class."""
    return lambda v: isinstance(v, protocol_class)

def have_attribute(attr_name: str) -> Callable[[Any], bool]:
    return lambda v: hasattr(v, attr_name)

def be_callable() -> Callable[[Any], bool]:
    """Checks if a value is callable (e.g., a function or method)."""
    return lambda v: callable(v)

# --- Identity Checks ---
def be_the_same_as(identity: Any) -> Callable[[Any], bool]:
    """Checks if a value is the exact same object as another (using 'is')."""
    return lambda v: v is identity

def be_unmodified_builtin(name_str: str) -> Callable[[Any], bool]:
    """Checks if an object is the canonical, un-shadowed Python built-in."""
    true_builtin = getattr(builtins, name_str)
    return lambda v: v is true_builtin

# --- Numeric Checks ---
def be_greater_than(limit: float) -> Callable[[Any], bool]:
    return lambda v: v > limit

def be_in_range(lower_bound: float, upper_bound: float) -> Callable[[Any], bool]:
    return lambda v: lower_bound <= v <= upper_bound

# --- String Checks ---
def match_pattern(pattern: str) -> Callable[[str], bool]:
    return lambda v: isinstance(v, str) and re.match(pattern, v) is not None

# --- Collection Checks ---
def not_be_empty() -> Callable[[Any], bool]:
    return lambda v: len(v) > 0

def have_length(expected_len: int) -> Callable[[Any], bool]:
    return lambda v: len(v) == expected_len

# --- Filesystem Checks ---
def be_existing_file() -> Callable[[str], bool]:
    return lambda v: isinstance(v, str) and os.path.isfile(v)


# ==============================================================================
# SECTION 4: IMPERATIVE AND LOW-LEVEL TOOLS
# For direct, inline validation checks.
# ==============================================================================

def ensure(condition: bool, error_cls: Type[BaseException] = AssertionError, *args: Any, **kwargs: Any) -> None:
    """
    The core imperative assertion. Asserts `condition` is True; otherwise,
    raises `error_cls`. It is "always-on" and not disabled by Python's -O flag.
    """
    if not condition:
        raise error_cls(*args, **kwargs)

def ensure_precondition(condition: bool, *args: Any, **kwargs: Any) -> None:
    """Helper for a common precondition check."""
    ensure(condition, InvalidArgumentError, *args, **kwargs)


# ==============================================================================
# SECTION 5: EXAMPLE USAGE
# Demonstrates the power and readability of the declarative Principia Engine.
# ==============================================================================

if __name__ == "__main__":
    # --- 1. Define Reusable, Semantic Contracts ---
    
    # A contract to ensure the environment can print to an interactive terminal.
    TERMINAL_CONTRACT = AssumptionContract(
        environment=AssuranceMatcher(None, name="Environment")
            .must(lambda _: 'print' in globals(), PreconditionError, "Global 'print' function not found.")
            .must(lambda _: be_unmodified_builtin("print")(globals()['print']), PreconditionError, "'print' name has been shadowed.")
            .must(lambda _: conform_to(TextIOBase)(sys.stdout), ConfigurationError, "sys.stdout does not conform to TextIOBase protocol.")
            .must(lambda _: sys.stdout.isatty(), ConfigurationError, "Output is not an interactive terminal."),
        on_success="[Principia] ✅ Terminal environment checks passed."
    )

    # A contract for a valid user identifier.
    ID_CONTRACT = AssumptionContract(
        preconditions={
            'user_id': AssuranceMatcher(None, name="User ID")
                .must(be_a(int), InvalidArgumentError, "{name} must be an integer.")
                .must(be_greater_than(0), InvalidArgumentError, "{name} must be a positive integer.")
        }
    )

    # --- 2. Apply Contracts to Business Logic ---

    @contract(TERMINAL_CONTRACT, ID_CONTRACT)
    def fetch_user_data(user_id: int):
        """
        A function whose operational environment and arguments are protected
        by Principia contracts.
        """
        print(f"--> Core Logic: Fetching data for user {user_id}...")
        return {"id": user_id, "name": "Alice"}

    # --- 3. Execute and Observe ---
    
    print("--- Testing Principia Engine with a valid call ---")
    try:
        user = fetch_user_data(user_id=123)
        print(f"--> Success: Got user data: {user}")
    except PrincipiaError as e:
        print(f"--> This should not happen. Caught error: {e}")

    print("\n--- Testing Principia Engine with an invalid argument ---")
    try:
        fetch_user_data(user_id=-5)
    except InvalidArgumentError as e:
        print(f"--> Caught expected error: {e}")
    
    print("\n--- To test the environment check, redirect output to a file: ---")
    print("--- python principia.py > output.txt ---")
