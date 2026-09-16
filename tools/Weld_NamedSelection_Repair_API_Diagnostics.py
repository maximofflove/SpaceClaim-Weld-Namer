# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# SpaceClaim Weld Namer v0.12 - READ-ONLY Named Selection repair API probe.
#
# Purpose:
#   Find the exact SpaceClaim 2021 R1 / Script API V19 methods available for
#   safely editing the contents of an EXISTING Named Selection / Group.
#
# This probe uses CLR reflection and read-only queries only. It does NOT:
#   - create, rename or delete Named Selections;
#   - modify group contents;
#   - change active selection;
#   - change geometry, colors, rendering or the document.
#
# Output:
#   %TEMP%\SpaceClaim_Weld_NamedSelection_Repair_API_V19.txt

import clr
import os
import io
import tempfile
import traceback
from System import AppDomain
from System.Reflection import BindingFlags

lines = []
flags_declared = BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly
flags_all = BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static


def emit(value):
    try:
        lines.append(str(value))
    except Exception:
        lines.append('<unprintable>')


def describe_type(t, include_inherited=False):
    emit('\nTYPE ' + str(t.FullName))
    try:
        emit('ASSEMBLY ' + str(t.Assembly.FullName))
    except Exception:
        pass
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
        try:
            emit('ENUM: ' + ', '.join(str(x) for x in t.GetEnumNames()))
        except Exception:
            pass
        return

    member_flags = flags_all if include_inherited else flags_declared
    try:
        for ctor in t.GetConstructors():
            emit('CTOR ' + str(ctor))
    except Exception:
        emit('CTOR ERROR\n' + traceback.format_exc())
    try:
        for prop in t.GetProperties(member_flags):
            emit('PROPERTY ' + str(prop) + ' | readable=' + str(prop.CanRead) + ' | writable=' + str(prop.CanWrite))
    except Exception:
        emit('PROPERTY ERROR\n' + traceback.format_exc())
    try:
        for event in t.GetEvents(member_flags):
            emit('EVENT ' + str(event))
    except Exception:
        emit('EVENT ERROR\n' + traceback.format_exc())
    try:
        for method in t.GetMethods(member_flags):
            if not method.IsSpecialName:
                emit(('STATIC ' if method.IsStatic else 'INSTANCE ') + str(method))
    except Exception:
        emit('METHOD ERROR\n' + traceback.format_exc())


def method_is_repair_relevant(method):
    try:
        name = str(method.Name).lower()
        if name in ('add', 'remove', 'replace', 'delete', 'rename', 'create', 'set', 'clear'):
            return True
        keywords = ('group', 'selection', 'member', 'object', 'item', 'content', 'replace', 'remove', 'add', 'delete', 'rename', 'set')
        for k in keywords:
            if k in name:
                return True
    except Exception:
        pass
    return False


emit('SpaceClaim Weld Namer v0.12 - Named Selection Repair API Probe')
emit('SpaceClaim 2021 R1 / Script API V19')
emit('READ-ONLY REFLECTION + READ-ONLY GROUP INSPECTION')
emit('NO MODEL CHANGES')

# Record current active selection only; never set or clear it.
try:
    active = Selection.GetActive()
    emit('\nACTIVE SELECTION')
    emit('Count = ' + str(active.Count))
    try:
        for item in list(active.Items)[:20]:
            emit('Item type = ' + str(item.GetType().FullName))
    except Exception:
        emit('Active item enumeration error\n' + traceback.format_exc())
except Exception:
    emit('\nACTIVE SELECTION READ ERROR\n' + traceback.format_exc())

# Read existing Named Selection groups with the already proven explicit root call.
# This is read-only and deliberately does not use Part.Groups.
try:
    root = GetRootPart()
    emit('\nROOT PART')
    emit('Runtime type = ' + str(root.GetType().FullName))
    groups = NamedSelection.GetGroups(root)
    emit('NamedSelection.GetGroups(root) count = ' + str(len(groups)))
    for index, group in enumerate(list(groups)[:8]):
        try:
            emit('GROUP[%d] runtime type = %s' % (index, str(group.GetType().FullName)))
            try:
                emit('GROUP[%d] Name = %s' % (index, str(group.Name)))
            except Exception:
                pass
        except Exception:
            emit('GROUP[%d] runtime inspection error\n%s' % (index, traceback.format_exc()))
except Exception:
    emit('\nGROUP READ ERROR\n' + traceback.format_exc())

# Load all public V19 API types.
assemblies = []
all_types = []
for assembly in AppDomain.CurrentDomain.GetAssemblies():
    try:
        aname = str(assembly.GetName().Name)
    except Exception:
        continue
    if aname.startswith('SpaceClaim.Api.V19'):
        assemblies.append(assembly)
        emit('\nLOADED ASSEMBLY ' + str(assembly.FullName))
        try:
            all_types.extend(list(assembly.GetExportedTypes()))
        except Exception:
            emit('TYPE LOAD ERROR\n' + traceback.format_exc())

# Target classes/interfaces around Named Selections and groups.
seen = set()
exact_names = set([
    'SpaceClaim.Api.V19.Group',
    'SpaceClaim.Api.V19.IGroup',
    'SpaceClaim.Api.V19.GroupFolder',
    'SpaceClaim.Api.V19.Selection',
    'SpaceClaim.Api.V19.Scripting.Selection.Selection',
    'SpaceClaim.Api.V19.Scripting.Selection.ISelection',
    'SpaceClaim.Api.V19.Scripting.Commands.NamedSelection',
])

for t in all_types:
    full = str(t.FullName)
    short = str(t.Name)
    low = full.lower()
    wanted = full in exact_names
    if 'namedselection' in low:
        wanted = True
    if short in ('Group', 'IGroup', 'GroupFolder'):
        wanted = True
    if full.startswith('SpaceClaim.Api.V19.Scripting.Commands.') and ('Group' in short or 'Selection' in short):
        wanted = True
    if full.startswith('SpaceClaim.Api.V19.Scripting.Selection.'):
        wanted = True
    if wanted and full not in seen:
        seen.add(full)
        try:
            describe_type(t, include_inherited=False)
        except Exception:
            emit('DESCRIBE ERROR ' + full + '\n' + traceback.format_exc())

# A second filtered pass catches helper/command types whose names do not contain
# NamedSelection but expose methods capable of changing Group membership.
emit('\n\n=== REPAIR-RELEVANT METHODS ON GROUP/SELECTION RELATED TYPES ===')
for t in all_types:
    full = str(t.FullName)
    short = str(t.Name)
    low = full.lower()
    if not (('group' in low) or ('selection' in low) or ('named' in low)):
        continue
    relevant = []
    try:
        for method in t.GetMethods(flags_declared):
            if method.IsSpecialName:
                continue
            if method_is_repair_relevant(method):
                relevant.append(method)
    except Exception:
        continue
    if relevant:
        emit('\nMETHOD OWNER ' + full)
        for method in relevant:
            emit(('STATIC ' if method.IsStatic else 'INSTANCE ') + str(method))

# Inspect the actual runtime type of one existing Group including inherited
# public members. This is often the highest-value part of the report.
try:
    root2 = GetRootPart()
    groups2 = NamedSelection.GetGroups(root2)
    if len(groups2) > 0:
        runtime_type = groups2[0].GetType()
        emit('\n\n=== ACTUAL EXISTING GROUP RUNTIME TYPE - ALL PUBLIC MEMBERS ===')
        describe_type(runtime_type, include_inherited=True)
    else:
        emit('\nNO EXISTING GROUPS: runtime Group type could not be sampled.')
except Exception:
    emit('\nRUNTIME GROUP INSPECTION ERROR\n' + traceback.format_exc())

# Explicitly dump the runtime CLR type behind the scripting NamedSelection symbol
# if IronPython can resolve it. No methods are invoked here.
try:
    nt = clr.GetClrType(NamedSelection)
    emit('\n\n=== clr.GetClrType(NamedSelection) ===')
    describe_type(nt, include_inherited=True)
except Exception:
    emit('\nclr.GetClrType(NamedSelection) ERROR\n' + traceback.format_exc())

path = os.path.join(tempfile.gettempdir(), 'SpaceClaim_Weld_NamedSelection_Repair_API_V19.txt')
try:
    with io.open(path, 'w', encoding='utf-8') as stream:
        try:
            text = u'\n'.join(unicode(x) for x in lines)
        except NameError:
            text = '\n'.join(str(x) for x in lines)
        stream.write(text)
    print('Repair API report saved: ' + path)
    print('Types inspected: %d. No model changes.' % len(seen))
except Exception:
    print(traceback.format_exc())
    for line in lines:
        print(line)
