#!/usr/bin/env python3
# Author: Eric Feng, ef2648

import sys
import csv
import itertools
from collections import defaultdict


# items2keys = {
#    'PM': 'Shift',
#    'AM': 'Shift',
#    'Gray': 'Primary Fur Color',
#    'Black': 'Primary Fur Color',
#    'Cinnamon': 'Primary Fur Color',
#    'Adult': 'Age',
#    'Juvenile': 'Age',
# }


def parse_data():
    args = sys.argv
    if len(args) != 4:
        sys.exit("Usage: ./association.py INTEGRATED-DATASET.csv 0.01 0.5")

    filename = args[1]
    min_sup = float(args[2])
    min_conf = float(args[3])
    return filename, min_sup, min_conf


def get_initial_items(filename, min_sup):
    file = list(csv.DictReader(open(filename, encoding="utf-8")))
    L_1 = defaultdict(int)

    for row in file:
        if row['Primary Fur Color'].isalpha():
            L_1[row['Primary Fur Color']] += 1
        if row['Age'].isalpha():
            L_1[row['Age']] += 1
        L_1[row['Shift']] += 1
        L_1['Running'] += row['Running'] == 'true'
        L_1['Chasing'] += row['Chasing'] == 'true'
        L_1['Climbing'] += row['Climbing'] == 'true'
        L_1['Eating'] += row['Eating'] == 'true'
        L_1['Foraging'] += row['Foraging'] == 'true'
        L_1['Kuks'] += row['Kuks'] == 'true'
        L_1['Quaas'] += row['Quaas'] == 'true'
        L_1['Moans'] += row['Moans'] == 'true'
        L_1['Tail flags'] += row['Tail flags'] == 'true'
        L_1['Tail twitches'] += row['Tail twitches'] == 'true'
        L_1['Approaches'] += row['Approaches'] == 'true'
        L_1['Indifferent'] += row['Indifferent'] == 'true'
        L_1['Runs from'] += row['Runs from'] == 'true'

    items = [([k], v / len(file)) for (k, v) in L_1.items() if v / len(file) >= min_sup]
    n2items = {n: item[0][0] for n, item in enumerate(items)}
    items2n = {item[0][0]: n for n, item in enumerate(items)}

    return n2items, items2n, file, [items]


def apriori_gen(L, k):
    C_k = []

    for p, ptem in enumerate(L):
        for q, qtem in enumerate(L):
            if ptem[:k - 1] == qtem[:k - 1] and ptem[k - 1] < qtem[k - 1]:
                C_k.append(ptem + [qtem[k - 1]])

    for itemset in C_k[:]:
        sublists = [list(item) for item in list(itertools.combinations(itemset, k))]
        for sub in sublists:
            if sub not in L and itemset in C_k:
                C_k.remove(itemset)
    return C_k


# need to turn these into tuples
def extract_large_itemsets(min_sup, n2items, items2n, file_dict, L):
    k = 1
    L_next = [[key] for key in n2items.keys()]

    while True:
        C_k = [list(map(lambda key: n2items[key], candidate)) for candidate in apriori_gen(L_next, k)]
        L_add = []
        L_next = []

        for candidate in C_k:
            L_temp = 0

            for transaction in file_dict:
                transaction.pop('Highlight Fur Color', None)
                curr = sum(
                    [1 if c in transaction.values() or (c in transaction and transaction[c] == 'true') else 0 for c in
                     candidate])
                if curr == len(candidate):
                    L_temp += 1

            # print(candidate, L_temp)
            candidate_support = L_temp / len(file_dict)
            if candidate_support >= min_sup:
                # need to turn keys, which are item names right now, to their numbers
                L_next.append([items2n[item] for item in candidate])
                L_add.append(([item for item in candidate], candidate_support))

        if not L_next:
            break
        L.append(L_add)
        k += 1

    return L


def extract_association_rules(candidate2support, min_conf):
    association_rules = []
    seen = set()

    for k, v in candidate2support.items():
        if len(k) < 2:
            continue

        permutations = list(itertools.permutations(k))
        for permutation in permutations:
            LHS = permutation[:-1]
            RHS = (permutation[-1],)

            sorted_LHS = tuple(sorted(LHS))
            LHSuRHS_support = candidate2support[tuple(sorted(permutation))]
            LHS_support = candidate2support[sorted_LHS]
            conf = LHSuRHS_support / LHS_support
            if conf >= min_conf and sorted_LHS not in seen:
                seen.add(sorted_LHS)
                association_rules.append((sorted_LHS, RHS, conf, candidate2support[tuple(sorted(permutation))]))

    return association_rules


def output_file(candidate2support, association_rules, min_sup, min_conf):
    f = open('output.txt', 'w')
    f.write("==Frequent itemsets (min_sup=" + str(min_sup * 100) + "%)\n")
    for k, v in sorted(candidate2support.items(), key=lambda i: i[1], reverse=True):
        f.write("[" + ", ".join(k) + "]" + ", " + str(v * 100) + "\n")
    f.write("==High-confidence association rules (min_conf=" + str(min_conf * 100) + "%)\n")
    for item in sorted(association_rules, key=lambda i: i[2], reverse=True):
        LHS = item[0]
        RHS = item[1]
        conf = item[2]
        sup = item[3]
        f.write("[" + ", ".join(LHS) + "] => [" + ", ".join(RHS) + "] (Conf: " + str(conf * 100) + "%, Supp: " + str(
            sup * 100) + "%)\n")


def main():
    filename, min_sup, min_conf = parse_data()
    n2items, items2n, file_dict, L = get_initial_items(filename, min_sup)

    frequent_itemsets = extract_large_itemsets(min_sup, n2items, items2n, file_dict, L)
    candidate2support = {tuple(sorted(item[0])): item[1] for item_set in frequent_itemsets for item in item_set}
    association_rules = extract_association_rules(candidate2support, min_conf)

    output_file(candidate2support, association_rules, min_sup, min_conf)


if __name__ == '__main__':
    main()
