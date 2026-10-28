# SAIV 2027 website

Source of <https://www.aiverification.org/2027/>, the website of the 10th International Symposium on AI Verification (SAIV 2027), London, UK, October 31 – November 5, 2027.

The site is built by GitHub Pages (classic build from `main`, `/`) with the [jekyll-theme-conference](https://github.com/DigitaleGesellschaft/jekyll-theme-conference) theme, in the same style as the [2026](https://github.com/SAIV-conference/2026), [2025](https://github.com/SAIV-conference/2025), and [2024](https://github.com/SAIV-conference/2024) editions. Local modifications to the theme are listed in [CHANGELOG.md](CHANGELOG.md). The root site <https://www.aiverification.org/> ([saiv-conference.github.io](https://github.com/SAIV-conference/saiv-conference.github.io)) redirects to the first entry of its `editions.json`, which also feeds the *Editions* menu of every edition.

## Pages

| Page | Source |
|---|---|
| Home | `index.md` (dates and info bar in `_config.yml`) |
| About | `about/index.md` |
| SAIV Week | `week/index.md` |
| Call for Papers | `call/index.md` |
| Committees | `committees/index.md`, rendered from the people datastore |
| Venue | `venue/index.md` |

## People datastore

Everyone shown on the site is stored once, in `_data/people.yml`; committee membership is stored separately in `_data/committees.yml`. Pages render committees with `{% include partials/committee.html id="<group id>" %}`, so the same record can appear in several committees and new groups (e.g. the program committee) need no new markup.

A person record holds only public professional information:

```yaml
- id: taylor-t-johnson            # kebab-case, unique
  name: Taylor T. Johnson          # as the person writes it, with diacritics
  sort_name: Johnson, Taylor       # ASCII "Family, Given", used for alphabetical order
  affiliation: Vanderbilt University
  country: USA
  website: https://www.taylortjohnson.com/
  orcid: https://orcid.org/0000-0001-8021-9923
  google_scholar: https://scholar.google.com/citations?user=MdTkXNYAAAAJ
  dblp: null                       # use null when unknown or unverified
  photo: taylor-t-johnson.webp     # in assets/images/people/, or null for initials
  photo_source: https://www.taylortjohnson.com/
  checked_on: 2026-10-28
```

Rules:

- **Public data only.** This repository is public. Do not add email addresses, phone numbers, notes, or people who have not agreed to serve (e.g. candidate or invitation lists); keep those in a private planning repository.
- **Verified identifiers only.** Add an ORCID, Google Scholar, or dblp link only if it is linked from the person's own homepage or the identifier's record clearly matches them; otherwise use `null`. A wrong link is worse than none.
- **Photos** come from the person's own or institutional page, recorded in `photo_source`. Normalize them with `python3 scripts/normalize_photo.py <id> <downloaded-image>` (320×320 WebP, ≤ 64 KB).
- Groups with `order: alphabetical` must follow `sort_name`.

### Adding a person to a committee

1. Add (or update) the record in `_data/people.yml`.
2. Optionally add a photo with `scripts/normalize_photo.py`.
3. Add `- person: <id>` to the group in `_data/committees.yml` (optionally with `role: Chair`).
4. Run `python3 scripts/validate_data.py`.

The schemas are in `schemas/`; `scripts/validate_data.py` also checks cross-references, ordering, and photo files. CI runs it and a full Jekyll build on every push and pull request.

## Building locally

Requires Ruby with Bundler, or Docker:

```bash
pip install -r requirements.txt && python3 scripts/validate_data.py
bundle install && bundle exec jekyll serve          # http://localhost:4000/2027/
# or, without a local Ruby toolchain:
docker run --rm -it -p 4000:4000 -v "$PWD":/site -w /site ruby:3.2 \
  bash -c 'bundle install && bundle exec jekyll serve -H 0.0.0.0'
```

The *Editions* menu loads `/editions.json` from the root site, so it stays empty in local previews.
