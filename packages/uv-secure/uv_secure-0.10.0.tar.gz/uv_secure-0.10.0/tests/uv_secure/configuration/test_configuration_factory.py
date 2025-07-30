from pathlib import Path
from textwrap import dedent
from typing import Optional

from anyio import Path as APath
import pytest

from uv_secure.configuration import (
    config_file_factory,
    Configuration,
    VulnerabilityCriteria,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("filename", "file_contents", "expected_configuration"),
    [
        pytest.param(
            "uv-secure.toml",
            "",
            Configuration(),
            id="Empty configuration returns Configuration",
        ),
        pytest.param(
            "uv-secure.toml",
            """
            [vulnerability_criteria]
            aliases = true
            desc = true
            """,
            Configuration(
                vulnerability_criteria=VulnerabilityCriteria(aliases=True, desc=True)
            ),
            id="Enable aliases and description",
        ),
        pytest.param(
            "pyproject.toml",
            """
            [tool.some_tool]
            some_option = true
            some_other_option = true
            """,
            None,
            id="pyproject.toml no uv-secure",
        ),
    ],
)
async def test_check_dependencies_alias_hyperlinks(
    tmp_path: Path,
    filename: str,
    file_contents: str,
    expected_configuration: Optional[Configuration],
) -> None:
    config_file_path = tmp_path / filename
    config_file_path.write_text(dedent(file_contents).strip())
    config = await config_file_factory(APath(config_file_path))
    assert config == expected_configuration
