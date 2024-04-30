param n := read "instanceOpenTSP.txt" as "1n" use 1;
param nArcs := read "instanceOpenTSP.txt" as "2n" use 1;

set I := {0 .. n-1}; #  start node 0 , end node n-1
set IIl := I*I;

param bigM := 99999;
param d[IIl] := read "instanceOpenTSP.txt" as "<1n 2n> 3n" skip 1 use nArcs default bigM;

param nodeS1 := 1;
param nodeE1 := 2;

set II := {<i,j> in IIl  with d[i,j] < bigM and i != j} union {<nodeE1,nodeS1>};

set Sources:= {0, 3, 4, 5, 6, 10, 15, 20, 25, 30, 35, 40, 45};
param maxL := 15;

var x[II] binary; 
var y[II] >=0; 
var w[Sources] binary;

minimize cost : sum <k> in Sources : -100 * w[k] + sum <i,j> in II   :  x[i,j]; 

subto c0: x[nodeE1,nodeS1] == 1;

subto c01: sum <i,nodeS1> in II : x[i,nodeS1] == 1;

subto c1 : sum <nodeS1, j> in II : x[nodeS1,j] == 1;

subto c3: forall <j> in I with j != nodeS1 and j != nodeE1 do 
             sum <i,j> in II : x[i,j] - sum <j,i> in II : x[j,i] == 0;

subto c4: sum <i,j> in II : x[i,j] <= maxL;             

subto d01: sum <nodeS1,i> in II : y[nodeS1,i] == (sum<k> in Sources : w[k])+1;

subto d1 : forall <i,j> in II do 
              y[i,j] <= 2*card(Sources)*x[i,j];

subto d3: forall <j> in I-Sources with j != nodeS1 and j != nodeE1 do
             sum <i,j> in II : y[i,j] - sum <j,i> in II : y[j,i] == 0;

subto d4: forall <j> in Sources with j != nodeS1 and j != nodeE1 do
             sum <i,j> in II : y[i,j] - sum <j,i> in II : y[j,i] == w[j];

subto d5: sum <i,nodeE1> in II : y[i,nodeE1] == 1;


