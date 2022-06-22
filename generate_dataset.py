import pandas as pd
import random
import statistics

# выбор вариантов для ответов
def find_answers(type_of_answer):
    if type_of_answer == 1:
        return [10, 0, 0.25, 0.5, 0.75, 1], [10, 0, 1], [10, 0, 0.5, 1]
    if type_of_answer == 2:
        return [10, 0.25, 0.5, 0.75, 1], [10, 0, 1], [10, 0.5, 1]
    if type_of_answer == 3:
        return [10, 0.25, 0.5, 0.75, 1], [10, 1], [10, 0.5, 1]
    if type_of_answer == 4:
        return [10, 1], [10, 1], [10, 0.5, 1]
    if type_of_answer == 5:
        return [10, 0.5, 0.75, 1], [10, 1],[10, 0.5, 1]
    if type_of_answer == 6:
        return [0, 0.25, 0.5, 0.75, 1], [0, 1], [0, 0.5, 1]
    if type_of_answer == 7:
        return [0.25, 0.5, 0.75, 1], [1],[0.5, 1]
    if type_of_answer == 8:
        return [0.75, 1],[1],[0.5, 1]

#создание набора данных
def create_dataframe():
    questions_category_3 = [8,9,15,16,28,39,45,46,47,52,53,55,56,57,61,62,69,70,73,77,78,79,80,81,82,83,94,95,
                            105,106,107,108,109,111,112,113,114,115,119,121,123,125,127,128,129,130,132,133,134,
                            135,138,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,160,164,167]
    questions_category_2 = [11,31,40,41,54,71,90,91,120,122,131,139,158,166]
    test_list = []

    for i in range(0,10000):
        test = []
        items_EV1 = []
        items_EV2 = []
        k1,k2,EV1,EV2 = 0,0,0,0
        answer_category_1, answer_category_2, answer_category_3 = find_answers(random.choice([1,2,3,4,5,6,7,8]))

        # формируем лист с ответами
        for item in range(0, 167):
            if item in questions_category_2:
                test.append(random.choice(answer_category_2))
            elif item in questions_category_3:
                test.append(random.choice(answer_category_3))
            else:
                test.append(random.choice(answer_category_1))

        #проводим оценку
        for item in range(0,len(test)):
            if (item <= 103 or item >= 154) and test[item] != 10:
                items_EV1.append(test[item])
            if item >= 104 and item <= 153 and test[item] != 10:
                items_EV2.append(test[item])

        EV1 = statistics.mean(items_EV1)
        EV2 = statistics.mean(items_EV2)
        count_for_k1 = items_EV1.count(0)
        count_for_k2 = items_EV1.count(0)
        if count_for_k1 == 0:
            k1 = 1
        if count_for_k1 < 11 and count_for_k1 != 0:
            k1 = 0.85
        if count_for_k1 >= 11:
            k1 = 0.7
        if count_for_k2 == 0:
            k2 = 1
        if count_for_k2 < 6 and count_for_k2 != 0:
            k2 = 0.85
        if count_for_k2 >= 6:
            k2 = 0.7
        if EV2 != None and EV1 != None:
            buf1 = EV1 * k1
            buf2 = EV2 * k2
            R = min(buf1, buf2)
        else:
            R = 0
        test.append(round(R, 3))
        test_list.append(test)

    return test_list


res = create_dataframe()
test_columns = ["requirement_"+ str(item) for item in range(1,168)]
test_columns.append("result")
df = pd.DataFrame(res, columns=test_columns)
df.to_excel("test_data.xlsx", index=False)
