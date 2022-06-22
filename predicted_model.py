import pandas as pd
import math

# определеяем расстояние евклида
def euclid_destination(data_list, example_list):
    return 1 / (1 + math.sqrt(sum([(item[0] - item[1]) ** 2 for item in zip(data_list, example_list)])))

# основная функци расчета
def find_rates(date, array_from_db):
    list_destination = []
    tests = {}
    df = pd.read_excel("test_data_2.xlsx")
    to_pred = array_from_db
    #to_pred = [0,0,0,0,56,0,0,0,0,11,90]

    for index, row in df.iterrows():
        list_destination.append(euclid_destination([row[item] for item in df if item not in ['test_number', 'result']], to_pred))

    df['destination'] = list_destination
    df1=df.sort_values(by=['destination'], ascending=False).head(3)
    R = round(df1['result'].mean(),2)
    if R >= 0.85:
        tests[str(date)] = str(
            R) + " - защита информации при переводах денежных средств обеспечена на <b>хорошем<b> уровне."
    if R < 0.85 and R >= 0.7:
        tests[str(date)] = str(
            R) + " - защита информации при переводах денежных средств обеспечена на <b>удовлетворительном<b> уровне."
    if R < 0.7 and R >= 0.5:
        tests[str(date)] = str(
            R) + " - защита информации при переводах денежных средств обеспечена на <b>сомнительном<b> уровне."
    if R < 0.5:
        tests[str(date)] = str(
            R) + " - защита информации при переводах денежных средств обеспечена на <b>неудовлетворительном<b> уровне."
    return tests
