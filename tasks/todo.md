# Excel-compatible CAD source preview

Context: reproduce the supplied workbook mathematics without storing the workbook; no geometry creation. Fresh, empty private repository in a separate clone; no existing files or checkout instructions to preserve.

Routing: hard; current GPT-6 session, high reasoning (requested legacy Codex routing models unavailable). Independent numerical review delegated to numerical_review; implementation, packaging and documentation handled by primary agent. CAD products and VBA compiler unavailable on this Mac.

Execution constraints: keep 1000-segment polygon semantics; report fit length error separately; never include spreadsheets or arbitrary workspace files in packages.

- [x] Confirm Tim's identity, empty private repository and isolated branch; inspect repository instructions (none).
- [x] Record numerical contracts in shared references and watch core tests fail.
- [x] Implement and verify Python amplitude solve and unconstrained form fit.
- [x] Add compatible VBA core with independent shared-reference runner.
- [x] Add NX Block Styler and CATIA UserForm source adapters and exact build instructions.
- [x] TDD package guard with adversarial workbook/disguised ZIP/symlink cases.
- [x] Add least-privilege CI and gated source-preview release workflow.
- [x] Review mathematics independently; run local tests and audit package.
- [x] Conventional commit, push branch, inspect remote CI and report tested limits.

- [x] Normalize ZIP creator metadata after cross-platform hash comparison; verify identical archives.

## Review

Changed: pure Python and VBA cores; shared scalar references; NX and CATIA source adapters; adversarial packaging tests and file allowlist; CI and manual prerelease workflow; native build/test guides and mathematical contract.

Verification: 17 local unittest cases pass, Python compileall passes, independent golden-section/Simpson numerical check passes. Precommit source archive has exactly 22 allowlisted files plus a status/checksum manifest. LF checkout normalization and explicit ZIP creator metadata added after observing platform hash differences; regression demonstrated red then green. Staged index audit and final commit-package build run immediately before/after commit. Windows cscript passed in CI run 43723275112 under initial en-US and de-DE locale, including a deliberately failing radius mutation. All three Linux/Windows jobs passed. No VBA compiler or CAD host is present. No native DLX/CATVBA binaries or geometry are generated. Workbook input was not supplied or used.

Review findings handled: region-independent CSV fixture parsing (en-US and de-DE host test passes scheduled in CI), re-resolve release tag immediately before publication, clarify manual acknowledgement versus unconfigured environment approvals. Remaining release limitation: server-side immutable tag rules are not configured; manual release publication and all CAD acceptance tests remain unexecuted.

Subagents: independent numerics (id: /root/numerical_review), source/security review (id: /root/source_security_review). Primary handled implementation, documentation and commit. No separate commit agent: serialized Git ownership avoids overlapping mutations. Model/effort: current GPT-6 agent, high reasoning; legacy model names from routing skill unavailable. Complexity: hard.

Remote: first verified source commit `72190950f290f3ec6bb4c09453f72ca5b804bcf1` pushed; [CI evidence](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43723275112) succeeded. Repository stays private. As the first branch in an empty repository, GitHub selected the feature branch as default; `main` does not yet exist. No merge, tag or release performed. Final documentation commit records this evidence and is rechecked by CI.

# Directly runnable CAD entry files

Context: Tim wants to open prepared entry files, without manually drawing forms or creating binary projects. Continue the same isolated branch, preserve the pure cores and Excel semantics. Detailed CAD-only steps, download/extract, settings, verified dependencies, inputs, expected results and troubleshooting are required.

Routing: hard; current GPT-6 agent, high reasoning. CATIA interface research delegated to /root/catia_entry_research. Primary owns implementation/Git; independent source review follows. Constraints from lessons: inline unchanged kernels, disclose host limits, audit staged bytes and only exact source paths in packages.

- [x] Record direct-entry design and tests; observe missing behavior failures.
- [x] Implement generated native Windows dialog in a self-contained NX Python journal.
- [x] Implement self-contained CATScript using native InputBox/MsgBox and invariant parsing.
- [x] Verify generated-file freshness, same reference calculations and safe packaging.
- [x] Execute actual Windows dialog automation and actual CATScript workflow source in CI.
- [x] Rewrite detailed guides around delivered entry files; retain optional designer guides.
- [x] Review, Conventional Commit, push same branch, inspect CI and artifact contents.

## Direct-entry review

Changed: generated self-contained NX Python/Win32 journal and CATScript; native dialog adapters; strict locale-independent parsers; generation/freshness tool; standalone and Windows UI/workflow tests; explicit source allowlist; CI and detailed workstation guides. Pure calculation kernels have no diff.

Verification before push: 21 local tests pass (new four tests first failed because entry functionality was absent), Python compileall passes, independent golden-section/Simpson check passes, generated freshness passes, 32-file allowlisted package validates. Windows actual-dialog and generated CATScript workflow tests require the next CI run; CAD integration remains untested. No Excel files, binary projects or geometry generation.

Routing: hard, current GPT-6/high. CATIA research (id: /root/catia_entry_research), source/security review (id: /root/source_security_review); primary handles code, docs and serialized Git operations. Dedicated commit agent skipped to keep one Git owner.

Independent direct-entry review found no production must-fix. Its test-harness hang concern was fixed: every cross-process text/check/click/close message uses SendMessageTimeoutW with explicit 5-second bounds and cleanup terminates only the spawned test process if needed. Native Windows execution remains pending CI.

Direct-entry result: commit `9627bab3a971a91d3b205ff05b73b64d208f3627` pushed to the same branch. CI43726095118 passed all four jobs, including real Win32 UI outside NX and actual generated CATScript controlled-I/O workflows. All five local/CI package hashes match; artifact uploads0. Unpacked final sources passed21tests and freshness check. CAD host integration, ctypes/engine availability there, import/registration, licenses and real workstation setup remain untested. Final documentation records these results and qualifies both additional user-supplied research links by version/source.
