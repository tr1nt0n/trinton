\version "2.23.14"

% ekmelos markups

tremolo-largo = \markup {
    \hspace #0.6
    \fontsize #3.5
    \override #'(font-name . "ekmelos")
    \override #'(whiteout-style . "outline")
    \override #'(whiteout . 1)
    \override #'(layer . 20)
    {
        \char ##xe220
    }
}

tremolo-moderato = \markup {
    \hspace #0.6
    \fontsize #3.5
    \override #'(font-name . "ekmelos")
    \override #'(whiteout-style . "outline")
    \override #'(whiteout . 1)
    \override #'(layer . 20)
    {
        \char ##xe221
    }
}

tremolo-stretto = \markup {
    \hspace #0.6
    \fontsize #3.5
    \override #'(font-name . "ekmelos")
    \override #'(whiteout-style . "outline")
    \override #'(whiteout . 1)
    \override #'(layer . 20)
    {
        \char ##xe222
    }
}

tremolo-largo-large = \markup {
    \hspace #0.6
    \fontsize #8
    \override #'(font-name . "ekmelos")
    \override #'(whiteout-style . "outline")
    \override #'(whiteout . 1)
    \override #'(layer . 20)
    {
        \char ##xe220
    }
}

tremolo-moderato-large = \markup {
    \hspace #0.6
    \fontsize #8
    \override #'(font-name . "ekmelos")
    \override #'(whiteout-style . "outline")
    \override #'(whiteout . 1)
    \override #'(layer . 20)
    {
        \char ##xe221
    }
}

tremolo-stretto-large = \markup {
    \hspace #0.6
    \fontsize #8
    \override #'(font-name . "ekmelos")
    \override #'(whiteout-style . "outline")
    \override #'(whiteout . 1)
    \override #'(layer . 20)
    {
        \char ##xe222
    }
}

multiple-staccato = \markup {
    \hspace #0.6
    \fontsize #3.5
    \override #'(font-name . "ekmelos")
    \char ##xe5f2
}

multiple-staccato = \markup {
    \hspace #-0.1
    \fontsize #6
    \override #'(font-name . "ekmelos")
    \char ##xf42F
}

gridato-twist-bow = \markup {
    \hspace #0.5
    \fontsize #6
    \override #'(font-name . "ekmelos")
    \char ##xe80B
}

#(append! default-script-alist
   (list
    `(gridatotwistbow
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,gridato-twist-bow)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

twist-bow = #(make-articulation 'gridatotwistbow)

#(append! default-script-alist
   (list
    `(multiplestaccato
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,multiple-staccato)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

ricochet = #(make-articulation 'multiplestaccato)

% bowing articulations

au-talon-to-punta = \markup {
    \hspace #-0.5
    \override #'(font-name . "ekmelos")
    {
        \fontsize #8
        {
            \char ##xe610
        }
        \hspace #-0.77
        \raise #-1 \with-dimensions-from \null
        \fontsize #6
        {
            \char ##xeB62
        }
    }
}

#(append! default-script-alist
   (list
    `(talontopunta
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,au-talon-to-punta)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,UP)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

talon-to-punta = #(make-articulation 'talontopunta)

punta-to-au-talon = \markup {
    \hspace #-0.5
    \override #'(font-name . "ekmelos")
    {
        \fontsize #8
        {
            \char ##xe612
        }
        \hspace #-0.77
        \raise #1.41 \with-dimensions-from \null
        \fontsize #6
        {
            \char ##xeB62
        }
    }
}

#(append! default-script-alist
   (list
    `(puntatotalon
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,punta-to-au-talon)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,UP)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

punta-to-talon = #(make-articulation 'puntatotalon)

% woodwind articulations

woodwind-open = \markup {
    % \hspace #0.5
    \override #'(layer . 3)
    \override #'(whiteout . 1)
    \override #'(whiteout-style . #'outline)
    \fontsize #12
    \override #'(font-name . "ekmelos")
    {
        \char ##xe5F9
    }
}

#(append! default-script-alist
   (list
    `(woodwindopen
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,woodwind-open)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

wind-open = #(make-articulation 'woodwindopen)

woodwind-half-closed = \markup {
    % \hspace #0.5
    \fontsize #12
    \override #'(font-name . "ekmelos")
    \char ##xe5F6
}

#(append! default-script-alist
   (list
    `(woodwindhalclosed
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,woodwind-half-closed)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

half-closed = #(make-articulation 'woodwindhalfclosed)

woodwind-three-quarters-closed = \markup {
    % \hspace #0.5
    \fontsize #12
    \override #'(font-name . "ekmelos")
    \char ##xe5F5
}

#(append! default-script-alist
   (list
    `(woodwindthreequartersclosed
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,woodwind-three-quarters-closed)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

three-quarters-closed= #(make-articulation 'woodwindthreequartersclosed)

woodwind-closed = \markup {
    % \hspace #0.5
    \fontsize #12
    \override #'(font-name . "ekmelos")
    \char ##xe5F4
}

#(append! default-script-alist
   (list
    `(woodwindclosed
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,woodwind-closed)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

wind-closed = #(make-articulation 'woodwindclosed)

% accidentals

flat-markup = \markup {
    \fontsize #1 {
        \override #'(whiteout-style . "outline")
        \override #'(whiteout . 1)
        {
            \accidental #-1/2
        }
    }
}

#(append! default-script-alist
   (list
    `(flat-list
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,flat-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

flat-articulation = #(make-articulation 'flat-list)

quarter-flat-markup = \markup {
    \fontsize #1 {
        \override #'(whiteout-style . "outline")
        \override #'(whiteout . 1)
        {
            \accidental #-1/4
        }
    }
}

#(append! default-script-alist
   (list
    `(quarter-flat-list
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,quarter-flat-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

quarter-flat-articulation = #(make-articulation 'quarter-flat-list)

quarter-sharp-markup = \markup {
    \fontsize #1 {
        \override #'(whiteout-style . "outline")
        \override #'(whiteout . 1)
        {
            \accidental #1/4
        }
    }
}

#(append! default-script-alist
   (list
    `(quarter-sharp-list
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,quarter-sharp-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

quarter-sharp-articulation = #(make-articulation 'quarter-sharp-list)

sharp-markup = \markup {
    \fontsize #1 {
        \override #'(whiteout-style . "outline")
        \override #'(whiteout . 1)
        {
            \accidental #1/2
        }
    }
}

#(append! default-script-alist
   (list
    `(sharp-list
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,sharp-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

sharp-articulation = #(make-articulation 'sharp-list)

natural-markup = \markup {
    \fontsize #1 {
        \override #'(whiteout-style . "outline")
        \override #'(whiteout . 1)
        {
            \accidental #0
        }
    }
}

#(append! default-script-alist
   (list
    `(natural-list
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,natural-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

natural-articulation = #(make-articulation 'natural-list)

hammer-on-markup = \markup {
    \fontsize #4 {
        \override #'(font-name . "Bodoni72 Book")
        \override #'(whiteout-style . "outline")
        \override #'(whiteout . 1)
        {
            H
        }
    }
}

#(append! default-script-alist
   (list
    `(hammer-on-articulation
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,hammer-on-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

hammer-on = #(make-articulation 'hammer-on-articulation)

tremolo-markup = \markup {
    \fontsize #4.5
    \override #'(font-name . "ekmelos")
    {
        \hspace #0.5
        \char ##xe222
    }
}

#(append! default-script-alist
   (list
    `(tremolomarkup
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,tremolo-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

tremolo-articulation = #(make-articulation 'tremolomarkup)

salzedo-thunder-markup = \markup {
    \fontsize #5
    \override #'(font-name . "ekmelos")
    {
        \hspace #0.5
        \char ##xe686
    }
}

#(append! default-script-alist
   (list
    `(salzedothundermarkup
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,salzedo-thunder-markup)
           (avoid-slur . around)
           (padding . 0.20)
           (script-priority . 150)
           (side-relative-direction . ,DOWN)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

salzedo-thunder = #(make-articulation 'salzedothundermarkup)

% fermatas

extremely-short-fermata = \markup {
    \center-column {
        \override #'(font-name . "ekmelos")
        \char ##xf69E
    }
}

very-short-fermata = \markup {
    \center-column {
        \override #'(font-name . "ekmelos")
        \char ##xe4C2
    }
}

short-fermata = \markup {
    \center-column {
        \override #'(font-name . "ekmelos")
        \char ##xe4C4
    }
}

middle-fermata = \markup {
    \center-column {
        \override #'(font-name . "ekmelos")
        \char ##xe4C0
    }
}

long-fermata = \markup {
    \center-column {
        \override #'(font-name . "ekmelos")
        \char ##xe4C6
    }
}

very-long-fermata = \markup {
    \center-column {
        \override #'(font-name . "ekmelos")
        \char ##xe4C8
    }
}

extremely-long-fermata = \markup {
    \center-column {
        \override #'(font-name . "ekmelos")
        \char ##xf6A0
    }
}
