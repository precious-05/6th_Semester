parent(ali, ahmed).
parent(ahmed, sara).

grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
?- grandparent(ali, sara).




%-------Comments