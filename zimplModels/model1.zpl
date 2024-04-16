set M := {0,1,2};
set N := {0 ..8};
set F := {0,1,2,3};
set path[F]:= <0> {0, 2, 5, 6, 3},<1> {0, 2, 3}, <2> {1, 4, 3}, <3> {1, 4, 8, 7, 3};
set V := {0 ..6};
set Vd[N] := <0> {0, 3, 4, 5, 6}, <1> {0, 1, 2, 3, 4, 5, 6}, <2> {0, 1, 3, 4, 5, 6},
<3> {0, 1, 2, 6}, <4> {0, 1, 3, 4, 5, 6}, <5> {0, 4, 5, 6}, <6> {0, 1, 2, 3, 4, 5, 6}, <7> {0, 3, 4, 6}, <8> {2, 3, 4, 5, 6};

param capFlow[F] := <0> 5, <1> 6,<2> 4, <3> 6;
param sV[V] := <0>2, <1>3, <2>1, <3>2, <4>1, <5>2, <6>2 ;

set Ps := {0,1,2};
set Rms[M*Ps] := <0,0> {2, 3},    <0,1> {0, 6}, <0,2> {}, 
                 <1,0> {2},       <1,1> {} ,    <1,2> {},
                 <2,0> {0, 2, 5}, <2,1> {4, 6}, <2,2> {1, 3};
param Rmt[M*Ps]:=<0,0> 1, <0,1> 0, <0,2> 0,      
                 <1,0> 0, <1,1> 0, <1,2> 0,     
                 <2,0> 1, <2,1> 0, <2,2> 0;
set crossPathD[N] := <0> {0, 1},<1> {2, 3},<2> {0, 1},<3> {0, 1, 2, 3},<4> {2, 3},<5> {0},<6> {0},<7> {3},<8> {3};

set MDP := M*N*Ps;
set MP := M*Ps;
set DVF := N*V*F;
set DV := N*V;

var s[MDP] binary;
var a[MDP] integer;
var t[MP] binary;
var b[MP] integer;
var y[DVF] binary;

maximize fo : sum <m,d,p> in MDP : s[m,d,p]  + sum <m,p> in MP : t[m,p];

subto c1: forall <f> in F do
              sum <d,v,f> in DVF : sV[v] * y[d,v,f] <= capFlow[f];

subto c2: forall <d,v> in DV do
             sum <d,v,f> in DVF : y[d,v,f] <= 1;

subto c3: forall <m,d,p> in MDP do
             a[m,d,p] == sum <d,v,f> in DVF : y[d,v,f];

subto c4: forall <m,d,p> in MDP with card(Rms[m,p]) > 0 do
             s[m,d,p] <=  a[m,d,p] / card(Rms[m,p]);

subto c5: forall <m,p> in MP do
             b[m,p] == sum <d,v,f> in DVF : y[d,v,f];

subto c6: forall <m,p> in MP with card(Rms[m,p]) > 0 do
             t[m,p] <=  b[m,p] / card(Rms[m,p]);

