set M := {0,1,2};
set N := {0 ..8};
set F := {0,1,2,3};
set V := {0 ..6};

param  Vd[N*V] := <0,0>1, <0,3>1, <0,4>1, <0,5>1, <0,6>1, 
                  <1,0>1, <1,1>1, <1,2>1, <1,3>1, <1,4>1, <1,5>1, <1,6> 1, 
                  <2,0>1, <2,1>1, <2,3>1, <2,4>1, <2,5>1, <2,6> 1,
                  <3,0> 1, <3,1> 1, <3,2> 1, <3,6>1, 
                  <4,0>1, <4,1>1, <4,3>1, <4,4>1, <4,5>1, <4,6> 1, 
                  <5,0> 1, <5,4> 1, <5,5> 1, <5,6>1, 
                  <6,0>1, <6,1>1, <6,2>1, <6,3>1, <6,4>1, <6,5> 1, <6,6> 1, 
                  <7,0>1, <7,3>1, <7,4>1, <7,6> 1, 
                  <8,2>1, <8,3>1, <8,4>1, <8,5>1, <8,6> 1 default 0;

param capFlow[F] := <0> 5, <1> 6,<2> 4, <3> 6;
param sV[V] := <0>2, <1>3, <2>1, <3>2, <4>1, <5>2, <6>2 ;

param path[F*N]:= <0,0>1, <0,2> 1, <0,5> 1, <0,6> 1, <0,3> 1,
                  <1,0>1, <1,2> 1, <1,3> 1,
                  <2,1> 1, <2,4> 1, <2,3> 1,
                  <3,1>1, <3,4>1, <3,8> 1, <3,7>1, <3,3> 1 default 0;

set Ps := {0,1,2};

param Rms[M*Ps*V] := <0,0,2>1, <0,0,3>1,    <0,1,0> 1, <0,1,6>1, 
                     <1,0,2>1,  
                     <2,0,0>1, <2,0,2>1, <2,0,5>1, <2,1,4>1, <2,1,6>1, <2,2,1>1, <2,2,3> 1 default 0;
param sizeRms[M*Ps] := <0,0> 2,    <0,1> 2, <0,2> 0, 
                 <1,0> 1,       <1,1> 0 ,    <1,2> 0,
                 <2,0> 3, <2,1> 2, <2,2> 2;


param Rmt[M*Ps]:=<0,0> 1, <0,1> 0, <0,2> 0,      
                 <1,0> 0, <1,1> 0, <1,2> 0,     
                 <2,0> 1, <2,1> 0, <2,2> 0;

param w[<m,p> in M*Ps] :=  Rmt[m,p] + 1 ;                 

set crossPathD[N] := <0> {0, 1},<1> {2, 3},<2> {0, 1},<3> {0, 1, 2, 3},<4> {2, 3},<5> {0},<6> {0},<7> {3},<8> {3};

set MDP := M*N*Ps;
set MP := M*Ps;
set DVF := N*V*F;
set DV := N*V;


var y[<d,v,f> in DVF] integer >=0 <= if (path[f,d] == 1 and Vd[d,v] == 1) then 1 else 0 end;
var s[M*Ps] integer >=0 ;

maximize fo : w[0,1] * s[0,1]+ w[2,0] * s[2,0]+ w[2,2] * s[2,2]; 

subto c1: forall <f> in F do
                 sum <d,v,f> in DVF : sV[v] * y[d,v,f] <= capFlow[f];

subto c2: forall <d,v> in DV do
             sum <d,v,f> in DVF : y[d,v,f] <= 1;

subto c3: s[0,1] + s[2,0] + s[2,2] >= 1;

subto c4: sum <d,2,f> in DVF : y[d,2,f] >= 4;   # initial solution
subto c5: sum <d,3,f> in DVF : y[d,3,f] >= 3;
subto c6: sum <d,4,f> in DVF : y[d,4,f] >= 1;
subto c7: sum <d,1,f> in DVF : y[d,6,f] >= 1;

subto x1: s[0,1] <= sum <d,0,f> in DVF : y[d,0,f];
subto x2: s[0,1] <= sum <d,6,f> in DVF : y[d,6,f];
subto x3: s[2,0] <= sum <d,0,f> in DVF : y[d,0,f];
subto x4: s[2,0] <= sum <d,2,f> in DVF : y[d,2,f];
subto x5: s[2,0] <= sum <d,5,f> in DVF : y[d,5,f];
subto x6: s[2,2] <= sum <d,1,f> in DVF : y[d,1,f];
subto x7: s[2,2] <= sum <d,3,f> in DVF : y[d,3,f];
