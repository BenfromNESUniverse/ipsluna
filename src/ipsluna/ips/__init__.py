from ctypes import c_ulong
class OffsetError(Exception):
    """
    Raised when attepting to perform an illegal operation due to offset clashing
    """
    pass

class ScopeError(Exception):
    """
    Raised when job scope exceeds limitations of IPS.
    """


    
        
        

class ips:
    class instance:
        """
        Task stored in ips file storing data for modification. 
        """
        def __init__(self, offset : int,data : bytes | bytearray | tuple,name : str = None):
            """
            IPS instance initialization 
            :param int offset: Offset for where the patcher will write to
            :param str name: The secondary key "name" used to provide more human information on the instance.
            :param data: The integrity of the IPS 
            :type data: bytes or bytearray or tuple
            :raises TypeError: if offset is not integral
            :raises TypeError: if name is not string or None
            :raises ScopeError: if offset is above 0xFFFFFF or smaller than zero.
            """
            if not isinstance(data,(bytes,bytearray,tuple)): raise TypeError("Instance data is invalid!")
            if len(data) != 2 if isinstance(data,tuple) else False: raise ScopeError("Tuple has invalid data!")
            if not isinstance(offset, int): raise TypeError("Offset is not integral!")
            if offset > min(0xFFFFFF, (2**super().bitsize)-1): raise ScopeError("Offset exceeds limitations of IPS")
            if offset < 0: raise ScopeError("Offset is below zero and therefore impossible!")
            if not isinstance(name, str) and name is not None: raise TypeError("Given name is not of type string and is therefore unsuitable")
            self.rle,self.offset,self.data = isinstance(data, tuple),offset,data 
            self.size = data[1] if self.rle else len(data)
            self.end = self.offset + self.size
            self.name = name if name is not None else f"Unnamed patch at {offset}"

            
        def give_name(self,name : str):
            """
            Allows the user to provide the instance a specified name
            :type str name: The name to give to the instance
            :raises TypeError: if name is not string
            """
            if not isinstance(name, str):
                raise TypeError("Given name is not of type String!")
            self.name = name
        def noRLE(self):
            """
            Converts instance of RLE to noRLE
            """
            if self.rle:
                self.rle = False
                self.data = tuple(self.data[1]*self.data[0])
            self.end = self.offset + self.size
        def RLE(self):
            if not self.rle:
                temp = bytes([self.data[1]])*self.size 
                if self.data == temp: self.data = self.data[1],self.size
                else: raise ScopeError("Cannot convert non-repeating data into RLE")


        def iwrapper(give) -> object:
            def wrap(self, data : bytes | bytearray | int, override : int = False, sustain : bool = True):
                if not isinstance(data,(bytes,bytearray,tuple)): raise TypeError("`data` must be type `bytes`, `bytearray`, or `tuple`.") 
                if not isinstance(override,bool): raise TypeError("`override` must be type `bool`")
                if not isinstance(sustain,bool): raise TypeError("`sustain` must be type `bool`")
                end = self.offset + (data[0] if isinstance(data,tuple) else len(data))
                if end > min(0xFFFF,(2**super().bitsize)-1): raise ScopeError("`data` writes beyond scope") 
                if self.end == self.offset: 
                    if isinstance(data, tuple): print("Wriring Zero data will increase the Filesize, Complexity and occupy an offset")
                    else: raise ScopeError("noRLE data cannot have length of zero")
                    clashes = super().in_range(self.offset,end)
                if len(clashes):
                    if override: 
                        for ins in clashes: super().remove(ins)
                    else: raise ScopeError("instance `data` exceeds scope of parent")
                give(self,data,override,sustain)
            return wrap

        @iwrapper
        def give_RLE(self,data : tuple,override : int = False, sustain : bool = True) -> tuple:
            """
            Gives immediate RLE instance to specified instance.
            :param byte: The byte to be looped in RLE
            :param int length: The run length for the byte.
            :type byte: bytes or bytearray
            :return: tuple by (byte,offset)
            :rtype: tuple
            :raises TypeError: if byte is not of type `bytes` or `bytearray`
            :raises TypeError: if length is not integral
            :raises ScopeError: if length is over 0xFF or less than zero.
            :raises ScopeError: if length of `byte` is does not equal one.
            """
            if not isinstance(data[1],tuple):
                raise TypeError(f"Type Error : {data[1]} is not a tuple object.")
            if not isinstance(data[0], int):
                raise TypeError(f"Type Error : {data[0]} is not integer")
            if data[0] > min(0xFFFF, (2**super().bitsize)-1) or data[0] < 0:
                raise ScopeError(f"RLE Error : {data[0]} is either above 255 and therefore too large, or smaller than zero and therefore impossible!")
            if len(data[1]) != 1:
                raise ScopeError(f"RLE ERROR : {data[1]} is either too long or zero length, please ensure that this is a singular byte!")
            if not data[0]:
                print("Warning : Zero Length data has been wrote, this will not write anything and may break some IPS patchers.")
            self.rle = True 
            self.data = data
            self.end = self.offset + self.size
            return self.data

        @iwrapper
        def give_noRLE(self,data : bytes | bytearray,override : int = False, sustain : bool = True) -> bytes:
            """
            Gives immediate noRLE instance to specified instance.
            :param data: The byte to be looped in RLE
            :type data: bytes or bytearray
            :return: bytearray of data
            :rtype: bytearray
            :raises TypeError: if data is not of type `bytes` or `bytearray`
            :raises ScopeError: if length of data is over 0xFFFF or less than zero.
            """
            if not isinstance(data,(bytes,bytearray)): raise TypeError(f"Given data is not bytes or bytearray type!")
            if len(data) > min(0xFFFF, (2**super().bitsize)-1) or len(data) < 0: raise ScopeError(f"Given data is either above 65535 and therefore too large, or smaller than zero and therefore impossible!")
            if len(data) == 0: print("Warning : Zero Length data has been wrote, this will not write anything and may break some IPS patchers.")
            self.rle = False
            self.data = data
            self.size = len(self.data)
            self.end = self.offset + self.size

        def give(self, data : tuple | bytes | bytearray,override : int = False, sustain : bool = True) -> tuple | bytearray: 
            """
            nospecific data modifier used for human interaction or unkown instance type
            :param data: The data to insert into the instance
            :type data: bytes or bytearray or tuple
            :return: bytearray or tuple of data
            :rtype: tuple or bytearray
            :raises TypeError: if data is not of type `bytes` or `bytearray`
            :raises ScopeError: if length of data is over 0xFFFF or less than zero.
            """
            if isinstance(data,tuple): return self.give_RLE(data, override, sustain) 
            if not isinstance(data,(bytes,bytearray)): return self.give_noRLE(data, override, sustain)
            raise TypeError("Unexpected type for data!")
        """
        class supporting intimate interactions with the normalized ips data.
        """

    def __init__(self, patch : bytes | bytearray, bitsize : int = 24):
        """
        initialization maps out all instances in normalized dictionary into `instances`
        :raises TypeError: if normalized is not type `dict`
        """
        count, changes,patch = 0, {}, patch[5:-3]
        while count != len(patch):
            count += 8
            if patch[count - 5] > 0 or patch[count - 4] > 0:
                size = int(patch[count - 5:count - 3].hex(),16)
                changes[int(patch[count-8:count - 5].hex(),16)] = patch[count - 3:count + size - 3]
                count += size - 3
            else:  #Handle RLE, only if NON-RLE is not met     
                changes[int(patch[count-8:count - 5].hex(),16)] = int(patch[count - 3:count - 1].hex(),16),bytes([patch[count - 1]]),    
        if not isinstance(changes,dict):
            raise TypeError("normalized is not type `dict` and therefore cannot be accessed")
        if not isinstance(bitsize, int):
            raise TypeError("specified bitsize is not type `int`")
        if bitsize % 8 or not bitsize or bitsize > c_ulong(-1).value.bit_length(): raise ScopeError("specified bitsize impossible")
        self.instances = []
        self.bitsize = bitsize
        
        for offset in changes: self.instances.append(self,self.instance(self,offset=offset,data=changes[offset]))

    def get_instance(self, specifier : str | int | instance) -> object | None: 
        hold = self.get_instances(specifier)
        if len(hold): return hold[0]
    def get_instances(self,specifier : str | int) -> tuple:
        """
        return generator by name or ID
        :param specifier: The name or ID of desired instance
        :type specifier: str or int to match desired instance
        :return: generator to provide all potentially desired instances
        :rtype: object
        """
        return tuple(match for match in self.instances if (match.name == specifier if isinstance(specifier,str) else match.offset == specifier))
    def in_range(self,start : int = 0, end : int = None) -> tuple:
        if end is None: end = (2**self.bitsize)-1
        elif not isinstance(end, int): raise TypeError("End of range must be integral or None") 
        if not isinstance(start, int): raise TypeError("start of range must be integral or None")  
        if start < 0: raise ScopeError("Starting range cannot be negative!") 
        if end < 0: raise ScopeError("Ending range cannot be negative!")
        """
        returns generator providing instances within a range in offset
        :param int start: Starting offset for search
        :param int end: Ending offset for search
        :return: returns generator object for requested data
        :rtype: object:
        :raises TypeError: if start is not integral
        :raises TypeError: if end is not integral
        """
        return tuple(instance for instance in self.instances if instance.offset >= start and instance.offset < end) 
    def insert(self, new : instance, override : bool = False, sustain : bool = True):
        #self is ips, new is instance obj. Override is flag to avoid overwrites. #sustain attempts to keep old patch data instead of removing it.
        """
        Insert an instance into an ips object.
        :param instance new: instance needed to be implemented
        :param bool override: Override flag, should clashing data be removed. Disabled by default
        :param bool sustain: Sustain flag, should data around new data be kept by moving the patches? Enabled by default [Only triggered when overriding]
        """
        
        if not isinstance(new, self.instance): raise TypeError("provided instance is not instance")
        if not isinstance(override, bool): raise TypeError("provided override flag is not of type Bool") 

        lowercheck = tuple(self.in_range(end = new.offset)) 
        if len(lowercheck):
            lowercheck = lowercheck[-1] 
            if lowercheck.end > new.offset:
                if override:
                    if sustain:
                        if lowercheck.rle:
                            lowercheck.give_RLE(lowercheck[0],new.offset-lowercheck.end)
                        else: 
                            lowercheck.give_noRLE(lowercheck.data[lowercheck.offset-new.end:])
                    else: 
                        self.remove(lowercheck)  
                else:
                    raise OffsetError(f"{lowercheck.name} write into areas occupied by {new.name}") 
        uppercheck = tuple(self.in_range(new.offset, new.end)) 
        if len(uppercheck):
            if override:
                for ins in uppercheck: self.remove(ins) 
                uppercheck = uppercheck[-1] 
                if sustain: 
                    if uppercheck.rle:
                        uppercheck.give_RLE(uppercheck.data[1],uppercheck.offset-new.end)
                    else: 
                        uppercheck.give_noRLE(uppercheck.data[uppercheck.offset-new.end:])
                    self.move(uppercheck,new.end)
                else: self.remove(uppercheck)  
            else: raise OffsetError(f"{new.name} writes into areas between {uppercheck[0].offset} and {uppercheck[-1].end}")


        uppercheck = tuple(self.in_range(new.end,0xFFFFFF+0xFFFF if self.bitsize >= 32 else (2**self.bitsize)-1))
        if len(uppercheck):
            uppercheck = self.instances.index(uppercheck[0]) 
        else:
            uppercheck = -1
        self.instances.insert(uppercheck,new)    
    def remove(self, instances : instance | str | int) -> instance | tuple:
        """
        Used to remove an instance from an ips class
        :param patch:
        :type patch: instance or str or int
        :raises TypeError: if nor str, int or instance is provided
        :raises KeyError: if patch is not present in ips
        """
        if isinstance(instances,(str,int)):
            for ins in tuple(self.get_instances(instances)): self.remove(ins)
        elif isinstance(instances,self.instance): self.instances.remove(instances)
        else: raise TypeError("given patch is not an instance.")
        return instances   
    def move(self, Instance : instance, offset : int,override : bool = False):
        if isinstance(Instance,(str,int)):
            Instance = self.get_instances(Instance) 
            if len(Instance): 
                Instance = Instance[0] 
            else: raise IndexError("No Instance exists by discriminator provided")
        if not isinstance(Instance,self.instance):
            raise Exception(f"Type Error : {Instance} is not an instance or instance name/offset.")
        if Instance not in self.instances:
            raise Exception(f"Key Error : {Instance} is not an instance in this class")
        if offset > (2**self.bitsize)-1 or offset < 0:
            raise Exception(f"Number Error : {offset} is either over {0xFFFF + 0xFFFF if self.bitsize >= 32 else (2**self.bitsize)-1} or smaller than zero which is impossible!")
        self.remove(Instance)
        try:
            self.insert(self.instance(offset,Instance.data,Instance.name),override)
        except OffsetError:
            self.insert(Instance)
    
        

def build(base : bytes | bytearray, prepatch : bytes | bytearray, legal : bool = None, bitsize : int = 24) -> bytes:
        """
        Used to create an IPS file when comparing a modified file to a base file. 
        :param base: The base file that the recepitent of the the IPS will have
        :param prepatch: The modified file that the IPS will create.
        :param bool legal: The integrity of the IPS 
        :type base: bytes or bytearray
        :type prepatch: bytes or bytearray
        :return: IPS file bytearray
        :rtype: bytearray
        :raises TypeError: if base or prepatch are not bytes or bytearray
        :raises TypeError: if legal is not bool
        :raises ScopeError: if modified file is unsuitabel for IPS generation
        :raises ScopeError: if IPS file bytes or bytearray contains illegal data.
        """

        #legal may be None, in which it will prioritize legality but will contain illegal data should it be needed to generate the file
        #bitsize will be used to dictate if the build is possible (if the file writes beyond said bitsize then whatever it is inteded for is halted)

        if not isinstance(prepatch,(bytes,bytearray)): raise TypeError("Modified file must be bytes or bytearray") #no solution
        if not isinstance(base,(bytes,bytearray)): raise TypeError("Original file must be bytes or bytearray") #no solution
        if not (isinstance(legal,bool) or legal is None): raise TypeError("`Legal` parameter must be Type `bool`")         #no solution
        if isinstance(bitsize,int):
            if bitsize % 8 or not bitsize: raise ScopeError("specified bitsize impossible")
        else: raise TypeError("`bitsize` parameter must be Type `int` or `str`")         #no solution

        fileupperlimit= 16842750 if bitsize >= 32 else (2**bitsize)-1


        if len(prepatch) > fileupperlimit:
            raise ScopeError("Modified file has data beyond target!")   #solution would be to split and append data
        elif len(prepatch) < len(base):
            raise ScopeError("Modified file is smaller than Original!") #solution would be to trim original to size of modded.
        else:
            count = 0;build=b""        
            while count != len(prepatch):
                if count == len(prepatch)-1:
                    build += count.to_bytes(3,"big")+b"\x00\x01"+bytes([prepatch[count]])
                    count += 1
                elif prepatch[count] == base[count] if count < len(base) else prepatch[count] == 0:
                    count += 1
                elif prepatch[count:count + 9] == bytes([prepatch[count]])*9:
                    for readahead in range(min(0xFFFF,len(prepatch)-count)):
                        if prepatch[count+readahead] == base[count+readahead] if count + readahead < len(base) else prepatch[count+readahead] == 0:
                            break 
                        elif prepatch[count:count+readahead] != bytes([prepatch[count]])*readahead:
                            break
                        else:
                            length = readahead+1
                    if length > 8: 
                        build += count.to_bytes(3,"big")+b"\x00\x00"+(length-1).to_bytes(2,"big")+bytes([prepatch[count]])
                        count += length-1
                    else:
                        build += count.to_bytes(3,"big")+length.to_bytes(2,"big")+prepatch[count:count+length]
                        count += length
                else:
                    for readahead in range(min(0xFFFF,len(prepatch)-count)):
                        if prepatch[count+readahead] == base[count+readahead] if count + readahead < len(base) else prepatch[count+readahead:count+readahead+5] == b"\x00"*5:
                            break 
                        else:
                            length = readahead+1 
                    build += count.to_bytes(3,"big")+length.to_bytes(2,"big")+prepatch[count:count+length]
                    count += length
            return b"PATCH"+build+b"EOF" #return bytearray of IPS file

def apply(patch : ips, base : bytes | bytearray) -> bytes:
        """
        Used to apply an IPS file when applying a patch file to a base file. 
        :param base: The base file that the recepitent of the the IPS will have
        :param patch: The IPS file that will create the intended modified result.
        :type base: bytes or bytearray
        :type ips: ips
        :return: modified bytearray
        :rtype: bytearray
        :raises TypeError: if base is not bytes or bytearray
        :raises TypeError: if ips is not of type ips
        """
        try:
            if not isinstance(patch, ips):
                raise TypeError("IPS given is not of type ips!")
            if not isinstance(base,(bytes,bytearray)):
                raise TypeError("base given is not of type bytes or bytearray!")

            build = b""
            for instance in patch.instances:      
                #if len(base) > instance.offset                         #If still overwriting
                #   build+= base[len(build):instance.offset]            #store original data up to this current point
                #else:                                                  #otherwise we are appending new bytes
                #   build+= b"\x00" * (instance.offset - len(build))    #and therefore will append zerodata until the first offset
                #if instance.rle:                                       #if instance is of type rle
                #   build+= instance.data[1]*instance.data[0]           #append bytes of hunk byte with hunk length | byte : length
                build+= (b"\x00" * (instance.offset - len(build)) if len(base) < instance.offset else base[len(build):instance.offset])+(instance.data[1]*instance.data[0] if instance.rle else instance.data)
            return build+ base[len(build):]
        except:
            raise Exception("ips class contains impossible data")
 


  #Code is still faulty
  #True overwrite will require upperlimit to be modified to recurse until final patch can be assured to exist oustide of jurisdicution of overriding patch
