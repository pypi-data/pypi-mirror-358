
import matplotlib.pyplot as plt
import numpy as np

class Komponenta:
    sta: str
    chan: str
    a03: float
    pga: float
    maxf: float
    maxpsa: float
    nf: int
    f: list
    psa: list

    def __init__(self):
        self.sta=''
        self.chan=''
        self.a03=float()
        self.pga=float()
        self.maxf=float()
        self.maxpsa=float()
        self.nf=0
        self.f=[]
        self.psa=[]

    def lval(l,lvar):
        nlf=l.find(lvar)
        if nlf>0:
            ll=l[nlf:].split(':',1)
            lll=ll[1].split(';')
            if len(lll)>0:
                return lll
        return None
  
def f_pga_eq_psa(fpsa,psa,pga,fpsamax):
    for i,f in reversed(list(enumerate(fpsa))):
        if (f > fpsamax): continue
        if (psa[i]<pga): break
    #(psa[i+1]-psa[i])/(fpsa[i+1]-fpsa[i])=(pga-psa[i])/(pf-fpsa[i])
    pf=fpsa[i]+(fpsa[i+1]-fpsa[i])/(psa[i+1]-psa[i])*(pga-psa[i])
    return pf

def read_psa(ifile):
    #az: list
    az=[]

    l_n=-1
    ifreq=-1
    sta=''
    chantype=''
    fi = open(ifile,'r')

    #region:  Hostěradice
    #time:  2014-06-01 00:43
    #magnitudo:  2.0
    #net: 
    #epicentral distance [km]:  16

    radka=fi.readline()
    p=radka.rstrip().split(':',1)
    if "evid" in radka: evid=p[1].strip()
    radka=fi.readline()
    p=radka.rstrip().split(':',1)
    if "reg" in radka: reg=p[1].strip()
    radka=fi.readline()
    p=radka.rstrip().split(':',1)
    if "time" in radka: cas=p[1].strip()
    radka=fi.readline()
    p=radka.rstrip().split(':',1)
    if "mag" in radka: mag=p[1].strip()
    radka=fi.readline()
    p=radka.rstrip().split(':',1)
    if "net" in radka: net=p[1].strip()
    radka=fi.readline()
    p=radka.rstrip().split(':',1)
    if "epi" in radka: dist=p[1].strip()

    while True:
        radka=fi.readline()
        if radka == "":
             break
        l=radka.rstrip()
        
        if l_n<0:
            if len(l)>0: l_n=0
        elif l_n==0:
            if len(l)>0: l_n=l_n+1
        elif l_n==1:
            if len(l)==0: l_n=2
        elif l_n==2:
            if len(l)>0: l_n=l_n+1
        elif l_n==3:
            if len(l)>0: l_n=l_n+1
            else: l_n=-1
        elif l_n==4:
            if l[0:2]=="f[": 
                l_n=l_n+1
                ifreq=-1
        elif l_n==5:
            if len(l) == 0: l_n = 6
            elif l[0:3] == "---": l_n = 7
        else: pass

        #print(l_n,l,sep=': ')

        if l_n < 0:
            pass
        elif l_n==0:
            zz=[]
            p=l.split(':')
            if len(p)>1:
                p1=p[1].strip().split()
                sta=p1[0].strip()
                chantype=p1[1].strip()
        elif l_n==3:
            z=Komponenta()
            p=l.strip().split()
            if len(p)>1:
                z.sta=p[0].strip()
                z.chan=p[1].strip()
                z.chan=chantype+z.chan[-1]
        elif l_n==4:
            if "a03" in l:
                p=l.split(':')
                if len(p)>1:
                    p1=p[1].strip().split(';')
                    z.a03=float(p1[0])
                    z.pga=float(p1[1])
            if "max" in l:
                p=l.split(':')
                if len(p)>1:
                    p1=p[1].strip().split(';')
                    z.maxf=float(p1[0])
                    z.maxpsa=float(p1[1])
                    
        elif l_n==5:
            if ifreq<0: ifreq=0
            else:
                p=l.strip().split(';')
                z.f.append(float(p[0]))
                z.psa.append(float(p[1]))
                ifreq=ifreq+1
        elif l_n==6:
            z.nf=ifreq
            zz.append(z)
            del z
            l_n=2
        elif l_n==7:
            z.nf=ifreq
            zz.append(z)
            del z
            l_n=-1
            #for pz in zz:
            #    print(pz.sta,chantype+pz.chan[-1],pz.a03,pz.pga,pz.maxf,pz.maxpsa,pz.nf)
            az.append(zz)
        else: pass

    fi.close()
    return az,reg,cas,net,evid,mag,dist

def plot_psa_sta(zz,reg,cas,net,evid,mag,dist):
    numo=1000000.0
    dBl=60.0

    #x-axis: frequency  y-axis: mm/s/s
    fig = plt.figure(figsize=(8, 6), dpi=100)
    #plt.title("PSA   "+zz[0].sta+"_"+zz[0].chan[0:-1]+"   "+reg+" "+cas)
    plt.title("PSA   "+zz[0].sta+"     "+reg+" "+cas)
    plt.xlabel('f [Hz]')
    #plt.ylabel('PSA [nm/s^2] [dB]')
    #plt.ylabel('PSA $\mathrm{[{\mu}m/s^2] [dB]}$')
    #plt.axis((0.5,50.0,80.0-dBl,165.0-dBl))
    plt.ylabel('PSA $\mathrm{[mm/s^2] }$')
    plt.xlim(0.5,50.0)
    plt.ylim(0.04,1080.0)
    plt.grid(which='both', axis='both')

    for pz in zz:
        pf=f_pga_eq_psa(pz.f,pz.psa,pz.pga,pz.maxf)
        print("{};{};{};{};{};{};{};{};{};{};{};{};{}".format(net,evid,cas,reg,mag,dist,pz.sta,pz.chan,pz.a03/numo,pz.pga/numo,pz.maxf,pz.maxpsa/numo,pf))
        #p=plt.semilogx(pz.f,20*np.log10(pz.psa)-dBl,label=pz.chan[-1])
        #color = p[0].get_color()
        ##plt.plot((pz.maxf),20*np.log10(pz.maxpsa)-dBl,'o',c=color,label="max PSA "+pz.chan[-1])
        #plt.plot((pz.maxf),20*np.log10(pz.maxpsa)-dBl,'o',c=color)
        ##plt.axhline(20*np.log10(pz.pga)-dBl, linestyle='--',color=color,label="PGA "+pz.chan[-1])
        #plt.axhline(20*np.log10(pz.pga)-dBl, linestyle='--',color=color)
        p=plt.loglog(pz.f,np.array(pz.psa)/numo,label=pz.chan[-1])
        color = p[0].get_color()
        #plt.plot((pz.maxf),pz.maxpsa/numo,'o',c=color,label="max PSA "+pz.chan[-1])
        plt.plot((pz.maxf),pz.maxpsa/numo,'o',c=color)
        #plt.axhline(pz.pga/numo, linestyle='--',color=color,label="PGA "+pz.chan[-1])
        plt.axhline(pz.pga/numo, linestyle='--',color=color)
        
    YYMMDDmmss=cas.replace(' ','').replace(':','').replace('-','')
    plt.plot([], [], 'o', label="max PSA",color='gray')
    plt.plot([], [], '--', label="PGA",color='gray')
    plt.legend(loc='lower right')
    #plt.savefig("psaf_"+zz[0].sta+"_"+zz[0].chan[0:-1]+"_"+YYMMDDmmss+".png")
    #plt.show()
    return fig

