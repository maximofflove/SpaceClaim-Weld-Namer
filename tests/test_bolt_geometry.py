import ast,math,pathlib,re,traceback,types,unittest
p=pathlib.Path(__file__).resolve().parents[1] / 'Weld_Namer.py';t=ast.parse(p.read_text())
ns={'math':math,'re':re,'traceback':traceback,'log_event':lambda x:None,'BOLT_AXIS_TOL_DEG':1.0,'BOLT_MIN_LENGTH':1e-6,'CONTACT_MODE':'ctkt','CONTACT_MAX_PAIR':9999999,'WELD_MODE':'w','BOLT_MODE':'f','FACE_MESH_MODE':'fm','BOLT_MAX_PAIR':999999,'FACE_MESH_MAX':999999999}
names={'_bolt_xyz','_bolt_unit','_bolt_deviation','_bolt_tolerance','_bolt_station','_bolt_pair_axis','check_bolt_creation','audit_bolt_pairs','create_next','next_group_name','geometry_mode'}
exec(compile(ast.Module(body=[x for x in t.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),str(p),'exec'),ns)
class XYZ:
 def __init__(self,v):self.X,self.Y,self.Z=v
class Circle:
 def __init__(self,c,n,r):self.Frame=types.SimpleNamespace(Origin=XYZ(c),DirZ=XYZ(n));self.Radius=r
class Plane:
 def __init__(self,n):self.Frame=types.SimpleNamespace(DirZ=XYZ(n))
class Generic:
 def __getitem__(self,k):return lambda:None
class Edge:
 def __init__(self,c=(0,0,0),n=(0,0,1),normals=None,r=.005,arc=False):
  self.Shape=types.SimpleNamespace(Geometry=Circle(c,n,r),Length=2*math.pi*r*(.5 if arc else 1))
  self.Faces=[types.SimpleNamespace(Shape=types.SimpleNamespace(Geometry=Plane(normal))) for normal in (normals if normals is not None else [n])]
  self.Faces.append(types.SimpleNamespace(Shape=types.SimpleNamespace(Geometry='Cylinder',GetGeometry=Generic())))
class Sel:
 def __init__(self,items):self.Items=items
class Selection:
 groups={};active=[]
 @staticmethod
 def CreateByGroups(n):return None if Selection.groups[n] is None else Sel(Selection.groups[n])
 @staticmethod
 def GetActive():return Sel(Selection.active)
 @staticmethod
 def Empty():return Sel([])
mutations=[]
class Named:
 @staticmethod
 def Create(*a):mutations.append('Create');raise RuntimeError('MUTATION_REACHED')
ns.update(SCCircle=Circle,SCPlane=Plane,Selection=Selection,NamedSelection=Named,context=lambda:'root',validate_items=lambda i,m:None,all_groups=lambda root:[types.SimpleNamespace(Name=n) for n in Selection.groups],log_creation_signatures=lambda:None)
def station(e,name):return ns['_bolt_station']([e],name,1)
class Tests(unittest.TestCase):
 def setUp(self):Selection.groups={};Selection.active=[];mutations[:]=[]
 def test_normal_pair(self):self.assertEqual(ns['_bolt_pair_axis'](station(Edge(),'f1a'),station(Edge(c=(0,0,.01),n=(0,0,-1)),'f1b'),1),[0,0])
 def test_offset_centres(self):
  with self.assertRaisesRegex(ValueError,'NOT perpendicular'):ns['_bolt_pair_axis'](station(Edge(),'f1a'),station(Edge(c=(.005,0,.01)),'f1b'),1)
 def test_arbitrary_orientation(self):
  n=(1,2,3);end=tuple(.01*x for x in n);self.assertLess(max(ns['_bolt_pair_axis'](station(Edge(n=n),'f1a'),station(Edge(c=end,n=n),'f1b'),1)),1e-5)
 def test_tolerance(self):
  b=station(Edge(c=(math.tan(math.radians(.5))*.01,0,.01)),'f1b');a=station(Edge(),'f1a')
  self.assertAlmostEqual(ns['_bolt_pair_axis'](a,b,1)[0],.5)
  with self.assertRaises(ValueError):ns['_bolt_pair_axis'](a,b,.1)
 def test_coincident(self):
  with self.assertRaisesRegex(ValueError,'coincident'):ns['_bolt_pair_axis'](station(Edge(),'f1a'),station(Edge(),'f1b'),1)
 def test_arc(self):
  with self.assertRaisesRegex(ValueError,'full circular'):station(Edge(arc=True),'f1a')
 def test_no_planar(self):
  with self.assertRaisesRegex(ValueError,'no adjacent planar'):station(Edge(normals=[]),'f1a')
 def test_multiple_edges(self):
  with self.assertRaisesRegex(ValueError,'ONE'):ns['_bolt_station']([Edge(),Edge()],'f1a',1)
 def test_skew_plate_normal(self):
  with self.assertRaises(ValueError):station(Edge(normals=[(1,0,0)]),'f1a')
 def test_pipeline_no_mutation_on_bad_pair(self):
  Selection.groups={'f1a':[Edge()]};Selection.active=[Edge(c=(.005,0,.01))]
  with self.assertRaisesRegex(ValueError,'NOT perpendicular'):ns['create_next'](purpose='f')
  self.assertEqual(mutations,[])
 def test_pipeline_valid_pair_reaches_creation(self):
  Selection.groups={'f1a':[Edge()]};Selection.active=[Edge(c=(0,0,.01))]
  with self.assertRaisesRegex(RuntimeError,'MUTATION_REACHED'):ns['create_next'](purpose='f')
  self.assertEqual(mutations,['Create'])
 def test_pipeline_first_side_pending(self):
  self.assertIn('PENDING',ns['check_bolt_creation']('root','f1a',[Edge()],[],1))
 def test_pipeline_gap_with_existing_b(self):
  Selection.groups={'F1B':[Edge(c=(0,0,.01))]}
  groups=ns['all_groups']('root');self.assertIn('OK',ns['check_bolt_creation']('root','f1a',[Edge()],groups,1))
 def test_audit_continues_after_error(self):
  Selection.groups={'f1a':[Edge()],'f1b':[Edge(c=(.005,0,.01))],'f2a':[Edge()],'f2b':[Edge(c=(0,0,.01))],'f3a':[Edge()]}
  self.assertEqual([r['status'] for r in ns['audit_bolt_pairs']('root',1)],['ERROR','OK','INCOMPLETE'])
 def test_unreadable(self):
  Selection.groups={'f1a':None,'f1b':[Edge()]};self.assertEqual(ns['audit_bolt_pairs']('root',1)[0]['status'],'ERROR')
 def test_invalid_tolerance(self):
  for v in [0,-1,float('nan'),float('inf'),11]:
   with self.assertRaises(ValueError):ns['_bolt_tolerance'](v)
if __name__ == '__main__':
    unittest.main()
