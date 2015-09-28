#!/bin/bash

echo "CREATE TABLE Keys(Id INT PRIMARY KEY, UUID TEXT, Description TEXT, PublicKey BLOB);" | sqlite3 ekey.db