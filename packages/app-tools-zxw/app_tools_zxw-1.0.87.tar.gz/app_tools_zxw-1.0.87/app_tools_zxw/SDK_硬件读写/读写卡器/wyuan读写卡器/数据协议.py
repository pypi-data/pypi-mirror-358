"""
读取结果：
Len     Adr     reCmd   Status	Data[]	CRC-16
0x11	0xXX	0xee	0xee	——	    LSB	MSB

Data[]:
ENum	EPC	    Mem	    WordPtr	Num	    Pwd	    MaskAdr	MaskLen
0xXX	变长	    0xXX	0xXX	0xXX	4Byte	0xXX	0xXX

命令模块：
Len	Adr	Cmd	Data[]	LSB-CRC16	MSB-CRC16
数据各部分说明如下：
	        长度(字节)	说明
Len	        1	        命令数据块的长度，但不包括Len本身。即数据块的长度等于4加Data[]的长度。Len允许的最大值为96，最小值为4。
Adr	        1	        读写器地址。地址范围：0x00~0xFE，0xFF为广播地址，读写器只响应和自身地址相同及地址为0xFF的命令。读写器出厂时地址为0x00。
Cmd	        1	        命令代码。
Data[]	                不定	参数域。在实际命令中，可以不存在。
LSB-CRC16	1	        CRC16低字节。CRC16是从Len到Data[]的CRC16值
MSB-CRC16	1	        CRC16高字节。 算法见（UHF电子标签读写器用户手册v2.0.doc）
"""


def 读卡(data_读取到的16进制数据: str):
    """
    18000-6c协议：
    11 00 EE 00 E2 00 00 17 00 14 02 66 16 70 6B 48 83 37
    机号：第2byte数据位：00
    EPC号：E2 00 00 17 00 14 02 66 16 70 6B 48
    """
    data = data_读取到的16进制数据[9:9 + 24]
    return data
