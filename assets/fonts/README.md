# Brand fonts

Static TrueType weights of the Northern Mile Media brand faces, fetched by
`scripts/fetch_brand_fonts.py`.

| Family | Role | Weights |
|--------|------|---------|
| Space Grotesk | Display, headings | 400, 500, 600, 700 |
| Inter | Body, labels | 400, 500, 600, 700 |
| IBM Plex Mono | Numerals, data | 400, 500, 600 |

## Why static cuts rather than variable fonts

Variable fonts resolve to their default instance in matplotlib, which renders
everything at weight 300. Charts came out visibly thin and amateurish. The
static per-weight files let the renderer actually select 400/500/600/700.

Note that Google Fonts ships IBM Plex Mono's non-regular weights under
*separate family names* ("IBM Plex Mono Medium", "IBM Plex Mono SemiBold").
Requesting weight 600 from the base family silently falls back to 400, so
`blog_visuals.data_font()` maps weights to the correct family name.

## Licensing

All three families are licensed under the SIL Open Font License 1.1, which
permits bundling and redistribution. They are also already loaded from Google
Fonts by the dashboard itself.
