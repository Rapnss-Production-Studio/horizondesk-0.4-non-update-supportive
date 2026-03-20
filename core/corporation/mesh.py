import socket
import threading
import time
import json
from core.security.neuro_crypt import shield

class MeshNode:
    """
    P2P Networking Layer.
    Allows OmniAgents to discover each other on LAN/WAN.
    """
    def __init__(self, port=58440):
        shield.check_integrity()
        self.port = port
        self.peers = {} # IP -> ID
        self.my_id = shield._fingerprint
        self.running = False
        
    def start_discovery(self):
        """Starts UDP Beacon and Listener."""
        self.running = True
        threading.Thread(target=self._broadcast_beacon, daemon=True).start()
        threading.Thread(target=self._listen_beacon, daemon=True).start()
        return "Mesh Discovery Protocol Active."

    def _broadcast_beacon(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        data = json.dumps({"type": "OMNI_HELLO", "id": self.my_id}).encode()
        try:
            while self.running:
                sock.sendto(data, ('<broadcast>', self.port))
                time.sleep(5)
        except: pass

    def _listen_beacon(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.port))
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                if msg.get('type') == "OMNI_HELLO" and msg.get('id') != self.my_id:
                     self.peers[addr[0]] = msg.get('id')
                     print(f"[Mesh] Peer Discovered: {addr[0]} ({msg.get('id')[:6]})")
            except: pass

    def list_peers(self):
        return self.peers

# Singleton
mesh = MeshNode()
