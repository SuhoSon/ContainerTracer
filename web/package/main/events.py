import os
import sys
from flask import session
from flask_socketio import emit
from .. import socketio
from .. import Config

set_config = Config()


@socketio.on("connect")
def connect():
    if "session" in session:
        pass
    else:
        session["session"] = os.urandom(24)


@socketio.on("disconnect")
def disconnect():
    session.clear()


@socketio.on("set_driver")
def set_driver(driver):
    set_config.store(driver, "driver")
    emit("set_driver_ret")


@socketio.on("set_options")
def set_options(set_each, set_all):
    set_config.store(set_all, "set_all")
    set_config.store(set_each, "set_each")
    json_config = set_config.get_config_data()
    try:
        container_tracer = set_config.set_container_tracer(json_config)
        container_tracer.run_all_container_tracer()  # 여기서 trace-replay가 시작합니다
    except OSError as e:
        print(e, file=sys.stderr)
        sys.exit(-1)
    except Exception as e:
        emit("Invalid", str(e))
        return

    nr_cgroup = len(set_config.data["setting"]["task_option"])
    emit("chart_start", nr_cgroup)


@socketio.on("test_set_options")
def test_set_options(set_each, set_all):
    set_config.store(set_all, "set_all")
    set_config.store(set_each, "set_each")
    emit("save", set_config.get_config_data())
