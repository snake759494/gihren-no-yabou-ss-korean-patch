"""Small deterministic SH-2 emitter for audited game hooks (big endian)."""
import struct

class SH2:
    def __init__(self,base):self.base=base;self.words=[];self.labels={};self.fix=[];self.pool=[]
    @property
    def pc(self):return self.base+len(self.words)*2
    def emit(self,*v):self.words.extend(v)
    def label(self,name):assert name not in self.labels;self.labels[name]=self.pc
    def imm(self,n,v):assert -128<=v<=255;self.emit(0xe000|(n<<8)|(v&255))
    def mov(self,n,m):self.emit(0x6003|(n<<8)|(m<<4))
    def addi(self,n,v):self.emit(0x7000|(n<<8)|(v&255))
    def lit(self,n,value):
        key=('literal',len(self.pool));self.pool.append((key,value));self.fix.append((len(self.words),'lit',n,key));self.emit(0)
    def branch(self,kind,target):self.fix.append((len(self.words),kind,0,target));self.emit(0)
    def finish(self):
        if self.pc%4:self.emit(9)
        for key,value in self.pool:self.label(key);self.emit(value>>16,value&65535)
        for pos,kind,n,target in self.fix:
            pc=self.base+pos*2;dst=self.labels[target]
            if kind=='lit':
                d=(dst-((pc+4)&~3))//4;assert 0<=d<=255;v=0xd000|(n<<8)|d
            else:
                d=(dst-pc-4)//2
                if kind in ('bra','bsr'):assert -2048<=d<2048;v={'bra':0xa000,'bsr':0xb000}[kind]|(d&4095)
                else:assert -128<=d<128;v={'bt':0x8900,'bf':0x8b00,'bt/s':0x8d00,'bf/s':0x8f00}[kind]|(d&255)
            self.words[pos]=v
        return struct.pack('>'+str(len(self.words))+'H',*self.words)

def jump_stub(address):
    # Aligned entry: MOV.L @(1,PC),R0 / JMP @R0 / NOP / NOP / address.
    return struct.pack('>4HI',0xd001,0x402b,9,9,address)
