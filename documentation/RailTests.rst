Rail Tests
##########

..  rail::

    body    :
    [1] ( ( '[' string ']' )
            ? body[2--6] + '|'
            )
    | [2] body[3--6] '*' body[5--6]
    | [2] body[3--6] '+' body[5--6]
    | [3] ( body[4--5] + )
    | [4] body[5] '?'
    | [5] identifier ( '[' string ']' ) ?
    | [5] quote string quote
    | [5] dquote string dquote
    | [5] '(' body[1--6] ')'
    | [5] cr
    | [6]
    ;
