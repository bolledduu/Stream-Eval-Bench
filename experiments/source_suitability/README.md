# Suitability audit of the three prototype sources

All three original MP4s were downloaded from their pinned URLs and matched their recorded SHA-256 hashes. Seven contact-sheet pages covering 266 samples at one frame per second were visually reviewed by the assistant. This is a source-screening audit, not frame-by-frame independent human annotation. Audio was not analyzed. Very brief events or small printed details can be missed.

| Source | Observed material in sampled review | Status for original hypothesis |
|---|---|---|
| Camera, 68.1 s | Lens removal/reseating, cap handling, controls, battery/card handling; terminal transition near the end | Existing lens/cap case measures component/state recognition. No validated initially-hidden fact plus later evidence tied to the same earlier event has been annotated. |
| Printer, 76.1 s | Display illumination and darkening, paper handling, tray opening/loading | Existing display case measures state changes. Paper reverse-side visibility is a possible annotation candidate, but sheet identity and earlier uncertainty are unverified; no scored label assigned. |
| Table, 121.8 s | Tray/frame handling, fasteners, assembly and final tray placement | Existing tray case measures before/after states and controlled delayed delivery. It does not by itself establish retrospective event association. |

**Admission result: zero currently verified cases for the full original-event-revelation hypothesis.** This does not mean these sources contain no usable event, or the datasets lack useful data. It means the present cases are not annotated and validated for that hypothesis. Eligibility is a property of a defined question and evidence pair, not merely of a dataset name.

An eligible case needs: (1) a defined earlier event, (2) evidence the relevant fact is initially unresolved, (3) later footage resolving that same event's fact, (4) independently checkable event linkage, (5) an unrelated fact that should be preserved, and (6) an unambiguous scoring rule. Natural delayed reveals and constructed delivery interventions must be reported separately. A natural replay is not mandatory, but a later physical state alone does not establish an earlier hidden fact.

The six new endpoint recognition controls in ../format_controls/ diagnose the existing examples only. They do not satisfy the missing event-association annotations. Their expected labels were visually screened before model calls.

## Reproduce

Run `python experiments/source_suitability/audit_sources.py` with Pillow and ffmpeg available. Downloads are stored under ignored source_media/. Contact-sheet timestamps are approximate sampling-bin labels, not authoritative event timestamps. Consult source_audit.json for hashes and exact provenance.
