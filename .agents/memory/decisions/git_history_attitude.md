# Git history attitude — approved direction, policy not yet migrated

Status: **maintainer direction approved; current additive/no-rewrite rules remain authoritative until the corresponding reminder is implemented.**

The maintainer distinguishes meaningful **Git history** from incidental **commit history**.

Working interpretation for future design/review:

- Preserve meaningful historical repository states and unique work.
- Do not preserve administrative commit boundaries merely because they happened.
- A claim → implementation → completion sequence may be a reasonable squash candidate when claim/completion only encode task bookkeeping and no useful repository state disappears.
- A fixup may be foldable when it only makes an immediately preceding commit represent what that checkpoint was clearly intended to be.
- Conversely, if commit B introduced a substantive state and commit C later changed that state, squashing B+C destroys meaningful history even if the combined result looks cleaner; default against that.
- Large deletion, large squash, destructive rebase, and force movement are **fat red flags requiring scrutiny**, not automatic proof that the operation is wrong.
- Published-history topology is a separate risk: rewritten SHAs can invalidate concurrent branches, links, reviews, clones, and external references even when semantic history preservation would otherwise permit cleanup.

Do not use this note as blanket authorization to rewrite current history. The active repository workflow still requires explicit authorization under its existing rules until the future cleanup policy deliberately replaces them.
