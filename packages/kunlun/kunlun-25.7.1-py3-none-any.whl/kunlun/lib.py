from kunlun.job import util, vars
from kunlun.service import configs, testcase
from kunlun.service.plus import sched

conn = vars.CONN_DICT
se = vars.CONN_DICT
ud = vars.USER_DICT
kw = vars.CASE_KW
pa = vars.JSON_PARAMS
xlsx = vars.XLSX_MEASURE
autotest_sched = sched.autotest_sched
#
VERSION = vars.VERSION
USERNAME = vars.USERNAME
HOSTNAME = vars.HOSTNAME
DATA_PATH = vars.DATA_PATH
SCRIPT_PATH = vars.SCRIPT_PATH
TEST_LOG_PATH = vars.TEST_LOG_PATH

CTRL_A = "\001"
CTRL_B = "\002"
CTRL_C = "\003"
CTRL_D = "\004"
CTRL_E = "\005"
CTRL_F = "\006"
CTRL_G = "\007"
#
CTRL_H = "\010"
CTRL_I = "\011"
CTRL_J = "\012"
CTRL_K = "\013"
CTRL_L = "\014"
CTRL_M = "\015"
CTRL_N = "\016"
CTRL_O = "\017"
#
CTRL_P = "\020"
CTRL_Q = "\021"
CTRL_R = "\022"
CTRL_S = "\023"
CTRL_T = "\024"
CTRL_U = "\025"
CTRL_V = "\026"
CTRL_W = "\027"
#
CTRL_X = "\030"
CTRL_Y = "\031"
CTRL_Z = "\032"
#
ESC = "\033"
BREAK_TELNET = "\035"
UP = "\x1b[A"
DOWN = "\x1b[B"
RIGHT = "\x1b[C"
LEFT = "\x1b[D"


def get_configuration(**kwargs):
    return configs.Configs(**kwargs)


def get_event_logger():
    return util.get_event_logger()


def get_container_name():
    return util.get_container_info("name")


def get_mode():
    return util.get_container_info("mode")


def set_display1(value, name=""):
    return util.set_container_info("display1", value, name=name)


def set_display2(value, name=""):
    return util.set_container_info("display2", value, name=name)


def set_display3(value, name=""):
    return util.set_container_info("display3", value, name=name)


def set_display4(value, name=""):
    return util.set_container_info("display4", value, name=name)


def set_display5(value, name=""):
    return util.set_container_info("display5", value, name=name)


def set_display6(value, name=""):
    return util.set_container_info("display6", value, name=name)


def set_custom_data(name, value, display=""):
    return util.set_custom_data(name, value, display=display)


def set_step_name(name):
    return util.set_step_name(name)


def get_step_name():
    return util.get_container_info("step_name")


def ask_question(question, **kwargs):
    return util.ask_question(question, **kwargs)


def ask_questions(questions, **kwargs):
    return util.ask_questions(questions, **kwargs)


def acquire_locking(name, wait_timeout=3600, privilege=False):
    util.acquire_queue(name, wait_timeout=wait_timeout, privilege=privilege)


def release_locking(name):
    util.release_queue(name)


class FIFOLocking(util.FIFOQueue):
    def __init__(self, name, wait_timeout=3600, privilege=False):
        super(FIFOLocking, self).__init__(name, wait_timeout=wait_timeout, privilege=privilege)


def fifo_locking(name, wait_timeout=3600, privilege=False):
    return util.fifo_queue(name, wait_timeout=wait_timeout, privilege=privilege)


def sync_up(group_name, wait_timeout=3600):
    return util.sync_up(group_name, wait_timeout=wait_timeout)


class SyncUp(util.SyncUp):
    def __init__(self, group_name, wait_timeout=3600):
        super(SyncUp, self).__init__(group_name, wait_timeout=wait_timeout)


def leader_sync_up(group_name, leader_container, wait_timeout=3600):
    return util.leader_sync_up(group_name, leader_container=leader_container, wait_timeout=wait_timeout)


def start_test(name, override=True, wait=False):
    return util.start_test(name, override=override, wait=wait)


def stop_test(name):
    return util.stop_test(name)


def deposit_test(name):
    return util.deposit_test(name)


def put_cache(name, value):
    return util.put_cache(name, value)


def get_cache(name):
    return util.get_cache(name)


def get_params(name=""):
    return util.get_params(name=name)


def get_sync_group(name):
    return util.get_sync_group(name)


def add_test_data(**kwargs):
    return util.add_test_data(**kwargs)


def get_json_params(sheet="Sheet1", name=""):
    return util.get_json_params(sheet=sheet, name=name)


def get_sequence_definition(name="SEQUENCE", **kwargs):
    return util.get_sequence_definition(name=name, **kwargs)


def get_sequence_data():
    return util.get_sequence_data()


def add_measure(name, value, **kwargs):
    return util.add_measure(name, value, **kwargs)


def add_xlsx_measure(sheet, name, value, **kwargs):
    return util.add_xlsx_measure(sheet, name, value, **kwargs)


class TestCase(testcase.TestCase):
    # for project/testcase
    pass
