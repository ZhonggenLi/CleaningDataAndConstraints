import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

#days = 1460

def random_walk(df, days, rate, divide, threshold=0.67):
    # 第一列数据
    start_value1 = 12
    min_value1 = 10
    max_value1 = 15
    step_size1 = 1.0
    previous_value = start_value1
    for index, row in df.iterrows():
        if previous_value < min_value1:
            previous_value = min_value1
        if previous_value > max_value1:
            previous_value = max_value1
        probability = random.random()
        weight = random.random()
        if probability >= threshold:
            if previous_value + step_size1 * weight <= max_value1:
                df.loc[index, 'value1'] = previous_value + step_size1 * weight
            else:
                df.loc[index, 'value1'] = previous_value
        elif probability < 0.33:
            if previous_value - step_size1 * weight >= min_value1:
                df.loc[index, 'value1'] = previous_value - step_size1 * weight
            else:
                df.loc[index, 'value1'] = previous_value
        else:
            df.loc[index, 'value1'] = previous_value
        previous_value = df.loc[index, 'value1']
    # for i in range(int(divide)):
    #     bios = int(days * random.random())
    #     #print((bios-pd.to_datetime('2017-01-01')).days+2, end=', ')
    #     if random.random() < 0.5:
    #         for j in range(int(rate / divide)):
    #             df.loc[(bios+j)%len(df), 'value1'] = max_value1 + max_value1 * (0.1+random.random())
    #     else:
    #         for j in range(int(rate / divide)):
    #             df.loc[(bios+j)%len(df), 'value1'] = min_value1 - min_value1 * (0.1+random.random())

    #第二列数据
    start_value2 = 51
    min_value2 = 50
    max_value2 = 55
    step_size2 = 1.0
    previous_value = start_value2
    for index, row in df.iterrows():
        if previous_value < min_value2:
            previous_value = min_value2
        if previous_value > max_value2:
            previous_value = max_value2
        probability = random.random()
        weight = random.random()
        if probability >= threshold:
            if previous_value + step_size2 * weight <= max_value2:
                df.loc[index, 'value2'] = previous_value + step_size2 * weight
            else:
                df.loc[index, 'value2'] = previous_value
        elif probability < 0.33:
            if previous_value - step_size2 * weight >= min_value2:
                df.loc[index, 'value2'] = previous_value - step_size2 * weight
            else:
                df.loc[index, 'value2'] = previous_value
        else:
            df.loc[index, 'value2'] = previous_value
        previous_value = df.loc[index, 'value2']
    # for i in range(int(divide)):
    #     bios = int(days * random.random())
    #     #print((bios - pd.to_datetime('2017-01-01')).days + 2, end=', ')
    #     if random.random() < 0.5:
    #         for j in range(int(rate / divide)):
    #             df.loc[(bios+j)%len(df), 'value2'] = max_value2 + max_value2 * (0.1 + random.random())
    #     else:
    #         for j in range(int(rate / divide)):
    #             df.loc[(bios+j)%len(df), 'value2'] = min_value2 - min_value2 * (0.1 + random.random())

    # 第三列数据
    C = 2
    err = 18
    for index, row in df.iterrows():
        df.loc[index, 'value3'] = df.loc[index, 'value2'] / C
    # for i in range(4):
    #     bios = int(days * random.random())
    #     #print((bios - pd.to_datetime('2017-01-01')).days + 2, end=', ')
    #     if random.random() < 0.5:
    #         for j in range(int(err / 4)):
    #             df.loc[(bios+j)%len(df), 'value3'] = df.loc[(bios+j)%len(df), 'value3'] + df.loc[(bios+j)%len(df), 'value3'] * (0.15 + random.random())
    #     else:
    #         for j in range(int(err / 4)):
    #             df.loc[(bios+j)%len(df), 'value3'] = df.loc[(bios+j)%len(df), 'value3'] - df.loc[(bios+j)%len(df), 'value3'] * (0.15 + random.random())

    #第四列约束
    start_value4 = 21
    min_value4 = 20
    max_value4 = 22
    step_size4 = 0.5
    previous_value = start_value4
    for index, row in df.iterrows():
        if previous_value < min_value4:
            previous_value = min_value4
        if previous_value > max_value4:
            previous_value = max_value4
        probability = random.random()
        weight = random.random()
        if probability >= threshold:
            if previous_value + step_size4 * weight <= max_value4:
                df.loc[index, 'value4'] = previous_value + step_size4 * weight
            else:
                df.loc[index, 'value4'] = previous_value
        elif probability < 0.33:
            if previous_value - step_size4 * weight >= min_value4:
                df.loc[index, 'value4'] = previous_value - step_size4 * weight
            else:
                df.loc[index, 'value4'] = previous_value
        else:
            df.loc[index, 'value4'] = previous_value
        previous_value = df.loc[index, 'value4']

    #第五列约束
    C2 = 2
    err = 18
    for index, row in df.iterrows():
        df.loc[index, 'value5'] = (df.loc[index, 'value1'] + df.loc[index, 'value4']) * C2
    # for i in range(4):
    #     bios = int(days * random.random())
    #     #print((bios - pd.to_datetime('2017-01-01')).days + 2, end=', ')
    #     if random.random() < 0.5:
    #         for j in range(int(err / 4)):
    #             df.loc[(bios+j)%len(df), 'value5'] = df.loc[(bios+j)%len(df), 'value5'] + df.loc[(bios+j)%len(df), 'value5'] * (0.15 + random.random())
    #     else:
    #         for j in range(int(err / 4)):
    #             df.loc[(bios+j)%len(df), 'value5'] = df.loc[(bios+j)%len(df), 'value5'] - df.loc[(bios+j)%len(df), 'value5'] * (0.15 + random.random())

    return df

if __name__ == '__main__':
    data_num = 25000
    rate = 0 * data_num
    divide = 25
    #rate = 0
    dates = [i for i in range(data_num)]
    print()
    df = pd.DataFrame({
        'date':dates,
        'value1': np.random.normal(0, 1, len(dates)),
        'value2': np.random.normal(0, 1, len(dates)),
        'value3': np.random.normal(0, 1, len(dates)),
        'value4': np.random.normal(0, 1, len(dates)),
        'value5': np.random.normal(0, 1, len(dates)),
    })
    df.set_index('date', inplace=True)
    df = random_walk(df, days=data_num, rate=rate, divide=divide)
    df.to_csv("正常数据25000.csv")