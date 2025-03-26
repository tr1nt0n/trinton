\version "2.23.81"

 %%% GRAPHIC BOW PRESSURE %%%

startGraphicBowPressure = #(
    make-music 'TextSpanEvent 'span-direction START 'spanner-id "GraphicBP"
)

stopGraphicBowPressure = #(
    make-music 'TextSpanEvent 'span-direction STOP 'spanner-id "GraphicBP"
)

#(define ((bow-pressure-stencil shape) grob)
  (let* ((lbi (ly:grob-property grob 'left-bound-info '()))
         (rbi (ly:grob-property grob 'right-bound-info '()))
         (lbx (ly:assoc-get 'X lbi 0))
         (rbx (ly:assoc-get 'X rbi 0))
         (ss (ly:staff-symbol-staff-space grob)))
    (set! shape (append '((1 . 0) (0 . 0)) shape))
    (set! shape
      (map
        (lambda (pt) (let ((x (car pt)) (y (cdr pt)))
          (cons (* x (- rbx lbx)) (* -2/3 ss y))))
        shape))
    (grob-interpret-markup grob
      #{ \markup \polygon #shape #})))

startBowSpan =
    #(define-event-function (shape) (number-pair-list?) #{
      -\tweak stencil #(bow-pressure-stencil shape)
       \startGraphicBowPressure #})

stopBowSpan = \stopGraphicBowPressure
