import shutil
from pathlib import Path

import pytest

from kst.api import CustomScriptPayload
from kst.exceptions import (
    DuplicateInfoFileError,
    DuplicateScriptError,
    InvalidScriptError,
    MissingInfoFileError,
)
from kst.repository import ACCEPTED_INFO_EXTENSIONS, CustomScript


@pytest.fixture
def script_directory_info_file(script_directory) -> Path:
    """Return the path to a valid info file in the script directory."""
    return next(script_directory.glob("info.*"))


@pytest.fixture
def script_directory_audit_script(script_directory) -> Path:
    """Return the path to a valid audit script file in the script directory."""
    return next(script_directory.glob("audit*"))


@pytest.fixture
def script_directory_remediation_script(script_directory) -> Path:
    """Return the path to a valid remediation script file in the script directory."""
    return next(script_directory.glob("remediation*"))


@pytest.fixture
def script_directory_without_audit_script(script_directory, script_directory_audit_script) -> Path:
    """Return the path to a script directory without an audit script file."""
    script_directory_audit_script.unlink()
    return script_directory


@pytest.fixture
def script_directory_with_extra_audit_script(script_directory, script_directory_audit_script) -> Path:
    """Return the path to a script directory with an extra audit script file."""
    shutil.copy(script_directory_audit_script, script_directory_audit_script.with_name("audit2"))
    return script_directory


@pytest.fixture
def script_directory_with_extra_remediation_script(script_directory, script_directory_remediation_script) -> Path:
    """Return the path to a script directory with an extra remediation script file."""
    shutil.copy(script_directory_remediation_script, script_directory_remediation_script.with_name("remediation2"))
    return script_directory


@pytest.fixture
def script_directory_without_info_file(script_directory, script_directory_info_file) -> Path:
    """Return the path to a script directory without a info file."""
    script_directory_info_file.unlink()
    return script_directory


@pytest.fixture
def script_directory_with_extra_info_file(script_directory, script_directory_info_file) -> Path:
    """Return the path to a script directory with an extra info file."""
    suffix = (ACCEPTED_INFO_EXTENSIONS - {script_directory_info_file.suffix}).pop()
    shutil.copy(script_directory_info_file, script_directory_info_file.with_name(f"info{suffix}"))
    return script_directory


class TestCustomScript:
    def test_audit_path_raises_if_unset(self, custom_script_obj):
        """Ensure the script_path property raises a ValueError if the script_path is unset."""
        assert custom_script_obj.audit.path is None
        with pytest.raises(ValueError, match="The audit_path property must be set before reading."):
            custom_script_obj.audit_path

    def test_remediation_path_raises_if_unset(self, custom_script_obj):
        """Ensure the script_path property raises a ValueError if the script_path is unset."""
        if custom_script_obj.remediation is not None:
            assert custom_script_obj.remediation.path is None
        with pytest.raises(ValueError, match="The remediation_path property must be set before reading."):
            custom_script_obj.remediation_path

    def test_ensure_paths_without_paths(self, custom_script_obj, scripts_repo):
        """Ensure the ensure_paths method sets the info_path and script_path properties."""
        expected_info_path = scripts_repo / custom_script_obj.name / f"info.{custom_script_obj.info.format}"
        expected_audit_path = scripts_repo / custom_script_obj.name / "audit"
        expected_remediation_path = scripts_repo / custom_script_obj.name / "remediation"

        assert not custom_script_obj.has_paths
        custom_script_obj.ensure_paths(scripts_repo)
        assert custom_script_obj.has_paths
        assert custom_script_obj.info_path == expected_info_path
        assert custom_script_obj.audit_path == expected_audit_path
        if custom_script_obj.has_remediation:
            assert custom_script_obj.remediation_path == expected_remediation_path

    def test_ensure_paths_with_paths(self, custom_script_obj, scripts_repo):
        """Ensure the ensure_paths method does nothing if the paths are already set."""
        expected_info_path = scripts_repo / "What a Neat Script" / f"info.{custom_script_obj.info.format}"
        expected_audit_path = scripts_repo / "What a Neat Script" / "audit"
        expected_remediation_path = scripts_repo / "What a Neat Script" / "remediation"

        custom_script_obj.info.path = expected_info_path
        custom_script_obj.audit.path = expected_audit_path
        if custom_script_obj.has_remediation:
            custom_script_obj.remediation.path = expected_remediation_path

        assert custom_script_obj.has_paths
        custom_script_obj.ensure_paths(scripts_repo)
        assert custom_script_obj.has_paths

        assert custom_script_obj.info_path == expected_info_path
        assert custom_script_obj.audit_path == expected_audit_path
        if custom_script_obj.has_remediation:
            assert custom_script_obj.remediation_path == expected_remediation_path

    def test_ensure_paths_with_existing_parent(self, custom_script_obj, scripts_repo):
        """Ensure the ensure_paths method increments the path if the parent directory already exists."""
        (scripts_repo / custom_script_obj.name).mkdir()
        expected_info_path = scripts_repo / f"{custom_script_obj.name} (1)" / f"info.{custom_script_obj.info.format}"
        expected_audit_path = scripts_repo / f"{custom_script_obj.name} (1)" / "audit"
        expected_remediation_path = scripts_repo / f"{custom_script_obj.name} (1)" / "remediation"

        assert not custom_script_obj.has_paths
        custom_script_obj.ensure_paths(scripts_repo)
        assert custom_script_obj.has_paths
        assert custom_script_obj.info_path == expected_info_path
        assert custom_script_obj.audit_path == expected_audit_path
        if custom_script_obj.has_remediation:
            assert custom_script_obj.remediation_path == expected_remediation_path

    def test_write_to_path(self, custom_script_obj, scripts_repo):
        """Writing to disk should create a file both the info and script files."""
        custom_script_obj.ensure_paths(scripts_repo)

        # Check that files don't exist
        assert not custom_script_obj.info_path.exists()
        assert not custom_script_obj.audit_path.exists()
        if custom_script_obj.has_remediation:
            assert not custom_script_obj.remediation_path.exists()

        custom_script_obj.write()

        # Check that files were written
        assert custom_script_obj.info_path.exists()
        assert custom_script_obj.audit_path.exists()
        if custom_script_obj.has_remediation:
            assert custom_script_obj.remediation_path.exists()

    def test_write_to_path_without_paths(self, custom_script_obj: CustomScript):
        """Writing to disk with no info_path or script_path should raise a InvalidScriptError."""
        assert custom_script_obj.info.path is None
        assert custom_script_obj.audit.path is None
        if custom_script_obj.remediation is not None:
            assert custom_script_obj.remediation.path is None

        with pytest.raises(ValueError, match="All path properties must be set before writing the custom script."):
            custom_script_obj.write()

    def test_write_raises_on_different_parent_directories(self, scripts_repo: Path, custom_script_obj: CustomScript):
        """Writing to disk with info_path and script_path in different directories should raise a InvalidScriptError."""
        custom_script_obj.info_path = scripts_repo / "dir01/info.plist"
        custom_script_obj.audit_path = scripts_repo / "dir02/audit"
        if custom_script_obj.has_remediation:
            custom_script_obj.remediation_path = scripts_repo / "dir03/remediation"
        with pytest.raises(InvalidScriptError, match=r"must be paths to files within the same directory"):
            custom_script_obj.write()

    @pytest.mark.parametrize(
        "has_remediation", [pytest.param(True, id="with_remediation"), pytest.param(False, id="without_remediation")]
    )
    def test_from_api_payload(self, script_info_data_factory, script_content, has_remediation):
        response_data = script_info_data_factory()
        response_data["script"] = script_content
        response_data["remediation_script"] = script_content if has_remediation else ""
        script_response = CustomScriptPayload.model_validate(response_data)
        script = CustomScript.from_api_payload(script_response)
        assert isinstance(script, CustomScript)
        assert script.audit.content == script_content
        if has_remediation:
            assert script.remediation is not None
            assert script.remediation.content == script_content
        else:
            assert script.remediation is None

    def test_to_api_payload(self, custom_script_obj):
        """Ensure the to_api_payload method returns a valid API payload."""
        custom_script_obj.to_api_payload()

    def test_load_from_info_path(self, script_directory_info_file):
        """Ensure creating a CustomScript from a valid info file succeeds."""
        assert isinstance(CustomScript.from_path(script_directory_info_file), CustomScript)

    def test_load_from_script_path(self, script_directory_audit_script):
        """Ensure creating a CustomScript from a valid script succeeds."""
        assert isinstance(CustomScript.from_path(script_directory_audit_script), CustomScript)

    def test_load_from_directory_path(self, script_directory):
        """Ensure creating a CustomScript from a valid script directory succeeds."""
        assert isinstance(CustomScript.from_path(script_directory), CustomScript)

    @pytest.mark.usefixtures("script_directory_without_audit_script")
    def test_load_with_missing_audit_script(self, script_directory):
        """Creating a CustomScript from an info file that doesn't have a matching script should raise a InvalidScriptError."""
        CustomScript.from_path(script_directory)
        assert (script_directory / "audit.zsh").exists()

    @pytest.mark.usefixtures("script_directory_with_extra_audit_script")
    def test_load_with_extra_audit_script(self, script_directory):
        """Creating a CustomScript from an info file that has an extra script should raise a InvalidScriptError."""
        with pytest.raises(DuplicateScriptError):
            CustomScript.from_path(script_directory)

    @pytest.mark.usefixtures("script_directory_with_extra_remediation_script")
    def test_load_with_extra_remediation_script(self, script_directory):
        """Creating a CustomScript from an info file that has an extra script should raise a InvalidScriptError."""
        with pytest.raises(DuplicateScriptError):
            CustomScript.from_path(script_directory)

    @pytest.mark.usefixtures("script_directory_without_info_file")
    def test_load_with_missing_info_file(self, script_directory):
        """Creating a CustomScript from a script file without a matching info file should raise a InvalidScriptError."""
        with pytest.raises(MissingInfoFileError):
            CustomScript.from_path(script_directory)

    @pytest.mark.usefixtures("script_directory_with_extra_info_file")
    def test_load_with_extra_info_file(self, script_directory):
        """Creating a CustomScript from a script file that has an extra info file should raise a InvalidScriptError."""
        with pytest.raises(DuplicateInfoFileError):
            CustomScript.from_path(script_directory)

    def test_diff_hash(self, custom_script_obj):
        """Test that the diff_hash property is correctly calculated."""

        # Hash should always exist in a CustomScript object
        original_hash = custom_script_obj.diff_hash
        assert original_hash is not None

        # Modify the info file
        original_name = custom_script_obj.name
        custom_script_obj.name = "New Script Name"
        assert custom_script_obj.diff_hash != original_hash
        custom_script_obj.name = original_name
        assert custom_script_obj.diff_hash == original_hash

        # Modify the audit script
        original_content = custom_script_obj.audit.content
        custom_script_obj.audit.content = "#!/bin/sh\necho 'Goodbye, World!'"
        assert custom_script_obj.diff_hash != original_hash
        custom_script_obj.audit.content = original_content
        assert custom_script_obj.diff_hash == original_hash

        if custom_script_obj.remediation is not None:
            # Modify the remediation script
            original_content = custom_script_obj.remediation.content
            custom_script_obj.remediation.content = "#!/bin/sh\necho 'Hello Again, World!'"
            assert custom_script_obj.diff_hash != original_hash
            custom_script_obj.remediation.content = original_content
            assert custom_script_obj.diff_hash == original_hash
