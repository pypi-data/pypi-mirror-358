from typing import TYPE_CHECKING

import astroid


if TYPE_CHECKING:
    from pylint.lint import PyLinter


def register(_: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    astroid.MANAGER.register_transform(astroid.ClassDef, transform)  # type: ignore


def transform(cls):
    if not cls.decorators:
        return

    for node in cls.decorators.nodes:
        if isinstance(node, astroid.Call):  # decorator with arguments
            node_to_infer = node.func
        else:
            node_to_infer = node

        try:
            inferred = next(node_to_infer.infer())
        except (astroid.InferenceError, StopIteration):
            inferred = astroid.Uninferable

        if (isinstance(inferred, astroid.FunctionDef)
            and inferred.name == "dictparser"
            and inferred.root().name.startswith("dictparser.")):

            cls.is_dataclass = True

            from_dict_def = astroid.parse(f"def from_dict(data: dict) -> {cls.name}:\n    Pass\n")["from_dict"]
            cls.locals["from_dict"] = [from_dict_def]

            from_file_def = astroid.parse(f"def from_file(file: Path) -> {cls.name}:\n    Pass\n")["from_file"]
            cls.locals["from_file"] = [from_file_def]

            as_dict_def = astroid.parse("def as_dict(self) -> dict:\n    Pass\n")["as_dict"]
            cls.locals["as_dict"] = [as_dict_def]
