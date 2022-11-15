# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 11:21:11 2022

@author: MaxKo
"""
import z3

def connectedCheck(br):
    #Generate matrix for DFS
    n = len(verts)
    adj_matrix = [[0 for i in range(n)] for i in range(n)]
    for bridge in bridges:
        num_bridges = br[bridges.index(bridge)]
        if num_bridges > 0:
            adj_matrix[bridge[0]][bridge[1]] = 1
            adj_matrix[bridge[1]][bridge[0]] = 1
            
    l = list()
    
    def VisitVertex(M, i):
        if i in l:
            return l
        l.append(i)
        for j in range(0, n):
            if M[i][j] > 0:
                VisitVertex(M, j)
        
    VisitVertex(adj_matrix, 0)
    
    if (len(l) == n):
        return z3.BoolVal(True)
    else: return z3.BoolVal(False)

def drawGrid(answer):
    filled_grid = grid.copy()
    a = 0
    while a < len(answer):
        if answer[a] > 0:
            v1 = verts[bridges[a][0]]
            v2 = verts[bridges[a][1]]
            if bridges[a] in horiz_edges:
                if answer[a] == 1:
                    draw = "─"
                if answer[a] == 2:
                    draw = "═"
                x1 = min(v1[0], v2[0])
                x2 = max(v1[0], v2[0])
                filled_grid[v1[1]] = filled_grid[v1[1]][:x1+1] + draw * (x2-x1-1) + filled_grid[v1[1]][x2:]
            elif bridges[a] in vert_edges:
                if answer[a] == 1:
                    draw = "│"
                if answer[a] == 2:
                    draw = "║"
                for i in range(v1[1] + 1, v2[1]):
                   filled_grid[i] = filled_grid[i][:v1[0]] + draw + filled_grid[i][v1[0] + 1:]
        a += 1
    for line in filled_grid:
        print(line)
        
def all_smt(s, initial_terms):
    def block_term(s, m, t):
        s.add(t != m.eval(t))
    def fix_term(s, m, t):
        s.add(t == m.eval(t))
    def all_smt_rec(terms):
        if z3.sat == s.check():
           m = s.model()
           yield m
           for i in range(len(terms)):
               s.push()
               block_term(s, m, terms[i])
               for j in range(i):
                   fix_term(s, m, terms[j])
               yield from all_smt_rec(terms[i:])
               s.pop()   
    yield from all_smt_rec(list(initial_terms))  

givens1 = [
    [2, 3, 0, 4, 0, 2, 0],
    [0, 0, 0, 0, 0, 0, 2],
    [1, 1, 0, 0, 1, 3, 3],
    [2, 0, 0, 8, 0, 5, 2],
    [3, 0, 3, 0, 0, 0, 1],
    [0, 0, 2, 0, 0, 3, 4],
    [3, 0, 0, 3, 1, 0, 2],
    ]

#givens = [[4, 0, 0, 4, 0, 6, 0, 0, 3],
#          [0, 2, 0, 0, 3, 0, 1, 0, 0],
#          [2, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 2, 0, 1, 0, 4, 0, 0, 0],
#          [4, 0, 4, 0, 3, 0, 2, 0, 3],
#          [0, 0, 0, 2, 0, 8, 0, 4, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 2],
#          [0, 0, 2, 0, 1, 0, 0, 2, 0],
#          [3, 0, 0, 2, 0, 4, 0, 0, 2],
#          ]

verts = []
adj_matrix = []
horiz_edges = []
vert_edges = []
crossing_edge_pairs = set()
grid = [' '*len(givens)]*len(givens[0])

#Get islands
for y in range(len(givens)):
    for x in range(len(givens[y])):
        if givens[y][x] != 0:
            verts.append((x, y))
            grid[y] = grid[y][:x] + str(givens[y][x]) + grid[y][x + 1:]
            #Get edges
            #adj_matrix.append([0])
            n = len(verts)
            x_linked = False
            y_linked = False
            for vert in verts[-2::-1]:
                if not y_linked and vert[0] == verts[n-1][0]:
                    y_linked = True
                    vert_edges.append((verts.index(vert), n-1))
                elif not x_linked and vert[1] == verts[n-1][1]:
                    x_linked = True
                    horiz_edges.append((verts.index(vert), n-1))
            
#Get crossing edges
for horiz_edge in horiz_edges:
    for vert_edge in vert_edges:
        if verts[horiz_edge[0]][0] < verts[vert_edge[0]][0] and \
           verts[horiz_edge[1]][0] > verts[vert_edge[0]][0] and \
           verts[vert_edge[0]][1] < verts[horiz_edge[0]][1] and \
           verts[vert_edge[1]][1] > verts[horiz_edge[1]][1]:
               crossing_edge_pairs.add((horiz_edge, vert_edge))

bridges = horiz_edges + vert_edges

b = z3.IntVector('b', len(bridges))
bridge_count_c = [ givens[i[1]][i[0]] == sum([br for br in b if verts.index(i) in bridges[b.index(br)]]) for i in verts] 
bridge_limit_c = [ z3.And(br >= 0, br <= 2) for br in b ]
no_crossings_c = [ z3.Or(b[bridges.index(pair[0])] == 0, b[bridges.index(pair[1])] == 0) for pair in crossing_edge_pairs ]

s = z3.Solver()
s.append(bridge_count_c + bridge_limit_c + no_crossings_c)

if s.check():
    connected = False
    models = list(all_smt(s, b))
    index = 0
    while not connected:
        m = models[index]
        answer = [ m[b[i]].as_long() for i in range(len(bridges)) ]
        if (connectedCheck(answer)):
            connected = True
            drawGrid(answer)
        else:
            index = index + 1