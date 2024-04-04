import os, sys

import subprocess, shlex
import getmac
import time
import wakeonlan
import atexit
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

master_conversation = ["diag", "start", "stop", "stall", "sleep", "progress", "quit"]

def get_ip():
    routeline = subprocess.check_output(shlex.split("ip route show default"), text=True)
    return routeline.split(" ")[2]

"""mainly a controller for machine connections"""

class machine():
    def __init__(self, machine_dict):
        # def __init__(self, name=os.uname().nodename, ip=get_ip(),
        #              mac=getmac.get_mac_address()):
        super().__init__()
        self.__dict__.update(machine_dict)
        self.ip = self.ip if "ip" in dir(self) else get_ip()
        self.mac = self.mac if "mac" in dir(self) else getmac.get_mac_address()
        self.path = "~/.ssh/controlmasters/"+self.ip
        self.port = 0
        logger.info ("[+] machine "+self.name+" "+self.ip+" "+self.mac+" online")

    def conf(self):
        return {"name": self.name, "ip": self.ip, "mac": self.mac}
    
    def check_arp_entry(self):
        pass # TODO: discover arp entry missing
    
    def add_arp_entry(self):
        logger.info ("[+] adding arp entry for machine wol")
        self.admin_interface = "enp9s0"
        cmd = "sudo arp -H ether -i "+self.admin_interface+" -s "+self.ip+" "+self.mac
        logger.info ("[+] arp cmd: \""+cmd+"\"")
        return subprocess.Popen(shlex.split(cmd))
    
    def close_ports(self):
        self.console_log("[+] closing ports to machine")
        cmd = "ssh -KL "+str(self.ssh_port)+":localhost:22 -KL "+str(self.cnc_port)+":localhost:666 -O cancel -S "+self.path+" "+self.ip
        sub = subprocess.Popen(shlex.split(cmd))
        ret = sub.wait()
        return (ret == 0)
    
    def check_master_ok(self):
        self.console_log("[+] checking control master ok")
        dnp = open(os.devnull, "w")
        sub = subprocess.Popen(shlex.split("ssh -O check -S "+self.path+" "+self.ip), stdout=dnp, stderr=dnp)
        dnp.close()
        ret = sub.wait()
        return (ret == 0)

    def control_master(self):
        file_exists = self.check_ssh_file()
        if file_exists:
            master_ok = self.check_master_ok()
            if not master_ok:
                self.shutdown_control_master()
                self.start_control_master()
            else:
                logger.info ("[+] control master check OK")
        else:
            self.start_control_master()
        # if not self.check_ssh_file() or not self.check_master_ok():
        #     self.start_control_master()
        
    def start_control_master(self):
        logger.info ("[+] starting control master connection to machine")
        cmd = 'ssh -no ControlMaster=yes -o ControlPersist=yes -o ControlPath=\"'+self.path+'\" '+self.ip
        logger.info (cmd)
        dnp = open(os.devnull, "w")
        sub = subprocess.Popen(shlex.split(cmd), stdout=dnp, stderr=dnp)
        dnp.close()
        return (sub.wait() == 0)
    
    def shutdown_control_master(self):
        logger.info ("[+] shutting down control master")
        sub = subprocess.Popen(shlex.split("ssh -O exit -S"+self.path+" "+self.ip))
        return (sub.wait() == 0)

    def check_ssh_file(self):
        logger.info ("[+] checking existence of ssh control master file")
        try:
            os.stat(os.path.expanduser(self.path))
        except FileNotFoundError as err:
            return False
        except Exception as e:
            logger.info("check_ssh_file exception", file=sys.stderr)
            logger.info(e, file=sys.stderr)
            return False
        return True

    def run_command(self, cmd):
        return subprocess.check_output(shlex.split("ssh -p "+str(self.ssh_port)+" localhost "+cmd))
    
    def wol_ping_wrapper(self):
        if not self.ping():
            logger.info("[+] waking "+self.name+" "+self.mac)
            self.wol()
            while not self.ping_minute():
                logger.info("[+] retrying wol for machine "+self.name)
                self.wol()
            logger.info("[+] machine {} is woke AF".format(self.name))

    def ping_minute(self):
        logger.info ("[+] pinging machine "+self.name+" until up")
        cmd = "ping -c1 -w60 -W1 -t1 "+self.ip
        logger.info ("[+] ping cmd: \""+cmd+"\"")
        dnp = open(os.devnull, 'w')
        sub = subprocess.Popen(shlex.split(cmd), stdout=dnp)
        dnp.close()
        ret = sub.wait()
        logger.info("ping_minute ret {}".format(ret))
        return (ret == 0)
        return (sub.wait() == 0)

    def ping(self):
        logger.info ("[+] pinging machine "+self.name)
        cmd = "ping -c1 -w1 -W1 -t1 "+self.ip
        dnp = open(os.devnull, 'w')
        sub = subprocess.Popen(shlex.split(cmd), stdout=dnp)
        dnp.close()
        return (sub.wait() == 0)

    """wol: wake machine, cnc function."""
    def wol(self):
        self.add_arp_entry()
        wakeonlan.send_magic_packet(self.mac, ip_address=self.ip)

    """sleep: suspend the machine, slave function."""
    def sleep(self):
        return self.run_command_wrapper("acpitool -S")
    
    def install_wrapper(self):
        if not self.is_slave_installed():
            self.console_log("[+] base not installed, installing...", file=sys.stderr)
            self.install_slave()
        else:
            self.console_log("[+] base installed")

    def is_slave_installed(self):
        # self.run_command_wrapper("stat slave.py")
        cmd = "ssh -p "+str(self.ssh_port)+" localhost stat slave.py"
        dnp = open(os.devnull, "w")
        sub = subprocess.Popen(shlex.split(cmd), stdout=dnp)
        dnp.close()
        return (sub.wait() == 0)
    
    def install_slave(self):
        dnp = open(os.devnull, "w")
        cmd = "scp -P "+str(self.ssh_port)+" machine.py localhost:slave.py"
        logger.info (cmd)
        ret = subprocess.Popen(shlex.split(cmd)).wait()
        dnp.close()
        return (ret == 0)
    
    def spawn_slave(self):
        # return self.run_command_wrapper("./slave.py "+str(self.ssh_port))
        return subprocess.Popen(shlex.split("ssh -p "+str(self.ssh_port)+" localhost ./slave.py "+str(self.ssh_port)))

    def system(self):
        conf = self.conf()
        conf.update({"ssh_port":self.ssh_port,
                     "pub_port":self.pub_port,
                     "cnc_port":self.cnc_port,
                     "type":self.type})
        return conf

    def console_log(self, message):
        if self.is_slave:
            self.int_pub_socket.send({"log": message})
        else:
            self.cnc_socket.send({"log": message})
    
    def slave_loop(self):
        while True:
            message = self.socket.recv()
            keys = set(message.keys())
            if keys.intersect(master_conversation) == 1:
                if message.cmd == "debug":
                    self.socket.send(self.system())
                elif message.cmd == "diag":
                    self.socket.send({"log":"[++] diag ack success"})
                elif message.cmd == "start":
                    # cmd = {"name":, "type":}
                    self.socket.send({"info":"received {}".format(message.cmd)})
                elif message.cmd == "stop":
                    self.socket.send({"info":"stopped {}".format(message.data)})
                elif message.cmd == "stall":
                    self.socket.send({"stall":""})
                elif message.cmd == "sleep":
                    self.socket.send({"info":"going to sleep"})
                    self.sleep()
                elif message.cmd == "quit":
                    logger.info("received quit, quitting")
                    break
                elif message.cmd == "sleep":
                    self.sleep()
            
cpu_commands = ["start", "debug", "progress"]

