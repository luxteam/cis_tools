c:
cd c:\JN

curl -O https://rpr.cis.luxoft.com/jnlpJars/agent.jar

:up 

rem replace this line with java -jar slave.jar -jnlpUrl ...

echo reconnecting
goto up
