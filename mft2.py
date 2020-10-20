import os
import sys
import struct
import binascii
import re

full_path_1={}
full_path_0={}
num=1
class Path_Parsing:
    def __init__(self,path,cnt):
        self.seq=0
        self.arr=[]
        self.name_seq={}
        self.parent_seq={}
        self.Data={}
        try:
            self.f=open(path,'rb')
        except IOError:
            print("[-] Error:MFT File doesn't exist.")

    def Return_DirPath(self):#Return[0]isasequenceNumber,[1]isadirectorypath
        self.Read_MFT()
        self.Build_path()
        return

    def Build_path(self):
        cnt=0
        for i in self.arr:
            path=''
            init=i
            while True:
                try:
                    tmp_path=str(self.name_seq[init])
                    Data = str(self.Data[init])
                    
                    tmp_path=tmp_path
                    path=tmp_path+path+"[/]" +Data
                    p_seq=self.parent_seq.get(init)
                    init=p_seq
                    if p_seq==5:
                        break
                except KeyError:
                    break
                #printpath
            if num == 1:
                full_path_0[cnt]=path
                cnt += 1
            else:
                full_path_1[cnt]=path
                cnt += 1

        #print(full_path)
        return

    def Read_MFT(self):
        while True:
            self.buf=bytearray(self.f.read(0x400))
            if len(self.buf)!=0x400:
                print('[+]Success Read File.')
                break
            if LittleEndianToInteger(self.buf[0x16:0x18])==0x1:
                tmp=self.Dir_name_seq()
                self.arr.append(self.seq)
                self.name_seq[self.seq]=tmp[0]
                self.parent_seq[self.seq]=tmp[1]
                self.Data[self.seq]=tmp[2]
            else:
                pass
            self.seq+=1
        return


    def Dir_name_seq(self):
        attr_off=LittleEndianToInteger(self.buf[0x14:0x16])
        attr_buf=self.buf[attr_off:]
        dir_name=None
        dir_pseq=None
        Data_R=None

        while True:
            attr_type=LittleEndianToInteger(attr_buf[0x00:0x04])
            attr_size=LittleEndianToInteger(attr_buf[0x04:0x08])
            
            if attr_size==0:
                break
            if attr_type==0x00|attr_type==0xFFFF:
                break

            if attr_type==0x30:
                dir_pseq=LittleEndianToInteger(attr_buf[0x18:0x1b])
                dir_name_len=attr_buf[0x58]*2
                dir_name=Remove_uni_null(attr_buf[0x5a:0x5a+dir_name_len])

            if attr_type==0x80:
                #print(dir_name)
                Data_R = self.MFT_At_Data()

            attr_buf=attr_buf[attr_size:]
        return dir_name,dir_pseq,Data_R
    
    def MFT_At_Data(self):
        attr_off=LittleEndianToInteger(self.buf[0x14:0x16])
        attr_buf=self.buf[attr_off:]  
        while True:
            attr_type=LittleEndianToInteger(attr_buf[0x00:0x04])
            attr_size=LittleEndianToInteger(attr_buf[0x04:0x08])
            if attr_size==0:
                break
            if attr_type==0x00|attr_type==0xFFFF: 
                break
            if attr_type==0x80:
                attr_size=LittleEndianToInteger(attr_buf[0x04:0x08])
                data_area=LittleEndianToInteger(attr_buf[0x00:0x00+attr_size])
                a = (hex((attr_buf[0x00+attr_size-8:0x00+attr_size])[0]))
                #print(str(a).replace('0x','')[0])
                '''
                runlist_off=LittleEndianToInteger(attr_buf)
                runlist=attr_buf[runlist_off:]

                count=0
                tmp="00"
                clu_size=[None]*10
                clu_off=[None]*10
                calc=0
                tmp_size=[None]*10
                tmp_offset=[None]*10
                add_offset=0

                while True:
                    cal=int(tmp[0])+int(tmp[1])
                    runlist=runlist[cal:]

                    if count!=0:
                        runlist=runlist[1:]
                    tmp=str('xx'%runlist[0])
                    if runlist[0]==0x00:
                        break
                    clu_size[count]=tmp[1]
                    clu_off[count]=tmp[0]

                    tmp_size[count]=LittleEndianToInteger(runlist[1:int(clu_size[count])+1])
                    tmp_offset[count]=LittleEndianToInteger(runlist[int(clu_size[count]+1|int(clu_size[count]+int(clu_off[count])+1))])
                    tmp_offset[count]+=add_offset
                    add_offset=0
                    add_offset+=tmp_offset[count]

                    count+=1

                size=[]
                offset=[]
                '''
                break
            attr_size=LittleEndianToInteger(attr_buf[0x04:0x08])
            attr_buf=attr_buf[attr_size:]
        return data_area
    
    def Data_Parser(self, attr_off):
        attr_type=LittleEndianToInteger(attr_off[0x00:0x04])
        print(attr_type)
        attr_size=LittleEndianToInteger(attr_off[0x04:0x08])

        runlist_off=LittleEndianToInteger(attr_off)
        runlist=attr_off[runlist_off:]

        count=0
        tmp="00"
        clu_size=[None]*10
        clu_off=[None]*10
        calc=0
        tmp_size=[None]*10
        tmp_offset=[None]*10
        add_offset=0

        while True:
            cal=int(tmp[0])+int(tmp[1])
            runlist=runlist[cal:]

            if count!=0:
                runlist=runlist[1:]
            tmp=str('xx'%runlist[0])
            if runlist[0]==0x00:
                break
            clu_size[count]=tmp[1]
            clu_off[count]=tmp[0]

            tmp_size[count]=LittleEndianToInteger(runlist[1:int(clu_size[count])+1])
            tmp_offset[count]=LittleEndianToInteger(runlist[int(clu_size[count]+1|int(clu_size[count]+int(clu_off[count])+1))])
            tmp_offset[count]+=add_offset
            add_offset=0
            add_offset+=tmp_offset[count]

            count+=1

        size=[]
        offset=[]

def Remove_uni_null(uni_str):
    tmp=[]
    count=0

    while True:
        if count==len(uni_str):
            break

        if uni_str[count+1]!=0:
            han=Read_Han(uni_str[count:count+2])
            tmp.append(han)
        else:
            tmp.append(chr(uni_str[count]))
        count+=2
    return''.join(tmp)

def Read_Han(buf):
    return buf.decode('utf-16').encode('mbcs')

def LittleEndianToInteger(buf):
    val=0
    for i in range(0,len(buf)):
        multi=1
        for j in range(0,i):
            multi*=256
        val+=buf[i]*multi
    return val

if __name__=='__main__':
    if len(sys.argv) != 3:
        print("[Usage]parser.py originfile infectfile")
        sys.exit()
    else:
        for arg in sys.argv[1:]:
            input_file = arg
            MFT=Path_Parsing(input_file,num)
            Path_Parsing.Return_DirPath(MFT)
            num += 1

    cnt_0 = 0
    cnt_1 = 0
    full_path_0 = dict({key: value for key, value in full_path_0.items() if value.split('[/]')[0] != 'None'}) ## 
    full_path_1 = dict({key: value for key, value in full_path_1.items() if value.split('[/]')[0] != 'None'}) ##
    while True:
        if cnt_0 in full_path_0:
            split_Str_0=full_path_0[cnt_0].split('[/]')
            if list(full_path_0.keys())[-1] == cnt_0:
                break
            else:
                cnt_0 += 1
                while True:
                    if cnt_1 in full_path_1:
                        split_Str_1=full_path_1[cnt_1].split('[/]')
                        if split_Str_1[0].find(split_Str_0[0]) != -1:
                            if split_Str_0[1].find(split_Str_1[1]) != -1:
                                if list(full_path_1.keys())[-1] == cnt_1:
                                    cnt_1 = 0
                                    break
                                else:
                                    cnt_1 += 1
                                    continue
                            else:
                                print(split_Str_0[0] + "->" + split_Str_1[0] + "로 변경됨")
                                cnt_1 +=1
                                continue
                        else:
                            if list(full_path_1.keys())[-1] == cnt_1:
                                cnt_1 = 0
                                break
                            else:
                                cnt_1 += 1
                                continue
                    else:
                        if list(full_path_1.keys())[-1] == cnt_1:
                            cnt_1 = 0
                            break
                        else:
                            cnt_1 += 1
                            continue
        else:
            cnt_0 += 1
            continue

            

