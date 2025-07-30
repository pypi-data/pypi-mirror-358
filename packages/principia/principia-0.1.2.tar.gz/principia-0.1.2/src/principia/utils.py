
from . import principia

# A contract for the prompt generation function.
PROMPT_CONTRACT = principia.AssumptionContract(
    preconditions={
        'style': principia.AssuranceMatcher(None, name="Style")
            .must(principia.be_a(str), principia.InvalidArgumentError, "{name} must be a string.")
            .must(lambda s: s in ['concise', 'verbose'], principia.InvalidArgumentError, "{name} must be either 'concise' or 'verbose'."),
        'audience': principia.AssuranceMatcher(None, name="Audience")
            .must(principia.be_a(str), principia.InvalidArgumentError, "{name} must be a string.")
            .must(lambda s: s in ['human', 'llm'], principia.InvalidArgumentError, "{name} must be either 'human' or 'llm'.")
    },
    postcondition=principia.AssuranceMatcher(None, name="Prompt")
        .must(principia.be_a(str), principia.IllegalStateError, "The generated prompt must be a string.")
        .must(principia.not_be_empty(), principia.IllegalStateError, "The generated prompt cannot be empty."),
    on_success="[Principia] ✅ Prompt contract validated."
)

@principia.contract(PROMPT_CONTRACT)
def prompt(style='verbose', audience='llm'):
    """
    Generates and prints a detailed prompt explaining how to create
    verbose, rich, and informative contracts using the Principia library.

    This function itself is a primary example of the Principia model:
    1.  **Assumption**: It assumes the 'style' and 'audience' arguments
        conform to specific constraints (e.g., must be one of the allowed
        options).
    2.  **Assertion**: The PROMPT_CONTRACT makes these assumptions explicit
        and verifies them at runtime.
    3.  **Consequence**: If an assumption is violated, a specific, informative
        error (e.g., InvalidArgumentError) is raised, preventing misuse.

    Args:
        style (str): The desired verbosity of the prompt ('concise' or 'verbose').
        audience (str): The target audience for the prompt ('human' or 'llm').

    Returns:
        str: The generated instructional prompt.
    """
    if audience == 'llm':
        # Instructions tailored for an LLM
        header = "As a large language model, your task is to create Principia contracts."
        philosophy = """
        **Core Philosophy: The Assumption-Assertion-Consequence Model**

        Principia transforms implicit developer assumptions into explicit, verifiable assertions.
        Your goal is to leave no assumption undocumented. For every function, consider:

        1.  **Assumptions (The 'What Ifs')**:
            -   What must be true about the arguments (`preconditions`)?
            -   What must be true about the return value (`postcondition`)?
            -   What must be true about the environment (e.g., dependencies, files) (`environment`)?

        2.  **Assertions (The 'Make Sures')**:
            -   Use the `AssumptionContract` to formalize these assumptions.
            -   Employ the rich semantic layer (`be_a`, `be_in_range`, `not_be_empty`, etc.)
                to build expressive `AssuranceMatcher` chains.

        3.  **Consequences (The 'Or Elses')**:
            -   For each assertion, specify a precise exception (`PreconditionError`,
                `InvalidArgumentError`, `IllegalStateError`, etc.). This is critical.
                The consequence should match the severity and nature of the failure.
        """
        instructions = """
        **Your Task: Constructing a Perfect Contract**

        When asked to write a function, you must also provide a `principia.AssumptionContract`
        that is as verbose, rich, and informative as possible.

        -   **Preconditions**: For each argument, create an `AssuranceMatcher`. Chain multiple
            `.must()` calls to cover all assumptions (type, range, length, format, etc.).
            The error message should be a template string: `"{name} must be..."`
        -   **Postcondition**: Define the expected state of the return value. Is it a specific
            type? Should it not be empty?
        -   **Environment**: If the function depends on external state (e.g., a file must
            exist, a library must be imported), define an `environment` check.
        -   **Consequence**: Choose the most specific exception. `InvalidArgumentError` for bad
            values, `PreconditionError` for fundamental type mismatches, `IllegalStateError`
            for incorrect return values.
        """
    else:
        # Instructions tailored for a human developer
        header = "How to Write Effective Principia Contracts"
        philosophy = """
        **The Goal: Self-Verifying Code**

        Principia helps you write robust code by forcing you to make your assumptions
        explicit. The core idea is the "Assumption-Assertion-Consequence" model.
        Before you write the function's logic, define what must be true for it to
        succeed.
        """
        instructions = """
        **Building a Contract: A Quick Guide**

        1.  **Create an `AssumptionContract`**: This is the container for all your checks.
        2.  **Define `preconditions`**: This is a dictionary mapping argument names to
            `AssuranceMatcher` objects. Use the matchers to chain checks:
            ```python
            'user_id': principia.AssuranceMatcher(None, name="User ID")
                .must(principia.be_a(int), principia.InvalidArgumentError, "{name} must be an integer.")
                .must(principia.be_greater_than(0), principia.InvalidArgumentError, "{name} must be positive.")
            ```
        3.  **Define a `postcondition`**: This is a single `AssuranceMatcher` for the
            function's return value.
        4.  **Apply the contract**: Use the `@principia.contract(...)` decorator on your function.
        """

    prompt_text = f"""
================================================================================
{header}
================================================================================

{philosophy}
{instructions}
"""

    if style == 'concise':
        prompt_text = f"Principia contracts formalize assumptions. Use AssumptionContract to define preconditions, postconditions, and environment checks with specific consequences for failures."

    print(prompt_text)
    return prompt_text
