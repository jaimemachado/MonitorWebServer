#!/usr/bin/env python

# sample usage: checksites.py config file

import pickle, os, sys, logging
from httplib import HTTPConnection, socket
from smtplib import SMTP
from attrdict import AttrDict
import ConfigParser
import json
from urlparse import urlparse
import urllib2

class MonitorServer(object):
    def email_alert(self, message, status):
        fromaddr = self.Email.fromaddr
        toaddrs = self.Email.toaddr

        server = SMTP(self.Email.smtpserver)
        server.starttls()
        server.login(self.Email.loginsmtpserver, self.Email.passwordsmtpserver)
        server.sendmail(fromaddr, toaddrs, 'Subject: %s\r\n%s' % (status, message))
        server.quit()


    def get_site_status(self, url):
        response = self.get_response(url)
        try:
            if getattr(response, 'code') == 200:
                return 'up'
        except AttributeError:
            pass
        return 'down'


    def get_response(self, url):
        '''Return response object from URL'''
        try:
            result = urllib2.urlopen(url.geturl());
            return result;
        except socket.error:
            return None
        except:
            logging.error('Bad URL:', url)
            exit(1)


    def get_headers(self, url):
        '''Gets all headers from URL request and returns'''
        response = self.get_response(url)
        try:
            return getattr(response, 'headers')
        except AttributeError:
            return 'Headers unavailable'


    def compare_site_status(self, prev_results):
        '''Report changed status based on previous results'''

        def is_status_changed(url):
            status = self.get_site_status(url)
            friendly_status = '%s is %s' % (url.geturl(), status)
            print friendly_status
            if url.geturl() in prev_results and prev_results[url.geturl()] != status:
                logging.warning(status)
                # Email status messages
                if(self.enableEmail):
                    self.email_alert(str(self.get_headers(url)), friendly_status)
            prev_results[url.geturl()] = status

        return is_status_changed


    def is_internet_reachable(self):
        '''Checks Google then Yahoo just in case one is down'''
        for url in self.checkstatusurls:
            if self.get_site_status(url) == "up":
                return True
        return False


    def load_old_results(self, file_path):
        '''Attempts to load most recent results'''
        pickledata = {}
        if os.path.isfile(file_path):
            picklefile = open(file_path, 'rb')
            pickledata = pickle.load(picklefile)
            picklefile.close()
        return pickledata


    def store_results(self, file_path, data):
        '''Pickles results to compare on next run'''
        output = open(file_path, 'wb')
        pickle.dump(data, output)
        output.close()


    def main(self):
        # Setup logging to store time
        logging.basicConfig(level=logging.WARNING, filename='checksites.log',
                            format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        # Load previous data
        pickle_file = 'data.pkl'
        pickledata = self.load_old_results(pickle_file)

        # Check sites only if Internet is_available
        if self.is_internet_reachable():
            status_checker = self.compare_site_status(pickledata)
            map(status_checker, self.urls)
        else:
            logging.error('Either the world ended or we are not connected to the net.')

        # Store results in pickle file
        self.store_results(pickle_file, pickledata)

    def parseConfig(self):
        #Server
        tempUrls = json.loads(self.config.get("Servers", "urls"));
        self.urls = []
        for url in tempUrls:
            self.urls.append(urlparse(url.encode('ascii', 'ignore')));


        #Config
        self.enableEmail = self.config.getboolean("Config", "enableEmailSend");
        self.Email = AttrDict();
        self.Email.fromaddr = self.config.get("Email", "fromaddr");
        self.Email.toaddr = self.config.get("Email", "toaddr");
        self.Email.smtpserver = self.config.get("Email", "smtpserver");
        self.Email.loginsmtpserver = self.config.get("Email", "loginsmtpserver");
        self.Email.passwordsmtpserver = self.config.get("Email", "passwordsmtpserver");

        #Internet
        tempcheckurls = json.loads(self.config.get("Internet", "checkstatusurls"));
        self.checkstatusurls = []
        for url in tempcheckurls:
            self.checkstatusurls.append(urlparse(url.encode('ascii', 'ignore')));


    def __init__(self, config):
        self.config = config
        self.parseConfig();

if __name__ == '__main__':
    configFile = sys.argv[1];
    # First arg is script name, skip it
    config = ConfigParser.ConfigParser(allow_no_value=True);
    config.read([configFile])
    monitorServer = MonitorServer(config);
    monitorServer.main()