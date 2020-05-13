SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

export CIS_TOOLS=${SCRIPTPATH}
JENKINS_ROOT=${SCRIPTPATH}/..

source ./runJenkinsAgent.conf

wget --timestamping  ${JENKINS_SERVER}/jnlpJars/agent.jar

# source scl_source enable devtoolset-7

# gcc --version

while true
do
    echo "connecting..."
    java -jar agent.jar -jnlpUrl ${JENKINS_SERVER}/computer/${JENKINS_AGENTNAME}/slave-agent.jnlp -secret ${JENKINS_SECRET} -workDir "${JENKINS_ROOT}"
    sleep 5
done


