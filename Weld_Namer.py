# Python Script, API Version = V19
# -*- coding: utf-8 -*-
# SpaceClaim Weld Namer 0.10 STABLE - IronPython 2.7, SpaceClaim script editor.
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
    group_names, items = weld_group_geometry(root)
    if clear_primary:
        # After Create Next the just-created edges are still the primary selection.
        # Clear only that primary selection first so the weld overlay can be seen
        # in SpaceClaim's secondary-selection color (normally blue).
        Selection.Empty().SetActive()
    if items:
        Selection.Create(items).SetActiveSecondary()
    else:
        Selection.Empty().SetActiveSecondary()
    log_event('HIGHLIGHT: groups=%d | items=%d | clear_primary=%s' %
              (len(group_names), len(items), str(bool(clear_primary))))
    return len(group_names), len(items)

def clear_weld_highlight():
    Selection.Empty().SetActiveSecondary()
    log_event('HIGHLIGHT: secondary selection cleared')

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
    if pair_number is None or pair_number < 1:
        Selection.Empty().SetActiveSecondary()
        log_event('HIGHLIGHT PAIR: none | clear_primary=%s' % str(bool(clear_primary)))
        return 0, 0
    requested = ['w%da' % pair_number, 'w%db' % pair_number]
    group_names, items = geometry_for_group_names(root, requested)
    if clear_primary:
        Selection.Empty().SetActive()
    if items:
        Selection.Create(items).SetActiveSecondary()
    else:
        Selection.Empty().SetActiveSecondary()
    log_event('HIGHLIGHT PAIR: w%d | groups=%d | items=%d | clear_primary=%s' %
              (pair_number, len(group_names), len(items), str(bool(clear_primary))))
    return len(group_names), len(items)

def highlight_current_pair(root, clear_primary=False):
    pair_number, target = current_pair_from_names(names_in(root))
    groups, items = highlight_pair(root, pair_number, clear_primary)
    return pair_number, groups, items, target

def create_next(mode="Faces", auto_highlight=True):
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
    highlight_note = ' | Auto highlight: OFF'
    if auto_highlight:
        try:
            pair_number = pair_number_from_name(target)
            group_count, item_count = highlight_pair(root, pair_number, True)
            highlight_note = ' | Auto highlight: w%d (%d groups / %d items)' % (pair_number, group_count, item_count)
        except Exception:
            log_event('HIGHLIGHT ERROR after create %s: %s' % (target, traceback.format_exc()))
            highlight_note = ' | Auto highlight: FAILED (group is OK)'
    return 'Created %s | %s: %d | Next: %s%s' % (target, mode, len(items), next_name(names_in(root)), highlight_note)

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
from System.Windows.Forms import Form, Button, Label, TextBox, CheckBox, FormBorderStyle, FormStartPosition, ScrollBars, ComboBox, ComboBoxStyle
from System.Drawing import Point, Size
from System import Action, IntPtr, AppDomain, String
from System.Diagnostics import Process
from System.Threading import Thread, Monitor
from System.Windows.Forms import Control
import os
import tempfile
import io
import datetime

LOG_PATH = os.path.join(tempfile.gettempdir(), 'SpaceClaim_Weld_Namer_v010.log')

def log_event(text):
    # Logging must not call the script editor from a UI callback.
    try:
        with io.open(LOG_PATH, 'a', encoding='utf-8') as stream:
            stream.write(u'%s | thread %s | %s\n' %
                         (datetime.datetime.now().isoformat(),
                          Thread.CurrentThread.ManagedThreadId, text))
    except Exception:
        pass


class WeldNamerForm(Form):
    def __init__(self):
        Form.__init__(self)
        self.Text = 'MF | SpaceClaim Weld Namer 0.10 STABLE'
        self.ClientSize = Size(465, 438)
        self.FormBorderStyle = FormBorderStyle.FixedToolWindow
        self.StartPosition = FormStartPosition.CenterScreen
        self.TopMost = True
        self.ShowInTaskbar = False
        self.busy = False
        self.owner_thread_id = Thread.CurrentThread.ManagedThreadId

        self.caption = Label()
        self.caption.Text = 'Choose Faces or Edges, select geometry, then Create Next.\nSecondary highlight marks existing weld geometry in blue.'
        self.caption.Location = Point(12, 10)
        self.caption.Size = Size(440, 38)

        self.mode_label = Label()
        self.mode_label.Text = 'Selection type:'
        self.mode_label.Location = Point(12, 59)
        self.mode_label.Size = Size(120, 23)

        self.mode = ComboBox()
        self.mode.DropDownStyle = ComboBoxStyle.DropDownList
        self.mode.Location = Point(140, 55)
        self.mode.Size = Size(180, 25)
        self.mode.Items.Add('Faces')
        self.mode.Items.Add('Edges')
        self.mode.SelectedIndex = 0

        self.create = Button()
        self.create.Text = 'Create Next'
        self.create.Location = Point(12, 95)
        self.create.Size = Size(215, 36)
        self.create.Click += self.on_create

        self.refresh = Button()
        self.refresh.Text = 'Check Next Name'
        self.refresh.Location = Point(238, 95)
        self.refresh.Size = Size(215, 36)
        self.refresh.Click += self.on_refresh

        self.auto_highlight = CheckBox()
        self.auto_highlight.Text = 'Auto highlight current pair after Create'
        self.auto_highlight.Location = Point(12, 142)
        self.auto_highlight.Size = Size(320, 24)
        self.auto_highlight.Checked = True

        self.highlight_pair_btn = Button()
        self.highlight_pair_btn.Text = 'Highlight Current Pair'
        self.highlight_pair_btn.Location = Point(12, 176)
        self.highlight_pair_btn.Size = Size(215, 34)
        self.highlight_pair_btn.Click += self.on_highlight_pair

        self.highlight_all = Button()
        self.highlight_all.Text = 'Highlight All Weld Groups'
        self.highlight_all.Location = Point(238, 176)
        self.highlight_all.Size = Size(215, 34)
        self.highlight_all.Click += self.on_highlight_all

        self.clear_highlight = Button()
        self.clear_highlight.Text = 'Clear Highlight'
        self.clear_highlight.Location = Point(12, 220)
        self.clear_highlight.Size = Size(441, 32)
        self.clear_highlight.Click += self.on_clear_highlight

        self.output = TextBox()
        self.output.Location = Point(12, 264)
        self.output.Size = Size(441, 156)
        self.output.Multiline = True
        self.output.ReadOnly = True
        self.output.ScrollBars = ScrollBars.Vertical

        for control in (self.caption, self.mode_label, self.mode, self.create, self.refresh,
                        self.auto_highlight, self.highlight_pair_btn, self.highlight_all,
                        self.clear_highlight, self.output):
            self.Controls.Add(control)

        self.output.Text = ('Ready on host UI thread %s.\r\n'
                            'Auto highlight defaults to the pair just created.\r\n'
                            'Log: %s') % (Thread.CurrentThread.ManagedThreadId, LOG_PATH)
        log_event('Window ready')

    def assert_ui_thread(self):
        if Thread.CurrentThread.ManagedThreadId != self.owner_thread_id:
            raise RuntimeError('UI thread mismatch; operation cancelled.')

    def on_refresh(self, sender, args):
        try:
            self.assert_ui_thread()
            root = context()
            names = names_in(root)
            pair_number, target = current_pair_from_names(names)
            pair_text = 'none' if pair_number is None else 'w%d' % pair_number
            self.output.Text = 'Next: %s | Current pair: %s | Groups inspected: %d' % (target, pair_text, len(names))
        except ValueError as error:
            self.output.Text = str(error)
            log_event('INPUT: ' + str(error))
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_highlight_pair(self, sender, args):
        try:
            self.assert_ui_thread()
            pair_number, groups, items, target = highlight_current_pair(context(), False)
            if pair_number is None:
                self.output.Text = 'No current weld pair to highlight. Next: %s' % target
            else:
                self.output.Text = ('Highlighted current pair w%d | Existing groups in pair: %d | '
                                    'Geometry items: %d | Next: %s') % (pair_number, groups, items, target)
        except ValueError as error:
            self.output.Text = str(error)
            log_event('INPUT: ' + str(error))
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_highlight_all(self, sender, args):
        try:
            self.assert_ui_thread()
            groups, items = highlight_weld_groups(context(), False)
            self.output.Text = 'Highlighted ALL weld groups: %d | Geometry items: %d | Secondary selection = blue' % (groups, items)
        except ValueError as error:
            self.output.Text = str(error)
            log_event('INPUT: ' + str(error))
        except Exception:
            self.output.Text = traceback.format_exc()
            log_event(self.output.Text)

    def on_clear_highlight(self, sender, args):
        try:
            self.assert_ui_thread()
            clear_weld_highlight()
            self.output.Text = 'Weld highlight cleared.'
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
            self.output.Text = create_next(str(self.mode.SelectedItem), bool(self.auto_highlight.Checked))
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
STATE_KEY = 'MF.SpaceClaim.WeldNamer.v010.State'
STATE_LOCK = String.Intern('MF.SpaceClaim.WeldNamer.v010.StateLock')

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
        state = {'phase': 'queued', 'form': None, 'callback': None,
                 'mode': last_mode, 'auto_highlight': last_auto}
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
                def closed(sender, args):
                    # Only close makes a new run eligible. Replays while open
                    # still return without Show/Activate or another callback.
                    Monitor.Enter(STATE_LOCK)
                    try:
                        state['mode'] = str(form.mode.SelectedItem)
                        state['auto_highlight'] = bool(form.auto_highlight.Checked)
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
