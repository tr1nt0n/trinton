\version "2.23.14"

% ekmelos markups

tremolo-largo = \markup {
    \hspace #0.6
    \fontsize #3.5
    \override #'(font-name . "ekmelos")
    \char ##xe220
}

tremolo-moderato = \markup {
    \hspace #0.6
    \fontsize #3.5
    \override #'(font-name . "ekmelos")
    \char ##xe221
}

tremolo-stretto = \markup {
    \hspace #0.6
    \fontsize #3.5
    \override #'(font-name . "ekmelos")
    \char ##xe222
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
           (direction . ,DOWN)
           (padding . 0.20)
           (script-priority . 150)
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
           (direction . ,DOWN)
           (padding . 0.20)
           (script-priority . 150)
           (skyline-horizontal-padding . 0.20)
           (toward-stem-shift . 0.5)
           ))))

ricochet = #(make-articulation 'multiplestaccato)

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
