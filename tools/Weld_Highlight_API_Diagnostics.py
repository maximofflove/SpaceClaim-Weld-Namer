# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# Read-only API inspection for independent weld A/B highlight colors.
# Does not create groups, change selection, colors or geometry, or open windows.
import clr
import os
import io
import tempfile
import traceback
from System.Reflection import BindingFlags
from System import AppDomain

lines = []
flags = BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly

def emit(value):
    lines.append(str(value))

def describe(t):
    emit('\nTYPE ' + str(t.FullName))
    if t.IsEnum:
        emit('ENUM: ' + ', '.join(str(x) for x in t.GetEnumNames()))
        return
    for ctor in t.GetConstructors():
        emit('CTOR ' + str(ctor))
    for prop in t.GetProperties(flags):
        emit('PROPERTY ' + str(prop) + ' | writable=' + str(prop.CanWrite))
    for event in t.GetEvents(flags):
        emit('EVENT ' + str(event))
    for method in t.GetMethods(flags):
        if not method.IsSpecialName:
            emit(('STATIC ' if method.IsStatic else 'INSTANCE ') + str(method))

emit('Weld Namer: custom highlight API probe, V19')
try:
    selection = Selection.Empty()
    describe(selection.GetType())
except Exception:
    emit(traceback.format_exc())

# Inspect public metadata of assemblies already loaded by SpaceClaim.
# No new application DLLs are loaded, instantiated or invoked here.
seen = set()
for assembly in AppDomain.CurrentDomain.GetAssemblies():
    name = str(assembly.GetName().Name)
    if not name.startswith('SpaceClaim.Api.V19'):
        continue
    emit('\nASSEMBLY ' + str(assembly.FullName))
    try:
        exported = assembly.GetExportedTypes()
    except Exception:
        emit(traceback.format_exc())
        continue
    for t in exported:
        full = str(t.FullName)
        short = str(t.Name)
        if full in seen:
            continue
        # Rendering primitives and their styles, custom display hooks, window
        # attachment points, and curve/face extraction for exact geometry.
        wanted = ('.Graphics.' in full or '.Rendering.' in full or
                  short in ('Graphic', 'GraphicStyle', 'CustomObject',
                            'CustomObjectDisplay', 'IDisplayObject', 'Window',
                            'DisplayMode', 'LineStyle', 'FillStyle', 'Color',
                            'DesignEdge', 'IDesignEdge', 'DesignFace', 'IDesignFace',
                            'Tool', 'InteractionMode') or
                  'Highlight' in short or 'Render' in short)
        if wanted:
            seen.add(full)
            try:
                describe(t)
            except Exception:
                emit(traceback.format_exc())

path = os.path.join(tempfile.gettempdir(), 'SpaceClaim_Weld_Highlight_API_V19.txt')
try:
    with io.open(path, 'w', encoding='utf-8') as stream:
        stream.write(u'\n'.join(unicode(x) for x in lines))
    print('API report saved: ' + path)
    print('Types inspected: %d. No model changes.' % len(seen))
except Exception:
    print(traceback.format_exc())
    for line in lines:
        print(line)
