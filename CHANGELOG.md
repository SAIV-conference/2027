- _includes/partials/header.html:
# add favicon on all pages
  <link rel="shortcut icon" type="image/x-icon" href="{{ 'favicon.png' | relative_url }}">

- ‎_sass/conference.scss‎:
# default color
$primary:                      #074 !default;
→
$primary:                      #008080ff !default;
# column width
    // Width of columns with content (default)
    width: 635px;

- ‎_layouts/home.html‎:
# (reduce padding -- reverted)
  <div class="jumbotron">
    <h1 class="display-3 text-break">
→
  <div class="jumbotron">
    <h1 class="text-break">

- SAIV 2027 additions:
  - `_sass/saiv.scss` (imported last in `assets/css/main.scss`): Font Awesome brand icons, committee person cards, and the "SAIV Week" event blocks.
  - `_includes/partials/committee.html` and `_includes/partials/person_card.html`: render committees from `_data/committees.yml` and `_data/people.yml` (see README).
