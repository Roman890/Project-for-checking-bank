# -*- coding: utf-8 -*-
from main import Banks, Tests, db
from sqlalchemy import desc, asc
from sqlalchemy import func, or_
import predicted_model

def find_test_from_banks():
    """Достать банки и тесты в каждом"""
    data = {}
    tests = {}
    answers = {}
    banks = Banks.query.order_by(asc(Banks.id)).all()
    for bank in banks:
        tests_from_bots = db.session.query(Tests.bank_id, func.count(Tests.answer), Tests.created_date).group_by(Tests.created_date, Tests.bank_id).having(Tests.bank_id == bank.id)
        for index_date in tests_from_bots:
            answers_from_tests = db.session.query(Tests.bank_id, Tests.answer, func.count(Tests.answer), Tests.created_date).group_by(Tests.created_date, Tests.bank_id, Tests.answer).having(Tests.bank_id == bank.id).having(Tests.created_date == index_date[2]).order_by(Tests.answer)
            for element in answers_from_tests:
                answers[element[1]] = element[2]
            tests[str(index_date[2])] = answers
            answers = {}
        data[bank] = tests
        tests = {}
    return data




def find_rates():
    """Оценка по 382-п"""
    data = {}
    tests = {}
    k1 = 0
    k2 = 0
    banks = Banks.query.order_by(asc(Banks.id)).all()
    for bank in banks:
        tests_from_bots = db.session.query(Tests.bank_id, func.count(Tests.answer), Tests.created_date).group_by(Tests.created_date, Tests.bank_id).having(Tests.bank_id == bank.id)
        for index_date in tests_from_bots:
            count_n_o = db.session.query(func.count(Tests.id)).filter(Tests.created_date == index_date[2], Tests.bank_id == bank.id, Tests.answer == -1).scalar()
            if count_n_o == 1:
                EV1_1 = db.session.query(Tests.answer, func.count(Tests.answer)).filter(Tests.created_date == index_date[2],
                                                                      Tests.bank_id == bank.id,
                                                                      Tests.answer != -1).filter(
                    or_(Tests.question_id <= 104, Tests.question_id >= 155)).group_by(Tests.answer).order_by(Tests.answer)
                EV2_1 = db.session.query(Tests.answer, func.count(Tests.answer)).filter(Tests.created_date == index_date[2],
                                                                      Tests.bank_id == bank.id,
                                                                      Tests.answer != -1).filter(
                    Tests.question_id >= 105, Tests.question_id <= 154).group_by(Tests.answer).order_by(Tests.answer)
                EV1_result_dict = {0 : 0, 0.25: 0, 0.5: 0, 0.75: 0, 1: 0}
                EV2_result_dict = {0: 0, 0.25: 0, 0.5: 0, 0.75: 0, 1: 0}
                for i, j in EV1_result_dict.items():
                    for k in EV1_1:
                        if i == k[0]:
                            EV1_result_dict[i] = k[1]
                print(EV1_result_dict)
                EV1_result = list(EV1_result_dict.values())

                for i, j in EV2_result_dict.items():
                    for k in EV2_1:
                        if i == k[0]:
                            EV2_result_dict[i] = k[1]
                print(EV2_result_dict)
                EV2_result = list(EV2_result_dict.values())

                array_from_db = EV1_result + EV2_result + [count_n_o]
                data[bank] = predicted_model.find_rates(index_date[2], array_from_db)
                continue

            EV1 = db.session.query(func.avg(Tests.answer)).filter(Tests.created_date == index_date[2], Tests.bank_id == bank.id, Tests.answer != -1).filter(or_(Tests.question_id <= 104, Tests.question_id >= 155)).scalar()
            EV2 = db.session.query(func.avg(Tests.answer)).filter(Tests.created_date == index_date[2], Tests.bank_id == bank.id, Tests.answer != -1).filter(Tests.question_id >= 105, Tests.question_id <= 154).scalar()
            count_for_k1 = db.session.query(func.count(Tests.id)).filter(Tests.created_date == index_date[2], Tests.bank_id == bank.id, Tests.answer == 0).filter(or_(Tests.question_id <= 104, Tests.question_id >= 155)).scalar()
            count_for_k2 = db.session.query(func.count(Tests.id)).filter(Tests.created_date == index_date[2], Tests.bank_id == bank.id, Tests.answer == 0).filter(Tests.question_id >= 105, Tests.question_id <= 154).scalar()
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
            if EV2 != None and EV1 != None :
                buf1 = EV1*k1
                buf2 = EV2*k2
                R = min(buf1, buf2)
            else:
                R = 0
            if R >= 0.85:
                tests[str(index_date[2])] = str(R) + " - защита информации при переводах денежных средств обеспечена на <b>хорошем<b> уровне."
            if R < 0.85 and R >= 0.7:
                tests[str(index_date[2])] = str(R) + " - защита информации при переводах денежных средств обеспечена на <b>удовлетворительном<b> уровне."
            if R < 0.7 and R >= 0.5:
                tests[str(index_date[2])] = str(R) + " - защита информации при переводах денежных средств обеспечена на <b>сомнительном<b> уровне."
            if R < 0.5:
                tests[str(index_date[2])] = str(R) + " - защита информации при переводах денежных средств обеспечена на <b>неудовлетворительном<b> уровне."
        data[bank] = tests
        tests = {}
    return data
