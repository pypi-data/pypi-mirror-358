import sqlite3

def create_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Experiments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Experiments
        (
        run_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        experiment varchar(128) NOT NULL,
        config varchar(128),
        config_hash varchar(64),
        cli varchar(512),
        command varchar(256),
        comment TEXT,
        start DATETIME NOT NULL,
        status TEXT CHECK (status IN ('running', 'finished', 'failed')) DEFAULT 'running',
        commit_hash varchar(40),
        diff TEXT,
        hidden INTEGER NOT NULL DEFAULT 0
        );
    """)

    # Create Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Results
        (
            id_ INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            metric varchar(128) NOT NULL,
            value NOT NULL,
            is_hparam INTEGER DEFAULT 0,
            FOREIGN KEY (run_id) REFERENCES Experiments(run_id)
        );
    """)

    # Create Logs table for scalar values
    # Wall time is in seconds
    # We must allow NULL values for the value column when the value is NaN
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Logs
    (
        id_ INTEGER PRIMARY KEY AUTOINCREMENT,
       run_id INTEGER NOT NULL,
       epoch INTEGER,
       step INTEGER NOT NULL,
       split varchar (128) NOT NULL,
       label varchar(128) NOT NULL,
       value REAL,
       wall_time REAL NOT NULL,
       run_rep INTEGER NOT NULL,
       FOREIGN KEY(run_id) REFERENCES Experiments(run_id)
    );
    """)

    # Create an Image table to store images
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Images
    (
        id_ INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        step INTEGER NOT NULL,
        epoch INTEGER,
        run_rep INTEGER NOT NULL,
        img_type varchar(64) NOT NULL, -- IMAGE or PLOT
        split varchar(128),
        image BLOB NOT NULL,
        FOREIGN KEY(run_id) REFERENCES Experiments(run_id)
    );
    """)
    # Create a table to store text data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Fragments
    (
        id_ INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        step INTEGER NOT NULL,
        epoch INTEGER,
        run_rep INTEGER NOT NULL,
        fragment_type varchar(64) NOT NULL, -- RAW or HTML
        split varchar(128),
        fragment text NOT NULL,
        FOREIGN KEY(run_id) REFERENCES Experiments(run_id)
    );
    """)
    # Display Table
    # This table stores every column of Results, their order and whether they displayed or not
    # If order is Null, it means that the column is not displayed
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ResultDisplay
    (
        Name varchar(128) NOT NULL, display_order INTEGER, 
        alias varchar(128) NOT NULL,
        PRIMARY KEY(Name)
    );
    """)  # We can put order to unique, because each NULL value will be unique

    # Add default columns
    cursor.execute("""
    INSERT
    OR IGNORE INTO ResultDisplay (Name, display_order, alias) VALUES
    ('run_id', 0, 'Run ID'),
    ('experiment', 1, 'Experiment'),
    ('config', 2, 'Config'),
    ('config_hash', NULL, 'Config Hash'),
    ('cli', NULL, 'Cli'),
    ('command', NULL, 'Command'),
    ('comment', 4, 'Comment'),
    ('start', NULL, 'Start'),
    ('status', NULL, 'Status'),
    ('commit_hash', NULL, 'Commit'),
    ('diff', NULL, 'Diff'),
    ('hidden', NULL, 'Hidden');
    """)

    # Create a trigger to add a new metric to the display table
    cursor.execute("""
                   CREATE TRIGGER IF NOT EXISTS after_result_insert
    AFTER INSERT ON Results
                   BEGIN
        -- Insert a row into ResultDisplay if the Name does not exist
        INSERT
                   OR IGNORE INTO ResultDisplay (Name, display_order, alias)
                   SELECT NEW.metric,
                          COALESCE(MAX(display_order), 0) + 1,
                          NEW.metric
                   FROM ResultDisplay;
                   END;
                   """)
    # Create index for speed
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_config_hash ON Experiments(experiment, config, config_hash, cli, comment);")
    conn.commit()
    conn.close()