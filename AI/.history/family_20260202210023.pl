parent(ali, ahmed).
parent(ahmed, sara).

grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
?- grandparent(ali, sara).




%-------Comments are added using percentage sign-------------------------


% ----- FACTS -----
parent(ali, ahmed).
parent(ali, sana).
parent(ahmed, sara).
parent(sana, bilal).

male(ali).
male(ahmed).
male(bilal).

female(sana).
female(sara).

% ----- RULES -----
father(X, Y) :-
    parent(X, Y),
    male(X).

mother(X, Y) :-
    parent(X, Y),
    female(X).

grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y).
