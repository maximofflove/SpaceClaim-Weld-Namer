# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# SpaceClaim Weld Namer 0.6 REOPEN FIX - IronPython 2.7, SpaceClaim script editor.
import re
import sys
import traceback

MAX_PAIR = 99999999

def next_name(names, maximum=MAX_PAIR):
    occupied = set()
    for value in names:
        match = re.match(r'^w([1-9][0-9]*)([ab])$', str(value).lower())
        if match:
            number = int(match.group(1))
            if number <= maximum:
                occupied.add(2 * (number - 1) + (match.group(2) == 'b'))
    index = 0
    while index in occupied:
        index += 1
    if index >= maximum * 2:
        raise ValueError('All weld names are occupied.')
    return 'w%d%s' % (index // 2 + 1, 'ab'[index % 2])

def context():
    root = GetRootPart()
    if root is None:
        raise ValueError('Open a SpaceClaim design first.')
    if GetActivePart() != root:
        raise ValueError('Activate the ROOT component before creating weld groups.')
    return root

def runtime_type(owner):
    # IronPython exposes a CLR class as PythonType. Calling its inherited
    # Object.GetType() without an instance raises "takes exactly 1 argument".
    try:
        return clr.GetClrType(owner)
    except TypeError:
        return owner.GetType()

def all_groups(root):
    # Confirmed in the user's V19 log: GetGroups(SpaceClaim.Api.V19.IPart).
    # Do not call parameterless GetGroups(): it failed from the modeless callback.
    if root is None:
        raise ValueError('Open a design and activate its root component.')
    log_event('GROUPS: call NamedSelection.GetGroups(root)')
    groups = NamedSelection.GetGroups(root)
    if groups is None:
        raise RuntimeError('GetGroups(root) returned null. No group will be created.')
    result = list(groups)
    for group in result:
        if not hasattr(group, 'Name'):
            raise RuntimeError('GetGroups(root) returned an object without Name.')
    log_event('GROUPS: returned %d groups' % len(result))
    return result

def validate_items(items, mode):
    if mode not in ('Faces', 'Edges'):
        raise ValueError('Choose Faces or Edges.')
    if not items:
        raise ValueError('Select one or more %s in the model first.' % mode.lower())
    allowed = ('DesignFace', 'IDesignFace', 'DesignFaceGeneral') if mode == 'Faces' else (
               'DesignEdge', 'IDesignEdge', 'DesignEdgeGeneral')
    for item in items:
        metadata = item.GetType()
        names = [metadata.Name] + [t.Name for t in metadata.GetInterfaces()]
        if not any(name in allowed for name in names):
            raise ValueError('%s mode: select only %s. Current type: %s' %
                             (mode, mode.lower(), metadata.Name))

def names_in(root):
    return [str(group.Name) for group in all_groups(root)]

def log_creation_signatures():
    # Read-only diagnostics for the next stage; no alternate mutation is retried.
    try:
        for method in runtime_type(NamedSelection).GetMethods():
            if method.Name in ('Create', 'Rename'):
                log_event('API SIGNATURE: ' + str(method))
    except Exception:
        log_event('Signature diagnostics unavailable: ' + traceback.format_exc())

def create_next(mode="Faces"):
    log_event('CREATE: begin')
    root = context()
    log_event('CREATE: read selection')
    selection = Selection.GetActive()
    items = list(selection.Items)
    validate_items(items, mode)
    log_event('CREATE: read groups before')
    before = all_groups(root)
    target = next_name([str(g.Name) for g in before])
    # Create once only. Never retry a mutation with another signature.
    log_event('CREATE: call NamedSelection.Create | target=' + target)
    log_creation_signatures()
    NamedSelection.Create(selection, Selection.Empty())
    log_event('CREATE: NamedSelection.Create returned')
    after = all_groups(root)
    added = [g for g in after if g not in before]
    if len(added) != 1:
        raise RuntimeError('Creation could not be verified. Inspect Groups before retrying; a default group may exist.')
    new_group = added[0]
    temporary_name = str(new_group.Name)
    if sum(str(g.Name).lower() == temporary_name.lower() for g in after) != 1:
        raise RuntimeError('Default group name is ambiguous. Rename the new group manually to ' + target)
    # Recheck before rename; existing names are never overwritten.
    if target.lower() in [str(g.Name).lower() for g in after if g != new_group]:
        raise RuntimeError('Name became occupied. Inspect the new default group before retrying.')
    try:
        log_event('CREATE: call NamedSelection.Rename')
        NamedSelection.Rename(temporary_name, target)
        log_event('CREATE: NamedSelection.Rename returned')
        if str(new_group.Name) != target:
            raise RuntimeError('Rename was not confirmed.')
    except Exception:
        raise RuntimeError('New group "%s" exists, but rename to "%s" failed. Inspect Groups before retrying.\n%s' %
                           (temporary_name, target, traceback.format_exc()))
    return 'Created %s | %s: %d | Next: %s' % (target, mode, len(items), next_name(names_in(root)))


import clr
from System.Threading import Thread
import os
import tempfile
import io
import datetime

LOG_PATH = os.path.join(tempfile.gettempdir(), 'SpaceClaim_Weld_Namer_v06.log')

def log_event(text):
    # Logging must not call the script editor from a UI callback.
    try:
        with io.open(LOG_PATH, 'a', encoding='utf-8') as stream:
            stream.write(u'%s | thread %s | %s\n' %
                         (datetime.datetime.now().isoformat(),
                          Thread.CurrentThread.ManagedThreadId, text))
    except Exception:
        pass



# Set to 'Edges' for shell edges. Run once only.
SELECTION_MODE = 'Faces'
try:
    print(create_next(SELECTION_MODE))
except ValueError as error:
    print(str(error))
except Exception:
    log_event(traceback.format_exc())
    print(traceback.format_exc())
