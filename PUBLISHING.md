# Publishing checklist

Status: **pushed to a PRIVATE GitHub repo. Not public. No DOI. No preprint.**

## Cleared before the private push (5 Sept 2026)

- [x] No secrets, API keys or tokens anywhere in the tree or history
- [x] No email addresses or personal contact details
- [x] No absolute home paths leaking into committed files
- [x] Licence present — MIT for code, CC-BY-4.0 for prose, third-party data
      under its own terms, plus an explicit no-operational-warning-use clause
- [x] Derived `.npy` arrays untracked (54 MB, regenerable in ~10 min from
      `calcs/sentinel_wedge.py`)
- [x] Third-party screenshots untracked — Google Earth imagery and news stills
      credited to @vantortech via Republic Digital are not ours to
      redistribute. The *measurements* taken from them are in the dossier
      with provenance; the images are not.

## MUST clear before making it PUBLIC

- [ ] **Purge the removed binaries from git HISTORY.** `git rm --cached` stops
      tracking them but they remain in every earlier commit — 57 MB of pack,
      including the third-party screenshots. Use `git filter-repo` before the
      repo goes public, not after.
- [ ] **`data/ffd_report.pdf` (9.2 MB)** — Nepal DHM/FFD official press
      release. Redistribution terms unverified. Decide: link to the source
      instead of redistributing, or confirm terms with DHM.
- [ ] **`data/198_discharge.csv`** — same question, DHM data.
- [ ] `outreach/gift-note.md` names four people we intend to contact. Harmless
      but oddly public. Decide whether it belongs in the repo at all.
- [ ] Read the whole thing once more as a stranger would.
- [ ] Decide branch name — currently `master`, GitHub's default is `main`.

## Then, in order

1. Public repo
2. **Enable GitHub Pages** — Settings → Pages → Source: `main`, folder `/docs`.
   Gives https://djhume.github.io/nepal-flood-2026/ . Regenerate the folder with
   `python report/build_site.py` whenever the pages change. This is what makes
   the work readable *and indexable* — GitHub renders .html as source code, and
   Claude artifacts are not crawled at all, so Pages is the only version a
   search engine or an AI with web search can find.
3. Zenodo DOI via the GitHub release integration (tag a version; the retraction
   history must be visible IN the archived snapshot, not just in the git log)
4. EarthArXiv preprint, citing the Zenodo DOI
5. Four emails, no reply expected — ICIMOD, Kargel, Petley, Willsey
6. Nothing else. No press, no media, no amplification.

## Still open scientifically (none of it blocks publication)

- The modelled deposit sits at km 0–36; stereo measurement puts it at 40–43
- Galchhi stage rise fails out-of-sample (3.6 m modelled vs ~9 observed);
  lower-reach channel widths are a rule of thumb, not measurements
- Composition (wetness, ice fraction) unresolved by our observables
- Seti 2012 needs a full rebuild — spec in `hindcast/seti/RESULTS.md`
- Nepali translation withdrawn pending a native speaker
