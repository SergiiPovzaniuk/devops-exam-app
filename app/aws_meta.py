import os
import urllib.request

IMDS = "http://169.254.169.254"
TOKEN_URL = f"{IMDS}/latest/api/token"
META = f"{IMDS}/latest/meta-data"


def _token(timeout=1.0):
    req = urllib.request.Request(
        TOKEN_URL,
        method="PUT",
        headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode()


def _get(path, token, timeout=1.0):
    req = urllib.request.Request(
        f"{META}/{path}",
        headers={"X-aws-ec2-metadata-token": token},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode()


def fetch_aws_metadata():
    data = {
        "instance_id": os.environ.get("AWS_INSTANCE_ID", "n/a"),
        "availability_zone": os.environ.get("AWS_AZ", "n/a"),
        "private_ip": os.environ.get("AWS_PRIVATE_IP", "n/a"),
        "public_ip": os.environ.get("AWS_PUBLIC_IP", "n/a"),
        "instance_type": os.environ.get("AWS_INSTANCE_TYPE", "n/a"),
        "ami_id": os.environ.get("AWS_AMI_ID", "n/a"),
        "local_hostname": os.environ.get("AWS_LOCAL_HOSTNAME", "n/a"),
    }
    try:
        token = _token()
        data.update(
            {
                "instance_id": _get("instance-id", token),
                "availability_zone": _get("placement/availability-zone", token),
                "private_ip": _get("local-ipv4", token),
                "instance_type": _get("instance-type", token),
                "ami_id": _get("ami-id", token),
                "local_hostname": _get("local-hostname", token),
            }
        )
        try:
            data["public_ip"] = _get("public-ipv4", token)
        except Exception:
            pass
    except Exception:
        pass
    return data