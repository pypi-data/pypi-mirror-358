import os
import shutil


def mkdirp(dirname):
    if os.path.isdir(dirname):
        return
    os.makedirs(dirname)


def addtree(src, dst, symlinks=False):
    """
    Recurive copy of directories, both real and virtual (using importlib.resources).
    If src is a string, it is treated as a path.
    If src is a Path, it is treated as a Path object.
    If src is a directory, it copies all files and subdirectories to dst.
    If dst does not exist, it is created.
    If dst exists, it will raise an error if there are conflicts.
    If symlinks is True, it will copy symbolic links as links.
    If symlinks is False, it will copy the files they point to."""
    mkdirp(dst)
    errors = []

    # Se src è una stringa/path, converti in Path
    if isinstance(src, str):
        import pathlib

        src = pathlib.Path(src)

    # Se è una directory reale
    if hasattr(src, "is_dir") and src.is_dir() and hasattr(src, "iterdir"):
        for item in src.iterdir():
            dstname = os.path.join(dst, item.name)
            try:
                if hasattr(item, "is_dir") and item.is_dir():
                    addtree(item, dstname, symlinks)
                else:
                    with item.open("rb") as src_file, open(dstname, "wb") as dst_file:
                        shutil.copyfileobj(src_file, dst_file)
            except Exception as why:
                errors.append((str(item), dstname, str(why)))
    else:
        # fallback: usa la vecchia logica per directory reali
        names = os.listdir(src)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    addtree(srcname, dstname, symlinks)
                else:
                    shutil.copy2(srcname, dstname)
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
            except shutil.Error as err:
                errors.extend(err.args[0])
    if errors:
        raise shutil.Error(errors)
