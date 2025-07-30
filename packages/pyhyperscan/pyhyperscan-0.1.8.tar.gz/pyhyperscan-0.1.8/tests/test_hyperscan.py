import pyhyperscan

def test_compile_pattern():
    pattern = b"abc.*def"
    db = pyhyperscan.compile_pattern(pattern)
    assert db != 0
    pyhyperscan.free_database(db)

def test_scan_data():
    pattern = b"abc.*def"
    db = pyhyperscan.compile_pattern(pattern)
    data = b"abcdefghijklmnopqrstuvwxyz"
    pyhyperscan.scan_data(db, data)
    pyhyperscan.free_database(db)