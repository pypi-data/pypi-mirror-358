import pytest


@pytest.fixture
def example_project(invoke, main, tmp_path):
    project = main.create_project(tmp_path)
    project.pyproject.set_data(
        {
            "project": {
                "name": "test_app",
                "version": "0.1.0",
                "requires-python": ">=3.8",
                "dependencies": ["requests==2.32.3"],
            },
            "build-system": {
                "requires": ["pdm-backend"],
                "build-backend": "pdm.backend",
            },
        }
    )
    project.pyproject.write()
    invoke(["lock"], obj=project)
    return project


def test_i(example_project, invoke):
    result = invoke(["i"], raising=False, obj=example_project)
    assert result.exit_code == 0


def test_pdm_i_help(example_project, invoke):
    result = invoke(["i", "-h"], raising=False, obj=example_project)
    assert result.exit_code == 0
