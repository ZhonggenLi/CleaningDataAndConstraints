import queue as Q
import copy
from bNDCRepair import Constraint,Detect
import pandas as pd
import numba as nb

class q_item:
    def __init__(self, i, s):
        self.seq = i
        self.rel = s
    def __eq__(self, other):
        if self.seq == other.seq:
            return True
        else:
            return False


def cost_ConSet(conset,lst,lamb):
    cost = 0
    for x in lst:
        cost+=len(x)
    return cost

def not_visit(lst, visited_state):
    for x in visited_state:
        if x == lst:
            return False
    return True

@nb.jit()
def repair(lst,C,I):
    cost = 0
    for t in range(len(I)-1):
        for i in range(len(C)):
            result = True
            for p in C[i]:
                p_str = p.split(' ')
                if len(p_str[2])>1:
                    if p_str[1] == '<':
                        result = result & (I[int(p_str[0])].iloc[t] < float(p_str[2]))
                    elif p_str[1] == '>':
                        result = result & (I[int(p_str[0])].iloc[t] > float(p_str[2]))
                    elif p_str[1] == '<=':
                        result = result & (I[int(p_str[0])].iloc[t] <= float(p_str[2]))
                    elif p_str[1] == '>=':
                        result = result & (I[int(p_str[0])].iloc[t] >= float(p_str[2]))
                    elif p_str[1] == '=':
                        result = result & (I[int(p_str[0])].iloc[t] == float(p_str[2]))
                elif len(p_str[2])==1:
                    if p_str[1] == '<':
                        result = result & (I[int(p_str[0])].iloc[t] < I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '>':
                        result = result & (I[int(p_str[0])].iloc[t] > I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '<=':
                        result = result & (I[int(p_str[0])].iloc[t] <= I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '>=':
                        result = result & (I[int(p_str[0])].iloc[t] >= I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '=':
                        result = result & (I[int(p_str[0])].iloc[t] == I[int(p_str[2])].iloc[t+1])
            if len(lst)>0 and len(lst[i])>0:
                for it in lst[i]:
                    if it.rel == '<=':
                        result = result & (I[it.seq].iloc[t] <= I[it.seq].iloc[t+1])
                    else:
                        result = result & (I[it.seq].iloc[t] >= I[it.seq].iloc[t + 1])
            if result == True:
                cost+=1
    return cost

def select_rel(seq,con_id,C,I,lst):
    temp1 = q_item(seq,'>=')
    temp2 = q_item(seq,'<=')
    lst_cpy1 = copy.deepcopy(lst)
    lst_cpy2 = copy.deepcopy(lst)
    lst_cpy1[con_id].append(temp1)
    lst_cpy2[con_id].append(temp2)
    if repair(lst_cpy1,C,I) > repair(lst_cpy2,C,I):
        return '<='
    else:
        return '>='

def not_in(item_list,k):
    for itt in item_list:
        if itt.seq == k:
            return False
    return True

def addCons(C, I, col, theta, lamb, maxp):
    Mincost = 1e10
    MinCons = None
    visited_state = []
    queue = Q.Queue()

    for i in range(len(C)):
        for j in range(col):
            temp = [[] for x in range(len(C))]
            temp_item = q_item(j,select_rel(j,i,C,I,[[] for x in range(len(C))]))
            temp[i].append(temp_item)
            queue.put(temp)

    while not queue.empty():
        lst = queue.get()
        for iitt in lst:
            print('[ ', end='')
            for cc in iitt:
                print(cc.seq,end=' ')
            print(']',end=' ')
        print()

        if not_visit(lst, visited_state):
            if cost_ConSet(C, lst, lamb) > theta:
                continue

            visited_state.append(lst)

            if repair(lst, C, I) < Mincost:
                Mincost = repair(lst, C, I)
                MinCons = lst

            for j in range(len(lst)):
                if len(lst[j])<maxp:
                    for k in range(col):
                        if not_in(lst[j],k):
                            temp_list = copy.deepcopy(lst)
                            t_item = q_item(k,select_rel(k,j,C,I,lst))
                            temp_list[j] = lst[j] + [t_item]
                            queue.put(temp_list)
    return MinCons

def detect_DC(C,I):
    vio_list = []
    for t in range(len(I)-1):
        for i in range(len(C)):
            result = True
            for p in C[i]:
                p_str = p.split(' ')
                if len(p_str[2])>1:
                    if p_str[1] == '<':
                        result = result & (I[int(p_str[0])].iloc[t] < float(p_str[2]))
                    elif p_str[1] == '>':
                        result = result & (I[int(p_str[0])].iloc[t] > float(p_str[2]))
                    elif p_str[1] == '<=':
                        #print(I.loc[t,0])
                        result = result & (I[int(p_str[0])].iloc[t] <= float(p_str[2]))
                    elif p_str[1] == '>=':
                        result = result & (I[int(p_str[0])].iloc[t] >= float(p_str[2]))
                    elif p_str[1] == '=':
                        result = result & (I[int(p_str[0])].iloc[t] == float(p_str[2]))
                elif len(p_str[2])==1:
                    if p_str[1] == '<':
                        result = result & (I[int(p_str[0])].iloc[t] < I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '>':
                        result = result & (I[int(p_str[0])].iloc[t] > I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '<=':
                        result = result & (I[int(p_str[0])].iloc[t] <= I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '>=':
                        result = result & (I[int(p_str[0])].iloc[t] >= I[int(p_str[2])].iloc[t+1])
                    elif p_str[1] == '=':
                        result = result & (I[int(p_str[0])].iloc[t] == I[int(p_str[2])].iloc[t+1])

            if result == True:
                for pp in C[i]:
                    pp_str = pp.split(' ')
                    vio_list.append((t,int(pp_str[0])))
    return vio_list

if __name__ == '__main__':
    # Constraints to be Repaired
    C = [['0 >= 4000'], ['0 <= 0.0'], ['1 <= -6'], ['1 >= -1']]

    I = pd.read_csv("../DataSample/IDF-1w-5%.csv", header = None)

    # Call the algorithm
    res = addCons(C,I,col=2,theta=3,lamb=-0.5,maxp=2)

    # Print results
    print("result: ")
    for i in range(len(res)):
        print('[ ',end='')
        for item in res[i]:
            print(str(item.seq)+item.rel+str(item.seq)+' ',end='')
            s = str(item.seq)+' '+item.rel+' '+str(item.seq)
            C[i].append(s)
        print(']')
    print('results: ')
    print(C)
    print(repair([],C,I))

    # Ground Truth Constraints
    c1 = Constraint('a', 0, 6475.96387, {0}, 1)
    c2 = Constraint('b', -4.92642, -1.79391, {1}, 1)

    C_truth = {c1,c2}

    # Calculate Precision and Recall

    vio_dc = detect_DC(C, I)

    R_truth = Detect(C_truth, I)

    Point_our = set(vio_dc)
    Point_truth = set()

    for pp in R_truth:
        Point_truth.add((pp[0], pp[1]))

    Point_all = set()
    for i in range(len(I)):
        for j in range(len(I.columns)):
            Point_all.add((i, j))

    TP = len(Point_all - (Point_our | Point_truth))
    TN = len(Point_our & Point_truth)
    FP = len((Point_all - Point_our) & Point_truth)
    FN = len(Point_our & (Point_all - Point_truth))
    print(TP, TN, FP, FN)

    P = TP / (TP + FP)
    R = TP / (FN + TP)
    print('Precision: ' + str(TP / (TP + FP)), 'Recall: ' + str(TP / (FN + TP)))