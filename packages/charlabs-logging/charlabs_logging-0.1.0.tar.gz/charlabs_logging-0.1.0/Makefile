EXECUTOR := uv run

.PHONY: all

test:
	$(EXECUTOR) pytest $(ARGS)

types:
	$(EXECUTOR) pyright $(ARGS)

pc: pre-commit
pre-commit:
	$(EXECUTOR) pre-commit run --all-files $(ARGS)

pci: pre-commit-install
pre-commit-install:
	$(EXECUTOR) pre-commit install $(ARGS)

lint:
	$(EXECUTOR) ruff check $(ARGS)

format:
	$(EXECUTOR) ruff format --check $(ARGS)

lx: lint-fix
lint-fix:
	$(EXECUTOR) ruff check --fix $(ARGS)

fx: format-fix
format-fix:
	$(EXECUTOR) ruff format $(ARGS)
