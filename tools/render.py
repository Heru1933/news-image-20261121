#!/usr/bin/env python3
"""Render the 21 November 2026 world-news front page (1024x1024).

Draws a one-page newspaper from the researched brief: masthead, lead story
(Poland / NATO) with a generated editorial illustration, six secondary
stories in two columns, and an "In brief" strip at the bottom. All text is
drawn by this script with PIL; no timestamps or randomness are used, so the
output is deterministic.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (247, 243, 234)
INK = (26, 26, 26)
MUTED = (90, 86, 78)
ACCENT = (163, 30, 34)
RULE = (26, 26, 26)
HAIRLINE = (150, 144, 130)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF = os.path.join(FONT_DIR, "noto", "NotoSerif-Regular.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "noto", "NotoSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "noto", "NotoSerif-Italic.ttf")
SANS = os.path.join(FONT_DIR, "noto", "NotoSans-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "noto", "NotoSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x, y, width, weight=2, fill=RULE):
    draw.rectangle([x, y, x + width, y + weight - 1], fill=fill)
    return y + weight


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    y = 24

    # ---- Masthead ----
    mast = font(SERIF_BOLD, 78)
    draw.text((W // 2, y), "THE WORLD", font=mast, fill=INK, anchor="ma")
    y += 86
    rule(draw, MARGIN, y, CONTENT_W, 4)
    y += 10
    date_f = font(SANS_BOLD, 21)
    dateline = "SATURDAY 21 NOVEMBER 2026"
    draw.text((W // 2, y), dateline, font=date_f, fill=ACCENT, anchor="ma")
    y += 28
    rule(draw, MARGIN, y, CONTENT_W, 1, HAIRLINE)
    y += 10

    # ---- Lead story ----
    kicker_f = font(SANS_BOLD, 17)
    draw.text((MARGIN, y), "LEAD  •  POLAND  •  NATO", font=kicker_f, fill=ACCENT)
    y += 22

    head_f = font(SERIF_BOLD, 40)
    headline = "Russian missiles land in Poland as NATO jets scramble"
    lines = wrap(draw, headline, head_f, CONTENT_W)
    y = draw_lines(draw, lines, MARGIN, y, head_f, INK, 45)
    y += 6

    # Hero image: crop the wide illustration to the page's band, keeping the
    # jets, the dawn band and the horizon; then scale to full content width.
    hero = Image.open(os.path.join(here, "hero.png")).convert("RGB")
    hw, hh = hero.size
    target_h = 200
    crop_h = int(hw * target_h / CONTENT_W)
    crop_y = 30
    hero = hero.crop((0, crop_y, hw, crop_y + crop_h))
    hero = hero.resize((CONTENT_W, target_h), Image.LANCZOS)
    page.paste(hero, (MARGIN, y))
    draw.rectangle([MARGIN, y, MARGIN + CONTENT_W, y + target_h],
                   outline=INK, width=1)
    y += target_h + 6

    cap_f = font(SERIF_ITALIC, 16)
    caption = ("Dawn over south-eastern Poland as Polish F-16s scrambled after "
               "Russian missiles crossed the border. Illustration.")
    cap_lines = wrap(draw, caption, cap_f, CONTENT_W)
    y = draw_lines(draw, cap_lines, MARGIN, y, cap_f, MUTED, 19)
    y += 4

    deck_f = font(SERIF, 20)
    deck = ("Two missiles and a drone came down in the south-east during one "
            "of Russia's largest air attacks on Ukraine. No injuries in "
            "Poland; Warsaw calls it an \u201cintentional provocation\u201d and "
            "NATO chief Mark Rutte, visiting Warsaw today, called it a "
            "\u201cgrave violation\u201d.")
    deck_lines = wrap(draw, deck, deck_f, CONTENT_W)
    y = draw_lines(draw, deck_lines, MARGIN, y, deck_f, INK, 25)
    y += 8
    rule(draw, MARGIN, y, CONTENT_W, 2)
    y += 8

    # ---- Secondary stories, two columns, three rows ----
    col_w = (CONTENT_W - 28) // 2
    stories = [
        ("MARKETS", "Wall Street slides into correction",
         "US stocks fell about 3.7% on Friday as AI and chip shares sold "
         "off; the S&P 500 and Dow entered correction territory."),
        ("CLIMATE  •  COP31", "COP31 in overtime, fossil fuels gone",
         "Talks in Antalya ran into overtime with no mention of fossil "
         "fuels in the draft deal; Panama vowed to object."),
        ("DIPLOMACY", "Britain and EU sign reset deals",
         "Brussels agreements on food trade, carbon markets and youth "
         "mobility rebuild post-Brexit ties."),
        ("SUMMIT FALLOUT", "Trump\u2013Xi\u2013Putin summit ends thin",
         "The first three-way meeting in Shenzhen produced few concrete "
         "results; Trump is \u201cnot rushing\u201d a decision on Iran."),
        ("JUSTICE", "ICJ: Myanmar committed genocide",
         "The court ruled Myanmar's forces committed state-sponsored "
         "genocide against the Rohingya in the 2017 crackdown."),
        ("WEATHER", "Cyclone Akvan hits India's east coast",
         "The storm crossed the Odisha and north Andhra Pradesh coast near "
         "Gopalpur; about 300,000 people were evacuated."),
    ]
    kick_f = font(SANS_BOLD, 14)
    s_head_f = font(SERIF_BOLD, 22)
    s_deck_f = font(SERIF, 16)

    row_tops = []
    for row in range(3):
        row_tops.append(y)
        row_bottom = y
        for col in range(2):
            idx = row * 2 + col
            kick, head, deck_text = stories[idx]
            x = MARGIN + col * (col_w + 28)
            yy = y
            draw.text((x, yy), kick, font=kick_f, fill=ACCENT)
            yy += 19
            h_lines = wrap(draw, head, s_head_f, col_w)
            yy = draw_lines(draw, h_lines, x, yy, s_head_f, INK, 26)
            d_lines = wrap(draw, deck_text, s_deck_f, col_w)
            yy = draw_lines(draw, d_lines, x, yy, s_deck_f, INK, 21)
            row_bottom = max(row_bottom, yy)
        y = row_bottom + 8
        if row < 2:
            rule(draw, MARGIN, y, CONTENT_W, 1, HAIRLINE)
            y += 8

    # ---- In brief strip ----
    rule(draw, MARGIN, y, CONTENT_W, 2)
    y += 8
    brief_f = font(SANS_BOLD, 15)
    draw.text((MARGIN, y), "IN BRIEF", font=brief_f, fill=ACCENT)
    y += 20
    brief_items = [
        "Pancreatic-cancer pill hailed as a breakthrough.",
        "Trump pardons baseball star Pete Rose posthumously.",
        "Estonia shuts all border crossings with Russia.",
        "Indonesia's fires: losses could reach $30bn.",
    ]
    item_f = font(SERIF, 16)
    half = CONTENT_W // 2
    for i, item in enumerate(brief_items):
        x = MARGIN + (i % 2) * half
        yy = y + (i // 2) * 22
        draw.text((x, yy), "\u2022  " + item, font=item_f, fill=INK)
    y += 48
    rule(draw, MARGIN, y, CONTENT_W, 1, HAIRLINE)
    y += 6
    sport_f = font(SERIF_ITALIC, 16)
    sport = ("Sport: India 159/1 at stumps on day 2 in Wellington \u2014 "
             "Jaiswal and Rahul share a century opening stand.")
    draw.text((MARGIN, y), sport, font=sport_f, fill=MUTED)
    print("final text baseline y:", y)

    out = os.path.join(os.path.dirname(here), "entry.png")
    page.save(out, format="PNG", optimize=True)
    print("wrote", out, page.size)


if __name__ == "__main__":
    main()
