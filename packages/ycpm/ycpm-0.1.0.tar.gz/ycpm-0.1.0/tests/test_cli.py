import os
import pytest
import json
from ycpm import cli
from ycpm import clyp_packages_folder

@pytest.fixture(autouse=True)
def setup_and_teardown(tmp_path, monkeypatch):
    # Patch clyp_packages_folder to use a temp directory
    monkeypatch.setattr('ycpm.clyp_packages_folder', str(tmp_path))
    yield
    # Cleanup handled by tmp_path fixture

def test_print_info(capsys):
    cli.print_info()
    captured = capsys.readouterr()
    assert "ycpm" in captured.out
    assert "Clyp version" in captured.out
    assert "Clyp packages folder" in captured.out

def test_create_new_package(tmp_path):
    pkg_name = "testpkg"
    os.chdir(tmp_path)
    cli.create_new_package(pkg_name)
    assert os.path.isdir(pkg_name)
    ycpm_json = os.path.join(pkg_name, 'ycpm.json')
    assert os.path.isfile(ycpm_json)
    with open(ycpm_json) as f:
        data = json.load(f)
        assert data["name"] == pkg_name
        assert data["file"] == f"{pkg_name}.cpak"

def test_build_package(tmp_path, capsys):
    pkg_name = "testpkg"
    os.chdir(tmp_path)
    cli.create_new_package(pkg_name)
    os.chdir(tmp_path)
    # Add a dummy file
    with open(os.path.join(pkg_name, "foo.txt"), "w") as f:
        f.write("bar")
    os.chdir(tmp_path)
    # Build
    with open("ycpm.json", "w") as f:
        json.dump({"name": pkg_name, "file": f"{pkg_name}.cpak"}, f)
    cli.build_package()
    captured = capsys.readouterr()
    assert f"Building package {pkg_name}" in captured.out
    assert os.path.isfile(f"{pkg_name}.cpak")

def test_list_packages(tmp_path, capsys):
    import ycpm  # ensure we use the patched value
    os.makedirs(os.path.join(ycpm.clyp_packages_folder, "pkg1"))
    os.makedirs(os.path.join(ycpm.clyp_packages_folder, "pkg2"))
    cli.list_packages()
    captured = capsys.readouterr()
    assert "pkg1" in captured.out
    assert "pkg2" in captured.out

def test_uninstall_package(tmp_path, monkeypatch, capsys):
    pkg_name = "pkg1"
    monkeypatch.setattr('ycpm.clyp_packages_folder', str(tmp_path))
    import ycpm
    pkg_path = os.path.join(ycpm.clyp_packages_folder, pkg_name)
    os.makedirs(pkg_path)
    # Simulate user input 'y'
    monkeypatch.setattr('builtins.input', lambda: 'y')
    cli.uninstall_package(pkg_name)
    captured = capsys.readouterr()
    assert f"Uninstalling package '{pkg_name}'" in captured.out
    assert not os.path.exists(pkg_path)

def test_uninstall_package_cancel(tmp_path, monkeypatch, capsys):
    pkg_name = "pkg2"
    monkeypatch.setattr('ycpm.clyp_packages_folder', str(tmp_path))
    import ycpm
    pkg_path = os.path.join(ycpm.clyp_packages_folder, pkg_name)
    os.makedirs(pkg_path)
    # Simulate user input 'n'
    monkeypatch.setattr('builtins.input', lambda: 'n')
    cli.uninstall_package(pkg_name)
    captured = capsys.readouterr()
    assert "Uninstallation canceled" in captured.out
    assert os.path.exists(pkg_path)
