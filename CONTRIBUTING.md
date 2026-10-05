# Contributing

## Workflow

1. Branch from `main` (`feature/…`, `fix/…`, `docs/…`).
2. Keep each pull request to one topic and fill in the template.
3. CI must be green: ruff, pytest on Windows and Linux, and the launcher
   build. Pull requests that touch `packaging/`, `launcher/` or
   `requirements.txt` also build and smoke-test the portable app on Windows.
4. Update `CHANGELOG.md` under *Unreleased* for anything users will notice.

## Local checks

```sh
pip install -r requirements-dev.txt
ruff check .
pytest                      # add `xvfb-run -a` on headless Linux for the Tk tests
make -C launcher test       # if you changed the launcher
```

Tests create their sample media on the fly, so please don't commit media
files.

## Changing rules

Rules in `app/helpers/rules.py` encode published Scala and Dise guidance.
When you change one:

- quote or link the guideline (document and date) in the pull request;
- add or update a test in `tests/test_rules.py` that shows the new
  behaviour;
- update [docs/checks.md](docs/checks.md);
- if the guideline document changed, update `DISE_SOURCE` or `SCALA_SOURCE`.

## Dependencies

`requirements.txt` pins the exact packages shipped in the portable runtime.
Dependabot proposes updates monthly. The Windows build in the pull request
checks that the new versions still install and run.

## Releasing

See [docs/building.md](docs/building.md#automated-builds-recommended).
