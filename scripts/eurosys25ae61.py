import os


# Run Q1
os.system("rm -rf ../../savepoint/*")
os.system("cp -r ../../all_savepoint/q1/* ../../savepoint/")
os.system("python3 runall.py expjson_singlequery_8slot/q1-sliding.json q1 -1")
os.system("mkdir q1 q1_custom q1_even q1_random")
os.system("mv q1-slidingjson_q1_custom* q1_custom")
os.system("mv q1-slidingjson_q1_even* q1_even")
os.system("mv q1-slidingjson_q1_random* q1_random")
os.system("mv q1_custom q1")
os.system("mv q1_even q1")
os.system("mv q1_random q1")

# Run Q2
os.system("rm -rf ../../savepoint/*")
os.system("cp -r ../../all_savepoint/q2/* ../../savepoint/")
os.system("python3 runall.py expjson_singlequery_8slot/q2-join.json q2 -1")
os.system("mkdir q2 q2_custom q2_even q2_random")
os.system("mv q2-joinjson_q2_custom* q2_custom")
os.system("mv q2-joinjson_q2_even* q2_even")
os.system("mv q2-joinjson_q2_random* q2_random")
os.system("mv q2_custom q2")
os.system("mv q2_even q2")
os.system("mv q2_random q2")

# Run Q3
os.system("python3 runall.py expjson_singlequery_8slot/q3-inf.json q3 -1")
os.system("mkdir q3 q3_custom q3_even q3_random")
os.system("mv q3-infjson_q3_custom* q3_custom")
os.system("mv q3-infjson_q3_even* q3_even")
os.system("mv q3-infjson_q3_random* q3_random")
os.system("mv q3_custom q3")
os.system("mv q3_even q3")
os.system("mv q3_random q3")


# Run Q4
os.system("rm -rf ../../savepoint/*")
os.system("cp -r ../../all_savepoint/q4/* ../../savepoint/")
os.system("python3 runall.py expjson_singlequery_8slot/q4-join.json q4 -1")
os.system("mkdir q4 q4_custom q4_even q4_random")
os.system("mv q4-joinjson_q4_custom* q4_custom")
os.system("mv q4-joinjson_q4_even* q4_even")
os.system("mv q4-joinjson_q4_random* q4_random")
os.system("mv q4_custom q4")
os.system("mv q4_even q4")
os.system("mv q4_random q4")


# Run Q5
os.system("rm -rf ../../savepoint/*")
os.system("cp -r ../../all_savepoint/q5/* ../../savepoint/")
os.system("python3 runall.py expjson_singlequery_8slot/q5-aggregate.json q5 -1")
os.system("mkdir q5 q5_custom q5_even q5_random")
os.system("mv q5-aggregatejson_q5_custom* q5_custom")
os.system("mv q5-aggregatejson_q5_even* q5_even")
os.system("mv q5-aggregatejson_q5_random* q5_random")
os.system("mv q5_custom q5")
os.system("mv q5_even q5")
os.system("mv q5_random q5")


# Run Q6
os.system("rm -rf ../../savepoint/*")
os.system("cp -r ../../all_savepoint/q6/* ../../savepoint/")
os.system("python3 runall.py expjson_singlequery_8slot/q6-session.json q6 -1")
os.system("mkdir q6 q6_custom q6_even q6_random")
os.system("mv q6-sessionjson_q6_custom* q6_custom")
os.system("mv q6-sessionjson_q6_even* q6_even")
os.system("mv q6-sessionjson_q6_random* q6_random")
os.system("mv q6_custom q6")
os.system("mv q6_even q6")
os.system("mv q6_random q6")



