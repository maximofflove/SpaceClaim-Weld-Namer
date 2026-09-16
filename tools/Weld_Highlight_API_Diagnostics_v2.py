# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# SpaceClaim Weld Namer - read-only graphics API probe v2.
# Purpose: identify the exact V19 primitive/indicator API needed to render
# temporary red geometry for weld-side B without changing model appearance.
# This script only reads public CLR metadata. It does not create/rename groups,
# change selection, geometry, colors, rendering, active tools, or windows.

import clr
import os
import io
import tempfile
import traceback
from System.Reflection import BindingFlags
from System import AppDomain

lines = []
flags = BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly
all_public = BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static

def emit(value):
    try:
        lines.append(str(value))
    except Exception:
        lines.append('<unprintable>')

def describe(t, include_inherited=False):
    emit('\nTYPE ' + str(t.FullName))
    try:
        emit('BASE ' + (str(t.BaseType.FullName) if t.BaseType is not None else '<none>'))
    except Exception:
        pass
    try:
        interfaces = list(t.GetInterfaces())
        if interfaces:
            emit('INTERFACES: ' + ', '.join(str(x.FullName) for x in interfaces))
    except Exception:
        pass
    if t.IsEnum:
        emit('ENUM: ' + ', '.join(str(x) for x in t.GetEnumNames()))
        return
    member_flags = all_public if include_inherited else flags
    try:
        for ctor in t.GetConstructors():
            emit('CTOR ' + str(ctor))
    except Exception:
        emit('CTOR ERROR ' + traceback.format_exc())
    try:
        for prop in t.GetProperties(member_flags):
            emit('PROPERTY ' + str(prop) + ' | writable=' + str(prop.CanWrite))
    except Exception:
        emit('PROPERTY ERROR ' + traceback.format_exc())
    try:
        for event in t.GetEvents(member_flags):
            emit('EVENT ' + str(event))
    except Exception:
        emit('EVENT ERROR ' + traceback.format_exc())
    try:
        for method in t.GetMethods(member_flags):
            if not method.IsSpecialName:
                emit(('STATIC ' if method.IsStatic else 'INSTANCE ') + str(method))
    except Exception:
        emit('METHOD ERROR ' + traceback.format_exc())

emit('Weld Namer: custom highlight API probe v2, V19')
emit('READ-ONLY REFLECTION PROBE - NO MODEL CHANGES')

# Also record current selection runtime type(s) without changing the selection.
try:
    active = Selection.GetActive()
    emit('\nACTIVE SELECTION COUNT ' + str(active.Count))
    for item in list(active.Items)[:10]:
        t = item.GetType()
        emit('ACTIVE ITEM TYPE ' + str(t.FullName))
except Exception:
    emit('ACTIVE SELECTION READ ERROR\n' + traceback.format_exc())

seen = set()
assemblies = []
for assembly in AppDomain.CurrentDomain.GetAssemblies():
    name = str(assembly.GetName().Name)
    if name.startswith('SpaceClaim.Api.V19'):
        assemblies.append(assembly)
        emit('\nASSEMBLY ' + str(assembly.FullName))

# First pass: collect all exported V19 types so we can identify Primitive subclasses.
all_types = []
for assembly in assemblies:
    try:
        all_types.extend(list(assembly.GetExportedTypes()))
    except Exception:
        emit('ASSEMBLY TYPE LOAD ERROR ' + str(assembly.FullName) + '\n' + traceback.format_exc())

primitive_base = None
for t in all_types:
    if str(t.FullName) == 'SpaceClaim.Api.V19.Display.Primitive':
        primitive_base = t
        break

# Exact types needed around graphics, indicators and edge-curve extraction.
exact_names = set([
    'SpaceClaim.Api.V19.Display.Primitive',
    'SpaceClaim.Api.V19.Display.Graphic',
    'SpaceClaim.Api.V19.Display.GraphicStyle',
    'SpaceClaim.Api.V19.Indicator',
    'SpaceClaim.Api.V19.Tool',
    'SpaceClaim.Api.V19.Window',
    'SpaceClaim.Api.V19.DesignEdge',
    'SpaceClaim.Api.V19.IDesignEdge',
    'SpaceClaim.Api.V19.DesignFace',
    'SpaceClaim.Api.V19.IDesignFace',
    'SpaceClaim.Api.V19.Modeler.Edge',
    'SpaceClaim.Api.V19.Modeler.Face',
    'SpaceClaim.Api.V19.Geometry.ITrimmedCurve',
    'SpaceClaim.Api.V19.Geometry.CurveSegment',
    'SpaceClaim.Api.V19.Geometry.Curve',
    'SpaceClaim.Api.V19.Geometry.Interval',
    'SpaceClaim.Api.V19.Geometry.Point',
])

for t in all_types:
    full = str(t.FullName)
    short = str(t.Name)
    wanted = full in exact_names
    if full.startswith('SpaceClaim.Api.V19.Display.'):
        wanted = True
    if short in ('Indicator', 'IIndicator') or 'Indicator' in short:
        wanted = True
    if 'Primitive' in short:
        wanted = True
    if primitive_base is not None:
        try:
            if t != primitive_base and primitive_base.IsAssignableFrom(t):
                wanted = True
        except Exception:
            pass
    # Curve/edge helper types that may expose conversion to a display primitive.
    if full.startswith('SpaceClaim.Api.V19.Geometry.') and (
            'Curve' in short or 'Polyline' in short or 'Segment' in short):
        wanted = True
    if wanted and full not in seen:
        seen.add(full)
        try:
            describe(t, include_inherited=False)
        except Exception:
            emit('DESCRIBE ERROR ' + full + '\n' + traceback.format_exc())

# Explicit inherited-member dumps for the most relevant types, because useful
# factory methods may be declared on a base class rather than the concrete type.
for full_name in [
        'SpaceClaim.Api.V19.Display.Primitive',
        'SpaceClaim.Api.V19.Indicator',
        'SpaceClaim.Api.V19.Modeler.Edge',
        'SpaceClaim.Api.V19.Geometry.CurveSegment']:
    for t in all_types:
        if str(t.FullName) == full_name:
            emit('\nINHERITED MEMBERS FOR ' + full_name)
            try:
                describe(t, include_inherited=True)
            except Exception:
                emit(traceback.format_exc())
            break

path = os.path.join(tempfile.gettempdir(), 'SpaceClaim_Weld_Highlight_API_V19_v2.txt')
try:
    with io.open(path, 'w', encoding='utf-8') as stream:
        stream.write(u'\n'.join(unicode(x) for x in lines))
    print('API v2 report saved: ' + path)
    print('Types inspected: %d. No model changes.' % len(seen))
except Exception:
    print(traceback.format_exc())
    for line in lines:
        print(line)
