#This is a convex hull algorithm that absorbs minimal separations, 
#inputs the undirected graph and sets of concerns, and obtains the convex hull.
import networkx as nx

class Convex_hull_UG:

    def __init__(self, graph):
        self.graph = graph

    def CloseSeparator(self, g_C, a, b):
        N_A = set(g_C.adj[a])
        V_remove_N_A = set(g_C.nodes) - N_A
        N_V_C = {n for n in nx.node_boundary(g_C, nbunch1=nx.node_connected_component(nx.subgraph(g_C, V_remove_N_A), b), nbunch2=N_A)}
        return N_V_C

    def CMSA(self,r):
        g = self.graph
        s = 1 
        H=set(r)
        while s == 1:
            s = 0
            M = set(g.nodes)-H
            M_c = list(nx.connected_components(nx.subgraph(g, M))) 
            for i in range(0,len(M_c)):
                h = {n for n in nx.node_boundary(g, nbunch1=M_c[i], nbunch2=H)}           
                for a in h:
                    for b in h:
                        if a!=b and b not in g.adj[a]:
                            Subgraph = nx.subgraph(g, M | {a,b})
                            H |= self.CloseSeparator(Subgraph,a,b)
                            H |= self.CloseSeparator(Subgraph,b,a)
                            s = 1
                            break
                    else:
                        continue
                    break    
        return H
    
    def IPA(self,r):
        g = self.graph
        s = 1 
        H=set(r)
        while s == 1:
            s = 0
            M = set(g.nodes)-H
            M_c = list(nx.connected_components(nx.subgraph(g, M))) 
            for i in range(0,len(M_c)):
                h = {n for n in nx.node_boundary(g, nbunch1=M_c[i], nbunch2=H)}           
                for a in h:
                    for b in h:
                        if a!=b and b not in g.adj[a]:
                            Subgraph = nx.subgraph(g, M | {a,b})
                            H |= set(nx.shortest_path(Subgraph, a, b))
                            s = 1
                            break
                    else:
                        continue
                    break    
        return H
    

#from Convex_hull_UG import *
#hull = Convex_hull_UG(G)
#CMSA Algorithm, hull.CMSA(R)#R = list
#IPA Algorithm, hull.IPA(R)#R = list