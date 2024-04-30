param n := read "instanceOpenTSP.txt" as "1n" use 1;
param nArcs := read "instanceOpenTSP.txt" as "2n" use 1;

set I := {0 .. n-1}; #  start node 0 , end node n-1
set IIl := I*I;

param bigM := 99999;
param d[IIl] := read "instanceOpenTSP.txt" as "<1n 2n> 3n" skip 1 use nArcs default bigM;

param nodeS := 31;
param nodeE := 44;
param onThePathNode[I] := <10> 1  default 0;

set IIll := {<i,j> in IIl  with d[i,j] < bigM};

param HasStoD := sum <nodeS,nodeE> in IIll : 1;

set II := IIll union { <nodeE,nodeS>, <nodeS, nodeE>};

var x[II] binary; 
var u[<i> in I] >= 0 <= if i == nodeS then 0 else infinity end;

#minimize cost : sum <i,j> in II with i != j and d[i,j] < bigM : d[i,j] * x[i,j]; 
minimize cost : sum <i,j> in II with i != j and d[i,j] < bigM : x[i,j]; 

subto c01: sum <i,nodeS> in II : x[i,nodeS] == 1;
subto c02: x[nodeE,nodeS] == 1;

subto c1: sum <nodeS,j> in II : x[nodeS,j] == 1;

subto c2: if sum <i> in I : onThePathNode[i] > 0 or HasStoD == 0 then 
             forall <j> in I with j != nodeS and j != nodeE do 
                 sum <i,j> in II with i != j : x[i,j] - sum <j,i> in II with i !=j : x[j,i] == 0
          end;    

subto c3: forall <j> in I with onThePathNode[j] == 1 do
              sum <i,j> in II with i !=j : x[i,j] == 1;

subto c6:  if sum <i> in I : onThePathNode[i] > 0 or HasStoD == 0  then 
              forall <j> in I with j != nodeS do
                 forall <i,j> in II with i != j and i != nodeE  do
                    u[j] >= 1 + u[i] - bigM * ( 1 - x[i,j])
          end;          

subto c7:  if (sum <i> in I : onThePathNode[i] > 0) or (HasStoD == 0) then 
              x[nodeS,nodeE] == 0
           end;   

