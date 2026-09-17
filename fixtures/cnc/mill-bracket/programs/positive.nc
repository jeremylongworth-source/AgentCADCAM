%
( CADCAM synthetic CNC fixture )
( JOB: cnc-mill-bracket )
( REVISION: B )
( UNITS: mm )
( MACHINE: fixture-mill-3axis )
( CONTROLLER: fixture-controller )
( POST: fixture-post-v1 )
( SETUP: setup-1 )
G21
G90 G17 G54
G94 G97
M5
T1 M6
S5000 M3
G0 X0 Y0 Z25
G1 Z0 F100
G1 X60 Y0 F200
G1 X60 Y40
G1 X0 Y40
G1 X0 Y0
G0 Z25
M5
M30
%
