from typing import Optional

from wexample_wex_core.common.kernel import Kernel
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.middleware import middleware
from wexample_wex_core.decorator.option import option


@option(
    name="tool",
    type=str,
    required=False,
    description="Specific tool to run (mypy, pylint, pyright). If not specified, all tools will be run.",
)
@option(
    name="stop_on_failure",
    type=bool,
    required=False,
    default=True,
    description="Stop execution when a tool reports a failure",
)
@middleware(
    # TODO working command:  bash cli/wex python::code/check --file ../../pip/wex-core/wexample_wex_core/ -sof
    #      -> sof / stop_on_failure does not works
    #         en tout cas ça ne marche pas lors de l'itération, il faudrait etre capable d'ajouter un signal d'arret.
    #      -> Gérer les valeurs de retour, pour l'instant c'est une liste, ce sera un MultipleResponse
    #      -> continue_on_error=False,
    #      -> aggregation_mode='list',
    #      -> parallel=True,
    #      -> limit=False,
    #      -> show_progres=True
    #      -> Peut être que
    name="each_python_file",
    should_exist=True,
    expand_glob=True,
    recursive=True)
# TODO après et durant la mise en place de ça on pourrait:
#   - Créer des commandes de test
#   - Les outilis utilisent des méthodes pour exécuter des commandes shell, on peut les wrap dans des premier helpers
#   - Dans les commandes de test:
#     > teste l'appel de commandes en interne
#     > teste du prompting et des context de prompt et du nesting
@command()
def python__code__check(
    kernel: "Kernel",
    file: str,
    tool: Optional[str] = None,
    stop_on_failure: bool = True,
) -> bool:
    """Check a Python file using various code quality tools."""
    from wexample_wex_addon_dev_python.commands.code.check.mypy import _code_check_mypy
    from wexample_wex_addon_dev_python.commands.code.check.pylint import (
        _code_check_pylint,
    )
    from wexample_wex_addon_dev_python.commands.code.check.pyright import (
        _code_check_pyright,
    )

    # Map tool names to their check functions
    tool_map = {
        "mypy": _code_check_mypy,
        "pylint": _code_check_pylint,
        "pyright": _code_check_pyright,
    }

    # Determine which tools to run
    if tool and tool.lower() in tool_map:
        # Run only the specified tool
        check_functions = [tool_map[tool.lower()]]
    else:
        # Run all tools if no specific tool is specified or if the specified tool is invalid
        check_functions = [
            _code_check_mypy,
            _code_check_pylint,
            _code_check_pyright,
        ]

    # Track overall success
    all_checks_passed = True

    # Run each check function
    for check_function in check_functions:
        kernel.io.title(check_function.__name__)
        kernel.io.log_indent_up()
        kernel.io.log(file)

        check_result = check_function(kernel, file)

        if check_result:
            kernel.io.success(f"No critical issue found for {check_function.__name__}")

        # Update overall success status
        all_checks_passed = all_checks_passed and check_result
        kernel.io.log_indent_down()

        # Stop if a check fails and stop_on_failure is True
        if not check_result and stop_on_failure:
            kernel.io.error("One check failed")
            return False

    return all_checks_passed
