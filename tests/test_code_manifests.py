#!/usr/bin/env python3
"""test_code_manifests.py — hermetic tests for scripts/code-manifests.py.

Builds a throwaway git repo with several real manifests plus a gitignored
vendored manifest, and asserts dependency extraction + the gitignore guarantee.

Usage:
  python3 tests/test_code_manifests.py
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "code-manifests.py"

spec = importlib.util.spec_from_file_location("code_manifests", HELPER)
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)


class Fail(SystemExit):
    pass


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30)


def make_repo(tmp):
    repo = Path(tmp) / "repo"
    repo.mkdir(parents=True)
    (repo / "package.json").write_text(json.dumps({
        "name": "demo",
        "dependencies": {"react": "^18.2.0", "lodash": "^4.17.0"},
        "devDependencies": {"jest": "^29.0.0"},
    }), encoding="utf-8")
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "demo"\ndependencies = ["requests>=2.31", "httpx[http2]>=0.27; python_version>\\"3.8\\""]\n',
        encoding="utf-8")
    (repo / "requirements.txt").write_text("# comment\nflask==2.3.0\n-r other.txt\n", encoding="utf-8")
    (repo / "go.mod").write_text(
        "module demo\n\ngo 1.21\n\nrequire (\n\tgithub.com/pkg/errors v0.9.1\n)\n", encoding="utf-8")
    (repo / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    vendor = repo / "node_modules" / "foo"
    vendor.mkdir(parents=True)
    (vendor / "package.json").write_text(json.dumps({"dependencies": {"evil": "1.0.0"}}), encoding="utf-8")
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "t@example.com"], repo)
    run(["git", "config", "user.name", "Test"], repo)
    run(["git", "add", "package.json", "pyproject.toml", "requirements.txt", "go.mod", ".gitignore"], repo)
    run(["git", "commit", "-q", "-m", "init"], repo)
    return repo


def test_parses_and_respects_gitignore():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        result = cm.collect(str(repo), None)
        names = {d["name"] for d in result["dependencies"]}
        manifests = {m["path"] for m in result["manifests_found"]}

        assert_true("react (package.json) parsed", "react" in names, hint=str(names))
        assert_true("jest dev dep parsed", "jest" in names)
        assert_true("flask (requirements.txt) parsed", "flask" in names)
        assert_true("go dep parsed", "github.com/pkg/errors" in names)
        assert_true("vendored manifest EXCLUDED (gitignore)",
                    "node_modules/foo/package.json" not in manifests, hint=str(manifests))
        assert_true("evil vendored dep NOT present", "evil" not in names, hint=str(names))

        # pyproject (toml) only parses on Python 3.11+ where tomllib exists.
        if cm.tomllib is not None:
            assert_true("requests (pyproject) parsed", "requests" in names, hint=str(names))
            assert_true("httpx extras stripped from name", "httpx" in names, hint=str(names))

        # scope + ecosystem fidelity
        jest = next(d for d in result["dependencies"] if d["name"] == "jest")
        assert_true("jest scope=dev", jest["scope"] == "dev", hint=str(jest))
        assert_true("jest ecosystem=npm", jest["ecosystem"] == "npm")
        assert_true("ecosystems include npm+go", {"npm", "go"} <= set(result["ecosystems"]),
                    hint=str(result["ecosystems"]))


def test_cli_writes_json():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        out = Path(tmp) / "out"
        r = subprocess.run([sys.executable, str(HELPER), str(repo), "--out", str(out)],
                           capture_output=True, text=True, timeout=30)
        assert_true("cli rc=0", r.returncode == 0, hint=r.stderr)
        deps = json.loads((out / "deps.json").read_text())
        assert_true("deps.json non-empty", len(deps["dependencies"]) >= 3)


def main():
    print("=== test_code_manifests.py ===")
    test_parses_and_respects_gitignore()
    test_cli_writes_json()
    print("\nAll code-manifests tests passed.")


if __name__ == "__main__":
    main()
