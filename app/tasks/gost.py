import json
import typing as t
import ansible_runner
from uuid import uuid4

from . import celery_app
from app.db.session import SessionLocal
from app.db.models.port import Port
from app.db.models.user import User
from app.db.models.server import Server
from app.db.models.port_forward import PortForwardRule
from app.db.crud.server import get_server
from app.tasks.utils import prepare_priv_dir, iptables_finished_handler


@celery_app.task()
def gost_finished_handler(stdout_name: str):
    pass
    # with open(stdout_name, 'r') as f:
    # return f.read()


@celery_app.task()
def gost_status_handler(port_id: int, status_data: dict, update_status: bool):
    if not update_status:
        return status_data

    db = SessionLocal()
    rule = (
        db.query(PortForwardRule)
        .filter(PortForwardRule.port_id == port_id)
        .first()
    )
    if rule:
        if (
            status_data.get("status", None) == "starting"
            and rule.status == "running"
        ):
            return status_data
        rule.status = status_data.get("status", None)
        db.add(rule)
        db.commit()
    return status_data


@celery_app.task()
def gost_runner(
    port_id: int,
    server_id: int,
    port_num: int,
    gost_config: t.Dict,
    remote_ip: str = None,
    update_gost: bool = False,
    update_status: bool = False,
):
    server = get_server(SessionLocal(), server_id)
    priv_data_dir = prepare_priv_dir(server)
    with open(f"ansible/project/roles/gost/files/{port_id}.json", "w") as f:
        f.write(json.dumps(gost_config, indent=4))

    extra_vars = {
        "host": server.ansible_name,
        "port_id": port_id,
        "local_port": port_num,
        "remote_ip": remote_ip,
        "update_gost": update_gost,
        "update_status": update_status,
    }
    r = ansible_runner.run_async(
        private_data_dir=priv_data_dir,
        project_dir="ansible/project",
        playbook="gost.yml",
        extravars=extra_vars,
        status_handler=lambda s, **k: gost_status_handler.delay(
            port_id, s, update_status
        ),
        finished_callback=iptables_finished_handler(server, True)
        if update_status
        else lambda r: None,
    )
    return r[1].config.artifact_dir
