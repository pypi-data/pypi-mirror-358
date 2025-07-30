from .Convex_hull_UG import Convex_hull_UG
from .LPD_UG import LPD
from .Convex_hull_DAG import Convex_hull_DAG
from .Graph_gererators import generator_connected_ug, generate_connected_dag 
from .examples import get_example

__all__ = ['get_example', 'generator_connected_ug', 'generate_connected_dag']

def CMSA(graph, r):
    convex_hull_ug = Convex_hull_UG(graph) 
    return convex_hull_ug.CMSA(r)

def IPA(graph, r):
    convex_hull_ug = Convex_hull_UG(graph) 
    return convex_hull_ug.IPA(r)


def CMDSA(graph, r):
    convex_hull_dag = Convex_hull_DAG(graph)
    return convex_hull_dag.CMDSA(r)

def Decom_CMSA(input_tuple):
    lpd_ug = LPD(input_tuple)
    return lpd_ug.Decom_CMSA()

def Decom_IPA(input_tuple):
    lpd_ug = LPD(input_tuple)
    return lpd_ug.Decom_IPA()
