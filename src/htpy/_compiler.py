import ast
import dataclasses
import inspect
import typing as t
from collections.abc import Callable, Iterator, Mapping

from markupsafe import Markup

from ._contexts import Context
from ._elements import BaseElement
from ._rendering import iter_chunks_node
from ._types import Node, Renderable

_py_compile = compile


class CompiledElement:
    def __init__(self, *parts: Node):
        self.parts = [Markup(part) if isinstance(part, str) else part for part in parts]

    def __str__(self) -> Markup:
        return Markup("".join(self.iter_chunks()))

    def __html__(self) -> Markup:
        return Markup("".join(self.iter_chunks()))

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        return iter_chunks_node(self.parts, context)

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)


@dataclasses.dataclass
class StaticCallArgs:
    args: tuple[t.Any]
    kwargs: dict[str, t.Any]

    @classmethod
    def from_call(cls, node: ast.Call) -> t.Self | None:
        if not all(isinstance(arg, ast.Constant) for arg in node.args):
            return None

        if any(not isinstance(kwarg.value, ast.Constant) for kwarg in node.keywords):
            return None

        return cls(
            tuple(arg.value for arg in node.args),  # type:ignore
            {kwarg.arg: kwarg.value.value for kwarg in node.keywords},  # type:ignore
        )


def compile[T, **P](func: Callable[P, T]) -> Callable[P, T | Renderable]:
    globals = func.__globals__
    node = ast.parse(inspect.getsource(func))

    class HtpyCompiler(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> t.Any:
            filtered_decorators: list[ast.expr] = [
                dec
                for dec in node.decorator_list
                # TODO: Removing the decorator like this is fragile.
                if isinstance(dec, ast.Name) and dec.id != "compile"
            ]

            return ast.FunctionDef(
                name=node.name,
                args=node.args,
                body=[self.visit(x) for x in node.body],
                decorator_list=filtered_decorators,
                returns=node.returns,
            )

        def visit_Call(self, node: ast.Call) -> t.Any:
            match node.func:
                case ast.Attribute(value=ast.Name(id=name), attr=attr):
                    resolved = getattr(globals[name], attr)

                    if not isinstance(resolved, BaseElement):
                        return node

                    if (static_call_args := StaticCallArgs.from_call(node)) is None:
                        return None

                    elem = resolved(*static_call_args.args, **static_call_args.kwargs)
                    return ast.Call(
                        ast.Name(id="__htpy__CompiledElement", ctx=ast.Load()),
                        [
                            ast.Constant(
                                value=Markup(elem).unescape(),
                            )
                        ],
                    )
                    return

            return node

    new = ast.fix_missing_locations(HtpyCompiler().visit(node))
    globals = {
        **func.__globals__,
        "__htpy__CompiledElement": CompiledElement,
    }
    exec(
        _py_compile(new, filename=func.__code__.co_filename, mode="exec"),
        globals,
    )

    return globals[func.__name__]  # type: ignore
