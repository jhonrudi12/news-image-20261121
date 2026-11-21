# The World Today — 21 November 2026

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/jhonrudi12/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/jhonrudi12/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

A newspaper-style front page that sums up the world news of **Saturday 21 November 2026** in one image, built for the [make.fun bounty "Sum up 21 November's world news in one image"](https://make.fun/bounty/news-image-20261121).

## The day in six stories

1. **Russian missiles land in Poland** — two missiles and a suspected drone came down in Poland on Friday during a huge Russian attack on Ukraine; PM Tusk calls it an intentional provocation, NATO chief Rutte a grave violation. Eight killed in Ukraine.
2. **Houthi missiles at Riyadh stopped** — Saudi defences shot down three ballistic missiles fired at Riyadh early on Saturday, the second attack on the capital in days after its tallest tower was hit on Thursday.
3. **Wall St sinks into correction** — the S&P 500 fell 3.7% on Friday and the Nasdaq 5.3%, wiping out the year's gains as AI shares crashed; Nvidia plunged 14%, Anthropic slid 9% a day after its record IPO.
4. **UK and EU seal post-Brexit reset** — deals on food trade, youth mobility for 100,000 young people a year and linking carbon markets; PM Burnham called it a win-win worth billions.
5. **COP31 talks run into overtime** — climate talks in Antalya missed their Friday deadline with no deal; the latest draft drops any mention of fossil fuels and a $120bn adaptation target, a new text due Saturday.
6. **World Court: Myanmar committed genocide** — the ICJ ruled Myanmar's forces committed state-sponsored genocide against the Rohingya, the first time the court has held a state responsible; Myanmar called the ruling unfair.

Plus: sources AP, Reuters, Wall Street Journal, Al Jazeera, NPR (early edition, stories reported by 09:00 WIB, 21 Nov 2026).

## How it works

`main.py` is a pure Python 3.13 standard-library program: it draws the whole front page — masthead, headlines, summaries and icons — with an embedded 5x7 bitmap font and simple shapes, and writes a deterministic 1024×1024 PNG to `/output/entry.png`. No network, no fonts, no image libraries, so two runs produce identical bytes.

## Run it

```bash
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, under 1 MiB)
```

## License

MIT — see [LICENSE](LICENSE).
