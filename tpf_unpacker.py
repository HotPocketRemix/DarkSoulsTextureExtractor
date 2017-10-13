import struct
import sys
import os

def consume_byte(content, offset, byte, length=1):
    """Consume length bytes from content, starting at offset. If they
     are not all byte, raises a ValueError.
    """
    
    for i in xrange(0, length-1):
        if content[offset + i] != byte:
            raise ValueError("Expected byte '" + byte.encode("hex") + "' at offset " +\
                    hex(offset + i) + " but received byte '" +\
                    content[offset + i].encode("hex") + "'.")
    return offset + length
    
def extract_strz(content, offset):
    extracted = ''
    while content[offset] != '\x00':
        extracted = extracted + content[offset]
        offset += 1
    return extracted
    
def create_file(filename):
    """Attempts to create filename."""
    
    path = os.path.dirname(filename)
    
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
    
    f = open(filename, "wb+")
    return f
    
def appears_tpf(content):
    """Checks if the magic bytes at the start of content indicate that it
    is a TPF file.
    """
    return content[0:4] == "TPF\x00"
    
def unpack_tpf(content):
    """Unpacks the .dds files from a .tpf texture pack file."""
    
    master_offset = 0
    master_offset = consume_byte(content, master_offset, 'T', 1)
    master_offset = consume_byte(content, master_offset, 'P', 1)
    master_offset = consume_byte(content, master_offset, 'F', 1)
    master_offset = consume_byte(content, master_offset, '\x00', 1)
    
    (packed_data_size, num_of_records) = struct.unpack_from("<II", content, offset=master_offset)
    master_offset += struct.calcsize("<II")
    
    # Check for correct DS1 version number.
    master_offset = consume_byte(content, master_offset, '\x00', 1)
    master_offset = consume_byte(content, master_offset, '\x03', 1)
    master_offset = consume_byte(content, master_offset, '\x02', 1)
    master_offset = consume_byte(content, master_offset, '\x00', 1)
    
    return_namedata_list = []
    for _ in xrange(num_of_records):
        (filedata_offset, filedata_size, filedata_flags1, filename_offset, 
            filedata_flags2) = struct.unpack_from("<IIIII", content, offset=master_offset)
        master_offset += struct.calcsize("<IIIII")
        
        filename = extract_strz(content, filename_offset) + ".dds"
        filedata = content[filedata_offset:filedata_offset + filedata_size]
        
        return_namedata_list.append((filename, filedata))
    return return_namedata_list
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: " + str(sys.argv[0]) + " <TPF File>"
    else:
        (base, _) = os.path.split(os.path.abspath(sys.argv[1]))
        with open(sys.argv[1], 'rb') as f:
            file_content = f.read()
            file_list = unpack_tpf(file_content)
        print "  - Created file list:"
        for (filename, filedata) in file_list:
            g = create_file(os.path.normpath(os.path.join(base, "./" + filename)))
            g.write(filedata)
            g.flush()
            g.close()
            print "  - " + str(filename)
    
    
    
    
    
    
    
