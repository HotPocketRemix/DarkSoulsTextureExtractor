import fnmatch
import hashlib
import os
import sys
import tpf_unpacker
import c_superfasthash as sfh

import logging
log = logging.getLogger(__name__)

SEARCHED_DIRS = [
    "chr", "event", "facegen", "font", "map", "menu", "msg", "mtd", 
    "obj", "other", "param", "paramdef", "parts", "remo", "script", 
    "sfx", "shader", "sound", "unpackDS-BND"
]

MAIN_DIR = "unpack-textures"
MANIFEST_FILE = os.path.join(MAIN_DIR, "unpack-textures-manifest.txt")

TEXTURE_DIR = os.path.join(MAIN_DIR, "textures")
NORMALS_DIR = os.path.join(MAIN_DIR, "normals")
SPECULARS_DIR = os.path.join(MAIN_DIR, "speculars")

def get_checksum(content, blocksize=65536):
    """Computes the SHA256 checksum of content, read in of chunks of blocksize bytes."""
    
    hash_string = hashlib.sha256()
    for block in [content[i:i+blocksize] for i in range(0, len(content), blocksize)]:
        hash_string.update(block)
    return hash_string.hexdigest()

def yes_no(answer):
    """Prompts the user answer and returns True / False for a Yes / No 
     response, respectively.
    """
    
    yes = set(['yes','y', 'ye'])
    no = set(['no','n'])
     
    while True:
        choice = raw_input(answer).lower()
        if choice in yes:
            log.info("User chose Y for question '" + answer + "'.")
            return True
        elif choice in no:
            log.info("User chose N for question '" + answer + "'.")
            return False
        else:
            print "Unknown response. Respond [Y]es / [N]o.  "
            
def create_extract_dirs():
    """Creates directories to store unpacked files."""
    
    for d in [TEXTURE_DIR, NORMALS_DIR, SPECULARS_DIR]:
        try: 
            os.makedirs(d)
        except OSError:
            if not os.path.isdir(d):
                raise
                
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
            
def wait_before_exit(exit_code):
    """Displays a message before exiting with exit code exit_code"""
    
    raw_input("Exiting. Press ENTER to continue... ")
    log.info("Exited with exit code " + str(exit_code)) 
    sys.exit(exit_code)
    
def attempt_unpack():
    """Searches for .tpf files inside the known DATA subdirectories
    created by UDSFM and extracts them. Also builds a manifest of
    the extracted files.
    """
    
    log.info("Beginning search.")
    print "Searching for .tpf files..."
    
    matches = []
    for unpack_dir in SEARCHED_DIRS:
        print "\r - Searching for .tpf files in " + str(unpack_dir) + "          ",
        sys.stdout.flush()
        for root, dirnames, filenames in os.walk(unpack_dir):
            for filename in fnmatch.filter(filenames, '*.tpf'):
                matches.append(os.path.join(root, filename))
    print "\rSearching complete. Found " + str(len(matches)) + " .tpf files.         "
    log.info("Search complete.")
    
    log.info("Write DSFix names check")
    use_dsfix_names = yes_no("Write extracted files using DSFix hashed names instead of true names?\n" +
        "(DSFix names are useful for texture replacement.) [Y]es / [N]o  ")
    
    print "Extracting .tpf files..."
    
    filename_dict = {}
    dsfix_dict = {}
    
    total_files = len(matches)
    msg_len = 0
    
    manifest_string = ""
    
    for count, filepath in enumerate(matches):
        (_, tpf_filename) = os.path.split(filepath)
        
        print "\r" + " " * msg_len,
        msg = "\r - (" + str(count+1) + "/" + str(total_files) + ") Unpacking TPF file " + str(tpf_filename)
        msg_len = len(msg)
        print msg,
        sys.stdout.flush()
        
        log.info("Reading file '" + str(filepath) + "'")
        f = open(filepath, "rb")
        content = f.read()
        f.close()
        
        manifest_string += filepath + "\n"
        
        if tpf_unpacker.appears_tpf(content):
            log.debug("File appears to be truly TPF")
            extracted_files = tpf_unpacker.unpack_tpf(content)
            log.info("File contains " + str(len(extracted_files)) + " constituent files.")
            for (ext_filename, ext_filedata) in extracted_files:
                filehash = get_checksum(ext_filedata)
                log.info("Exporting subfile " + ext_filename)
                log.debug("Subfile has hash '" + str(filehash) + "'")
                
                manifest_string += "  " + ext_filename
                
                ext_filename = '-'.join(os.path.normpath(filepath).lstrip(os.path.sep).split(os.path.sep) + [ext_filename])
                
                # Check for distinct files with the same true file name.
                if ext_filename in filename_dict:
                    if filehash not in filename_dict[ext_filename]:
                        filename_dict[ext_filename].add(filehash)
                        log.debug("True name collision for '" + ext_filename + "': " + str(filename_dict[ext_filename]))
                else:
                    filename_dict[ext_filename] = set([filehash])

                output_dir = TEXTURE_DIR
                if ext_filename[-6:] == "_n.dds":
                    log.debug("File appears to be _n")
                    output_dir = NORMALS_DIR
                elif ext_filename[-6:] == "_s.dds":
                    log.debug("File appears to be _s")
                    output_dir = SPECULARS_DIR
                    
                out_filename = ext_filename
                if use_dsfix_names:
                    out_filename = ("%08x" % sfh.c_superfasthash(ext_filedata)) + ".dds"
                    log.info("Computed DSFix name as " + out_filename)
                    
                    manifest_string += " --> " + out_filename
                    
                    # Check for distinct files with the same superfasthash.
                    #  That is, distinct files with the same DSFix name.
                    if out_filename in dsfix_dict:
                        if filehash not in dsfix_dict[out_filename]:
                            dsfix_dict[out_filename].add(filehash)
                            log.debug("DSFix name collision: " + str(dsfix_dict[ext_filename]))
                    else:
                        dsfix_dict[out_filename] = set([filehash])
                
                manifest_string += "\n"
                        
                output_filepath = os.path.abspath(os.path.join(os.getcwd(), output_dir, out_filename))
                f = create_file(output_filepath)
                f.write(ext_filedata)
                f.flush()
                f.close()
        else:
            log.debug("File appears to not be truly TPF")
    print "\r - (" + str(count+1) + "/" + str(total_files) + ") Unpacking TPF files... Done. "
    
    log.info("Writing manifest.")
    print "Writing manifest file... ",
    with open(MANIFEST_FILE, "w") as g:
        g.write(manifest_string)
        g.close()
    print "Done."
    
    print "Textures extraction complete!"
    wait_before_exit(0)

            
            
