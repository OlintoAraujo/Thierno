param n := read "instanceOpenTSP.txt" as "1n" use 1;
param nArcs := read "instanceOpenTSP.txt" as "2n" use 1;

set I := {0 .. n-1}; #  start node 0 , end node n-1
set IIl := I*I;

param bigM := 99999;
param d[IIl] := read "instanceOpenTSP.txt" as "<1n 2n> 3n" skip 1 use nArcs default bigM;

param nodeS1 := 1;
param nodeE1 := 2;

set II := {<i,j> in IIl  with d[i,j] < bigM and i != j} union {<nodeE1,nodeS1>};

set Items:= {0, 3, 4, 5, 6, 10, 15, 20, 25, 30, 35, 40, 45};
param sizeItems[Items]:= <0> 5, <3> 3, <4> 4, <5> 6, <6> 2, <10> 4, <15>5, <20>3, <25> 3, <30> 1, <35>5, <40>6, <45>5;
param maxL := 10;
param Kf := 16;

var x[II] binary; 
var y[II] >=0 <= Kf+1; 
var w[Items] binary;

minimize cost : sum <k> in Items : -100 * sizeItems[k]*w[k] + sum <i,j> in II   :  x[i,j]; 

subto c0: x[nodeE1,nodeS1] == 1;

subto c01: sum <i,nodeS1> in II : x[i,nodeS1] == 1;

subto c1 : sum <nodeS1, j> in II : x[nodeS1,j] == 1;

subto c3: forall <j> in I with j != nodeS1 and j != nodeE1 do 
             sum <i,j> in II : x[i,j] - sum <j,i> in II : x[j,i] == 0;

subto c4: sum <i,j> in II : x[i,j] <= maxL;             

subto d01: sum <nodeS1,i> in II : y[nodeS1,i] == (sum<k> in Items : sizeItems[k]*w[k])+1;

subto d1 : forall <i,j> in II do 
              y[i,j] <= 2*card(Items)*x[i,j];

subto d3: forall <j> in I-Items with j != nodeS1 and j != nodeE1 do
             sum <i,j> in II : y[i,j] - sum <j,i> in II : y[j,i] == 0;

subto d4: forall <j> in Items with j != nodeS1 and j != nodeE1 do
             sum <i,j> in II : y[i,j] - sum <j,i> in II : y[j,i] == sizeItems[j]*w[j];

subto d5: sum <i,nodeE1> in II : y[i,nodeE1] == 1;


