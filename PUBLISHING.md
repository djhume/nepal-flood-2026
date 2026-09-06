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

## The 6 September cold-read audit

A second stranger's read, this time of the published landing page, and it went
after the *dependencies* rather than the prose. Five things came out of it.

1. **The corrected clock never reached the code.** The 6 Sept commit updated
   the hero stats, the clocks table, §00, finding 02 and the plain-English page
   — every place a human reads 7 min 40 s — and did not touch a single model
   constant. `model/unified.py`, `model/snowplow.py`, `calcs/ensemble.py`,
   `calcs/front_speed_closure.py`, `calcs/analyse_border_speed.py` and
   `notebooks/build_workings.py` were all still scoring against **7.0 min**.
   The published 14–34 Mm³ envelope was therefore computed against a number the
   site had already retracted. Fixed in all six files and both ensembles rerun.
   The envelope barely moves — **13.3–34.0 Mm³, median 23.2**, from 21 of 200,
   against the published 14–34 and median 21 from 26 of 220. The smallness of
   that change is the reassuring part, not the interesting one.
   The general lesson is cheap and was learned expensively: a correction to a
   *published figure* is not done when the pages read right. Grep the code.
2. **The profile-integrity check was still a sentence.** `hindcast/seti/
   RESULTS.md` closed on 3 Sept with "a profile-integrity check now belongs in
   every path build". It did not exist. It does now — `model/check_profile.py`,
   four gates, non-zero exit. Seti-as-published fails all four; Trishuli and
   Chamoli pass; the *repaired* Seti channel still fails on a 972 m raw step,
   which is the argument for a rebuild rather than a patch.
3. **The first draft of that check reported the live Trishuli profile as
   FAILING**, at 52% flat, and it was wrong — it audited the clamped
   intermediate rather than the profile the model consumes after smoothing
   (1.4% flat, reach slopes within 10% of raw). Recorded here because the near
   miss is the point: a check reading the wrong pipeline stage would have
   retracted a sound finding. The lower-river staircase it found is real,
   though, and it is why Galchhi's failure now points at the **widths** — a
   hydraulic-geometry rule of thumb below km 60 — rather than the elevations.
4. **The CAS re-score was promised on three pages and never run.** It is now a
   named scenario, `TRISHULI_VBORDER=cas python calcs/ensemble.py`, and the
   answer is sharper than a moved envelope: **0 of 200 samples satisfy all five
   observables**, against 21 of 200 for the front scenario. The conflict is not
   about size — `border_min + v_border: 0 runs` across the whole 1–200 Mm³
   prior, and `syabru_min + v_border: 0 runs` too, while each constraint alone
   is met by 64 and 35 samples. Consistent with CAS measuring the post-turn
   water surface rather than the front; equally consistent with our
   speed-to-arrival physics being wrong. It does not choose between them and
   the page says so. Both scorings published.
5. **geopera was carrying more weight than "an independent analyst" admits.**
   Erosion figure, border superelevation, deposit location and the convergent
   settling-velocity result are all theirs, and "a completely different method"
   is true of the solver, not the inputs — shared imagery, shared literature,
   shared published estimates. Named on the page now.

## Still open scientifically (none of it blocks publication)

- Composition (wetness, ice fraction) unresolved by our observables
- The modelled deposit sits at km 0–36; stereo measurement puts it at 40–43
- Galchhi stage rise fails out-of-sample (3.6 m modelled vs ~9 observed);
  lower-reach channel widths are a rule of thumb, not measurements
- The Devghat peak passes on a factor-of-2 criterion, but all 26 survivors land
  below the observation — a one-sided residual, not a clean pass
- ~~**The border speed the size envelope scores against (48.5 ± 35% m/s) is
  contradicted by the CAS peer-reviewed value of 19 m/s.** Re-scoring is the
  most consequential outstanding modelling task~~ — **done 6 Sept**, both
  scenarios published side by side (`TRISHULI_VBORDER`). The reconciliation
  argument (CAS measures the post-turn water surface, not the front; 19 m/s
  would need a run-up coefficient α = 2.72, which is unphysical) is ours and
  unreviewed, while the number it sets aside is peer-reviewed, so the site now
  shows both envelopes rather than asserting the reconciliation
- **The up-valley wedge, from the routing side, and it points UP.** With the
  Kyirong arm modelled as a backwater wedge rather than a linear store, a 4×3
  sweep over release volume and wetness (`calcs/wedge_grid.py`) finds **no cell
  reproducing the Galchhi rise and the border clock together**. Nearest miss:
  60 Mm³ at w0 = 0.40 clears Galchhi at 10.6 m and arrives at the border
  **eight seconds** too early — under the superseded 7.0-minute clock it would
  have passed. Same direction as the up-valley volume route and the Hakubesi
  mud line from the 6 Sept (late) session: up. The ensemble has NOT been rerun
  with the wedge installed, and that is the next real job — the same one that
  session named (stage observables, a momentum-splitting junction node, the
  corrected clock)
- Seti 2012 needs a full rebuild — spec in `hindcast/seti/RESULTS.md`
- Nepali translation withdrawn pending a native speaker
