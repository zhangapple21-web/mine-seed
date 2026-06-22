import socket
import struct
import threading
import time

# ==========================================
# 1. 隐蔽触发：端口敲击 (Port Knocking) 验证模块
# ==========================================
class KnockTrigger:
    """
    通过特定序列的 UDP 端口敲击触发隐藏指令
    顺序敲击 7000 -> 8000 -> 9000 即可激活状态
    """
    def __init__(self):
        self.sequence = [7000, 8000, 9000]
        self.state = {}  # 记录每个IP的敲击进度

    def check_knock(self, client_ip, port):
        current_step = self.state.get(client_ip, 0)
        if port == self.sequence[current_step]:
            self.state[client_ip] = current_step + 1
            if self.state[client_ip] == len(self.sequence):
                self.state[client_ip] = 0  # 重置状态
                return True
        else:
            self.state[client_ip] = 0  # 顺序错误则重置
        return False

# ==========================================
# 2. 自定义底层协议与拆分通信 (Custom Protocol & Fragmentation)
# ==========================================
class CustomProtocol:
    """
    协议结构 (Total 8 bytes header + Payload):
    [2 Bytes: Magic Number][2 Bytes: Action][4 Bytes: Length][Payload]
    """
    MAGIC = 0x5443  # 暗号 "TC"
    CMD_SYNC = 0x01
    CMD_DATA = 0x02

    @staticmethod
    def pack(cmd_type, data: bytes) -> bytes:
        header = struct.pack("!HHI", CustomProtocol.MAGIC, cmd_type, len(data))
        return header + data

    @staticmethod
    def unpack(header_bytes: bytes):
        if len(header_bytes) < 8:
            return None
        magic, cmd_type, length = struct.unpack("!HHI", header_bytes)
        if magic != CustomProtocol.MAGIC:
            return None
        return cmd_type, length

    @staticmethod
    def fragment_send(sock, cmd_type, data: bytes, chunk_size=2):
        """
        将标准内容拆分成微小的碎片(分片混淆)绕过流量深度检测
        """
        packet = CustomProtocol.pack(cmd_type, data)
        for i in range(0, len(packet), chunk_size):
            sock.send(packet[i:i+chunk_size])
            time.sleep(0.01)  # 微时延规避流检测

# ==========================================
# 3. 核心节点：双模接收端 (Server / Receiver)
# ==========================================
class SecureMirrorNode:
    def __init__(self, host="127.0.0.1", tcp_port=9999):
        self.host = host
        self.tcp_port = tcp_port
        self.knocker = KnockTrigger()
        self.authenticated_clients = set()
        self.is_running = True

    def start_knock_listener(self):
        """启动 UDP 端口敲击监听"""
        def listen(port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.host, port))
            while self.is_running:
                _, addr = sock.recvfrom(1024)
                if self.knocker.check_knock(addr[0], port):
                    print(f"[*] [Trigger] IP {addr[0]} 成功激活隐藏触发指令。")
                    self.authenticated_clients.add(addr[0])

        for p in self.knocker.sequence:
            threading.Thread(target=listen, args=(p,), daemon=True).start()

    def start_tcp_server(self):
        """启动底层的自定义 TCP 通道"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.tcp_port))
        server.listen(5)
        print(f"[*] [TCP] 核心通信通道已在端口 {self.tcp_port} 隐蔽建立...")

        while self.is_running:
            conn, addr = server.accept()
            # 零信任验证：未经过端口敲击触发的IP直接拒绝连接
            if addr[0] not in self.authenticated_clients:
                conn.close()
                continue
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        """解析自定义语法，实现内网数据镜像和高效对话"""
        try:
            while True:
                header = conn.recv(8)
                res = CustomProtocol.unpack(header)
                if not res:
                    break
                cmd_type, length = res
                
                # 循环接收被拆分的碎片数据
                payload = b""
                while len(payload) < length:
                    chunk = conn.recv(length - len(payload))
                    if not chunk:
                        break
                    payload += chunk

                if cmd_type == CustomProtocol.CMD_SYNC:
                    print(f"[+] [内网同步] 收到映射指令，正在同步数据对象: {payload.decode('utf-8')}")
                elif cmd_type == CustomProtocol.CMD_DATA:
                    print(f"[+] [核心对话] 提取核心解构数据: {payload.decode('utf-8')}")
        except Exception:
            pass
        finally:
            conn.close()

# ==========================================
# 4. 自动化控制端演示 (Client / Sender)
# ==========================================
def simulate_pipeline():
    # 初始化服务端结构
    node = SecureMirrorNode()
    node.start_knock_listener()
    threading.Thread(target=node.start_tcp_server, daemon=True).start()
    time.sleep(1)

    # 步骤 1: 触发隐藏指令 (依次敲击UDP端口)
    print("\n--- 阶段 1: 触发隐藏指令 ---")
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for port in:
        udp_client.sendto(b"\x00", ("127.0.0.1", port))
        time.sleep(0.1)
    time.sleep(0.5)

    # 步骤 2: 建立专属 TCP 路径并发送自定义分片语法
    print("\n--- 阶段 2: 逆向映射与轻量级对话 ---")
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_client.connect(("127.0.0.1", 9999))
        
        # 发送映射克隆指令
        CustomProtocol.fragment_send(tcp_client, CustomProtocol.CMD_SYNC, b"PROJECT_MAP_001")
        
        # 发送极其精简的精简核心对话(解构后的数据)
        CustomProtocol.fragment_send(tcp_client, CustomProtocol.CMD_DATA, b"{id:101,action:run}")
        
        time.sleep(1)
    except Exception as e:
        print(f"[-] 连接失败: {e}")
    finally:
        tcp_client.close()
        node.is_running = False

if __name__ == "__main__":
    simulate_pipeline()
