import os
from os import path
from fnmatch import fnmatch
import shutil

def _treelist(root, child, exclude, include):  
    """
    Recursive function that does the actual work of `treelist`.
    """
    src_dir = root
    if child:
        src_dir = path.join(src_dir, child)
        
    files = []
    for filename in os.listdir(src_dir):
        part = filename
        if child:
            part = path.join(child, filename)
            
        src = path.join(root, part)

        if exclude and any(fnmatch(filename, p) for p in exclude):
            continue
        elif not path.isdir(src) and include and not any(fnmatch(filename, p) for p in include):
            continue

        if path.isdir(src):
            files.extend(_treelist(root, part, exclude=exclude, include=include))
        else:
            files.append(part)
    
    return files

def treelist(root, exclude=None, include=None):
    """
    Returns a list of child file paths relative to `root`.

    :param exclude: Exclude files matching this list of glob patterns
    :param include: Include files only if the match this list of glob patterns
    """    
    return _treelist(root, child=None, exclude=exclude, include=include)    

class SyncListener(object):
    def exists(self, srcroot, srcname, dstroot, dstname):
        """
        Called when destination path already exists.

        Retun True to overwrite, False to skip.
        """
        return True

    def copy(self, srcroot, srcname, dstroot, dstname):
        """
        Called when destination path does not already exists.

        Retun True to write, False to skip.
        """        
        return True

    def copied(self, srcroot, srcname, dstroot, dstname):
        """
        Called for each file that is copied
        """        
        pass

    def destpath(self, srcroot, srcname, dstroot, dstname):
        """
        Called for each file before each sync operation. Here you can rewrite
        the destination name if need be.        

        Retuns a tuple of dstroot, dstname
        """        
        return dstroot, dstname

_default_listener = SyncListener()

def synctree(src_dir, dst_dir, exclude=None, include=None, listener=_default_listener):
    if not path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    files_to_copy = treelist(src_dir, exclude=exclude, include=include)
    for filename in files_to_copy:        
        src = path.join(src_dir, filename)
        dst_dir, dst_file = listener.destpath(src_dir, filename, dst_dir, filename)
        dst = path.join(dst_dir, dst_file)

        copy = False
        if path.exists(dst):
            copy = listener.exists(src_dir, filename, dst_dir, dst_file)
        else:    
            copy = listener.copy(src_dir, filename, dst_dir, dst_file)

        if copy:
            if not path.exists(path.dirname(dst)):
                os.makedirs(path.dirname(dst))

            shutil.copy2(src, dst)
            listener.copied(src_dir, filename, dst_dir, dst_file)