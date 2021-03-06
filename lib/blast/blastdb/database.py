#!/usr/bin/env python3
#  blastdb.py
#
#  Author: Jan Piotr Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0.0

import os
import sys
import gzip
import subprocess
import tarfile
import urllib.request
import time

from . import blastdbcmd


class BlastDatabase:
    def __init__(self, cmd=None, dbdir=None, name=None, typ=None, verbose=False):
        """
        Initialize the blast database
        :param cmd: an array of the commands
        :param dbdir: the directory that holds the database
        :param name: the name of the database in that directory
        :param typ: the type (nucl or protein)
        :param verbose: make additional output
        """
        self.title = name
        self.dbdir = dbdir
        self.typ = typ
        self.dbtool = blastdbcmd.Blastdbcmd()
        self.path = os.path.join(self.dbdir, self.title)
        self.cmd = [cmd]
        self.verbose = verbose

    def check_database(self):
        """
        Check a database for the files if it has compiled.
        :param db: The database object
        :return: True if all files are present. False if not
        """

        extensions = []
        if 'nucl' == self.typ:
            extensions = ["nhd", "nhi", "nhr", "nin", "nog", "nsd", "nsi", "nsq"]
        elif 'prot' == self.typ:
            extensions = ["phd", "phi", "phr", "pin", "pog", "psd", "psi", "psq"]
        elif 'rps' == self.typ:
            extensions = ["aux", "freq", "loo", "phr", "pin", "psd", "psi", "psq", "rps"]
        else:
            sys.stderr.write("Can't determine what the database type is for {}\n".format(self.typ))
            sys.exit(-1)

        dbcomplete = True
        for extn in extensions:
            if not os.path.exists(os.path.join(self.dbdir, "{}.{}".format(self.title, extn))):
                dbcomplete = False
        return dbcomplete

    def make_db(self, fil=None):
        # test and see if the database has already been formatted

        if not self.check_database():
            sys.stderr.write("The database {} is complete. Not reformatting\n".format(self.title))
            return

        cmd = self.cmd + ['-dbtype', self.typ, '-in', fil, '-out', os.path.join(self.dbdir, self.title), '-title',
                          self.title]
        print(cmd)
        subprocess.run(cmd)

    def make_db_stdin(self, stdout):
        cmd = self.cmd + ['-dbtype', self.typ, '-out', os.path.join(self.dbdir, self.title), '-title', self.title]
        print(cmd)
        # p = subprocess.Popen(cmd, stdin=stdout)
        p = subprocess.Popen(cmd, stdin=stdout)
        while p.poll() == None:
            time.sleep(2)

        if p.returncode != 0:
            print("Creating db {} failed. Aborting.".format(self.title))
            raise RuntimeError()

    def setup(self, src):
        if os.path.exists(self.dbdir):
            if not self.dbtool.exists(os.path.join(self.dbdir, self.title)):
                print("No Blast DB {0}".format(os.path.join(self.dbdir, self.title), file=sys.stderr))
                if not os.path.exists(os.path.join(os.path.join(self.dbdir, self.title))):
                    self.fetch_db(src, self.title)
                print("\tfound local data at {0}. Creating database".format(os.path.join(self.dbdir, self.title),
                                                                            file=sys.stderr))
                dbdir_title = os.path.join(self.dbdir, self.title)
                self.make_db(dbdir_title)
            else:
                print("\tfound local Blast DB {0}".format(os.path.join(self.dbdir, self.title), file=sys.stderr))
        else:
            os.mkdir(self.dbdir)
            self.fetch_db(src, self.title)
            self.make_db(src)
        sys.stderr.write("RAE EXitering setup\n")

    def fetch_db(self, src, title):
        if src == 'Cdd':
            return
        print("Fetching database {} from {}".format(title, src))
        db = open(self.path, 'w')
        for i in src:
            if not i.startswith('http') and not i.startswith('ftp'):
                sys.stderr.write("{} does not appear to be a URL from to which to fetch the file\n".format(i))
                continue
            dbgz = open('dbgz', 'wb')
            response = urllib.request.urlopen(i)
            dbgz.write(response.read())
            dbgz.close()
            f = gzip.open('dbgz', 'rb')
            db.write(f.read().decode())
            os.unlink('dbgz')
        db.close()
        # print("DB fetch placeholder for {0} to make db {1}".format(src, title))



