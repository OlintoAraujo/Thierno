param n := read "instanceOpenTSP.txt" as "1n" use 1;
param nArcs := read "instanceOpenTSP.txt" as "2n" use 1;

set I := {0 .. n}; #  start node 0 , end node n-1,  n is a fake node
set IIl := I*I;

param bigD := 99999;
param d[IIl] := read "instanceOpenTSP.txt" as "<1n 2n> 3n" skip 1 use nArcs default bigD;

param nodeS1 := 1;
param L:= 15 + 1;

set II := {<i,j> in IIl  with (d[i,j] < bigD and i != j) or j == n};

param bigM := card(I) * 2; 

var x[II] binary; 
var u[I] >=0;

minimize cost : sum <i,j> in II   :  x[i,j]; 

subto c0 : sum <nodeS1, j> in II : x[nodeS1,j] == 1;

subto c1 : sum <i, n> in II : x[i,n] == 1;

subto c3 : forall <j> in I  do 
              sum <i,j> in II : x[i,j] <= 1;

subto c4 : forall <j> in I with j != nodeS1 and j != n do
              sum <i,j> in II : x[i,j] - sum<j,i> in II : x[j,i] == 0;

subto c5 : u[nodeS1] == 0;

subto c6 : forall <i,j> in II  with j != nodeS1 do
             u[j] >= u[i] + 1 + bigM *( x[i,j] - 1) ;

subto c7 : sum <i,j> in II : x[i,j] == L;

