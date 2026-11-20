# The World Today — 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/azkhabaskara/news-image-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/azkhabaskara/news-image-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

Entry for the [make.fun](https://make.fun/c/news-image-20261120)
competition **news-image-20261120**: sum up the world's news of
Friday 20 November 2026 in one image.

## What it is

`main.py` (pure Python 3.13 standard library, no network) draws a
newspaper front page — masthead dated **Friday, 20 November 2026** —
and writes it to `/output/entry.png` (1024×1024 PNG, ~22 KB):

- **Lead:** Trump, Xi and Putin meet in Shenzhen — first three-way
  summit; joint peace declaration, no deal on Ukraine or Iran.
- **Ukraine:** Russia's big overnight attack — 110+ missiles and
  ~400 drones; 8 dead, 28 hurt in Kyiv.
- **Justice:** Myanmar guilty of genocide — the world court rules for
  the Rohingya, a first of its kind; vote 9-6.
- **Markets:** Anthropic IPO closes at $97, up 17% on its $83 offer
  price; S&P and Nasdaq fall ~2%; Nikkei -4.8%; SoftBank -16%.
- **Middle East:** Houthi missile damages the Saudi PIF tower in
  Riyadh's financial district.
- **Also:** GTA 6 tops $2.3bn in sales, a launch record; Kenya sends
  its last Ebola patient home, 37 days after the first case.

The image is drawn in code with an embedded 5×7 bitmap font and a
hand-written PNG encoder, so two runs write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
