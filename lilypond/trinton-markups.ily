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
