# Publishing checklist

Status: **public on GitHub, live on GitHub Pages at
https://djhume.github.io/nepal-flood-2026/ . No DOI. No preprint. No outreach
emails sent.**

## Cleared before the public push (5 Sept 2026)

- [x] No secrets, API keys or tokens anywhere in the tree or history
- [x] No email addresses or personal contact details in the prose or code — **but see the 8 September note below: this was not quite true of the data files**
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
- [x] **`outreach/gift-note.md` deleted** (Dave, 8 Sept). No outreach is
      happening, so the note had no purpose, and it named four people who did
      not ask to be named. **The git history is deliberately NOT being
      rewritten — see the decision below.**
      **Still in `outreach/`: `dhm-data-request.md`, a data request to DHM,
      and `warning-concept-note.md`. Both are asks under the 8 September rule
      and neither was sent. Decide.**
- [x] **No Nepali scientist has read this.** It remains the largest gap in the
      work. The site states it as a limitation of the analysis rather than as
      a request, which is where it now stays.

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
5. **Nothing else. No emails, no press, no media, no amplification, and no
   requests of anybody.**

## The no-outreach rule, adopted 8 September

Dave: *"I do not want to tell anyone anything or ask anything of anyone
either."* Adopted, and it is stronger than the earlier "no press" line —
it removes the asks as well as the amplification.

What this means in practice, and what was changed on the site to comply:

1. **No requests for data.** The landing page's "What would help most" and the
   plain page's equivalent were lists of things we wanted from DHM, from the
   hydropower operators, and from whoever might fly a survey. They are now
   "What is missing from this analysis" — the same facts, stated as limits on
   what we can conclude, explicitly not a request.
2. **No recommendations to anyone.** Gone: "Warning systems should know that";
   the prescription of seismic tripwires, tunnel egress alarms and fail-safe
   intake gates to the hydropower industry; "recovering those records would do
   more … than any instrument that could be deployed now"; and the framing of
   the detection gap as "a much cheaper gap to close than new monitoring
   hardware". Where the physics implies something about timescales, the page
   now states the timescale and stops.
3. **No instructions about other people's numbers.** "We would ask anyone
   quoting it to go back to the release" is gone (8 Sept, earlier commit).
4. **No asking for a reviewer.** The absence of a Nepali reader stays on the
   page as a limitation of the work, not as an appeal.
5. **What stays.** The licence, which grants rather than asks; the fact that
   the issue tracker exists, stated without inviting anyone to use it; and
   every retraction. Publishing the work and making no claim on anyone else's
   attention are not in conflict.

The four emails (ICIMOD, Kargel, Petley, Willsey) are cancelled. The note that
went with them — that the site used to describe Kargel's 6 min 50 s as
independent confirmation of our clock, and no longer does because his stated
basis is "22 km at 193 km/h" with no method — is a correction we made to our
own page and stands on its own; it needed no email.

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

## The git history stays as it is — decided 8 September

Deleting `outreach/gift-note.md` from HEAD raised the obvious follow-up:
purge it from the history too, since a public repo still carries it in every
clone. It was scoped and prepared — `git filter-repo` is installed, the repo
has 0 stars, 0 forks, 0 watchers and 0 issues so deleting and recreating it on
GitHub would have cost nothing, and a full pre-rewrite bundle was taken and
verified (`~/personal/nepal-flood-2026-backup/nepal-flood-PREREWRITE.bundle`,
"records a complete history"). **We are not doing it.** Three reasons, in
order of weight.

1. **The content does not warrant it.** The note was read before deciding. It
   offers four people the work for free, explicitly asks nothing of them, and
   the recipient table's remarks about each are complimentary. There is nothing
   in it that could embarrass or misrepresent any of them. The privacy concern
   is real but thin, and deleting it from HEAD already stops the site and the
   repo presenting anyone as a target.

2. **The commit log is the thing this project trades on.** Two pages say so:
   "every retraction and the reasoning behind it is in the commit log; nothing
   rests on trusting either of us." Rewriting 86 commits — every hash changed,
   the GitHub repo deleted and recreated, a creation date later than the first
   commit — to chase a deleted draft is disproportionate, and it damages
   exactly the asset the work runs on.

3. **It would be inconsistent with the discipline.** The rule here is *do not
   tidy the record*: retractions stay visible, and the wrong first version of
   §26b sits above its own correction. A history rewrite to remove something
   mildly awkward is tidying the record. The inconsistency costs more than the
   tidiness is worth.

Also true and worth stating plainly: **a rewrite would reduce future exposure,
not past.** The repo has been public since 5 September.

**Revisit if** the project acquires a DOI, a preprint, or any real readership —
scrutiny of the history goes up and the calculus changes. The bundle makes the
rewrite easy to do later; it cannot be undone once done.

**One thing that WAS fixed, without a rewrite.** The checklist above claimed no
email addresses or contact details were in the tree. Checking the history for
this decision found two: `contact@geoclash.org`, an institutional address in a
source-table line about the CLaSH centre, which is published on their own site
and stays; and `hotelmilarepa@gmail.com`, a private business's address carried
in on an `email` tag that OSM had attached — plainly in error — to a stream in
`hindcast/seti/osm_rivers.json` (way 577718458, "Firke Khola"). That one had no
analytical purpose and is removed from the working tree. Not from the history,
for the reasons above.
