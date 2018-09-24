DROP TABLE IF EXISTS geocodes;

CREATE TABLE geocodes (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  query             TEXT NOT NULL,
  formatted_address TEXT NOT NULL,
  longitude         REAL NOT NULL,
  latitude          REAL NOT NULL
);

CREATE UNIQUE INDEX idx_query
  ON geocodes (query);