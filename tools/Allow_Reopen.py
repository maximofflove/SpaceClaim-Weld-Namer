# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# Explicit re-arm after closing the v0.6 window. Does not run model operations.
from System import AppDomain, String
from System.Threading import Monitor
key = 'MF.SpaceClaim.WeldNamer.v06.State'
lock = String.Intern('MF.SpaceClaim.WeldNamer.v06.StateLock')
Monitor.Enter(lock)
try:
    state = AppDomain.CurrentDomain.GetData(key)
    if state is None:
        print('Ready. Run Weld_Namer.py once.')
    elif state['phase'] in ('closed', 'failed'):
        AppDomain.CurrentDomain.SetData(key, None)
        print('Re-armed. Run Weld_Namer.py once.')
    else:
        print('Window is open or queued. Close it before re-arming.')
finally:
    Monitor.Exit(lock)
