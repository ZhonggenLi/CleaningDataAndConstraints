import copy

import pandas as pd


class Constraint:
    def __init__(self, name, feature1, feature2, s, type):
        self.name = name
        self.feature1 = feature1
        self.feature2 = feature2
        self.s = s
        self.type = type

class ConsViolation:
    def __init__(self, t, s, c):
        self.t = t
        self.s = s
        self.c = c

def cost_2(c,c_t):
    if c_t.feature1 <= c.feature1 and c_t.feature2 >= c.feature2:
        return ((c.feature1-c_t.feature1) + (c_t.feature2-c.feature2))/\
               ((c_t.feature2-c_t.feature1)+(c.feature2-c.feature1))
    elif c.feature1 <= c_t.feature1 and c.feature2 >= c_t.feature2:
        return ((c_t.feature1 - c.feature1) + (c.feature2 - c_t.feature2)) / \
               ((c.feature2 - c.feature1) + (c_t.feature2 - c_t.feature1))
    else:
        return None

def cost_1(I,C):
    cost = 0
    for i in range(len(I)):
        for c in C:
            if c.type == 1:
                if I[list(c.s)[0]].iloc[i] < c.feature1:
                    cost += (c.feature1 - I[list(c.s)[0]].iloc[i])
                elif I[list(c.s)[0]].iloc[i] > c.feature2:
                    cost += (I[list(c.s)[0]].iloc[i] - c.feature2)
            elif c.type == 2 and i > 0:
                if abs(I[list(c.s)[0]].iloc[i-1] - I[list(c.s)[0]].iloc[i]) > c.feature2:
                    cost += (abs(I[list(c.s)[0]].iloc[i-1] - I[list(c.s)[0]].iloc[i])-c.feature2)
                elif abs(I[list(c.s)[0]].iloc[i-1] - I[list(c.s)[0]].iloc[i]) < c.feature1:
                    cost += (c.feature1 - abs(I[list(c.s)[0]].iloc[i-1] - I[list(c.s)[0]].iloc[i]))
            elif c.type == 3 and c.name == 'f':
                if I[1].iloc[i]/I[2].iloc[i] > c.feature2:
                    cost += (I[1].iloc[i]/I[2].iloc[i]- c.feature2)
                elif I[1].iloc[i]/I[2].iloc[i] < c.feature1:
                    cost += (c.feature1 - I[1].iloc[i] / I[2].iloc[i])
            elif c.type==3 and c.name == 'g':
                if I[4].iloc[i]/(I[0].iloc[i]+I[3].iloc[i]) > c.feature2:
                    cost+= (I[4].iloc[i]/(I[0].iloc[i]+I[3].iloc[i])-c.feature2)
                elif I[4].iloc[i]/(I[0].iloc[i]+I[3].iloc[i]) < c.feature1:
                    cost += (c.feature1 - I[4].iloc[i] / (I[0].iloc[i] + I[3].iloc[i]))
    return cost

def ConstraintShrink(miu,c, d_min, d_max, S, T, lamb, I, C):
    d_min_t = d_min
    d_max_t = d_max
    MinCost = lamb * cost_1(I,{c})
    for t in T:
        if c.type == 1:
            if d_min_t <= I[list(c.s)[0]].iloc[t] and d_max_t >= I[list(c.s)[0]].iloc[t]:
                c_res_1 = Constraint(c.name, c.feature1, I[list(c.s)[0]].iloc[t], c.s, c.type)
                c_res_2 = Constraint(c.name, I[list(c.s)[0]].iloc[t], c.feature2, c.s, c.type)
                flag = 0
                if cost_1(I, {c_res_1}) > cost_1(I, {c_res_2}):
                    c_update = c_res_2
                else:
                    c_update = c_res_1
                    flag = 1
                if flag == 1 and miu*(I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t-d_min_t+I[list(c.s)[0]].iloc[t]-d_min_t)+lamb*cost_1(I,{c_update})<MinCost:
                    d_max_t = I[list(c.s)[0]].iloc[t]
                    d_min_t = c_update.feature1
                    MinCost = miu*(I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t-d_min_t+I[list(c.s)[0]].iloc[t]-d_min_t)+lamb*cost_1(I,{c_update})
                elif flag == 0:
                    c_update.feature1 = I[list(c.s)[0]].iloc[t]
                    c_update.feature2 = c.feature2
                    if miu*(d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t-d_min_t+d_max_t-I[list(c.s)[0]].iloc[t])+lamb*cost_1(I,{c_update})<MinCost:
                        d_min_t = I[list(c.s)[0]].iloc[t]
                        d_max_t = c_update.feature2
                        MinCost = miu*(d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t-d_min_t+d_max_t-I[list(c.s)[0]].iloc[t])+lamb*cost_1(I,{c_update})
        elif c.type == 2 and t>0:
            if d_min_t <= abs(I[list(c.s)[0]].iloc[t-1]-I[list(c.s)[0]].iloc[t]) and d_max_t >= abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]):
                c_res_1 = Constraint(c.name, c.feature1, abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]), c.s, c.type)
                c_res_2 = Constraint(c.name, abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]), c.feature2, c.s, c.type)
                flag = 0
                if cost_1(I, {c_res_1}) > cost_1(I, {c_res_2}):
                    c_update = c_res_2
                else:
                    c_update = c_res_1
                    flag = 1
                if flag == 1 and miu*(abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]) - d_max_t) / (d_max_t-d_min_t+abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])-d_min_t)+lamb*cost_1(I,{c_update})<MinCost:
                    d_max_t = abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])
                    d_min_t = c_update.feature1
                    MinCost = miu*(abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]) - d_max_t) / (d_max_t-d_min_t+abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])-d_min_t)+lamb*cost_1(I,{c_update})
                elif flag == 0:
                    c_update.feature1 = abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])
                    c_update.feature2 = c.feature2
                    if miu*(d_min_t - abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])) / (d_max_t-d_min_t+d_max_t-abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]))+lamb*cost_1(I,{c_update})<MinCost:
                        d_min_t = abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])
                        d_max_t = c_update.feature2
                        MinCost = miu*(d_min_t - abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])) / (d_max_t-d_min_t+d_max_t-abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]))+lamb*cost_1(I,{c_update})
        elif c.type == 3:
            if c.name=='g':
                temp = I[4].iloc[t]/(I[0].iloc[t]+I[3].iloc[t])
            elif c.name == 'f':
                temp = I[1].iloc[t] / I[2].iloc[t]
            if d_min_t <= temp and d_max_t >= temp:
                c_res_1 = Constraint(c.name, c.feature1, temp, c.s, c.type)
                c_res_2 = Constraint(c.name, temp, c.feature2, c.s, c.type)
                flag = 0
                if cost_1(I, {c_res_1}) > cost_1(I, {c_res_2}):
                    c_update = c_res_2
                else:
                    c_update = c_res_1
                    flag = 1
                if flag == 1 and miu*(temp - d_max_t) / (d_max_t-d_min_t+temp-d_min_t)+lamb*cost_1(I,{c_update})<MinCost:
                    d_max_t = temp
                    d_min_t = c_update.feature1
                    MinCost = miu*(temp - d_max_t) / (d_max_t-d_min_t+temp-d_min_t)+lamb*cost_1(I,{c_update})
                elif flag == 0:
                    c_update.feature1 = temp
                    c_update.feature2 = c.feature2
                    if miu*(d_min_t - temp) / (d_max_t-d_min_t+d_max_t-temp)+lamb*cost_1(I,{c_update})<MinCost:
                        d_min_t = temp
                        d_max_t = c_update.feature2
                        MinCost = miu*(d_min_t - temp) / (d_max_t-d_min_t+d_max_t-temp)+lamb*cost_1(I,{c_update})
    return Constraint(c.name, d_min_t, d_max_t, c.s, c.type)

def ConstraintShrinkStar(miu, c, d_min, d_max, S, T, lamb, I, C):
    d_min_t = d_min
    d_max_t = d_max
    MinCost = lamb * cost_1(I,C)
    for t in T:
        if c.type == 1:
            if d_min_t <= I[list(c.s)[0]].iloc[t] and d_max_t >= I[list(c.s)[0]].iloc[t]:
                c_res_1 = Constraint(c.name, c.feature1, I[list(c.s)[0]].iloc[t], c.s, c.type)
                c_res_2 = Constraint(c.name, I[list(c.s)[0]].iloc[t], c.feature2, c.s, c.type)
                flag = 0
                if cost_1(I, {c_res_1}) > cost_1(I, {c_res_2}):
                    c_update = c_res_2
                else:
                    c_update = c_res_1
                    flag = 1
                if flag == 1 and miu*(I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t-d_min_t+I[list(c.s)[0]].iloc[t]-d_min_t)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))<MinCost:
                    d_max_t = I[list(c.s)[0]].iloc[t]
                    d_min_t = c_update.feature1
                    MinCost = miu*(I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t-d_min_t+I[list(c.s)[0]].iloc[t]-d_min_t)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))
                elif flag == 0:
                    c_update.feature1 = I[list(c.s)[0]].iloc[t]
                    c_update.feature2 = c.feature2
                    if miu*(d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t-d_min_t+d_max_t-I[list(c.s)[0]].iloc[t])+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))<MinCost:
                        d_min_t = I[list(c.s)[0]].iloc[t]
                        d_max_t = c_update.feature2
                        MinCost = miu*(d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t-d_min_t+d_max_t-I[list(c.s)[0]].iloc[t])+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))
        elif c.type == 2 and t>0:
            if d_min_t <= abs(I[list(c.s)[0]].iloc[t-1]-I[list(c.s)[0]].iloc[t]) and d_max_t >= abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]):
                c_res_1 = Constraint(c.name, c.feature1, abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]), c.s, c.type)
                c_res_2 = Constraint(c.name, abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]), c.feature2, c.s, c.type)
                flag = 0
                if cost_1(I, {c_res_1}) > cost_1(I, {c_res_2}):
                    c_update = c_res_2
                else:
                    c_update = c_res_1
                    flag = 1
                if flag == 1 and miu*(abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]) - d_max_t) / (d_max_t-d_min_t+abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])-d_min_t)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))<MinCost:
                    d_max_t = abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])
                    d_min_t = c_update.feature1
                    MinCost = miu*(abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]) - d_max_t) / (d_max_t-d_min_t+abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])-d_min_t)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))
                elif flag == 0:
                    c_update.feature1 = abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])
                    c_update.feature2 = c.feature2
                    if miu*(d_min_t - abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])) / (d_max_t-d_min_t+d_max_t-abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]))+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))<MinCost:
                        d_min_t = abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])
                        d_max_t = c_update.feature2
                        MinCost = miu*(d_min_t - abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1])) / (d_max_t-d_min_t+d_max_t-abs(I[list(c.s)[0]].iloc[t]-I[list(c.s)[0]].iloc[t-1]))+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))
        elif c.type == 3:
            if c.name=='g':
                temp = I[4].iloc[t]/(I[0].iloc[t]+I[3].iloc[t])
            elif c.name == 'f':
                temp = I[1].iloc[t] / I[2].iloc[t]
            if d_min_t <= temp and d_max_t >= temp:
                c_res_1 = Constraint(c.name, c.feature1, temp, c.s, c.type)
                c_res_2 = Constraint(c.name, temp, c.feature2, c.s, c.type)
                flag = 0
                if cost_1(I, {c_res_1}) > cost_1(I, {c_res_2}):
                    c_update = c_res_2
                else:
                    c_update = c_res_1
                    flag = 1
                if flag == 1 and miu*(temp - d_max_t) / (d_max_t-d_min_t+temp-d_min_t)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))<MinCost:
                    d_max_t = temp
                    d_min_t = c_update.feature1
                    MinCost = miu*(temp - d_max_t) / (d_max_t-d_min_t+temp-d_min_t)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))
                elif flag == 0:
                    c_update.feature1 = temp
                    c_update.feature2 = c.feature2
                    if miu*(d_min_t - temp) / (d_max_t-d_min_t+d_max_t-temp)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))<MinCost:
                        d_min_t = temp
                        d_max_t = c_update.feature2
                        MinCost = miu*(d_min_t - temp) / (d_max_t-d_min_t+d_max_t-temp)+lamb*(cost_1(I,{c_update})+cost_1(I,C-{c}))
    return Constraint(c.name, d_min_t, d_max_t, c.s, c.type)

def ConstraintExpand(c, d_min, d_max, S, T, lamb, I, C):
    d_min_t = d_min
    d_max_t = d_max
    MinCost = lamb * cost_1(I, {c})
    if len(T)>200:
        T=T[-200:]
    for t in T:
        if c.type == 1:
            if I[list(c.s)[0]].iloc[t] > d_max_t:
                c_update = Constraint(c.name, c.feature1, I[list(c.s)[0]].iloc[t], c.s, c.type)
                if (I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t - d_min_t + I[list(c.s)[0]].iloc[t] - d_min_t) + lamb * cost_1(I, {c_update}) < MinCost:
                    d_max_t = I[list(c.s)[0]].iloc[t]
                    d_min_t = c_update.feature1
                    MinCost = (I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t - d_min_t + I[list(c.s)[0]].iloc[t] - d_min_t) + lamb * cost_1(I, {c_update})
            elif I[list(c.s)[0]].iloc[t] < d_min_t:
                c_update = Constraint(c.name, I[list(c.s)[0]].iloc[t], c.feature2, c.s, c.type)
                if (d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t - d_min_t + d_max_t - I[list(c.s)[0]].iloc[t]) + lamb * cost_1(I, {c_update}) < MinCost:
                    d_min_t = I[list(c.s)[0]].iloc[t]
                    d_max_t = c_update.feature2
                    MinCost = (d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t - d_min_t + d_max_t - I[list(c.s)[0]].iloc[t]) + lamb * cost_1(I, {c_update})
        elif c.type == 2 and t > 0:
            temp = abs(I[list(c.s)[0]].iloc[t-1] - I[list(c.s)[0]].iloc[t])
            if temp > d_max_t:
                c_update = Constraint(c.name, c.feature1, temp, c.s, c.type)
                if (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * cost_1(I, {c_update}) < MinCost:
                    d_max_t = temp
                    d_min_t = c_update.feature1
                    MinCost = (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * cost_1(I, {c_update})
            elif temp < d_min_t:
                c_update = Constraint(c.name, temp, c.feature2, c.s, c.type)
                if (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * cost_1(I, {c_update}) < MinCost:
                    d_min_t = temp
                    d_max_t = c_update.feature2
                    MinCost = (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * cost_1(I, {c_update})
        elif c.type == 3:
            if c.name=='g':
                temp = I[4].iloc[t]/(I[0].iloc[t]+I[3].iloc[t])
            elif c.name == 'f':
                temp = I[1].iloc[t] / I[2].iloc[t]
            if temp > d_max_t:
                c_update = Constraint(c.name, c.feature1, temp, c.s, c.type)
                if (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * cost_1(I, {c_update}) < MinCost:
                    d_max_t = temp
                    d_min_t = c_update.feature1
                    MinCost = (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * cost_1(I, {c_update})
            elif temp < d_min_t:
                c_update = Constraint(c.name, temp, c.feature2, c.s, c.type)
                if (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * cost_1(I, {c_update}) < MinCost:
                    d_min_t = temp
                    d_max_t = c_update.feature2
                    MinCost = (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * cost_1(I, {c_update})
    return Constraint(c.name, d_min_t, d_max_t, c.s, c.type)

def ConstraintExpandStar(c, d_min, d_max, S, T, lamb, I, C):
    d_min_t = d_min
    d_max_t = d_max
    MinCost = lamb * cost_1(I, C)
    for t in T:
        if c.type == 1:
            if I[list(c.s)[0]].iloc[t] > d_max_t:
                c_update = Constraint(c.name, c.feature1, I[list(c.s)[0]].iloc[t], c.s, c.type)
                if (I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t - d_min_t + I[list(c.s)[0]].iloc[t] - d_min_t) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c})) < MinCost:
                    d_max_t = I[list(c.s)[0]].iloc[t]
                    d_min_t = c_update.feature1
                    MinCost = (I[list(c.s)[0]].iloc[t] - d_max_t) / (d_max_t - d_min_t + I[list(c.s)[0]].iloc[t] - d_min_t) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c}))
            elif I[list(c.s)[0]].iloc[t] < d_min_t:
                c_update = Constraint(c.name, I[list(c.s)[0]].iloc[t], c.feature2, c.s, c.type)
                if (d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t - d_min_t + d_max_t - I[list(c.s)[0]].iloc[t]) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c})) < MinCost:
                    d_min_t = I[list(c.s)[0]].iloc[t]
                    d_max_t = c_update.feature2
                    MinCost = (d_min_t - I[list(c.s)[0]].iloc[t]) / (d_max_t - d_min_t + d_max_t - I[list(c.s)[0]].iloc[t]) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c}))
        elif c.type == 2 and t > 0:
            temp = abs(I[list(c.s)[0]].iloc[t-1] - I[list(c.s)[0]].iloc[t])
            if temp > d_max_t:
                c_update = Constraint(c.name, c.feature1, temp, c.s, c.type)
                if (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c})) < MinCost:
                    d_max_t = temp
                    d_min_t = c_update.feature1
                    MinCost = (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c}))
            elif temp < d_min_t:
                c_update = Constraint(c.name, temp, c.feature2, c.s, c.type)
                if (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c})) < MinCost:
                    d_min_t = temp
                    d_max_t = c_update.feature2
                    MinCost = (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c}))
        elif c.type == 3:
            if c.name=='g':
                temp = I[4].iloc[t]/(I[0].iloc[t]+I[3].iloc[t])
            elif c.name == 'f':
                temp = I[1].iloc[t] / I[2].iloc[t]
            if temp > d_max_t:
                c_update = Constraint(c.name, c.feature1, temp, c.s, c.type)
                if (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c})) < MinCost:
                    d_max_t = temp
                    d_min_t = c_update.feature1
                    MinCost = (temp - d_max_t) / (d_max_t - d_min_t + temp - d_min_t) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c}))
            elif temp < d_min_t:
                c_update = Constraint(c.name, temp, c.feature2, c.s, c.type)
                if (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c})) < MinCost:
                    d_min_t = temp
                    d_max_t = c_update.feature2
                    MinCost = (d_min_t - temp) / (d_max_t - d_min_t + d_max_t - temp) + lamb * (cost_1(I, {c_update})+cost_1(I, C-{c}))
    return Constraint(c.name, d_min_t, d_max_t, c.s, c.type)

def ConstraintShrinkS(c, d_min, d_max, S, TimeInterval, I):
    d_min_t = d_min
    d_max_t = d_max
    value1 = d_max_t
    value2 = d_min_t
    value3 = d_max_t
    value4 = d_min_t
    delta = 0
    left = 0
    right = 0
    for T in TimeInterval:
        for t in T:
            temp = 0
            if c.type == 1:
                temp = I[list(c.s)[0]].iloc[t]
            elif c.type == 2:
                temp = abs(I[list(c.s)[0]].iloc[t-1]-I[list(c.s)[0]].iloc[t])
            else:
                if c.name == 'f':
                    temp = I[1].iloc[t] / I[2].iloc[t]
                elif c.name == 'g':
                    temp = I[4].iloc[t] / (I[0].iloc[t] + I[3].iloc[t])
            if temp - d_min_t > 0 and abs(temp-d_min_t)<abs(d_min_t-value1):
                value1 = temp
            if temp - d_max_t < 0 and abs(temp-d_max_t)<abs(d_max_t-value2):
                value2 = temp
            if temp - d_min_t > 0 and abs(temp-d_min_t)<abs(d_min_t-value3):
                value3 = temp
            if temp - d_max_t > 0 and abs(temp-d_max_t)<abs(d_max_t-value4):
                value4 = temp
        delta += min(abs(d_min_t-value1),abs(d_min_t-value3),abs(d_max_t-value2),abs(d_max_t-value4))/3
        if min(abs(d_min_t-value1),abs(d_min_t-value3),abs(d_max_t-value2),abs(d_max_t-value4)) == abs(d_min_t-value1)\
            or min(abs(d_min_t-value1),abs(d_min_t-value3),abs(d_max_t-value2),abs(d_max_t-value4)) == abs(d_min_t-value3):
            left += 1
        else:
            right += 1
    if left > right:
        return Constraint(c.name, c.feature1+delta, c.feature2, c.s, c.type)
    else:
        return Constraint(c.name, c.feature1, c.feature2-delta, c.s, c.type)

def ConstraintShrinkS_Star(c, d_min, d_max, S, TimeInterval, I, d_left_min, d_left_max, d_right_min, d_right_max):
    d_min_t = d_min
    d_max_t = d_max
    value1 = d_max_t
    value2 = d_min_t
    value3 = d_max_t
    value4 = d_min_t
    delta = 0
    left = 0
    right = 0
    for T in TimeInterval:
        for t in T:
            temp = 0
            if c.type == 1:
                temp = I[list(c.s)[0]].iloc[t]
            elif c.type == 2:
                temp = abs(I[list(c.s)[0]].iloc[t - 1] - I[list(c.s)[0]].iloc[t])
            else:
                if c.name == 'f':
                    temp = I[1].iloc[t] / I[2].iloc[t]
                elif c.name == 'g':
                    temp = I[4].iloc[t] / (I[0].iloc[t] + I[3].iloc[t])
            if temp - d_min_t > 0 and abs(temp - d_min_t) < abs(d_min_t - value1):
                value1 = temp
            if temp - d_max_t < 0 and abs(temp - d_max_t) < abs(d_max_t - value2):
                value2 = temp
            if temp - d_min_t > 0 and abs(temp - d_min_t) < abs(d_min_t - value3):
                value3 = temp
            if temp - d_max_t > 0 and abs(temp - d_max_t) < abs(d_max_t - value4):
                value4 = temp

        delta += min(abs(d_min_t-value1),abs(d_min_t-value3),abs(d_max_t-value2),abs(d_max_t-value4))/3
        if min(abs(d_min_t-value1),abs(d_min_t-value3),abs(d_max_t-value2),abs(d_max_t-value4)) == abs(d_min_t-value1)\
            or min(abs(d_min_t-value1),abs(d_min_t-value3),abs(d_max_t-value2),abs(d_max_t-value4)) == abs(d_min_t-value3):
            left += 1
        else:
            right += 1
    if left > right:
        if (c.feature1+delta) <= d_left_max and c.feature1+delta >= d_left_min:
            return Constraint(c.name, c.feature1+delta, c.feature2, c.s, c.type)
        elif c.feature1+delta < d_left_min:
            return Constraint(c.name, d_left_min, c.feature2, c.s, c.type)
        else:
            return Constraint(c.name, d_left_max, c.feature2, c.s, c.type)
    else:
        if c.feature2-delta <= d_right_max and c.feature2-delta >= d_right_min:
            return Constraint(c.name, c.feature1, c.feature2-delta, c.s, c.type)
        elif c.feature2-delta < d_right_min:
            return Constraint(c.name, c.feature1, d_right_min, c.s, c.type)
        else:
            return Constraint(c.name, c.feature1, d_right_max, c.s, c.type)

def ConstraintExpandS(c, d_min, d_max, S, TimeInterval, I):
    d_min_t = d_min
    d_max_t = d_max
    value1 = d_max_t
    value2 = d_min_t
    value3 = d_max_t
    value4 = d_min_t
    delta = 0
    left = 0
    right = 0
    for T in TimeInterval:
        for t in T:
            temp = 0
            if c.type == 1:
                temp = I[list(c.s)[0]].iloc[t]
            elif c.type == 2:
                temp = abs(I[list(c.s)[0]].iloc[t - 1] - I[list(c.s)[0]].iloc[t])
            else:
                if c.name == 'f':
                    temp = I[1].iloc[t] / I[2].iloc[t]
                elif c.name == 'g':
                    temp = I[4].iloc[t] / (I[0].iloc[t] + I[3].iloc[t])
            if temp - d_min_t > 0 and abs(temp - d_min_t) < abs(d_min_t - value1):
                value1 = temp
            if temp - d_max_t < 0 and abs(temp - d_max_t) < abs(d_max_t - value2):
                value2 = temp
            if temp - d_min_t > 0 and abs(temp - d_min_t) < abs(d_min_t - value3):
                value3 = temp
            if temp - d_max_t > 0 and abs(temp - d_max_t) < abs(d_max_t - value4):
                value4 = temp
        delta += min(abs(d_min_t - value1), abs(d_min_t - value3), abs(d_max_t - value2), abs(d_max_t - value4)) / 3
        if min(abs(d_min_t - value1), abs(d_min_t - value3), abs(d_max_t - value2), abs(d_max_t - value4)) == abs(
                d_min_t - value1) \
                or min(abs(d_min_t - value1), abs(d_min_t - value3), abs(d_max_t - value2),
                       abs(d_max_t - value4)) == abs(d_min_t - value3):
            left += 1
        else:
            right += 1
    if left > right:
        return Constraint(c.name, c.feature1-delta, c.feature2, c.s, c.type)
    else:
        return Constraint(c.name, c.feature1, c.feature2+delta, c.s, c.type)

def ConstraintExpandS_Star(c, d_min, d_max, S, TimeInterval, I, d_left_min, d_left_max, d_right_min, d_right_max):
    d_min_t = d_min
    d_max_t = d_max
    value1 = d_max_t
    value2 = d_min_t
    value3 = d_max_t
    value4 = d_min_t
    delta = 0
    left = 0
    right = 0
    for T in TimeInterval:
        for t in T:
            temp = 0
            if c.type == 1:
                temp = I[list(c.s)[0]].iloc[t]
            elif c.type == 2:
                temp = abs(I[list(c.s)[0]].iloc[t - 1] - I[list(c.s)[0]].iloc[t])
            else:
                if c.name == 'f':
                    temp = I[1].iloc[t] / I[2].iloc[t]
                elif c.name == 'g':
                    temp = I[4].iloc[t] / (I[0].iloc[t] + I[3].iloc[t])
            if temp - d_min_t > 0 and abs(temp - d_min_t) < abs(d_min_t - value1):
                value1 = temp
            if temp - d_max_t < 0 and abs(temp - d_max_t) < abs(d_max_t - value2):
                value2 = temp
            if temp - d_min_t > 0 and abs(temp - d_min_t) < abs(d_min_t - value3):
                value3 = temp
            if temp - d_max_t > 0 and abs(temp - d_max_t) < abs(d_max_t - value4):
                value4 = temp

        delta += min(abs(d_min_t - value1), abs(d_min_t - value3), abs(d_max_t - value2), abs(d_max_t - value4)) / 3
        if min(abs(d_min_t - value1), abs(d_min_t - value3), abs(d_max_t - value2), abs(d_max_t - value4)) == abs(
                d_min_t - value1) \
                or min(abs(d_min_t - value1), abs(d_min_t - value3), abs(d_max_t - value2),
                       abs(d_max_t - value4)) == abs(d_min_t - value3):
            left += 1
        else:
            right += 1
    if left > right:
        if (c.feature1-delta) <= d_left_max and c.feature1-delta >= d_left_min:
            return Constraint(c.name, c.feature1-delta, c.feature2, c.s, c.type)
        elif c.feature1-delta < d_left_min:
            return Constraint(c.name, d_left_min, c.feature2, c.s, c.type)
        else:
            return Constraint(c.name, d_left_max, c.feature2, c.s, c.type)
    else:
        if c.feature2+delta <= d_right_max and c.feature2+delta >= d_right_min:
            return Constraint(c.name, c.feature1, c.feature2+delta, c.s, c.type)
        elif c.feature2+delta < d_right_min:
            return Constraint(c.name, c.feature1, d_right_min, c.s, c.type)
        else:
            return Constraint(c.name, c.feature1, d_right_max, c.s, c.type)


def Rel(c,confidence,C,R_final):
    rel_c = []
    for c_ori in C:
        if c.name == c_ori.name:
            c = c_ori
    for c_other in C:
        if c in R_final.keys() and c_other.name != c.name:
            if rel(c,c_other,R_final)>=confidence:
                rel_c.append(c_other)
    return rel_c

def rel(c1,c2,R_final):
    j = 0
    i = 0
    interval = 0
    while i < len(R_final[c1]) and j < len(R_final[c2]):
        if R_final[c1][i][0][0] >= R_final[c2][j][0][0] and R_final[c1][i][0][0] <= R_final[c2][j][0][1]:
            if R_final[c1][i][0][1] <= R_final[c2][j][0][1]:
                interval += (R_final[c1][i][0][1] - R_final[c1][i][0][0] + 1)
                i += 1
            else:
                interval += (R_final[c2][j][0][1] - R_final[c1][i][0][0] + 1)
                j += 1
        elif R_final[c1][i][0][0] <= R_final[c2][j][0][0] and R_final[c2][j][0][0] <= R_final[c1][i][0][1]:
            if R_final[c2][j][0][1] <= R_final[c1][i][0][1]:
                interval += (R_final[c2][j][0][1] - R_final[c2][j][0][0] + 1)
                j += 1
            else:
                interval += (R_final[c1][i][0][1] - R_final[c2][j][0][0] + 1)
                i += 1
        elif R_final[c1][i][0][0] > R_final[c2][j][0][1]:
            j += 1
        elif R_final[c2][j][0][0] > R_final[c1][i][0][1]:
            i += 1
    return interval

def Detect(C, dataSet):
    R = []
    for i in range(len(dataSet)):
        for c in C:
            if c.type == 1:
                for j in c.s:
                    if dataSet.iloc[i,j] < c.feature1 or dataSet.iloc[i,j] > c.feature2:
                        R.append((i,j,c))
            elif c.type == 2:
                for j in c.s:
                    if dataSet.iloc[i,j]>=dataSet.iloc[i-1,j]:
                        R.append((i,j,c))
            elif c.type == 3:
                for j in c.s:
                    if dataSet.iloc[i,j]<=dataSet.iloc[i-1,j]:
                        R.append((i, j, c))
    return R

def takeFirst(elem):
    return elem[0]

def Aggregate(C, R, delta):
    R_final = {}
    for c in C:
        temp = [x for x in R if x[2].name == c.name]
        temp.sort(key = takeFirst)
        if temp!=None and len(temp)>0:
            i=0
            while i<len(temp)-1:
                start = i
                while i<len(temp)-1 and temp[i+1][0]-temp[i][0] <= delta:
                    i+=1
                if temp[i][2] in R_final.keys():
                    R_final[temp[i][2]].append(((temp[start][0],temp[i][0]),temp[i][1]))
                else:
                    R_final[temp[i][2]] = [((temp[start][0],temp[i][0]),temp[i][1])]
                i+=1
    return R_final

def RegionUpdate1(C, Validation, I, lamb, R, miu, max_T,confidence,R_final,omg):
    C_copy = copy.deepcopy(C)
    T = range(0,21)
    T_shrink = range(0,21)
    T_shrink_m = range(0,21)
    TimeInterval = [range(0,21), range(30,41), range(50,61)]
    Omg = 0.1
    for c in C_copy:
        print('Algorithm is repairing constraints: ' + c.name)
        temp_max = 0
        max_tup = None
        for cc in R.keys():
            if c.name == cc.name:
                for tup in R[cc]:
                    if tup[0][1] - tup[0][0] > temp_max:
                        max_tup = tup
                        temp_max = tup[0][1] - tup[0][0]
                if temp_max > 0:
                    T = range(max_tup[0][0], max_tup[0][1] + 1)
                break
        temp_max_shrink = 0
        max_index = 0
        max_index_m=0
        min_mean = float("inf")
        max_mean = float("-inf")
        for ccc in R.keys():
            if c.name == ccc.name:
                for i in range(len(R[ccc]) - 1):
                    temp_mean = I.iloc[R[ccc][i][0][1]+1:R[ccc][max_index + 1][0][0],list(ccc.s)[0]].mean()
                    if temp_mean < min_mean and R[ccc][i + 1][0][0] - R[ccc][i][0][1] > 10:
                        min_mean = temp_mean
                        max_index = i
                        temp_max_shrink = R[ccc][i + 1][0][0] - R[ccc][i][0][1]
                    if temp_mean > max_mean and R[ccc][i + 1][0][0] - R[ccc][i][0][1] > 5:
                        max_mean = temp_mean
                        max_index_m = i
                        temp_max_shrink_m = R[ccc][i + 1][0][0] - R[ccc][i][0][1]
                if temp_max_shrink > 0:
                    if R[ccc][max_index + 1][0][0] > max_T:
                        T_shrink = range(R[ccc][max_index][0][1]+1, R[ccc][max_index][0][1]+max_T)
                    else:
                        T_shrink = range(R[ccc][max_index][0][1] + 1, R[ccc][max_index + 1][0][0])
                T_shrink_m = range(R[ccc][max_index_m][0][1] + 1, R[ccc][max_index_m + 1][0][0])
                break
        c_shrink = ConstraintShrink(miu, c, c.feature1, c.feature2, c.s, T_shrink, lamb, I, C)
        c_shrink = ConstraintShrink(miu, c_shrink, c_shrink.feature1, c_shrink.feature2, c.s, T_shrink_m, lamb, I, C)
        c_expand = ConstraintExpand(c, c.feature1, c.feature2, c.s, T, lamb, I, C)
        if c.feature1 < c_shrink.feature1 and abs(c.feature2 - c_shrink.feature2) < 1e-2 and \
                c.feature2 < c_expand.feature2 and abs(c.feature1 - c_expand.feature1) < 1e-2:
            c_update = c_shrink
            c_update.feature2 = c_expand.feature2
        elif c.feature2 > c_shrink.feature2 and abs(c.feature1 - c_shrink.feature1) < 1e-2 and \
                c.feature1 > c_expand.feature1 and abs(c.feature2 - c_expand.feature2) < 1e-2:
            c_update = c_shrink
            c_update.feature1 = c_expand.feature1
        elif abs(c.feature1 - c_expand.feature1) < 1e-2 and abs(c.feature2 - c_expand.feature2) < 1e-2:
            c_update = c_shrink
        elif abs(c.feature1 - c_shrink.feature1) < 1e-2 and abs(c.feature2 - c_shrink.feature2) < 1e-2:
            c_update = c_expand
        else:
            if -miu*cost_2(c, c_shrink)+lamb*cost_1(I,{c_shrink})-cost_2(c, c_expand)-lamb*cost_1(I,{c_expand}) <= 0:
                c_update = c_shrink
            else:
                c_update = c_expand
        c.feature1 = c_update.feature1
        c.feature2 = c_update.feature2
    return C_copy

def RegionUpdate2(C, Validation, I, lamb, R, miu, max_T,confidence,R_final,omg):
    C_copy = copy.deepcopy(C)
    T = range(0, 21)
    T_shrink = range(0,21)
    TimeInterval = [range(0, 21), range(30, 41), range(50, 61)]
    Omg = 0.1
    for c in C_copy:
        print('Algorithm is repairing constraints: ' + c.name)
        temp_max = 0
        max_tup = None
        for cc in R.keys():
            if c.name == cc.name:
                for tup in R[cc]:
                    if tup[0][1] - tup[0][0] > temp_max:
                        max_tup = tup
                        temp_max = tup[0][1] - tup[0][0]
                if temp_max > 0:
                    T = range(max_tup[0][0], max_tup[0][1] + 1)
                break
        temp_max_shrink = 0
        max_index = 0
        for ccc in R.keys():
            if c.name == ccc.name:
                for i in range(len(R[ccc])-1):
                    if R[ccc][i+1][0][0] - R[ccc][i][0][1] > temp_max_shrink:
                        max_index = i
                        temp_max_shrink = R[ccc][i+1][0][0] - R[ccc][i][0][1]
                if temp_max_shrink > 0:
                    if R[ccc][max_index + 1][0][0] > max_T:
                        T_shrink = range(R[ccc][max_index][0][1]+1, R[ccc][max_index][0][1]+max_T)
                    else:
                        T_shrink = range(R[ccc][max_index][0][1] + 1, R[ccc][max_index + 1][0][0])
                break
        c_shrink = ConstraintShrinkStar(miu, c, c.feature1, c.feature2, c.s, T_shrink, lamb, I, C_copy)
        c_expand = ConstraintExpandStar(c, c.feature1, c.feature2, c.s, T, lamb, I, C_copy)

        if c.feature1<c_shrink.feature1 and abs(c.feature2-c_shrink.feature2)<1e-2 and \
                c.feature2<c_expand.feature2 and abs(c.feature1-c_expand.feature1) < 1e-2:
            c_update = c_shrink
            c_update.feature2 = c_expand.feature2
        elif c.feature2>c_shrink.feature2 and abs(c.feature1-c_shrink.feature1)<1e-2 and \
                c.feature1 > c_expand.feature1 and abs(c.feature2-c_expand.feature2)<1e-2:
            c_update = c_shrink
            c_update.feature1 = c_expand.feature1
        elif abs(c.feature1-c_expand.feature1)<1e-2 and abs(c.feature2-c_expand.feature2)<1e-2:
            c_update = c_shrink
        elif abs(c.feature1-c_shrink.feature1)<1e-2 and abs(c.feature2-c_shrink.feature2)<1e-2:
            c_update = c_expand
        else:
            if -miu*cost_2(c, c_shrink)+lamb*cost_1(I,{c_shrink})-cost_2(c, c_expand)-lamb*cost_1(I,{c_expand}) <= 0:
                c_update = c_shrink
            else:
                c_update = c_expand
        c.feature1 = c_update.feature1
        c.feature2 = c_update.feature2
        ff = 0
        while len(Detect({c}, Validation)) != 0:
            c_temp = ConstraintExpandS(c, c.feature1, c.feature2, c.s, TimeInterval, I)
            if abs(c_temp.feature1-c.feature1)>10 or abs(c_temp.feature2-c.feature2)>10:
                break
            if abs(c_temp.feature1-c.feature1)<1e-5 and abs(c_temp.feature2-c.feature2)<1e-5:
                ff += 1
                if ff > 10:
                    break
            c.feature1 = c_temp.feature1
            c.feature2 = c_temp.feature2
    return C_copy

def ConstraintRepair(I, C, lamb, delta, alpha, Validation, miu, max_T,confidence,omg):
    T = range(0,21)
    T_shrink = range(0,21)
    TimeInterval = [range(0, 21), range(30, 41), range(50, 61)]
    R = Detect(C, I)
    R = Aggregate(C, R, delta)
    con_dic = {}
    for c in C:
        for s in c.s:
            if s in con_dic.keys():
                con_dic[s].add(c)
            else:
                con_dic[s] = {c}
    C_independent = set()
    for key,value in con_dic.items():
        if len(value) == 1:
            for item in value:
                C_independent.add(item)
    if cost_1(I, C) > alpha:
        if len(C_independent & C) == len(C):
            C = RegionUpdate1(C, Validation, I, lamb, R, miu, max_T,confidence,R,omg)
        else:
            C_rel_new = {}
            C_ind_new = RegionUpdate1(C_independent, Validation, I, lamb, R, miu, max_T,confidence,R,omg)
            for s in con_dic.keys():
                if(len(con_dic[s])>1):
                    print('Repairing ' + str(s) + ' Sequence')
                    C_rel_new[s] = RegionUpdate2(con_dic[s], Validation, I, lamb, R, miu, max_T, confidence,R,omg)


            for c in C:
                if len(c.s) > 1:
                    d_left_max = float('-inf')
                    d_left_min = float('inf')
                    d_right_min = float('inf')
                    d_right_max = float('-inf')
                    flag = 0
                    for c_new in C_ind_new:
                        if c_new.name == c.name:
                            flag = 1
                            if d_left_min > c_new.feature1:
                                d_left_min = c_new.feature1
                            if d_left_max < c_new.feature1:
                                d_left_max = c_new.feature1
                            if d_right_min > c_new.feature2:
                                d_right_min = c_new.feature2
                            if d_right_max < c_new.feature2:
                                d_right_max = c_new.feature2
                            c.feature1 = c_new.feature1
                            c.feature2 = c_new.feature2
                            break
                    for s in c.s:
                        if s in C_rel_new.keys():
                            for c_rel in C_rel_new[s]:
                                if c_rel.name == c.name:
                                    if d_left_min > c_rel.feature1:
                                        d_left_min = c_rel.feature1
                                    if d_left_max < c_rel.feature1:
                                        d_left_max = c_rel.feature1
                                    if d_right_min > c_rel.feature2:
                                        d_right_min = c_rel.feature2
                                    if d_right_max < c_rel.feature2:
                                        d_right_max = c_rel.feature2
                                    if flag == 0:
                                        c.feature1 = c_rel.feature1
                                        c.feature2 = c_rel.feature2
                                        flag = 1
                                    elif flag != 0:
                                        c.feature1 = c.feature1 + c_rel.feature1
                                        c.feature2 = c.feature2 + c_rel.feature2
                                        flag += 1
                                break
                    temp_max = 0
                    max_tup = None
                    if c in R.keys():
                        for tup in R[c]:
                            if tup[0][1] - tup[0][0] > temp_max:
                                max_tup = tup
                                temp_max = tup[0][1] - tup[0][0]
                        if temp_max > 0:
                            T = range(max_tup[0][0], max_tup[0][1] + 1)

                    temp_max_shrink = 0
                    max_index = 0
                    if c in R.keys():
                        for i in range(len(R[c]) - 1):
                            if R[c][i + 1][0][0] - R[c][i][0][1] > temp_max_shrink:
                                max_index = i
                                temp_max_shrink = R[c][i + 1][0][0] - R[c][i][0][1]
                        if temp_max_shrink > 0:
                            if R[c][max_index + 1][0][0] > max_T:
                                T_shrink = range(R[c][max_index][0][1] + 1, R[c][max_index][0][1] + max_T)
                            else:
                                T_shrink = range(R[c][max_index][0][1] + 1, R[c][max_index + 1][0][0])

                    if flag != 0:
                        c.feature1 /= flag
                        c.feature2 /= flag
                    min_cost = float('inf')
                    while c.feature1 >= d_left_min and c.feature1 <= d_left_max and \
                        c.feature2 >= d_right_min and c.feature2 <= d_right_min >= d_right_max:
                        c_shrink = ConstraintShrink(miu, c, c.feature1, c.feature2, c.s, T_shrink, lamb, I, C)
                        c_expand = ConstraintExpand(c, c.feature1, c.feature2, c.s, T, lamb, I, C)
                        if -miu*cost_2(c,c_shrink) + lamb * cost_1(I, {c_shrink}) - cost_2(c, c_expand)-lamb*cost_1(I, {c_expand}) <= 0:
                            c_update = ConstraintShrinkS_Star(c, c.feature1, c.feature2, c.s, TimeInterval, I, d_left_min, d_left_max, d_right_min, d_right_max)
                        else:
                            c_update = ConstraintExpandS_Star(c, c.feature1, c.feature2, c.s, TimeInterval, I, d_left_min, d_left_max, d_right_min, d_right_max)
                        if c_update.feature1 == c.feature1 and c_update.feature2 == c.feature2:
                            break
                        if cost_2(c, c_update) + lamb * cost_1(I, {c_update}) < min_cost:
                            c.feature1 = c_update.feature1
                            c.feature2 = c_update.feature2
                            min_cost = cost_2(c, c_update) + lamb * cost_1(I, {c_update})
                else:
                    for c_in in C_ind_new:
                        if c.name == c_in.name:
                            c.feature1 = c_in.feature1
                            c.feature2 = c_in.feature2
                            break
                    for ss in C_rel_new.keys():
                        for c_re in C_rel_new[ss]:
                            if c.name == c_re.name:
                                c.feature1 = c_re.feature1
                                c.feature2 = c_re.feature2
                                break
    return C