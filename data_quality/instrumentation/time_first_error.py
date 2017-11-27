import time
import matplotlib.pyplot as plt
import numpy as np
import sys
from data_quality.examples.tutorials.jadianes import kddcup99spark as kddcup99spark
from data_quality.examples.github.erfannoury.TextClassification import naive_bayes as naivebayesclass
from data_quality.examples.homeworks.mcb112 import sandmice_Nathan as nathan, sandmice_Harleen as harleen
from data_quality.examples.github.RuiqingQiu import oja as ruiqingqiuoja
from data_quality.examples.homeworks.dat8 import homework3_chipotle as runchipotle


def kddcup99spark(filename):
    kddcup99spark.main(filename)


def naivebayes():
    naivebayesclass.main()


def mcb112sandmiceNathan(filename):
    nathan.main(filename)


def mcb112sandmiceHarleen(filename):
    harleen.main(filename)


def oja(filename):
    ruiqingqiuoja.main(filename)


def chipotle(filename):
    runchipotle.main(filename)


def run(script_to_run, filename):
    start = time.time()
    try:
        if script_to_run == 'kddcup99spark':
            kddcup99spark(filename)
        if script_to_run == 'NaiveBayes':
            naivebayes()
        if script_to_run == 'sandmice_Nathan':
            mcb112sandmiceNathan(filename)
        if script_to_run == 'sandmice_Harleen':
            mcb112sandmiceHarleen(filename)
        if script_to_run == 'oja':
            oja(filename)
        if script_to_run == 'homework3_chipotle':
            chipotle(filename)
    except:
        print(sys.exc_info()[0], sys.exc_info()[1])
        return time.time() - start
    raise AssertionError('No error was raised.')

fig, axs = plt.subplots()
root = '/home/madi/Documents/ETH/master/masterthesis/lyrarep/Lyra/data_quality/examples/'
programs = {'homework3_chipotle': 'homeworks/dat8/', 'oja': 'github/RuiqingQiu/', 'sandmice_Harleen': 'homeworks/mcb112/data/', 'sandmice_Nathan': 'homeworks/mcb112/data/'}
files = {'homework3_chipotle': 'chipotle_few_elems.tsv', 'oja': 'new_data_1_error_end','sandmice_Harleen': 'sandmouse.fa_error_end.txt', 'sandmice_Nathan': 'sandmouse.fa_error_end.txt'}
iterations = 3
all_results = []
for ind, program in enumerate(programs.keys()):
    results = []
    for i in range(iterations):
        print("running iteration", i)
        result = run(program, root + programs[program] + files[program])
        results.append(result)

    mean_result = np.mean(results)
    result_lower = mean_result - np.min(results)
    result_upper = np.max(results) - mean_result
    print(results)
    print(mean_result)
    print(result_lower)
    print(result_upper)
    all_results.append((program, ind, [mean_result], np.array([[result_lower, result_upper]]).T))
plt.gcf().clear()
for program_result in all_results:
    print(program_result)
    plt.errorbar([program_result[1]], program_result[2], yerr=program_result[3], marker='o', capsize=5)
    plt.xticks([res[1] for res in all_results], [res[0] for res in all_results])
    plt.ylabel('runtime until error in s')
fig.savefig('instrumentation.pdf')
plt.show()
