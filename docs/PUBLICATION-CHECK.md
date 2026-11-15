# Publication check

Audit date: 2026-11-15. The owner requested `main` as the default branch and public visibility after confidentiality review. Visibility stays private while the historical author-email disclosure decision is pending. This report contains no raw credentials, personal email address or raw CI logs.

## Inventory before transition

Only `feat/excel-compatible-source-preview` existed, at `49c9568d90fd74dc5ef03822db82f9936574d50d`, and was the remote default. No `master` or `main` existed. There were no foreign or uncommitted changes, forks, tags, releases, PRs, issues or deployments. The original branch is preserved; no force push or history rewrite is used for the main transition.

## Examined surfaces

- All 5 historical commits, 39 trees, 63 distinct blobs (267427 bytes), and 43 historical file paths. Full Git object integrity check passed, with no dangling objects.
- Author/committer names, emails and commit messages; every historical file name and payload, including removed/replaced file versions.
- All 5 Actions runs, all 17 job logs (779765 bytes), and every run's artifact inventory. Artifact count0. No reusable workflow or private external repository path was found.
- Repository description, homepage, topics, branches, tags, releases, issues, PRs, deployments, hooks, secret-name inventory, variable inventory and environment inventory. Counts0 for all optional stored surfaces; description contains only this calculator's purpose. Wiki and Pages are disabled.

## Findings and classification

No employer reference, confidential workstation/network path, original workbook, ZIP/OLE workbook container, embedded binary, recognizable access token/private key/password, or suspicious encoded payload was found in the examined source/history/logs/metadata. Pattern checks and manual review were used; this is a recorded audit, not a mathematical guarantee that arbitrary text cannot contain sensitive information.

Synthetic workbook/secret strings in adversarial tests are test fixtures, not a supplied workbook or credentials. GitHub token expressions in workflows are runtime references, not committed tokens. `C:\CAD-Test\Wrinkle` is a neutral documented example. JSON path-pattern matches are public GitHub API `/users/...` URLs, not local home directories.

One disclosure question remains: all five original commits contain the owner's personal author/committer email, which is not exposed by the public profile. Historical Actions run metadata also contains the author email. It is not a credential, but public visibility would expose it. The owner has been asked whether this existing metadata may become public. New commits use the account's GitHub noreply identity in this repository only; global/account settings were not changed.

No history rewrite, deletion of Actions records, deletion of branches, or claim of cached-object removal is made. [GitHub documents](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) that old SHA/cache accesses can remain after a rewrite. Its [commit-email documentation](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address) also distinguishes future commit configuration from old metadata. Public visibility is gated on resolving this actual disclosure question.

## Transition and verification

`main` is based on the verified source head above. Current README/download links point to main; dated historical verification records preserve their original branch/commit references. The calculation kernels, generated CAD entry files, workbook exclusions and minimal CI permissions are unchanged. No additional rights, deployment or release is requested or created.

After pushing main, verify its complete CI and then set it as the remote default. Re-read default branch and visibility remotely. If publication becomes authorized after the email decision, recheck new run logs and current metadata before changing visibility, then verify public access without credentials. Until that decision, the repository must remain private.


Verified transition: main was pushed at `a2b48947e51528bc80ddb971b602f1eced684020`, and [CI43728154687](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43728154687) passed. GitHub was then queried after the default-branch update: `default_branch=main`, `visibility=private`. The featurebranch remained at its original verified head. Public visibility is still pending the owner's explicit historical-email disclosure decision; no additional rights, release or deployment was created.
