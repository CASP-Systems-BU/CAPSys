import os
import sys




#specify which query to run
kwd=sys.argv[1]

print('Compiling Query '+kwd)
runduration=60*60*9        #9h


query_name={'1':'Query1', '3':'Query3Stateful', '5':'Query5', '8':'Query8', '1d':'Query1d'}
_cmd="sed 's/QUERYNO/"+query_name[kwd]+"/g' ./pom_template.xml >> pom.xml"
os.popen(_cmd).read()


print(os.popen('mvn clean package').read())
os.popen('rm ./pom.xml').read()

