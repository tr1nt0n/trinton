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


def treat_tuplets(non_power_of_two=False):
    def treatment(selections):
        tuplets = abjad.select.tuplets(selections)
        rmakers.trivialize(tuplets)
        tuplets = abjad.select.tuplets(selections)
        rmakers.rewrite_rest_filled(tuplets)
        if non_power_of_two is False:
            tuplets = abjad.select.tuplets(selections)
            rmakers.rewrite_sustained(tuplets)
        tuplets = abjad.select.tuplets(selections)
        rmakers.extract_trivial(tuplets)
        tuplets = abjad.select.tuplets(selections)
        rmakers.rewrite_dots(tuplets)

    return treatment


def force_note(selector):
    def force(selections):
        selection = selector(selections)
        rmakers.force_note(selection)

    return force


def force_rest(selector):
    def force(selections):
        selection = selector(selections)
        rmakers.force_rest(selection)

    return force


def beam_groups(beam_rests):
    def beam(selections):
        rmakers.beam_groups([selections], beam_rests=beam_rests)

    return beam
