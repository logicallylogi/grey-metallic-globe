import csv
import sqlite3
import string
from collections import Counter
import Stemmer
import pandas

stemmer = Stemmer.Stemmer('english')

df = pandas.read_csv('Suicide_Detection.csv')

for id, entry in df.iterrows():
    sentence = entry.to_string().split(',')[0].translate(str.maketrans('', '', string.punctuation))
    sentence_meaning = []
    for word in sentence.lower().split(" "):
        word = stemmer.stemWord(word)
        con = sqlite3.connect("model.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS words(word text PRIMARY KEY, weight tinyint, score tinyint)")
        con.commit()
        meta = cur.execute("SELECT word, weight, score FROM words WHERE word == '{a}';".format(a=word))

        try:
            word, weight, score = meta.fetchone()
            for i in range(int(weight)):
                sentence_meaning.append(int(score))
            con.close()
        except TypeError:
            weight = input("What is the weight of {a}?\n> ".format(a=word))
            if weight is None:
                break
            elif int(weight) != 0:
                value = input("What is the value of {a}?\n> ".format(a=word))
                if value is None:
                    break

                cur.execute("INSERT INTO words (word, weight, score) VALUES ('{a}', '{b}', '{c}');".format(a=word,
                                                                                                           b=weight,
                                                                                                           c=value))
            else:
                cur.execute("INSERT INTO words (word, weight, score) VALUES ('{a}', '{b}', '{c}');".format(a=word,
                                                                                                           b=weight,
                                                                                                           c=0))

            con.commit()
            con.close()

    labels = [
        "NONE"
        "SELF",     # 1
        "HARM",     # 2
        "KILL",     # 3
        "RUNAWAY",  # 4
        "RAPE",     # 5
        "SEX",      # 6
        "OTHER",    # 7 (Other person - not other category)
    ]
    counter = Counter(sentence_meaning)
    full_output = []

    try:
        output = counter.most_common(1)[0]
        for item in output:
            full_output.append(labels[item])

    except IndexError:
        full_output.append("NONE")

    print(full_output)

