# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# SpaceClaim Named Selection Namer 0.13.1 - IronPython 2.7, SpaceClaim script editor.
import re
import sys
import traceback

MAX_PAIR = 99999999
BOLT_MAX_PAIR = 999999
FACE_MESH_MAX = 999999999
WELD_MODE = 'Weld pair (w)'
BOLT_MODE = 'Bolt pair (f)'
FACE_MESH_MODE = 'Face Meshing (fm)'

def next_group_name(names, purpose):
    if purpose == WELD_MODE:
        return next_name(names)
    if purpose == BOLT_MODE:
        pattern = re.compile(r'^f([1-9][0-9]*)([ab])$', re.I)
        occupied = set()
        for value in names:
            match = pattern.match(str(value))
            if match:
                number = int(match.group(1))
                if number <= BOLT_MAX_PAIR:
                    occupied.add(2 * (number - 1) + (match.group(2).lower() == 'b'))
        index = 0
        while index in occupied:
            index += 1
        if index >= 2 * BOLT_MAX_PAIR:
            raise ValueError('All bolt names are occupied.')
        return 'f%d%s' % (index // 2 + 1, 'ab'[index % 2])
    if purpose == FACE_MESH_MODE:
        pattern = re.compile(r'^fm([1-9][0-9]*)$', re.I)
        occupied = set()
        for value in names:
            match = pattern.match(str(value))
            if match:
                number = int(match.group(1))
                if number <= FACE_MESH_MAX:
                    occupied.add(number)
        number = 1
        while number in occupied:
            number += 1
        if number > FACE_MESH_MAX:
            raise ValueError('All Face Meshing names are occupied.')
        return 'fm%d' % number
    raise ValueError('Select a Named Selection purpose.')

def geometry_mode(purpose, weld_mode):
    if purpose == WELD_MODE:
        return weld_mode
    if purpose == BOLT_MODE:
        return 'Edges'
    if purpose == FACE_MESH_MODE:
        return 'Faces'
    raise ValueError('Select a Named Selection purpose.')

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
    try:
        groups = NamedSelection.GetGroups(root)
        if groups is None:
            raise RuntimeError('GetGroups(root) returned null.')
        result = list(groups)
    except Exception:
        # The scripting command may lose its document context in a modeless
        # WinForms callback. Read the same root part through the document API.
        log_event('GROUPS: scripting API failed; trying root.GetChildren[Group](): '
                  + traceback.format_exc())
        try:
            from SpaceClaim.Api.V19 import Group
            result = list(root.GetChildren[Group]())
        except Exception:
            log_event('GROUPS: document API failed: ' + traceback.format_exc())
            raise RuntimeError('Cannot read Named Selection groups from the active root part. '
                               'No group was created. Close the Namer window, activate the '
                               'root component, run the script again, and send the log: ' + LOG_PATH)
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




def _item_type_names(item):
    metadata = item.GetType()
    return [metadata.Name] + [t.Name for t in metadata.GetInterfaces()]

def _is_weld_face_item(item):
    names = _item_type_names(item)
    return any(name in ('DesignFace', 'IDesignFace', 'DesignFaceGeneral') for name in names)

def _is_weld_edge_item(item):
    names = _item_type_names(item)
    return any(name in ('DesignEdge', 'IDesignEdge', 'DesignEdgeGeneral') for name in names)

def weld_group_geometry_by_side(root):
    # Return exact Named Selection geometry split by suffix.  Side A keeps the
    # proven SpaceClaim Secondary Selection.  Side B is rendered separately by
    # a temporary red Display.Graphic, so CAD appearance is not modified.
    a_names, a_items = [], []
    b_names, b_items = [], []
    for group in all_groups(root):
        name = str(group.Name)
        match = re.match(r'^w[1-9][0-9]*([ab])$', name.lower())
        if match is None:
            continue
        sel = Selection.CreateByGroups(name)
        if sel is None:
            log_event('HIGHLIGHT WARNING: %s returned null selection' % name)
            continue
        group_items = list(sel.Items)
        if not group_items:
            log_event('HIGHLIGHT WARNING: %s contains no selectable geometry' % name)
            continue
        if match.group(1) == 'a':
            a_names.append(name)
            a_items.extend(group_items)
        else:
            b_names.append(name)
            b_items.extend(group_items)
    return a_names, a_items, b_names, b_items

def _graphics_equal(left, right):
    if left is right:
        return True
    if left is None or right is None:
        return False
    try:
        return bool(left.Equals(right))
    except Exception:
        return False

def _windows_equal(left, right):
    if left is right:
        return True
    if left is None or right is None:
        return False
    try:
        return bool(left.Equals(right))
    except Exception:
        return False

def _edge_key(edge):
    try:
        return 'M:' + str(edge.Moniker)
    except Exception:
        try:
            return 'E:' + str(edge.ExportIdentifier)
        except Exception:
            return 'O:' + str(edge)

def _curve_primitive_for_edge(edge):
    # API V19 reflection on the user's installation confirms:
    #   DesignEdge.Shape -> Modeler.Edge
    #   Modeler.Edge implements Geometry.ITrimmedCurve
    #   Display.CurvePrimitive.Create(ITrimmedCurve)
    candidates = []
    try:
        candidates.append(edge.Shape)
    except Exception:
        pass
    candidates.append(edge)
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            return CurvePrimitive.Create(candidate)
        except Exception:
            pass
    return None

def red_primitives_from_items(items):
    # Edges are drawn directly.  For a face Named Selection, draw the exact
    # boundary edges of that face in red.  This avoids recoloring the parent body.
    primitives = []
    seen_edges = set()
    skipped = 0
    for item in items:
        edges = []
        try:
            if _is_weld_face_item(item):
                edges = list(item.Edges)
            elif _is_weld_edge_item(item):
                edges = [item]
            else:
                # Defensive fallback for API wrappers that still expose Edges.
                candidate_edges = getattr(item, 'Edges', None)
                if candidate_edges is not None:
                    edges = list(candidate_edges)
                else:
                    edges = [item]
        except Exception:
            edges = [item]
        for edge in edges:
            key = _edge_key(edge)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            primitive = _curve_primitive_for_edge(edge)
            if primitive is None:
                skipped += 1
                continue
            primitives.append(primitive)
    return primitives, skipped

def _style_show_always(style):
    # ShowWhen has an enum member literally named "None" in V19.  getattr is
    # required because None is a Python keyword.
    try:
        style.ShowWhen = getattr(ShowWhen, 'None')
    except Exception:
        pass

def _make_red_graphic(items):
    primitives, skipped = red_primitives_from_items(items)
    if not primitives:
        return None, 0, skipped
    style = GraphicStyle()
    _style_show_always(style)
    style.LineColor = Color.Red
    style.LineWidth = Single(4.0)
    style.IsSelectable = False
    style.EnableDepthBuffer = True
    graphic = Graphic.Create(style, Array[Primitive](primitives))
    return graphic, len(primitives), skipped

def _compose_overlay_graphics(graphics):
    active = [graphic for graphic in graphics if graphic is not None]
    if not active:
        return None
    if len(active) == 1:
        return active[0]
    style = GraphicStyle()
    _style_show_always(style)
    style.IsSelectable = False
    return Graphic.Create(style, Array[Primitive]([]), Array[Graphic](active))

def _clear_overlay_window(window):
    # Confirmed in the user's SpaceClaim 2021 R1 / API V19 test:
    # the Window.Rendering getter may throw when the custom-rendering slot is
    # empty, but assigning a Graphic (or None) and RefreshRendering() works.
    # Never read Window.Rendering here.
    if window is None:
        return False
    try:
        if window.IsDeleted:
            return False
    except Exception:
        pass
    try:
        log_event('OVERLAY: direct clear Window.Rendering=None (getter avoided)')
        window.Rendering = None
        window.RefreshRendering()
        return True
    except Exception:
        log_event('OVERLAY CLEAR ERROR: ' + traceback.format_exc())
        return False

def _apply_overlay_state(state):
    if state is None:
        return
    window = state.get('window')
    if window is None:
        return
    combined = _compose_overlay_graphics([state.get('red'), state.get('problem')])
    try:
        if combined is None:
            log_event('OVERLAY: assign None | getter avoided')
            window.Rendering = None
        else:
            log_event('OVERLAY: direct assign combined Window.Rendering | getter avoided')
            window.Rendering = combined
        window.RefreshRendering()
        log_event('OVERLAY: RefreshRendering returned')
    except Exception:
        log_event('OVERLAY APPLY ERROR: ' + traceback.format_exc())
        raise

def _get_overlay_state_for_active_window():
    window = SCWindow.ActiveWindow
    if window is None:
        raise RuntimeError('SpaceClaim active graphics window is unavailable.')
    state = AppDomain.CurrentDomain.GetData(COLOR_STATE_KEY)
    if state is None:
        state = {'window': window, 'red': None, 'problem': None,
                 'red_count': 0, 'problem_count': 0}
        AppDomain.CurrentDomain.SetData(COLOR_STATE_KEY, state)
        return state
    old_window = state.get('window')
    if old_window is not None and not _windows_equal(old_window, window):
        _clear_overlay_window(old_window)
        state = {'window': window, 'red': None, 'problem': None,
                 'red_count': 0, 'problem_count': 0}
        AppDomain.CurrentDomain.SetData(COLOR_STATE_KEY, state)
    return state

def clear_red_weld_overlay():
    state = AppDomain.CurrentDomain.GetData(COLOR_STATE_KEY)
    if state is None:
        return 0
    count = int(state.get('red_count', 0))
    state['red'] = None
    state['red_count'] = 0
    _apply_overlay_state(state)
    if state.get('problem') is None:
        AppDomain.CurrentDomain.SetData(COLOR_STATE_KEY, None)
    log_event('RED OVERLAY: cleared | primitives=%d' % count)
    return count

def set_red_weld_overlay(items):
    red_graphic, primitive_count, skipped = _make_red_graphic(items)
    state = _get_overlay_state_for_active_window()
    state['red'] = red_graphic
    state['red_count'] = primitive_count
    _apply_overlay_state(state)
    log_event('RED OVERLAY: applied | source_items=%d | primitives=%d | skipped=%d' %
              (len(items), primitive_count, skipped))
    return primitive_count

def _make_problem_graphic(items):
    primitives, skipped = red_primitives_from_items(items)
    if not primitives:
        return None, 0, skipped
    style = GraphicStyle()
    _style_show_always(style)
    style.LineColor = Color.Orange
    style.LineWidth = Single(6.0)
    style.IsSelectable = False
    style.EnableDepthBuffer = True
    graphic = Graphic.Create(style, Array[Primitive](primitives))
    return graphic, len(primitives), skipped

def set_problem_overlay(items):
    graphic, primitive_count, skipped = _make_problem_graphic(items)
    state = _get_overlay_state_for_active_window()
    state['problem'] = graphic
    state['problem_count'] = primitive_count
    _apply_overlay_state(state)
    log_event('PROBLEM OVERLAY: applied | source_items=%d | primitives=%d | skipped=%d' %
              (len(items), primitive_count, skipped))
    return primitive_count

def clear_problem_highlight():
    state = AppDomain.CurrentDomain.GetData(COLOR_STATE_KEY)
    if state is None:
        return 0
    count = int(state.get('problem_count', 0))
    state['problem'] = None
    state['problem_count'] = 0
    _apply_overlay_state(state)
    if state.get('red') is None:
        AppDomain.CurrentDomain.SetData(COLOR_STATE_KEY, None)
    log_event('PROBLEM OVERLAY: cleared | primitives=%d' % count)
    return count

def weld_group_geometry(root):
    # Exact geometry from all Weld Namer groups.  We deliberately use SpaceClaim's
    # secondary-selection highlight instead of changing CAD appearance.  In V19,
    # an edge color override belongs to the parent solid/surface, so it cannot
    # reliably mark only the topological edges stored in each weld group.
    group_names = []
    items = []
    for group in all_groups(root):
        name = str(group.Name)
        if not re.match(r'^w[1-9][0-9]*[ab]$', name.lower()):
            continue
        sel = Selection.CreateByGroups(name)
        if sel is None:
            log_event('HIGHLIGHT WARNING: %s returned null selection' % name)
            continue
        group_items = list(sel.Items)
        if not group_items:
            log_event('HIGHLIGHT WARNING: %s contains no selectable geometry' % name)
            continue
        group_names.append(name)
        items.extend(group_items)
    return group_names, items

def highlight_weld_groups(root, clear_primary=False):
    clear_problem_highlight()
    a_names, a_items, b_names, b_items = weld_group_geometry_by_side(root)
    if clear_primary:
        # After Create Next the just-created edges are still the primary selection.
        Selection.Empty().SetActive()
    if a_items:
        Selection.Create(a_items).SetActiveSecondary()
    else:
        Selection.Empty().SetActiveSecondary()
    red_primitives = set_red_weld_overlay(b_items)
    total_groups = len(a_names) + len(b_names)
    total_items = len(a_items) + len(b_items)
    log_event('HIGHLIGHT: groups=%d | items=%d | clear_primary=%s' %
              (total_groups, total_items, str(bool(clear_primary))))
    log_event('HIGHLIGHT AB: A groups=%d/items=%d secondary | B groups=%d/items=%d red_primitives=%d' %
              (len(a_names), len(a_items), len(b_names), len(b_items), red_primitives))
    return total_groups, total_items

def clear_weld_highlight():
    Selection.Empty().SetActiveSecondary()
    red_count = clear_red_weld_overlay()
    log_event('HIGHLIGHT: secondary selection and red B overlay cleared | red_primitives=%d' % red_count)

def pair_number_from_name(name):
    match = re.match(r'^w([1-9][0-9]*)([ab])$', str(name).lower())
    if match is None:
        raise ValueError('Not a Weld Namer group: ' + str(name))
    return int(match.group(1))

def current_pair_from_names(names):
    # Define the current pair relative to the first free sequential weld name.
    # Examples:
    #   w1a present                 -> next w1b -> current pair 1
    #   w1a,w1b present             -> next w2a -> current pair 1
    #   only w1b present            -> next w1a -> current pair 1 (gap pair)
    #   no weld groups              -> next w1a -> no current pair
    lowered = set(str(value).lower() for value in names)
    target = next_name(names)
    match = re.match(r'^w([1-9][0-9]*)([ab])$', target)
    number = int(match.group(1))
    suffix = match.group(2)
    if suffix == 'b':
        return number, target
    if ('w%db' % number) in lowered:
        return number, target
    if number > 1:
        return number - 1, target
    return None, target

def geometry_for_group_names(root, requested_names):
    # Resolve case-insensitively, but pass the actual stored group name to
    # Selection.CreateByGroups(). This keeps existing mixed-case groups usable.
    actual_by_lower = {}
    for group in all_groups(root):
        actual_by_lower[str(group.Name).lower()] = str(group.Name)
    found_names = []
    items = []
    for requested in requested_names:
        actual = actual_by_lower.get(str(requested).lower())
        if actual is None:
            continue
        sel = Selection.CreateByGroups(actual)
        if sel is None:
            log_event('HIGHLIGHT WARNING: %s returned null selection' % actual)
            continue
        group_items = list(sel.Items)
        if not group_items:
            log_event('HIGHLIGHT WARNING: %s contains no selectable geometry' % actual)
            continue
        found_names.append(actual)
        items.extend(group_items)
    return found_names, items

def highlight_pair(root, pair_number, clear_primary=False):
    clear_problem_highlight()
    if pair_number is None or pair_number < 1:
        Selection.Empty().SetActiveSecondary()
        clear_red_weld_overlay()
        log_event('HIGHLIGHT PAIR: none | clear_primary=%s' % str(bool(clear_primary)))
        return 0, 0

    a_requested = ['w%da' % pair_number]
    b_requested = ['w%db' % pair_number]
    a_names, a_items = geometry_for_group_names(root, a_requested)
    b_names, b_items = geometry_for_group_names(root, b_requested)
    if clear_primary:
        Selection.Empty().SetActive()
    if a_items:
        Selection.Create(a_items).SetActiveSecondary()
    else:
        Selection.Empty().SetActiveSecondary()
    red_primitives = set_red_weld_overlay(b_items)
    total_groups = len(a_names) + len(b_names)
    total_items = len(a_items) + len(b_items)
    log_event('HIGHLIGHT PAIR: w%d | groups=%d | items=%d | clear_primary=%s' %
              (pair_number, total_groups, total_items, str(bool(clear_primary))))
    log_event('HIGHLIGHT PAIR AB: w%d | A groups=%d/items=%d secondary | B groups=%d/items=%d red_primitives=%d' %
              (pair_number, len(a_names), len(a_items), len(b_names), len(b_items), red_primitives))
    return total_groups, total_items

def highlight_current_pair(root, clear_primary=False):
    pair_number, target = current_pair_from_names(names_in(root))
    groups, items = highlight_pair(root, pair_number, clear_primary)
    return pair_number, groups, items, target

def current_bolt_pair_from_names(names):
    target = next_group_name(names, BOLT_MODE)
    match = re.match(r'^f([1-9][0-9]*)([ab])$', target)
    number = int(match.group(1))
    if match.group(2) == 'b' or ('f%db' % number) in set(str(n).lower() for n in names):
        return number, target
    return (number - 1 if number > 1 else None), target

def highlight_bolt_pair(root, number, clear_primary=False):
    clear_problem_highlight()
    if clear_primary:
        Selection.Empty().SetActive()
    if number is None:
        Selection.Empty().SetActiveSecondary()
        clear_red_weld_overlay()
        return 0, 0
    a_names, a_items = geometry_for_group_names(root, ['f%da' % number])
    b_names, b_items = geometry_for_group_names(root, ['f%db' % number])
    if a_items:
        Selection.Create(a_items).SetActiveSecondary()
    else:
        Selection.Empty().SetActiveSecondary()
    set_red_weld_overlay(b_items)
    log_event('BOLT HIGHLIGHT: f%d | A=%d items | B=%d items' %
              (number, len(a_items), len(b_items)))
    return len(a_names) + len(b_names), len(a_items) + len(b_items)

def highlight_all_bolt_groups(root, clear_primary=False):
    clear_problem_highlight()
    if clear_primary:
        Selection.Empty().SetActive()
    a_names, a_items, b_names, b_items = [], [], [], []
    for group in all_groups(root):
        name = str(group.Name)
        match = re.match(r'^f[1-9][0-9]*([ab])$', name, re.I)
        if not match:
            continue
        selected = Selection.CreateByGroups(name)
        items = [] if selected is None else list(selected.Items)
        if not items:
            log_event('BOLT HIGHLIGHT WARNING: %s contains no selectable geometry' % name)
            continue
        if match.group(1).lower() == 'a':
            a_names.append(name)
            a_items.extend(items)
        else:
            b_names.append(name)
            b_items.extend(items)
    if a_items:
        Selection.Create(a_items).SetActiveSecondary()
    else:
        Selection.Empty().SetActiveSecondary()
    set_red_weld_overlay(b_items)
    return len(a_names) + len(b_names), len(a_items) + len(b_items)

def face_mesh_names(root):
    result = []
    for group in all_groups(root):
        name = str(group.Name)
        match = re.match(r'^fm([1-9][0-9]*)$', name, re.I)
        if match and int(match.group(1)) <= FACE_MESH_MAX:
            result.append((int(match.group(1)), name))
    return result

def highlight_face_mesh_groups(root, requested_names, clear_primary=False):
    clear_problem_highlight()
    if clear_primary:
        Selection.Empty().SetActive()
    found, items = geometry_for_group_names(root, requested_names)
    if items:
        Selection.Create(items).SetActiveSecondary()
    else:
        Selection.Empty().SetActiveSecondary()
    clear_red_weld_overlay()
    log_event('FACE MESH HIGHLIGHT: groups=%d | items=%d' % (len(found), len(items)))
    return len(found), len(items)


def _doc_item_key(item):
    try:
        return 'M:' + str(item.Moniker)
    except Exception:
        pass
    try:
        return 'E:' + str(item.ExportIdentifier)
    except Exception:
        pass
    return 'O:' + str(item.GetType().FullName) + ':' + str(item)

def _geometry_kind(items):
    if not items:
        return 'Empty'
    kinds = set()
    for item in items:
        if _is_weld_edge_item(item):
            kinds.add('Edges')
        elif _is_weld_face_item(item):
            kinds.add('Faces')
        else:
            kinds.add('Other')
    if len(kinds) == 1:
        return list(kinds)[0]
    return 'Mixed'

def _geometry_metric(items, kind):
    # Metric is used only as a relative A/B screening value.  No display-unit
    # assumption is made.  For Edges it is total curve length; for Faces total area.
    total = 0.0
    if kind == 'Edges':
        for item in items:
            value = None
            try:
                value = item.Shape.Length
            except Exception:
                try:
                    value = item.Length
                except Exception:
                    pass
            if value is None:
                return None
            total += float(value)
        return total
    if kind == 'Faces':
        for item in items:
            value = None
            try:
                value = item.Area
            except Exception:
                try:
                    value = item.Shape.Area
                except Exception:
                    pass
            if value is None:
                return None
            total += float(value)
        return total
    return None

def _relative_difference_percent(a, b):
    if a is None or b is None:
        return None
    scale = max(abs(float(a)), abs(float(b)))
    if scale <= 1.0e-15:
        return 0.0
    return abs(float(a) - float(b)) / scale * 100.0

def validate_weld_named_selections(root, metric_tolerance_percent=10.0):
    # Read-only QA screening.  The metric tolerance is deliberately a screening
    # criterion, not a weld acceptance criterion: partition counts may legitimately
    # differ while total edge length / face area remains comparable.
    groups = all_groups(root)
    weld_groups = []
    group_names_lower = {}
    geometry_cache = {}
    usage = {}

    for group in groups:
        name = str(group.Name)
        lower = name.lower()
        match = re.match(r'^w([1-9][0-9]*)([ab])$', lower)
        if match is None:
            continue
        number = int(match.group(1))
        side = match.group(2)
        weld_groups.append((number, side, name))
        group_names_lower.setdefault(lower, []).append(name)
        try:
            sel = Selection.CreateByGroups(name)
            items = [] if sel is None else list(sel.Items)
        except Exception:
            items = []
            log_event('QA WARNING: failed to resolve geometry for %s: %s' % (name, traceback.format_exc()))
        geometry_cache[lower] = items
        for item in items:
            key = _doc_item_key(item)
            usage.setdefault(key, set()).add(lower)

    by_pair = {}
    for number, side, name in weld_groups:
        by_pair.setdefault(number, {})[side] = name

    # Whole-pair sequence gaps are useful QA findings, but MAX_PAIR is very large.
    # Never expand an accidental high-number group into millions of table rows.
    # Enumerate at most 1000 missing pair numbers; larger gaps are summarized on
    # the first existing pair after the gap.
    pair_numbers = sorted(by_pair.keys())
    validation_numbers = set(pair_numbers)
    gap_annotations = {}
    gap_budget = 1000
    previous = 0
    for existing_number in pair_numbers:
        gap_count = existing_number - previous - 1
        if gap_count > 0:
            if gap_count <= gap_budget:
                for missing_number in range(previous + 1, existing_number):
                    validation_numbers.add(missing_number)
                gap_budget -= gap_count
            else:
                gap_annotations[existing_number] = (previous + 1, existing_number - 1)
                gap_budget = 0
        previous = existing_number

    records = []
    for number in sorted(validation_numbers):
        names = by_pair.get(number, {})
        a_name = names.get('a')
        b_name = names.get('b')
        a_items = geometry_cache.get(a_name.lower(), []) if a_name else []
        b_items = geometry_cache.get(b_name.lower(), []) if b_name else []
        a_kind = _geometry_kind(a_items)
        b_kind = _geometry_kind(b_items)
        reasons = []
        severity = 0  # 0 OK, 1 CHECK, 2 ERROR

        if number in gap_annotations:
            first_missing, last_missing = gap_annotations[number]
            severity = 2
            if first_missing == last_missing:
                reasons.append('Large sequence gap: missing w%d' % first_missing)
            else:
                reasons.append('Large sequence gap: missing w%d..w%d' %
                               (first_missing, last_missing))

        if a_name is None:
            severity = 2
            reasons.append('Missing A')
        if b_name is None:
            severity = 2
            reasons.append('Missing B')
        if a_name is not None and not a_items:
            severity = 2
            reasons.append('A empty/unresolved')
        if b_name is not None and not b_items:
            severity = 2
            reasons.append('B empty/unresolved')

        if a_items and a_kind in ('Mixed', 'Other'):
            severity = 2
            reasons.append('A geometry type: %s' % a_kind)
        if b_items and b_kind in ('Mixed', 'Other'):
            severity = 2
            reasons.append('B geometry type: %s' % b_kind)
        if a_items and b_items and a_kind != b_kind:
            severity = 2
            reasons.append('A/B type mismatch')

        a_metric = _geometry_metric(a_items, a_kind)
        b_metric = _geometry_metric(b_items, b_kind)
        metric_diff = None
        if a_items and b_items and a_kind == b_kind and a_kind in ('Edges', 'Faces'):
            metric_diff = _relative_difference_percent(a_metric, b_metric)
            if metric_diff is not None and metric_diff > float(metric_tolerance_percent):
                severity = max(severity, 1)
                label = 'length' if a_kind == 'Edges' else 'area'
                reasons.append('%s mismatch %.1f%% > %.1f%%' %
                               (label, metric_diff, float(metric_tolerance_percent)))

        # Object-count mismatch is shown in the table but is not automatically a
        # problem because one side of a weld may be split into more topological
        # edges/faces than the other.
        if a_items and b_items and len(a_items) != len(b_items):
            reasons.append('Count A/B %d/%d (info)' % (len(a_items), len(b_items)))

        own_groups = set()
        if a_name:
            own_groups.add(a_name.lower())
        if b_name:
            own_groups.add(b_name.lower())
        duplicate_external = set()
        duplicate_internal = False
        pair_keys = {}
        conflict_items = []
        conflict_item_keys = set()
        for side_name, side_items in ((a_name, a_items), (b_name, b_items)):
            if side_name is None:
                continue
            for item in side_items:
                key = _doc_item_key(item)
                pair_keys.setdefault(key, set()).add(side_name.lower())
                users = usage.get(key, set())
                external = users.difference(own_groups)
                if external:
                    duplicate_external.update(external)
                    if key not in conflict_item_keys:
                        conflict_item_keys.add(key)
                        conflict_items.append(item)
        for key, users in pair_keys.items():
            if len(users) > 1:
                duplicate_internal = True
                # Also expose the internally duplicated object for conflict highlight.
                if key not in conflict_item_keys:
                    for item in a_items + b_items:
                        if _doc_item_key(item) == key:
                            conflict_item_keys.add(key)
                            conflict_items.append(item)
                            break
        if duplicate_internal:
            severity = 2
            reasons.append('Same geometry used in A and B')
        if duplicate_external:
            severity = max(severity, 1)
            reasons.append('Geometry reused by other weld group(s)')

        # Case-insensitive duplicate group names are an error if the host permits them.
        duplicate_names = []
        for actual in (a_name, b_name):
            if actual is not None and len(group_names_lower.get(actual.lower(), [])) > 1:
                duplicate_names.append(actual)
        if duplicate_names:
            severity = 2
            reasons.append('Duplicate group name ignoring case')

        status = 'ERROR' if severity == 2 else ('CHECK' if severity == 1 else 'OK')
        problem_reasons = [r for r in reasons if not r.endswith('(info)')]
        info_reasons = [r for r in reasons if r.endswith('(info)')]
        reason_text = '; '.join(problem_reasons + info_reasons) if reasons else 'OK'
        records.append({
            'pair': number,
            'a_name': a_name or '',
            'b_name': b_name or '',
            'a_items': a_items,
            'b_items': b_items,
            'a_kind': a_kind,
            'b_kind': b_kind,
            'a_count': len(a_items),
            'b_count': len(b_items),
            'a_metric': a_metric,
            'b_metric': b_metric,
            'metric_diff': metric_diff,
            'status': status,
            'severity': severity,
            'reason': reason_text,
            'problem': severity > 0,
            'conflict_groups': sorted(list(duplicate_external)),
            'conflict_items': conflict_items,
            'duplicate_internal': duplicate_internal
        })

    log_event('QA VALIDATE: weld_groups=%d | pairs=%d | problems=%d | tolerance=%.1f%%' %
              (len(weld_groups), len(records), sum(1 for r in records if r['problem']),
               float(metric_tolerance_percent)))
    return records

def problem_geometry_from_records(records):
    items = []
    for record in records:
        if not record.get('problem'):
            continue
        items.extend(record.get('a_items', []))
        items.extend(record.get('b_items', []))
    return items

def highlight_problem_records(records):
    # Problem mode is intentionally visually exclusive: orange = screening issue.
    Selection.Empty().SetActiveSecondary()
    clear_red_weld_overlay()
    items = problem_geometry_from_records(records)
    count = set_problem_overlay(items) if items else 0
    log_event('QA HIGHLIGHT PROBLEMS: pairs=%d | items=%d | primitives=%d' %
              (sum(1 for r in records if r.get('problem')), len(items), count))
    return count

def clear_all_weld_overlays():
    Selection.Empty().SetActiveSecondary()
    red_count = clear_red_weld_overlay()
    problem_count = clear_problem_highlight()
    log_event('HIGHLIGHT: all overlays cleared | red=%d | problem=%d' %
              (red_count, problem_count))

def _repair_selection_items():
    selection = Selection.GetActive()
    if selection is None:
        raise ValueError('Select replacement geometry in the SpaceClaim graphics window first.')
    items = list(selection.Items)
    if not items:
        raise ValueError('Select one or more edges/faces in the SpaceClaim graphics window first.')
    kind = _geometry_kind(items)
    if kind not in ('Edges', 'Faces'):
        raise ValueError('Repair selection must contain only Edges or only Faces. Current type: %s' % kind)
    validate_items(items, kind)
    return items, kind

def _unique_items(items):
    result = []
    seen = set()
    for item in items:
        key = _doc_item_key(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result

def _actual_group_name(root, requested_name):
    requested_lower = str(requested_name).lower()
    matches = [str(g.Name) for g in all_groups(root) if str(g.Name).lower() == requested_lower]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        return None
    raise RuntimeError('Duplicate group names ignoring case: %s' % requested_name)

def _validate_repair_kind(items, expected_kind=None):
    kind = _geometry_kind(items)
    if kind not in ('Edges', 'Faces'):
        raise ValueError('Repair geometry must be all Edges or all Faces. Current type: %s' % kind)
    if expected_kind in ('Edges', 'Faces') and kind != expected_kind:
        raise ValueError('Geometry type mismatch: target expects %s, current selection is %s.' %
                         (expected_kind, kind))
    validate_items(items, kind)
    return kind

def _log_replace_signature():
    try:
        for method in runtime_type(NamedSelection).GetMethods():
            if method.Name == 'Replace':
                log_event('REPAIR API SIGNATURE: ' + str(method))
    except Exception:
        log_event('REPAIR signature diagnostics unavailable: ' + traceback.format_exc())

def replace_named_selection_geometry(root, group_name, new_items, expected_kind=None):
    actual = _actual_group_name(root, group_name)
    if actual is None:
        raise ValueError('Named Selection does not exist: ' + str(group_name))
    new_items = _unique_items(new_items)
    if not new_items:
        raise ValueError('Replacement geometry cannot be empty.')
    kind = _validate_repair_kind(new_items, expected_kind)
    expected_keys = set(_doc_item_key(item) for item in new_items)
    selection = Selection.Create(new_items)
    log_event('REPAIR REPLACE: begin | group=%s | kind=%s | items=%d' %
              (actual, kind, len(new_items)))
    _log_replace_signature()
    # Reflection from the user's real SpaceClaim 2021 R1 / API V19 installation
    # confirms NamedSelection.Replace(name, primary, secondary, ICommandInfo).
    # Like the already proven Create command, the scripting wrapper exposes the
    # final command-info argument as optional in IronPython.
    NamedSelection.Replace(actual, selection, Selection.Empty())
    log_event('REPAIR REPLACE: NamedSelection.Replace returned | group=' + actual)
    verify = Selection.CreateByGroups(actual)
    verified_items = [] if verify is None else list(verify.Items)
    verified_keys = set(_doc_item_key(item) for item in verified_items)
    if expected_keys != verified_keys:
        raise RuntimeError('Replace returned, but geometry verification failed for %s. Expected %d unique item(s), got %d.' %
                           (actual, len(expected_keys), len(verified_keys)))
    log_event('REPAIR REPLACE: verified | group=%s | items=%d' % (actual, len(verified_items)))
    return actual, len(verified_items), kind

def create_missing_named_selection(root, target, items, expected_kind=None):
    if _actual_group_name(root, target) is not None:
        raise ValueError('Named Selection already exists: ' + str(target))
    items = _unique_items(items)
    if not items:
        raise ValueError('Cannot create an empty Named Selection.')
    kind = _validate_repair_kind(items, expected_kind)
    selection = Selection.Create(items)
    before = all_groups(root)
    log_event('REPAIR CREATE MISSING: begin | target=%s | kind=%s | items=%d' %
              (target, kind, len(items)))
    NamedSelection.Create(selection, Selection.Empty())
    after = all_groups(root)
    added = [g for g in after if g not in before]
    if len(added) != 1:
        raise RuntimeError('Creation could not be verified. Inspect Groups before retrying.')
    new_group = added[0]
    temporary_name = str(new_group.Name)
    if _actual_group_name(root, target) is not None and str(new_group.Name).lower() != str(target).lower():
        raise RuntimeError('Target name became occupied: ' + str(target))
    if temporary_name != target:
        NamedSelection.Rename(temporary_name, target)
    if str(new_group.Name) != target:
        raise RuntimeError('Rename was not confirmed for new group ' + str(target))
    verify = Selection.CreateByGroups(target)
    verified = [] if verify is None else list(verify.Items)
    expected_keys = set(_doc_item_key(item) for item in items)
    verified_keys = set(_doc_item_key(item) for item in verified)
    if expected_keys != verified_keys:
        raise RuntimeError('Created %s, but geometry verification failed.' % target)
    log_event('REPAIR CREATE MISSING: verified | target=%s | items=%d' % (target, len(verified)))
    return target, len(verified), kind

def repair_expected_kind(record, side):
    own = record.get('%s_kind' % side.lower())
    other_side = 'b' if side.lower() == 'a' else 'a'
    other = record.get('%s_kind' % other_side)
    if own in ('Edges', 'Faces'):
        return own
    if other in ('Edges', 'Faces'):
        return other
    return None

def repair_existing_items(record, side):
    return list(record.get('%s_items' % side.lower(), []))

def repair_target_name(record, side):
    side = side.lower()
    existing = record.get('%s_name' % side)
    if existing:
        return existing
    return 'w%d%s' % (record['pair'], side)

def repair_merge_items(existing, selected):
    return _unique_items(list(existing) + list(selected))

def repair_remove_items(existing, selected):
    remove_keys = set(_doc_item_key(item) for item in selected)
    return [item for item in existing if _doc_item_key(item) not in remove_keys]

def create_next(mode="Faces", auto_highlight=True, purpose=WELD_MODE):
    log_event('CREATE: begin')
    mode = geometry_mode(purpose, mode)
    root = context()
    log_event('CREATE: read selection')
    selection = Selection.GetActive()
    items = list(selection.Items)
    validate_items(items, mode)
    log_event('CREATE: read groups before')
    before = all_groups(root)
    target = next_group_name([str(g.Name) for g in before], purpose)
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
    highlight_note = ' | Auto highlight: OFF'
    if auto_highlight:
        try:
            if purpose == WELD_MODE:
                pair_number = pair_number_from_name(target)
                group_count, item_count = highlight_pair(root, pair_number, True)
                highlighted = 'w%d' % pair_number
            elif purpose == BOLT_MODE:
                pair_number = int(re.match(r'^f([1-9][0-9]*)[ab]$', target).group(1))
                group_count, item_count = highlight_bolt_pair(root, pair_number, True)
                highlighted = 'f%d' % pair_number
            else:
                group_count, item_count = highlight_face_mesh_groups(root, [target], True)
                highlighted = target
            highlight_note = ' | Auto highlight: %s (%d groups / %d items)' % (
                highlighted, group_count, item_count)
        except Exception:
            log_event('HIGHLIGHT ERROR after create %s: %s' % (target, traceback.format_exc()))
            highlight_note = ' | Auto highlight: FAILED (group is OK)'
    return 'Created %s | %s: %d | Next: %s%s' % (target, mode, len(items),
               next_group_name(names_in(root), purpose), highlight_note)

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('SpaceClaim.Api.V19')
from System.Windows.Forms import Form, Button, Label, TextBox, CheckBox, FormBorderStyle, FormStartPosition, ScrollBars, ComboBox, ComboBoxStyle, DataGridView, DataGridViewSelectionMode, DataGridViewAutoSizeColumnsMode, DataGridViewColumnHeadersHeightSizeMode, DataGridViewTextBoxColumn, SaveFileDialog, DialogResult, MessageBox, MessageBoxButtons, MessageBoxIcon
from System.Drawing import Point, Size, Color
from System import Action, IntPtr, AppDomain, String, Array, Single, Object
from SpaceClaim.Api.V19 import Window as SCWindow
from SpaceClaim.Api.V19.Display import Graphic, GraphicStyle, CurvePrimitive, Primitive, ShowWhen
from System.Diagnostics import Process
from System.Threading import Thread, Monitor
from System.Windows.Forms import Control
import os
import tempfile
import io
import datetime

LOG_PATH = os.path.join(tempfile.gettempdir(), 'SpaceClaim_Weld_Namer_v012.log')
COLOR_STATE_KEY = 'MF.SpaceClaim.WeldNamer.v012.OverlayState'

def log_event(text):
    # Logging must not call the script editor from a UI callback.
    try:
        with io.open(LOG_PATH, 'a', encoding='utf-8') as stream:
            stream.write(u'%s | thread %s | %s\n' %
                         (datetime.datetime.now().isoformat(),
                          Thread.CurrentThread.ManagedThreadId, text))
    except Exception:
        pass



class NamedSelectionManagerForm(Form):
    def __init__(self, parent_form):
        Form.__init__(self)
        self.parent_form = parent_form
        self.Text = 'MF | Weld Named Selection QA / Repair Manager 0.12.1'
        self.ClientSize = Size(1080, 720)
        self.FormBorderStyle = FormBorderStyle.SizableToolWindow
        self.StartPosition = FormStartPosition.CenterParent
        self.TopMost = True
        self.ShowInTaskbar = False
        self.records = []
        self.metric_tolerance = 10.0

        self.info = Label()
        self.info.Text = ('QA screening + controlled repair. Orange = problem. A/B object-count differences are informational; '
                          'edge-length / face-area mismatch > 10% is CHECK. Repair uses current SpaceClaim selection.')
        self.info.Location = Point(12, 10)
        self.info.Size = Size(1045, 36)

        self.validate_btn = Button()
        self.validate_btn.Text = 'Validate All'
        self.validate_btn.Location = Point(12, 50)
        self.validate_btn.Size = Size(130, 32)
        self.validate_btn.Click += self.on_validate

        self.problems_only = CheckBox()
        self.problems_only.Text = 'Show Problems Only'
        self.problems_only.Location = Point(155, 55)
        self.problems_only.Size = Size(165, 24)
        self.problems_only.CheckedChanged += self.on_filter_changed

        self.highlight_problems_btn = Button()
        self.highlight_problems_btn.Text = 'Highlight Problems'
        self.highlight_problems_btn.Location = Point(335, 50)
        self.highlight_problems_btn.Size = Size(150, 32)
        self.highlight_problems_btn.Click += self.on_highlight_problems

        self.clear_problem_btn = Button()
        self.clear_problem_btn.Text = 'Clear Problem Highlight'
        self.clear_problem_btn.Location = Point(495, 50)
        self.clear_problem_btn.Size = Size(175, 32)
        self.clear_problem_btn.Click += self.on_clear_problem

        self.export_btn = Button()
        self.export_btn.Text = 'Export CSV'
        self.export_btn.Location = Point(680, 50)
        self.export_btn.Size = Size(120, 32)
        self.export_btn.Click += self.on_export

        self.grid = DataGridView()
        self.grid.Location = Point(12, 94)
        self.grid.Size = Size(1055, 350)
        self.grid.ReadOnly = True
        self.grid.AllowUserToAddRows = False
        self.grid.AllowUserToDeleteRows = False
        self.grid.MultiSelect = False
        self.grid.SelectionMode = DataGridViewSelectionMode.FullRowSelect
        self.grid.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
        self.grid.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.AutoSize
        self.grid.RowHeadersVisible = False
        self.grid.SelectionChanged += self.on_selection_changed
        for title in ('Weld', 'A', 'B', 'Type A', 'Type B', 'Count A', 'Count B', 'Metric diff %', 'Status', 'Reason'):
            column = DataGridViewTextBoxColumn()
            column.HeaderText = title
            column.Name = title
            if title in ('Weld', 'Count A', 'Count B', 'Metric diff %', 'Status'):
                column.FillWeight = 55
            elif title in ('A', 'B', 'Type A', 'Type B'):
                column.FillWeight = 70
            else:
                column.FillWeight = 200
            self.grid.Columns.Add(column)

        self.prev_btn = Button()
        self.prev_btn.Text = '< Previous Problem'
        self.prev_btn.Location = Point(12, 457)
        self.prev_btn.Size = Size(150, 34)
        self.prev_btn.Click += self.on_previous_problem

        self.next_btn = Button()
        self.next_btn.Text = 'Next Problem >'
        self.next_btn.Location = Point(172, 457)
        self.next_btn.Size = Size(150, 34)
        self.next_btn.Click += self.on_next_problem

        self.highlight_selected_btn = Button()
        self.highlight_selected_btn.Text = 'Highlight Selected Pair'
        self.highlight_selected_btn.Location = Point(337, 457)
        self.highlight_selected_btn.Size = Size(175, 34)
        self.highlight_selected_btn.Click += self.on_highlight_selected

        self.zoom_btn = Button()
        self.zoom_btn.Text = 'Zoom Selected Pair'
        self.zoom_btn.Location = Point(522, 457)
        self.zoom_btn.Size = Size(160, 34)
        self.zoom_btn.Click += self.on_zoom_selected

        self.repair_label = Label()
        self.repair_label.Text = 'Repair selected pair using CURRENT SpaceClaim primary selection:'
        self.repair_label.Location = Point(12, 502)
        self.repair_label.Size = Size(620, 22)

        self.replace_a_btn = Button()
        self.replace_a_btn.Text = 'Replace A'
        self.replace_a_btn.Location = Point(12, 526)
        self.replace_a_btn.Size = Size(120, 32)
        self.replace_a_btn.Click += lambda s, e: self.on_repair_side('a', 'replace')

        self.replace_b_btn = Button()
        self.replace_b_btn.Text = 'Replace B'
        self.replace_b_btn.Location = Point(140, 526)
        self.replace_b_btn.Size = Size(120, 32)
        self.replace_b_btn.Click += lambda s, e: self.on_repair_side('b', 'replace')

        self.add_a_btn = Button()
        self.add_a_btn.Text = 'Add to A'
        self.add_a_btn.Location = Point(268, 526)
        self.add_a_btn.Size = Size(120, 32)
        self.add_a_btn.Click += lambda s, e: self.on_repair_side('a', 'add')

        self.add_b_btn = Button()
        self.add_b_btn.Text = 'Add to B'
        self.add_b_btn.Location = Point(396, 526)
        self.add_b_btn.Size = Size(120, 32)
        self.add_b_btn.Click += lambda s, e: self.on_repair_side('b', 'add')

        self.remove_a_btn = Button()
        self.remove_a_btn.Text = 'Remove from A'
        self.remove_a_btn.Location = Point(12, 564)
        self.remove_a_btn.Size = Size(120, 32)
        self.remove_a_btn.Click += lambda s, e: self.on_repair_side('a', 'remove')

        self.remove_b_btn = Button()
        self.remove_b_btn.Text = 'Remove from B'
        self.remove_b_btn.Location = Point(140, 564)
        self.remove_b_btn.Size = Size(120, 32)
        self.remove_b_btn.Click += lambda s, e: self.on_repair_side('b', 'remove')

        self.create_a_btn = Button()
        self.create_a_btn.Text = 'Create Missing A'
        self.create_a_btn.Location = Point(268, 564)
        self.create_a_btn.Size = Size(120, 32)
        self.create_a_btn.Click += lambda s, e: self.on_create_missing('a')

        self.create_b_btn = Button()
        self.create_b_btn.Text = 'Create Missing B'
        self.create_b_btn.Location = Point(396, 564)
        self.create_b_btn.Size = Size(120, 32)
        self.create_b_btn.Click += lambda s, e: self.on_create_missing('b')

        self.conflict_btn = Button()
        self.conflict_btn.Text = 'Highlight Conflict'
        self.conflict_btn.Location = Point(530, 526)
        self.conflict_btn.Size = Size(150, 70)
        self.conflict_btn.Click += self.on_highlight_conflict

        self.details = TextBox()
        self.details.Location = Point(12, 608)
        self.details.Size = Size(1055, 98)
        self.details.Multiline = True
        self.details.ReadOnly = True
        self.details.ScrollBars = ScrollBars.Vertical
        self.details.Text = 'Press Validate All.'

        for control in (self.info, self.validate_btn, self.problems_only,
                        self.highlight_problems_btn, self.clear_problem_btn,
                        self.export_btn, self.grid, self.prev_btn, self.next_btn,
                        self.highlight_selected_btn, self.zoom_btn, self.repair_label,
                        self.replace_a_btn, self.replace_b_btn, self.add_a_btn, self.add_b_btn,
                        self.remove_a_btn, self.remove_b_btn, self.create_a_btn, self.create_b_btn,
                        self.conflict_btn, self.details):
            self.Controls.Add(control)

        self.FormClosed += self.on_closed
        self.on_validate(None, None)

    def on_closed(self, sender, args):
        try:
            if self.parent_form is not None:
                self.parent_form.manager_form = None
        except Exception:
            pass

    def on_validate(self, sender, args):
        try:
            self.records = validate_weld_named_selections(context(), self.metric_tolerance)
            self.refresh_grid()
            problems = sum(1 for r in self.records if r['problem'])
            errors = sum(1 for r in self.records if r['status'] == 'ERROR')
            checks = sum(1 for r in self.records if r['status'] == 'CHECK')
            self.details.Text = (('Validation complete: %d pairs | %d problems (%d ERROR, %d CHECK).\r\n'
                                  'CHECK is screening only; review geometry before changing the model.') %
                                 (len(self.records), problems, errors, checks))
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event(self.details.Text)

    def refresh_grid(self):
        selected_pair = self.selected_pair_number()
        self.grid.Rows.Clear()
        for record in self.records:
            if self.problems_only.Checked and not record['problem']:
                continue
            diff = '' if record['metric_diff'] is None else ('%.1f' % record['metric_diff'])
            values = ('w%d' % record['pair'], record['a_name'], record['b_name'],
                      record['a_kind'], record['b_kind'], str(record['a_count']),
                      str(record['b_count']), diff, record['status'], record['reason'])
            idx = self.grid.Rows.Add(Array[Object](list(values)))
            row = self.grid.Rows[idx]
            row.Tag = record['pair']
            if record['status'] == 'ERROR':
                row.DefaultCellStyle.BackColor = Color.MistyRose
            elif record['status'] == 'CHECK':
                row.DefaultCellStyle.BackColor = Color.LemonChiffon
        if selected_pair is not None:
            self.select_pair_row(selected_pair)
        elif self.grid.Rows.Count > 0:
            self.grid.Rows[0].Selected = True

    def on_filter_changed(self, sender, args):
        try:
            self.refresh_grid()
        except Exception:
            self.details.Text = traceback.format_exc()

    def selected_pair_number(self):
        try:
            if self.grid.SelectedRows.Count > 0:
                return int(self.grid.SelectedRows[0].Tag)
        except Exception:
            pass
        return None

    def selected_record(self):
        pair = self.selected_pair_number()
        if pair is None:
            return None
        for record in self.records:
            if record['pair'] == pair:
                return record
        return None

    def select_pair_row(self, pair):
        for row in self.grid.Rows:
            try:
                if int(row.Tag) == int(pair):
                    self.grid.ClearSelection()
                    row.Selected = True
                    self.grid.CurrentCell = row.Cells[0]
                    return True
            except Exception:
                pass
        return False

    def on_selection_changed(self, sender, args):
        record = self.selected_record()
        if record is None:
            return
        diff = 'n/a' if record['metric_diff'] is None else '%.2f%%' % record['metric_diff']
        conflicts = ', '.join(record.get('conflict_groups', []))
        conflict_text = '' if not conflicts else ('\r\nConflict groups: ' + conflicts)
        self.details.Text = (('w%d | %s\r\nA: %s | %s | count=%d\r\nB: %s | %s | count=%d\r\nMetric difference: %s | %s%s') %
                             (record['pair'], record['status'], record['a_name'] or '<missing>',
                              record['a_kind'], record['a_count'], record['b_name'] or '<missing>',
                              record['b_kind'], record['b_count'], diff, record['reason'], conflict_text))

    def on_highlight_problems(self, sender, args):
        try:
            if not self.records:
                self.on_validate(None, None)
            primitives = highlight_problem_records(self.records)
            problem_count = sum(1 for r in self.records if r['problem'])
            self.details.Text = (('Problem highlight: %d pair(s), %d orange primitive(s).\r\n'
                                  'Orange is a QA screening flag, not an engineering acceptance result.') %
                                 (problem_count, primitives))
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event(self.details.Text)

    def on_clear_problem(self, sender, args):
        try:
            count = clear_problem_highlight()
            self.details.Text = 'Problem highlight cleared (%d primitive(s)).' % count
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event(self.details.Text)

    def _problem_pairs(self):
        return [r['pair'] for r in self.records if r['problem']]

    def _move_problem(self, step):
        pairs = self._problem_pairs()
        if not pairs:
            self.details.Text = 'No problems found.'
            return
        current = self.selected_pair_number()
        if current not in pairs:
            target = pairs[0] if step > 0 else pairs[-1]
        else:
            idx = pairs.index(current)
            target = pairs[(idx + step) % len(pairs)]
        if self.problems_only.Checked or self.select_pair_row(target):
            self.select_pair_row(target)
        else:
            self.problems_only.Checked = True
            self.select_pair_row(target)
        self._highlight_pair_number(target, zoom=True)

    def on_previous_problem(self, sender, args):
        self._move_problem(-1)

    def on_next_problem(self, sender, args):
        self._move_problem(1)

    def _highlight_pair_number(self, pair, zoom=False):
        clear_problem_highlight()
        if zoom:
            names, items = geometry_for_group_names(context(), ['w%da' % pair, 'w%db' % pair])
            if items:
                Selection.Create(items).SetActive()
                window = SCWindow.ActiveWindow
                if window is not None:
                    window.ZoomSelection()
                Selection.Empty().SetActive()
        groups, items_count = highlight_pair(context(), pair, False)
        self.details.Text = ('w%d highlighted: A blue / B red | groups=%d | items=%d' %
                             (pair, groups, items_count))

    def on_highlight_selected(self, sender, args):
        try:
            pair = self.selected_pair_number()
            if pair is None:
                self.details.Text = 'Select a weld row first.'
                return
            self._highlight_pair_number(pair, zoom=False)
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event(self.details.Text)

    def on_zoom_selected(self, sender, args):
        try:
            pair = self.selected_pair_number()
            if pair is None:
                self.details.Text = 'Select a weld row first.'
                return
            self._highlight_pair_number(pair, zoom=True)
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event(self.details.Text)

    def _confirm_repair(self, title, text):
        return MessageBox.Show(self, text, title, MessageBoxButtons.YesNo,
                               MessageBoxIcon.Warning) == DialogResult.Yes

    def _after_repair(self, pair, message):
        try:
            Selection.Empty().SetActive()
        except Exception:
            pass
        self.records = validate_weld_named_selections(context(), self.metric_tolerance)
        self.refresh_grid()
        self.select_pair_row(pair)
        try:
            self._highlight_pair_number(pair, zoom=False)
        except Exception:
            log_event('REPAIR post-highlight warning: ' + traceback.format_exc())
        self.details.Text = message + '\r\nRevalidated w%d. Review the updated status before continuing.' % pair

    def on_repair_side(self, side, operation):
        try:
            record = self.selected_record()
            if record is None:
                self.details.Text = 'Select a weld row first.'
                return
            side = side.lower()
            group_name = record.get('%s_name' % side)
            if not group_name:
                self.details.Text = ('w%d%s is missing. Use Create Missing %s.' %
                                     (record['pair'], side, side.upper()))
                return
            selected, selected_kind = _repair_selection_items()
            expected_kind = repair_expected_kind(record, side)
            _validate_repair_kind(selected, expected_kind)
            existing = repair_existing_items(record, side)
            if operation == 'replace':
                new_items = list(selected)
                action = 'Replace'
            elif operation == 'add':
                new_items = repair_merge_items(existing, selected)
                action = 'Add selection to'
            elif operation == 'remove':
                new_items = repair_remove_items(existing, selected)
                action = 'Remove selection from'
                if len(new_items) == len(existing):
                    self.details.Text = 'None of the currently selected objects belongs to %s.' % group_name
                    return
                if not new_items:
                    self.details.Text = ('Repair cancelled: removing the selected geometry would leave %s empty. '
                                         'Use Replace instead.') % group_name
                    return
            else:
                raise ValueError('Unknown repair operation: ' + str(operation))
            new_items = _unique_items(new_items)
            prompt = (('%s %s?\n\nOld geometry: %d %s\nCurrent SpaceClaim selection: %d %s\nResult: %d %s\n\n'
                       'This changes the Named Selection in the active model. Continue?') %
                      (action, group_name, len(existing), record.get('%s_kind' % side),
                       len(selected), selected_kind, len(new_items), expected_kind or selected_kind))
            if not self._confirm_repair('Repair ' + group_name, prompt):
                self.details.Text = 'Repair cancelled.'
                return
            actual, count, kind = replace_named_selection_geometry(context(), group_name, new_items,
                                                                    expected_kind)
            log_event('REPAIR UI: %s | operation=%s | result=%d' % (actual, operation, count))
            self._after_repair(record['pair'], '%s completed: %s now contains %d %s.' %
                               (action, actual, count, kind))
        except ValueError as error:
            self.details.Text = str(error)
            log_event('REPAIR INPUT: ' + str(error))
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event('REPAIR ERROR: ' + self.details.Text)

    def on_create_missing(self, side):
        try:
            record = self.selected_record()
            if record is None:
                self.details.Text = 'Select a weld row first.'
                return
            side = side.lower()
            existing_name = record.get('%s_name' % side)
            if existing_name:
                self.details.Text = '%s already exists.' % existing_name
                return
            selected, selected_kind = _repair_selection_items()
            expected_kind = repair_expected_kind(record, side)
            _validate_repair_kind(selected, expected_kind)
            target = repair_target_name(record, side)
            prompt = (('Create missing Named Selection %s?\n\nCurrent selection: %d %s\n\n'
                       'This creates a new group in the active model. Continue?') %
                      (target, len(selected), selected_kind))
            if not self._confirm_repair('Create ' + target, prompt):
                self.details.Text = 'Creation cancelled.'
                return
            actual, count, kind = create_missing_named_selection(context(), target, selected,
                                                                  expected_kind)
            log_event('REPAIR UI: create missing | %s | items=%d' % (actual, count))
            self._after_repair(record['pair'], 'Created %s with %d %s.' % (actual, count, kind))
        except ValueError as error:
            self.details.Text = str(error)
            log_event('REPAIR INPUT: ' + str(error))
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event('REPAIR ERROR: ' + self.details.Text)

    def on_highlight_conflict(self, sender, args):
        try:
            record = self.selected_record()
            if record is None:
                self.details.Text = 'Select a weld row first.'
                return
            conflict_items = list(record.get('conflict_items', []))
            conflict_groups = list(record.get('conflict_groups', []))
            if not conflict_items:
                self._highlight_pair_number(record['pair'], zoom=False)
                self.details.Text = 'w%d has no reusable-geometry conflict to highlight.' % record['pair']
                return
            # Pair remains A=blue / B=red; exact conflicting geometry is overlaid orange.
            self._highlight_pair_number(record['pair'], zoom=False)
            count = set_problem_overlay(conflict_items)
            groups_text = ', '.join(conflict_groups) if conflict_groups else 'A/B internal duplicate'
            self.details.Text = (('w%d conflict highlighted in orange: %d object(s), %d primitive(s).\r\n'
                                  'Also used by: %s') %
                                 (record['pair'], len(conflict_items), count, groups_text))
            log_event('QA HIGHLIGHT CONFLICT: w%d | items=%d | primitives=%d | groups=%s' %
                      (record['pair'], len(conflict_items), count, groups_text))
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event(self.details.Text)

    def on_export(self, sender, args):
        try:
            if not self.records:
                self.on_validate(None, None)
            dialog = SaveFileDialog()
            dialog.Filter = 'CSV files (*.csv)|*.csv|All files (*.*)|*.*'
            dialog.FileName = 'SpaceClaim_Weld_Named_Selection_QA.csv'
            if dialog.ShowDialog(self) != DialogResult.OK:
                return
            with io.open(dialog.FileName, 'w', encoding='utf-8') as stream:
                stream.write(u'Weld,A,B,TypeA,TypeB,CountA,CountB,MetricDiffPercent,Status,Reason\n')
                for r in self.records:
                    diff = '' if r['metric_diff'] is None else ('%.6g' % r['metric_diff'])
                    reason = str(r['reason']).replace('"', '""')
                    stream.write(u'w%d,%s,%s,%s,%s,%d,%d,%s,%s,"%s"\n' %
                                 (r['pair'], r['a_name'], r['b_name'], r['a_kind'], r['b_kind'],
                                  r['a_count'], r['b_count'], diff, r['status'], reason))
            self.details.Text = 'CSV exported: ' + dialog.FileName
            log_event('QA CSV exported: ' + dialog.FileName)
        except Exception:
            self.details.Text = traceback.format_exc()
            log_event(self.details.Text)

class WeldNamerForm(Form):
    def __init__(self):
        Form.__init__(self)
        self.Text = 'MF | SpaceClaim Named Selection Namer 0.13.1'
        self.ClientSize = Size(465, 536)
        self.FormBorderStyle = FormBorderStyle.FixedToolWindow
        self.StartPosition = FormStartPosition.CenterScreen
        self.TopMost = True
        self.ShowInTaskbar = False
        self.busy = False
        self.owner_thread_id = Thread.CurrentThread.ManagedThreadId

        self.caption = Label()
        self.caption.Text = 'Choose a purpose, select geometry, then Create Next.\nPairs: A = blue, B = red. Face Meshing groups = blue.'
        self.caption.Location = Point(12, 10)
        self.caption.Size = Size(440, 38)

        self.purpose_label = Label()
        self.purpose_label.Text = 'Group purpose:'
        self.purpose_label.Location = Point(12, 59)
        self.purpose_label.Size = Size(120, 23)

        self.purpose = ComboBox()
        self.purpose.DropDownStyle = ComboBoxStyle.DropDownList
        self.purpose.Location = Point(140, 55)
        self.purpose.Size = Size(313, 25)
        for name in (WELD_MODE, BOLT_MODE, FACE_MESH_MODE):
            self.purpose.Items.Add(name)
        self.purpose.SelectedIndex = 0
        self.purpose.SelectedIndexChanged += self.on_purpose_changed

        self.mode_label = Label()
        self.mode_label.Text = 'Selection type:'
        self.mode_label.Location = Point(12, 99)
        self.mode_label.Size = Size(120, 23)

        self.mode = ComboBox()
        self.mode.DropDownStyle = ComboBoxStyle.DropDownList
        self.mode.Location = Point(140, 95)
        self.mode.Size = Size(180, 25)
        self.mode.Items.Add('Faces')
        self.mode.Items.Add('Edges')
        self.mode.SelectedIndex = 0

        self.create = Button()
        self.create.Text = 'Create Next'
        self.create.Location = Point(12, 135)
        self.create.Size = Size(215, 36)
        self.create.Click += self.on_create

        self.refresh = Button()
        self.refresh.Text = 'Check Next Name'
        self.refresh.Location = Point(238, 135)
        self.refresh.Size = Size(215, 36)
        self.refresh.Click += self.on_refresh

        self.auto_highlight = CheckBox()
        self.auto_highlight.Text = 'Auto highlight after Create'
        self.auto_highlight.Location = Point(12, 182)
        self.auto_highlight.Size = Size(320, 24)
        self.auto_highlight.Checked = True

        self.highlight_pair_btn = Button()
        self.highlight_pair_btn.Text = 'Highlight Current Pair'
        self.highlight_pair_btn.Location = Point(12, 216)
        self.highlight_pair_btn.Size = Size(215, 34)
        self.highlight_pair_btn.Click += self.on_highlight_pair

        self.highlight_all = Button()
        self.highlight_all.Text = 'Highlight All Weld Groups'
        self.highlight_all.Location = Point(238, 216)
        self.highlight_all.Size = Size(215, 34)
        self.highlight_all.Click += self.on_highlight_all

        self.clear_highlight = Button()
        self.clear_highlight.Text = 'Clear Highlight'
        self.clear_highlight.Location = Point(12, 260)
        self.clear_highlight.Size = Size(441, 32)
        self.clear_highlight.Click += self.on_clear_highlight

        self.output = TextBox()
        self.manager = Button()
        self.manager.Text = 'Weld Named Selection QA / Repair Manager'
        self.manager.Location = Point(12, 302)
        self.manager.Size = Size(441, 34)
        self.manager.Click += self.on_manager

        self.output.Location = Point(12, 348)
        self.output.Size = Size(441, 170)
        self.output.Multiline = True
        self.output.ReadOnly = True
        self.output.ScrollBars = ScrollBars.Vertical

        for control in (self.caption, self.purpose_label, self.purpose, self.mode_label, self.mode, self.create, self.refresh,
                        self.auto_highlight, self.highlight_pair_btn, self.highlight_all,
                        self.clear_highlight, self.manager, self.output):
            self.Controls.Add(control)

        self.manager_form = None
        self.last_created_by_purpose = {}
        self.output.Text = ('Ready on host UI thread %s.\r\n'
                            'Auto highlight defaults to the pair just created.\r\nQA Manager: validation + orange problem highlight.\r\n'
                            'Repair Manager: Replace/Add/Remove/Create Missing + conflict highlight.\r\nLog: %s') % (Thread.CurrentThread.ManagedThreadId, LOG_PATH)
        log_event('Window ready')

    def assert_ui_thread(self):
        if Thread.CurrentThread.ManagedThreadId != self.owner_thread_id:
            raise RuntimeError('UI thread mismatch; operation cancelled.')

    def on_purpose_changed(self, sender, args):
        purpose = str(self.purpose.SelectedItem)
        clear_all_weld_overlays()
        self.mode.Enabled = (purpose == WELD_MODE)
        self.mode_label.Enabled = self.mode.Enabled
        if purpose == BOLT_MODE:
            self.mode.SelectedItem = 'Edges'
        elif purpose == FACE_MESH_MODE:
            self.mode.SelectedItem = 'Faces'
        self.highlight_pair_btn.Text = ('Highlight Current Group' if purpose == FACE_MESH_MODE
                                        else 'Highlight Current Pair')
        self.highlight_all.Text = ('Highlight All Face Meshing' if purpose == FACE_MESH_MODE
                                   else 'Highlight All Bolt Groups' if purpose == BOLT_MODE
                                   else 'Highlight All Weld Groups')
        self.manager.Enabled = (purpose == WELD_MODE)
        self.output.Text = '%s | selection: %s' % (purpose, geometry_mode(purpose, str(self.mode.SelectedItem)))

    def on_refresh(self, sender, args):
        try:
            self.assert_ui_thread()
            root = context()
            names = names_in(root)
            purpose = str(self.purpose.SelectedItem)
            if purpose == WELD_MODE:
                pair_number, target = current_pair_from_names(names)
                pair_text = 'none' if pair_number is None else 'w%d' % pair_number
                self.output.Text = 'Next: %s | Current pair: %s | Groups inspected: %d' % (target, pair_text, len(names))
            elif purpose == BOLT_MODE:
                number, target = current_bolt_pair_from_names(names)
                pair_text = 'none' if number is None else 'f%d' % number
                self.output.Text = 'Next: %s | Current pair: %s | Groups inspected: %d' % (
                    target, pair_text, len(names))
            else:
                self.output.Text = 'Next: %s | Selection: %s | Groups inspected: %d' % (
                    next_group_name(names, purpose), geometry_mode(purpose, str(self.mode.SelectedItem)), len(names))
        except ValueError as error:
            self.output.Text = str(error)
            log_event('INPUT: ' + str(error))
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_highlight_pair(self, sender, args):
        try:
            self.assert_ui_thread()
            root = context()
            purpose = str(self.purpose.SelectedItem)
            if purpose == WELD_MODE:
                pair_number, groups, items, target = highlight_current_pair(root, False)
                label = 'w%d' % pair_number if pair_number is not None else 'none'
            elif purpose == BOLT_MODE:
                pair_number, target = current_bolt_pair_from_names(names_in(root))
                groups, items = highlight_bolt_pair(root, pair_number, False)
                label = 'f%d' % pair_number if pair_number is not None else 'none'
            else:
                existing = face_mesh_names(root)
                last = self.last_created_by_purpose.get(FACE_MESH_MODE)
                actual = dict((name.lower(), name) for number, name in existing)
                current = actual.get(str(last).lower()) if last else None
                if current is None and existing:
                    current = max(existing)[1]
                groups, items = highlight_face_mesh_groups(root, [current] if current else [], False)
                target = next_group_name(names_in(root), purpose)
                label = current or 'none'
            self.output.Text = ('Highlighted %s | Groups: %d | Geometry items: %d | Next: %s' %
                                (label, groups, items, target))
        except ValueError as error:
            self.output.Text = str(error)
            log_event('INPUT: ' + str(error))
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_highlight_all(self, sender, args):
        try:
            self.assert_ui_thread()
            root = context()
            purpose = str(self.purpose.SelectedItem)
            if purpose == WELD_MODE:
                groups, items = highlight_weld_groups(root, False)
            elif purpose == BOLT_MODE:
                groups, items = highlight_all_bolt_groups(root, False)
            else:
                groups, items = highlight_face_mesh_groups(root,
                                [name for number, name in face_mesh_names(root)], False)
            legend = 'blue' if purpose == FACE_MESH_MODE else 'A = blue / B = red'
            self.output.Text = 'Highlighted ALL %s: %d groups | %d items | %s' % (
                purpose, groups, items, legend)
        except ValueError as error:
            self.output.Text = str(error)
            log_event('INPUT: ' + str(error))
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_clear_highlight(self, sender, args):
        try:
            self.assert_ui_thread()
            clear_all_weld_overlays()
            self.output.Text = 'All highlight cleared (blue + red + QA orange).'
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_manager(self, sender, args):
        try:
            self.assert_ui_thread()
            if self.manager_form is not None and not self.manager_form.IsDisposed:
                self.manager_form.Activate()
                return
            self.manager_form = NamedSelectionManagerForm(self)
            self.manager_form.Show(self)
            log_event('QA Manager opened')
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_create(self, sender, args):
        if self.busy:
            return
        self.busy = True
        self.create.Enabled = False
        try:
            self.assert_ui_thread()
            purpose = str(self.purpose.SelectedItem)
            result = create_next(str(self.mode.SelectedItem), bool(self.auto_highlight.Checked), purpose)
            match = re.match(r'^Created ([^ |]+)', result)
            if match:
                self.last_created_by_purpose[purpose] = match.group(1)
            self.output.Text = result
            log_event(self.output.Text)
        except ValueError as error:
            self.output.Text = str(error)
            log_event('INPUT: ' + str(error))
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)
        finally:
            self.create.Enabled = True
            self.busy = False


# IMPORTANT: create ALL controls on the existing host UI thread.
# Do not use Show() on the script worker, ShowDialog(), Application.Run(),
# an independent STA thread, synchronous Invoke(), Join(), or DoEvents loops.
# BeginInvoke returns immediately, allowing the script runner to finish.
STATE_KEY = 'MF.SpaceClaim.WeldNamer.v011.State'
STATE_LOCK = String.Intern('MF.SpaceClaim.WeldNamer.v011.StateLock')

def find_host_dispatch():
    process = Process.GetCurrentProcess()
    process.Refresh()
    handle = process.MainWindowHandle
    if handle == IntPtr.Zero:
        raise RuntimeError('SpaceClaim main window handle is unavailable. No window created.')
    host = Control.FromHandle(handle)
    if host is not None:
        if not host.IsHandleCreated or host.IsDisposed:
            raise RuntimeError('SpaceClaim host control is not ready.')
        return (lambda action: host.BeginInvoke(action)), host, 'WinForms.BeginInvoke'
    # Some host builds use WPF. Only use the dispatcher of the actual host HWND.
    # Never create a new dispatcher on the script worker thread.
    clr.AddReference('PresentationCore')
    clr.AddReference('WindowsBase')
    from System.Windows.Interop import HwndSource
    from System.Windows.Threading import DispatcherPriority
    source = HwndSource.FromHwnd(handle)
    if source is None:
        raise RuntimeError('No managed dispatcher for SpaceClaim main HWND. Run UI_Diagnostics.py; no window created.')
    dispatcher = source.Dispatcher
    if dispatcher.HasShutdownStarted or dispatcher.HasShutdownFinished:
        raise RuntimeError('SpaceClaim dispatcher is shutting down.')
    return (lambda action: dispatcher.BeginInvoke(DispatcherPriority.Normal, action)), None, 'WPF.BeginInvoke'

def schedule_window():
    # AppDomain storage survives script scope recreation. An atomic latch is set
    # BEFORE posting; repeated script runs perform no UI actions and no logging.
    Monitor.Enter(STATE_LOCK)
    try:
        state = AppDomain.CurrentDomain.GetData(STATE_KEY)
        if state is not None and state['phase'] != 'closed':
            return
        last_mode = state.get('mode', 'Faces') if state is not None else 'Faces'
        last_auto = state.get('auto_highlight', True) if state is not None else True
        last_purpose = state.get('purpose', WELD_MODE) if state is not None else WELD_MODE
        state = {'phase': 'queued', 'form': None, 'callback': None,
                 'mode': last_mode, 'auto_highlight': last_auto, 'purpose': last_purpose}
        AppDomain.CurrentDomain.SetData(STATE_KEY, state)
    finally:
        Monitor.Exit(STATE_LOCK)
    try:
        post, owner, route = find_host_dispatch()
        log_event('Launch requested via ' + route)

        def launch_on_host():
            try:
                log_event('Host UI callback entered')
                form = WeldNamerForm()
                state['form'] = form
                form.mode.SelectedItem = state['mode']
                form.auto_highlight.Checked = bool(state.get('auto_highlight', True))
                if state.get('purpose', WELD_MODE) in (WELD_MODE, BOLT_MODE, FACE_MESH_MODE):
                    form.purpose.SelectedItem = state['purpose']
                def closed(sender, args):
                    # Only close makes a new run eligible. Replays while open
                    # still return without Show/Activate or another callback.
                    Monitor.Enter(STATE_LOCK)
                    try:
                        state['mode'] = str(form.mode.SelectedItem)
                        state['auto_highlight'] = bool(form.auto_highlight.Checked)
                        state['purpose'] = str(form.purpose.SelectedItem)
                        state['form'] = None
                        state['phase'] = 'closed'
                    finally:
                        Monitor.Exit(STATE_LOCK)
                    log_event('Window closed; ready for next Run')
                form.FormClosed += closed
                if owner is not None:
                    form.Show(owner)
                else:
                    form.Show()
                state['phase'] = 'open'
            except Exception:
                state['phase'] = 'failed'
                log_event('UI START ERROR: ' + traceback.format_exc())
            finally:
                state['callback'] = None

        callback = Action(launch_on_host)
        state['callback'] = callback
        post(callback)
        print('Window queued once. Log: ' + LOG_PATH)
    except Exception:
        state['phase'] = 'failed'
        state['callback'] = None
        raise

try:
    schedule_window()
except Exception:
    message = traceback.format_exc()
    log_event(message)
    print(message)
