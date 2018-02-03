source ./jenkins_options.txt

while true
do
    echo "connecting..."
    java -jar agent.jar -jnlpUrl ${JENKINS_SERVER}/computer/${JENKINS_AGENTNAME}/slave-agent.jnlp -secret ${JENKINS_SECRET} -workDir "${JENKINS_ROOT}"
    sleep 5
done


