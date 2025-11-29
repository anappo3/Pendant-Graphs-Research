import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import random

# note (and could play around with this more): you can assign a dictionary to each node

def cycle_graph(n):
    G = nx.Graph()
    i = 1
    while i < n:
        G.add_edge(f'V{i}',f'V{i+1}')
        G.add_edge(f'V{i}',f'P{i}')
        i += 1
    G.add_edge(f'V{n}',f'V{1}')
    G.add_edge(f'V{n}',f'P{n}')

    return G

def is_intersecting(listA,listB):
    if len(set(listA).intersection(set(listB))) == 0:
        return False
    return True

def is_family_intersecting(family):
    for v1,v2 in itertools.combinations(family,2):
        if len(set(v1).intersection(set(v2))) == 0:
            return False
    return True

def is_independent(G,vertex_set):
    for v1,v2 in itertools.combinations(vertex_set,2):
        if G.has_edge(v1,v2):
            return False
    return True

def create_independent_family(G,r): # graph G, size r set
    F_r = itertools.combinations(G.nodes(),r)
    family = []
    for s in F_r:
       if is_independent(G,s):
           family.append(s)
    random.shuffle(family) # shuffles set so that we get randomness of making families
    return family

def create_intersecting_family(G,r):
    I_r = [set(x) for x in create_independent_family(G,r)]
    rand = random.randint(0,len(I_r) - 1)
    fixed_set = I_r[rand] # fix a random set
    family = [fixed_set]

    I_r.remove(fixed_set)

    # build an intersecting set from random vertex
    random.shuffle(I_r)

    for s in I_r:
        if all(s & t for t in family):
            family.append(s)
    family = [tuple(x) for x in family]
    return family

def create_star_family(G,r,center):
    if type(center) != str:
        return print("Center must be string V1...Vn or P1...Pn")
    elif center not in G.nodes():
        return print("Center must be a vertex of the graph")
    else:
        star_family = []
        I_r = create_independent_family(G,r)
        # iterate until we find a set with the center, then add
        for s in I_r:
            if is_intersecting([center],s):
                star_family.append(s)
        return star_family

'''Gets sets where all vertices are pendants'''
def get_pendant_family(G,intersecting_family):
    internals = [x for x in G.nodes() if x[0] == 'V']
    return [f for f in intersecting_family if not(is_intersecting(f,set(internals)))]

# def get_consec_pendant_set(G,r):
#     p = [x for x in G.nodes() if x[0] == 'P']
#     res = []
#     for i in range(r):
#         res.append(p[i])
#     return tuple(res)

# V1, works, but there are some bugs, especially the fact that we edit in place while iterating
# def out_shift(G,intersecting_family):
#     internals = [x for x in G.nodes() if x[0] == 'V']
#     pendants = [x for x in G.nodes() if x[0] == 'P']
#     family_of_lists = [list(x) for x in intersecting_family]

#     for i in range(len(internals)):
#         for list_ in family_of_lists:
#             # shifting definition applied
#             if internals[i] in list_:
#                 target = list_
#                 print("list",list_)
#                 index = list_.index(internals[i])
#                 target[index] = pendants[i]
#                 print("target",target)
#                 if set(target) not in [set(x) for x in family_of_lists]:
#                     family_of_lists.remove(list_)
#                     family_of_lists.append(target) 
#             print(family_of_lists)
#     shifted_family = [tuple(x) for x in family_of_lists]
#     return shifted_family

'''Version 2, better time complexity and does not have bugs with iterating over the set'''
def out_shift(G,intersecting_family):

    internals = [x for x in G.nodes() if x[0] == 'V']
    pendants = [x for x in G.nodes() if x[0] == 'P']
    family_of_lists = [list(x) for x in intersecting_family]

    for i in range(len(internals)):
        shifted_family = []
        # use frozen set for better time complexity
        family_of_sets = [frozenset(x) for x in family_of_lists]

        for list_ in family_of_lists:
            if internals[i] not in list_:
                shifted_family.append(list_)
            else:
                #apply definition of shift
                target = list_.copy()
                index = list_.index(internals[i])
                target[index] = pendants[i]
                if set(target) not in family_of_sets:
                    shifted_family.append(target)
                else:
                    # if shifted set already in family of sets, append set
                    shifted_family.append(list_)
        family_of_lists = shifted_family 
    
    shifted_family = [tuple(x) for x in family_of_lists]
    return shifted_family

'''Not sure why I created this method, but it's here anyway'''
def check_duplicates(list_):
    # we want a set of sets, which Python doesn't allow, so we need another method
    hash_dict = {}
    res = []
    for s in list_:
        # use frozenset since sets are unhashable
        if frozenset(s) in hash_dict:
            res.append(s)
        else:
            hash_dict[frozenset(s)] = 1
    return len(res) > 0

def internals_per_set(G,family):
    max_internals = 0
    internals = {x for x in G.nodes() if x[0] == 'V'}
    family = [set(x) for x in family]

    for f in family:
        n = len(f.intersection(internals))
        if n > max_internals:
            max_internals = n
    return max_internals

'''need this to find "anchor" for our rotate shift'''
def greatest_intersection(G,family):
    pendants = [x for x in G.nodes() if x[0] == 'P']
    out = {}
    for p in pendants:
        out[p] = 0
    for set_ in family:
        for e in set_:
            if e[0] == "P":
                out[e] += 1
    return max(out, key=out.get)

def standardize(G,intersecting_family):
    # standardize set to be centered at p1 but moving largest center to p1
    standardized_family = []
    # gets star number
    p = int(greatest_intersection(G,intersecting_family)[1])
    n = int(len(G.nodes)/2)
    # add by:
    num = n-p+1
    for set_ in intersecting_family:
        standard_set = []
        for vertex in set_:
            new_index = new_index = int((int(vertex[1]) + num) % n) or n # 0 = 'False'
            standard_set.append(vertex[0] + str(new_index))
        standardized_family.append(standard_set)
    standardized_family = [tuple(x) for x in standardized_family]

    return standardized_family

def compress_set(vertices,res,count):
    
    if count == 1:
        vertices = list(vertices)
        #Sorting dealt with later, before we call compress since the order of compression matters
        #vertices.sort(key=lambda x: int(x[1:])) # sorts by index of vertices

    if len(vertices) == 0:
        return res
    
    if int(vertices[0][1]) == count:
        count += 1
        res.append(vertices[0])
        return compress_set(vertices[1:],res,count)
    
    else:
        for x in vertices:
            res.append(x[0] + str(int(x[1]) - 1)) # X_i -> X_{i-1}
        return res

def compress_family(intersecting_family):
    res = []
    shifted_family = []
    print(f"{intersecting_family=}")
    intersecting_family = [list(x) for x in intersecting_family]
    for s in intersecting_family:
        s.sort(key=lambda x: int(x[1:]))
        shifted_family.append(s)

    # Sorts further. Breaks each set into e.g. [(1,P),(2,V)] then it will sort using that as its key
    # print(f"{intersecting_family=}")
    # row is something like ['P1', 'P3', 'P6']
    sorted_family = sorted(intersecting_family, key=lambda row : [(int(c[1:]),c[0]) for c in row])

    for i in range(len(sorted_family)):
        comp_set = compress_set(sorted_family[i],[],1)

        # definition of my compression algorithm
        if comp_set not in res:
            # print(comp_set in res)
            # print("appended this set!", comp_set)
            res.append(comp_set)
            #print("pass",i,res)
        else:
            temp = comp_set.copy()
            last = comp_set[len(comp_set) - 1]
            if last[0] == 'P':
                comp_set[len(comp_set) - 1] = 'V' + str(int(last[1]) + 1) #add one because we want pre-compressed number
            elif last[0] == 'V':
                comp_set[len(comp_set) - 1] = 'P' + str(int(last[1]) + 1)
            
            if comp_set in res:
                res.append(temp)
            else:
                res.append(comp_set)
            #print("pass", i, res)
    s = [tuple(x) for x in res] 
    return s

g = cycle_graph(6)
i = create_intersecting_family(g,3)
#print(i)

shift = out_shift(g,i)
#print(shift)
#print(greatest_intersection(g,shift))

st = standardize(g,shift)
#print(st)
comp = compress_family(st)
#print(comp)