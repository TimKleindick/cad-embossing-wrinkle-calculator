# Source packages and releases

The original Excel workbook contains internal metadata. Keep it out of Git, CI artifacts, and releases, including renamed copies, screenshots, embedded data, and historical Excel binaries. The build uses the supplied reference numbers and formulas.

## Package safeguards

- `.gitignore` excludes common Excel filename patterns in either case. Because `git add -f` bypasses those patterns, enable the pre-commit hook with `git config core.hooksPath .githooks`.
- `python tools/package_preview.py audit` inspects the **staged blob bytes** of all regular Git files. It checks names, UTF-8 encoding, size, ZIP/OLE signatures, and workbook XML. It rejects symlinks and Git links and catches an unsafe index even when the working tree looks clean. CI repeats the audit.
- `PACKAGE_FILES` in `tools/package_preview.py` names each allowed source file explicitly. `reference/cases.csv` is the sole allowed CSV. Review additions to the allowlist because technical filters cannot identify sensitive metadata in arbitrary plain text.
- Package creation requires a clean commit and stops before output if a file is missing or a symlink, workbook, or foreign container is detected. The manifest records the source commit, CAD test status, and each file's SHA-256. ZIP ordering and timestamps are deterministic. Verification rechecks the exact allowlist and checksums after creation.
- The regular CI workflow uploads no artifacts. The manual preview release workflow passes the ZIP and SHA-256 file between jobs with one-day retention. Before publication, the publisher checks the manifest, source commit, ZIP hash, and tag target again. It attaches those two files.

## Reproducible local build

From a clean, tested Git checkout, run the following commands.

```sh
python3 -m unittest discover -s tests -v
python3 tools/package_preview.py audit
python3 tools/package_preview.py build
python3 tools/package_preview.py verify
```

The builder writes `dist/wrinkle-source-preview.zip` and `dist/wrinkle-source-preview.sha256`. Git ignores `dist/`. Move or remove the previous archive before rebuilding because the builder refuses to overwrite it. The checksums verify file integrity. Signatures and CAD certification are outside this build.

## Manual preview release

The source preview includes a manual publishing workflow. The release publishing path has yet to be exercised.

1. Review the changes on `main` and check that CI passes there. Workflow triggers avoid `pull_request_target` and `workflow_run`. Pull request code runs with read-only repository contents access.
2. Create and push a new tag such as `v0.1.0-source-preview.1` on the verified `main` commit. The workflow expects the tag to exist at that commit.
3. In Actions, manually run `Source preview release (CAD untested)` **on main**. Enter the existing tag and type `CAD UNTESTED SOURCE PREVIEW` exactly.
4. The verification job checks the tag pattern and target, regenerates nothing, checks the staged source and generated entries, and runs Python, Windows Script Host, and Windows dialog tests. Only the publishing job gets `contents: write`. The remaining jobs have `contents: read`. The workflow pins actions to full official commit SHAs and disables persisted checkout credentials.
5. Download the two assets from the resulting **prerelease** and verify the hash, manifest, and status. The title includes `Source Preview - CAD UNTESTED`, and the notes state the CAD test status. The workflow creates a new release through the tag.

The acknowledgement is a workflow input. The repository setup described here includes no configured GitHub environment approval, required reviewers, or branch or tag rules. GitHub documents the available protections and explains least-privilege permissions and SHA pinning. [GitHub's secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use)

GitHub also creates source archives from the release tag. The entire tagged source tree must therefore be suitable for publication. Keep the original workbook out of local Git history as well, including files that would be deleted in a later commit.

The final tag check reduces the time during which a changed tag can invalidate verification. Atomic tag immutability requires server-side tag protection, which the workflow does not configure.
