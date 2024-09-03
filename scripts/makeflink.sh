cd ..
mvn spotless:apply
mvn clean package -e -DskipTests -Dcheckstyle.skip
cd scripts
