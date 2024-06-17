# dreambank

Download [DreamBank](https://dreambank.net) datasets directly from Python.

If you use any of these datasets for publication, cite the original DreamBank dataset reference:

> Domhoff, G. W., & Schneider, A. (2008). Studying dream content using the archive and search engine on DreamBank.net. _Consciousness and Cognition_, 17(4), 1238-1247. doi:[10.1016/j.concog.2008.06.010](https://doi.org/10.1016/j.concog.2008.06.010)


Similar projects that I browsed while developing this code:

* [mattbierner/DreamScrape](https://github.com/mattbierner/DreamScrape)
* [josauder/dreambank_visualized](https://github.com/josauder/dreambank_visualized)
* [MigBap/dreambank](https://github.com/MigBap/dreambank)
* [jjcordes/Dreambank](https://github.com/jjcordes/Dreambank)

Goes beyond other projects by
1. More careful extraction of metadata from dream reports (e.g., gets dates from individual dream reports when present).
2. Grabs additional info about each dataset (including second level of detail if present).
3. Includes more (some are missing in other repos)


## Versioning

Uses semantic versioning, where major versions are when dataset changes (not expected much, if at all, maybe cleaning up or something) and minor changes are when code changes and does not impact dataset.
