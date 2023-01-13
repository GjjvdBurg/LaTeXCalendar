#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create pretty LaTeX calendars in A3 or A4 format

Author: Gertjan van den Burg <gertjanvandenburg@gmail.com>
Date: 2022-02-09
License: See LICENSE file.

"""

import argparse
import datetime as dt
import calendar
import json

from typing import Dict

from pathlib import Path

from dateutil.easter import easter

WEEKDAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_file", help="Output .tex file to write to")
    parser.add_argument(
        "--year",
        help="Year to generate calendar for, defaults to current",
        type=int,
    )
    parser.add_argument(
        "--mode",
        help="Calendar type to generate",
        choices=["a3-year", "a4-first-half", "a4-second-half"],
        default="a3-year",
    )
    parser.add_argument(
        "--holidays",
        help=(
            "Optional JSON file with holidays (ISO-8601 to label map). If "
            "omitted, uses UK government API for England & Wales."
        ),
        type=Path,
    )
    return parser.parse_args()


def make_table(year: int, month_range: type, holidays: Dict[dt.date, str]):
    header = [f"{{\\large \\bfseries {MONTHS[i - 1]}}}" for i in month_range]
    table = []
    clrA = lambda c: f"\\cellcolor{{ColorA}}{{{c}}}"
    clrB = lambda c: f"\\cellcolor{{ColorB}}{{{c}}}"
    bft = lambda t: f"\\textbf{{{t}}}"

    for i in range(31):
        row = []
        for month in month_range:
            month_start, month_days = calendar.monthrange(year, month)
            if i + 1 > month_days:
                row.append("")
                continue

            thedate = dt.date(year, month, i + 1)

            daynum = calendar.weekday(year, month, i + 1)
            day = WEEKDAYS[daynum]
            daystr = f"{i+1:02d} {day}"

            if daynum == 5:
                cell = clrA(bft(daystr))
            elif daynum == 6 or thedate in holidays:
                cell = clrB(bft(daystr))
            else:
                cell = daystr

            if thedate in holidays:
                cell += f" {{\\tiny {holidays[thedate]} }}"
            row.append(cell)
        table.append(row)
    return header, table


def build_tex(year: int, holidays: Dict[dt.date, str], mode="a3-year"):
    settings = {
        "a3-year": {
            "papersize": "a3paper",
            "orientation": "",
            "arraystretch": "1.35",
            "top": "20mm",
            "headsep": "0mm",
            "headheight": "15mm",
            "headlength": "20mm",
            "headfont": "{40}{50}",
        },
        "a4-first-half": {
            "papersize": "a4paper",
            "orientation": "landscape",
            "arraystretch": "1.3",
            "top": "10mm",
            "headsep": "2mm",
            "headheight": "10mm",
            "headlength": "20mm",
            "headfont": "{30}{40}",
        },
    }
    settings["a4-second-half"] = settings["a4-first-half"]
    stretch = settings[mode]["arraystretch"]

    docopts = ["10pt"]
    if settings[mode]["orientation"]:
        docopts.append(settings[mode]["orientation"])
    docopts = ", ".join(docopts)

    geom_opts = ", ".join(
        [
            f"headheight={settings[mode]['headheight']}",
            f"headsep={settings[mode]['headsep']}",
            "margin=12mm",
            f"top={settings[mode]['top']}",
            "nofoot",
            f"paper={settings[mode]['papersize']}",
        ]
    )

    preamble = [
        f"\\documentclass[{docopts}]{{article}}",
        "\\usepackage[utf8]{inputenc}",
        "\\usepackage[T1]{fontenc}",
        "\\usepackage{fancyhdr}",
        "\\usepackage{fix-cm}",
        "\\usepackage{tabularx}",
        "\\usepackage{xcolor}",
        "\\usepackage{colortbl}",
        "\\usepackage{DejaVuSansMono}",
        f"\\usepackage[{geom_opts}]{{geometry}}",
        "\\renewcommand*\\familydefault{\\ttdefault}",
        f"\\renewcommand*{{\\arraystretch}}{{{stretch}}}",
        "\\definecolor{ColorA}{HTML}{dddddd}",
        "\\definecolor{ColorB}{HTML}{bbbbbb}",
    ]

    headfont = settings[mode]["headfont"]
    header_footer = [
        "\\renewcommand{\\headrulewidth}{0pt}",
        f"\\setlength{{\\headheight}}{{{settings[mode]['headlength']}}}",
        "\\setlength{\\footskip}{2mm}",
        "\\chead{%",
        f"\t\\fontsize{headfont}\\selectfont\\textbf{{Calendar {year}}}\\hfill",
        "}",
        "\\cfoot{}",
    ]

    center = lambda c: f"{{\\hfill {c} \\hfill \\hfill }}"
    fmt_hdr = lambda h: " & ".join(map(center, h)) + " \\\\"
    join_row = lambda r: " & ".join(r)
    join_tab = lambda t: " \\\\ \n\\hline\n".join(map(join_row, t))
    fmt_tab = lambda t: f"{join_tab(t)} \\\\ \n"
    tex_tab = lambda h, t: [
        "\\begin{tabularx}{\\textwidth}{|X|X|X|X|X|X|}",
        "\\hline",
        fmt_hdr(h),
        "\\hline",
        fmt_tab(t),
        "\\hline",
        "\\end{tabularx}",
    ]

    doc_pre = [
        "\\begin{document}",
        "\\pagestyle{fancy}",
        "\\begin{center}",
    ]
    doc_post = [
        "\\end{center}",
        "\\end{document}",
    ]

    if mode == "a3-year":
        header_1, table_1 = make_table(year, range(1, 7), holidays)
        header_2, table_2 = make_table(year, range(7, 13), holidays)
        doc_tab = (
            tex_tab(header_1, table_1)
            + ["\\vskip\\baselineskip"]
            + tex_tab(header_2, table_2)
        )
    elif mode == "a4-first-half":
        header, table = make_table(year, range(1, 7), holidays)
        doc_tab = tex_tab(header, table)
    elif mode == "a4-second-half":
        header, table = make_table(year, range(7, 13), holidays)
        doc_tab = tex_tab(header, table)

    doc = doc_pre + doc_tab + doc_post
    tex = preamble + header_footer + doc
    return tex


def load_holidays_from_file(filename: Path) -> Dict[dt.date, str]:
    with open(filename, "r", encoding="utf-8") as fp:
        contents = json.load(fp)
    out = {dt.date.fromisoformat(k): v for k, v in contents.items()}
    return out


def get_ew_bank_holidays(year: int) -> Dict[dt.date, str]:
    from govuk_bank_holidays.bank_holidays import BankHolidays

    bh = BankHolidays()
    holidays = bh.get_holidays(
        division=BankHolidays.ENGLAND_AND_WALES, year=year
    )
    out = {
        d["date"]: f"{d['title']}"
        if not d["notes"]
        else f"{d['title']} ({d['notes']})"
        for d in holidays
    }
    out = {k: v.replace("’", "'") for k, v in out.items()}
    for key, value in out.items():
        value = value.replace("(Substitute day)", "(sub)")
        if value == "Platinum Jubilee bank holiday":
            value = "Platinum Jubilee"
        out[key] = value

    out[easter(year)] = "Easter Sunday"
    out[dt.date(year, 12, 25)] = "Christmas Day"
    out[dt.date(year, 12, 26)] = "Boxing Day"
    return out


def main():
    args = parse_args()

    year = args.year or dt.date.today().year
    if args.holidays is not None:
        holidays = load_holidays_from_file(args.holidays)
    else:
        holidays = get_ew_bank_holidays(year)
    tex = build_tex(year, holidays=holidays, mode=args.mode)

    with open(args.output_file, "w") as fp:
        fp.write("\n".join(tex))


if __name__ == "__main__":
    main()
