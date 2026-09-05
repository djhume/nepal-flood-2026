# Publishing checklist

Status: **public on GitHub, live on GitHub Pages at
https://djhume.github.io/nepal-flood-2026/ . No DOI. No preprint. No outreach
emails sent.**

## Cleared before the public push (5 Sept 2026)

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

## Done since

- [x] **Purged the removed binaries from git HISTORY** with `git filter-repo`.
- [x] Renamed the branch `master` → `main`.
- [x] Added the GitHub Pages build (`report/build_site.py` → `docs/`).
- [x] **Read the whole thing once more as a stranger would** — 5 Sept, and it
      was worth it. The cold read found three things the authors could not see:
      the melt ceiling was stated as "far below" 20 Mm³ while the chart showed
      15 against 20 (fixed by carrying the size envelope into the energy
      budget: the real ceiling is 1.1–2.5); a chart bar labelled "river already
      lying in the channel, 47" was actually the whole wave at Devghat; and the
      border-clock resolution was written with more confidence than its sources
      carry. It also found that **the published workings were three days behind
      the findings** — the reviewer page did not contain findings 04 or 05 at
      all. That is now built by a script rather than by hand.

## STILL to clear

- [ ] **`data/ffd_report.pdf` (9.2 MB)** — Nepal DHM/FFD official press
      release. Redistribution terms unverified. Decide: link to the source
      instead of redistributing, or confirm terms with DHM.
- [ ] **`data/198_discharge.csv`** — same question, DHM data.
- [ ] `outreach/gift-note.md` names four people we intend to contact. Harmless
      but oddly public. Decide whether it belongs in the repo at all.
- [ ] **Find a Nepali reader.** This is the largest gap in the work and the one
      thing that cannot be closed from Wellington. The site now says so
      explicitly rather than leaving it as a silence.

## Then, in order

1. ~~Public repo~~ — done
2. ~~**Enable GitHub Pages**~~ — done. Source: `main`, folder `/docs`.
   Regenerate with `python report/build_site.py` whenever the pages change —
   and rebuild the workings alongside them, see README. This is what makes
   the work readable *and indexable*: GitHub renders .html as source code, so
   Pages is the only version a search engine or an AI with web search can find.
3. Zenodo DOI via the GitHub release integration (tag a version; the retraction
   history must be visible IN the archived snapshot, not just in the git log)
4. EarthArXiv preprint, citing the Zenodo DOI
5. Four emails, no reply expected — ICIMOD, Kargel, Petley, Willsey.
   **One thing to check before the Kargel email:** the site used to describe his
   6 min 50 s as independent confirmation of our clock. It is not demonstrably
   independent — his stated basis is "22 km at 193 km/h" with no method — and
   the pages now say so. If he replies with his method, that resolves the
   largest remaining soft spot in finding 02 either way.
6. Nothing else. No press, no media, no amplification.

## A promotion rule, adopted 5 September

Nothing goes into the site's numbered findings on the day it is computed. New
results land in the changelog first and move up only after surviving a night
and one out-of-sample check. Findings 04 and 05 were promoted the same day they
were produced; finding 03 was promoted and then withdrawn. The retraction rate
is not the problem — every withdrawal here is attached to a named mechanism,
which is what makes them read as diligence rather than churn — but the
*promotion* rate is, because a reader doing the obvious arithmetic assumes the
current findings have the same half-life.

## Still open scientifically (none of it blocks publication)

- Composition (wetness, ice fraction) unresolved by our observables
- The modelled deposit sits at km 0–36; stereo measurement puts it at 40–43
- Galchhi stage rise fails out-of-sample (3.6 m modelled vs ~9 observed);
  lower-reach channel widths are a rule of thumb, not measurements
- The Devghat peak passes on a factor-of-2 criterion, but all 26 survivors land
  below the observation — a one-sided residual, not a clean pass
- **The border speed the size envelope scores against (48.5 ± 35% m/s) is
  contradicted by the CAS peer-reviewed value of 19 m/s.** Re-scoring is the
  most consequential outstanding modelling task: it is an input to finding 04
- Seti 2012 needs a full rebuild — spec in `hindcast/seti/RESULTS.md`
- Nepali translation withdrawn pending a native speaker
