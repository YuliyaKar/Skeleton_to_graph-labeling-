# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 14:05:58 2016

Contains the functions necessary to transform the 3D skeleton
into a graph using the initial labeling of the input binary array as
nodes and branches on the base of the neighborhood of each point.
"""

from skimage import measure, morphology
from skimage import util
import numpy as np
from scipy import ndimage, signal
import networkx as nx
import tables as tb
import numpy as np

#This function now does not create triple branches and works properly.
#It uses uniform filter.
def numb(c) :
    """
    Counts the number of neighboring 1 for every nonzero
    element in 3D.
    
    Parameters
    ------
    skel_mat : 3d binary array
    
    Returns
    ------
    arr : The array of uint8 of the same size as skel_mat 
    with the elements equal to the number of neighbors 
    for the current point.
    
    Examples
    ------
    >>> a = np.random.random_integers(0,1,(3,3,3))
    >>> a 
    array([[[0, 0, 1],
            [0, 1, 1],
            [1, 0, 1]],        
           [[1, 0, 1],
            [1, 0, 1],
            [1, 1, 0]],        
           [[1, 1, 1],
            [1, 0, 0],
            [1, 1, 0]]])
    >>> neigh = numb(a)
    >>> neigh 
    array([[[ 0,  0,  4],
            [ 0, 10,  6],
            [ 4,  0,  4]],            
           [[ 5,  0,  6],
            [10,  0,  9],
            [ 7, 10,  0]],            
           [[ 4,  7,  3],
            [ 8,  0,  0],
            [ 5,  6,  0]]], dtype=uint8)
    """

    fil = 3**3 * ndimage.uniform_filter(c.astype('float32'), 3, mode='constant')
    mask = c>0
    return (fil.astype('int8') * mask) - 1
 
#Here I tried different methods, but they are slower.   
#def numb_convolve(c):
#    cube = np.ones((3,3,3))
#    fil = signal.convolve(c, cube, mode='same') - 1
#    return (fil * c).astype('uint8')
#    
#def numb_un_f(c):
#    fil = 3**3 * ndimage.uniform_filter(c.astype('float32'), 3, mode='constant') - 1
#    mask = c>0
#    return fil.astype('uint8') * mask


def label_br(num):
    """
    Returns the array where each region of points with the number
    of neighbors 1 or 2 is labeled from 1 to N, where N is the
    number of regions.
    
    Parameters
    ---------
    num : a 3D array counting the number of neighbors at each point
    
    Returns
    -------
    arr : an array of the same shape as the input with labeled regions
    
    Examples
    --------
    >>>c = np.zeros((3,4,3))
    >>>c[1,:,0] = c[1, 1,:] = 1
    array([[[ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.]],
           [[ 1.,  0.,  0.],
            [ 1.,  1.,  1.],
            [ 1.,  0.,  0.],
            [ 1.,  0.,  0.]],
           [[ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.]]])
    >>>num = numb(c)
    >>>num
    array([[[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
           [[2, 0, 0],
            [3, 4, 1],
            [3, 0, 0],
            [1, 0, 0]],
           [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]], dtype=uint8)
    >>>label_br(num)
    array([[[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
           [[1, 0, 0],
            [0, 0, 2],
            [0, 0, 0],
            [3, 0, 0]],
           [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]], dtype=uint8)   
    """
    br2 = num == 2
    branches = br2
    label_branches = measure.label(branches, background=0)
    return label_branches.astype('uint32')

 
def label_nodes(num):
    """
    Returns the array where each region of points with the number
    of neighbors more than 3 is labeled from 1 to N, where N is the
    number of regions.
    
    Parameters
    ---------
    num : a 3D array counting the number of neighbors at each point
    
    Returns
    -------
    arr : an array of the same shape as the input with labeled regions
    
    Examples
    --------
    >>>c = np.zeros((3,4,3))
    >>>c[1,:,0] = c[1, 1,:] = 1
    array([[[ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.]],
           [[ 1.,  0.,  0.],
            [ 1.,  1.,  1.],
            [ 1.,  0.,  0.],
            [ 1.,  0.,  0.]],
           [[ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.]]])
    >>>num = numb(c)
    >>>num
    array([[[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
           [[2, 0, 0],
            [3, 4, 1],
            [3, 0, 0],
            [1, 0, 0]],
           [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]], dtype=uint8)
    >>>label_nodes(num)
    array([[[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
           [[0, 0, 0],
            [1, 1, 0],
            [1, 0, 0],
            [0, 0, 0]],
           [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]], dtype=uint8) 
    """
    n1 = num>2
    n2 = num==1
    no = n1 + n2
    label_n = measure.label(no, background=0)
    return label_n.astype('uint32')
    
def label_iso(num):
    no = num==0
    label_iso = measure.label(no, background=0)
    return label_iso.astype('uint32')    
    
    
#This function is used for clearing the borders and applied to
#both branches and nodes arrays.    
def rem_bound(arr_br):
    """
    Function clears the borders by removing the branches
    that touches them.
    
    Parameters
    ---------
    arr_br : array that contains labeled branches
    
    Examples
    --------
    >>>arr_br
    >>>array([[[1, 0, 0, 0, 2],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]],
              [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 3, 0, 0],
               [0, 0, 3, 0, 0],
               [0, 0, 0, 0, 0]],
              [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]],
              [[4, 0, 0, 0, 5],
               [0, 4, 0, 5, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 6, 0, 0],
               [0, 0, 6, 0, 0]],
              [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]]], dtype=uint16)
    >>>rem_bound(arr_br)
    >>>array([[[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]],
              [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 3, 0, 0],
               [0, 0, 3, 0, 0],
               [0, 0, 0, 0, 0]],
              [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]],
              [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]],
              [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]]], dtype=uint16)

    """
    find_br = ndimage.find_objects(arr_br)
    a = np.copy(arr_br)
    n0 = a.shape[0] - 1
    n1 = a.shape[1] - 1
    n2 = a.shape[2] - 1
    for i in np.unique(arr_br[0,:,:])[1:]:
        mask = a[find_br[i-1]]==i
        a[find_br[i-1]] = a[find_br[i-1]] - mask * i
    for i in np.unique(arr_br[n0,:,:])[1:]:
        mask = a[find_br[i-1]]==i
        a[find_br[i-1]] = a[find_br[i-1]] - mask * i
    for i in np.unique(arr_br[:,0,:])[1:]:
        mask = a[find_br[i-1]]==i
        a[find_br[i-1]] = a[find_br[i-1]] - mask * i
    for i in np.unique(arr_br[:,n1,:])[1:]:
        mask = a[find_br[i-1]]==i
        a[find_br[i-1]] = a[find_br[i-1]] - mask * i
    for i in np.unique(arr_br[:,:,0])[1:]:
        mask = a[find_br[i-1]]==i
        a[find_br[i-1]] = a[find_br[i-1]] - mask * i
    for i in np.unique(arr_br[:,:,n2])[1:]:
        mask = a[find_br[i-1]]==i
        a[find_br[i-1]] = a[find_br[i-1]] - mask * i
    return a
    
   
def neigh_br(arr_nodes, arr_br):
    """
    Creates a graph with nodes from the array of nodes and branches
    by considering the branches that adjoin to the current node.
    The labels of these branches are set as an attribute of the
    node.
    
    Parameters
    ---------
    arr_nodes : array of labeled regions that are considered as nodes
    arr_br : array of labeled regions considered as branches
    
    Returns
    ------
    G : a graph of nodes with the attribute 'neigh' 
    
    Examples
    -------
    >>>arr_nodes = label_nodes(num)
    >>>arr_nodes
    array([[[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
           [[0, 0, 0],
            [1, 1, 0],
            [1, 0, 0],
            [0, 0, 0]],
           [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]], dtype=uint8) 
    >>>arr_br = label_br(num)
    >>>arr_br
    array([[[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
           [[1, 0, 0],
            [0, 0, 2],
            [0, 0, 0],
            [3, 0, 0]],
           [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]], dtype=uint8) 
    >>>G = neigh_br(arr_nodes, arr_br)
    >>>G.nodes()
    [1]
    >>>nx.get_node_attributes(G, 'neigh')
    {1: array([1, 2, 3])}
    
    """
    G = nx.MultiGraph()
    nodes = np.unique(arr_nodes)[1:]
    find_nodes = ndimage.find_objects(arr_nodes)
    start = np.zeros(3)
    stop = np.zeros(3)
    cube = morphology.cube(3)
    size0 = arr_nodes.shape[0]
    size1 = arr_nodes.shape[1]
    size2 = arr_nodes.shape[2]
    for j in nodes:
        sl = find_nodes[j-1]
        mask = np.zeros((size0,size1,size2))  
        mask[sl] = arr_nodes[sl]==j
        posit = ndimage.measurements.center_of_mass(mask[sl])
        pos = np.zeros(3)
        for i in range(3):
            start[i] = sl[i].start - 1
            stop[i] = sl[i].stop + 1
            pos[i] = posit[i] + start[i] + 1
        #volume with node
        vol_c_n = mask[start[0]:stop[0], start[1]:stop[1],
                       start[2]:stop[2]] 
        #dilation to find the joint branches               
        dil = ndimage.binary_dilation(vol_c_n, cube)
        dil = dil.astype('uint8')
        vol_c = arr_br[start[0]:stop[0], start[1]:stop[1],
                       start[2]:stop[2]] 
        #find the labels of connected branches
        n = np.unique(vol_c * dil)[1:]
        G.add_node(j, neigh = n, position = pos)
    
    return G


    
def create_con(graph, arr_br, th):
    """
    Creates the edges in the input graph with nodes that have
    the labels of adjoint branches as an attribute 'neigh'.
    End nodes are created while adding the edges to the graph and
    do not have the attribute 'neigh'. The edges have the attribute
    'length' that counts the number of elements in the branch and
    corresponds to the length of the branch.
    
    Parameters
    ---------
    graph : a graph of nodes
    arr_br : array of labeled regions considered as branches
    th : the list of mean thicknesses of branches    
    
    Returns
    -------
    G : a copy of the input graph with edges and end nodes added
    
    Examples
    --------
    >>>c = np.zeros((3,4,3))
    >>>c[1,:,0] = c[1, 1,:] = 1
    array([[[ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.]],
           [[ 1.,  0.,  0.],
            [ 1.,  1.,  1.],
            [ 1.,  0.,  0.],
            [ 1.,  0.,  0.]],
           [[ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.],
            [ 0.,  0.,  0.]]])
    >>>G = neigh_br(arr_nodes, arr_br)
    >>>G.nodes()
    [1]
    >>>nx.get_node_attributes(G, 'neigh')
    {1: array([1, 2, 3])}
    >>>G_con = create_con(G, arr_br)
    >>>G_con.nodes()
    [1, 2, 3, 4]
    >>>G_con.edges()
    [(1, 2), (1, 3), (1, 4)]
    >>>nx.get_edge_attributes(G_con, 'length')
    {(1, 2): 1, (1, 3): 1, (1, 4): 1}    
    """
    
    G = graph.copy()
    n = nx.get_node_attributes(G, 'neigh')
    list_br = [] #the list doesn't influence the code, it just stores
                 #all branches that have been written to the graph as edges.
    le = list()
    num_of_nodes = nx.number_of_nodes(G)
    nodes = []
    for i in G.nodes():
        nodes = np.append(nodes, i)
    find_br = ndimage.find_objects(arr_br)
    un = np.unique(arr_br)[1:]
    for k in un:
        mask = arr_br[find_br[k-1]]
        le.append(np.count_nonzero(mask))
    le_dict = dict(zip(un, le)) #dictionary of lengthes
    th_dict = dict(zip(un, th))
    br_dict = {} #dictionary of branches
    for k in n:
        for v in n[k]:
            br_dict.setdefault(v, []).append(k)
    for k in br_dict:
        n1 = br_dict[k][0]
        if len(br_dict[k])==2:
            n2 = br_dict[k][1]
            G.add_edge(min(n1,n2), max(n1, n2), length = le_dict[k], thick = th_dict[k], number=[k])
            list_br = np.append(list_br, k)
        if len(br_dict[k])==1:
            num_of_nodes += 1
            G.add_edge(min(n1, num_of_nodes), max(n1, num_of_nodes), length = le_dict[k], thick = th_dict[k], number=[k])
            list_br = np.append(list_br, k)
        if len(br_dict[k])>2: #test
            error

    return G

#If it is necessary to take into account the isolated nodes and
#include them to graph
def add_isol_nodes(graph, arr_iso):
    G = graph.copy()
    nodes = np.unique(arr_iso)[1:]
    n = nx.number_of_nodes(G)
    for i in nodes:
        G.add_node(n+1)
        n+=1
    return G
  