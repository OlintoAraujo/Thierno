param n := read "instanceOpenTSP.txt" as "1n" use 1;
param nArcs := read "instanceOpenTSP.txt" as "2n" use 1;

set I := {0 .. n-1}; #  start node 0 , end node n-1
set IIl := I*I;

param bigM := 99999;
param d[IIl] := read "instanceOpenTSP.txt" as "<1n 2n> 3n" skip 1 use nArcs default bigM;

param nodeS := 0;
param nodeE := 2;
param onThePathNode[I] := <5> 1, <30>1, <20> 1, <17> 1, <38> 1 default 0;

set IIll := {<i,j> in IIl  with d[i,j] < bigM};

set II := IIll union { <nodeE,nodeS> };

var x[<i,j> in II] integer >= 0 <= if i == nodeS and j == nodeE then 0 else 1 end;
var u[<i> in I] >= 0 <= if i == nodeS then 0 else infinity end;

minimize cost : sum <i,j> in II with i != j and d[i,j] < bigM and j != nodeE: d[i,j] * x[i,j]; 

subto c0: sum <nodeS,j> in II : x[nodeS,j] == 1;
subto x0: sum <i,nodeS> in II : x[i,nodeS] == 1;
subto c1: sum <i,nodeE> in II : x[i,nodeE] == 1;
subto cx: x[nodeE,nodeS] == 1;

subto c2: forall <j> in I with j != nodeS and j != nodeE do 
              sum <i,j> in II with i != j : x[i,j] - sum <j,i> in II with i !=j : x[j,i] == 0; 

subto c3: forall <j> in I with onThePathNode[j] == 1 do
              sum <i,j> in II with i !=j : x[i,j] == 1;

subto c6: forall <j> in I with j != nodeS do
              forall <i,j> in II with i != j and i != nodeE  do
                 u[j] >= 1 + u[i] - bigM * ( 1 - x[i,j]);

