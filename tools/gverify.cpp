#include <ymir/sys/saturn.hpp>
#include <ymir/media/loader/loader.hpp>
#include <fstream>
#include <iostream>
#include <vector>
#include <memory>
#include <unordered_map>
#include <algorithm>
#include <ymir/debug/sh2_tracer_base.hpp>
#include <ymir/savestate/savestate.hpp>
#include <map>
using namespace ymir;
static std::vector<uint32> pixels; static uint32 w,h; static uint16 buttons=0xffff;
void frame(uint32* p,uint32 x,uint32 y,void*) { w=x;h=y;pixels.assign(p,p+x*y); }
void input(peripheral::PeripheralReport& p,void*) {p.report.controlPad.buttons=static_cast<peripheral::Button>(buttons);}
struct Hist:debug::ISH2Tracer {sh2::SH2* cpu;std::unordered_map<uint32,uint64> c;uint32 bp=0;bool hit=false;std::ofstream* log=nullptr;
 void ExecuteInstruction(uint32 pc,uint16 op,bool)override{c[pc]++; if(log&&pc==bp){auto& p=cpu->GetProbe();(*log)<<std::hex<<pc;for(int i=0;i<15;i++)(*log)<<" r"<<std::dec<<i<<"="<<std::hex<<p.R(i);(*log)<<" pr="<<p.PR()<<std::endl;}}};
static void dumprange(Saturn* s,const std::string& n,uint32 a,uint32 len){std::ofstream o(n,std::ios::binary);auto& p=s->masterSH2.GetProbe();for(uint32 i=0;i<len;i++){char b=p.MemPeekByte(a+i,true);o.write(&b,1);}}
int main(int argc,char**argv){
 auto s=std::make_unique<Saturn>();
 std::array<uint8,sys::kIPLSize> bios; std::ifstream("D:/ss/Sega Saturn BIOS Pack/Sega Saturn BIOS v1.01 (JAP).bin",std::ios::binary).read((char*)bios.data(),bios.size()); s->LoadIPL(bios);
 if(argc>2){std::error_code ec;s->LoadInternalBackupMemoryImage(argv[2],true,ec);}
 smpc::PersistentSMPCData pd;pd.STE=true;s->SMPC.LoadPersistentData(pd);
 auto renderer=s->VDP.UseSoftwareRenderer(); renderer.Value()->EnableThreadedVDP1(false);renderer.Value()->EnableThreadedVDP2(false);renderer.Value()->EnableThreadedDeinterlacer(false);
 s->VDP.SetSoftwareRenderCallback({nullptr,frame});
 s->SMPC.GetPeripheralPort1().ConnectControlPad();s->SMPC.GetPeripheralPort1().SetPeripheralReportCallback({nullptr,input});
 media::Disc disc;if(!media::LoadDisc(argv[1],disc,false,[](media::MessageType,std::string msg){std::cerr<<msg<<std::endl;}))return 2;
 s->LoadDisc(std::move(disc));s->AutodetectRegion();s->CloseTray();s->Reset(true);
 Hist hist;hist.cpu=&s->masterSH2;std::map<std::string,std::unique_ptr<savestate::SaveState>> states;
 std::cout<<"READY"<<std::endl;std::string cmd;unsigned long long frames=0;
 while(std::cin>>cmd){if(cmd=="run"){int n,mask;std::cin>>n>>mask;buttons=uint16(~mask);for(int i=0;i<n;i++){s->RunFrame();frames++;}std::cout<<"FRAME "<<frames<<std::endl;}
 else if(cmd=="shot"){std::string name;std::cin>>name;std::ofstream o(name,std::ios::binary);o<<"P6\n"<<w<<" "<<h<<"\n255\n";for(auto p:pixels){char rgb[]={char(p),char(p>>8),char(p>>16)};o.write(rgb,3);}std::cout<<"SHOT "<<name<<" "<<w<<"x"<<h<<std::endl;}
 else if(cmd=="hist"){int on;std::cin>>on;if(on)hist.c.clear();s->masterSH2.UseTracer(on?&hist:nullptr);s->EnableDebugTracing(on);std::cout<<"HIST "<<on<<std::endl;}
 else if(cmd=="bp"){std::string name;std::cin>>std::hex>>hist.bp>>std::dec>>name;delete hist.log;hist.log=new std::ofstream(name);std::cout<<"BP"<<std::endl;}
 else if(cmd=="histdump"){std::string name;std::cin>>name;std::vector<std::pair<uint32,uint64>> v(hist.c.begin(),hist.c.end());std::sort(v.begin(),v.end(),[](auto&a,auto&b){return a.second>b.second;});std::ofstream o(name);for(auto&[k,c]:v)o<<std::hex<<k<<" "<<std::dec<<c<<"\n";std::cout<<"HISTDUMP"<<std::endl;}
 else if(cmd=="save"){std::string name;std::cin>>name;auto st=std::make_unique<savestate::SaveState>();s->SaveState(*st);states[name]=std::move(st);std::cout<<"SAVED "<<name<<std::endl;}
 else if(cmd=="load"){std::string name;std::cin>>name;std::cout<<"LOADED "<<s->LoadState(*states.at(name))<<std::endl;}
 else if(cmd=="dump"){std::string name;std::cin>>name;dumprange(s.get(),name,0x06000000,0x100000);dumprange(s.get(),name+".lo",0x00200000,0x100000);std::cout<<"DUMPED "<<name<<std::endl;}
 else if(cmd=="vdump"){std::string name;std::cin>>name;dumprange(s.get(),name+".v1",0x05C00000,0x80000);dumprange(s.get(),name+".v2",0x05E00000,0x80000);dumprange(s.get(),name+".cram",0x05F00000,0x1000);dumprange(s.get(),name+".v2reg",0x05F80000,0x120);std::cout<<"VDUMPED "<<name<<std::endl;}
 else if(cmd=="peek"){unsigned a,n;std::cin>>std::hex>>a>>n>>std::dec;auto& p=s->masterSH2.GetProbe();for(unsigned i=0;i<n;i++)std::cout<<std::hex<<unsigned(p.MemPeekByte(a+i,true))<<" ";std::cout<<std::dec<<std::endl;}
 else if(cmd=="poke"){unsigned a,b;std::cin>>std::hex>>a>>b>>std::dec;s->masterSH2.GetProbe().MemPokeByte(a,b,true);std::cout<<"POKED"<<std::endl;}
 else if(cmd=="exportbackup"){std::string name;std::cin>>name;auto data=s->mem.GetInternalBackupRAM().ReadAll();std::ofstream o(name,std::ios::binary);o.write((char*)data.data(),data.size());std::cout<<"BACKUP "<<name<<" "<<data.size()<<std::endl;}
 else if(cmd=="disc"){std::string name;std::getline(std::cin>>std::ws,name);media::Disc d2;bool ok=media::LoadDisc(name,d2,false,[](media::MessageType,std::string msg){std::cerr<<msg<<std::endl;});if(ok){s->LoadDisc(std::move(d2));}std::cout<<"DISC "<<ok<<std::endl;}
 else if(cmd=="reset"){s->Reset(true);std::cout<<"RESET"<<std::endl;}
 else if(cmd=="quit")break;}
}
