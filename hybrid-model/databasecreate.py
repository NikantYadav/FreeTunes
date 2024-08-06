import os
import sqlite3


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than PostgreSQL, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'" + s.replace("'", "''") + "'"

def die_with_usage():
    """ HELP MENU """
    print('mxm_dataset_to_db.py')
    print('   by T. Bertin-Mahieux (2011) Columbia University')
    print('      tb2332@columbia.edu')
    print ('This code puts the musiXmatch dataset into an SQLite database.')
    print ('')
    print ('USAGE:')
    print ('  Modify the script to set file paths directly.')
    print ('PARAMS:')
    print ('      <train>  - mXm dataset text train file')
    print ('       <test>  - mXm dataset text test file')
    print ('  <output.db>  - SQLite database to create')
    sys.exit(0)

if __name__ == '__main__':

    # Hardcoded file paths
    trainf = 'train.txt'
    testf = 'test.txt'
    outputf = 'output.db'

    # sanity checks
    if not os.path.isfile(trainf):
        print(f'ERROR: {trainf} does not exist.')
        sys.exit(0)
    if not os.path.isfile(testf):
        print(f'ERROR: {testf} does not exist.')
        sys.exit(0)
    if os.path.exists(outputf):
        print(f'ERROR: {outputf} already exists.')
        sys.exit(0)

    # open output SQLite file
    conn = sqlite3.connect(outputf)

    # create tables -> words and lyrics
    q = "CREATE TABLE words (word TEXT PRIMARY KEY)"
    conn.execute(q)
    q = "CREATE TABLE lyrics (track_id TEXT, mxm_tid INT, word TEXT, count INT, is_test INT, FOREIGN KEY(word) REFERENCES words(word))"
    conn.execute(q)

    # get words, put them in the words table
    with open(trainf, 'r') as f:
        for line in f.readlines():
            if line == '':
                continue
            if line[0] == '%':
                topwords = line.strip()[1:].split(',')
                break

    for w in topwords:
        q = "INSERT INTO words VALUES(" + encode_string(w) + ")"
        conn.execute(q)
    conn.commit()

    # sanity check, make sure the words were entered according
    # to popularity, most popular word should have ROWID 1
    q = "SELECT ROWID, word FROM words ORDER BY ROWID"
    res = conn.execute(q)
    tmpwords = res.fetchall()
    assert len(tmpwords) == len(topwords), 'Number of words issue.'
    for k in range(len(tmpwords)):
        db_word = tmpwords[k][1].strip()
        original_word = topwords[k].strip()
        assert db_word == original_word, f'ROWID issue: DB word "{db_word}" does not match original word "{original_word}".'
    print("'words' table filled, checked.")

    # we put the train data in the dataset
    with open(trainf, 'r') as f:
        cnt_lines = 0
        for line in f.readlines():
            if line == '' or line.strip() == '':
                continue
            if line[0] in ('#', '%'):
                continue
            lineparts = line.strip().split(',')
            tid = lineparts[0]
            mxm_tid = lineparts[1]
            for wordcnt in lineparts[2:]:
                wordid, cnt = wordcnt.split(':')
                q = "INSERT INTO lyrics"
                q += " SELECT '" + tid + "', " + mxm_tid + ", "
                q += " words.word, " + cnt + ", 0"
                q += " FROM words WHERE words.ROWID=" + wordid
                conn.execute(q)
            # verbose
            cnt_lines += 1
            if cnt_lines % 15000 == 0:
                print(f'Done with {cnt_lines} train tracks.')
                conn.commit()
    conn.commit()
    print('Train lyrics added.')

    # we put the test data in the dataset
    # only difference from train: is_test is now 1
    with open(testf, 'r') as f:
        cnt_lines = 0
        for line in f.readlines():
            if line == '' or line.strip() == '':
                continue
            if line[0] in ('#', '%'):
                continue
            lineparts = line.strip().split(',')
            tid = lineparts[0]
            mxm_tid = lineparts[1]
            for wordcnt in lineparts[2:]:
                wordid, cnt = wordcnt.split(':')
                q = "INSERT INTO lyrics"
                q += " SELECT '" + tid + "', " + mxm_tid + ", "
                q += " words.word, " + cnt + ", 1"
                q += " FROM words WHERE words.ROWID=" + wordid
                conn.execute(q)
            # verbose
            cnt_lines += 1
            if cnt_lines % 15000 == 0:
                print(f'Done with {cnt_lines} test tracks.')
                conn.commit()
    conn.commit()
    print('Test lyrics added.')

    # create indices
    conn.execute("CREATE INDEX idx_lyrics1 ON lyrics (track_id)")
    conn.execute("CREATE INDEX idx_lyrics2 ON lyrics (mxm_tid)")
    conn.execute("CREATE INDEX idx_lyrics3 ON lyrics (word)")
    conn.execute("CREATE INDEX idx_lyrics4 ON lyrics (count)")
    conn.execute("CREATE INDEX idx_lyrics5 ON lyrics (is_test)")
    conn.commit()
    print('Indices created.')

    # close output SQLite connection
    conn.close()
