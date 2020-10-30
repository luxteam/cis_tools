set -x

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

CIS_TOOLS=${SCRIPTPATH}
JENKINS_ROOT=${SCRIPTPATH}/..
JN_RUN_OPTIONS=${SCRIPTPATH}/runJenkinsAgent.conf

#ssh-keygen -t rsa
#ssh-copy-id admin@172.30.23.112

[ ! -f ${JN_RUN_OPTIONS} ] && echo '# jenkins agent options'  >> $JN_RUN_OPTIONS

HOSTNAME=`hostname`

echo 'JENKINS_SECRET=145678901890190123457890123457890' >> $JN_RUN_OPTIONS
echo 'JENKINS_SERVER=                          '        >> $JN_RUN_OPTIONS
echo 'JENKINS_AGENTNAME=`hostname`'                     >> $JN_RUN_OPTIONS

