
import argparse
import hashlib
import shutil
from pathlib import Path

def _all_files_in_dir(d:Path) -> list[str]:
    """
    Returns all files in the given directory.
    
    >>> d = Path("/tmp/test__1234")
    >>> d.mkdir(exist_ok=False)
    >>> fle = d / "test.txt"
    >>> fle.write_text("test")
    4
    >>> [fle.name for fle in _all_files_in_dir(d)]
    ['test.txt']
    >>> sd = d / "a_sub_dir"
    >>> sd.mkdir(exist_ok=False)
    >>> fle = sd / "test2.txt"
    >>> fle.touch()
    >>> sorted(fle.name for fle in _all_files_in_dir(d))
    ['test.txt', 'test2.txt']
    >>> shutil.rmtree(d)
    """
    visited = set()
    left = list(d.iterdir())
    while left:
        fle = left.pop()
        sfle = str(fle.resolve())
        if sfle in visited:
            continue
        else:
            visited.add(sfle)

        if fle.is_dir():
            left += list(fle.iterdir())
        else:
            yield fle

def dir_contents(d:Path, hash_fun ) -> list[tuple[Path,str]]:
    fles = _all_files_in_dir(d)
    tups = [(fle, hash_fun(fle)) for fle in fles]
    return tups

def covered(src:Path, covered_by:Path, hash_fun):
    """
    Returns empty list
    if no difference, otherwise a list
    of all files within directory `src`
    that are missing within directory `covered_by`
    """
    contents_src = dir_contents(src,hash_fun)
    contents_cov = dir_contents(covered_by,hash_fun)
    hashes_cov = {hsh for _,hsh in contents_cov}
    missings = []
    for fle_src,hash_src in contents_src:
        if hash_src not in hashes_cov:
            missings.append((fle_src,hash_src))
    return missings



def sha1_file_hash(fle:Path):
    BUF_SIZE = 65536  
    sha1 = hashlib.sha1()
    with open(fle, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return "{}".format(sha1.hexdigest())


def main():
    parser = argparse.ArgumentParser(
        prog="covered",
        description="""
        Determines whether src is covered by cov, aka
        whether all files within directory `src`
        are also present within `cov`.
        The sha1 hash is used to compare files for equality.

        When all files in src are covered by cov,
        no output is produced.
        Otherwise, all files present within src but
        missing in cov are printed line by line
        in the format
            absolute-path    sha1-check-sum
        e.g. 
            /home/user/src/some-file    84df1fe2495
        """,

    )

    parser.add_argument("--src",required=True,)
    parser.add_argument("--cov",required=True)
    hash_fun = sha1_file_hash
    args = parser.parse_args()
    sep = '\t'
    missings = covered(src=Path(args.src),
    covered_by=Path(args.cov),hash_fun=hash_fun)
    for missing in missings:
        print(f"{missing[0]}{sep}{missing[1]}")


if __name__ == "__main__":
    main()




            

