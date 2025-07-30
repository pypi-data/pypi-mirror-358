import uuid
import threading
import signal
import logging
import sys


_TEST_SERVER_ENABLED = 'TEST_SERVER_ENABLED'
_TEST_SERVER_DOMAIN = 'TEST_SERVER_DOMAIN'
_PROJECT_ID = 'PROJECT_ID'
_FEATURE_ID = 'FEATURE_ID'
_TESTCASE_ID = 'TESTCASE_ID'
_TESTCASE_STAGE_ID = 'TESTCASE_STAGE_ID'
_AUTO_INCREMENT = 'AUTO_INCREMENT'
_JOB_ID = 'JOB_ID'

class LocalVars:
    def __init__(self):
        self.local = threading.local()    
        setattr(self.local, _JOB_ID, uuid.uuid4().hex)
        setattr(self.local, _PROJECT_ID, 'scc-fmon')
        setattr(self.local, _TEST_SERVER_ENABLED, False)
        setattr(self.local, _TEST_SERVER_DOMAIN, '')
        setattr(self.local, _FEATURE_ID, '')
        setattr(self.local, _TESTCASE_ID, '')
        setattr(self.local, _TESTCASE_STAGE_ID, '')
        setattr(self.local, _AUTO_INCREMENT, 0)
    
    @property
    def jid(self) -> str:
        return self.get(_JOB_ID)

    def set(self, key, value):
        setattr(self.local, key, value)

    def get(self, key):
        return getattr(self.local, key)
    
    def _next_auto_increment(self):
        current = self.get(_AUTO_INCREMENT) or 0
        if not isinstance(current, int):
            current = 0

        new = current + 1
        self.set(_AUTO_INCREMENT, new)
        return new
    
    @property
    def project_id(self) -> str:
        return self.get(_PROJECT_ID)
    
    @property
    def feature_id(self) -> str:
        return self.get(_FEATURE_ID)
    
    def set_feature_id(self, value: str):
        self.set(_FEATURE_ID, value)
    
    @property
    def testcase_id(self) -> str:
        return self.get(_TESTCASE_ID)
    
    @property
    def testcase_stage_id(self):
        val = self.get(_TESTCASE_STAGE_ID)
        if val is None or val == '':
            return str(self._next_auto_increment())
        return val
    
    def set_testcase_stage_id(self, value: str):
        self.set(_TESTCASE_STAGE_ID, value)

    @property
    def test_server_domain(self) -> str:
        return self.get(_TEST_SERVER_DOMAIN)
    
    def set_test_server_domain(self, value: str):
        self.set(_TEST_SERVER_DOMAIN, value)

    @property
    def test_server_enabled(self) -> bool:
        return self.get(_TEST_SERVER_ENABLED)
    
    def set_test_server_enabled(self, value: bool):
        self.set(_TEST_SERVER_ENABLED, value)

local_vars = LocalVars()


def set_plugin_id(plugin_id: str):
    local_vars.set_feature_id(plugin_id)
    logger = logging.getLogger(plugin_id)

    def signal_handler(signum, frame):
        try:
            signal_name = signal.Signals(signum).name  # Ví dụ: SIGTERM
            logger.error(f"Received signal: {signal_name} ({signum}) — exiting")
        except: 
            print(f"Received signal: {signum} — exiting")
        finally:
            sys.exit(1)

    catchable_signals = [signal.SIGTERM, signal.SIGINT, signal.SIGHUP]

    for sig in catchable_signals:
        try:
            signal.signal(sig, signal_handler)
            logger.info(f"Attached logging_handler to signal {sig}")
        except Exception as e:
            logger.warning(f"Could not attach handler to signal {sig}: {e}")


def detect_is_test_host(is_enabled: str, test_domain: str):
    if str(is_enabled).lower() in ('true', '1', 'yes'):
        local_vars.set_test_server_enabled(True)
    if test_domain and test_domain.startswith('http'):
        if test_domain.endswith('/'):
            test_domain = test_domain[:-1]
        local_vars.set_test_server_domain(test_domain)

def set_new_job():
    local_vars.set(_JOB_ID, uuid.uuid4().hex)

