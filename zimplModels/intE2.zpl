param n := read "instanceOpenTSP.txt" as "1n" use 1;
param nArcs := read "instanceOpenTSP.txt" as "2n" use 1;

set I := {0 .. n-1}; #  start node 0 , end node n-1
set IIl := I*I;

param bigD := 99999;
param d[IIl] := read "instanceOpenTSP.txt" as "<1n 2n> 3n" skip 1 use nArcs default bigD;

param nodeS1 := 1;
param nodeE1 := 2;

set II := {<i,j> in IIl  with d[i,j] < bigD and i != j};

set Nodes:= {nodeS1,0, 3, 4, 5, 6, 10, 15, 20, 25, 30, 35, 40, 45,nodeE1};
param sizeItems[Nodes]:= <nodeS1> 1,<0> 1, <3> 3, <4> 2, <5> 6, <6> 1, <10> 4, <15>5, <20>3, <25> 3, <30> 1, <35>5, <40>6, <45>5, <nodeE1>11;

param maxL := 13;
param Kf := 20;
param bigM := sum <k> in Nodes: sizeItems[k];

var x[<i,j> in II] integer  >=0  <= if i == nodeE1 then 0 else 1 end; 
var y[II] >=0 <= Kf; 
var w[Nodes] binary;
var zE1 binary;
var zS1 binary;
minimize cost : sum <k> in Nodes: -100 * w[k] + sum <i,j> in II   :  x[i,j]; 

subto c01: sum <i,nodeE1> in II : x[i,nodeE1] == zE1; 

subto c1 : sum <nodeS1, j> in II : x[nodeS1,j] == zS1; 

subto c30: forall <j> in I do 
             sum <i,j> in II : x[i,j] <= 1;

subto c31: forall <j> in I with j != nodeS1 and j != nodeE1 do 
             sum <i,j> in II : x[i,j] - sum <j,i> in II : x[j,i] == 0;


subto c4: sum <i,j> in II : x[i,j] <= maxL;             

subto d01: sum <nodeS1,i> in II : y[nodeS1,i] ==  sizeItems[nodeS1]*w[nodeS1];

subto d1 : forall <i,j> in II do 
              y[i,j] <= bigM *x[i,j];

subto d3: forall <j> in I-Nodes with j != nodeS1 and j != nodeE1 do
             sum <i,j> in II : y[i,j] - sum <j,i> in II : y[j,i] == 0;

subto d4: forall <j> in Nodes with j != nodeS1 and j != nodeE1 do
             sum <i,j> in II : y[i,j] - sum <j,i> in II : y[j,i] == -sizeItems[j]*w[j];

subto d5: sum <i,nodeE1> in II : y[i,nodeE1] == sum<k> in Nodes : sizeItems[k]*w[k];  


