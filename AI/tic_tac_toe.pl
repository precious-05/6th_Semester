% -----------------------------
% TIC TAC TOE IN PROLOG
% -----------------------------

% --------- BOARD ---------

% Initial empty board
initial_board([e,e,e,
               e,e,e,
               e,e,e]).

% --------- PLAYER ---------

% Switch player
next_player(x, o).
next_player(o, x).

% --------- MOVE ---------

% Make a move at Position (1-9)
move(Board, Player, Pos, NewBoard) :-
    nth1(Pos, Board, e),           % position must be empty
    replace(Board, Pos, Player, NewBoard).

% Replace element in list
replace([_|T], 1, X, [X|T]).
replace([H|T], Pos, X, [H|R]) :-
    Pos > 1,
    Pos1 is Pos - 1,
    replace(T, Pos1, X, R).

% --------- WIN CONDITIONS ---------

win(Board, Player) :-
    row(Board, Player);
    column(Board, Player);
    diagonal(Board, Player).

row(Board, P) :-
    nth1(1, Board, P), nth1(2, Board, P), nth1(3, Board, P);
    nth1(4, Board, P), nth1(5, Board, P), nth1(6, Board, P);
    nth1(7, Board, P), nth1(8, Board, P), nth1(9, Board, P).

column(Board, P) :-
    nth1(1, Board, P), nth1(4, Board, P), nth1(7, Board, P);
    nth1(2, Board, P), nth1(5, Board, P), nth1(8, Board, P);
    nth1(3, Board, P), nth1(6, Board, P), nth1(9, Board, P).

diagonal(Board, P) :-
    nth1(1, Board, P), nth1(5, Board, P), nth1(9, Board, P);
    nth1(3, Board, P), nth1(5, Board, P), nth1(7, Board, P).

% --------- GAME OVER ---------

game_over(Board, Player) :-
    win(Board, Player),
    write(Player), write(' wins!'), nl.

game_over(Board, _) :-
    \+ member(e, Board),
    write('Game is a draw.'), nl.
