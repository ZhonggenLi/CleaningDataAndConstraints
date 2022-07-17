import pandas as pd
from bNDCRepair import Constraint, ConstraintRepair, Detect

ValidSet = pd.read_csv("../DataSample/IDF-ValidSet.csv", header=None)

dataSet = pd.read_csv("../DataSample/IDF-1w-5%.csv", header=None)

# Constraints to be repaired
c1b = Constraint('a', 0, 4000, {0}, 1)
c2b = Constraint('b', -6, -1, {1}, 1)

C = {c1b,c2b}

# Ground Truth Constraints
c1 = Constraint('a', 0, 6475.96387, {0}, 1)
c2 = Constraint('b', -4.92642, -1.79391, {1}, 1)

C_truth = {c1,c2}

# Call the algorithm
C_new = ConstraintRepair(dataSet, C, lamb=0.0000004, delta=1, alpha=0, Validation=ValidSet, miu=3, max_T=50,
                         confidence=0.8, omg=0.001)

# Print results
for c in C_new:
    print(c.name, end='')
    print("[", end='')
    print(c.feature1, c.feature2, end='')
    print("]")

# Calculate Precision and Recall

R_our = Detect(C_new, dataSet)

R_truth = Detect(C_truth, dataSet)


Point_our=set()
Point_truth = set()
Point_all = set()

for point in R_our:
    Point_our.add((point[0],point[1]))

for pp in R_truth:
    Point_truth.add((pp[0],pp[1]))

for i in range(len(dataSet)):
    for j in range(len(dataSet.columns)):
        Point_all.add((i,j))

TP = len(Point_all - (Point_our | Point_truth))
TN = len(Point_our & Point_truth)
FP = len((Point_all-Point_our)&Point_truth)
FN = len(Point_our & (Point_all-Point_truth))
print(TP,TN,FP,FN)

P = TP/(TP+FP)
R = TP/(FN+TP)
print('Precision: '+str(TP/(TP+FP)), 'Recall: '+str(TP/(FN+TP)))
