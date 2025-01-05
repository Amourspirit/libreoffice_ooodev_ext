help:
	@echo "Run make build to compile into 'build' folder."
	@echo "Run make diff to write 'changes_since_last_commit.diff into' into 'tmp' folder."
	@echo "Run make diff_sum to write 'summary_since_last_commit.diff into' into 'tmp' folder."

.PHONY: build diff diff_sum help

build:
	uv run --no-config make.py build

create_build_dir:
	mkdir -p tmp

diff: create_build_dir
    # https://stackoverflow.com/questions/855767/can-i-use-git-diff-on-untracked-files
	git diff HEAD > ./tmp/changes_since_last_commit.diff

diff_sum: create_build_dir
	git diff --compact-summary HEAD > ./tmp/summary_since_last_commit.diff