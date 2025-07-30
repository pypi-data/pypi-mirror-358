# gleaner

A simple web scraper that finds all the pages on a domain using breadth-first search.

## Installation

```bash
pipx install gleaner
```

## Usage

```bash
glean https://example.com -o output.txt
```

This will

- Start at given URL
- Search through HTML to find pages on the same domain
- Follow those links and repeat the process
- Save all discovered URLs to output.txt

## Options

For more help on options

```bash
glean --help
```

- `-o, --output` - Output file (default: `urls.txt`)
- `-r, --rps` - Maximum requests per second (default: 10)
- `-v, --verbose` - Enable verbose output

## Limitations

- Rate limiter only works for rps >= 1
- Only follows `<a>`-tag links
- Doesn't read `robots.txt`
- No user-agent header
- Doesn't handle 429 errors (too many requests)
- Doesn't parse sitemap.xml
- No export formats beyond `.txt` (json? csv?)
- Only works for entire domains. You can't glean an individual page and all sub-pages
- Doesn't store progress for larger sites where scraping might last more than a few minutes
- No concurrent processing
