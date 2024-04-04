import os, sys
import json
# import zmq
import traceback
import subprocess
import machines
import atexit
import random
import psutil
import shlex
from gear_handler import gear_handler
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

MINPORT = 2501
MAXPORT = 22501
MAXTRIES = 5
state = ["free", "stall", "busy"]
admin_conversation = set(["sched", "shutdown"])
slave_conversation = set(["log", "complete", "offline"])

def check_port_opened(port):
    return len([b for b in psutil.net_connections() if b.laddr.port == port]) > 0

"""machine herd controller, cross-architecture scheduler."""
class network(gear_handler):
    def __init__(self):
        super().__init__()
        self._used_random_ports = set()
        self._child_pid = 0
        self._machines = [{"name": "machine", "ip": "10.0.0.1", "mac": "d8:50:e6:c3:4d:6a",
                           "children": [{"name": "echo"},
                                        {"name": "info"},
                                        {"name": "config"}]}]
        self._hosts = {}
        self.load_machines()
        self.load_work()
        atexit.register(self.__shutdown)

    def dispatch_request(self):
        return json.dumps(list(self._hosts.keys()))

    def hostname(self, hostname):
        if hostname in self._hosts.keys():
            return self._hosts[hostname]
        else:
            logger.info("hostname {} not found in machines {}".format(hostname, self._machines))

    """find_random_open_port: find first open port on cnc, store/reference used ports."""
    def find_random_open_port(self):
        while True:
            random_port = random.randint(machines.MINPORT, machines.MAXPORT)
            if not check_port_opened(random_port):
                break
            elif random_port in self._used_random_ports:
                logger.info("[++] impossibly, random port collision, retrying")
            else:
                logger.info("port {} used, retrying...".format(random_port))
        self._used_random_ports.add(random_port)
        return random_port

    """run_command_wrapper: run command cmd on machine mach."""
    def run_command_wrapper(self, mach, cmd):
        mach.wol_ping_wrapper()
        mach.control_master()
        mach.ssh_port = self.find_random_open_port()
        self.open_ssh_port(mach)
        r = mach.run_command(cmd)
        return r
    
    """
    establish_cnc(mach): establish cnc connection to machine mach.
    .=====,            .=====,  :?-ssh->:22   .=====,
    |flask| scheduler  | cnc | :?<-cnc->:666  |slave|
    '====='  :?<->:?   '====='     <-n->      '====='
    """
    def establish_cnc(self, mach):
        self.cnc_port = self.find_random_open_port()
        logger.info("[+] starting cnc for machine " + mach.name)
        self.open_ports(mach)
        
    def open_ports(self, mach):
        logger.info("[+] forwarding ports to machine " + mach.name)
        self.open_ssh_port(mach)
        self.open_cnc_port(mach)
        logger.info("[+] ports forwarded to " + mach.name)
    
    def open_ssh_port(self, mach):
        self.ssh_port = self.find_random_open_port()
        cmd = "ssh -L "+str(self.ssh_port)+":localhost:22 -O forward -S "+mach.path+" "+mach.ip
        logger.info("[+] ssh: \"" + cmd + "\"")
        sub = subprocess.Popen(shlex.split(cmd))
        ret = sub.wait()
        atexit.register(self.close_ssh_port, mach)
        return (ret == 0)

    def close_ssh_port(self, mach):
        logger.info("[+] closing ssh port to machine " + mach.name)
        cmd = "ssh -KL "+str(self.ssh_port)+":localhost:22 -O cancel -S "+mach.path+" "+mach.ip
        logger.info("[+] ssh: \"" + cmd + "\"")
        sub = subprocess.Popen(shlex.split(cmd))
        ret = sub.wait()
        return (ret == 0)
    
    def open_cnc_port(self, mach):
        logger.info("[+] forwarding ports to machine")
        cmd = "ssh -L "+str(self.cnc_port)+":localhost:666 -O forward -S "+mach.path+" "+mach.ip
        logger.info("[+] ssh: \"" + cmd + "\"")
        sub = subprocess.Popen(shlex.split(cmd))
        ret = sub.wait()
        atexit.register(self.close_cnc_port, mach)
        return (ret == 0)

    def close_cnc_port(self, mach):
        logger.info("[+] closing cnc port to machine " + mach.name)
        cmd = "ssh -KL "+str(self.cnc_port)+":localhost:666 -O cancel -S "+mach.path+" "+mach.ip
        logger.info("[+] ssh: \"" + cmd + "\"")
        sub = subprocess.Popen(shlex.split(cmd))
        ret = sub.wait()
        return (ret == 0)

    def save_work(self):
        if len(self._work) > 0:
            os.rename("work.json", "./work.json.save")
            try:
                wfp = open("work.json", "w")
                logger.info("writing work file")
                wfp.write(json.dumps(self._work))
                wfp.close()
                self._work = []
            except Exception as e:
                print("save_work exception", file=sys.stderr)
                print(e)
            
    def load_work(self):
        try:
            rfp = open("work.json", "r")
            lines = ''.join(rfp.readlines())
            rfp.close()
            if lines:
                logger.info("work file: " + lines)
                self._work = json.loads(lines)
            else:
                self._work = []
        except Exception as e:
            print("work file handler exception", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            self._work = []
        atexit.register(self.save_work)

    def save_machines(self):
        os.rename("machines.json", "./machines.json.save")
        try:
            wfp = open("machines.json", "w")
            wfp.write(json.dumps(self.machine_list()))
            wfp.close()
        except Exception as e:
            print("save_machines exception", file=sys.stderr)
            print(e)

    def load_machines(self):
        try:
            rfp = open("work.json", "r")
            _machines = json.load(rfp)
            rfp.close()
            for m in _machines:
                mach = machines.machine(m)
                self._machines.append(mach)
                self._hosts[m["name"]] = mach
            logger.info("self._machines")
            logger.info(self._machines)
            logger.critical(' '.join(list(self._hosts.keys())))
        except Exception as e:
            print("load_work exception", file=sys.stderr)
            traceback.print_exc()
            
    """{"name":"", "host":"", cmd:"", raw:"", type:""}"""
    def spawn_job_queue(self):
        rfd, wfd = os.pipe()
        self._child_pid = os.fork()
        if self._child_pid == 0:
            wfp = os.fdopen(wfd, 'w')
            os.close(rfd)
            self.scheduler_socket = self.context.socket(zmq.PAIR)
            self.scheduler_port = self.scheduler_socket.bind_to_random_port("tcp://127.0.0.1", MINPORT, MAXPORT, MAXTRIES)
            wfp.write(str(self.scheduler_port))
            logger.info("[+] spawning queue controller")
            self.queue_controller()
            wfp.close()
            sys.exit(0)
        else:
            os.close(wfd)
            rfp = os.fdopen(rfd, 'r')
            logger.info("[+] creating cnc connection to scheduler")
            self.scheduler_socket = self.context.socket(zmq.PAIR)
            self.scheduler_port_str = rfp.read()
            logger.info("[+] port received " + self.scheduler_port_str)
            self.scheduler_socket.bind_to_random_port("tcp://127.0.0.1:"+self.scheduler_port_str)
            rfp.close()
            logger.info("[+} spawned queue controller pid {}".format(self._child_pid))


    """kill_slave: kill the scheduler process."""
    def kill_slave(self):
        if self._child_pid != 0:
            logger.info("[+] killing scheduler")
            os.kill(self._child_pid)
            self._child_pid = 0


    def poll_slave_sockets(self):
        for mach in self.machines:
            mesg = mach.scheduler_socket.recv(flags=zmq.NOBLOCK)
            keys = set(mesg.keys())
            logger.info("scheduler: " + mesg)
            if keys.intersect(admin_conversation) == 1:
                key = keys[0]
                if key == "log":
                    logger.info(mesg.log)
                # elif key == "complete":
                #     scheduler.complete_job(mesg.complete)
                elif key == "shutdown":
                    logger.info("[+] machine " + mach.name + " going offline")
                

    """queue_loop: scheduler control."""
    def queue_loop(self):
        while True:
            self.poll_slave_sockets()
            
            mesg = self.scheduler_socket.recv(flags=zmq.NOBLOCK)
            keys = set(mesg.keys()) 
            if keys.intersect(slave_conversation) == 1:
                key = keys[0]
                if key == "sched":
                    self.scheduler_socket.send({"log":"[+] received a sched"})
                elif key == "shutdown":
                    self.scheduler_socket.send({"log":"[+] received shutdown, shutdown"})
                else:
                    self.scheduler_socket.send({"log":"[++] received bogus cmd {}".format(mesg)})
            else:
                self.scheduler_socket.send({"log":"[++] received bogus msg {}".format(mesg)})
            
    """process work queue in a loop."""
    def queue_controller(self):
        self.machines = list(self._machines)
        try:
            self.queue_loop()
        except KeyboardInterrupt as ki:
            logger.info("[+] received usrint {}, quitting...".format(ki))
        except Exception as e:
            logger.info("[+] received exception {}".format(e))
        logger.info("[+] saving machine conf machines.json")
        self.scheduler_socket.close()
        self.kill_slave()
    
    def __shutdown(self):
        logger.info("[+] shutdown handler")
        self.save_work()
        self.save_machines()

    machine_menu = [{"name":"power"},
                    {"name":"ssh"},
                    {"name":"install"},
                    {"name":"sleep"},
                    {"name":"version"},
                    {"name":"start"},
                    {"name":"stop"}]
    
    def machine_list(self):
        data = []
        for m in self._machines:
            mach = m.conf()
            mach["children"] = self.machine_menu
            data.append(mach)
        return [{"name":"root", "children": data}]

        
if __name__ == '__main__':
    pass

# machs = machines()

    
