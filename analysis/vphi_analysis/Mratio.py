import numpy as np

Volt_FB=1.
nbits_fb=14
Rfb=7780.+50.
vphi_fb=9600.

Volt_detb=2.5
nbits_detb=16
Rdetb=519.
vphi_detb=40.

Ifb=vphi_fb/2**nbits_fb*Volt_FB/Rfb
Idetb=vphi_detb/2**nbits_detb*Volt_detb/Rdetb

Mratio=Ifb/Idetb

print 'Mratio=', Mratio
