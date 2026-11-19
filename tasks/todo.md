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


# Main branch and publication audit

Context: owner explicitly requested main/default and public visibility after a complete confidentiality review. Snapshot: only featurebranch/default existed; no master/main, tags, releases, forks, PRs or issues. Preserve all history and other branches; no forced updates or unrelated rights/deployments/releases.

Routing: hard; current GPT-6/high. Independent publication audit delegated to /root/publication_review; primary handles remote logs, documentation and serialized Git/API mutations. Constraints: full historical blob/metadata scan, workbook exclusion, visibility remains private while any disclosure decision is pending.

- [x] Inventory local/remote refs and inspect every historical commit/tree/blob.
- [x] Inspect all Actions logs, artifacts and repository metadata/settings.
- [x] Create main from the verified head and update current download links; preserve feature branch.
- [x] Run checks and push main; confirm its CI, then set main default.
- [ ] Resolve historical personal author-email disclosure before public visibility.
- [ ] Recheck remote state and publish only if the audit and explicit disclosure decision permit it.

Finding: historical commits contain the owner's personal author/committer email, which is not listed on the public profile. No credential is implied, but publication is held pending the owner's disclosure choice. New commits use the GitHub noreply identity locally; no historical rewrite or promise to purge cached GitHub objects has been made.

Remote audit snapshot: all5 Actions runs /17 job logs (779765 bytes) downloaded and scanned locally;0 artifacts, releases, tags, issues, PRs, deployments, hooks, repository secret names, variables or environments. Path-pattern hits in JSON are GitHub API /users/... URLs, not workstation filesystem paths; reviewed as false positives. No employer or credential matches in metadata/logs. No private raw audit files are committed.


## Publication review

Completed: main created from verified49c9568 without losing source/history; current download links updated; featurebranch retained; main pushed and remotely set as default. Remote visibility deliberately remains private. CI43728154687 on a2b48947e51528bc80ddb971b602f1eced684020 passed. Existing21tests and generated freshness/staged source audit pass; calculation kernels and CAD source entries unchanged.

Audit evidence:5initialcommits/39trees/63blobs/43paths independently examined; all5pre-transitionActions runs and17logs scanned,0artifacts/optionalstoredsurfaces. One personal author/committer email is present in all5initialcommits and historical Actions run metadata. New commits use the account's noreply identity. The owner's disclosure choice is pending; no history rewrite, force-push, deletion or public visibility action executed. This is the remaining blocker, not an automatic approval rejection.

Roles: independent publication audit (/root/publication_review); primary handled remote review, docs, commits and API setting. Separate commit agent skipped for serialized Git ownership. Complexity hard; current GPT-6/high. Raw audit data stays outside Git. Recheck future logs/current remote state before any later authorized visibility change.

# CATScript startup directive

Scope: targeted CATIA startup bug fix. GPT-6.2-sol, direct execution for a small change. Keep the existing calculation and generated-file check. Compile the delivered header in Windows CI.

- [x] Locate the reported directive and compare the generator with the Windows test harness and Dassault's V5 rules.
- [x] Observe the regression test failure, fix and regenerate the entry, and run local verification.

Review: the regression failed on the old first line and all 22 tests passed after regeneration. The Windows runner now compiles the original delivered file before the behavior tests. A rerun inside CATIA V5 R32 is the remaining host check. The primary agent handled the targeted fix, documentation and Git work.

# CATIA illustrated results

Standard change using GPT-6.2-sol. Primary implementation with independent geometry review. Reuse the existing CATScript solver and publish a self-contained entry locally. CATScript MsgBox supports plain text and fixed icons, so open a local offline browser result after a successful calculation and retain the text pages on launch failure.

- [x] Verify that the generated file embeds the complete template. Add Windows workflow cases for illustrated output, fallback, decimal handling and flat results.
- [x] Add the dimensioned profile, definitions and existing results to a single page.
- [x] Regenerate the standalone macro and check reference and flat-case results.
- [x] Verify browser rendering, package contents and documentation. Record CATIA host limits.

## Review

23 local Python tests passed, including a failing-then-passing regression test for the embedded HTML. Headless Chrome rendered the 40/30, flat 30/30, and 60/30 cases with matching result rows. Reference screenshot inspected for dimensions and legibility. The VBA workflow tests are prepared for the next Windows CI run. CATIA V5 R32 execution and Windows browser launch have not been tested for this revision. The primary agent handled the implementation, documentation and local Git work. Numerical annotations reviewed independently by `/root/numerical_review`.

# Shared English CAD results

Standard change using GPT-6.2-sol. Preserve both tested solver cores and package protections. Give the two direct launchers the same offline illustrated report, and translate all current UI and repository guides to English. Documentation translations delegated independently to `english_guides` and `english_reference`.

- [x] Test standalone NX report output using the existing reference and flat cases.
- [x] Share the report template, implement NX browser launch and translate both UI paths.
- [x] Verify the delivered files, browser rendering and English documentation.

Review: the new standalone NX report test failed before implementation. All 24 local tests now pass. Both shipped files embed the same template. Chrome rendered the English reference and flat reports and the reference image was inspected. The Python and VBA calculation cores have no diff. Both source entry points and the optional CAD interfaces are in English. Documentation translation and verification were handled by `/root/english_guides` and `/root/english_reference`. Windows CI will exercise the actual NX dialog with a captured report and the CATScript runner. CAD host launch is a workstation check.

# Compact shared report and fracture screening

Standard change using GPT-6.2-sol. Preserve the two calculation cores, numeric reference data, and offline single-file delivery. Use the requested cosine strain result and manual fracture elongation input. Classify unrounded values by the requested thresholds. Keep the screening distinct from a real crack prediction and DIN requirements. Parallel work on native text fallbacks and guides by `compact_fallbacks` and `screening_docs`.

- [x] Verify threshold boundaries and unchanged computational inputs.
- [x] Simplify the shared chart and tables, then regenerate both macro files.
- [x] Exercise browser interaction and inspect the reference sketch.

Review: 25 local tests passed. Browser checks covered the reference values, the disclosure and all three bands, decimal comma, invalid input, and a flat profile without thickness. The standalone files share one template, and both solver cores and numeric reference data are unchanged. GitHub Actions records the platform checks for this revision. CAD host launch remains a workstation check.
