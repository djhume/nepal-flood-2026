# The gift note — DRAFT, NOT YET SENT

Dave's decision (3 Sept 2026): release the work to the people who can use it,
**without taking on any ongoing involvement** — no co-authorship, no
correspondence obligation, no preprint commitment. The note below is written to
make that explicit so recipients don't feel they owe a reply, and so Dave
doesn't acquire a workload by accident.

**Send only when the release checklist at the bottom is clear.**

---

## The note (same body for everyone; swap the first line)

> Subject: Langtang–Trishuli flood — a water-budget analysis, yours to use
>
> [OPENING LINE — pick one:]
> — *Prince:* I watched your analysis of the Nepal debris flow and it reaches,
>   from geomorphology, the conclusion I'd been testing with a routing model.
> — *Willsey:* Your interview with Jeff Kargel is what set me off on this;
>   thank you for it.
> — *ICIMOD:* I've done some independent modelling of the 26 August event that
>   may be useful to your assessment work.
> — *Kargel:* Your interview with Shawn Willsey on the Langtang event is what
>   set me off testing the water budget with a model.
>
> Over the past week I built a physics model to test one question about the
> 26 August Langtang Lirung collapse: where the flood water actually came
> from. The short answer is that frictional melt is energy-limited to a few
> million cubic metres against roughly twenty million of officially estimated
> "excess" water, so the flood was mostly the monsoon Trishuli itself, swept
> up and delivered at once. Two things fell out that may be more useful: the
> 08:44 border camera clock appears to discriminate what the fallen mass was
> *made of* rather than how big it was, and the erosion the model predicts for
> the corridor (3.8 Mm3, no fitted constants) matches what stereo satellite
> imagery measured (3.2 Mm3) — while implying the corridor cannot have received
> anything like the rock volume the largest source estimates suggest.
>
> Everything is here, including what it gets wrong:
> https://claude.ai/code/artifact/50fbb9c4-1dd2-43f6-a8c1-dbbf80e9d197
> Code and data: [REPO URL]
>
> **This is yours to use however is helpful — modify it, take the ideas,
> publish anything you find useful, no credit needed. I'm not looking to
> co-author or to be involved further, and no reply is expected.** I'm an
> engineer in New Zealand who did this on evenings; the people who can act on
> it are you, not me.
>
> One caveat I'd want any user to see: the model currently has no sediment
> entrainment term, so it carries too little sediment downstream. It is
> preliminary and not peer-reviewed, and should not underpin an operational
> warning decision without independent validation.
>
> — Dave Hume

## Recipients (short list — four is plenty, two would do)

| Who | Why them | Note |
|---|---|---|
| **Philip Prince**, Virginia Tech Geosciences | Has publicly reached the qualitative version of the same result; most likely to actually read it | Also shares a department with Shirzaei, whose InSAR precursory-creep finding conflicts with geopera's — worth mentioning as an open question if a conversation happens |
| **Shawn Willsey** | This project began with his Kargel interview; large audience of exactly the right kind | |
| **ICIMOD** (Kathmandu) | Regional mandate, running the coordination hub for this event, warning systems are their remit — the natural institutional home | The likeliest route to the work being *used* rather than just read |
| **Jeff Kargel** / PSI | His rapid assessment of this event is unpublished, and his public framing of the water sources is the one this work quantifies | Our Seti 2012 hindcast was withdrawn (bad channel profile) — do NOT claim it corroborates his Seti conclusion |

Deliberately **not** on the list for a first send: journals, media, DHM. DHM
gets the separate, specific data request in `dhm-data-request.md` — a different
kind of ask, and it should not be bundled with a gift.

## Release checklist — clear these before sending

- [x] **Entrainment term built** (3 Sept night, `model/ENTRAINMENT.md`) — but
      it opened two new items below
- [x] **Seti withdrawal propagated** — hub + technical report republished
      4 Sept; README, PLAN and this note done. Plain pages still to check.
- [ ] Decide how to state the event-size contradiction (entrainment ledger says
      the release delivered <=3-5 Mm3 of solids; our routing wants 30-60 Mm3
      through the border) — it is the sharpest open question and the note
      should not oversell past it
- [ ] Plain-English and technical pages updated with the entrainment result and
      the corrected (retracted) geopera deposition figures
- [x] Nepali page — WITHDRAWN 5 Sept rather than shipped unreviewed. The
      artifact now carries a bilingual notice explaining why and inviting any
      Nepali speaker to translate the openly-licensed material themselves.
- [ ] Prince video title + publication date recorded for the source table
- [ ] Repo pushed public; `[REPO URL]` filled in above
- [ ] `data/198_discharge.csv` redistribution terms verified with DHM, and a
      decision made on linking vs redistributing `data/ffd_report.pdf`
- [ ] Read the whole thing once more as a stranger would

## After sending

Nothing. That is the point. No follow-ups, no checking for replies, no
metrics. If someone writes back and Dave wants to engage, that is a free
choice made later — not an obligation created now.
