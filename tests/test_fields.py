import pytest
import project0
from project0 import project0

url3 = ("file:///project/cs5293sp19-project0/tests/file.pdf")

def test_extract():
    df = project0.extractincidents([url3])
    assert df.size == 216

def test_populate():
    df = project0.extractincidents([url3])
    conn = project0.createdb()
    project0.populatedb(df, conn)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM arrests")
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == '2/9/2019 14:43'
    assert result[1] == '2019-00011057'
    assert result[2] == '2110 24TH AVE NW'
    assert result[3] == 'POSSESSION OF CDS'
    assert result[4] == 'BRADLEY SCOTT BUCHANAN'
    assert result[5] == '2/18/1979'
    assert result[6] == '2524 AGNEW AVE OKLAHOMA CITY OK 73108'
    assert result[7] == 'FDBDC (Jail)'
    assert result[8] == '0945 - Slater;'

def test_random_title():
    df = project0.extractincidents([url3])
    conn = project0.createdb()
    project0.populatedb(df, conn)
    randomrecord = project0.status(conn)

    assert randomrecord is not None
    assert len(randomrecord) == 9
    assert type(randomrecord[0]) == str

