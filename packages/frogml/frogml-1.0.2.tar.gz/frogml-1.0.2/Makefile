SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MODULE := frogml

.PHONY: clean install format lint bump_version

clean:
	rm -rf .mypy_cache .pytest_cache tests/.pytest_cache .coverage coverage-reports dist

format:
	uv run black tests $(MODULE)

install:
	uv sync --all-groups

install-basic:
	uv sync --no-dev

lint:
	uv run pre-commit run --all-files

test:
	uv run coverage run -m pytest --disable-warnings -m "not integration" tests


integration-test:
ifeq ($(strip $(base-url)),)
endif
ifeq ($(strip $(local-artifactory)),)
	TEST_BASE_URL=$(base-url) uv run coverage run -m pytest --disable-warnings tests/integration_test
else
	TEST_BASE_URL=$(base-url) IS_LOCAL_MACHINE=true uv run coverage run -m pytest --disable-warnings tests/integration_test
endif


unit-test:
	uv run pytest tests -m "not integration"

coverage-report:
	uv run coverage xml -i

bump-version-dev:
	uv run bump2version --allow-dirty build VERSION
	uv lock

bump-version-prod:
	uv run bump2version --allow-dirty release VERSION
	uv lock

patch-version:
	uv run bump2version --allow-dirty patch VERSION
	uv lock

dev-release:
	uv build
	uv publish --publish-url $(JFROG_ARTIFACTORY_URL) --username $(JFROG_USER) --password $(JFROG_PASSWORD)

prod-release:
	uv build
	uv publish --token $(PYPI_API_TOKEN)
