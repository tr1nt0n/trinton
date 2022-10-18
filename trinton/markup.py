import abjad
import baca
import evans
import trinton
from abjadext import rmakers
from fractions import Fraction
import quicktions
import numpy
import datetime
import dataclasses
import typing
import pathlib
import os


def write_markup(voice, leaf, string, down):
    if down == True:
        markup = abjad.Markup(string, direction=abjad.Down)
        trinton.attach(voice, leaf, markup)
    else:
        markup = abjad.Markup(string, direction=abjad.Up)
        trinton.attach(voice, leaf, markup)


def write_startmarkups(score, voices, markups):
    for voice, markup in zip(voices, markups):
        start_markup = abjad.InstrumentName(markup=markup)

        trinton.attach(
            voice=score[voice],
            leaves=[0],
            attachment=start_markup,
        )


def write_marginmarkups(score, voices, markups):
    for voice, markup in zip(voices, markups):
        margin_markup = abjad.ShortInstrumentName(markup=markup)

        trinton.attach(
            voice=score[voice],
            leaves=[0],
            attachment=margin_markup,
        )
