# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
"""CLI command for compiling Vibe source files."""

from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

from pathlib import Path
import ast
import sys

from .utils import gather_python_sources, post_process_vibe_files
from ..analysis import ast_utils
from ..compiler import (
    FunctionPlot,
    PlotContext,
    ContextGatherer,
    ModuleContextGatherer,
    ImportContextGatherer,
    extract_plots,
    ContextItem,
)
from ..compiler import providers, prompt
from ..compiler.plots import apply_generated_code


def compile_command(sources: list[Path], provider_name: str | None = None) -> None:
    """Compile the specified Vibe source files."""

    expanded_sources = gather_python_sources(sources)

    provider = (
        providers.provider_from_name(provider_name)
        if provider_name
        else providers.auto_provider()
    )
    if provider:
        print(f"Using provider {provider.name}")

    gatherers: list[ContextGatherer] = [
        ModuleContextGatherer(),
        ImportContextGatherer(),
    ]

    vibe_files: list[Path] = []
    for src in expanded_sources:
        print(f"Compiling {src}")

        module_source = src.read_text()
        module_ast = ast_utils.parse_python_file(src)
        plots = extract_plots(src, module_ast)

        if not plots:
            continue

        for plot in plots:
            contexts: list[ContextItem] = []
            for gatherer in gatherers:
                contexts.extend(gatherer.gather(plot, module_ast, module_source))
            plot_context = PlotContext(plot, contexts)
            print(f"Context for {plot.qualname}:")
            for item in plot_context.items:
                print(f"{item.path}:{item.start_line}-{item.end_line}")
                print(item.source)
            if provider is None:
                print("Error: provider required for code generation", file=sys.stderr)
                sys.exit(1)

            prompt_text = prompt.create_prompt(plot_context)
            generated = provider.generate(prompt_text)
            apply_generated_code(plot, generated)

        remove_vibefarm_imports(module_ast)

        new_source = ast.unparse(module_ast)
        vibe_file = src.with_suffix(".vibe.py")
        vibe_file.write_text(new_source)
        vibe_files.append(vibe_file)

    post_process_vibe_files(vibe_files)


def remove_vibefarm_imports(module_ast: ast.Module) -> None:
    """Remove farm and code imports from vibe_farm in *module_ast*."""

    new_body: list[ast.stmt] = []
    for stmt in module_ast.body:
        if isinstance(stmt, ast.ImportFrom) and stmt.module == "vibe_farm":
            stmt.names = [
                alias for alias in stmt.names if alias.name not in {"farm", "code"}
            ]
            if not stmt.names:
                continue
        new_body.append(stmt)
    module_ast.body = new_body


# Re-export internals for tests ------------------------------------------------

from ..compiler.plots import (
    create_plot_source,
    extract_plots as extract_plots_internal,
)  # noqa: E402

__all__ = [
    "compile_command",
    "FunctionPlot",
    "PlotContext",
    "ContextGatherer",
    "create_plot_source",
    "extract_plots_internal",
]
