# COMS E6111-Advanced Database Systems Project 3

1. Name and UNI: Eric Feng, ef2648
2. Files submitted: association.py, 2018_Central_Park_Squirrel_Census_-_Squirrel_Data.csv, example-run.txt, README.md

# Description of how to run program
1. Usage: `./association.py` `INTEGRATED-DATASET.csv` `<min_sup>` `<min_conf>`

Please have INTEGRATED-DATASET.csv in the same directory as association.py

# Description of NYC Open Data data set and motives:
The INTEGRATED-DATASET is the raw data from the `2018 Central Park Squirrel Census - Squirrel Data` dataset on NYC OpenData. Each row describes a squirrel sighting and the properties and behaviors of the squirrel at the time of the sighting. Below is a description provided by the data.

`The Squirrel Census (https://www.thesquirrelcensus.com/) is a multimedia science, design, and storytelling project focusing on the Eastern gray (Sciurus carolinensis). They count squirrels and present their findings to the public. This table contains squirrel data for each of the 3,023 sightings, including location coordinates, age, primary and secondary fur color, elevation, activities, communications, and interactions between squirrels and with humans.`

Please find the dataset here: `https://data.cityofnewyork.us/Environment/2018-Central-Park-Squirrel-Census-Squirrel-Data/vfnx-vebw`

I chose to investigate this data set because I thought it would be really interesting to relate the ideas of association rules to learn about the behavior of squirrels in New York. For example, do they tend to forage in the PM or AM? Is there a difference in behavior between the different colors of the squirrels? What time are they most friendly to humans? These are just some of the observations we may make by analyzing the behaviors through the lens of association rules.

# Description of internal design

The entry point of the program is in the main() function. We call parse_data() immediately to parse the CLI arguments. Please not we do not protect against improper arguments. In other words, it is advised to run the program as specified in the description of how to run the program, as improper arguments will cause the program to function unexpectedly. 

We then call get_initial_items, which reads the dataset and parses the CSV file into a dictionary with key item and value frequency. We will then filter this dictionary to only contain the items which pass the minimum support. As mentioned in section 2.1 of the `Fast Algorithms for Mining Association` paper, this first pass simply counts item occurences to determine the large 1-itemsets.

After we get our collection of large 1-itemsets, we call extract_large_itemsets. This function reflects the Algorithm Apriori demonstrated in the paper. We enter a while loop which calls apriori-gen to find new candidates then for each candidate scan the transactions in the dictionary we built in get_initial_items (to avoid having to repeatedly read the file since our dataset is small enough to keep completely in memory). We count the frequency for each candidate during the scan, and the ones that meet the minimum support are added to L_next, which is fed to the next iteration of the loop. The loop breaks when L_next is empty.

We use the implementation described in 2.1.1 for apriori-gen. To mimic the behavior of the join step, we run the candidate itemset in a double for loop and keep the candidates with the same elements for i = 1 to k - 1 (non-inclusive at k - 1) and with p.item_k - 1 < q.item_k - 1. Then, we prune the candidates by generating all combinations of a itemset, and removing all those sublists which are not in L from C_k. To support comparing behaviors by index k, dictionaries of key: item, value: k and vice versa are built in the extract_large_itemsets step.

We return from extract_large_itemsets when L_next is empty. We then call extract_association_rules. We pass in a dictionary with key: candidate, value: support, and the min_conf. Next, for each candidate with more than one item (ignoring trivial rules), we find all permutations of that candidate. The first n - 1 elements of the candidate is taken as the LHS and the nth element is taken as the RHS. We then find the support for the LHS and RHS by using the confidence(LHS -> RHS) = support (LHS U RHS) / support(LHS) formula. To get the support of any particular side, we simply find the corresponding value of the candidate:support dictionary we passed in at the start of the function. To avoid repeats, we sort the candidate tuples before looking them up in the dictionary. Those candidates with confidence above min_conf are appended to association_rules list. At the end of the function, this list is returned.

Finally, we iterate through the candidate:support dictionary and association_rules list to output to file "output.txt" as specified.

# Recommended CLI specification 
`./association.py 2018_Central_Park_Squirrel_Census_-_Squirrel_Data.csv 0.01 0.7` are the arguments provided for example-run.txt, and provides some interesting results. For example, observe the following association rule: [AM, Adult, Approaches, Gray] => [Foraging] (Conf: 72.91666666666667%, Supp: 1.1577902745616937%). This rule shows that we have relatively high confidence (though support is rather low) that adult gray squirrels which approach humans in the morning and tend to be foraging for food. Next, [Adult, Foraging, Gray, Tail flags] => [Indifferent] (Conf: 71.11111111111111%, Supp: 1.0585511081706915%) shows that adult gray squirrels which are flagging to tailstend to be somewhat indifferent to humans. [Climbing, PM, Tail twitches] => [Adult] (Conf: 78.04878048780488%, Supp: 1.0585511081706915%) shows that squirrels that are climbing and twitching their tails in the afternoon tend to be adults. These results are compelling because we can learn about the behaviors of squirrels and relate them to factors such as age, time of day, color and other behaviors.

# Dependencies
No external dependeicies; all within standard library
