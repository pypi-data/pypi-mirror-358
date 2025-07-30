import time
import requests
import threading
import queue
import signal
import fnmatch
import os
import csv
from rich.console import Console
from cryptography.x509.oid import NameOID


from phisher.config import *
from phisher.decoder import extract_cert
from phisher.telegram_notifier import notify_in_telegram



console = Console() 
print_lock = threading.Lock()


class CTMonitor:
    def __init__(self, keywords_file, output_file, format, keywords=None, notify=None, log=False, log_list_url='https://www.gstatic.com/ct/log_list/v3/log_list.json'):
        self.keywords_file = keywords_file
        self.keywords_list = keywords
        self.log = log
        self.output_file = output_file
        self.output_format = format
        self.log_list_url = log_list_url
        self.urls = self._get_urls()
        self.q = queue.Queue()
        self.last_tree_sizes = {}
        self.producer_thread = threading.Thread(target=self._producer)
        self.consumer_threads = [threading.Thread(target=self._consumer) for _ in range(2)]
        self.keywords = self._read_keywords()
        self.notify = notify

    def _write_csv(self, cn, cert):
        """ Writer to csv file """

        fields = ["Subject", "Issuer", "Serial No", "Version", "Not Before (UTC)", "Not After (UTC)"]
        data = {
            "Subject" : cert.subject.rfc4514_string(),
            "Issuer":cert.issuer.rfc4514_string(),
            "Serial No":cert.serial_number,
            "Version":cert.version.name, 
            "Not Before (UTC)":cert.not_valid_before_utc, 
            "Not After (UTC)":cert.not_valid_after_utc
        }
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writerow(data)

    def _write_txt(self, cn, cert):
        """ Writer to txt file """

        info = (
            f"[*] Found domain: {cn}\n"
            f"Subject:     {cert.subject.rfc4514_string()}\n"
            f"Issuer:      {cert.issuer.rfc4514_string()}\n"
            f"Serial No.:  {cert.serial_number}\n"
            f"Version:     {cert.version.name}\n"
            f"Validity:\n"
            f"  Not Before (UTC): {cert.not_valid_before_utc}\n"
            f"  Not After  (UTC): {cert.not_valid_after_utc}"
        )
        with open(self.output_file, 'a') as f:
            print(info, file=f)

    def _write_results(self, cn, cert):
        """ Logs certificate details to a file """
        
        if self.output_format == 'txt':
            self._write_txt(cn, cert)
        
        if self.output_format == 'csv':
            self._write_csv(cn, cert)
    
    def _read_keywords(self):
        """ Read keywords """
        k = []
        if os.path.exists(self.keywords_file):
            print("File exists !!!")
            with open(self.keywords_file) as f:
                raw = [line.strip() for line in f if line.strip()]
            k.extend([f"*{kw.lower()}*" for kw in raw])
        if self.keywords_list:
            k.extend([ f"*{k}*" for k in self.keywords_list ])
        
        return k if k else ["*"]
                
        

    def _safe_print(self, *args, **kwargs):
        """ Function to print on time while multiple threads are used """
        
        with print_lock:
            console.print(*args, **kwargs, highlight=False)
    def _get_urls(self):
        """ Gets the list of current CT logs urls """

        resp = requests.get(self.log_list_url)
        data = resp.json()

        result = []
        for operator in data.get('operators', []):
            name = operator.get('name')
            logs = operator.get('logs', [])
            if not name or not logs:
                continue

            first_url = logs[0].get('url', '')
            if not first_url or 'example.com' in first_url:
                continue

            result.append(first_url)
        return result
    
    def _get_size(self, url):
        """ Get the current CT logs tree size """
        
        r = requests.get(f"{url}ct/v1/get-sth")
        return r.json()['tree_size']

    def _get_entries(self, url, start, end):
        """ Get the CT log entries for given url. start and end defien the startind and ending index """
        
        params = {'start': start, 'end': end}
        r = requests.get(f"{url}ct/v1/get-entries", params=params)
        if r.status_code == 200:
            return r.json()
        
    def _poll_once(self):
        """ Functions to read up to BATCH_SIZE many CT logs entries """

        for url in self.urls:
            size = self._get_size(url)
            prev = self.last_tree_sizes.get(url, size-1)

            if size > prev:
                for start in range(prev, size, BATCH_SIZE):
                    end = min(start + BATCH_SIZE - 1, size)
                    entries = self._get_entries(url, start, end).get('entries', [])
                    if not entries:
                        continue
                    else:
                        for e in entries:
                            self.q.put(e)
                    time.sleep(MIN_INTERVAL)
                self.last_tree_sizes[url] = size
            time.sleep(MIN_INTERVAL)
    
    def _producer(self):
        """ Producer function for multithreading """

        while True:
            self._poll_once()
    
    def _consumer(self):
        """ Consumer function for multithreading """

        while True:
            batch = []
            for _ in range(BATCH_SIZE_CONSUMER):
                try:
                    item = self.q.get(timeout=1)
                except queue.Empty:
                    break
                batch.append(item)

            if not batch:
                continue 

            for ct_entry in batch:
                try:
                    leaf_input = ct_entry["leaf_input"]
                    extra_data = ct_entry["extra_data"]
                    self._check_ct_entry(leaf_input, extra_data)
                except Exception as e:
                    self._safe_print("Error occured:", e)

            for _ in batch:
                self.q.task_done()
    def _contains_keywords(self, domain):
        """ Checks if domain contains the keywords """

        for pat in self.keywords:
            if fnmatch.fnmatchcase(domain.lower(), pat):
                return True
        return False

    def _check_ct_entry(self, leaf_input, extra_data):
        cert = extract_cert(leaf_input, extra_data)
        if not cert:
            return
        cn_attrs = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        common_names = [attr.value for attr in cn_attrs]

        for cn in common_names:
            if self._contains_keywords(cn):
                self._safe_print(f"[#2596be][*] Found domain:[/#2596be] {cn}")
                if self.notify:
                    notify_in_telegram(f"Found domain {cn}", self.notify[0], self.notify[1])
                if self.log:
                    self._write_results(cn, cert)             
                
    def start(self):
        t_prod = threading.Thread(target=self._producer, args=())
        t = threading.Thread(target=self._consumer, args=())
            
        t_prod.start()
        t.start()
            
        signal.signal(signal.SIGINT, signal.SIG_DFL) 

        t_prod.join()  
        t.join()
        self.q.join()  


    