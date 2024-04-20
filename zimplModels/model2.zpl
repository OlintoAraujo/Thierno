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
param sizeRms[M*Ps] := <0,0> 2, <0,1> 2, <0,2> 0, 
                       <1,0> 1, <1,1> 0, <1,2> 0,
                       <2,0> 3, <2,1> 2, <2,2> 2;


param Rmt[M*Ps]:=<0,0> 1, <0,1> 0, <0,2> 0,      
                 <1,0> 0, <1,1> 0, <1,2> 0,     
                 <2,0> 1, <2,1> 0, <2,2> 0;
set crossPathD[N] := <0> {0, 1},<1> {2, 3},<2> {0, 1},<3> {0, 1, 2, 3},<4> {2, 3},<5> {0},<6> {0},<7> {3},<8> {3};

set MDP := M*N*Ps;
set MP := M*Ps;
set DVF := N*V*F;
set DV := N*V;
set MVP := M*V*Ps;

var s[<m,d,p> in MDP] integer >=0 <= if sizeRms[m,p] > 0 then 1 else 0 end; 
var a[MDP] integer;
var t[<m,p> in MP] integer >=0 <=  if Rmt[m,p] > 0 then 1 else 0 end;
var b[MP] integer;
var y[<d,v,f> in DVF] integer >=0 <= if (path[f,d] == 1 and Vd[d,v] == 1) then 1 else 0 end;
var w[MVP] binary;

maximize fo : sum <m,d,p> in MDP : s[m,d,p]  + sum <m,p> in MP : t[m,p];

subto c1: forall <f> in F do
                 sum <d,v,f> in DVF : sV[v] * y[d,v,f] <= capFlow[f];

subto c2: forall <d,v> in DV do
             sum <d,v,f> in DVF : y[d,v,f] <= 1;

subto c3: forall <m,d,p> in MDP do
             a[m,d,p] == sum <d,v,f> in DVF with Rms[m,p,v] == 1: y[d,v,f];

subto c4: forall <m,d,p> in MDP  with sizeRms[m,p] > 0 do
                sizeRms[m,p] * s[m,d,p] <=  a[m,d,p]; 

subto c50: forall <m,v,p> in MVP do
             w[m,v,p] <= sum <d,v,f> in DVF with Rmt[m,p] == 1 and Rms[m,p,v] == 1 : y[d,v,f];

subto c51: forall <m,p> in MP do
             b[m,p] == sum <m,v,p> in MVP : w[m,v,p];

subto c6: forall <m,p> in MP with sizeRms[m,p] > 0 do
                sizeRms[m,p] * t[m,p] <=  b[m,p];

# LOCAL SEARCH                
   # fix  strategy 1
#subto f1_1 : sum <1,2,f> in DVF : y[1,2,f] == 1; 
#subto f1_2 : sum <1,3,f> in DVF : y[1,3,f] == 1;
#subto f6_1 : sum <6,2,f> in DVF : y[6,2,f] == 1; 
#subto f6_2 : sum <6,3,f> in DVF : y[6,3,f] == 1;
#subto f8_1 : sum <8,2,f> in DVF : y[8,2,f] == 1; 
#subto f8_2 : sum <8,3,f> in DVF : y[8,3,f] == 1;
#
#subto f3_1: sum <3,2,f> in DVF : y[3,2,f] == 1;
#subto f0_1: sum <0,5,f> in DVF : y[0,5,f] == 1;
   # fix strategy 2
#subto s1 : sum <0,d,0> in MDP : s[0,d,0] == 3;
#subto s2 : sum <1,d,0> in MDP : s[1,d,0] == 4;
#subto t1 : t[0,0] == 1;
#subto t2 : t[2,0] == 1;
