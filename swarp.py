'''
Swarp - switch arp tool (for HP Switches) @2017
Python: V3
Sys: Windows
LibDep: 
    paramiko, getopt
Instalação das dependências:
    pip install paramiko getopt
Utilização: 
    python swarp.py -r <remoteip> -p <sshport> -u <user>
    python swarp.py --remote=<remoteip> --port=<sshport> --user=<user>
    
wr: Clayton G. C. Santos
'''

import paramiko, sys, getopt, re, time, subprocess, getpass, socket
from subprocess import check_output

#
def checkInfo(ip):
    try:
        text=check_output("wmic /node:%s computersystem get username, Name, Manufacturer" % (ip), timeout=1, stderr=subprocess.STDOUT).decode("cp858") 
        fields = text.splitlines()[2] # retira cabeçalho wmic
        print ("\t" + '\t'.join(fields.split())) #tabula dados recuperados
    except subprocess.TimeoutExpired as e:
        print("\t<Timeout>")
    except subprocess.CalledProcessError as e:
        print("\t<Undefined>")
        
def getHelp(error):
    print ('swarp.py -r <remoteip> -p <sshport> -u <user>')
    if error:
        sys.exit(2)
    else:
        sys.exit()
    
def main(argv):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    host = ''
    port = 22
    user = ''
    password = ''
    if len(sys.argv) == 1: 
        getHelp(False)
    
    else:
        try:
            opts, args = getopt.getopt(argv,"hr:p:u:s:",["remote=","port=","user=","password=",])
        except getopt.GetoptError:
            getHelp(True)
        
    for opt, arg in opts:
        if opt == '-h':
            getHelp(False)
        elif opt in ("-r","--remote"):
            remote = arg            
        elif opt in ("-p","--port"):
            port = int(arg)
        elif opt in ("-u","--user"):
            user = arg
        #elif opt in ("-s","--password"):
        #    password = arg

    if user=='':
        user=input("Login: ");
    password=getpass.getpass("Password: ")
    
    #Separa possível lista de hosts
    hosts = remote.split(',')
    for host in hosts:
        try:    
            ssh.connect(host, port, user, password, timeout=None)
        except paramiko.ChannelException as e:
            print("Erro de Conexao no Host: "+e)
            sys.exit(2)
        except OSError as e:
            print("Host não respondeu.\n")
            sys.exit(2)
        channel = ssh.invoke_shell(width=8000,height=100000)
        channel.send(" ")
        time.sleep(3)
        output=channel.recv(6024)
        name = output.decode("utf-8")
        
        #recupera o nome do switch HP entre <>
        print("\nSwitch "+host+": ", end="")
        for line in name.splitlines():
            regexp = re.compile(r'\<')
            if regexp.search(line):
                print(line)
                
        #imprime cabeçalho dos dados apresentados
        print("Endereço IP\tMAC\t\tVLAN\tInterface\tAging\tTipo\tFab.\tNome\tUsuário")
                
        #envia os comandos em sequência para o console, desabilitando o --more--
        channel.send("screen-length disable\n display arp all\n")
        time.sleep(3)
        output=channel.recv(6024)
        read = output.decode("utf-8");
        
        for line in read.splitlines():
            #regex para filtrar saída do switch, somente ips.
            regexGE = re.compile(r'^[1-9]')
            if regexGE.search(line):
                print('\t'.join(line.split()),end="") 
                checkInfo(line.split(' ')[0])
        ssh.close()

if __name__=="__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
        
    finally:
        print("\nsaindo...")