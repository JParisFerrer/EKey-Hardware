#!bin/bash

sqlite3 ekey.db < "CREATE TABLE Keys(Id INT PRIMARY KEY, UUID TEXT, Description TEXT, PublicKey BLOB)"