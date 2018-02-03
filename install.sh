set -x

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

CIS_TOOLS=${SCRIPTPATH}
JENKINS_ROOT=${SCRIPTPATH}/..
JN_RUN_SCRIPT=${CIS_TOOLS}/../runJenkinsAgent.sh

#ssh-keygen -t rsa
#ssh-copy-id admin@172.30.23.112

[ ! -f ${CIS_TOOLS}/../ ] && echo '# jenkins agent execution script' >> $JN_RUN_SCRIPT
chmod +x $JN_RUN_SCRIPT


JENKINS_SECRET=145678901890190123457890123457890
JENKINS_SERVER=https://rpr.cis.luxoft.com
JENKINS_AGENTNAME=`hostname`

wget --directory-prefix={JENKINS_ROOT} ${JENKINS_SERVER}/jnlpJars/agent.jar


while true
do
    echo "connecting..."
    java -jar agent.jar -jnlpUrl ${JENKINS_SERVER}/computer/${JENKINS_AGENTNAME}/slave-agent.jnlp -secret ${JENKINS_SECRET} -workDir "${JENKINS_ROOT}"
    sleep 5
done
