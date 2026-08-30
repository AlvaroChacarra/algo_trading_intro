# GitHub Infrastructure Contract --- Algorithmic Trading

**Status:** Authoritative target baseline — migration pending\
**Version:** 1.1\
**Date:** 2026-08-17\
**Owner:** AlvaroChacarra\
**Public repository:** `AlvaroChacarra/algo_trading_intro`\
**Private source repository:**
`AlvaroChacarra/algo_trading_intro_source`\
**Public site:** `https://alvarochacarra.github.io/algo_trading_intro/`

------------------------------------------------------------------------

## 1. Purpose

This document is the authoritative infrastructure contract for the
GitHub-based delivery of the Algorithmic Trading course.

The design has one primary objective:

> Keep all unreleased teaching material private while automatically
> publishing only the material explicitly authorized for release,
> without changing the current public GitHub Pages URL.

The system intentionally uses only two repositories and does not use
GitHub Classroom, student repositories, student push access, or
Git-based assignment submission.

------------------------------------------------------------------------

## 1.1. Source authority and pedagogical contract

Infrastructure and pedagogy have separate authorities.

-   **This `ARCHITECTURE.md`** is the golden source for GitHub
    infrastructure, repository topology, publication, security, CI, and
    Pages delivery.
-   **`CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md`** is the **golden
    source for pedagogy and assessment**.

Therefore, any statement in this architecture about lesson duration,
classroom structure, autonomous work, continuous tests, participation,
attendance, or final assessment is subordinate to the pedagogical
contract.

Current pedagogical invariants mirrored here for operational coherence:

-   standard in-person session: **approximately 50 minutes**;
-   normal allocation: **10 min continuous test + 20 min presentation +
    20 min guided exercises**;
-   students complete and consolidate required unfinished material
    autonomously after the session;
-   each assessed lesson normally generates **10 A/B/C/D questions in
    approximately 10 minutes**;
-   consecutive/double sessions do not force an immediate test between
    them; pending lessons are assessed at the next pedagogically valid
    opportunity;
-   some lessons or lesson components may be assigned asynchronously
    when pedagogically appropriate;
-   the final exam is mandatory and cumulative.

### Official assessment weights

  Component              Weight
  ------------------ ----------
  Attendance            **10%**
  Participation         **20%**
  Continuous exams      **40%**
  Final exam            **30%**
  **Total**            **100%**

The infrastructure must support this pedagogical model but must not
redefine it. If these mirrored values diverge from the pedagogical
contract, **the pedagogical contract prevails**.

------------------------------------------------------------------------

## 2. Alignment interview --- 10 decisions

The following answers are assumed to be approved unless explicitly
changed.

### Q1. Do we want exactly two repositories?

**Assumed answer: Yes.**

-   `algo_trading_intro_source`: private, authoritative source.
-   `algo_trading_intro`: public, generated distribution repository.

No organization, student repositories, assignment repositories, or
GitHub Classroom infrastructure is required.

------------------------------------------------------------------------

### Q2. Which repository is the source of truth?

**Assumed answer: `algo_trading_intro_source`, always.**

All authoring happens in the private repository.

The public repository is a derived publication target and must never
become the canonical source for course content.

Rule:

> Private source → controlled publication → public snapshot.

Never the reverse.

------------------------------------------------------------------------

### Q3. What must remain private until explicitly released?

**Assumed answer: everything not authorized by the publication
manifest.**

This includes, at minimum:

-   future classes;
-   future notebooks;
-   solutions;
-   answer keys;
-   exams;
-   exam generators;
-   hidden tests or validators that reveal answers;
-   internal teaching notes;
-   unpublished datasets or derived artifacts;
-   administrative scripts or configuration containing sensitive
    information.

A file is not publishable merely because it exists in the source tree.

Publication requires explicit authorization.

------------------------------------------------------------------------

### Q4. Should the public repository contain only released material?

**Assumed answer: Yes.**

`algo_trading_intro` must contain:

-   released teaching material;
-   released notebooks;
-   generated or publishable HTML;
-   JupyterLite assets required by students;
-   safe static assets;
-   safe build/runtime tooling required by GitHub Pages;
-   the public Pages workflow.

It must never contain future material, even temporarily or in an
intermediate commit.

------------------------------------------------------------------------

### Q5. How is the release date of each class defined?

**Assumed answer: through a machine-readable manifest in the private
repository.**

Canonical file:

`course_publish.yml`

Each releasable teaching unit has an explicit timestamp using the
`Europe/Madrid` timezone.

Example:

``` yaml
timezone: Europe/Madrid

classes:
  - id: "01"
    source: "01-python-i-data-model"
    publish_at: "2026-09-07T08:45:00+02:00"

  - id: "02"
    source: "02-python-ii-functional-book"
    publish_at: "2026-09-14T08:45:00+02:00"
```

The manifest is the publication policy.

The workflow schedule is only the mechanism that wakes the publisher up.

------------------------------------------------------------------------

### Q6. Do all classes need arbitrary independent publication times?

**Assumed answer: No. Prefer a stable course release hour.**

The normal operating model is:

-   one fixed local release time before class;
-   individual release dates controlled by `course_publish.yml`;
-   `Europe/Madrid` timezone;
-   workflow scheduled a few minutes away from the start of the hour to
    reduce GitHub Actions scheduling congestion.

If the timetable later requires two or more normal release times, add
the minimum required `schedule` entries rather than polling
continuously.

A manual `workflow_dispatch` trigger must always exist as fallback.

------------------------------------------------------------------------

### Q7. What should happen when the publication workflow runs?

**Assumed answer: rebuild the public snapshot from an allowlist, not
copy-and-delete.**

The publisher must:

1.  checkout the private source;
2.  validate the repository;
3.  read `course_publish.yml`;
4.  compute which classes are authorized at current time;
5.  create a fresh staging directory;
6.  copy only explicitly public infrastructure;
7.  add only authorized classes;
8.  build or validate the public snapshot;
9.  run leakage checks;
10. update the public repository only if every check passes;
11. push one atomic publication commit.

Forbidden pattern:

``` text
copy entire private repo
→ delete solutions
→ delete exams
→ publish what remains
```

Required pattern:

``` text
empty staging directory
→ explicit allowlist
→ authorized classes only
→ validate
→ publish
```

Default is deny.

------------------------------------------------------------------------

### Q8. How should the private repo authenticate against the public repo?

**Assumed answer: least-privilege cross-repository credential stored
only in the private repository.**

Preferred initial implementation:

-   fine-grained GitHub Personal Access Token;
-   repository access restricted to `AlvaroChacarra/algo_trading_intro`;
-   minimum repository content permissions required to update the public
    repository;
-   stored as a GitHub Actions secret in `algo_trading_intro_source`;
-   never committed to either repository;
-   never exposed to public workflows.

Secret name:

`PUBLIC_REPO_TOKEN`

Future migration to a GitHub App is allowed if operationally useful, but
is not required for a 15-student course.

------------------------------------------------------------------------

### Q9. Where should CI and GitHub Pages responsibilities live?

**Assumed answer: full course validation in private; public deployment
in public.**

#### Private repository

Owns:

-   source validation;
-   course generation;
-   exercise validation;
-   solution-aware checks;
-   smoke tests;
-   publication manifest validation;
-   release eligibility;
-   leakage checks;
-   publication to the public repository.

The current `course.yml` logic should migrate here.

#### Public repository

Owns only:

-   validation that can safely run on public material;
-   static-site build where needed;
-   JupyterLite/public assets;
-   GitHub Pages deployment.

The current `pages.yml` responsibility remains public, but it may be
simplified after migration.

------------------------------------------------------------------------

### Q10. What happens if automation fails?

**Assumed answer: fail closed. Never publish partially.**

If any validation, build, credential, leakage, or push step fails:

-   the current public site remains unchanged;
-   no partial class is published;
-   no destructive cleanup is performed on the public repository;
-   the workflow fails visibly;
-   the professor can correct the issue and invoke `workflow_dispatch`.

Availability is secondary to confidentiality.

Rule:

> A delayed class is acceptable. An accidentally released future class,
> solution, or exam is not.

------------------------------------------------------------------------

## 3. Repository architecture

### 3.1 Private authoritative repository

Repository:

`AlvaroChacarra/algo_trading_intro_source`

Visibility:

`private`

Suggested structure:

``` text
algo_trading_intro_source/
├── .github/
│   └── workflows/
│       ├── course.yml
│       └── publish.yml
│
├── framework/
│   └── _build/
│       ├── build_course.py
│       ├── build_pages.py
│       ├── check_pages.py
│       ├── publish_course.py
│       └── ...
│
├── 01-python-i-data-model/
├── 02-python-ii-functional-book/
├── ...
├── 15-final-exam/
│
├── solutions/
├── exams/
├── internal/
│
├── course_publish.yml
├── public_files.yml
└── README.md
```

This repository may contain the complete history of the course because
it is private.

All content changes are made here.

------------------------------------------------------------------------

### 3.2 Public distribution repository

Repository:

`AlvaroChacarra/algo_trading_intro`

Visibility:

`public`

Role:

-   distribution;
-   GitHub Pages;
-   browser-accessible notebooks;
-   JupyterLite;
-   released HTML;
-   public documentation.

It is not an authoring repository.

Expected structure is a sanitized subset/generated snapshot of the
private source.

The existing Pages URL must remain:

`https://alvarochacarra.github.io/algo_trading_intro/`

------------------------------------------------------------------------

## 4. Publication model

### 4.1 Two independent controls

A class is publishable only when both conditions are true:

1.  it is explicitly declared in `course_publish.yml`;
2.  its `publish_at` timestamp has been reached.

Conceptually:

``` text
declared AND due → eligible
otherwise        → private
```

A directory merely existing in the source repository does not make it
eligible.

------------------------------------------------------------------------

### 4.2 Publication manifest

Example contract:

``` yaml
version: 1
timezone: Europe/Madrid

classes:
  - id: "01"
    path: "01-python-i-data-model"
    publish_at: "2026-09-07T08:45:00+02:00"
    enabled: true

  - id: "02"
    path: "02-python-ii-functional-book"
    publish_at: "2026-09-14T08:45:00+02:00"
    enabled: true
```

Recommended semantics:

-   `enabled: false` overrides time and prevents release;
-   timestamps are explicit and timezone-aware;
-   duplicate IDs are invalid;
-   missing paths are invalid;
-   malformed timestamps are invalid;
-   a future timestamp always prevents publication.

------------------------------------------------------------------------

## 5. Scheduled workflow

Canonical workflow:

`.github/workflows/publish.yml`

Required triggers:

``` yaml
on:
  schedule:
    - cron: "47 8 * * 1"
      timezone: "Europe/Madrid"

  workflow_dispatch:
```

The exact weekday/hour must match the final timetable.

The example intentionally uses minute `47`, not `00`, because scheduled
GitHub Actions can be delayed during high-load periods, especially
around the start of an hour.

The manifest remains the source of release authorization.

The scheduled trigger must not contain the publication policy.

------------------------------------------------------------------------

## 6. Publication transaction

The release workflow follows this state machine:

``` text
1. CHECKOUT PRIVATE SOURCE
2. VALIDATE SOURCE
3. READ MANIFEST
4. RESOLVE CURRENT TIME
5. CALCULATE AUTHORIZED CLASSES
6. CREATE EMPTY STAGING TREE
7. COPY PUBLIC INFRASTRUCTURE ALLOWLIST
8. COPY AUTHORIZED CONTENT
9. BUILD PUBLIC ARTIFACTS
10. RUN LEAKAGE + INTEGRITY CHECKS
11. CHECKOUT PUBLIC REPO
12. SYNCHRONIZE SNAPSHOT
13. VERIFY FINAL DIFF
14. COMMIT
15. PUSH
16. PUBLIC PAGES WORKFLOW DEPLOYS
```

Any failure before step 15 aborts publication.

------------------------------------------------------------------------

## 7. Idempotency

Publication must be idempotent.

If the workflow runs twice with the same:

-   private source commit;
-   manifest;
-   current eligibility set;

the second run should produce no functional change.

If there is no public diff:

-   do not create an empty commit;
-   exit successfully.

This permits safe manual re-runs.

------------------------------------------------------------------------

## 8. Public snapshot policy

The publisher must use positive selection.

Two possible positive selectors are allowed:

### A. Infrastructure allowlist

Example:

``` yaml
public_infrastructure:
  - ".github/workflows/pages.yml"
  - "framework/_build/build_pages.py"
  - "framework/_build/check_pages.py"
  - "framework/_build/pages_e2e.js"
  - "requirements-pages.txt"
  - "README.md"
  - "assets/"
```

### B. Released class allowlist

Derived dynamically from `course_publish.yml`.

Anything not selected by A or B is absent from staging.

------------------------------------------------------------------------

## 9. Security invariants

The following are non-negotiable invariants.

### INV-01 --- No future material in public Git history

A future class, solution, exam, answer key, or hidden validator must
never be committed to the public repository.

Not even temporarily.

------------------------------------------------------------------------

### INV-02 --- No secrets in public

No PAT, API token, credential, private key, or sensitive environment
value may appear in:

-   committed files;
-   generated public files;
-   workflow logs;
-   static HTML;
-   notebook outputs.

------------------------------------------------------------------------

### INV-03 --- Cross-repository credential exists only in private source

`PUBLIC_REPO_TOKEN` is stored only in the Actions secrets of
`algo_trading_intro_source`.

------------------------------------------------------------------------

### INV-04 --- Fail closed

If publication eligibility cannot be determined confidently, publication
stops.

Unknown state means private.

------------------------------------------------------------------------

### INV-05 --- Public repository is disposable

The public repository must always be reproducible from:

-   a private source commit;
-   the manifest;
-   the publisher code.

No unique authoritative content may exist only in the public repository.

------------------------------------------------------------------------

### INV-06 --- Solutions and exams are opt-out impossible

Sensitive categories are never published through generic recursive
copying.

If solutions are ever intentionally released, that requires a separate
explicit publication rule.

------------------------------------------------------------------------

## 10. Pre-publish leakage checks

Before the public repo is modified, staging must be checked for
prohibited paths and patterns.

Minimum checks:

-   `solutions/`;
-   unreleased class directories;
-   private/internal directories;
-   final exam source/generator where not public;
-   answer-key filenames;
-   secret-like filenames;
-   accidental `.env`;
-   private config files.

Optional defense-in-depth:

-   scan staged text for known secret names;
-   compare staged class IDs against eligible manifest IDs;
-   verify every staged top-level teaching directory is authorized.

A leakage check failure blocks publication.

------------------------------------------------------------------------

## 11. CI responsibilities

The current public `course.yml` already validates:

-   framework tests;
-   smoke test;
-   exercise validation;
-   generated material consistency;
-   selected runnable scripts;
-   browser e2e on PRs.

That responsibility moves to the private source repository because some
validation requires full course content and solutions.

The public repository does not need access to unreleased material to
validate itself.

------------------------------------------------------------------------

## 12. GitHub Pages responsibilities

The current public Pages pipeline already:

-   builds a static `_site`;
-   validates HTML, links, and base path;
-   validates mobile experience;
-   uploads the Pages artifact;
-   deploys GitHub Pages.

This remains the conceptual responsibility of `algo_trading_intro`.

After the two-repository migration, it may be simplified, but the
existing URL and user experience are invariants.

------------------------------------------------------------------------

## 13. Existing public history

The current `algo_trading_intro` repository has previously been public
with the full course material.

Therefore:

> Anything historically committed while public must be considered
> potentially disclosed.

Removing a file in a later commit is not sufficient because Git history
may retain it and external clones may already exist.

Migration rule:

1.  create the private source from the complete current project;
2.  verify the private copy;
3.  define the initial public release set;
4.  recreate/sanitize the public repository history if confidentiality
    of future material matters;
5.  replace any exam or secret material that was previously public and
    must now be confidential.

History rewriting improves the public repository state but cannot revoke
external copies already made.

------------------------------------------------------------------------

## 14. Manual operations

The professor must retain two manual controls.

### Manual publication

`workflow_dispatch`

Use cases:

-   scheduled workflow delayed;
-   exceptional early publication;
-   repaired failed deployment.

Manual execution does **not** bypass `course_publish.yml` by default.

A separate explicit override input may be added later, but should
require deliberate confirmation.

### Emergency disable

Setting:

``` yaml
enabled: false
```

for a class must prevent its release even if `publish_at` has passed.

------------------------------------------------------------------------

## 15. Workflow permissions

Principle:

> Minimum permissions required per workflow.

### Private `course.yml`

Normally:

``` yaml
permissions:
  contents: read
```

unless a specific job requires more.

### Private `publish.yml`

The default repository `GITHUB_TOKEN` should have minimal local
permissions.

Cross-repository write uses `PUBLIC_REPO_TOKEN`.

### Public `pages.yml`

Only permissions required by Pages deployment:

``` yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

No administrative cross-repository secret exists in the public
repository.

------------------------------------------------------------------------

## 16. Publication commit convention

Automatically generated publication commits should be recognizable.

Recommended format:

``` text
release: publish course through class 07
```

Commit metadata should also make it possible to recover:

-   source repository commit SHA;
-   eligible class set;
-   workflow run.

Recommended commit body:

``` text
source_sha: <PRIVATE_SOURCE_SHA>
released_classes: 01,02,03,04,05,06,07
generated_by: publish.yml
```

Do not include sensitive source paths or secrets.

------------------------------------------------------------------------

## 17. Rollback

Rollback must not require editing generated content manually.

Preferred procedure:

1.  fix the manifest or source;
2.  run `publish.yml`;
3.  regenerate the authoritative public snapshot;
4.  push corrected state.

For emergency rollback of a defective public release, publication
tooling may support a manifest override or revert, but future content
confidentiality must never depend on a later revert.

Once sensitive material reaches a public commit, treat it as disclosed.

------------------------------------------------------------------------

## 18. Cost model

The architecture is intentionally lightweight:

-   one private repository with CI/publication Actions;
-   one public repository with Pages;
-   no per-student repositories;
-   no student Actions;
-   no continuous polling;
-   no external cloud infrastructure;
-   no GitHub Classroom dependency.

Normal publication requires only a small number of workflow runs per
class.

This is the preferred architecture for the course because operational
simplicity is more valuable than automating unused assignment
infrastructure.

------------------------------------------------------------------------

## 18.1. Pedagogical delivery implications

Publication scheduling must be capable of supporting the pedagogical
contract without assuming a rigid one-session/one-lesson/one-assessment
mapping.

The publication model must therefore allow:

-   material to be released before an in-person session so students can
    access it;
-   autonomous lessons to be released independently of a classroom
    presentation;
-   two consecutive lessons to remain available for later combined
    assessment;
-   exercise and consolidation material to remain accessible after the
    corresponding session;
-   assessment material, answer keys, question banks, and exam
    generators to remain private unless explicitly authorized.

The infrastructure does **not** calculate grades. It only preserves the
confidentiality and availability required by the assessment model.

------------------------------------------------------------------------

## 19. Non-goals

This architecture does **not** provide:

-   student Git submissions;
-   private student repositories;
-   GitHub-based grading;
-   GitHub-based attendance;
-   AI detection;
-   plagiarism detection;
-   secure examination delivery;
-   Moodle replacement.

Those responsibilities are deliberately outside GitHub infrastructure.

GitHub is used for:

-   authoring;
-   validation;
-   controlled course publication;
-   static delivery;
-   notebooks/JupyterLite;
-   versioned infrastructure.

------------------------------------------------------------------------

## 20. Acceptance criteria

The architecture is considered correctly implemented only if all tests
below pass.

### AC-01

Given classes 01--03 due and class 04 future:

``` text
public contains 01,02,03
public does not contain 04
```

### AC-02

Searching the complete public Git history after migration finds no
unreleased class, current solution, or current exam intended to remain
confidential.

### AC-03

Running `publish.yml` twice without source changes produces no second
content change.

### AC-04

A build failure leaves the public repository unchanged.

### AC-05

A leakage-check failure leaves the public repository unchanged.

### AC-06

Removing access to `PUBLIC_REPO_TOKEN` causes publication to fail
without changing the public repository.

### AC-07

`workflow_dispatch` can republish the same eligible snapshot safely.

### AC-08

Changing `enabled` from `true` to `false` before publication prevents
the class from appearing publicly.

### AC-09

A class with a future `publish_at` cannot be published by the normal
scheduled workflow.

### AC-10

The existing public URL continues serving the course:

`https://alvarochacarra.github.io/algo_trading_intro/`

------------------------------------------------------------------------

## 21. Final architecture decision

The approved target architecture is:

``` text
algo_trading_intro_source [PRIVATE]
        |
        |  course.yml
        |  publish.yml
        |  course_publish.yml
        |  PUBLIC_REPO_TOKEN
        |
        |  build + allowlist + validation
        v
algo_trading_intro [PUBLIC]
        |
        |  pages.yml
        v
GitHub Pages
```

Core principle:

> The private repository decides what is allowed to exist publicly.\
> The public repository never decides what should be private.

Any future infrastructure change must preserve the security invariants
and acceptance criteria in this document.

------------------------------------------------------------------------

## 22. External platform assumptions

Validated against GitHub documentation on 2026-08-17:

-   scheduled workflows support POSIX cron;
-   scheduled workflows can specify an IANA timezone such as
    `Europe/Madrid`;
-   scheduled runs may be delayed under load, particularly near the
    start of an hour;
-   scheduled workflows run from the default branch;
-   cross-repository writes require credentials with permission on the
    target repository rather than relying on the source repository's
    default `GITHUB_TOKEN`.

These are implementation assumptions, not business rules. If GitHub
changes platform behavior, implementation may change while preserving
the architectural contract above.
