
% Tower of Hanoi problem in prolog



% Base case:
% Agar sirf 1 disk hai, to sidha source se destination par move karo
hanoi(1, Source, Destination, _) :-
    write('Move disk from '),
    write(Source),
    write(' to '),
    write(Destination),
    nl.

% Recursive case:
% N-1 disks ko source se auxiliary par bhejo,
% phir largest disk ko destination par,
% phir N-1 disks ko auxiliary se destination par
hanoi(N, Source, Destination, Auxiliary) :-
    N > 1,
    N1 is N - 1,
    hanoi(N1, Source, Auxiliary, Destination),
    hanoi(1, Source, Destination, Auxiliary),
    hanoi(N1, Auxiliary, Destination, Source).