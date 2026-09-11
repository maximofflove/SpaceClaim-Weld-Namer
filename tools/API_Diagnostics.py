# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# Read only. Run once, then copy Output if group access still fails.
import clr
import traceback

def runtime_type(owner):
    try:
        return clr.GetClrType(owner)
    except TypeError:
        return owner.GetType()

root = GetRootPart()
document = getattr(root, 'Document', None)
if document is None:
    try:
        document = Window.ActiveWindow.Document
    except Exception:
        print(traceback.format_exc())
for label, obj in [('RootPart', root), ('Document', document), ('NamedSelection', NamedSelection)]:
    print('--- ' + label + ' ---')
    if obj is None:
        print('None')
        continue
    try:
        metadata = runtime_type(obj)
        print('CLR type: ' + str(metadata.FullName))
        print('Relevant members: ' + ', '.join(n for n in dir(obj)
              if any(w in n.lower() for w in ('group', 'select', 'document'))))
        for method in metadata.GetMethods():
            if any(w in method.Name.lower() for w in ('group', 'select', 'create', 'rename')):
                print(('STATIC ' if method.IsStatic else 'INSTANCE ') + str(method))
        if hasattr(obj, 'Groups'):
            print('Groups count: %d' % len(list(obj.Groups)))
    except Exception:
        print(traceback.format_exc())
print('--- Create / Rename help ---')
print(NamedSelection.Create.__doc__)
print(NamedSelection.Rename.__doc__)

print('--- Explicit root group access ---')
try:
    groups = NamedSelection.GetGroups(root)
    if groups is None:
        print('ERROR: GetGroups(root) returned null')
    else:
        groups = list(groups)
        print('Root groups: %d' % len(groups))
        for group in groups:
            print(str(group.Name))
except Exception:
    print(traceback.format_exc())

print('--- Secondary highlight support ---')
try:
    probe = Selection.Empty()
    metadata = probe.GetType()
    found = False
    for method in metadata.GetMethods():
        if 'Secondary' in method.Name or 'Active' in method.Name:
            print(('STATIC ' if method.IsStatic else 'INSTANCE ') + str(method))
            if method.Name == 'SetActiveSecondary':
                found = True
    print('SetActiveSecondary available: ' + str(found))
except Exception:
    print(traceback.format_exc())
